# Base image: lightweight Python
FROM python:3.12-slim

# Expose port 8000
EXPOSE 8000

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app
COPY . /app

# Set PYTHONPATH so imports like 'from app.models' work correctly
ENV PYTHONPATH=/app

# Create non-root user and set permissions
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Start the FastAPI app with Gunicorn and Uvicorn worker
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]

