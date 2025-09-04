#!/bin/bash

# Football Predictor Deployment Script

set -e  # Exit on any error

echo "🚀 Starting Football Predictor Deployment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your settings"
    exit 1
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

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose down

# Remove old volumes (optional - uncomment if you want fresh data)
# echo "🗑️ Removing old volumes..."
# docker compose down -v

# Build and start services
echo "🔨 Building and starting services..."
docker compose up --build -d

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
echo "🎉 Deployment completed!"
echo ""
echo "📱 Services are running on:"
echo "   - Frontend: http://localhost:3002"
echo "   - Backend API: http://localhost:8003"
echo "   - Telegram Bot: http://localhost:8004"
echo "   - API Docs: http://localhost:8003/docs"
echo ""
echo "🤖 Telegram Bot: @CodyTips_Bot"
echo "   Send /start to begin using the bot"
echo ""
echo "📊 To view logs:"
echo "   docker compose logs -f"
echo ""
echo "🔧 To check specific service logs:"
echo "   docker compose logs -f backend"
echo "   docker compose logs -f frontend"
echo "   docker compose logs -f telegram-bot"