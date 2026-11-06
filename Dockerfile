# Multi-stage / Production Dockerfile for Hanoi Multi-Station Weather Forecasting API
# Base image pinned to Debian Bookworm Python 3.12 Slim
FROM python:3.12-slim-bookworm

# Set metadata and labels
LABEL maintainer="Hanoi Weather Forecasting Team <hanguynthun@kaggle.com>"
LABEL description="Inference serving image for Hanoi multi-station temperature forecasting using DINOv3"
LABEL version="1.0.0"

# Python execution environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    MODEL_CHECKPOINT_PATH="/app/checkpoints/dinov3_forecaster_best.pt" \
    SCALER_PATH="/app/artifacts/scaler.pkl" \
    CONFIG_PATH="/app/configs/dinov3.yaml"

# Install minimal OS dependencies needed for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group for hardened security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Set working directory
WORKDIR /app

# Copy dependency definition files first for optimal Docker layer caching
COPY requirements.txt ./

# Install python dependencies with pip (no cache, production build)
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with appropriate permissions for non-root execution
RUN mkdir -p /app/checkpoints /app/artifacts /app/configs /app/docs && \
    chown -R appuser:appgroup /app

# Copy application source code, configs, artifacts, and documentation
COPY --chown=appuser:appgroup src/ /app/src/
COPY --chown=appuser:appgroup configs/ /app/configs/
COPY --chown=appuser:appgroup artifacts/ /app/artifacts/
COPY --chown=appuser:appgroup docs/api_example.json /app/docs/api_example.json
COPY --chown=appuser:appgroup dinov3_model.py /app/dinov3_model.py

# Switch to non-root user
USER appuser

# Expose API serving port
EXPOSE 8000

# Container healthcheck using standard library urllib (does not require curl)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').getcode() == 200 else 1)"

# Entrypoint running production Uvicorn server
CMD ["uvicorn", "src.weather.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
