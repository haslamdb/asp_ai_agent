#!/bin/bash

echo "=========================================="
echo "Starting ASP AI Agent with Ollama Models"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Install required Python packages if needed
echo "Checking Python dependencies..."
pip3 install -q flask flask-cors requests 2>/dev/null || {
    echo "Installing required packages..."
    pip3 install flask flask-cors requests
}

# Check if Ollama is running
echo ""
echo "Checking Ollama status..."
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama is running"
    ollama list
else
    echo "⚠️  Ollama is not running. Start it with: sudo systemctl start ollama"
fi

# Check if Citation Assistant is running
echo ""
echo "Checking Citation Assistant..."
if pgrep -f "server_secure.py" > /dev/null; then
    echo "✅ Citation Assistant is running"
else
    echo "⚠️  Citation Assistant is not running"
    echo "   To start it: cd ~/projects/citation_assistant && python server_secure.py"
fi

# Set environment variables if they exist in .env file
if [ -f .env ]; then
    echo ""
    echo "Loading environment variables from .env..."
    export $(cat .env | xargs)
fi

# Start the unified server
echo ""
echo "=========================================="
echo "Starting Unified AI Server on port 5000..."
echo "=========================================="
echo ""
echo "Access the interface at:"
echo "  http://localhost:5000"
echo "  file://$(pwd)/local_models.html"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

python3 unified_server.py