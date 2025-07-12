# Video Clipper Frontend

Modern Next.js frontend for video analysis and processing.

## Features

### 🎯 Two Main Modes

- **Analyze Video**: Extract detailed metadata from video files
- **Process Video**: Create montages by removing silent segments (boilerplate)

### 🎨 User Interface

- **Drag & Drop Upload**: Intuitive file upload with validation
- **Real-time Analysis**: Instant video metadata extraction
- **Processing Controls**: Adjustable silence threshold and audio sensitivity sliders
- **Progress Tracking**: Visual progress bars and status updates
- **Responsive Design**: Works on desktop and mobile devices

### 📊 Video Analysis Features

- File information (name, size, format)
- Video properties (resolution, FPS, codec, bitrate, aspect ratio)
- Audio properties (codec, channels, sample rate, bitrate)
- HDR detection
- Duration and file size display
- Organized metadata grid with visual icons

### ⚙️ Processing Features (Boilerplate)

- Silence threshold control (0.1-5.0 seconds)
- Audio sensitivity adjustment (10-100%)
- Processing progress indication
- Mock results display
- Download functionality structure

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom components
- **Icons**: Lucide React
- **File Upload**: React Dropzone
- **HTTP Client**: Axios
- **TypeScript**: Full type safety
- **Animations**: Custom CSS animations and transitions

## Setup & Installation

1. **Install dependencies**:

```bash
cd frontend
npm install
```

2. **Set up environment variables**:

```bash
# Create .env.local file
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run development server**:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles and Tailwind
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page component
├── components/
│   ├── VideoUpload.tsx      # Drag & drop upload component
│   ├── VideoAnalysis.tsx    # Video analysis results display
│   └── VideoProcessing.tsx  # Video processing controls
├── lib/
│   └── api.ts               # API utility functions
├── public/                  # Static assets
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Component Overview

### VideoUpload Component

- Drag & drop file upload with validation
- File type and size checking
- Visual feedback for drag states
- Error handling and display

### VideoAnalysis Component

- Metadata display in organized grid
- Category-based organization (File, Video, Audio)
- HDR detection highlighting
- Raw data toggle
- Loading and error states

### VideoProcessing Component

- Interactive sliders for settings
- Real-time value display
- Processing progress indication
- Results display with download button
- Mock data for demonstration

## API Integration

The frontend communicates with the FastAPI backend through:

- **POST /api/analyze-video** - Video metadata extraction
- **POST /api/process-video** - Video processing (boilerplate)
- **GET /api/health** - Server health check

## Styling & Design

### Design System

- **Primary Color**: Blue (#0ea5e9)
- **Typography**: Inter font family
- **Spacing**: Consistent 8px grid system
- **Shadows**: Layered shadow system
- **Animations**: Smooth transitions and hover effects

### Responsive Design

- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interactions
- Optimized for all screen sizes

## File Upload Validation

### Supported Formats

- MP4, AVI, MOV, MKV, WebM, M4V, FLV, WMV

### Validation Rules

- **No file size limits** - Supports large video files (15GB+)
- File type checking
- Drag & drop validation
- Error message display

## Error Handling

- Network error handling
- File validation errors
- Server response errors
- User-friendly error messages
- Graceful degradation

## Performance Optimizations

- Next.js automatic code splitting
- Image optimization
- CSS-in-JS with Tailwind
- Lazy loading of components
- Optimized bundle size

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Features

1. Create components in `components/` directory
2. Add API functions in `lib/api.ts`
3. Update main page in `app/page.tsx`
4. Add styling in `globals.css` or component-specific

### Styling Guidelines

- Use Tailwind utility classes
- Custom animations in `globals.css`
- Consistent spacing and typography
- Responsive design patterns

## Environment Variables

```bash
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_MAX_FILE_SIZE=104857600  # 100MB in bytes
```

## Known Issues

- Video processing is currently boilerplate only
- Requires backend server to be running
- Some advanced video formats may not be supported

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Update documentation
4. Test on multiple browsers
5. Ensure responsive design

## License

This project is part of the Video Clipper application suite.
