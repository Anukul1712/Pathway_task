# ==========================
# PATHWAY RAG System - Docker (Ollama Edition)
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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Disable pip cache
ENV PIP_NO_CACHE_DIR=1

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create app directory structure
RUN mkdir -p /app/app /app/data

# Copy application code
COPY app/ /app/app/

# Expose the API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/v1/statistics || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "-u", "app/main.py"]
