import os
import shutil
import logging
from pathlib import Path
from typing import Optional
import uuid
from fastapi import UploadFile, HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Allowed video file extensions
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}

# Maximum file size removed to allow large video files (15GB+)
# MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes


def validate_video_file(file: UploadFile) -> bool:
    """
    Validate if the uploaded file is a valid video file
    """
    if not file.filename:
        logger.error("❌ No filename provided")
        raise HTTPException(status_code=400, detail="No filename provided")

    logger.info(f"🔍 Validating video file: {file.filename}")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    logger.info(f"📁 File extension: {file_extension}")

    if file_extension not in ALLOWED_EXTENSIONS:
        logger.error(f"❌ Invalid file extension: {file_extension}")
        logger.error(f"❌ Allowed extensions: {ALLOWED_EXTENSIONS}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # File size check removed to allow large video files (15GB+)
    # if file.size and file.size > MAX_FILE_SIZE:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
    #     )

    logger.info("✅ File validation passed")
    return True


async def save_upload_file(file: UploadFile, directory: str = "uploads") -> str:
    """
    Save uploaded file to the specified directory
    Returns the saved file path
    """
    logger.info(f"💾 Starting file save process for: {file.filename}")
    logger.info(f"📁 Target directory: {directory}")

    # Validate file (this will check filename is not None)
    validate_video_file(file)

    # Generate unique filename (safe to use after validation)
    file_extension = Path(file.filename or "").suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    logger.info(f"🆔 Generated unique filename: {unique_filename}")

    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Directory created/verified: {directory}")

    # Save file
    file_path = Path(directory) / unique_filename
    absolute_path = file_path.absolute()
    logger.info(f"📍 Saving to absolute path: {absolute_path}")

    try:
        with open(file_path, "wb") as buffer:
            logger.info("📝 Starting file write...")
            shutil.copyfileobj(file.file, buffer)

        # Verify file was saved successfully
        if not file_path.exists():
            logger.error(f"❌ File not found after save: {file_path}")
            raise HTTPException(
                status_code=500, detail="File was not saved successfully"
            )

        saved_size = file_path.stat().st_size
        logger.info(f"✅ File saved successfully! Size: {saved_size} bytes")
        logger.info(f"📍 Final file path: {str(file_path)}")

        return str(file_path)
    except Exception as e:
        logger.error(f"❌ Error saving file: {str(e)}")
        # Clean up if save failed
        if file_path.exists():
            logger.info("🧹 Cleaning up failed save...")
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def cleanup_file(file_path: str) -> bool:
    """
    Clean up (delete) file at the specified path
    """
    logger.info(f"🧹 Attempting to cleanup file: {file_path}")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"✅ File cleaned up successfully: {file_path}")
            return True
        else:
            logger.warning(f"⚠️ File not found for cleanup: {file_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error cleaning up file: {str(e)}")
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes
    """
    try:
        size = os.path.getsize(file_path)
        logger.info(f"📊 File size for {file_path}: {size} bytes")
        return size
    except Exception as e:
        logger.error(f"❌ Error getting file size for {file_path}: {str(e)}")
        return None


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, create it if it doesn't
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directory ensured: {directory}")
        return True
    except Exception as e:
        logger.error(f"❌ Error ensuring directory {directory}: {str(e)}")
        return False
