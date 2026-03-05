# Use official Python runtime
FROM python:3.12-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose backend port (Railway overrides this with $PORT at runtime)
EXPOSE ${PORT:-8000}

# Start FastAPI with Gunicorn using shell form so Railway's $PORT is expanded
CMD gunicorn -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
