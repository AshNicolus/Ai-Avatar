
from typing import Optional
import os
import io

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse

from elevenlabs.client import AsyncElevenLabs

ELEVENLABS_API_KEY = "3356806df09a7ff4338bf3d36090f33081ad05ef1770253317d4aa40ef09600a"
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Please set ELEVENLABS_API_KEY environment variable")

client = AsyncElevenLabs(api_key=ELEVENLABS_API_KEY)
app = FastAPI(title="FastAPI + ElevenLabs TTS")


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = "eleven_multilingual_v2"
    output_format: Optional[str] = "mp3_44100_128"  # SDK/Docs allow formats like mp3_44100_128


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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
async def synthesize(req: TTSRequest):
    """
    Generate speech from text and return an MP3 stream.

    Request example (JSON):
    {
      "text": "Hello from ElevenLabs via FastAPI",
      "voice_id": "<your-voice-id>",
      "model_id": "eleven_multilingual_v2",
      "output_format": "mp3_44100_128"
    }
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def health():
    return JSONResponse({"status": "ok", "elevenlabs_key_present": True})


