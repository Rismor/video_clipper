// DOM elements
const dropZone = document.getElementById("dropZone");
const videoInput = document.getElementById("videoInput");
const controls = document.getElementById("controls");
const processBtn = document.getElementById("processBtn");
const progressSection = document.getElementById("progressSection");
const progressFill = document.getElementById("progressFill");
const progressText = document.getElementById("progressText");
const resultSection = document.getElementById("resultSection");
const resultVideo = document.getElementById("resultVideo");
const downloadBtn = document.getElementById("downloadBtn");

let selectedFile = null;

// Drag and drop event listeners
dropZone.addEventListener("click", () => {
  videoInput.click();
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect(files[0]);
  }
});

// File input event listener
videoInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

// Handle file selection
function handleFileSelect(file) {
  // Accept video files or MAV files (which might not have proper MIME type)
  if (
    !file.type.startsWith("video/") &&
    !file.name.toLowerCase().endsWith(".mav")
  ) {
    alert("Please select a video file (MP4, MAV, etc.)! 🎬");
    return;
  }

  if (file.size > 12 * 1024 * 1024 * 1024) {
    // 12GB limit
    alert("File is too large! Please select a video smaller than 12GB. 📏");
    return;
  }

  selectedFile = file;

  // Update UI with size warning for large files
  const sizeInMB = file.size / 1024 / 1024;
  const sizeInGB = sizeInMB / 1024;
  const sizeText =
    sizeInGB > 1 ? `${sizeInGB.toFixed(2)} GB` : `${sizeInMB.toFixed(2)} MB`;
  const warningText =
    sizeInGB > 1
      ? `<p class="help-text" style="color: #ff9800;">⚠️ Large file - processing may take 10-30 minutes!</p>`
      : "";

  dropZone.innerHTML = `
        <div class="drop-zone-content">
            <div class="upload-icon">✅</div>
            <h3>Video Selected!</h3>
            <p>${file.name}</p>
            <p class="help-text">Size: ${sizeText}</p>
            ${warningText}
        </div>
    `;

  // Show controls
  controls.style.display = "block";
  processBtn.disabled = false;

  // Add click to change file
  dropZone.addEventListener("click", () => {
    videoInput.click();
  });
}

// Process button event listener
processBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Please select a video file first! 🎬");
    return;
  }

  const silenceThreshold = document.getElementById("silenceThreshold").value;
  const audioSensitivity = document.getElementById("audioSensitivity").value;

  // Disable button and show progress
  processBtn.disabled = true;
  progressSection.style.display = "block";
  resultSection.style.display = "none";

  try {
    await processVideo(selectedFile, silenceThreshold, audioSensitivity);
  } catch (error) {
    console.error("Error processing video:", error);
    alert("Error processing video! Please try again. 😔");
    processBtn.disabled = false;
    progressSection.style.display = "none";
  }
});

// Process video function
async function processVideo(file, silenceThreshold, audioSensitivity) {
  const formData = new FormData();
  formData.append("video", file);
  formData.append("silence_threshold", silenceThreshold);
  formData.append("audio_sensitivity", audioSensitivity);

  // Start progress animation
  let progress = 0;
  const progressInterval = setInterval(() => {
    progress += Math.random() * 10;
    if (progress >= 90) {
      progress = 90;
    }
    progressFill.style.width = progress + "%";

    const isLargeFile = file.size > 1024 * 1024 * 1024; // 1GB+

    if (progress < 20) {
      progressText.textContent = isLargeFile
        ? "Processing large file... This may take a while 🎵"
        : "Analyzing audio patterns... 🎵";
    } else if (progress < 40) {
      progressText.textContent = "Detecting punch sequences... 🥊";
    } else if (progress < 65) {
      progressText.textContent = isLargeFile
        ? "Cutting out silence... Almost there! ✂️"
        : "Cutting out silence... ✂️";
    } else if (progress < 85) {
      progressText.textContent = "Creating your epic montage... 🎬";
    } else {
      progressText.textContent = isLargeFile
        ? "Finalizing your montage... Patience pays off! 🎯"
        : "Almost done... 🎉";
    }
  }, 500);

  try {
    const response = await fetch("/api/process-video", {
      method: "POST",
      body: formData,
    });

    clearInterval(progressInterval);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Complete progress
    progressFill.style.width = "100%";
    progressText.textContent = "Processing complete! 🎉";

    // Get the processed video
    const blob = await response.blob();
    const videoUrl = URL.createObjectURL(blob);

    // Show result
    setTimeout(() => {
      progressSection.style.display = "none";
      resultSection.style.display = "block";
      resultSection.classList.add("show");

      resultVideo.src = videoUrl;
      downloadBtn.href = videoUrl;

      // Re-enable process button
      processBtn.disabled = false;
    }, 1000);
  } catch (error) {
    clearInterval(progressInterval);
    throw error;
  }
}

// Add some nice UX touches
document.addEventListener("DOMContentLoaded", () => {
  // Add file type validation
  const fileTypes = [
    "video/mp4",
    "video/mov",
    "video/avi",
    "video/wmv",
    ".mav",
  ];

  // Update sensitivity display
  const sensitivityInput = document.getElementById("audioSensitivity");
  sensitivityInput.addEventListener("input", (e) => {
    const value = e.target.value;
    let description = "";

    if (value <= 0.2) {
      description = "Very Sensitive (catches quiet sounds)";
    } else if (value <= 0.4) {
      description = "Sensitive (good for most videos)";
    } else if (value <= 0.6) {
      description = "Moderate (only clear sounds)";
    } else if (value <= 0.8) {
      description = "Less Sensitive (loud sounds only)";
    } else {
      description = "Very Low (only very loud sounds)";
    }

    const helpText = e.target.parentElement.querySelector(".help-text");
    helpText.textContent = description;
  });

  // Trigger initial update
  sensitivityInput.dispatchEvent(new Event("input"));
});

// Add keyboard shortcuts
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !processBtn.disabled && selectedFile) {
    processBtn.click();
  }
});

// Add visual feedback for processing
function addProcessingFeedback() {
  const style = document.createElement("style");
  style.textContent = `
        .processing {
            pointer-events: none;
            opacity: 0.7;
        }
        
        .processing * {
            cursor: wait !important;
        }
    `;
  document.head.appendChild(style);
}

addProcessingFeedback();
