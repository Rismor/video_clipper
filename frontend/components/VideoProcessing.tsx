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
  noiseThresholdPercent: number;
  paddingDuration: number;
}

interface ProcessingResult {
  success: boolean;
  message: string;
  input_file: string;
  output_file: string;
  output_path: string;
  settings: {
    noise_threshold_percent: number;
    padding_duration: number;
  };
  processing_stats: {
    hits_detected: number;
    total_duration: string;
    montage_duration: string;
    compression_ratio: number;
    time_saved: string;
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
    noiseThresholdPercent: 90.0,
    paddingDuration: 2.0,
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
            Heavy Bag Processing Settings
          </h2>
        </div>

        <div className="space-y-6">
          {/* Noise Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Noise Threshold: {settings.noiseThresholdPercent}%
            </label>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">50%</span>
              <input
                type="range"
                min="50"
                max="99"
                step="1"
                value={settings.noiseThresholdPercent}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    noiseThresholdPercent: parseFloat(e.target.value),
                  }))
                }
                className="slider flex-1"
                disabled={isProcessing}
              />
              <span className="text-sm text-gray-500">99%</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Only keep audio above this percentage of your loudest hit
            </p>
          </div>

          {/* Padding Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Padding Duration: {settings.paddingDuration}s
            </label>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">0.5s</span>
              <input
                type="range"
                min="0.5"
                max="10.0"
                step="0.5"
                value={settings.paddingDuration}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    paddingDuration: parseFloat(e.target.value),
                  }))
                }
                className="slider flex-1"
                disabled={isProcessing}
              />
              <span className="text-sm text-gray-500">10.0s</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              How much video to keep around each combo (split before/after)
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
                  <span>Create Heavy Bag Montage</span>
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
              Processing Heavy Bag Video
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
              <span className="loading-dots">Detecting heavy bag combos</span>
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
                  <span className="text-gray-600">Combos Detected:</span>
                  <span className="font-medium">
                    {result.processing_stats.hits_detected}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Original Duration:</span>
                  <span className="font-medium">
                    {result.processing_stats.total_duration}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Montage Duration:</span>
                  <span className="font-medium">
                    {result.processing_stats.montage_duration}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time Saved:</span>
                  <span className="font-medium">
                    {result.processing_stats.time_saved}
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
                  Noise Threshold: {result.settings.noise_threshold_percent}%
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Film className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Padding Duration: {result.settings.padding_duration}s
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
