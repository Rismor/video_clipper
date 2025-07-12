"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileVideo, X, AlertCircle } from "lucide-react";

interface VideoUploadProps {
  onFileSelect: (file: File) => void;
  acceptedFiles?: string[];
  maxSize?: number;
  disabled?: boolean;
}

export default function VideoUpload({
  onFileSelect,
  acceptedFiles = [
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
    ".m4v",
    ".flv",
    ".wmv",
  ],
  maxSize, // No default size limit - allows large files like 15GB
  disabled = false,
}: VideoUploadProps) {
  const [uploadError, setUploadError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setUploadError(null);

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === "file-too-large") {
          setUploadError(
            maxSize
              ? `File too large. Maximum size is ${maxSize / (1024 * 1024)}MB`
              : "File too large for your system to handle"
          );
        } else if (rejection.errors[0]?.code === "file-invalid-type") {
          setUploadError(
            `Invalid file type. Supported formats: ${acceptedFiles.join(", ")}`
          );
        } else {
          setUploadError("File upload failed. Please try again.");
        }
        return;
      }

      // Handle accepted files
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        onFileSelect(file);
      }
    },
    [onFileSelect, acceptedFiles, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept: {
        "video/*": acceptedFiles,
      },
      maxFiles: 1,
      maxSize, // Will be undefined by default, allowing large files
      disabled,
    });

  const clearError = () => setUploadError(null);

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 transition-all duration-200 cursor-pointer
          ${isDragActive && !isDragReject ? "drag-over" : ""}
          ${isDragReject ? "drag-reject" : ""}
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
          ${
            !isDragActive && !isDragReject
              ? "border-gray-300 hover:border-primary-400 hover:bg-primary-50"
              : ""
          }
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center justify-center space-y-4">
          {isDragActive ? (
            isDragReject ? (
              <>
                <AlertCircle className="w-16 h-16 text-red-500" />
                <p className="text-lg font-medium text-red-600">
                  Invalid file type or size
                </p>
                <p className="text-sm text-red-500">
                  Please upload a valid video file
                  {maxSize && ` under ${maxSize / (1024 * 1024)}MB`}
                </p>
              </>
            ) : (
              <>
                <Upload className="w-16 h-16 text-primary-500 animate-bounce" />
                <p className="text-lg font-medium text-primary-600">
                  Drop your video here
                </p>
              </>
            )
          ) : (
            <>
              <FileVideo className="w-16 h-16 text-gray-400" />
              <div className="text-center">
                <p className="text-lg font-medium text-gray-700">
                  Drag & drop a video file here
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse files
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-400">
                  Supported formats: {acceptedFiles.join(", ")}
                </p>
                <p className="text-xs text-gray-400">
                  {maxSize
                    ? `Maximum size: ${maxSize / (1024 * 1024)}MB`
                    : "No file size limit - supports large video files"}
                </p>
              </div>
            </>
          )}
        </div>

        {disabled && (
          <div className="absolute inset-0 bg-gray-200 bg-opacity-50 rounded-xl flex items-center justify-center">
            <p className="text-gray-600 font-medium">Upload disabled</p>
          </div>
        )}
      </div>

      {uploadError && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-sm text-red-700">{uploadError}</p>
          </div>
          <button
            onClick={clearError}
            className="text-red-500 hover:text-red-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
