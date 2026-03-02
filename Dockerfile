# Use official Python 3.11 slim image — smaller than full Python
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed by lxml and httpx
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first — Docker caches this layer
# If requirements.txt hasn't changed, Docker skips pip install on rebuild
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY backend/ ./backend/

# Expose port 8000 so other services can reach the API
EXPOSE 8000

# Health check — Docker will restart container if this fails 3 times
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to start the FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]