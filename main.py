import whisper
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import base64
import shutil
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Voice Cloning",)

try:
    model = whisper.load_model("tiny")
    print("Whisper model loaded successfully")
except Exception as e:
    print(f"Error loading whisper model: {e}")
    model = None

# Initialize Coqui TTS model for voice cloning
try:
    from coqui_tts.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    print("Coqui TTS model loaded successfully")
except Exception as e:
    print(f"Error loading Coqui TTS model: {e}")
    tts = None

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return HTMLResponse(content=open("static/index.html", "r").read())

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not model:
        return JSONResponse(content={"error":"Whisper model is not available"})
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        print(f"Transcribing File: {temp_file_path}")
        
        # Robustly load audio using Whisper's loader (handles webm/ogg via ffmpeg)
        audio = whisper.load_audio(temp_file_path)
        sr = 16000  # whisper.load_audio returns 16kHz mono float32

        # Build mel spectrogram for display
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(mel_spec_db, sr=sr, x_axis="time", y_axis="mel")
        plt.colorbar(label="dB")
        plt.title('Mel Spectrogram')
        
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        img_b64 = base64.b64encode(buffer.read()).decode()
        mel_plot = f"data:image/png;base64,{img_b64}"
        plt.close()
        
        # Transcribe directly from the loaded audio array
        result = model.transcribe(audio=audio, fp16=False)
        
        return {
            "transcription": result["text"],
            "mel_spectrogram": mel_plot
        }
    
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred during transcription: {str(e)}"}, status_code=500)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")

@app.post("/clone-voice")
async def clone_voice(
    text: str = Form(...),
    ref_voice: UploadFile = File(...)
):
    if not tts:
        return JSONResponse(content={"error": "Coqui TTS model is not available"})
    
    temp_file_path = None
    output_file_path = None
    try:
        # Save reference voice file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(ref_voice.filename)[1]) as temp_file:
            content = await ref_voice.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"Reference voice saved: {temp_file_path}")
        
        # Create output file path
        output_file_path = tempfile.mktemp(suffix=".wav")
        
        print(f"Generating voice with Coqui TTS...")
        # Generate voice using Coqui TTS
        tts.tts_to_file(
            text=text,
            file_path=output_file_path,
            speaker_wav=temp_file_path,
            language="en"
        )
        
        # Convert audio to base64
        with open(output_file_path, "rb") as f:
            audio_data = f.read()
        audio_b64 = base64.b64encode(audio_data).decode()
        
        return {
            "audio": f"data:audio/wav;base64,{audio_b64}"
        }
    
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred during voice cloning: {str(e)}"}, status_code=500)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up reference file: {temp_file_path}")
        if output_file_path and os.path.exists(output_file_path):
            os.remove(output_file_path)
            print(f"Cleaned up output file: {output_file_path}")