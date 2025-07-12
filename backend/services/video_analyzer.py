import json
import subprocess
from typing import Dict, Optional, Any
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """
    Service for analyzing video files and extracting metadata
    """

    def __init__(self):
        self.ffprobe_path = self._find_ffprobe()

    def _find_ffprobe(self) -> str:
        """
        Find ffprobe executable in system PATH
        """
        logger.info("FFPROBE: Searching for ffprobe executable...")

        # Try common locations
        common_paths = [
            "ffprobe",
            "ffprobe.exe",
            "/usr/bin/ffprobe",
            "/usr/local/bin/ffprobe",
            "C:\\ffmpeg\\bin\\ffprobe.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe",
            "C:\\Program Files (x86)\\ffmpeg\\bin\\ffprobe.exe",
        ]

        for path in common_paths:
            try:
                logger.info(f"FFPROBE: Trying path: {path}")
                result = subprocess.run(
                    [path, "-version"],
                    capture_output=True,
                    check=True,
                    timeout=5,
                    text=True,
                )
                logger.info(f"FFPROBE: Found working ffprobe at: {path}")
                return path
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ) as e:
                logger.debug(f"FFPROBE: Failed to use {path}: {e}")
                continue

        # If not found, return default and let it fail gracefully
        logger.warning("FFPROBE: No working ffprobe found in common locations")
        return "ffprobe"

    def _check_ffprobe_available(self) -> bool:
        """
        Check if ffprobe is available and working
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, "-version"],
                capture_output=True,
                check=True,
                timeout=5,
                text=True,
            )
            return True
        except Exception as e:
            logger.error(f"FFPROBE: Not available - {e}")
            return False

    async def analyze_video(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze video file and extract metadata
        """
        logger.info(f"ANALYZE: Starting video analysis for: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"ERROR: Video file not found: {file_path}")
            raise FileNotFoundError(f"Video file not found: {file_path}")

        # Check if ffprobe is available
        if not self._check_ffprobe_available():
            error_msg = (
                "FFmpeg/ffprobe is not installed or not found in PATH. "
                "Please install FFmpeg from https://ffmpeg.org/download.html "
                "or ensure it's in your system PATH."
            )
            logger.error(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)

        try:
            # Run ffprobe to get video metadata
            cmd = [
                self.ffprobe_path,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ]

            logger.info(f"FFPROBE: Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )  # 5 minutes for large files

            if result.returncode != 0:
                logger.error(
                    f"FFPROBE: Command failed with return code {result.returncode}"
                )
                logger.error(f"FFPROBE: stderr: {result.stderr}")
                raise RuntimeError(f"FFprobe failed: {result.stderr}")

            logger.info("FFPROBE: Successfully extracted metadata")

            # Parse JSON output
            metadata = json.loads(result.stdout)

            # Extract and format relevant information
            analysis = self._extract_video_info(metadata, file_path)

            logger.info("ANALYZE: Video analysis completed successfully")
            return analysis

        except subprocess.TimeoutExpired:
            logger.error("FFPROBE: Analysis timed out")
            raise RuntimeError("Video analysis timed out")
        except json.JSONDecodeError as e:
            logger.error(f"FFPROBE: Failed to parse JSON output: {e}")
            raise RuntimeError("Failed to parse video metadata")
        except Exception as e:
            logger.error(f"ANALYZE: Video analysis failed: {str(e)}")
            raise RuntimeError(f"Video analysis failed: {str(e)}")

    def _extract_video_info(self, metadata: Dict, file_path: str) -> Dict[str, Any]:
        """
        Extract and format video information from ffprobe output
        """
        logger.info("EXTRACT: Extracting video information from metadata")

        format_info = metadata.get("format", {})
        streams = metadata.get("streams", [])

        # Find video and audio streams
        video_stream = None
        audio_stream = None

        for stream in streams:
            if stream.get("codec_type") == "video" and not video_stream:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and not audio_stream:
                audio_stream = stream

        if not video_stream:
            logger.error("EXTRACT: No video stream found in file")
            raise RuntimeError("No video stream found in file")

        # Extract video information
        width = video_stream.get("width", 0)
        height = video_stream.get("height", 0)
        fps = self._parse_fps(video_stream.get("r_frame_rate", "0/1"))
        duration = float(format_info.get("duration", 0))
        bitrate = int(format_info.get("bit_rate", 0))
        file_size = int(format_info.get("size", 0))

        # Video codec
        video_codec = video_stream.get("codec_name", "unknown")

        # Aspect ratio
        aspect_ratio = f"{width}:{height}"
        if width > 0 and height > 0:
            from math import gcd

            ratio_gcd = gcd(width, height)
            aspect_ratio = f"{width//ratio_gcd}:{height//ratio_gcd}"

        # HDR detection (basic check)
        color_space = video_stream.get("color_space", "").lower()
        color_transfer = video_stream.get("color_transfer", "").lower()
        is_hdr = any(
            hdr_indicator in color_space or hdr_indicator in color_transfer
            for hdr_indicator in ["bt2020", "smpte2084", "hlg", "hdr"]
        )

        # Audio information
        audio_info = {}
        if audio_stream:
            audio_info = {
                "codec": audio_stream.get("codec_name", "unknown"),
                "channels": audio_stream.get("channels", 0),
                "sample_rate": audio_stream.get("sample_rate", 0),
                "bitrate": audio_stream.get("bit_rate", 0),
            }

        # Format duration nicely
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        result = {
            "filename": os.path.basename(file_path),
            "resolution": f"{width}x{height}",
            "fps": round(fps, 2),
            "duration": duration_formatted,
            "duration_seconds": round(duration, 2),
            "aspect_ratio": aspect_ratio,
            "codec": video_codec,
            "bitrate": bitrate,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "hdr": is_hdr,
            "audio": audio_info,
            "format": format_info.get("format_name", "unknown"),
        }

        logger.info(f"EXTRACT: Successfully extracted info for {result['filename']}")
        return result

    def _parse_fps(self, fps_string: str) -> float:
        """
        Parse FPS from fractional string (e.g., "30000/1001")
        """
        try:
            if "/" in fps_string:
                numerator, denominator = fps_string.split("/")
                return float(numerator) / float(denominator)
            return float(fps_string)
        except (ValueError, ZeroDivisionError):
            return 0.0
