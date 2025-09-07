#!/bin/bash

# Frontend Logs Viewer Script

echo "🔍 Football Predictor Frontend Logs Viewer"
echo "=========================================="

# Create logs directory if it doesn't exist
mkdir -p /workspace/logs

# Function to show logs
show_logs() {
    local log_file=$1
    local description=$2
    
    if [ -f "$log_file" ]; then
        echo ""
        echo "📄 $description:"
        echo "----------------------------------------"
        if [ "$1" = "follow" ]; then
            tail -f "$log_file"
        else
            tail -20 "$log_file"
        fi
    else
        echo "⚠️  $description not found: $log_file"
    fi
}

# Check if follow mode is requested
if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
    echo "📡 Following frontend logs in real-time (Ctrl+C to stop)..."
    show_logs "/workspace/logs/frontend.log" "Following main frontend log"
else
    echo "📊 Showing recent frontend logs..."
    show_logs "/workspace/logs/frontend.log" "Main frontend log"
    show_logs "/workspace/logs/frontend_sessions.log" "Session logs"
    
    echo ""
    echo "💡 Usage:"
    echo "   $0              - Show recent logs"
    echo "   $0 -f           - Follow logs in real-time"
    echo "   $0 --follow     - Follow logs in real-time"
    echo ""
    echo "📁 Log files location: /workspace/logs/"
    echo "   - frontend.log           - Main frontend logs"
    echo "   - frontend_sessions.log  - Session-specific logs"
    echo "   - session_*.log          - Individual session logs"
fi