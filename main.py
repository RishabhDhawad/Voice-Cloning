import whisper
import os
import tempfile
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import librosa
import librosa.display
import base64
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import traceback
import torchaudio

app = FastAPI(title="Voice Cloning")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = whisper.load_model("tiny")
    print("Whisper model loaded successfully")
except Exception as e:
    print(f"Error loading whisper model: {e}")
    model = None


tts = None

try:
    from chatterbox.tts import ChatterboxTTS
    import torch

    print("Loading ChatterboxTTS...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = ChatterboxTTS.from_pretrained(device=device)
    print("ChatterboxTTS loaded successfully!")

except Exception:
    traceback.print_exc()
    tts = None

realtime_tts_available = False
try:
    from RealtimeTTS import TextToAudioStream, SystemEngine
    realtime_tts_available = True
    print("RealtimeTTS loaded successfully")
except Exception as e:
    print(f"Error loading RealtimeTTS: {e}")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="Whisper model is not available")

    temp_file_path = None
    try:
        suffix = os.path.splitext(file.filename or "")[1] or ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        print(f"Transcribing File: {temp_file_path}")

        audio = whisper.load_audio(temp_file_path)
        sr = 16000

        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(mel_spec_db, sr=sr, x_axis="time", y_axis="mel")
        plt.colorbar(label="dB")
        plt.title("Mel Spectrogram")

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        img_b64 = base64.b64encode(buffer.read()).decode()
        mel_plot = f"data:image/png;base64,{img_b64}"
        plt.close()

        result = model.transcribe(audio=audio, fp16=False)

        return {
            "transcription": result["text"],
            "mel_spectrogram": mel_plot,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")


@app.post("/clone-voice")
async def clone_voice(
    text: str = Form(...),
    ref_voice: UploadFile = File(...),
):
    if not tts and not realtime_tts_available:
        raise HTTPException(status_code=500, detail="No TTS engines (Chatterbox or RealtimeTTS) are available")

    temp_file_path = None
    output_file_path = None
    try:
        suffix = os.path.splitext(ref_voice.filename or "")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await ref_voice.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        print(f"Reference voice saved: {temp_file_path}")

        output_file_path = tempfile.mktemp(suffix=".wav")

        if tts:
            print(f"Generating voice with Chatterbox TTS...")
            wav = tts.generate(text, audio_prompt_path=temp_file_path)
            torchaudio.save(output_file_path, wav.cpu(), tts.sr)
        else:
            print(f"Generating speech with RealtimeTTS SystemEngine fallback...")
            engine = SystemEngine()
            stream = TextToAudioStream(engine)
            stream.feed(text)
            stream.play(output_wavfile=output_file_path, muted=True)
            try:
                engine.shutdown()
            except Exception:
                pass

        with open(output_file_path, "rb") as f:
            audio_data = f.read()
        audio_b64 = base64.b64encode(audio_data).decode()

        return {
            "audio": f"data:audio/wav;base64,{audio_b64}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during voice cloning: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up reference file: {temp_file_path}")
        if output_file_path and os.path.exists(output_file_path):
            os.remove(output_file_path)
            print(f"Cleaned up output file: {output_file_path}")
