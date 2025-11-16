# Production Deployment Guide - ASP AI Agent

## 🚨 Deployment Challenges

Your app has some unique requirements that make **Vercel alone** not ideal:

### Why Not Just Vercel?

❌ **Vercel Limitations:**
- **50MB function size limit** - Your sentence-transformers models are ~1GB
- **Ephemeral filesystem** - SQLite databases get wiped on each deploy
- **10-60s timeout** - LLM requests can take longer
- **No persistent storage** - ChromaDB embeddings need persistent disk

✅ **What Works on Vercel:**
- Static HTML/CSS/JS files
- Lightweight API endpoints
- Serverless functions with small dependencies

### What You Need for This App

✅ **Requirements:**
- **Persistent disk storage** - For SQLite databases and ChromaDB
- **Large dependency support** - sentence-transformers, chromadb (~1.5GB total)
- **Long request timeouts** - LLM calls can take 30-60s+
- **Python 3.12** environment
- **Environment variables** - For API keys

---

## 🎯 Recommended Deployment Options

### Option 1: Railway (Recommended) ⭐

**Best for:** Full-stack Flask apps with ML models

**Pros:**
- ✅ One-click GitHub deploy
- ✅ Persistent disk storage (built-in)
- ✅ No function size limits
- ✅ Long request timeouts (300s)
- ✅ Free tier: $5/month credit
- ✅ Automatic HTTPS
- ✅ Easy environment variables

**Cons:**
- ⚠️ Costs ~$5-10/month after free credit
- ⚠️ Need credit card for signup

**Best for your project:** ⭐⭐⭐⭐⭐

---

### Option 2: Render

**Best for:** Python apps with free tier

**Pros:**
- ✅ Generous free tier (750hrs/month)
- ✅ Persistent disk available
- ✅ Docker support
- ✅ Automatic HTTPS
- ✅ GitHub integration

**Cons:**
- ⚠️ Free tier spins down after 15min inactivity (slow cold starts)
- ⚠️ 512MB RAM on free tier (might be tight)

**Best for your project:** ⭐⭐⭐⭐

---

### Option 3: Fly.io

**Best for:** Docker-based deployments

**Pros:**
- ✅ Persistent volumes
- ✅ Full Docker support
- ✅ Global edge deployment
- ✅ Free tier available

**Cons:**
- ⚠️ Requires Dockerfile
- ⚠️ More complex setup
- ⚠️ Free tier is limited (3GB disk)

**Best for your project:** ⭐⭐⭐

---

### Option 4: Hybrid (Vercel + Railway)

**Best for:** Separating frontend and backend

**Setup:**
- **Frontend** (HTML/CSS/JS) → Vercel (free, fast CDN)
- **Backend** (Flask API) → Railway (persistent storage)

**Pros:**
- ✅ Best of both worlds
- ✅ Fast frontend on CDN
- ✅ Robust backend on Railway

**Cons:**
- ⚠️ More complex CORS setup
- ⚠️ Two deployments to manage

**Best for your project:** ⭐⭐⭐⭐

---

## 🚀 Quick Start: Railway Deployment (Recommended)

Railway is the easiest option for your Flask + ML app. Here's how:

### Step 1: Prepare Your Repository

Create these files:

#### 1. `railway.json` (Railway config)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python unified_server.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. `runtime.txt` (Python version)

```
python-3.12.0
```

#### 3. `Procfile` (Start command)

```
web: python unified_server.py
```

#### 4. Update `unified_server.py` port binding

Find the last line and change:
```python
# OLD:
app.run(host='0.0.0.0', port=8080, debug=True)

# NEW (for Railway):
port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port, debug=False)
```

### Step 2: Deploy to Railway

1. **Sign up**: Go to https://railway.app and sign up with GitHub
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repo**: Choose your `asp_ai_agent` repository
4. **Configure**:
   - Railway auto-detects Python
   - Add environment variables:
     - `ANTHROPIC_API_KEY` = your-claude-key
     - `GEMINI_API_KEY` = your-gemini-key
5. **Add Persistent Volume**:
   - Go to your service → "Volumes" tab
   - Click "Add Volume"
   - Mount path: `/app/data`
   - Size: 1GB (enough for databases)
6. **Deploy**: Railway starts building automatically

### Step 3: Update Database Paths

Modify your database paths to use persistent volume:

```python
# In session_manager.py
DB_PATH = os.environ.get('ASP_DB_PATH', '/app/data/asp_sessions.db')

# In expert_knowledge_rag.py (line ~47)
self.db_path = db_path or '/app/data/asp_expert_knowledge.db'
self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else Path('/app/data/expert_embeddings')
```

### Step 4: Access Your App

Railway gives you a URL like: `https://asp-ai-agent-production.up.railway.app`

Test it:
```bash
curl https://your-railway-url.railway.app/health
```

---

## 🔧 Detailed Railway Setup

### Create Railway Configuration Files

I'll create these for you:

```bash
# Create railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python unified_server.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Create Procfile
echo "web: python unified_server.py" > Procfile

# Create runtime.txt
echo "python-3.12.0" > runtime.txt

# Create .railwayignore (like .gitignore)
cat > .railwayignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
.git/
*.db-journal
EOF
```

