#!/bin/bash

# Football Predictor Service Health Check Script

echo "🔍 Checking Football Predictor Services..."

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Checking $service_name at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Check services
check_service "Backend API" "http://localhost:8001/health"
check_service "Frontend" "http://localhost:3001"
check_service "Telegram Bot" "http://localhost:8002/health"

echo "🏁 Health check completed!"