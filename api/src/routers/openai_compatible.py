from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import torch
import io
import soundfile as sf
from neuttsair.neutts import NeuTTSAir
import os

# Pydantic model for the request
class SpeechRequest(BaseModel):
    input: str
    voice: str  # e.g., 'dave' or 'jo'

# Router
router = APIRouter()

# Global TTS instance (for simplicity, CPU only)
tts = None

def get_tts():
    global tts
    if tts is None:
        tts = NeuTTSAir(
            backbone_repo="neuphonic/neutts-air",
            backbone_device="cpu",
            codec_repo="neuphonic/neucodec",
            codec_device="cpu"
        )
    return tts

# Hardcoded ref_text for voices (minimal implementation)
VOICE_REF_TEXT = {
    'dave': "So I'm live on radio. And I say, well, my dear friend James here clearly, and the whole room just froze. Turns out I'd completely misspoken and mentioned our other friend.",
    'jo': "So I'm live on radio. And I say, well, my dear friend James here clearly, and the whole room just froze. Turns out I'd completely misspoken and mentioned our other friend."  # Placeholder, adjust as needed
}

@router.post("/audio/speech")
async def create_speech(request: SpeechRequest):
    if request.voice not in VOICE_REF_TEXT:
        raise HTTPException(status_code=400, detail=f"Voice '{request.voice}' not supported. Available: {list(VOICE_REF_TEXT.keys())}")
    
    # Load voice model
    voice_path = f"api/src/voices/{request.voice}.pt"
    if not os.path.exists(voice_path):
        raise HTTPException(status_code=400, detail=f"Voice file '{voice_path}' not found")
    
    ref_codes = torch.load(voice_path, map_location='cpu')
    
    # Get TTS
    tts = get_tts()
    
    # Perform inference
    wav = tts.infer(request.input, ref_codes, VOICE_REF_TEXT[request.voice])
    
    # Convert to bytes
    buffer = io.BytesIO()
    sf.write(buffer, wav, 24000, format='WAV')
    buffer.seek(0)
    
    # Return as streaming response
    return StreamingResponse(buffer, media_type="audio/wav")
