# Multi-stage Dockerfile for Migraine ML API
# Optimized for production deployment

# Stage 1: Builder
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

# Set metadata
LABEL maintainer="darish05"
LABEL description="Migraine Prediction ML API"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment path
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MLFLOW_TRACKING_URI=mlruns

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories
RUN mkdir -p mlruns models data reports logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with Gunicorn for production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]