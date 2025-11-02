# ASP AI Agent

AI-powered tools and interfaces for antimicrobial stewardship programs with support for multiple AI models including Claude, Gemini, and local Ollama models.

## 🚀 Quick Start

**New to the project?** See our detailed [Setup Guide (SETUP.md)](./SETUP.md) for complete installation instructions.

### Fastest Setup (30 seconds)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/haslamdb/asp_ai_agent.git
   cd asp_ai_agent
   ```

2. **Get an API key** (choose one):
   - **Claude**: https://console.anthropic.com → API Keys
   - **Gemini**: https://aistudio.google.com → Get API Key

3. **Set environment variable**:
   ```bash
   export ANTHROPIC_API_KEY='your-claude-key-here'
   # OR
   export GEMINI_API_KEY='your-gemini-key-here'
   ```

4. **Start the server**:
   ```bash
   pip install -r requirements.txt
   python unified_server.py
   ```

5. **Open interface**: Visit `agent_models.html` in your browser or use:
   ```bash
   python -m http.server 8080
   # Then go to http://localhost:8080
   ```

## 🌟 Features

- **Agent Models Interface** (`agent_models.html`) - Advanced ASP training modules with AI feedback
- **Chat Interface** (`asp_ai_agent.html`) - General ASP consultation and case discussions  
- **Multi-Model Support** - Claude 3.5 Sonnet, Gemini 2.5 Flash, and local Ollama models
- **Unified Backend** - Single server handling all AI providers with automatic fallbacks
- **Production Ready** - Vercel deployment with secure API key management

## 🔗 Live Demo

- **GitHub Pages** (Frontend only): https://haslamdb.github.io/asp_ai_agent/
- **Full Application**: Deploy to Vercel for complete functionality with AI models

## 📖 Documentation

- **[Complete Setup Guide](./SETUP.md)** - Detailed installation and configuration
- **[API Key Setup](./SETUP.md#3-get-api-keys-choose-one-or-both)** - How to obtain Claude and Gemini keys
- **[Server Instructions](./SETUP.md#4-start-the-server)** - Starting the unified backend
- **[Deployment Guide](./SETUP.md#production-deployment-with-vercel)** - Production hosting on Vercel

## 🏗️ Project Structure

```
asp_ai_agent/
├── api/
│   ├── gemini.js           # Vercel Edge Function for Gemini API
│   └── claude.js           # Vercel Edge Function for Claude API
├── agent_models.html       # Main training interface with modules
├── asp_ai_agent.html       # Chat interface for general consultation
├── index.html              # Landing page navigation
├── unified_server.py       # Local development server (all models)
├── requirements.txt        # Python dependencies
├── SETUP.md               # Complete setup instructions
└── vercel.json            # Production deployment config
```

## 🚀 Deployment Options

### Local Development
Perfect for testing and development with all model options:
```bash
python unified_server.py  # Supports Claude, Gemini, and Ollama
```

### Production (Vercel)
Secure, scalable deployment for production use:
- Automatic HTTPS and global CDN
- Secure environment variable management
- Edge functions for low latency

See [SETUP.md](./SETUP.md) for complete deployment instructions.

## 🤖 AI Model Comparison

| Model | Best For | Cost | Local | Search |
|-------|----------|------|-------|---------|
| **Claude 3.5 Sonnet** | Complex medical reasoning | Pay-per-use | No | No |
| **Gemini 2.5 Flash** | General queries | Free tier | No | Yes |
| **Ollama (Local)** | Privacy, offline use | Free | Yes | No |

## 🔐 Security

- API keys are never exposed to the browser
- Server-side proxy protects credentials
- CORS configured for authorized origins only
- Environment variables for key management

## 🛠️ Technologies

- **Frontend**: HTML5, Tailwind CSS, JavaScript ES6+
- **Backend**: Python Flask, Vercel Edge Functions
- **AI Models**: Anthropic Claude, Google Gemini, Local Ollama
- **Hosting**: Vercel (production), GitHub Pages (static)

## 📋 Requirements

- Python 3.8+ (for local server)
- API key for Claude or Gemini (see [SETUP.md](./SETUP.md))
- Modern web browser
- Optional: Ollama for local models

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first to discuss the proposed changes.

## 📄 License

This project is proprietary and confidential.

---

**Need help?** Check the [Setup Guide](./SETUP.md) or open an issue for support.