import whisper
import os
import tempfile
import numpy as np
import matplotlib
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

try:
    model = whisper.load_model("tiny")
    print("Whisper model loaded succesfully")
except Exception as e:
    print(f"Error loading whisper model: {e}")
    model = None

@app.get("/")
def read_root():
    return {"message": "Whisper API is ready to transcribe audio!"}

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
        
        result = model.transcribe(temp_file_path, fp16=False) 
        
        return {"transcription": result["text"]}
    
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred during transcription: {str(e)}"}, status_code=500)
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temperory file: {temp_file_path}")
            