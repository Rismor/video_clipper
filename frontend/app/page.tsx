"use client";

import { useState, useEffect } from "react";
import {
  FileVideo,
  BarChart3,
  Settings,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import VideoUpload from "@/components/VideoUpload";
import VideoAnalysis from "@/components/VideoAnalysis";
import VideoProcessing from "@/components/VideoProcessing";
import { analyzeVideo, processVideo, checkServerHealth } from "@/lib/api";

type Mode = "analyze" | "process";

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

export default function Home() {
  const [mode, setMode] = useState<Mode>("analyze");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [serverStatus, setServerStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");

  // Analysis state
  const [analysisData, setAnalysisData] = useState<VideoAnalysisData | null>(
    null
  );
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Processing state
  const [processingResult, setProcessingResult] =
    useState<ProcessingResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [processingError, setProcessingError] = useState<string | null>(null);

  // Check server health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await checkServerHealth();
        setServerStatus("online");
      } catch (error) {
        setServerStatus("offline");
      }
    };
    checkHealth();
  }, []);

  // Handle file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    // Reset states when new file is selected
    setAnalysisData(null);
    setAnalysisError(null);
    setProcessingResult(null);
    setProcessingError(null);
    setProcessingProgress(0);
  };

  // Handle video analysis
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisData(null);

    try {
      const result = await analyzeVideo(selectedFile);
      if (result.success) {
        setAnalysisData(result.data);
      } else {
        setAnalysisError(result.message || "Analysis failed");
      }
    } catch (error) {
      setAnalysisError(
        error instanceof Error ? error.message : "Analysis failed"
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle video processing
  const handleProcess = async (settings: {
    noiseThresholdPercent: number;
    paddingDuration: number;
  }) => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setProcessingError(null);
    setProcessingResult(null);
    setProcessingProgress(0);

    // Simulate progress for demo purposes
    const progressInterval = setInterval(() => {
      setProcessingProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 10;
      });
    }, 500);

    try {
      const result = await processVideo(selectedFile, settings);
      if (result.success) {
        setProcessingResult(result.data);
        setProcessingProgress(100);
      } else {
        setProcessingError(result.message || "Processing failed");
      }
    } catch (error) {
      setProcessingError(
        error instanceof Error ? error.message : "Processing failed"
      );
    } finally {
      setIsProcessing(false);
      clearInterval(progressInterval);
    }
  };

  // Handle mode change
  const handleModeChange = (newMode: Mode) => {
    setMode(newMode);
    // Reset states when mode changes
    setAnalysisData(null);
    setAnalysisError(null);
    setProcessingResult(null);
    setProcessingError(null);
    setProcessingProgress(0);
  };

  // Auto-analyze when file is selected in analyze mode
  useEffect(() => {
    if (mode === "analyze" && selectedFile && !isAnalyzing) {
      handleAnalyze();
    }
  }, [mode, selectedFile]);

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Heavy Bag Video Clipper
          </h1>
          <p className="text-xl text-gray-600">
            Analyze your videos and create combo montages of your heavy bag
            training
          </p>

          {/* Server Status */}
          <div className="mt-4 flex justify-center">
            <div
              className={`
              flex items-center space-x-2 px-3 py-1 rounded-full text-sm
              ${
                serverStatus === "online"
                  ? "bg-green-100 text-green-800"
                  : serverStatus === "offline"
                  ? "bg-red-100 text-red-800"
                  : "bg-gray-100 text-gray-800"
              }
            `}
            >
              {serverStatus === "online" ? (
                <CheckCircle className="w-4 h-4" />
              ) : serverStatus === "offline" ? (
                <AlertCircle className="w-4 h-4" />
              ) : (
                <Settings className="w-4 h-4 animate-spin" />
              )}
              <span>
                {serverStatus === "online"
                  ? "Server Online"
                  : serverStatus === "offline"
                  ? "Server Offline"
                  : "Checking Server..."}
              </span>
            </div>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-xl shadow-lg p-2 flex">
            <button
              onClick={() => handleModeChange("analyze")}
              className={`
                flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
                ${
                  mode === "analyze"
                    ? "bg-primary-600 text-white shadow-md"
                    : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                }
              `}
            >
              <BarChart3 className="w-5 h-5" />
              <span>Analyze Video</span>
            </button>
            <button
              onClick={() => handleModeChange("process")}
              className={`
                flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
                ${
                  mode === "process"
                    ? "bg-primary-600 text-white shadow-md"
                    : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
                }
              `}
            >
              <FileVideo className="w-5 h-5" />
              <span>Create Heavy Bag Montage</span>
            </button>
          </div>
        </div>

        {/* Upload Area */}
        <div className="mb-8 max-w-4xl mx-auto">
          <VideoUpload
            onFileSelect={handleFileSelect}
            disabled={serverStatus === "offline" || isAnalyzing || isProcessing}
          />
        </div>

        {/* Content based on mode */}
        {mode === "analyze" && (
          <VideoAnalysis
            data={analysisData}
            isLoading={isAnalyzing}
            error={analysisError}
          />
        )}

        {mode === "process" && selectedFile && (
          <VideoProcessing
            onProcess={handleProcess}
            isProcessing={isProcessing}
            progress={processingProgress}
            result={processingResult}
            error={processingError}
          />
        )}

        {/* Footer */}
        <div className="mt-16 text-center text-gray-500">
          <p className="text-sm">
            Upload a video file to get started. Supported formats: MP4, AVI,
            MOV, MKV, WebM, M4V, FLV, WMV
          </p>
        </div>
      </div>
    </div>
  );
}
