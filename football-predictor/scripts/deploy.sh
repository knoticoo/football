#!/bin/bash

# Football Predictor Deployment Script

set -e  # Exit on any error

echo "🚀 Starting Football Predictor Deployment..."

# Function to install system dependencies
install_system_deps() {
    echo "📦 Installing system dependencies..."
    
    # Update package index
    sudo apt-get update
    
    # Install essential build tools and libraries
    sudo apt-get install -y \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        pkg-config \
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
        curl \
        wget \
        git \
        net-tools \
        procps
    
    echo "✅ System dependencies installed"
}

# Function to check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed!"
        echo "Installing Docker..."
        
        # Update package index
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Set up the stable repository
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Update package index again
        sudo apt-get update
        
        # Install Docker Engine
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        
        echo "✅ Docker installed successfully!"
        echo "⚠️  Please log out and log back in for group changes to take effect, or run: newgrp docker"
        echo "Then run this script again."
        exit 0
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon is not running!"
        echo "Starting Docker daemon..."
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Wait a moment for Docker to start
        sleep 3
        
        # Check again
        if ! docker info &> /dev/null; then
            echo "❌ Failed to start Docker daemon!"
            echo "Please start Docker manually: sudo systemctl start docker"
            exit 1
        fi
    fi
    
    echo "✅ Docker is installed and running"
}

# Function to check for port conflicts
check_port_conflicts() {
    echo "Checking for port conflicts..."
    
    # Ports used by football-predictor
    PORTS=(3002 8003 8004 6380 8080 8443)
    
    for port in "${PORTS[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            # Check if it's a football-predictor container
            CONTAINER_USING_PORT=$(docker ps --format "table {{.Names}}\t{{.Ports}}" | grep ":$port->" | grep -v "football-predictor" || true)
            
            if [ -n "$CONTAINER_USING_PORT" ]; then
                echo "⚠️  Port $port is in use by another service:"
                echo "   $CONTAINER_USING_PORT"
                echo "   This may cause conflicts. Please stop the conflicting service or change the port in docker-compose.yml"
            else
                echo "✅ Port $port is available or used by football-predictor"
            fi
        else
            echo "✅ Port $port is available"
        fi
    done
}

# Function to stop only football-predictor services
stop_football_services() {
    echo "🛑 Stopping Football Predictor services..."
    
    # Get the project name from docker-compose.yml directory
    PROJECT_NAME="football-predictor"
    
    # Stop only containers with the project name prefix
    if docker compose --project-name football-predictor ps -q &> /dev/null; then
        # Get running containers for this project
        RUNNING_CONTAINERS=$(docker compose --project-name football-predictor ps -q 2>/dev/null || true)
        
        if [ -n "$RUNNING_CONTAINERS" ]; then
            echo "Found running Football Predictor containers, stopping them..."
            docker compose --project-name football-predictor down
        else
            echo "No Football Predictor containers are currently running"
        fi
    else
        echo "No Football Predictor containers found"
    fi
    
    # Also check for any containers with football-predictor in the name
    FOOTBALL_CONTAINERS=$(docker ps -q --filter "name=football-predictor" 2>/dev/null || true)
    if [ -n "$FOOTBALL_CONTAINERS" ]; then
        echo "Stopping any remaining Football Predictor containers..."
        docker stop $FOOTBALL_CONTAINERS
        docker rm $FOOTBALL_CONTAINERS
    fi
}

# Install system dependencies
install_system_deps

# Check Docker installation and status
check_docker

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Creating .env file from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env file and configure your settings before running again"
        exit 1
    else
        echo "❌ .env.example file not found!"
        echo "Please create a .env file with your configuration"
        exit 1
    fi
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your-telegram-bot-token-here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not configured!"
    echo "Please set your Telegram bot token in .env file"
    exit 1
fi

echo "✅ Environment configuration validated"

# Check for port conflicts before starting
check_port_conflicts

# Stop only football-predictor services (not other services on ports 5000, 5001, etc.)
stop_football_services

# Remove old volumes (optional - uncomment if you want fresh data)
# echo "🗑️ Removing old volumes..."
# docker compose down -v

# Function to handle Python dependency issues
fix_python_deps() {
    echo "🐍 Checking Python dependency compatibility..."
    
    # Create a temporary requirements file with compatible versions
    cat > backend/requirements-compatible.txt << EOF
# Core FastAPI dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Email validation
email-validator==2.1.0

# HTTP requests
httpx==0.25.2
aiohttp==3.9.1

# Background tasks
celery==5.3.4
redis==5.0.1

# Scheduling
apscheduler==3.10.4

# Data processing (compatible versions)
numpy==1.24.4
pandas==2.0.3
scikit-learn==1.3.2

# Environment
python-dotenv==1.0.0

# CORS
fastapi-cors==0.0.6

# Logging
loguru==0.7.2

# Development (optional)
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
EOF

    echo "✅ Created compatible requirements file"
}

