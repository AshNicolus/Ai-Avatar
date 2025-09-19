from typing import Optional
import os
import io
from typing import Optional
import os
import io
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse

from elevenlabs.client import AsyncElevenLabs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variable for security
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "3356806df09a7ff4338bf3d36090f33081ad05ef1770253317d4aa40ef09600a")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Please set ELEVENLABS_API_KEY environment variable")

client = AsyncElevenLabs(api_key=ELEVENLABS_API_KEY)
app = FastAPI(title="FastAPI + ElevenLabs TTS")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = "eleven_multilingual_v2"
    output_format: Optional[str] = "mp3_44100_128"

class ChatRequest(BaseModel):
    message: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = "eleven_multilingual_v2"
    output_format: Optional[str] = "mp3_44100_128"

@app.get("/voices")
async def list_voices():
    """Return list of voices from ElevenLabs for the authenticated user."""
    try:
        resp = await client.voices.search()
        voices = []
        for v in resp.voices:
            voices.append({
                "id": getattr(v, "id", None) or getattr(v, "voice_id", None),
                "name": getattr(v, "name", None),
                "preview": getattr(v, "preview_url", None) or getattr(v, "preview", None),
            })
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error fetching voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def synthesize(req: TTSRequest):
    """
    Generate speech from text and return an MP3 stream.
    """
    if not req.voice_id:
        raise HTTPException(status_code=400, detail="voice_id is required")
    try:
        audio_bytes = await client.text_to_speech.convert(
            text=req.text,
            voice_id=req.voice_id,
            model_id=req.model_id,
            output_format=req.output_format,
        )
        if hasattr(audio_bytes, "read"):
            data = audio_bytes.read()
        else:
            data = bytes(audio_bytes)
        stream = io.BytesIO(data)
        headers = {"Content-Disposition": "attachment; filename=tts.mp3"}
        return StreamingResponse(stream, media_type="audio/mpeg", headers=headers)
    except Exception as e:
        logger.error(f"Error in TTS synthesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Accepts a user message, generates a response (echo for now), and returns TTS audio.
    Extend this to use an LLM for smarter responses.
    """
    if not req.voice_id:
        raise HTTPException(status_code=400, detail="voice_id is required")
    # For now, just echo the user's message as the "bot" response
    bot_response = f"You said: {req.message}"
    try:
        audio_bytes = await client.text_to_speech.convert(
            text=bot_response,
            voice_id=req.voice_id,
            model_id=req.model_id,
            output_format=req.output_format,
        )
        if hasattr(audio_bytes, "read"):
            data = audio_bytes.read()
        else:
            data = bytes(audio_bytes)
        stream = io.BytesIO(data)
        headers = {"Content-Disposition": "attachment; filename=chat_response.mp3"}
        return StreamingResponse(stream, media_type="audio/mpeg", headers=headers)
    except Exception as e:
        logger.error(f"Error in chat TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health():
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "elevenlabs_key_present": bool(ELEVENLABS_API_KEY)})
        stream = io.BytesIO(data)
        headers = {"Content-Disposition": "attachment; filename=tts.mp3"}
        return StreamingResponse(stream, media_type="audio/mpeg", headers=headers)

    except Exception as e:
        logger.error(f"Error in TTS synthesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def health():
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "elevenlabs_key_present": bool(ELEVENLABS_API_KEY)})


