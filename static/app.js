"use strict";

const elements = {
  fileInput: document.getElementById("audioFile"),
  uploadBtn: document.getElementById("sendBtn"),
  startBtn: document.getElementById("start"),
  stopBtn: document.getElementById("stop"),
  player: document.getElementById("player"),
  transcribeRecordingBtn: document.getElementById("transcribeRecordingBtn"),
  statusDisplay: document.getElementById("status"),
  statusBadge: document.getElementById("statusBadge"),
  transcriptDiv: document.getElementById("transcript"),
  melImg: document.getElementById("mel"),
};

// --- Store recording data ---
let mediaRecorder;
let audioChunks = [];
let recordedAudioBlob = null;

function updateUI(state, message = "") {
  elements.uploadBtn.disabled = false;
  elements.startBtn.disabled = false;
  elements.stopBtn.disabled = true;
  elements.transcribeRecordingBtn.disabled = true;

  switch (state) {
    case "IDLE":
      elements.statusBadge.textContent = "Ready";
      elements.statusDisplay.textContent = "Select a file or start recording.";
      break;
    case "RECORDING":
      elements.startBtn.disabled = true;
      elements.stopBtn.disabled = false;
      elements.statusBadge.textContent = "Working";
      elements.statusDisplay.textContent = "Recording...";
      break;
    case "PROCESSING":
      elements.uploadBtn.disabled = true;
      elements.startBtn.disabled = true;
      elements.statusBadge.textContent = "Working";
      elements.statusDisplay.textContent = "Uploading and transcribing...";
      elements.transcriptDiv.textContent = "";
      elements.melImg.style.display = "none";
      break;
    case "RECORDING_READY":
      elements.transcribeRecordingBtn.disabled = false; // The only button that should be enabled
      elements.statusBadge.textContent = "Ready";
      elements.statusDisplay.textContent =
        "Recording is ready to be transcribed.";
      break;
    case "DONE":
      elements.statusBadge.textContent = "Ready";
      elements.statusDisplay.textContent = "Done.";
      if (recordedAudioBlob) elements.transcribeRecordingBtn.disabled = false;
      break;
    case "ERROR":
      elements.statusBadge.textContent = "Error";
      elements.statusDisplay.textContent = `Error: ${message}`;
      if (recordedAudioBlob) elements.transcribeRecordingBtn.disabled = false;
      break;
  }
}

async function sendForTranscription(formData) {
  updateUI("PROCESSING");
  try {
    const response = await fetch("/transcribe", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "An unknown error occurred.");
    }

    elements.transcriptDiv.textContent =
      data.transcription || "[No transcription found]";
    elements.melImg.src = data.mel_spectrogram;
    elements.melImg.style.display = "block";
    updateUI("DONE");
  } catch (err) {
    console.error("Transcription Error:", err);
    updateUI("ERROR", err.message);
  }
}
// --- Main Setup ---

// 1. Handle File Upload
elements.uploadBtn.addEventListener("click", () => {
  if (!elements.fileInput.files.length) {
    alert("Please choose an audio file first.");
    return;
  }
  const formData = new FormData();
  formData.append("file", elements.fileInput.files[0]);
  sendForTranscription(formData);
});

// 2. Handle Live Recording
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  elements.startBtn.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);

      mediaRecorder.onstop = () => {
        recordedAudioBlob = new Blob(audioChunks, { type: "audio/webm" });
        elements.player.src = URL.createObjectURL(recordedAudioBlob);
        updateUI("RECORDING_READY");
      };

      mediaRecorder.start();
      updateUI("RECORDING");
    } catch (err) {
      updateUI("ERROR", "Could not access microphone.");
    }
  });

  elements.stopBtn.addEventListener("click", () => mediaRecorder.stop());

  elements.transcribeRecordingBtn.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("file", recordedAudioBlob, "recording.webm");
    sendForTranscription(formData);
  });
} else {
  // If the browser doesn't support recording, disable the feature
  updateUI("ERROR", "Live recording is not supported on your browser.");
  elements.startBtn.disabled = true;
}

// Set the initial state of the page on load
updateUI("IDLE");
