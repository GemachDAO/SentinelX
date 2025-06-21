# SentinelX Security Framework Container
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl wget git \
    # Network tools
    nmap netcat-openbsd \
    # Development tools
    build-essential \
    # Security tools
    nikto sqlmap \
    # PDF generation dependencies
    wkhtmltopdf \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash sentinelx
WORKDIR /home/sentinelx

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install SentinelX in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /home/sentinelx/reports /home/sentinelx/logs /home/sentinelx/data

# Set ownership
RUN chown -R sentinelx:sentinelx /home/sentinelx

# Switch to non-root user
USER sentinelx

# Expose port for web interface (future feature)
EXPOSE 8080

# Default command
CMD ["sentinelx", "--help"]
