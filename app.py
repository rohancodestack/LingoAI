# FastAPI-based backend for LingoAI (AI Audio Assistant)

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from gtts import gTTS
from googletrans import Translator
from io import BytesIO
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Mount templates & static folder
templates = Jinja2Templates(directory="templates")


# Translator
translator = Translator()

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

# Request body model
class AudioRequest(BaseModel):
    text: str
    language: str

# Route for main HTML UI
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("AudioTranslationUI.html", {"request": request})

# Endpoint to generate audio
@app.post("/generate-audio")
async def generate_audio(data: AudioRequest):
    if not data.text.strip():
        return {"error": "No text provided."}

    # Translate text if not English
    translated_text = data.text
    if data.language != "en":
        translated = translator.translate(data.text, dest=data.language)
        translated_text = translated.text

    # Generate audio using gTTS
    tts = gTTS(text=translated_text, lang=data.language, slow=False)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    return StreamingResponse(audio_bytes, media_type="audio/mpeg")

# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5050, reload=True)
