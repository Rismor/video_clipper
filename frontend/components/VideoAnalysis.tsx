"use client";

import { useState } from "react";
import {
  FileVideo,
  Clock,
  Monitor,
  Headphones,
  HardDrive,
  Settings,
  CheckCircle,
} from "lucide-react";

interface VideoAnalysisData {
  filename: string;
  resolution: string;
  fps: number;
  duration: string;
  duration_seconds: number;
  aspect_ratio: string;
  codec: string;
  bitrate: number;
  file_size: number;
  file_size_mb: number;
  hdr: boolean;
  audio: {
    codec: string;
    channels: number;
    sample_rate: number;
    bitrate: number;
  };
  format: string;
}

interface VideoAnalysisProps {
  data: VideoAnalysisData | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function VideoAnalysis({
  data,
  isLoading,
  error,
}: VideoAnalysisProps) {
  const [showRawData, setShowRawData] = useState(false);

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <Settings className="w-8 h-8 text-primary-500 animate-spin" />
            <h2 className="text-2xl font-bold text-gray-800">
              Analyzing Video
            </h2>
          </div>

          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileVideo className="w-8 h-8 text-red-500" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Analysis Failed
            </h2>
            <p className="text-red-600 mb-4">{error}</p>
            <p className="text-gray-500 text-sm">
              Please try uploading a different video file.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const formatBitrate = (bitrate: number) => {
    if (bitrate === 0) return "Unknown";
    return bitrate > 1000000
      ? `${(bitrate / 1000000).toFixed(1)} Mbps`
      : `${(bitrate / 1000).toFixed(0)} kbps`;
  };

  const formatSampleRate = (sampleRate: number) => {
    if (sampleRate === 0) return "Unknown";
    return `${(sampleRate / 1000).toFixed(1)} kHz`;
  };

  const analysisItems = [
    {
      icon: <FileVideo className="w-5 h-5" />,
      label: "Filename",
      value: data.filename,
      category: "file",
    },
    {
      icon: <Monitor className="w-5 h-5" />,
      label: "Resolution",
      value: data.resolution,
      category: "video",
    },
    {
      icon: <Monitor className="w-5 h-5" />,
      label: "Aspect Ratio",
      value: data.aspect_ratio,
      category: "video",
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: "FPS",
      value: `${data.fps} fps`,
      category: "video",
    },
    {
      icon: <Clock className="w-5 h-5" />,
      label: "Duration",
      value: data.duration,
      category: "video",
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: "Video Codec",
      value: data.codec.toUpperCase(),
      category: "video",
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: "Video Bitrate",
      value: formatBitrate(data.bitrate),
      category: "video",
    },
    {
      icon: <CheckCircle className="w-5 h-5" />,
      label: "HDR",
      value: data.hdr ? "Yes" : "No",
      category: "video",
      highlight: data.hdr,
    },
    {
      icon: <HardDrive className="w-5 h-5" />,
      label: "File Size",
      value: `${data.file_size_mb} MB`,
      category: "file",
    },
    {
      icon: <Settings className="w-5 h-5" />,
      label: "Container",
      value: data.format.toUpperCase(),
      category: "file",
    },
  ];

  // Add audio info if available
  if (data.audio && data.audio.codec) {
    analysisItems.push(
      {
        icon: <Headphones className="w-5 h-5" />,
        label: "Audio Codec",
        value: data.audio.codec.toUpperCase(),
        category: "audio",
      },
      {
        icon: <Headphones className="w-5 h-5" />,
        label: "Audio Channels",
        value: `${data.audio.channels} channels`,
        category: "audio",
      },
      {
        icon: <Headphones className="w-5 h-5" />,
        label: "Sample Rate",
        value: formatSampleRate(data.audio.sample_rate),
        category: "audio",
      },
      {
        icon: <Headphones className="w-5 h-5" />,
        label: "Audio Bitrate",
        value: formatBitrate(data.audio.bitrate),
        category: "audio",
      }
    );
  }

  const categories = {
    file: { name: "File Information", color: "blue" },
    video: { name: "Video Properties", color: "green" },
    audio: { name: "Audio Properties", color: "purple" },
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 animate-fade-in">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800">
              Video Analysis Complete
            </h2>
          </div>

          <button
            onClick={() => setShowRawData(!showRawData)}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            {showRawData ? "Hide Raw Data" : "Show Raw Data"}
          </button>
        </div>

        {Object.entries(categories).map(([categoryKey, category]) => {
          const categoryItems = analysisItems.filter(
            (item) => item.category === categoryKey
          );
          if (categoryItems.length === 0) return null;

          return (
            <div key={categoryKey} className="mb-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center">
                <div
                  className={`w-3 h-3 rounded-full bg-${category.color}-500 mr-3`}
                ></div>
                {category.name}
              </h3>

              <div className="file-grid">
                {categoryItems.map((item, index) => (
                  <div
                    key={index}
                    className={`
                      p-4 rounded-lg border transition-all duration-200 card-hover
                      ${
                        item.highlight
                          ? "border-green-300 bg-green-50"
                          : "border-gray-200 bg-gray-50"
                      }
                    `}
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`
                        w-10 h-10 rounded-full flex items-center justify-center
                        ${
                          item.highlight
                            ? "bg-green-100 text-green-600"
                            : "bg-gray-100 text-gray-600"
                        }
                      `}
                      >
                        {item.icon}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-600">
                          {item.label}
                        </p>
                        <p
                          className={`text-lg font-semibold ${
                            item.highlight ? "text-green-700" : "text-gray-800"
                          }`}
                        >
                          {item.value}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {showRawData && (
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">
              Raw Analysis Data
            </h3>
            <pre className="text-sm text-gray-600 overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
