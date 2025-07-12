# 🥊 Kickboxing Montage Creator

Automatically create epic montages from your kickboxing training videos by cutting out dead silence and keeping only the action-packed sequences!

## Features

- **Smart Audio Analysis**: Automatically detects punch sequences vs silence
- **Drag & Drop Interface**: Simple web interface for uploading videos
- **Configurable Settings**: Adjust silence threshold and audio sensitivity
- **High-Quality Output**: Maintains original video quality in MP4 format
- **Continuous Montage**: Stitches all active sequences into one epic video

## Prerequisites

Before you start, make sure you have:

1. **Python 3.8+** installed
2. **FFmpeg** installed and available in your system PATH
3. At least 2GB of free disk space for processing

### Installing FFmpeg

**Windows:**

- Download from https://ffmpeg.org/download.html
- Extract and add the `bin` folder to your PATH

**macOS:**

```bash
brew install ffmpeg
```

**Linux:**

```bash
sudo apt update
sudo apt install ffmpeg
```

## Setup Instructions

1. **Clone or download this project**

   ```bash
   git clone <your-repo-url>
   cd video_clipper
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python app.py
   ```

4. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## How to Use

1. **Upload Video**: Drag and drop your kickboxing training video (MP4 format)
2. **Adjust Settings**:
   - **Silence Threshold**: How long silence before cutting (default: 0.8s)
   - **Audio Sensitivity**: How sensitive to detect sounds (default: 0.3)
3. **Click "Create Montage"** and wait for processing
4. **Download** your epic montage!

## Settings Guide

### Silence Threshold

- **Lower values (0.1-0.5s)**: More aggressive cutting, removes short pauses
- **Higher values (1.0-2.0s)**: Only removes longer silence periods

### Audio Sensitivity

- **Lower values (0.1-0.3)**: More sensitive, catches quieter sounds
- **Higher values (0.4-0.8)**: Less sensitive, only loud punches

## Tips for Best Results

- **Clear Audio**: Make sure your video has good audio quality
- **Consistent Volume**: Try to maintain consistent punch intensity
- **Avoid Background Noise**: Minimize music or talking during recording
- **Good Lighting**: While not required for audio analysis, helps with final video quality

## Troubleshooting

### "No active segments found"

- Try lowering the audio sensitivity (0.1-0.2)
- Check if your video has audio
- Ensure there are actual sounds in your video

### "FFmpeg not found"

- Make sure FFmpeg is installed and in your PATH
- Try restarting your terminal after installation

### Processing takes too long

- Large videos (>100MB) may take several minutes
- Check your available disk space
- Close other applications to free up memory

### Poor quality output

- Check your input video quality
- Ensure stable internet connection during processing

## Technical Details

The app uses:

- **Flask** for the web server
- **librosa** for audio analysis
- **moviepy** for video processing
- **FFmpeg** for media encoding

## File Structure

```
video_clipper/
├── app.py              # Main Flask application
├── index.html          # Frontend interface
├── styles.css          # Styling
├── script.js           # Frontend logic
├── requirements.txt    # Python dependencies
├── uploads/            # Temporary upload folder
└── outputs/            # Processed video outputs
```

## Support

If you encounter issues:

1. Check the console output for error messages
2. Ensure all prerequisites are installed
3. Try with a smaller video file first
4. Check that your video has clear audio

---

**Built with ❤️ for kickboxing enthusiasts! 🥊**
