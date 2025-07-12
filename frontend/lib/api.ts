import axios from "axios";

// Dynamic API URL based on current host
const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    console.log("🔧 Using API URL from env:", process.env.NEXT_PUBLIC_API_URL);
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // If running in browser, use the same host as the frontend
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    const apiUrl = `http://${host}:8000`;
    console.log("🌐 Dynamic API URL:", apiUrl, "from hostname:", host);
    return apiUrl;
  }

  // Fallback for server-side rendering
  console.log("🔧 Using localhost fallback (server-side)");
  return "http://localhost:8000";
};

// Create axios instance with dynamic base URL
const createApiInstance = () => {
  return axios.create({
    baseURL: getApiBaseUrl(),
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// Video Analysis API
export const analyzeVideo = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const api = createApiInstance();
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

// Heavy Bag Video Processing API
export const processVideo = async (
  file: File,
  settings: { audioSensitivity: number; mergeThreshold: number }
) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("audio_sensitivity", settings.audioSensitivity.toString());
  formData.append("merge_threshold", settings.mergeThreshold.toString());

  try {
    const api = createApiInstance();
    const response = await api.post("/api/process-video", formData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Failed to process heavy bag video"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

// Combine Selected Segments API
export const combineSegments = async (
  segmentFilenames: string[],
  outputFilename?: string
) => {
  try {
    const api = createApiInstance();
    const response = await api.post(
      "/api/combine-segments",
      {
        segment_filenames: segmentFilenames,
        output_filename: outputFilename,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Failed to combine segments"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

// Health Check APIs
export const checkAnalysisHealth = async () => {
  try {
    const api = createApiInstance();
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
    const api = createApiInstance();
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
    const api = createApiInstance();
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || "Server unavailable");
    }
    throw new Error("An unexpected error occurred");
  }
};

// Export the URL function for use in components
export const getApiUrl = getApiBaseUrl;
