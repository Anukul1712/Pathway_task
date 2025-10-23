# ==========================
# PATHWAY RAG System - Docker
# ==========================

FROM python:3.10-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy app dependencies first (for Docker layer caching)
COPY app/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir \
        langchain \
        langchain_google_genai \
        google-generativeai \
        requests \
        python-dotenv

# Copy all application code
COPY app/ /app/app/
COPY data/ /app/data/
COPY .env /app/.env

# Create data directory if not already there (for mounting)
RUN mkdir -p /app/data

# Expose the API port (for Pathway server)
EXPOSE 8080

# Health check for the Pathway REST endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/v1/statistics || exit 1

# Default command (can be overridden by docker-compose)
CMD ["python", "-u", "app/main.py"]
