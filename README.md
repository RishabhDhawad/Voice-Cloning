# 🎧 Transcribe Audio (FastAPI + Whisper)

![Made with FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-tiny-6E56CF)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)

Minimal, fast, and friendly web app to transcribe audio and visualize its mel spectrogram.

The backend is built with FastAPI and OpenAI Whisper (tiny model by default). The frontend is plain HTML/CSS/JS for zero-friction usage.

## ✨ Features

* **Upload audio** from your device.
* **Record in browser** (Start/Stop) and transcribe with one click.
* **One-click transcription** using Whisper.
* **Mel spectrogram** generated with librosa + matplotlib, rendered inline as an image.
* **Minimal JS** — most logic lives in FastAPI.

## 🧰 Tech Stack

* **Backend:** FastAPI, Uvicorn, OpenAI Whisper, Librosa, NumPy, Matplotlib
* **Frontend:** Vanilla HTML/CSS/JS

## 📁 Project Structure

```
.
├─ main.py                 # FastAPI app with / and /transcribe endpoints
├─ requirements.txt        # All Python dependencies (FastAPI, Whisper, Librosa, etc.)
├─ static/                 # Frontend assets
│  ├─ index.html           # UI (Start/Stop recording, upload)
│  ├─ style.css            # Styles
│  └─ app.js               # Minimal client-side logic
└─ README.md
```

Key endpoints/functions:

* `GET /` serves `static/index.html`.
* `POST /transcribe` handled by `transcribe_audio` in `main.py`.

## 🧩 Prerequisites

* Python 3.9+ recommended.
* ffmpeg installed and available on PATH (required by Whisper/librosa).
  - Windows: `choco install ffmpeg` (Chocolatey) or download from ffmpeg.org.
  - macOS: `brew install ffmpeg`.
  - Linux: `sudo apt-get install ffmpeg` (Debian/Ubuntu).

## 🚀 Setup

1) Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
```

2) Install dependencies

```bash
pip install -r requirements.txt

# PyTorch is required by Whisper. If not auto-installed, install one of:
# CPU-only example (Windows/Linux/macOS):
pip install torch --index-url https://download.pytorch.org/whl/cpu
# For CUDA builds, follow: https://pytorch.org/get-started
```

3) Run the server

```bash
uvicorn main:app --reload
# Open http://127.0.0.1:8000
```

## 🖥️ Usage (UI)

1. Open the app in your browser.

Upload a file:
* Choose a file (WAV/MP3/etc.) and click "Transcribe".

Record in browser:
* Click "Start Recording", then "Stop Recording".
* Click "Transcribe" to upload the captured audio.

Wait for status "Done"; see transcript and mel spectrogram below.

Notes:
* The UI includes an audio player for playback of recorded audio.
* The backend decodes uploads (including WebM/Opus from the browser) using ffmpeg via `whisper.load_audio`.
* You can switch to a larger Whisper model in `main.py` by changing `whisper.load_model("tiny")` to `"base"`, `"small"`, etc. Larger models are slower but more accurate.

## 🔌 API

Endpoint: `POST /transcribe`

Form-Data:
* `file`: the audio file (key must be `file`).

Response (200):

```json
{
  "transcription": "...",
  "mel_spectrogram": "data:image/png;base64,...."
}
```

Response (error):

```json
{
  "error": "An error occurred during transcription: ..."
}
```

## ⚙️ Configuration

Edit `main.py`:
* Model size: `model = whisper.load_model("tiny")` → `"base" | "small" | "medium" | "large"`.
* Device/precision: `fp16=False` forces CPU-friendly precision; enable fp16 on GPU.

## 🧯 Troubleshooting

* **Whisper model fails to load**: Ensure PyTorch installed correctly; try CPU wheel above or install via pytorch.org.
* **ffmpeg not found**: Install ffmpeg and confirm `ffmpeg -version` works in your terminal.
* **librosa/audioread errors**: Usually ffmpeg-related; also verify the audio file isn’t corrupted.
* **Browser recording uploads but fails to transcribe**: Confirm ffmpeg is on PATH and try again; WebM/Opus requires ffmpeg.
* **Slow inference**: Use `tiny`/`base` models or enable GPU (CUDA build of PyTorch + fp16).

## 🗺️ Roadmap / Ideas

* Language selection / translation.
* Word-level timestamps and subtitle export (.srt).
* Save spectrograms and transcripts to disk.
* Model/device selection UI, timestamps toggle.

## 🙏 Acknowledgements

* OpenAI Whisper: https://github.com/openai/whisper
* FastAPI: https://fastapi.tiangolo.com/
* librosa: https://librosa.org/

---

Made with 💖 by **Rishabh Dhawad**.