#!/bin/bash

# ASP AI Agent Server Startup Script
# This script starts the unified server with the Claude API key

echo "🚀 Starting ASP AI Agent Server..."
echo "📋 Setting up environment..."

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Please create one from .env.example"
    echo "   cp .env.example .env"
    echo "   Then add your API keys to the .env file"
    exit 1
fi

# Check if Claude API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set in .env file"
    exit 1
fi

echo "🔑 Claude API Key: ${ANTHROPIC_API_KEY:0:20}..."
if [ ! -z "$GEMINI_API_KEY" ]; then
    echo "🔑 Gemini API Key: ${GEMINI_API_KEY:0:20}..."
fi

# Stop any existing server instances
echo "🛑 Stopping any existing servers..."
pkill -f unified_server.py 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

echo "🌟 Starting unified API server on port 5000..."
python unified_server.py &
API_PID=$!

# Give the API server time to start
sleep 2

echo ""
echo "🌐 Starting web server on port 8080..."
python -m http.server 8080 &
WEB_PID=$!

echo ""
echo "============================================"
echo "✅ Both servers are running!"
echo "============================================"
echo ""
echo "Access the ASP AI Agent at:"
echo "  📍 http://localhost:8080 - Main landing page"
echo "  📚 http://localhost:8080/agent_models.html - Training modules"
echo "  💬 http://localhost:8080/asp_ai_agent.html - Chat interface"
echo ""
echo "API endpoints available at:"
echo "  🔧 http://localhost:5000/api/models"
echo "  🔧 http://localhost:5000/api/chat"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C and clean up both processes
trap 'echo ""; echo "🛑 Stopping servers..."; kill $API_PID $WEB_PID 2>/dev/null; exit' INT

# Wait for either process to exit (shouldn't happen unless there's an error)
wait $API_PID $WEB_PID

# If we get here, something went wrong
echo "❌ One or both servers stopped unexpectedly"