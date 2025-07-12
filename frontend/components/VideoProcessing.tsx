"use client";

import { useState } from "react";
import {
  Settings,
  Play,
  Pause,
  Download,
  Clock,
  Film,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

interface ProcessingSettings {
  silenceThreshold: number;
  audioSensitivity: number;
}

interface ProcessingResult {
  success: boolean;
  message: string;
  input_file: string;
  output_file: string;
  output_path: string;
  settings: ProcessingSettings;
  processing_stats: {
    segments_found: number;
    total_duration: string;
    processed_duration: string;
    compression_ratio: number;
  };
  note?: string;
}

interface VideoProcessingProps {
  onProcess: (settings: ProcessingSettings) => Promise<void>;
  isProcessing?: boolean;
  progress?: number;
  result?: ProcessingResult | null;
  error?: string | null;
}

export default function VideoProcessing({
  onProcess,
  isProcessing = false,
  progress = 0,
  result,
  error,
}: VideoProcessingProps) {
  const [settings, setSettings] = useState<ProcessingSettings>({
    silenceThreshold: 0.8,
    audioSensitivity: 0.3,
  });

  const handleProcess = async () => {
    await onProcess(settings);
  };

  const handleDownload = () => {
    if (result?.output_path) {
      // Create a download link
      const link = document.createElement("a");
      link.href = result.output_path;
      link.download = result.output_file;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      {/* Settings Panel */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <Settings className="w-6 h-6 text-primary-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">
            Processing Settings
          </h2>
        </div>

        <div className="space-y-6">
          {/* Silence Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Silence Threshold: {settings.silenceThreshold}s
            </label>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">0.1s</span>
              <input
                type="range"
                min="0.1"
                max="5.0"
                step="0.1"
                value={settings.silenceThreshold}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    silenceThreshold: parseFloat(e.target.value),
                  }))
                }
                className="slider flex-1"
                disabled={isProcessing}
              />
              <span className="text-sm text-gray-500">5.0s</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Minimum duration of silence to detect segment boundaries
            </p>
          </div>

          {/* Audio Sensitivity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Audio Sensitivity: {Math.round(settings.audioSensitivity * 100)}%
            </label>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">10%</span>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={settings.audioSensitivity}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    audioSensitivity: parseFloat(e.target.value),
                  }))
                }
                className="slider flex-1"
                disabled={isProcessing}
              />
              <span className="text-sm text-gray-500">100%</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Sensitivity to audio changes when detecting active segments
            </p>
          </div>

          {/* Process Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleProcess}
              disabled={isProcessing}
              className={`
                px-8 py-3 rounded-lg font-semibold text-white text-lg transition-all duration-200
                ${
                  isProcessing
                    ? "bg-gray-400 cursor-not-allowed"
                    : "btn-primary"
                }
              `}
            >
              {isProcessing ? (
                <div className="flex items-center space-x-2">
                  <Settings className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Play className="w-5 h-5" />
                  <span>Create Montage</span>
                </div>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {isProcessing && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="w-6 h-6 text-primary-500 animate-spin" />
            <h3 className="text-lg font-semibold text-gray-800">
              Processing Video
            </h3>
          </div>

          <div className="space-y-3">
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-500 h-3 rounded-full progress-bar"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Progress: {progress}%</span>
              <span className="loading-dots">Analyzing audio segments</span>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <h3 className="text-lg font-semibold text-red-700">
              Processing Failed
            </h3>
          </div>
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-gray-500 text-sm">
            Please try again with different settings or a different video file.
          </p>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800">
                Processing Complete
              </h3>
            </div>

            <button
              onClick={handleDownload}
              className="btn-primary flex items-center space-x-2"
            >
              <Download className="w-5 h-5" />
              <span>Download</span>
            </button>
          </div>

          {result.note && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-yellow-600" />
                <p className="text-sm text-yellow-800">{result.note}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* File Information */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                File Information
              </h4>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Input File:</span>
                  <span className="font-medium">{result.input_file}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Output File:</span>
                  <span className="font-medium">{result.output_file}</span>
                </div>
              </div>
            </div>

            {/* Processing Statistics */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Processing Statistics
              </h4>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Segments Found:</span>
                  <span className="font-medium">
                    {result.processing_stats.segments_found}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Original Duration:</span>
                  <span className="font-medium">
                    {result.processing_stats.total_duration}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Processed Duration:</span>
                  <span className="font-medium">
                    {result.processing_stats.processed_duration}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Compression Ratio:</span>
                  <span className="font-medium">
                    {Math.round(
                      result.processing_stats.compression_ratio * 100
                    )}
                    %
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Settings Used */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Settings Used
            </h4>
            <div className="flex space-x-6">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Silence Threshold: {result.settings.silenceThreshold}s
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Film className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Audio Sensitivity:{" "}
                  {Math.round(result.settings.audioSensitivity * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
