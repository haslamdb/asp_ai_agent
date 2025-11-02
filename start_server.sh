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

echo "🌟 Starting unified server..."
python unified_server.py

# If the script exits, show a message
echo "❌ Server stopped"