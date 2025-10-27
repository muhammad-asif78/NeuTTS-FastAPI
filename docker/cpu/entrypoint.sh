#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Starting NeuTTS FastAPI server on ${HOST}:${PORT}"

# Run the FastAPI application
exec uvicorn api.src.main:app --host $HOST --port $PORT