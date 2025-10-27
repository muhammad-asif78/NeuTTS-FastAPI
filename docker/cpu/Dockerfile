FROM python:3.10-slim

# Install dependencies and check espeak location
# Rust is required to build some packages
RUN apt-get update -y &&  \
    apt-get install -y espeak-ng espeak-ng-data git libsndfile1 curl ffmpeg g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /usr/share/espeak-ng-data && \
    ln -s /usr/lib/*/espeak-ng-data/* /usr/share/espeak-ng-data/ && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/ && \
    mv /root/.local/bin/uvx /usr/local/bin/ && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./pyproject.toml

# Install dependencies with CPU extras
RUN uv venv --python 3.10 && \
    uv sync --extra cpu --no-cache

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
