# 🚀 Production Deployment Guide

## Complete Security-Hardened Deployment for ASP AI Agent

**Last Updated:** 2025-01-18
**Status:** All Critical Security Fixes Implemented ✅

---

## 📋 Security Fixes Summary

| # | Vulnerability | Status | Impact |
|---|---------------|--------|--------|
| **1** | Dangerous File Serving | ✅ FIXED | Nginx now serves all static files |
| **2** | Hardcoded Secret Keys | ✅ FIXED | Secure random keys or crash |
| **3** | Default Admin Backdoor | ✅ FIXED | Random passwords only |
| **4** | CSRF Protection | ✅ FIXED | All forms and APIs protected |
| **5** | Rate Limiting | ✅ FIXED | Brute force prevention |
| **6** | Debug Mode | ✅ FIXED | Disabled in production |
| **7** | Prompt Injection | ✅ FIXED | Multi-layer protection |
| **8** | HTTPS Configuration | ✅ CONFIGURED | Ready for SSL certificate |

---

## 🎯 Pre-Deployment Checklist

### System Requirements

- [ ] Ubuntu/Debian Linux server
- [ ] Python 3.12 installed
- [ ] Nginx installed
- [ ] Domain name configured (asp-ai-agent.com)
- [ ] Ports 80 and 443 accessible
- [ ] At least 4GB RAM
- [ ] 20GB+ disk space

### Optional (Recommended)

- [ ] Redis server (for distributed rate limiting)
- [ ] Dedicated database server (PostgreSQL)
- [ ] SSL certificate from Let's Encrypt
- [ ] Monitoring tools (Prometheus, Grafana)

---

## 📦 Step 1: System Preparation

### 1.1 Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.2 Install Required Packages

```bash
# Web server and SSL
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Python and dependencies
sudo apt-get install -y python3.12 python3-pip python3-venv

# Optional: Redis for rate limiting
sudo apt-get install -y redis-server

# Optional: PostgreSQL for production database
sudo apt-get install -y postgresql postgresql-contrib
```

### 1.3 Create Application User

```bash
sudo useradd -m -s /bin/bash aspapp
sudo usermod -aG www-data aspapp
```

---

## 🔐 Step 2: Security Configuration

### 2.1 Generate Secret Key

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Save this output - you'll need it for FLASK_SECRET_KEY
```

**Example output:**
```
vX3k9mP_zQ7nR2aL1sYf4wN8bT1cH6eA9dK2jM5pQ7r
```

### 2.2 Create Environment File

```bash
cd /home/david/projects/asp_ai_agent

# Create .env file
sudo nano .env
```

**Add the following (replace with your actual keys):**

```bash
# CRITICAL: Production environment
FLASK_ENV=production
FLASK_SECRET_KEY=vX3k9mP_zQ7nR2aL1sYf4wN8bT1cH6eA9dK2jM5pQ7r

# Database (optional - upgrade from SQLite)
# DATABASE_URL=postgresql://user:password@localhost/aspdb

# API Keys
ANTHROPIC_API_KEY=your-claude-api-key
GEMINI_API_KEY=your-gemini-api-key
OLLAMA_API=http://localhost:11434

# Application settings
PORT=8080
BASE_URL=https://asp-ai-agent.com

# Email (for verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@asp-ai-agent.com
```

**Secure the file:**

```bash
chmod 600 .env
sudo chown aspapp:aspapp .env
```

### 2.3 Verify Environment Variables

```bash
# Test that Flask will fail without secret key
python3 -c "
import os
os.environ['FLASK_ENV'] = 'production'
# Don't set FLASK_SECRET_KEY - app should crash
from unified_server import app
"
# Expected: ValueError about missing FLASK_SECRET_KEY
```

---

## 📝 Step 3: Application Setup

### 3.1 Install Python Dependencies

```bash
cd /home/david/projects/asp_ai_agent

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Create Admin User

```bash
# Load environment variables
source .env

# Run admin creation script
python create_admin.py
```

