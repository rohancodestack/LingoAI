from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from gtts import gTTS
from googletrans import Translator
from io import BytesIO
from tasks import generate_audio_background
import uvicorn
import boto3

# Initialize FastAPI app
app = FastAPI()

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Translator
translator = Translator()

# S3 configuration
s3 = boto3.client("s3")
BUCKET_NAME = "lingo-ai-files"

# Supported languages
supported_languages = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "gu": "Gujarati",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "ur": "Urdu",
    "fr": "French",
    "es": "Spanish"
}

# Request model
class AudioRequest(BaseModel):
    text: str
    language: str

# Route to serve main UI
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("AudioTranslationUI.html", {"request": request})

# Async endpoint to generate audio
@app.post("/generate-audio")
async def generate_audio(data: AudioRequest):
    if not data.text.strip():
        return JSONResponse(status_code=400, content={"error": "No text provided."})

    # Dispatch background task
    task = generate_audio_background.delay(data.text, data.language)
    return {"task_id": task.id, "status": "Processing..."}

# Upload audio file to S3
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    s3.put_object(Bucket=BUCKET_NAME, Key=file.filename, Body=contents)
    return {"message": f"'{file.filename}' uploaded to S3 successfully."}

# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
