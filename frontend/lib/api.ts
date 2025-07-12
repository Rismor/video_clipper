import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

// Video Analysis API
export const analyzeVideo = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("/api/analyze-video", formData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Failed to analyze video"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

// Video Processing API
export const processVideo = async (
  file: File,
  settings: { silenceThreshold: number; audioSensitivity: number }
) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("silence_threshold", settings.silenceThreshold.toString());
  formData.append("audio_sensitivity", settings.audioSensitivity.toString());

  try {
    const response = await api.post("/api/process-video", formData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Failed to process video"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

// Health Check APIs
export const checkAnalysisHealth = async () => {
  try {
    const response = await api.get("/api/analyze-video/health");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Analysis service unavailable"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

export const checkProcessingHealth = async () => {
  try {
    const response = await api.get("/api/process-video/health");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Processing service unavailable"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

// General health check
export const checkServerHealth = async () => {
  try {
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || "Server unavailable");
    }
    throw new Error("An unexpected error occurred");
  }
};
