from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from routes.video_analysis import router as video_analysis_router
from routes.video_processing import router as video_processing_router

# Create FastAPI app
app = FastAPI(
    title="Video Clipper API",
    description="API for video analysis and processing",
    version="1.0.0",
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - perfect for local network access
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include routers
app.include_router(video_analysis_router, prefix="/api")
app.include_router(video_processing_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Video Clipper API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # Configure uvicorn for large file uploads (15GB+)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=300,  # 5 minutes keep-alive
        limit_max_requests=1000,  # Allow many requests
        limit_concurrency=10,  # Allow concurrent uploads
    )
