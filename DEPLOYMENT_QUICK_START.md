# ⚡ Quick Start Deployment Checklist

**30-Minute Production Deployment**

---

## 🔐 1. Generate Secret Key (1 min)

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Save this output!
```

---

## 📝 2. Create .env File (2 min)

```bash
cd /home/david/projects/asp_ai_agent
nano .env
```

**Paste this (replace YOUR_SECRET_KEY):**

```bash
FLASK_ENV=production
FLASK_SECRET_KEY=YOUR_SECRET_KEY_HERE
ANTHROPIC_API_KEY=your-claude-key
GEMINI_API_KEY=your-gemini-key
BASE_URL=https://asp-ai-agent.com
```

**Save and secure:**

```bash
chmod 600 .env
```

---

## 📦 3. Install Dependencies (3 min)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 👤 4. Create Admin User (2 min)

```bash
python create_admin.py
```

**SAVE THE PASSWORD!** It's shown only once.

---

## 🔒 5. Get SSL Certificate (5 min)

```bash
sudo systemctl stop nginx

sudo certbot certonly --standalone \
  -d asp-ai-agent.com \
  -d www.asp-ai-agent.com \
  --email your-email@example.com

sudo systemctl start nginx
```

---

## 🌐 6. Configure Nginx (3 min)

```bash
sudo cp deploy/nginx-asp-ai-agent-external.conf /etc/nginx/sites-available/asp-ai-agent
sudo ln -s /etc/nginx/sites-available/asp-ai-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 7. Create Systemd Service (5 min)

```bash
sudo nano /etc/systemd/system/asp-ai-agent.service
```

**Paste:**

```ini
[Unit]
Description=ASP AI Agent
After=network.target

[Service]
Type=simple
User=aspapp
WorkingDirectory=/home/david/projects/asp_ai_agent
Environment="PATH=/home/david/projects/asp_ai_agent/venv/bin"
EnvironmentFile=/home/david/projects/asp_ai_agent/.env
ExecStart=/home/david/projects/asp_ai_agent/venv/bin/python unified_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable asp-ai-agent
sudo systemctl start asp-ai-agent
```

---

## 🔥 8. Configure Firewall (2 min)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## ✅ 9. Verify Deployment (5 min)

```bash
# 1. Check service is running
sudo systemctl status asp-ai-agent

# 2. Test HTTPS
curl -I https://asp-ai-agent.com

# 3. Test health endpoint
curl https://asp-ai-agent.com/api/health

# 4. Test rate limiting
for i in {1..6}; do curl -X POST https://asp-ai-agent.com/login \
  -d '{"email":"test@test.com","password":"wrong"}' -w "\n%{http_code}\n"; done
```

**Expected:**
- Service: Active (running) ✅
- HTTPS: 200 OK ✅
- Health: {"status": "healthy"} ✅
- Rate limit: 6th request returns 429 ✅

---

## 🔄 10. Setup Auto-Renewal (2 min)

```bash
sudo nano /etc/cron.d/certbot-renew
```

**Add:**

```cron
0 */12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
```

---

## 🎉 Done!

Your application is now live at: **https://asp-ai-agent.com**

### Next Steps:

1. Login at: https://asp-ai-agent.com/login
2. Use admin credentials from Step 4
3. Monitor logs: `sudo journalctl -u asp-ai-agent -f`

---

## 🚨 Quick Troubleshooting

### App won't start?
```bash
sudo journalctl -u asp-ai-agent -n 50
```

### HTTPS not working?
```bash
sudo ls /etc/letsencrypt/live/asp-ai-agent.com/
sudo nginx -t
```

### Need to restart?
```bash
sudo systemctl restart asp-ai-agent
sudo systemctl reload nginx
```

---

**Full Guide:** See `PRODUCTION_DEPLOYMENT_GUIDE.md`
