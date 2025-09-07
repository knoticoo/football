#!/bin/bash

# Backend API Testing Script
# This script helps debug backend issues by running it directly

set -e

echo "🧪 Testing Backend API Directly..."

# Change to backend directory
cd /workspace/football-predictor/backend

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy

# Try to install other dependencies
echo "📦 Installing additional dependencies..."
pip install python-jose[cryptography] passlib[bcrypt] python-multipart email-validator httpx aiohttp || echo "Some optional dependencies failed"

# Test basic imports
echo "🔍 Testing basic imports..."
python3 -c "
try:
    from fastapi import FastAPI
    from pydantic import BaseSettings
    from sqlalchemy import create_engine
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Try to run the backend
echo "🚀 Starting backend server..."
echo "Backend will be available at: http://localhost:8001"
echo "Health check: http://localhost:8001/health"
echo "API docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the backend
python3 main.py