# Build and start services
echo "🔨 Building and starting services..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found!"
    echo "Please run this script from the football-predictor directory"
    exit 1
fi

# Fix Python dependencies
fix_python_deps

# Build and start services with project name to avoid conflicts
echo "🔨 Building Docker images..."
docker compose --project-name football-predictor build --no-cache

echo "🚀 Starting services..."
docker compose --project-name football-predictor up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Checking $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to become healthy"
    return 1
}

# Check services
echo "🔍 Checking service health..."

# Check backend first with detailed logging
echo "⏳ Checking Backend API..."
if check_service "Backend API" "http://localhost:8003/health"; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is unhealthy - checking logs..."
    echo "Backend logs:"
    docker compose --project-name football-predictor logs --tail=50 backend
    echo ""
    echo "Trying to restart backend..."
    docker compose --project-name football-predictor restart backend
    sleep 10
    if check_service "Backend API" "http://localhost:8003/health"; then
        echo "✅ Backend API recovered after restart"
    else
        echo "❌ Backend API still unhealthy after restart"
        echo "Full backend logs:"
        docker compose --project-name football-predictor logs backend
    fi
fi

check_service "Frontend" "http://localhost:3002"
check_service "Telegram Bot" "http://localhost:8004/health"

# Function to show backend logs
show_backend_logs() {
    echo ""
    echo "Backend Logs (last 30 lines):"
    echo "=========================================="
    
    # Show Docker container logs
    echo "📄 Docker container logs:"
    docker compose --project-name football-predictor logs --tail=30 backend
    
    echo ""
    echo "💡 To monitor backend logs in real-time, run:"
    echo "   docker compose --project-name football-predictor logs -f backend"
    echo "=========================================="
}

# Function to show frontend logs
show_frontend_logs() {
    echo ""
    echo "Frontend Logs (last 20 lines):"
    echo "=========================================="
    
    # Create logs directory if it doesn't exist
    mkdir -p /workspace/logs
    
    if [ -f "/workspace/logs/frontend.log" ]; then
        echo "📄 Main frontend log:"
        tail -20 /workspace/logs/frontend.log
    else
        echo "⚠️  No frontend logs found yet. Logs will appear when the frontend starts making requests."
    fi
    
    echo ""
    echo "📄 Session logs:"
    if [ -f "/workspace/logs/frontend_sessions.log" ]; then
        tail -10 /workspace/logs/frontend_sessions.log
    else
        echo "⚠️  No session logs found yet."
    fi
    
    echo ""
    echo "💡 To monitor logs in real-time, run:"
    echo "   tail -f /workspace/logs/frontend.log"
    echo "=========================================="
}

# Show backend logs
show_backend_logs

# Show frontend logs
show_frontend_logs

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📱 Football Predictor Services are running on:"
echo "   - Frontend: http://localhost:3002"
echo "   - Backend API: http://localhost:8003"
echo "   - Telegram Bot: http://localhost:8004"
echo "   - API Docs: http://localhost:8003/docs"
echo "   - Nginx Proxy: http://localhost:8080"
echo ""
echo "🤖 Telegram Bot: @${BOT_USERNAME:-CodyTips_Bot}"
echo "   Send /start to begin using the bot"
echo ""
echo "📊 Management Commands:"
echo "   View all logs:     docker compose --project-name football-predictor logs -f"
echo "   View backend logs: docker compose --project-name football-predictor logs -f backend"
echo "   View frontend logs: docker compose --project-name football-predictor logs -f frontend"
echo "   View bot logs:     docker compose --project-name football-predictor logs -f telegram-bot"
echo "   View redis logs:   docker compose --project-name football-predictor logs -f redis"
echo "   View nginx logs:   docker compose --project-name football-predictor logs -f nginx"
echo ""
echo "Backend Debugging:"
echo "   Test health endpoint: curl http://localhost:8003/health"
echo "   Test API docs:       curl http://localhost:8003/docs"
echo "   Check backend status: docker compose --project-name football-predictor ps backend"
echo "   Restart backend:     docker compose --project-name football-predictor restart backend"
echo "   Rebuild backend:     docker compose --project-name football-predictor build backend"
echo ""
echo "Frontend Logs:"
echo "   View frontend logs: tail -f /workspace/logs/frontend.log"
echo "   View session logs:  tail -f /workspace/logs/frontend_sessions.log"
echo "   Clear frontend logs: rm -f /workspace/logs/frontend*.log"
echo ""
echo "🔧 Service Management:"
echo "   Stop services:     docker compose --project-name football-predictor down"
echo "   Restart services:  docker compose --project-name football-predictor restart"
echo "   Check status:      docker compose --project-name football-predictor ps"
echo ""
echo "⚠️  Note: This deployment only manages Football Predictor services."
echo "   Other services on ports 5000, 5001, etc. are not affected."