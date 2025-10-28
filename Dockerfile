# Multi-stage Dockerfile optimized for Render deployment
# Layer caching strategy: least frequently changed → most frequently changed

# ============================================================================
# Builder Stage: Install build dependencies and compile Python packages
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /tmp

# Environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install build dependencies needed for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY api/requirements.txt .

# Create virtual environment and install Python dependencies
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Runtime Stage: Minimal runtime environment with only necessary packages
# ============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Environment variables for optimized Python and real-time logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PATH="/opt/venv/bin:$PATH"

# Copy packages.txt and install runtime dependencies
COPY packages.txt /tmp/packages.txt

# Install runtime system packages from packages.txt
RUN apt-get update && \
    xargs -a /tmp/packages.txt apt-get install -y --no-install-recommends && \
    # Additional required packages for WeasyPrint and document processing
    apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY backend/ /app/backend/
COPY api/ /app/api/

# Set working directory to API
WORKDIR /app/api

# Expose concrete port (Render injects PORT at runtime)
EXPOSE 8000

# Use sh -c to allow environment variable expansion at runtime
# ${PORT:-8000} provides fallback to port 8000 if PORT is not set
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