### Environment Variables to Set in Railway

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Optional (defaults work)
FLASK_SECRET_KEY=generate-a-random-secret-key-here

# Database paths (using persistent volume)
ASP_DB_PATH=/app/data/asp_sessions.db
```

### Persistent Volume Configuration

Railway → Your Service → Settings → Volumes:
- **Volume Name**: `asp-data`
- **Mount Path**: `/app/data`
- **Size**: 1GB

This persists:
- SQLite databases
- ChromaDB embeddings
- Expert knowledge

---

## 📦 Alternative: Render Deployment

If you prefer the free tier:

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: asp-ai-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python unified_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
    disk:
      name: asp-data
      mountPath: /app/data
      sizeGB: 1
```

### 2. Deploy to Render

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Render auto-detects Python
5. Add environment variables
6. Add disk (Settings → Disks)
7. Deploy

**Free Tier Note:** Spins down after 15min inactivity (first request takes ~30s to wake up)

---

## 🌐 Hybrid Deployment (Vercel + Railway)

Best for: Separating static frontend from Python backend

### Frontend on Vercel

**What goes on Vercel:**
- `index.html`
- `cicu_module.html`
- `agent_models.html`
- All CSS/JS files

**Deploy:**
```bash
# Push to GitHub
git push

# Vercel auto-deploys from main branch
# Or use Vercel CLI:
vercel --prod
```

### Backend on Railway

**What goes on Railway:**
- `unified_server.py`
- All Python files
- `requirements.txt`

**Update CORS in `unified_server.py`:**
```python
CORS(app, origins=[
    'http://localhost:*',
    'https://your-vercel-app.vercel.app',  # Add your Vercel URL
    'https://asp-ai-agent.vercel.app'      # Your production URL
])
```

### Connect Frontend to Backend

Update your HTML files to point to Railway API:

```javascript
// In index.html, cicu_module.html, etc.
const API_URL = 'https://your-railway-url.railway.app';

// Example API call
fetch(`${API_URL}/api/feedback/enhanced`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: userInput, level: 'beginner' })
})
```

---

## 🔐 Security Considerations

### 1. Environment Variables (Never Commit!)

```bash
# .env (add to .gitignore)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
FLASK_SECRET_KEY=...
```

### 2. Update `.gitignore`

```
# Add to .gitignore
.env
*.db
*.db-journal
venv/
__pycache__/
asp_literature/embeddings/
asp_literature/expert_embeddings/
```

### 3. Production Settings

Update `unified_server.py` for production:

```python
# At the end of file:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug  # False in production
    )
```

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid (Light Usage) | Best For |
|----------|-----------|-------------------|----------|
| **Railway** | $5 credit/month | ~$5-10/month | Production apps, always-on |
| **Render** | 750hrs/month | $7/month (always-on) | Free tier acceptable |
| **Fly.io** | Limited | ~$5-10/month | Docker experts |
| **Vercel** | Unlimited (static) | Free for this use | Frontend only |
| **Hybrid** | Mixed | ~$5/month total | Best performance |

---

## 🎯 My Recommendation

**For Your ASP AI Agent:**

### Best Option: Railway ⭐

**Why:**
1. ✅ Handles large ML dependencies easily
2. ✅ Persistent disk out-of-the-box
3. ✅ One-click deploy from GitHub
4. ✅ Always-on (no cold starts)
5. ✅ Perfect for your use case (fellows need instant access)

**Cost:** ~$5-10/month (worth it for professional deployment)

### Budget Option: Render

**Why:**
1. ✅ Free tier (750hrs) = always free if <750hrs/month
2. ✅ Persistent disk available
3. ✅ Good for low-traffic apps

**Caveat:** 15min spin-down means first request is slow

---

## 🚀 Next Steps

**Choose your path:**

### Path A: Railway (Recommended)
1. I'll create the Railway config files for you
2. You push to GitHub
3. Connect Railway to your repo
4. Add environment variables
5. Add persistent volume
6. Deploy!

### Path B: Render (Free Tier)
1. I'll create render.yaml for you
2. You push to GitHub
3. Connect Render to your repo
4. Add environment variables
5. Add disk
6. Deploy!

### Path C: Hybrid (Vercel + Railway)
1. Frontend files to Vercel
2. Backend to Railway
3. Update CORS and API URLs
4. Deploy both

**Which would you like to do?** I can help you set up any of these!

---

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app/
- **Render Docs**: https://render.com/docs
- **Fly.io Docs**: https://fly.io/docs/
- **Flask Deployment Best Practices**: https://flask.palletsprojects.com/en/2.3.x/deploying/

---

## 🆘 Troubleshooting

### Issue: "Module not found" errors on Railway

**Solution:** Make sure all imports are in `requirements.txt`:
```bash
pip freeze > requirements.txt
```

### Issue: Database not persisting

**Solution:** Check persistent volume is mounted at `/app/data` and database paths use that directory.

### Issue: "Out of memory" errors

**Solution:** Upgrade Railway service to 1GB+ RAM plan (~$5/month)

### Issue: Request timeout

**Solution:** Increase timeout in Railway settings or use async processing for long LLM calls.

---

**Ready to deploy?** Tell me which option you prefer and I'll create all the config files you need!
