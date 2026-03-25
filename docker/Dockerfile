# =============================================================================
# RIO Protocol — Docker Image
# =============================================================================
# Build:  docker build -f docker/Dockerfile -t rio-protocol .
# Run:    docker run -p 8050:8050 rio-protocol
# =============================================================================

FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r rio && useradd -r -g rio -m -s /bin/bash rio

# Set working directory
WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Fix ownership
RUN chown -R rio:rio /app

# Switch to non-root user
USER rio

# Initialize the system (creates data dirs, keys, seed files)
RUN python scripts/init_rio.py

# Expose the dashboard port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8050/')" || exit 1

# Default command: start the server
CMD ["python", "scripts/run_all.py", "--host", "0.0.0.0", "--port", "8050"]
