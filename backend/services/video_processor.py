from typing import Dict, Any, List, Tuple
import os
import logging
from pathlib import Path
import subprocess
import json
import uuid
import re

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

    def _analyze_audio_with_noise_gate(
        self, file_path: str, noise_threshold_percent: float, padding_duration: float
    ) -> List[Tuple[float, float]]:
        """
        Analyze audio using noise gate approach to detect heavy bag combos
        Returns list of (start_time, end_time) tuples for combo segments with padding
        """
        logger.info(f"NOISE_GATE: Analyzing audio for heavy bag combos in {file_path}")
        logger.info(
            f"NOISE_GATE: Threshold={noise_threshold_percent}%, Padding={padding_duration}s"
        )

        # Step 1: Get audio statistics to find peak volume
        stats_cmd = [
            self.ffmpeg_path,
            "-i",
            file_path,
            "-af",
            "astats=metadata=1:reset=1",
            "-f",
            "null",
            "-",
        ]

        try:
            result = subprocess.run(
                stats_cmd, capture_output=True, text=True, timeout=300
            )

            # Parse maximum peak from output
            max_peak_db = -60.0  # Default fallback
            for line in result.stderr.split("\n"):
                if "Overall Maximum Peak:" in line:
                    try:
                        peak_match = re.search(r"(-?\d+\.?\d*)\s*dB", line)
                        if peak_match:
                            max_peak_db = float(peak_match.group(1))
                            break
                    except ValueError:
                        continue

            logger.info(f"NOISE_GATE: Found maximum peak at {max_peak_db} dB")

            # Calculate threshold based on percentage
            # Use a proper dynamic range calculation
            # Assume noise floor is around -80 dB below peak
            noise_floor_db = max_peak_db - 80
            dynamic_range = max_peak_db - noise_floor_db

            # Calculate threshold as percentage from peak towards noise floor
            threshold_offset = dynamic_range * (noise_threshold_percent / 100)
            threshold_db = max_peak_db - threshold_offset

            # Safeguard: ensure threshold is at least 10 dB below peak
            # This prevents cases where the threshold is too close to the peak
            min_threshold_db = max_peak_db - 10
            if threshold_db > min_threshold_db:
                logger.warning(
                    f"NOISE_GATE: Threshold {threshold_db:.1f} dB too close to peak, using {min_threshold_db:.1f} dB instead"
                )
                threshold_db = min_threshold_db

            logger.info(
                f"NOISE_GATE: Peak: {max_peak_db} dB, Noise floor: {noise_floor_db} dB"
            )
            logger.info(
                f"NOISE_GATE: Using threshold of {threshold_db:.1f} dB ({noise_threshold_percent}% from peak)"
            )

            # Step 2: Detect silence segments (gaps longer than padding_duration)
            # This finds where audio is below threshold for more than padding_duration
            detect_cmd = [
                self.ffmpeg_path,
                "-i",
                file_path,
                "-af",
                f"silencedetect=noise={threshold_db}dB:d={padding_duration}",
                "-f",
                "null",
                "-",
            ]

            logger.info(
                f"NOISE_GATE: Running combo detection with {padding_duration}s silence threshold"
            )
            result = subprocess.run(
                detect_cmd, capture_output=True, text=True, timeout=300
            )

            # Debug: Log the silence detection output
            logger.info("NOISE_GATE: Silence detection output:")
            silence_lines = [
                line for line in result.stderr.split("\n") if "silence" in line.lower()
            ]
            for line in silence_lines:
                logger.info(f"  {line}")

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

            logger.info(
                f"NOISE_GATE: Found {len(silence_segments)} raw silence segments"
            )
            for i, (start, end) in enumerate(silence_segments):
                logger.info(
                    f"  Silence {i+1}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)"
                )

            # Get video duration
            duration = self._get_video_duration(file_path)
            logger.info(f"NOISE_GATE: Video duration: {duration:.2f}s")

            # Convert silence segments to combo segments
            # Everything that's NOT silent for more than padding_duration is a combo
            combo_segments = []
            last_end = 0.0

            logger.info("NOISE_GATE: Converting silence segments to combo segments...")
            for i, (silence_start, silence_end) in enumerate(silence_segments):
                # Add combo segment before this silence
                if silence_start > last_end:
                    combo_segments.append((last_end, silence_start))
                    logger.info(
                        f"  Added combo: {last_end:.2f}s - {silence_start:.2f}s (before silence {i+1})"
                    )
                else:
                    logger.info(
                        f"  Skipped combo before silence {i+1}: no gap ({last_end:.2f}s >= {silence_start:.2f}s)"
                    )
                last_end = silence_end

            # Add final combo segment if there's time left
            if last_end < duration:
                combo_segments.append((last_end, duration))
                logger.info(f"  Added final combo: {last_end:.2f}s - {duration:.2f}s")
            else:
                logger.info(
                    f"  No final combo needed: {last_end:.2f}s >= {duration:.2f}s"
                )

            logger.info(f"NOISE_GATE: Created {len(combo_segments)} raw combo segments")

            # Step 3: Add padding around combo segments
            padded_segments = []

            for start, end in combo_segments:
                # Add padding before and after each combo
                padded_start = max(0, start - padding_duration)
                padded_end = min(duration, end + padding_duration)
                padded_segments.append((padded_start, padded_end))

            # Step 4: Merge overlapping segments (in case padding causes overlap)
            if not padded_segments:
                logger.warning("NOISE_GATE: No combo segments found")
                return []

            # Sort by start time
            padded_segments.sort(key=lambda x: x[0])
            merged_segments = []
            current_start, current_end = padded_segments[0]

            for start, end in padded_segments[1:]:
                if start <= current_end:  # Overlapping segments
                    current_end = max(current_end, end)  # Extend current segment
                else:
                    merged_segments.append((current_start, current_end))
                    current_start, current_end = start, end

            # Add the last segment
            merged_segments.append((current_start, current_end))

            # Filter out very short segments (less than 0.5 seconds)
            merged_segments = [
                (start, end) for start, end in merged_segments if (end - start) >= 0.5
            ]

            logger.info(
                f"NOISE_GATE: Found {len(merged_segments)} combo segments with padding"
            )
            total_time = sum(end - start for start, end in merged_segments)
            logger.info(f"NOISE_GATE: Total combo time: {total_time:.2f}s")

            for i, (start, end) in enumerate(merged_segments):
                logger.info(
                    f"  Combo {i+1}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)"
                )

            return merged_segments

        except subprocess.TimeoutExpired:
            logger.error("NOISE_GATE: Audio analysis timed out")
            raise RuntimeError("Audio analysis timed out")
        except Exception as e:
            logger.error(f"NOISE_GATE: Audio analysis failed: {str(e)}")
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
        noise_threshold_percent: float = 90.0,
        padding_duration: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Process heavy bag training video using noise gate to detect combos
        Creates montage of all combinations with padding around each combo
        """
        logger.info(f"PROCESS: Starting heavy bag video processing for: {file_path}")
        logger.info(
            f"PARAMS: noise_threshold_percent={noise_threshold_percent}%, padding_duration={padding_duration}s"
        )

        # Validate input file exists
        if not os.path.exists(file_path):
            logger.error(f"ERROR: Input video file not found: {file_path}")
            raise FileNotFoundError(f"Input video file not found: {file_path}")

        # Validate parameters
        if not (50.0 <= noise_threshold_percent <= 99.0):
            raise ValueError("Noise threshold must be between 50% and 99%")
        if not (0.5 <= padding_duration <= 10.0):
            raise ValueError("Padding duration must be between 0.5 and 10.0 seconds")

        try:
            # Generate output filename
            input_filename = os.path.basename(file_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"heavy_bag_montage_{name}_{uuid.uuid4().hex[:8]}{ext}"
            output_path = os.path.join(self.output_dir, output_filename)

            logger.info(f"OUTPUT: Generated output path: {output_path}")

            # Step 1: Analyze audio with noise gate to find combo segments
            combo_segments = self._analyze_audio_with_noise_gate(
                file_path, noise_threshold_percent, padding_duration
            )

            if not combo_segments:
                return {
                    "success": False,
                    "message": "No heavy bag combos detected in video",
                    "input_file": input_filename,
                    "settings": {
                        "noise_threshold_percent": noise_threshold_percent,
                        "padding_duration": padding_duration,
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
                        "noise_threshold_percent": noise_threshold_percent,
                        "padding_duration": padding_duration,
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
                    "noise_threshold_percent": noise_threshold_percent,
                    "padding_duration": padding_duration,
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
