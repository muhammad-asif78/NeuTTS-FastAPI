from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import Response
import torch
import io
import soundfile as sf
from neuttsair.neutts import NeuTTSAir
import os
import re
import logging
import numpy as np
from typing import Optional

# Pydantic model for the request
class SpeechRequest(BaseModel):
    input: str
    voice: str  # e.g., 'dave' or 'jo'

# Router
router = APIRouter()
logger = logging.getLogger(__name__)

# Global TTS instance (for simplicity, CPU only)
tts = None
ref_codes_cache = {}
last_audio_bytes = None
last_audio_voice = None

AUDIO_WAV_RESPONSE = {
    200: {
        "description": "WAV audio stream",
        "content": {
            "audio/wav": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                }
            }
        },
    }
}

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


def get_ref_codes(voice: str):
    if voice in ref_codes_cache:
        return ref_codes_cache[voice]

    voice_path = os.path.join("api", "src", "voices", f"{voice}.pt")
    if not os.path.exists(voice_path):
        raise HTTPException(status_code=400, detail=f"Voice file '{voice_path}' not found")

    ref_codes = torch.load(voice_path, map_location="cpu")
    ref_codes_cache[voice] = ref_codes
    return ref_codes

# Hardcoded ref_text for voices (minimal implementation)
VOICE_REF_TEXT = {
    'dave': "So I'm live on radio. And I say, well, my dear friend James here clearly, and the whole room just froze. Turns out I'd completely misspoken and mentioned our other friend.",
    'jo': "So I'm live on radio. And I say, well, my dear friend James here clearly, and the whole room just froze. Turns out I'd completely misspoken and mentioned our other friend."  # Placeholder, adjust as needed
}


def split_text_for_tts(text: str, max_chars: int = 180) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= max_chars:
            chunks.append(sentence)
            continue

        # If a sentence is too long, split by words while preserving order.
        words = sentence.split()
        current = []
        current_len = 0
        for word in words:
            add_len = len(word) if not current else len(word) + 1
            if current and (current_len + add_len > max_chars):
                chunks.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += add_len
        if current:
            chunks.append(" ".join(current))

    return chunks


def synthesize_wav_bytes(input_text: str, voice: str) -> bytes:
    if voice not in VOICE_REF_TEXT:
        raise HTTPException(
            status_code=400,
            detail=f"Voice '{voice}' not supported. Available: {list(VOICE_REF_TEXT.keys())}",
        )

    chunks = split_text_for_tts(input_text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Input text is empty")

    logger.info("TTS request voice=%s chars=%d chunks=%d", voice, len(input_text), len(chunks))

    ref_codes = get_ref_codes(voice)
    tts_instance = get_tts()

    wav_chunks = []
    pause = np.zeros(int(0.08 * 24000), dtype=np.float32)
    with torch.inference_mode():
        for idx, chunk in enumerate(chunks):
            wav_part = np.asarray(
                tts_instance.infer(chunk, ref_codes, VOICE_REF_TEXT[voice]),
                dtype=np.float32,
            ).reshape(-1)
            if wav_part.size == 0:
                continue
            wav_chunks.append(wav_part)
            if idx < len(chunks) - 1:
                wav_chunks.append(pause)

    if not wav_chunks:
        raise HTTPException(status_code=500, detail="Generated audio is empty")

    wav = np.concatenate(wav_chunks, axis=0)

    buffer = io.BytesIO()
    sf.write(buffer, wav, 24000, format="WAV", subtype="PCM_16")
    audio_bytes = buffer.getvalue()

    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Generated audio is empty")

    return audio_bytes


def build_wav_response(audio_bytes: bytes, voice: str) -> Response:
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Content-Length": str(len(audio_bytes)),
            "Content-Disposition": f'inline; filename="{voice}.wav"',
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.post("/audio/speech", response_class=Response, responses=AUDIO_WAV_RESPONSE)
async def create_speech(request: SpeechRequest):
    global last_audio_bytes, last_audio_voice
    audio_bytes = synthesize_wav_bytes(request.input, request.voice)
    last_audio_bytes = audio_bytes
    last_audio_voice = request.voice
    return build_wav_response(audio_bytes, request.voice)


@router.get("/audio/speech", response_class=Response, responses=AUDIO_WAV_RESPONSE)
async def get_speech(
    input: Optional[str] = Query(default=None, description="Text to convert to speech"),
    voice: str = Query(default="dave", description="Voice id (dave or jo)"),
):
    global last_audio_bytes, last_audio_voice

    # Swagger UI audio widget often issues GET after a successful POST.
    # Return the latest generated WAV when no query text is supplied.
    if input is None:
        if last_audio_bytes is None:
            raise HTTPException(
                status_code=400,
                detail="No generated audio available yet. Send POST /v1/audio/speech first.",
            )
        return build_wav_response(last_audio_bytes, last_audio_voice or voice)

    audio_bytes = synthesize_wav_bytes(input, voice)
    last_audio_bytes = audio_bytes
    last_audio_voice = voice
    return build_wav_response(audio_bytes, voice)
