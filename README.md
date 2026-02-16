# NeuTTS-FastAPI

A FastAPI wrapper for NeuTTS-Air, providing an OpenAI-compatible text-to-speech API.

## Features

- **OpenAI-Compatible API**: Drop-in replacement for OpenAI's TTS API
- **CPU-Only Inference**: Optimized for CPU deployment
- **FastAPI Backend**: High-performance async API server
- **Docker Support**: Easy containerized deployment
- **Voice Cloning**: Support for custom voice models

## Today's Updates (February 16, 2026)

- Fixed local import path in `api/src/main.py` to avoid module import errors.
- Added startup warmup to preload NeuTTS model and voice reference tensors, reducing first-request cold-start delay.
- Improved `/v1/audio/speech` response handling:
  - returns full WAV bytes with explicit `Content-Length`
  - adds no-cache headers to prevent stale audio playback on frontend/docs
- Added `GET /v1/audio/speech` fallback behavior for docs/browser playback compatibility after POST.
- Added text chunking for long input in `api/src/routers/openai_compatible.py` so full text is synthesized instead of truncating to a short segment.
- Added in-memory caching for voice reference codes to reduce repeated per-request overhead.
- Updated Docker CPU setup:
  - removed dependency on missing root `pyproject.toml`
  - switched to direct pip install with CPU-only PyTorch wheels
  - removed problematic bind mounts in compose for better portability

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hasithdd/NeuTTS-FastAPI.git
   cd NeuTTS-FastAPI
   ```

2. **Build and run with Docker Compose:**
   ```bash
   cd docker/cpu
   docker-compose up --build
   ```

3. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/v1/audio/speech" \
     -H "Content-Type: application/json" \
     -d '{
       "input": "Hello, world!",
       "voice": "dave"
     }' \
     --output speech.wav
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install uv
   uv sync
   ```

2. **Run the server:**
   ```bash
   uv run uvicorn api.src.main:app --host 0.0.0.0 --port 8000
   ```

## API Usage

### POST /v1/audio/speech

Generate speech from text using the specified voice.

**Request Body:**
```json
{
  "input": "Text to convert to speech",
  "voice": "dave"
}
```

**Supported Voices:**
- `dave`: Male voice
- `jo`: Female voice

**Response:**
- Content-Type: `audio/wav`
- Body: WAV audio data

**Example:**
```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "dave"}' \
  --output hello.wav
```

## Project Structure

```
NeuTTS-FastAPI/
├── api/
│   └── src/
│       ├── main.py              # FastAPI application
│       ├── routers/
│       │   └── openai_compatible.py  # TTS endpoint
│       └── voices/              # Voice model files
│           ├── dave.pt
│           └── jo.pt
├── neutts-air/                  # NeuTTS-Air library
├── docker/
│   └── cpu/                     # Docker configuration
├── pyproject.toml               # Project dependencies
└── README.md
```

## Dependencies

- Python 3.10+
- NeuTTS-Air
- FastAPI
- PyTorch (CPU)
- SoundFile
- And other dependencies listed in `pyproject.toml`

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

## Roadmap

### Core Features
- [ ] **GPU Support**: Add CUDA acceleration for faster inference on GPU hardware
- [ ] **Voice Cloning**: Enable users to create custom voices from audio samples
- [ ] **Streaming Audio**: Implement real-time audio streaming for low-latency TTS
- [ ] **Multiple Audio Formats**: Support MP3, FLAC, and other popular audio formats
- [ ] **Batch Processing**: Allow processing multiple text inputs in a single request

### Enhanced Functionality
- [ ] **Web Interface**: Create a user-friendly web UI for testing and demonstration
- [ ] **Voice Mixing**: Combine multiple voices or adjust voice characteristics
- [ ] **Emotion Control**: Add parameters for controlling speech emotion and style
- [ ] **Multilingual Support**: Extend beyond English to support other languages
- [ ] **API Rate Limiting**: Implement request throttling and usage controls

### Technical Improvements
- [ ] **Performance Optimization**: Benchmark and optimize inference speed
- [ ] **Comprehensive Testing**: Add unit tests, integration tests, and CI/CD pipeline
- [ ] **API Documentation**: Generate interactive OpenAPI/Swagger documentation
- [ ] **Container Optimization**: Reduce Docker image size and improve startup time
- [ ] **Monitoring & Metrics**: Add logging, metrics, and health monitoring

## Contributing

See [Contributing.md](Contributing.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on [NeuTTS-Air](https://github.com/neuphonic/neutts-air)
- Inspired by [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)
