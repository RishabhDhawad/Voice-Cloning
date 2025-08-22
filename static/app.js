"use strict";

const elements = {
  fileInput: document.getElementById("audioFile"),
  uploadBtn: document.getElementById("sendBtn"),
  startBtn: document.getElementById("start"),
  stopBtn: document.getElementById("stop"),
  player: document.getElementById("player"),
  transcribeRecordingBtn: document.getElementById("transcribeRecordingBtn"),
  statusDisplay: document.getElementById("status"),
  transcriptDiv: document.getElementById("transcript"),
  melImg: document.getElementById("mel"),
};

let mediaRecorder;
let audioChunks = [];
let recordedAudioBlob = null;

async function sendForTranscription(formData) {
  elements.statusDisplay.textContent = "Uploading and transcribing...";
  elements.uploadBtn.disabled = true;
  elements.startBtn.disabled = true;
  elements.stopBtn.disabled = true;
  elements.transcribeRecordingBtn.disabled = true;
  elements.transcriptDiv.textContent = "";
  elements.melImg.style.display = "none";
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
    elements.statusDisplay.textContent = "Done.";

    elements.uploadBtn.disabled = false;
    elements.startBtn.disabled = false;
    if (recordedAudioBlob) elements.transcribeRecordingBtn.disabled = false;
  } catch (err) {
    console.error("Transcription Error:", err);
    elements.statusDisplay.textContent = `Error: ${err.message}`;
    if (recordedAudioBlob) elements.transcribeRecordingBtn.disabled = false;
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
        elements.transcribeRecordingBtn.disabled = false;
        elements.statusDisplay.textContent = "Recording ready.";
        // stop tracks to release mic
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      elements.startBtn.disabled = true;
      elements.stopBtn.disabled = false;
      elements.statusDisplay.textContent = "Recording...";
    } catch (err) {
      elements.statusDisplay.textContent = "Error: Could not access microphone.";
    }
  });

  elements.stopBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    elements.stopBtn.disabled = true;
    elements.startBtn.disabled = false;
  });

  elements.transcribeRecordingBtn.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("file", recordedAudioBlob, "recording.webm");
    sendForTranscription(formData);
  });
} else {
  // If the browser doesn't support recording, disable the feature
  elements.statusDisplay.textContent = "Live recording is not supported on your browser.";
  elements.startBtn.disabled = true;
}

// Set the initial state of the page on load
elements.stopBtn.disabled = true;
elements.transcribeRecordingBtn.disabled = true;
elements.statusDisplay.textContent = "Select a file or start recording.";
