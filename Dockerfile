# Multi-stage build for minimal runtime image size and RAM usage
# Stage 1: Build & compilation
FROM python:3.10-slim AS builder

WORKDIR /build

# Install compiler tools needed to build C++ extensions (like insightface/numpy/scipy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies (OpenCV requires libgl1 and libglib2.0-0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY main.py .

# Pre-download and cache the InsightFace buffalo_s model weights during Docker build.
# This prevents network timeouts and RAM spikes during initial container startup on Render.
RUN python -c "from insightface.app import FaceAnalysis; model = FaceAnalysis(name='buffalo_s', root='.'); model.prepare(ctx_id=-1, det_size=(320, 320))"

# Expose API port
EXPOSE 8000

# Start FastAPI using a single worker to respect the strict 512MB RAM budget
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