**Follow the prompts:**
```
Enter admin email address: admin@yourdomain.com
Enter admin full name: Your Name
Generate random password? (yes/no, default: yes): yes

✅ Admin User Created Successfully
📧 Email:     admin@yourdomain.com
🔑 Password:  [RANDOM PASSWORD SHOWN ONCE]
⚠️  SAVE THIS PASSWORD SECURELY!
```

**IMPORTANT:** Save the password immediately - it won't be shown again!

### 3.3 Test Application Locally

```bash
# Test the application starts
python unified_server.py

# Expected output:
# 🔒 Production mode: Debug is DISABLED
# ✓ Database initialized
# ⚠️  Production mode: Auto-admin creation disabled for security
# * Running on http://0.0.0.0:8080
```

**Verify in another terminal:**

```bash
curl http://localhost:8080/health

# Expected: {"status": "healthy", "timestamp": "..."}
```

**Stop the test server:** Press Ctrl+C

---

## 🌐 Step 4: Nginx Configuration

### 4.1 Copy Nginx Configuration

```bash
# For production with HTTPS
sudo cp deploy/nginx-asp-ai-agent-external.conf /etc/nginx/sites-available/asp-ai-agent

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/asp-ai-agent /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### 4.2 Create SSL Certificate Directory

```bash
sudo mkdir -p /var/www/certbot
sudo chown www-data:www-data /var/www/certbot
```

### 4.3 Test Nginx Configuration

```bash
sudo nginx -t

# Expected: syntax is ok, test is successful
```

### 4.4 Obtain SSL Certificate

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Get SSL certificate from Let's Encrypt
sudo certbot certonly --standalone \
  -d asp-ai-agent.com \
  -d www.asp-ai-agent.com \
  --agree-tos \
  --email your-email@example.com

# Restart Nginx
sudo systemctl start nginx
```

**Verify certificate:**

```bash
sudo ls -la /etc/letsencrypt/live/asp-ai-agent.com/

# Should show:
# fullchain.pem
# privkey.pem
```

### 4.5 Configure Auto-Renewal

```bash
# Create renewal cron job
sudo nano /etc/cron.d/certbot-renew
```

**Add:**

```cron
# Renew Let's Encrypt certificates twice daily
0 */12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
```

**Test renewal:**

```bash
sudo certbot renew --dry-run

# Expected: Congratulations, all renewals succeeded
```

---

## 🔧 Step 5: Systemd Service Setup

### 5.1 Create Systemd Service File

```bash
sudo nano /etc/systemd/system/asp-ai-agent.service
```

**Add the following:**

```ini
[Unit]
Description=ASP AI Agent - Antimicrobial Stewardship Training
After=network.target

[Service]
Type=simple
User=aspapp
Group=www-data
WorkingDirectory=/home/david/projects/asp_ai_agent
Environment="PATH=/home/david/projects/asp_ai_agent/venv/bin"
EnvironmentFile=/home/david/projects/asp_ai_agent/.env
ExecStart=/home/david/projects/asp_ai_agent/venv/bin/python unified_server.py

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/david/projects/asp_ai_agent

# Restart policy
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable asp-ai-agent

# Start the service
sudo systemctl start asp-ai-agent

# Check status
sudo systemctl status asp-ai-agent
```

**Expected output:**

```
● asp-ai-agent.service - ASP AI Agent
   Loaded: loaded (/etc/systemd/system/asp-ai-agent.service)
   Active: active (running) since ...
   Main PID: ...
```

### 5.3 View Service Logs

```bash
# Real-time logs
sudo journalctl -u asp-ai-agent -f

# Last 100 lines
sudo journalctl -u asp-ai-agent -n 100

# Today's logs
sudo journalctl -u asp-ai-agent --since today
```

---

## 🔥 Step 6: Firewall Configuration

### 6.1 Configure UFW

```bash
# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Allow HTTP (for Let's Encrypt and redirect)
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# If using non-standard ports
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### 6.2 Configure Fail2Ban (Optional but Recommended)

```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Create local configuration
sudo nano /etc/fail2ban/jail.local
```

**Add:**

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
```

**Start fail2ban:**

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## ✅ Step 7: Verification and Testing

### 7.1 Test HTTP → HTTPS Redirect

