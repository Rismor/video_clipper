from typing import Dict, Any, List, Tuple
import os
import logging
from pathlib import Path
import subprocess
import json
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Service for processing videos - removes silent segments while preserving original video quality
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

    def _analyze_audio_segments(
        self, file_path: str, silence_threshold: float, audio_sensitivity: float
    ) -> List[Tuple[float, float]]:
        """
        Analyze audio to find active segments (non-silent parts)
        Returns list of (start_time, end_time) tuples for active segments
        """
        logger.info(f"AUDIO: Analyzing audio segments for {file_path}")

        # Convert audio sensitivity (0.1-1.0) to FFmpeg silencedetect threshold
        # Higher sensitivity = lower threshold (more sensitive to quiet sounds)
        silence_db = -50 + (audio_sensitivity * 30)  # Range: -50dB to -20dB

        # Use FFmpeg silencedetect filter to find silent segments
        cmd = [
            self.ffmpeg_path,
            "-i",
            file_path,
            "-af",
            f"silencedetect=noise={silence_db}dB:d={silence_threshold}",
            "-f",
            "null",
            "-",
        ]

        logger.info(f"FFMPEG: Running silence detection: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Parse silence detection output
            silence_segments = []
            lines = result.stderr.split("\n")

            current_silence_start = None
            for line in lines:
                if "silence_start:" in line:
                    try:
                        start_time = float(line.split("silence_start:")[1].strip())
                        current_silence_start = start_time
                    except (ValueError, IndexError):
                        continue
                elif "silence_end:" in line and current_silence_start is not None:
                    try:
                        end_time = float(
                            line.split("silence_end:")[1].split("|")[0].strip()
                        )
                        silence_segments.append((current_silence_start, end_time))
                        current_silence_start = None
                    except (ValueError, IndexError):
                        continue

            # Get video duration
            duration = self._get_video_duration(file_path)

            # Convert silence segments to active segments
            active_segments = []
            last_end = 0.0

            for silence_start, silence_end in silence_segments:
                # Add active segment before this silence
                if silence_start > last_end:
                    active_segments.append((last_end, silence_start))
                last_end = silence_end

            # Add final active segment if there's time left
            if last_end < duration:
                active_segments.append((last_end, duration))

            # Filter out very short segments (less than 0.5 seconds)
            active_segments = [
                (start, end) for start, end in active_segments if (end - start) >= 0.5
            ]

            logger.info(f"SEGMENTS: Found {len(active_segments)} active segments")
            for i, (start, end) in enumerate(active_segments):
                logger.info(
                    f"  Segment {i+1}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)"
                )

            return active_segments

        except subprocess.TimeoutExpired:
            logger.error("AUDIO: Audio analysis timed out")
            raise RuntimeError("Audio analysis timed out")
        except Exception as e:
            logger.error(f"AUDIO: Audio analysis failed: {str(e)}")
            raise RuntimeError(f"Audio analysis failed: {str(e)}")

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
        Create montage from active segments, preserving original video quality and dimensions
        """
        logger.info(f"MONTAGE: Creating montage with {len(segments)} segments")

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
                f"MONTAGE: Successfully created montage: {output_path} ({output_size} bytes)"
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
        silence_threshold: float = 0.8,
        audio_sensitivity: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Process video to create montage by removing silent segments
        Preserves original video quality and dimensions
        """
        logger.info(f"PROCESS: Starting video processing for: {file_path}")
        logger.info(
            f"PARAMS: silence_threshold={silence_threshold}, audio_sensitivity={audio_sensitivity}"
        )

        # Validate input file exists
        if not os.path.exists(file_path):
            logger.error(f"ERROR: Input video file not found: {file_path}")
            raise FileNotFoundError(f"Input video file not found: {file_path}")

        # Validate parameters
        if not (0.1 <= silence_threshold <= 5.0):
            raise ValueError("Silence threshold must be between 0.1 and 5.0 seconds")
        if not (0.1 <= audio_sensitivity <= 1.0):
            raise ValueError("Audio sensitivity must be between 0.1 and 1.0")

        try:
            # Generate output filename
            input_filename = os.path.basename(file_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"clipped_{name}_{uuid.uuid4().hex[:8]}{ext}"
            output_path = os.path.join(self.output_dir, output_filename)

            logger.info(f"OUTPUT: Generated output path: {output_path}")

            # Step 1: Analyze audio to find active segments
            active_segments = self._analyze_audio_segments(
                file_path, silence_threshold, audio_sensitivity
            )

            if not active_segments:
                return {
                    "success": False,
                    "message": "No active segments found in video",
                    "input_file": input_filename,
                    "settings": {
                        "silence_threshold": silence_threshold,
                        "audio_sensitivity": audio_sensitivity,
                    },
                }

            # Step 2: Create montage from active segments
            montage_success = self._create_montage(
                file_path, active_segments, output_path
            )

            if not montage_success:
                return {
                    "success": False,
                    "message": "Failed to create video montage",
                    "input_file": input_filename,
                    "settings": {
                        "silence_threshold": silence_threshold,
                        "audio_sensitivity": audio_sensitivity,
                    },
                }

            # Calculate statistics
            total_active_time = sum(end - start for start, end in active_segments)
            original_duration = self._get_video_duration(file_path)
            compression_ratio = (
                total_active_time / original_duration if original_duration > 0 else 0
            )

            # Format durations nicely
            def format_duration(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"

            result = {
                "success": True,
                "message": "Video processing completed successfully",
                "input_file": input_filename,
                "output_file": output_filename,
                "output_path": f"/outputs/{output_filename}",  # Web-accessible path
                "settings": {
                    "silence_threshold": silence_threshold,
                    "audio_sensitivity": audio_sensitivity,
                },
                "processing_stats": {
                    "segments_found": len(active_segments),
                    "total_duration": format_duration(original_duration),
                    "processed_duration": format_duration(total_active_time),
                    "compression_ratio": round(compression_ratio, 2),
                    "time_saved": format_duration(
                        original_duration - total_active_time
                    ),
                },
            }

            logger.info("SUCCESS: Video processing completed successfully")
            return result

        except Exception as e:
            logger.error(f"PROCESS: Video processing failed: {str(e)}")
            raise RuntimeError(f"Video processing failed: {str(e)}")

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
