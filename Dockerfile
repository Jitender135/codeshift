# CodeShift Multi-Agent Migration System - Containerization Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Cloud healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

CMD ["python", "src/web/dashboard.py"]
