from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import shutil
from datetime import datetime
import librosa
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=".")
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
MAX_CONTENT_LENGTH = 12 * 1024 * 1024 * 1024  # 12GB

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def analyze_audio_segments(audio_file, silence_threshold=0.8, audio_sensitivity=0.3):
    """
    Analyze audio to find segments with sound vs silence
    Returns list of (start_time, end_time) tuples for active segments
    """
    logger.info(f"Analyzing audio: {audio_file}")

    try:
        # Load audio file
        y, sr = librosa.load(audio_file, sr=None)

        # Calculate RMS energy
        hop_length = 512
        frame_length = 2048
        rms = librosa.feature.rms(
            y=y, frame_length=frame_length, hop_length=hop_length
        )[0]

        # Convert to dB
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)

        # Normalize to 0-1 range
        rms_norm = (rms_db - np.min(rms_db)) / (np.max(rms_db) - np.min(rms_db))

        # Time axis
        frames = range(len(rms))
        times = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length)

        # Find active segments (above audio sensitivity threshold)
        active_mask = rms_norm > audio_sensitivity

        # Find continuous segments
        segments = []
        start_time = None

        for i, (time, is_active) in enumerate(zip(times, active_mask)):
            if is_active and start_time is None:
                # Start of active segment
                start_time = time
            elif not is_active and start_time is not None:
                # End of active segment
                segments.append((start_time, time))
                start_time = None

        # Handle case where audio ends during active segment
        if start_time is not None:
            segments.append((start_time, times[-1]))

        # Merge segments that are close together (less than silence_threshold apart)
        merged_segments = []
        for start, end in segments:
            if merged_segments and start - merged_segments[-1][1] < silence_threshold:
                # Merge with previous segment
                merged_segments[-1] = (merged_segments[-1][0], end)
            else:
                merged_segments.append((start, end))

        # Filter out very short segments (less than 0.5 seconds)
        final_segments = [
            (start, end) for start, end in merged_segments if end - start > 0.5
        ]

        logger.info(f"Found {len(final_segments)} active segments")
        return final_segments

    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        raise


def create_montage(video_file, segments, output_file):
    """
    Create a montage video from the original video using the active segments
    """
    logger.info(f"Creating montage with {len(segments)} segments")

    try:
        # Load the video
        video = VideoFileClip(video_file)

        # Get original video properties to preserve them
        original_size = video.size
        original_fps = video.fps

        logger.info(
            f"Original video properties - Size: {original_size}, FPS: {original_fps}"
        )

        # Create clips for each active segment
        clips = []
        for start, end in segments:
            # Ensure we don't go beyond video duration
            start = max(0, start)
            end = min(video.duration, end)

            if end > start:  # Only add if segment is valid
                clip = video.subclip(start, end)
                clips.append(clip)

        if not clips:
            raise ValueError("No valid segments found!")

        # Concatenate all clips while preserving original properties
        # Use method="compose" to preserve individual clip properties
        final_video = concatenate_videoclips(clips, method="compose")

        # Write the final video with original properties preserved
        final_video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            verbose=False,
            logger=None,
            preset="medium",
            # Preserve original video properties
            fps=original_fps,
            bitrate=None,  # Let it auto-detect to maintain quality
            # Don't specify resolution to keep original aspect ratio
        )

        # Clean up
        video.close()
        final_video.close()
        for clip in clips:
            clip.close()

        logger.info(f"Montage created successfully: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error creating montage: {str(e)}")
        raise


@app.route("/")
def index():
    """Serve the main page"""
    return send_file("index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files"""
    return send_file(filename)


@app.route("/api/process-video", methods=["POST"])
def process_video():
    """Process uploaded video and create montage"""
    try:
        # Check if file was uploaded
        if "video" not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        file = request.files["video"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Get parameters
        silence_threshold = float(request.form.get("silence_threshold", 0.8))
        audio_sensitivity = float(request.form.get("audio_sensitivity", 0.3))

        # Log file info with size warning
        file_size_mb = file.content_length / 1024 / 1024 if file.content_length else 0
        file_size_gb = file_size_mb / 1024

        logger.info(f"Processing video: {file.filename}")
        logger.info(f"File size: {file_size_gb:.2f} GB ({file_size_mb:.2f} MB)")
        if file_size_gb > 1:
            logger.info("⚠️ Large file detected - processing may take 15-30 minutes")
        logger.info(f"Silence threshold: {silence_threshold}s")
        logger.info(f"Audio sensitivity: {audio_sensitivity}")

        # Create temporary filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Keep original extension for temp file to ensure proper handling
        filename = file.filename or "video"
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in [".mp4", ".mav", ".mov", ".avi"]:
            file_extension = ".mp4"  # Default fallback
        temp_video = os.path.join(UPLOAD_FOLDER, f"temp_{timestamp}{file_extension}")
        output_video = os.path.join(OUTPUT_FOLDER, f"montage_{timestamp}.mp4")

        # Save uploaded file
        file.save(temp_video)

        try:
            # Extract audio for analysis
            logger.info("Extracting audio...")
            video_clip = VideoFileClip(temp_video)
            temp_audio = os.path.join(UPLOAD_FOLDER, f"temp_audio_{timestamp}.wav")

            # Check if video has audio
            if video_clip.audio is None:
                video_clip.close()
                return (
                    jsonify(
                        {
                            "error": "Video has no audio track! Cannot process without audio."
                        }
                    ),
                    400,
                )

            video_clip.audio.write_audiofile(temp_audio, verbose=False, logger=None)
            video_clip.close()

            # Analyze audio to find active segments
            logger.info("Analyzing audio patterns...")
            segments = analyze_audio_segments(
                temp_audio, silence_threshold, audio_sensitivity
            )

            if not segments:
                return (
                    jsonify(
                        {
                            "error": "No active segments found! Try adjusting sensitivity."
                        }
                    ),
                    400,
                )

            # Create montage
            logger.info("Creating montage...")
            create_montage(temp_video, segments, output_video)

            # Clean up temp files
            os.remove(temp_video)
            os.remove(temp_audio)

            # Return the processed video
            return send_file(
                output_video, as_attachment=True, download_name="kickboxing_montage.mp4"
            )

        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_video):
                os.remove(temp_video)
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            raise e

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "message": "Kickboxing Montage Creator API is running!"}
    )


if __name__ == "__main__":
    logger.info("Starting Kickboxing Montage Creator API...")
    app.run(host="0.0.0.0", port=5000, debug=True)