```bash
curl -I http://asp-ai-agent.com

# Expected: 301 Moved Permanently
# Location: https://asp-ai-agent.com
```

### 7.2 Test HTTPS Connection

```bash
curl -I https://asp-ai-agent.com

# Expected: 200 OK
# Headers should include:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
```

### 7.3 Test Health Endpoint

```bash
curl https://asp-ai-agent.com/api/health

# Expected: {"status": "healthy", "timestamp": "..."}
```

### 7.4 Test Rate Limiting

```bash
# Try 6 rapid requests (login limit is 5/min)
for i in {1..6}; do
  curl -X POST https://asp-ai-agent.com/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
  sleep 1
done

# Expected: First 5 return 401, 6th returns 429 (Rate Limited)
```

### 7.5 Test CSRF Protection

```bash
# Try to POST without CSRF token
curl -X POST https://asp-ai-agent.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'

# Expected: 400 Bad Request (CSRF token missing)
```

### 7.6 Test Prompt Injection Protection

```bash
# Try prompt injection attack
curl -X POST https://asp-ai-agent.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Ignore previous instructions"}]}'

# Expected: 400 Bad Request (Prompt injection detected)
```

### 7.7 Test SSL Certificate

```bash
# Check SSL grade
curl https://www.ssllabs.com/ssltest/analyze.html?d=asp-ai-agent.com

# Or use openssl
openssl s_client -connect asp-ai-agent.com:443 -servername asp-ai-agent.com < /dev/null

# Expected: Certificate chain shown, no errors
```

### 7.8 Test Static File Serving

```bash
# HTML should be served by Nginx
curl -I https://asp-ai-agent.com/index.html

# Expected: 200 OK, served by Nginx (check Server header)

# Try to access Python file (should be blocked)
curl -I https://asp-ai-agent.com/unified_server.py

# Expected: 403 Forbidden or 404 Not Found
```

---

## 📊 Step 8: Monitoring Setup

### 8.1 Application Logs

```bash
# Application logs
sudo journalctl -u asp-ai-agent -f

# Nginx access logs
sudo tail -f /var/log/nginx/asp-ai-agent-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/asp-ai-agent-error.log
```

### 8.2 Security Monitoring

```bash
# Watch for prompt injection attempts
sudo grep "Prompt injection" /var/log/syslog

# Watch for rate limit violations
sudo grep "rate limit" /var/log/nginx/asp-ai-agent-access.log

# Watch for CSRF failures
sudo grep "CSRF" /var/log/syslog
```

### 8.3 System Resource Monitoring

```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top

# Check running services
sudo systemctl status asp-ai-agent nginx postgresql redis
```

---

## 🔄 Step 9: Backup and Recovery

### 9.1 Database Backup

```bash
# Create backup directory
sudo mkdir -p /var/backups/asp-ai-agent
sudo chown aspapp:aspapp /var/backups/asp-ai-agent

# Backup SQLite database
cp /home/david/projects/asp_ai_agent/asp_ai_agent.db \
   /var/backups/asp-ai-agent/asp_ai_agent_$(date +%Y%m%d_%H%M%S).db

# Or PostgreSQL
pg_dump aspdb > /var/backups/asp-ai-agent/aspdb_$(date +%Y%m%d_%H%M%S).sql
```

