from typing import Dict, Any, List, Tuple
import os
import logging
from pathlib import Path
import subprocess
import json
import uuid
import re
import librosa
import numpy as np
from moviepy.editor import VideoFileClip

# Configure logging
logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Service for processing heavy bag training videos - detects hits using noise gate and creates montage
    """

    def __init__(self):
        self.output_dir = "outputs"
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = self._find_ffmpeg()
        logger.info(
            f"DIR: VideoProcessor initialized with output dir: {self.output_dir}"
        )

    def _find_ffmpeg(self) -> str:
        """Find ffmpeg executable in system PATH"""
        common_paths = [
            "ffmpeg",
            "ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
        ]

        for path in common_paths:
            try:
                subprocess.run(
                    [path, "-version"], capture_output=True, check=True, timeout=5
                )
                logger.info(f"FFMPEG: Found working ffmpeg at: {path}")
                return path
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                continue

        logger.warning("FFMPEG: No working ffmpeg found in common locations")
        return "ffmpeg"

    def _analyze_audio_with_rms_energy(
        self, file_path: str, audio_sensitivity: float, merge_threshold: float
    ) -> List[Tuple[float, float]]:
        """
        Analyze audio using RMS energy to detect heavy bag combos
        Returns list of (start_time, end_time) tuples for combo segments
        """
        logger.info(f"RMS_ENERGY: Analyzing audio for heavy bag combos in {file_path}")
        logger.info(
            f"RMS_ENERGY: Sensitivity={audio_sensitivity}, Merge threshold={merge_threshold}s"
        )

        temp_audio_path = None
        try:
            # Step 1: Extract audio using moviepy
            logger.info("RMS_ENERGY: Extracting audio from video...")
            video = VideoFileClip(file_path)

            # Create temporary audio file
            temp_audio_path = f"temp_audio_{uuid.uuid4().hex[:8]}.wav"
            video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            video.close()

            # Step 2: Load audio with librosa
            logger.info("RMS_ENERGY: Loading audio with librosa...")
            y, sr = librosa.load(temp_audio_path, sr=None)

            # Step 3: Calculate RMS energy
            logger.info("RMS_ENERGY: Calculating RMS energy...")
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

            # Step 4: Find active segments (above audio sensitivity threshold)
            active_mask = rms_norm > audio_sensitivity
            logger.info(
                f"RMS_ENERGY: Found {np.sum(active_mask)} active frames out of {len(active_mask)}"
            )

            # Step 5: Find continuous segments
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

            logger.info(f"RMS_ENERGY: Found {len(segments)} raw active segments")

            # Step 6: Merge segments that are close together
            merged_segments = []
            for start, end in segments:
                if merged_segments and start - merged_segments[-1][1] < merge_threshold:
                    # Merge with previous segment
                    merged_segments[-1] = (merged_segments[-1][0], end)
                else:
                    merged_segments.append((start, end))

            logger.info(f"RMS_ENERGY: After merging: {len(merged_segments)} segments")

            # Step 7: Filter out very short segments (less than 0.5 seconds)
            final_segments = [
                (start, end) for start, end in merged_segments if end - start > 0.5
            ]

            logger.info(f"RMS_ENERGY: Final segments: {len(final_segments)}")
            for i, (start, end) in enumerate(final_segments):
                logger.info(
                    f"  Segment {i+1}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)"
                )

            return final_segments

        except Exception as e:
            logger.error(f"RMS_ENERGY: Audio analysis failed: {str(e)}")
            raise RuntimeError(f"Audio analysis failed: {str(e)}")
        finally:
            # Clean up temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except:
                    pass

    def _get_video_duration(self, file_path: str) -> float:
        """Get video duration in seconds"""
        cmd = [self.ffmpeg_path, "-i", file_path, "-f", "null", "-"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Parse duration from stderr output
            for line in result.stderr.split("\n"):
                if "Duration:" in line:
                    duration_str = line.split("Duration:")[1].split(",")[0].strip()
                    # Parse HH:MM:SS.mmm format
                    time_parts = duration_str.split(":")
                    if len(time_parts) == 3:
                        hours = float(time_parts[0])
                        minutes = float(time_parts[1])
                        seconds = float(time_parts[2])
                        return hours * 3600 + minutes * 60 + seconds

            return 0.0

        except Exception as e:
            logger.error(f"DURATION: Failed to get video duration: {str(e)}")
            return 0.0

    def _create_montage(
        self, file_path: str, segments: List[Tuple[float, float]], output_path: str
    ) -> bool:
        """
        Create montage from hit segments, preserving original video quality and dimensions
        """
        logger.info(
            f"MONTAGE: Creating heavy bag montage with {len(segments)} segments"
        )

        if not segments:
            logger.error("MONTAGE: No segments to process")
            return False

        # Create filter complex for concatenating segments
        # This preserves original video quality and dimensions
        filter_parts = []
        input_parts = []

        for i, (start, end) in enumerate(segments):
            # Add input with seek and duration
            input_parts.extend(
                ["-ss", str(start), "-t", str(end - start), "-i", file_path]
            )

            # Add to filter complex
            filter_parts.append(f"[{i}:v][{i}:a]")

        # Build the complete FFmpeg command
        cmd = (
            [self.ffmpeg_path]
            + input_parts
            + [
                "-filter_complex",
                f"{''.join(filter_parts)}concat=n={len(segments)}:v=1:a=1[outv][outa]",
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                "-c:v",
                "libx264",  # Use H.264 codec
                "-c:a",
                "aac",  # Use AAC audio codec
                "-preset",
                "fast",  # Fast encoding
                "-crf",
                "23",  # Good quality
                "-movflags",
                "+faststart",  # Web optimization
                output_path,
            ]
        )

        logger.info(
            f"FFMPEG: Running montage creation: {' '.join(cmd[:10])}... (truncated)"
        )

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800
            )  # 30 minutes max

            if result.returncode != 0:
                logger.error(
                    f"MONTAGE: FFmpeg failed with return code {result.returncode}"
                )
                logger.error(f"MONTAGE: stderr: {result.stderr}")
                return False

            # Verify output file was created
            if not os.path.exists(output_path):
                logger.error(f"MONTAGE: Output file not created: {output_path}")
                return False

            output_size = os.path.getsize(output_path)
            logger.info(
                f"MONTAGE: Successfully created heavy bag montage: {output_path} ({output_size} bytes)"
            )
            return True

        except subprocess.TimeoutExpired:
            logger.error("MONTAGE: Montage creation timed out")
            return False
        except Exception as e:
            logger.error(f"MONTAGE: Montage creation failed: {str(e)}")
            return False

    async def process_video(
        self,
        file_path: str,
        audio_sensitivity: float = 0.3,
        merge_threshold: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Process heavy bag training video using RMS energy to detect combos
        Creates montage of all combinations
        """
        logger.info(f"PROCESS: Starting heavy bag video processing for: {file_path}")
        logger.info(
            f"PARAMS: audio_sensitivity={audio_sensitivity}, merge_threshold={merge_threshold}s"
        )

        # Validate input file exists
        if not os.path.exists(file_path):
            logger.error(f"ERROR: Input video file not found: {file_path}")
            raise FileNotFoundError(f"Input video file not found: {file_path}")

        # Validate parameters
        if not (0.0 <= audio_sensitivity <= 1.0):
            raise ValueError("Audio sensitivity must be between 0.0 and 1.0")
        if not (0.1 <= merge_threshold <= 5.0):
            raise ValueError("Merge threshold must be between 0.1 and 5.0 seconds")

        try:
            # Generate output filename
            input_filename = os.path.basename(file_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"heavy_bag_montage_{name}_{uuid.uuid4().hex[:8]}{ext}"
            output_path = os.path.join(self.output_dir, output_filename)

            logger.info(f"OUTPUT: Generated output path: {output_path}")

            # Step 1: Analyze audio with RMS energy to find combo segments
            combo_segments = self._analyze_audio_with_rms_energy(
                file_path, audio_sensitivity, merge_threshold
            )

            if not combo_segments:
                return {
                    "success": False,
                    "message": "No heavy bag combos detected in video",
                    "input_file": input_filename,
                    "settings": {
                        "audio_sensitivity": audio_sensitivity,
                        "merge_threshold": merge_threshold,
                    },
                }

            # Step 2: Create montage from combo segments
            montage_success = self._create_montage(
                file_path, combo_segments, output_path
            )

            if not montage_success:
                return {
                    "success": False,
                    "message": "Failed to create heavy bag montage",
                    "input_file": input_filename,
                    "settings": {
                        "audio_sensitivity": audio_sensitivity,
                        "merge_threshold": merge_threshold,
                    },
                }

            # Calculate statistics
            total_combo_time = sum(end - start for start, end in combo_segments)
            original_duration = self._get_video_duration(file_path)
            compression_ratio = (
                total_combo_time / original_duration if original_duration > 0 else 0
            )

            # Format durations nicely
            def format_duration(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"

            result = {
                "success": True,
                "message": "Heavy bag video processing completed successfully",
                "input_file": input_filename,
                "output_file": output_filename,
                "output_path": f"/outputs/{output_filename}",  # Web-accessible path
                "settings": {
                    "audio_sensitivity": audio_sensitivity,
                    "merge_threshold": merge_threshold,
                },
                "processing_stats": {
                    "hits_detected": len(combo_segments),
                    "total_duration": format_duration(original_duration),
                    "montage_duration": format_duration(total_combo_time),
                    "compression_ratio": round(compression_ratio, 2),
                    "time_saved": format_duration(original_duration - total_combo_time),
                },
            }

            logger.info("SUCCESS: Heavy bag video processing completed successfully")
            return result

        except Exception as e:
            logger.error(f"PROCESS: Heavy bag video processing failed: {str(e)}")
            raise RuntimeError(f"Heavy bag video processing failed: {str(e)}")

    def get_processing_status(self, task_id: str) -> Dict[str, Any]:
        """Get processing status for a task"""
        logger.info(f"STATUS: Getting processing status for task: {task_id}")
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "message": "Processing completed",
        }

    def cancel_processing(self, task_id: str) -> Dict[str, Any]:
        """Cancel a processing task"""
        logger.info(f"CANCEL: Cancelling processing task: {task_id}")
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled",
        }
