#!/bin/bash

# Football Predictor Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Football Predictor..."

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

# Create environment files if they don't exist
print_status "Creating environment files..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    print_warning "Created backend/.env from example. Please update with your values."
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    print_warning "Created frontend/.env from example. Please update with your values."
fi

if [ ! -f telegram-bot/.env ]; then
    cp telegram-bot/.env.example telegram-bot/.env
    print_warning "Created telegram-bot/.env from example. Please update with your values."
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p nginx/ssl
mkdir -p logs

# Set permissions
chmod +x scripts/*.sh

print_status "Setup completed successfully!"
print_warning "Please update the .env files with your actual values before running the application."
print_status "To start the application, run: docker-compose up -d"
print_status "To view logs, run: docker-compose logs -f"
print_status "To stop the application, run: docker-compose down"