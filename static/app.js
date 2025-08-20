"use strict";

document.getElementById("sendBtn").addEventListener("click", async () => {
  const status = document.getElementById("status");
  const statusBadge = document.getElementById("statusBadge");
  const transcript = document.getElementById("transcript");
  const melImg = document.getElementById("mel");
  const fileInput = document.getElementById("audioFile");

  if (!fileInput.files.length) {
    alert("Please choose an audio file first.");
    return;
  }

  const form = new FormData();
  form.append("file", fileInput.files[0]);

  status.textContent = "Uploading and transcribing...";
  statusBadge.textContent = "Working";
  transcript.textContent = "";
  melImg.removeAttribute("src");
  melImg.style.display = "none";

  try {
    const res = await fetch("/transcribe", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || "Request failed");
    }
    transcript.textContent = data.transcription || "";
    if (data.mel_spectrogram) {
      melImg.src = data.mel_spectrogram;
      melImg.style.display = "block";
    }
    status.textContent = "Done";
    statusBadge.textContent = "Ready";
  } catch (err) {
    console.error(err);
    status.textContent = "Error: " + err.message;
    statusBadge.textContent = "Error";
    statusBadge.classList.add("error", "dot");
  }
});
