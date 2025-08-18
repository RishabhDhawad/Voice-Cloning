import whisper

model = whisper.load_model("tiny")
result = model.transcribe("harvard.wav")
print(result["text"])
