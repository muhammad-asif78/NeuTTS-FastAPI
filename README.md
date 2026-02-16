# NeuTTS-FastAPI

FastAPI wrapper for NeuTTS with an OpenAI-compatible speech endpoint:

- `POST /v1/audio/speech`
- response: `audio/wav`

This repo is configured for CPU inference and includes Docker + local run options.

## What Was Updated Today (February 16, 2026)

Updated today: fixed import path, added startup warmup, improved WAV response and caching behavior, added GET playback fallback, added long-text chunking, and updated Docker CPU setup.

## Supported Voices

- `dave`
- `jo`

## Setup

### Option A: Docker (CPU)

```bash
cd docker/cpu
docker compose up --build -d
```

API base URL:

```text
http://localhost:8000
```

Stop:

```bash
docker compose down
```

### Option B: Local (uvicorn)

From repo root:

```bash
cd /path/to/NeuTTS-FastAPI
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
pip install fastapi "uvicorn[standard]" pydantic soundfile neutts
python3 -m uvicorn api.src.main:app --host 0.0.0.0 --port 8000
```

## How to Use

1. Open docs in browser:
   - `http://localhost:8000/docs`
2. Use `POST /v1/audio/speech` to generate speech.
3. Save or play the returned WAV bytes in frontend.

## API Reference

### POST `/v1/audio/speech`

Generate speech from input text.

Request JSON:

```json
{
  "input": "Hello, this is a test.",
  "voice": "dave"
}
```

Response:

- `200 OK`
- `Content-Type: audio/wav`
- body: WAV bytes

### GET `/v1/audio/speech`

Compatibility endpoint mainly for browser/docs playback:

- If `input` query param is provided, it synthesizes that text.
- If `input` is omitted, it returns the last generated audio from POST.

Example:

```bash
curl "http://localhost:8000/v1/audio/speech?input=Hello&voice=dave" --output hello.wav
```

## Test Commands

### Basic test

```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello from NeuTTS","voice":"dave"}' \
  --output speech.wav
```

### Long-text test

```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello, how are you lets they find the result in which i have facing the issue related to the output i which we work for the low latency and testing","voice":"dave"}' \
  --output long.wav
```

## Frontend Integration Notes

To avoid wrong/old playback:

1. Use POST response bytes directly as the audio source (Blob URL).
2. Avoid playing a stale static URL without cache-busting.
3. If you use GET playback, include explicit `input` and `voice` query params.
4. Open docs at `http://localhost:8000/docs` (use `localhost`, not `0.0.0.0` in browser).

## Latency Notes

- First request can still be slow on CPU because NeuTTS model load is heavy.
- Startup warmup is enabled in `api/src/main.py` to reduce first interactive request delay.
- Long input now runs in chunks and merges output WAV to improve correctness.

## Troubleshooting

### `404 /` in logs

Expected. Root route is not defined.

### `405 GET /v1/audio/speech`

If you still see this, restart server with latest code (old process still running).

### Audio player shows `0:00` or plays old output

- ensure server restart after latest changes
- hard refresh browser docs
- verify `POST` request is returning non-empty bytes
- use terminal `curl --output` to confirm generated file

### Push to upstream GitHub fails with `403`

You need write access to upstream repo. Push to your fork instead and open a PR.

## License

MIT License - see `LICENSE`.

## Acknowledgments

- [NeuTTS / Neuphonic](https://github.com/neuphonic/neutts-air)
- Inspired by Kokoro-FastAPI style API compatibility
