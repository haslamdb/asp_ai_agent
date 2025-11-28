# HTTPS Setup Guide

## Current Status: ✅ Nginx Already Configured for HTTPS

Your `nginx-asp-ai-agent-external.conf` is **already properly configured** for HTTPS!

---

## What's Already Configured

### ✅ HTTP to HTTPS Redirect

```nginx
server {
    listen 80;
    server_name asp-ai-agent.com www.asp-ai-agent.com;

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name:8443$request_uri;
    }
}
```

### ✅ HTTPS Server

```nginx
server {
    listen 443 ssl http2;
    server_name asp-ai-agent.com www.asp-ai-agent.com;

    # Modern SSL/TLS configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_certificate /etc/letsencrypt/live/asp-ai-agent.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/asp-ai-agent.com/privkey.pem;
}
```

### ✅ Security Headers

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

---

## 🚀 Setup Instructions

### Step 1: Install Certbot (Let's Encrypt Client)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Get certificate (standalone mode)
sudo certbot certonly --standalone \
  -d asp-ai-agent.com \
  -d www.asp-ai-agent.com \
  --agree-tos \
  --email your-email@example.com

# Restart Nginx
sudo systemctl start nginx
```

**OR** use webroot mode (if Nginx is running):

```bash
# Create webroot directory
sudo mkdir -p /var/www/certbot

# Get certificate
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d asp-ai-agent.com \
  -d www.asp-ai-agent.com \
  --agree-tos \
  --email your-email@example.com
```

### Step 3: Verify Certificate Installation

```bash
# Check certificate files exist
sudo ls -la /etc/letsencrypt/live/asp-ai-agent.com/

# Should see:
# fullchain.pem
# privkey.pem
# chain.pem
# cert.pem
```

### Step 4: Test Nginx Configuration

```bash
sudo nginx -t
# Expected: syntax is ok, test is successful
```

### Step 5: Reload Nginx

```bash
sudo systemctl reload nginx
```

### Step 6: Test HTTPS

```bash
# Test HTTPS works
curl -I https://asp-ai-agent.com:8443

# Test HTTP redirects to HTTPS
curl -I http://asp-ai-agent.com:8080
# Expected: 301 Moved Permanently
```

---

## 🔄 Auto-Renewal Setup

Let's Encrypt certificates expire every 90 days. Set up auto-renewal:

### Create Renewal Script

```bash
sudo nano /etc/cron.d/certbot-renew
```

Add this content:

```cron
# Renew Let's Encrypt certificates twice daily
0 */12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
```

### Test Renewal

```bash
# Dry run to test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Port Forwarding Setup

Your setup uses **non-standard ports** due to router forwarding:

| External Port | Internal Port | Service |
|---------------|---------------|---------|
| 80 (HTTP) | 8080 | Nginx HTTP (redirects to HTTPS) |
| 443 (HTTPS) | 8443 | Nginx HTTPS (main application) |

### Router Configuration Needed

On your router, forward these ports:

```
External 80 → Internal Server IP:8080 (HTTP)
External 443 → Internal Server IP:8443 (HTTPS)
```

### Firewall Rules

```bash
# Allow HTTP (for redirect)
sudo ufw allow 8080/tcp

# Allow HTTPS (main application)
sudo ufw allow 8443/tcp

# Reload firewall
sudo ufw reload
```

---

## 🔒 Security Enhancements

### Current Security Headers

Your config already includes:
- ✅ `Strict-Transport-Security` (HSTS)
- ✅ `X-Frame-Options`
- ✅ `X-Content-Type-Options`
- ✅ `X-XSS-Protection`

### Optional: Add Content Security Policy

Add to your HTTPS server block:

```nginx
# Prevent XSS, clickjacking, and other code injection attacks
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';" always;
```

### Optional: Add Referrer Policy

```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Optional: Add Permissions Policy

```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

---

## 🧪 Testing Your HTTPS Setup

