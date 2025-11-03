#!/bin/bash

echo "=========================================="
echo "Starting ASP AI Agent Local Server"
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
if pgrep -f "ollama serve" > /dev/null; then
    echo "✅ Ollama is already running"
else
    echo "🚀 Starting Ollama with models from /home/david/models..."
    export OLLAMA_MODELS=/home/david/models
    /usr/local/bin/ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Ollama started successfully"
    else
        echo "❌ Failed to start Ollama. Check /tmp/ollama.log"
    fi
fi
echo ""
echo "Available models:"
curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; models = json.load(sys.stdin)['models']; print('\n'.join(f\"  - {m['name']} ({m['details']['parameter_size']})\" for m in models))" 2>/dev/null || echo "  Unable to list models"

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