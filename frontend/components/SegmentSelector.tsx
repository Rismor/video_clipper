"use client";

import { useState } from "react";
import { Play, Download, Settings } from "lucide-react";

interface SegmentInfo {
  segment_number: number;
  filename: string;
  path: string;
  start_time: number;
  end_time: number;
  duration: number;
  size_bytes: number;
  size_mb: number;
}

interface SegmentSelectorProps {
  segments: SegmentInfo[];
  onCombineSelected: (selectedSegments: string[]) => void;
  isProcessing?: boolean;
}

export default function SegmentSelector({
  segments,
  onCombineSelected,
  isProcessing = false,
}: SegmentSelectorProps) {
  const [selectedSegments, setSelectedSegments] = useState<Set<string>>(
    new Set()
  );

  const toggleSegment = (filename: string) => {
    if (isProcessing) return;

    const newSelected = new Set(selectedSegments);
    if (newSelected.has(filename)) {
      newSelected.delete(filename);
    } else {
      newSelected.add(filename);
    }
    setSelectedSegments(newSelected);
  };

  const handleCombineSelected = () => {
    if (selectedSegments.size === 0 || isProcessing) return;
    onCombineSelected(Array.from(selectedSegments));
  };

  const selectAll = () => {
    if (isProcessing) return;
    setSelectedSegments(new Set(segments.map((s) => s.filename)));
  };

  const deselectAll = () => {
    if (isProcessing) return;
    setSelectedSegments(new Set());
  };

  // Get the proper video URL for playback
  const getVideoUrl = (path: string) => {
    const API_BASE_URL =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${API_BASE_URL}${path}`;
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (segments.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <Play className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">
              Individual Segments
            </h3>
            <p className="text-sm text-gray-600">
              {segments.length} segments detected
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={selectAll}
            disabled={isProcessing}
            className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            disabled={isProcessing}
            className="text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
          >
            Deselect All
          </button>
        </div>
      </div>

      {/* Segments Grid */}
      <div className="space-y-4 mb-6">
        {segments.map((segment) => (
          <div
            key={segment.filename}
            className={`
              border-2 rounded-lg p-4 transition-all duration-200
              ${
                selectedSegments.has(segment.filename)
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }
            `}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Left Column - Video */}
              <div className="space-y-3">
                <div className="bg-black rounded-lg overflow-hidden">
                  <video
                    controls
                    className="w-full h-auto"
                    style={{ maxHeight: "200px" }}
                    preload="metadata"
                  >
                    <source src={getVideoUrl(segment.path)} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>

                <div className="text-xs text-gray-500 flex justify-between">
                  <span>
                    {formatTime(segment.start_time)} -{" "}
                    {formatTime(segment.end_time)}
                  </span>
                  <span>{segment.size_mb} MB</span>
                </div>
              </div>

              {/* Right Column - Info & Toggle */}
              <div className="flex flex-col justify-between">
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold text-gray-800">
                      Segment {segment.segment_number}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Duration: {formatTime(segment.duration)}
                    </p>
                  </div>

                  <div className="text-xs text-gray-500">
                    <p>Start: {formatTime(segment.start_time)}</p>
                    <p>End: {formatTime(segment.end_time)}</p>
                    <p>Size: {segment.size_mb} MB</p>
                  </div>
                </div>

                {/* Apple-style Toggle Switch */}
                <div className="flex items-center justify-between mt-4">
                  <span className="text-sm font-medium text-gray-700">
                    Include in combo
                  </span>
                  <button
                    onClick={() => toggleSegment(segment.filename)}
                    disabled={isProcessing}
                    className={`
                      relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50
                      ${
                        selectedSegments.has(segment.filename)
                          ? "bg-blue-600"
                          : "bg-gray-200"
                      }
                    `}
                  >
                    <span
                      className={`
                        inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200
                        ${
                          selectedSegments.has(segment.filename)
                            ? "translate-x-6"
                            : "translate-x-1"
                        }
                      `}
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Combine Button */}
      <div className="border-t pt-6">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {selectedSegments.size === 0
              ? "No segments selected"
              : `${selectedSegments.size} segment${
                  selectedSegments.size === 1 ? "" : "s"
                } selected`}
          </div>

          <button
            onClick={handleCombineSelected}
            disabled={selectedSegments.size === 0 || isProcessing}
            className={`
              px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200
              ${
                selectedSegments.size === 0 || isProcessing
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg"
              }
            `}
          >
            {isProcessing ? (
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 animate-spin" />
                <span>Combining...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Download className="w-5 h-5" />
                <span>Combine Selected</span>
              </div>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