### Test 1: SSL Labs

Check your SSL configuration:
```
https://www.ssllabs.com/ssltest/analyze.html?d=asp-ai-agent.com
```

**Target Grade:** A or A+

### Test 2: Security Headers

Check security headers:
```
https://securityheaders.com/?q=https://asp-ai-agent.com:8443
```

**Target Grade:** A

### Test 3: HTTP → HTTPS Redirect

```bash
curl -I http://asp-ai-agent.com:8080
# Expected: 301 redirect to https://asp-ai-agent.com:8443
```

### Test 4: HTTPS Connection

```bash
curl -I https://asp-ai-agent.com:8443
# Expected: 200 OK with security headers
```

---

## 📊 Current Configuration Status

| Feature | Status | Notes |
|---------|--------|-------|
| HTTP → HTTPS Redirect | ✅ Configured | Line 17 in external config |
| HTTPS Listener | ✅ Configured | Port 443 (forwarded from 8443) |
| SSL Certificate Paths | ⚠️ Ready | Need to run certbot |
| Modern TLS (1.2/1.3) | ✅ Configured | Secure protocols only |
| HSTS Header | ✅ Configured | 1 year max-age |
| Security Headers | ✅ Configured | XSS, Frame, Content-Type |
| Rate Limiting | ✅ Configured | 10 req/sec, strict limits |

---

## 🚨 Important Notes

### Development vs Production

**Internal Config** (`nginx-asp-ai-agent.conf`):
- Listens on port 80 only
- Used for local development on `192.168.1.163`
- **No SSL required** (local network)

**External Config** (`nginx-asp-ai-agent-external.conf`):
- Listens on ports 80 (redirect) and 443 (HTTPS)
- Used for public internet access
- **Requires SSL certificate**

### Which Config to Use?

- **Development/Testing:** Use internal config
- **Production (Internet):** Use external config

### Certificate Renewal

- Certificates expire every **90 days**
- Auto-renewal runs **twice daily**
- Check renewal logs: `/var/log/letsencrypt/`

---

## 🔍 Troubleshooting

### Certificate Not Found

```bash
# Check if certificate exists
sudo ls /etc/letsencrypt/live/asp-ai-agent.com/

# If not found, run certbot again
sudo certbot certonly --standalone -d asp-ai-agent.com
```

### Nginx Fails to Start

```bash
# Check for syntax errors
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log
```

### Port Not Accessible

```bash
# Check if Nginx is listening
sudo netstat -tlnp | grep nginx

# Check firewall
sudo ufw status

# Check router port forwarding
```

### Certificate Renewal Fails

```bash
# Manual renewal
sudo certbot renew

# Check renewal log
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## ✅ Deployment Checklist

- [ ] Certbot installed
- [ ] SSL certificate obtained (`/etc/letsencrypt/live/asp-ai-agent.com/`)
- [ ] Nginx external config active
- [ ] Nginx config tested (`nginx -t`)
- [ ] Nginx reloaded
- [ ] Router ports forwarded (80→8080, 443→8443)
- [ ] Firewall allows ports 8080 and 8443
- [ ] HTTP redirects to HTTPS (test with curl)
- [ ] HTTPS works (test with browser)
- [ ] SSL Labs test passes (Grade A)
- [ ] Auto-renewal configured (`/etc/cron.d/certbot-renew`)
- [ ] Renewal tested (`certbot renew --dry-run`)

---

## 📞 Next Steps

1. **Run certbot** to obtain SSL certificate
2. **Test the configuration** with `nginx -t`
3. **Reload Nginx** to apply changes
4. **Test in browser** - should redirect HTTP → HTTPS
5. **Check SSL Labs** for grade A/A+
6. **Set up monitoring** for certificate expiration

---

**Your Nginx configuration is already HTTPS-ready! You just need to obtain the SSL certificate using certbot.**

**Last Updated:** 2025-01-18
