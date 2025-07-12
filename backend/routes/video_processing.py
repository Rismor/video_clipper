from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from services.video_processor import VideoProcessor
from utils.file_utils import save_upload_file, cleanup_file
from pydantic import BaseModel
from typing import List, Optional
import os
import traceback
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("video_processing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize video processor
processor = VideoProcessor()


@router.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    audio_sensitivity: float = Form(0.3),
    merge_threshold: float = Form(0.8),
):
    """
    Process uploaded heavy bag training video to create montage of hits

    Args:
        file: Video file to process
        audio_sensitivity: RMS energy sensitivity threshold (0.0-1.0, default 0.3)
        merge_threshold: How close segments can be to merge them in seconds (0.1-5.0, default 0.8)

    Returns:
        Processing results with heavy bag montage
    """
    file_path = None
    start_time = datetime.now()

    logger.info(
        f"PROCESS: Starting heavy bag video processing for file: {file.filename}"
    )
    logger.info(
        f"PARAMS: Parameters - audio_sensitivity: {audio_sensitivity}, merge_threshold: {merge_threshold}s"
    )
    logger.info(
        f"SIZE: File size: {file.size} bytes"
        if file.size
        else "SIZE: File size: Unknown"
    )

    try:
        # Validate parameters
        logger.info("VALIDATE: Validating parameters...")
        if not (0.0 <= audio_sensitivity <= 1.0):
            logger.error(f"ERROR: Invalid audio sensitivity: {audio_sensitivity}")
            raise HTTPException(
                status_code=400,
                detail="Audio sensitivity must be between 0.0 and 1.0",
            )

        if not (0.1 <= merge_threshold <= 5.0):
            logger.error(f"ERROR: Invalid merge threshold: {merge_threshold}s")
            raise HTTPException(
                status_code=400,
                detail="Merge threshold must be between 0.1 and 5.0 seconds",
            )

        # Save uploaded file
        logger.info("SAVE: Saving uploaded file...")
        file_path = await save_upload_file(file)
        logger.info(f"SUCCESS: File saved to: {file_path}")

        # Verify file exists after save
        if not os.path.exists(file_path):
            logger.error(f"ERROR: File not found after save: {file_path}")
            raise FileNotFoundError(f"File was not saved properly: {file_path}")

        file_size = os.path.getsize(file_path)
        logger.info(f"SIZE: Saved file size: {file_size} bytes")

        # Process heavy bag video
        logger.info("PROCESS: Starting heavy bag video processing...")
        processing_result = await processor.process_video(
            file_path=file_path,
            audio_sensitivity=audio_sensitivity,
            merge_threshold=merge_threshold,
        )

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"SUCCESS: Video processing completed in {processing_time:.2f} seconds"
        )

        # Clean up uploaded file after successful processing
        if file_path and os.path.exists(file_path):
            logger.info(
                f"CLEANUP: Cleaning up original file after successful processing: {file_path}"
            )
            cleanup_success = cleanup_file(file_path)
            if cleanup_success:
                logger.info("SUCCESS: Original file cleanup completed")
            else:
                logger.warning("WARNING: Original file cleanup failed")

        # Return processing results
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Heavy bag video processing completed successfully",
                "data": processing_result,
            },
        )

    except ValueError as e:
        logger.error(f"ERROR: ValueError: {str(e)}")
        # Clean up file on error
        if file_path and os.path.exists(file_path):
            logger.info(f"CLEANUP: Cleaning up file after ValueError: {file_path}")
            cleanup_file(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"ERROR: FileNotFoundError: {str(e)}")
        logger.error(f"ERROR: File path was: {file_path}")
        if file_path:
            logger.error(f"ERROR: File exists check: {os.path.exists(file_path)}")
        # Clean up file on error
        if file_path and os.path.exists(file_path):
            logger.info(
                f"CLEANUP: Cleaning up file after FileNotFoundError: {file_path}"
            )
            cleanup_file(file_path)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the full traceback for debugging
        error_trace = traceback.format_exc()
        logger.error(f"ERROR: Unexpected error in video processing: {error_trace}")
        # Clean up file on error
        if file_path and os.path.exists(file_path):
            logger.info(
                f"CLEANUP: Cleaning up file after unexpected error: {file_path}"
            )
            cleanup_file(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during video processing: {str(e)}",
        )
    # Note: Removed finally block - file cleanup only happens on success or error, not always


# Request model for combining segments
class CombineSegmentsRequest(BaseModel):
    segment_filenames: List[str]
    output_filename: Optional[str] = None


@router.post("/combine-segments")
async def combine_segments(request: CombineSegmentsRequest):
    """
    Combine selected segments into a new video file

    Args:
        request: Request containing segment filenames and optional output filename

    Returns:
        Combined video file information
    """
    start_time = datetime.now()

    logger.info(f"COMBINE: Starting segment combination")
    logger.info(f"COMBINE: Segments to combine: {request.segment_filenames}")
    logger.info(f"COMBINE: Output filename: {request.output_filename}")

    try:
        # Validate request
        if not request.segment_filenames:
            logger.error("COMBINE: No segments provided")
            raise HTTPException(
                status_code=400, detail="No segments provided for combining"
            )

        # Combine segments using video processor
        logger.info("COMBINE: Calling video processor to combine segments...")
        combine_result = await processor.combine_selected_segments(
            segment_filenames=request.segment_filenames,
            output_filename=request.output_filename,
        )

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"COMBINE: Segment combination completed in {processing_time:.2f} seconds"
        )

        # Return combination results
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Segments combined successfully",
                "data": combine_result,
            },
        )

    except ValueError as e:
        logger.error(f"COMBINE: ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"COMBINE: FileNotFoundError: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the full traceback for debugging
        error_trace = traceback.format_exc()
        logger.error(f"COMBINE: Unexpected error in segment combination: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during segment combination: {str(e)}",
        )


@router.get("/process-video/status/{task_id}")
async def get_processing_status(task_id: str):
    """
    Get processing status for a task (BOILERPLATE ONLY)
    """
    try:
        status = processor.get_processing_status(task_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Status retrieved successfully",
                "data": status,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get processing status: {str(e)}"
        )


@router.delete("/process-video/cancel/{task_id}")
async def cancel_processing(task_id: str):
    """
    Cancel a processing task (BOILERPLATE ONLY)
    """
    try:
        result = processor.cancel_processing(task_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Task cancelled successfully",
                "data": result,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel processing: {str(e)}"
        )


@router.get("/process-video/health")
async def process_health():
    """
    Health check endpoint for video processing service
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Video processing service is healthy (BOILERPLATE ONLY)",
            "status": "available",
            "note": "This is a boilerplate implementation",
        },
    )
