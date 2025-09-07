#!/bin/bash

# Football Predictor Deployment Script

set -e  # Exit on any error

echo "🚀 Starting Football Predictor Deployment..."

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
    echo "🔍 Checking for port conflicts..."
    
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

# Build and start services
echo "🔨 Building and starting services..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found!"
    echo "Please run this script from the football-predictor directory"
    exit 1
fi

# Build and start services with project name to avoid conflicts
docker compose --project-name football-predictor up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

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
check_service "Backend API" "http://localhost:8003/health"
check_service "Frontend" "http://localhost:3002"
check_service "Telegram Bot" "http://localhost:8004/health"

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
echo ""
echo "🔧 Service Management:"
echo "   Stop services:     docker compose --project-name football-predictor down"
echo "   Restart services:  docker compose --project-name football-predictor restart"
echo "   Check status:      docker compose --project-name football-predictor ps"
echo ""
echo "⚠️  Note: This deployment only manages Football Predictor services."
echo "   Other services on ports 5000, 5001, etc. are not affected."