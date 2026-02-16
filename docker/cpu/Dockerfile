FROM python:3.10-slim

# Install minimal system dependencies needed for CPU inference
RUN apt-get update -y &&  \
    apt-get install -y --no-install-recommends espeak-ng espeak-ng-data git libsndfile1 curl ffmpeg g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /usr/share/espeak-ng-data && \
    ln -s /usr/lib/*/espeak-ng-data/* /usr/share/espeak-ng-data/ && \
    useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Install runtime dependencies directly (repo has no root pyproject.toml)
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch torchaudio && \
    /app/.venv/bin/pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        pydantic \
        soundfile \
        neutts

# Copy project files
COPY --chown=appuser:appuser api ./api
COPY --chown=appuser:appuser neutts-air ./neutts-air
COPY --chown=appuser:appuser docker/cpu/entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

# Set environment variables
ENV PATH="/home/appuser/.cargo/bin:/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/api:/app/neutts-air \
    UV_LINK_MODE=copy \
    PHONEMIZER_ESPEAK_PATH=/usr/bin \
    PHONEMIZER_ESPEAK_DATA=/usr/share/espeak-ng-data \
    ESPEAK_DATA_PATH=/usr/share/espeak-ng-data

# Run FastAPI server through entrypoint.sh
CMD ["./entrypoint.sh"]
