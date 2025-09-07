FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with fallback for problematic packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install core dependencies first
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    sqlalchemy==2.0.23 \
    alembic==1.13.1 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    email-validator==2.1.0 \
    httpx==0.25.2 \
    aiohttp==3.9.1 \
    celery==5.3.4 \
    redis==5.0.1 \
    apscheduler==3.10.4 \
    python-dotenv==1.0.0 \
    fastapi-cors==0.0.6 \
    loguru==0.7.2

# Install data processing packages with fallback
RUN pip install --no-cache-dir numpy==1.24.4 || pip install --no-cache-dir numpy
RUN pip install --no-cache-dir pandas==2.0.3 || pip install --no-cache-dir pandas
RUN pip install --no-cache-dir scikit-learn==1.3.2 || pip install --no-cache-dir scikit-learn

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt || echo "Some optional dependencies failed to install"

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]