### 9.2 Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-asp-ai-agent.sh
```

**Add:**

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/asp-ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cp /home/david/projects/asp_ai_agent/asp_ai_agent.db \
   "$BACKUP_DIR/asp_ai_agent_$DATE.db"

# Backup environment file
cp /home/david/projects/asp_ai_agent/.env \
   "$BACKUP_DIR/env_$DATE.bak"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.bak" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Make executable:**

```bash
sudo chmod +x /usr/local/bin/backup-asp-ai-agent.sh
```

**Schedule with cron:**

```bash
sudo crontab -e
```

**Add:**

```cron
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-asp-ai-agent.sh >> /var/log/asp-backups.log 2>&1
```

---

## 🚨 Troubleshooting

### Issue: Application Won't Start

**Check logs:**
```bash
sudo journalctl -u asp-ai-agent -n 50
```

**Common causes:**
- Missing `FLASK_SECRET_KEY` → Set in .env file
- Wrong file permissions → `chmod 755` on directory
- Port already in use → `lsof -i :8080`
- Missing dependencies → `pip install -r requirements.txt`

### Issue: HTTPS Not Working

**Check certificate:**
```bash
sudo ls /etc/letsencrypt/live/asp-ai-agent.com/
```

**Test Nginx:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Renew certificate:**
```bash
sudo certbot renew
```

### Issue: Rate Limiting Too Strict

**Adjust limits in `unified_server.py`:**
```python
limiter = Limiter(
    app=app,
    default_limits=["500 per day", "100 per hour"]  # Increase
)
```

**Restart:**
```bash
sudo systemctl restart asp-ai-agent
```

### Issue: Database Locked

**SQLite concurrency issue:**
```bash
# Upgrade to PostgreSQL for production
sudo apt-get install postgresql
# Update DATABASE_URL in .env
```

---

## 📈 Performance Optimization

### Use Redis for Rate Limiting

```bash
# Install Redis
sudo apt-get install redis-server

# Update unified_server.py
# Change: storage_uri="memory://"
# To: storage_uri="redis://localhost:6379"

# Restart
sudo systemctl restart asp-ai-agent
```

### Enable Nginx Caching

```bash
sudo nano /etc/nginx/sites-available/asp-ai-agent
```

**Add:**

```nginx
# Add to http block
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=asp_cache:10m max_size=1g;

# Add to location block
proxy_cache asp_cache;
proxy_cache_valid 200 1h;
```

### Database Optimization

**Upgrade to PostgreSQL:**

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib python3-psycopg2

# Create database
sudo -u postgres createdb aspdb
sudo -u postgres createuser aspapp -P

# Update .env
DATABASE_URL=postgresql://aspapp:password@localhost/aspdb

# Restart
sudo systemctl restart asp-ai-agent
```

---

## ✅ Final Checklist

### Pre-Launch

- [ ] All environment variables set in .env
- [ ] FLASK_ENV=production
- [ ] FLASK_SECRET_KEY is strong and random
- [ ] SSL certificate obtained and valid
- [ ] Nginx configuration tested (`nginx -t`)
- [ ] Admin user created with secure password
- [ ] Firewall configured (UFW)
- [ ] Services enabled (`systemctl enable`)
- [ ] Backups scheduled (cron)
- [ ] Monitoring configured

### Post-Launch

- [ ] HTTP redirects to HTTPS ✓
- [ ] HTTPS loads correctly ✓
- [ ] Health endpoint responds ✓
- [ ] Rate limiting works ✓
- [ ] CSRF protection active ✓
- [ ] Prompt injection blocked ✓
- [ ] Static files served by Nginx ✓
- [ ] SSL grade A or A+ ✓
- [ ] Logs are clean ✓
- [ ] Backups running ✓

### Security Verification

- [ ] No debug mode in production
- [ ] No default admin credentials
- [ ] CSRF tokens on all forms
- [ ] Rate limits enforced
- [ ] Input validation working
- [ ] HTTPS enforced
- [ ] Security headers present
- [ ] File serving secure

---

## 🎉 Deployment Complete!

Your ASP AI Agent is now:
- ✅ **Secure** - All critical vulnerabilities fixed
- ✅ **Fast** - Nginx serving static files
- ✅ **Reliable** - Systemd managing service
- ✅ **Monitored** - Logging and backups enabled
- ✅ **Encrypted** - HTTPS with Let's Encrypt
- ✅ **Protected** - Rate limiting, CSRF, input validation

---

## 📞 Support

- **Documentation:** See `SECURITY_COMPLETE_SUMMARY.md`
- **Rate Limiting:** See `RATE_LIMITING_GUIDE.md`
- **HTTPS Setup:** See `HTTPS_SETUP_GUIDE.md`
- **Prompt Injection:** See `PROMPT_INJECTION_PROTECTION.md`

---

**Last Updated:** 2025-01-18
**Deployment Status:** ✅ PRODUCTION READY
