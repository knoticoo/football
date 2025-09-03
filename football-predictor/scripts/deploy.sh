#!/bin/bash

# Football Predictor Deployment Script
# This script deploys the application to production

set -e

echo "🚀 Deploying Football Predictor..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is allowed for Docker operations."
    print_warning "Make sure you understand the security implications."
    read -p "Continue as root? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if environment files exist
if [ ! -f backend/.env ]; then
    print_error "backend/.env not found. Please create it first."
    exit 1
fi

if [ ! -f frontend/.env ]; then
    print_error "frontend/.env not found. Please create it first."
    exit 1
fi

if [ ! -f telegram-bot/.env ]; then
    print_error "telegram-bot/.env not found. Please create it first."
    exit 1
fi

# Determine if we need sudo for Docker commands
DOCKER_CMD="docker"
COMPOSE_CMD="docker-compose"
if [ "$EUID" -eq 0 ]; then
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker-compose"
fi

# Stop existing containers
print_status "Stopping existing containers..."
$COMPOSE_CMD down

# Pull latest images
print_status "Pulling latest images..."
$COMPOSE_CMD pull

# Build and start services
print_status "Building and starting services..."
$COMPOSE_CMD up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "✅ Backend is healthy"
else
    print_warning "⚠️ Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    print_status "✅ Frontend is healthy"
else
    print_warning "⚠️ Frontend health check failed"
fi

# Check telegram bot
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    print_status "✅ Telegram bot is healthy"
else
    print_warning "⚠️ Telegram bot health check failed"
fi

# Show running containers
print_status "Running containers:"
$COMPOSE_CMD ps

print_status "Deployment completed!"
print_status "Services are running on:"
print_status "  - Frontend: http://localhost:3001"
print_status "  - Backend API: http://localhost:8001"
print_status "  - Telegram Bot: http://localhost:8002"
print_status ""
print_status "To view logs: $COMPOSE_CMD logs -f"
print_status "To stop services: $COMPOSE_CMD down"