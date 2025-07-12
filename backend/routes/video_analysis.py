from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.video_analyzer import VideoAnalyzer
from utils.file_utils import save_upload_file, cleanup_file
import os
import traceback

router = APIRouter()

# Initialize video analyzer
analyzer = VideoAnalyzer()


@router.post("/analyze-video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze uploaded video file and return metadata

    Returns:
        - FPS
        - Resolution
        - HDR (yes/no)
        - Aspect ratio
        - Codec
        - Duration
        - Bitrate
        - File size
        - Audio info
    """
    file_path = None
    try:
        # Save uploaded file
        file_path = await save_upload_file(file)

        # Analyze video
        analysis_result = await analyzer.analyze_video(file_path)

        # Return analysis results
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Video analysis completed successfully",
                "data": analysis_result,
            },
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Log the full traceback for debugging
        error_trace = traceback.format_exc()
        print(f"Unexpected error in video analysis: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during video analysis: {str(e)}",
        )
    finally:
        # Clean up uploaded file
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)


@router.get("/analyze-video/health")
async def analyze_health():
    """
    Health check endpoint for video analysis service
    """
    try:
        # Check if ffprobe is available
        test_analyzer = VideoAnalyzer()
        ffprobe_path = test_analyzer.ffprobe_path

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Video analysis service is healthy",
                "ffprobe_path": ffprobe_path,
                "status": "available",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Video analysis service has issues",
                "error": str(e),
                "status": "unavailable",
            },
        )
