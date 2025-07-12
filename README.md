# Video Clipper

A modern full-stack application for video analysis and processing, built with Next.js and FastAPI.

## 🎯 Features

### Video Analysis

- **Metadata Extraction**: Get detailed information about video files
- **HDR Detection**: Identify HDR content automatically
- **Audio Analysis**: Complete audio stream information
- **Format Support**: Wide range of video formats supported

### Video Processing (Boilerplate)

- **Montage Creation**: Remove silent segments (structure only)
- **Customizable Settings**: Adjustable silence threshold and audio sensitivity
- **Progress Tracking**: Real-time processing updates
- **Download Results**: Easy access to processed files

## 🏗️ Architecture

```
video_clipper/
├── frontend/          # Next.js React application
│   ├── app/          # Next.js 14 app router
│   ├── components/   # Reusable UI components
│   └── lib/          # API utilities
├── backend/          # FastAPI Python application
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   └── utils/        # Utility functions
├── uploads/          # Temporary upload directory
└── outputs/          # Processed file outputs
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+ and pip
- **FFmpeg** (for video analysis)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd video_clipper
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Install FFmpeg (Required for Video Analysis)

#### Windows

1. Download from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your PATH environment variable

#### macOS

```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

## 🔧 Configuration

### Environment Variables

#### Backend

No additional configuration required. The backend uses default settings.

#### Frontend

Create a `.env.local` file in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📖 Usage

### Video Analysis

1. Open the application in your browser
2. Select "Analyze Video" mode
3. Drag and drop a video file or click to browse
4. View detailed metadata including:
   - File information (name, size, format)
   - Video properties (resolution, FPS, codec, bitrate, HDR)
   - Audio properties (codec, channels, sample rate)

### Video Processing

1. Select "Process Video" mode
2. Upload a video file
3. Adjust settings:
   - **Silence Threshold**: Minimum duration of silence (0.1-5.0 seconds)
   - **Audio Sensitivity**: Sensitivity to audio changes (10-100%)
4. Click "Create Montage" to process
5. Download the processed video

> **Note**: Video processing currently returns mock data as it's implemented as boilerplate only.

## 🛠️ API Endpoints

### Video Analysis

- `POST /api/analyze-video` - Analyze video metadata
- `GET /api/analyze-video/health` - Service health check

### Video Processing

- `POST /api/process-video` - Process video (boilerplate)
- `GET /api/process-video/health` - Service health check

### General

- `GET /` - API root
- `GET /health` - General health check
- `GET /docs` - Swagger API documentation

## 🔍 Technical Details

### Backend (FastAPI)

- **Framework**: FastAPI with uvicorn
- **Video Analysis**: FFprobe for metadata extraction
- **File Handling**: Automatic cleanup and validation
- **Architecture**: Clean separation of routes, services, and utilities

### Frontend (Next.js)

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks
- **File Upload**: React Dropzone with validation

## 🎨 UI Features

- **Drag & Drop**: Intuitive file upload
- **Real-time Updates**: Live progress indicators
- **Responsive Design**: Works on all screen sizes
- **Visual Feedback**: Smooth animations and transitions
- **Error Handling**: User-friendly error messages

## 📁 File Support

### Supported Video Formats

- MP4, AVI, MOV, MKV, WebM, M4V, FLV, WMV

### File Size Limits

- **No file size limits** - Supports large video files (15GB+)
- Automatic file cleanup after processing

## 🔒 Security

- File type validation
- File size restrictions
- Automatic cleanup of temporary files
- CORS configuration for frontend access

## 📊 Performance

- Efficient file handling
- Automatic resource cleanup
- Optimized frontend bundle
- Responsive UI with smooth animations

## 🚧 Known Limitations

- **Video Processing**: Currently implemented as boilerplate only
- **File Size**: No limits - supports large video files (15GB+)
- **Concurrent Processing**: Single file processing at a time
- **Storage**: Temporary files are automatically cleaned up

## 🛠️ Development

### Backend Development

```bash
cd backend
# Install in development mode
pip install -r requirements.txt
# Run with auto-reload
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
# Install dependencies
npm install
# Run development server
npm run dev
```

### Project Structure

The project follows clean architecture principles:

- **Separation of Concerns**: Routes, services, and utilities are separate
- **Type Safety**: Full TypeScript implementation
- **Error Handling**: Comprehensive error handling throughout
- **Documentation**: Extensive inline documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is installed and in PATH
2. **CORS errors**: Check that backend is running on port 8000
3. **File upload fails**: Verify file format requirements (no size limits)
4. **Server offline**: Ensure both backend and frontend servers are running

### Getting Help

1. Check the console for error messages
2. Verify all dependencies are installed
3. Ensure FFmpeg is properly installed
4. Check that both servers are running on correct ports

## 🎉 Acknowledgments

Built with modern web technologies:

- Next.js for the frontend framework
- FastAPI for the backend API
- Tailwind CSS for styling
- FFmpeg for video processing
- React Dropzone for file uploads
