# ASP AI Agent Setup Guide

This guide will help you set up the ASP AI Agent with support for multiple AI models including Claude, Gemini, and local Ollama models.

## Overview

The ASP AI Agent provides:
- **Agent Models Interface** (`agent_models.html`) - Advanced training modules for ID fellows
- **Chat Interface** (`asp_ai_agent.html`) - General ASP consultation chat
- **Unified Backend** (`unified_server.py`) - Supports multiple AI providers
- **Vercel Deployment** - Production-ready cloud hosting

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/haslamdb/asp_ai_agent.git
cd asp_ai_agent
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Get API Keys (Choose One or Both)

#### Option A: Claude API Key (Recommended for Medical Tasks)

1. **Visit Anthropic Console**: Go to https://console.anthropic.com
2. **Create Account**: Sign up or sign in to your Anthropic account
3. **Navigate to API Keys**: 
   - Click on "API Keys" in the left sidebar
   - Or go directly to https://console.anthropic.com/settings/keys
4. **Create New Key**:
   - Click "Create Key"
   - Give it a descriptive name (e.g., "ASP AI Agent")
   - Copy the API key (starts with `sk-ant-api03-...`)
5. **Set Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY='your-claude-api-key-here'
   ```

#### Option B: Google Gemini API Key

1. **Visit Google AI Studio**: Go to https://aistudio.google.com
2. **Create Project**: Create a new Google Cloud project or use existing
3. **Get API Key**:
   - Click "Get API Key" button
   - Choose "Create API key in new project" or use existing
   - Copy the API key
4. **Set Environment Variable**:
   ```bash
   export GEMINI_API_KEY='your-gemini-api-key-here'
   ```

#### Option C: Both APIs (Best Experience)

Set both environment variables for maximum flexibility:
```bash
export ANTHROPIC_API_KEY='your-claude-api-key-here'
export GEMINI_API_KEY='your-gemini-api-key-here'
```

### 4. Start the Server

```bash
# Method 1: Direct Python execution
python unified_server.py

# Method 2: Using the package manager
python -m unified_server

# Method 3: Make it executable and run
chmod +x unified_server.py
./unified_server.py
```

The server will start on `http://localhost:5000` and show available services.

### 5. Open the Interface

Open your browser and navigate to:
- **Main Hub**: `file:///path/to/your/project/index.html`
- **Agent Models**: `file:///path/to/your/project/agent_models.html`
- **Chat Interface**: `file:///path/to/your/project/asp_ai_agent.html`

Or use a local web server:
```bash
# Python built-in server
python -m http.server 8080
# Then visit http://localhost:8080

# Node.js (if you have it)
npx serve .
```

## Advanced Setup

### Setting Up Ollama (Optional Local Models)

If you want to run local AI models:

1. **Install Ollama**: Visit https://ollama.ai and download for your OS
2. **Start Ollama**:
   ```bash
   ollama serve
   ```
3. **Pull Models**:
   ```bash
   # Recommended for medical tasks
   ollama pull gemma2:27b
   ollama pull llama3.1:8b
   
   # Smaller models for testing
   ollama pull gemma2:9b
   ollama pull phi3:mini
   ```

### Environment Variables

Create a `.env` file in your project root:
```env
# Required for Claude support
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Required for Gemini support  
GEMINI_API_KEY=your-gemini-key-here

# Optional: Custom endpoints
OLLAMA_API=http://localhost:11434
CITATION_API=http://localhost:9998
```

Then load it before starting:
```bash
# Load environment variables
source .env  # or use python-dotenv

# Start server
python unified_server.py
```

### Production Deployment with Vercel

For production deployment:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Set Environment Variables in Vercel**:
   ```bash
   vercel env add ANTHROPIC_API_KEY
   vercel env add GEMINI_API_KEY
   ```

3. **Deploy**:
   ```bash
   vercel deploy
   ```

## Troubleshooting

### Common Issues

1. **API Key Not Working**:
   ```bash
   # Check if key is set
   echo $ANTHROPIC_API_KEY
   echo $GEMINI_API_KEY
   
   # Test the server health
   curl http://localhost:5000/health
   ```

2. **CORS Errors**:
   - Make sure you're accessing files via HTTP (not file://)
   - Use `python -m http.server 8080` to serve files locally

3. **Server Won't Start**:
   ```bash
   # Check if port 5000 is in use
   lsof -i :5000
   
   # Use a different port
   export PORT=8000
   python unified_server.py
   ```

4. **Model Not Available**:
   - Check `/health` endpoint for service status
   - Verify API keys are correctly set
   - Check server logs for error messages

### Testing Your Setup

1. **Check Health**:
   ```bash
   curl http://localhost:5000/health
   ```

2. **List Available Models**:
   ```bash
   curl http://localhost:5000/api/models
   ```

3. **Test Claude**:
   ```bash
   curl -X POST http://localhost:5000/claude \
     -H "Content-Type: application/json" \
     -d '{
       "system": "You are a helpful assistant.",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

4. **Test Gemini**:
   ```bash
   curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gemini:2.0-flash",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

## Usage Tips

### Choosing the Right Model

- **Claude 3.5 Sonnet**: Best for complex medical reasoning and detailed feedback
- **Gemini 2.5 Flash**: Great for general queries with web search integration
- **Local Ollama**: Privacy-focused, no API costs, works offline

### API Costs

- **Claude**: Pay per token, excellent quality (~$3-15 per 1M tokens)
- **Gemini**: Generous free tier, then pay per use (~$0.50-7 per 1M tokens)
- **Ollama**: Free but requires local compute resources

### Security Notes

- Never commit API keys to version control
- Use environment variables or secure secret management
- For production, use Vercel's environment variable system
- Consider API key rotation for production systems

## Support

If you encounter issues:

1. Check the server logs in your terminal
2. Verify API keys are correctly set
3. Test individual components using the curl examples above
4. Check the `/health` endpoint for service status

For medical content accuracy, always verify AI-generated recommendations with current guidelines and literature.