from fastapi import FastAPI
from api.src.routers.openai_compatible import (
    router as openai_router,
    get_tts,
    get_ref_codes,
    VOICE_REF_TEXT,
)

app = FastAPI()

app.include_router(openai_router, prefix="/v1")


@app.on_event("startup")
async def warmup_models():
    # Preload model and voice reference tensors so first request is faster.
    get_tts()
    for voice in VOICE_REF_TEXT:
        get_ref_codes(voice)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
