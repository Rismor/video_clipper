# Video Clipper Backend

FastAPI backend for video analysis and processing.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Video Analysis

- `POST /api/analyze-video` - Analyze video metadata
- `GET /api/analyze-video/health` - Health check for analysis service

### Video Processing (Boilerplate)

- `POST /api/process-video` - Process video (boilerplate only)
- `GET /api/process-video/status/{task_id}` - Get processing status
- `DELETE /api/process-video/cancel/{task_id}` - Cancel processing
- `GET /api/process-video/health` - Health check for processing service

### General

- `GET /` - Root endpoint
- `GET /health` - General health check

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── routes/
│   ├── __init__.py
│   ├── video_analysis.py   # Video analysis endpoints
│   └── video_processing.py # Video processing endpoints
├── services/
│   ├── __init__.py
│   ├── video_analyzer.py   # Video analysis logic
│   └── video_processor.py  # Video processing logic (boilerplate)
├── utils/
│   ├── __init__.py
│   └── file_utils.py       # File handling utilities
├── uploads/                # Temporary upload directory
├── outputs/                # Processed video outputs
└── requirements.txt        # Python dependencies
```

## Important Notes

- **Video Processing**: The video processing functionality is currently boilerplate only due to suspected issues with Python video processing libraries. It returns mock responses.
- **FFmpeg Required**: Video analysis requires FFmpeg to be installed and accessible in the system PATH.
- **File Cleanup**: Uploaded files are automatically cleaned up after processing to save disk space.
- **CORS**: Configured to allow requests from `http://localhost:3000` (Next.js default port).

## Development

The backend is structured following FastAPI best practices:

- **Routes**: Handle HTTP requests and responses
- **Services**: Contain business logic
- **Utils**: Provide utility functions
- **Separation of Concerns**: Each layer has a specific responsibility
