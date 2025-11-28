# External Access Setup for asp-ai-agent.com

This guide will help you configure external access to your ASP AI Agent application with password protection and SSL encryption.

## Overview

- **Domain**: asp-ai-agent.com
- **Static Public IP**: 50.5.30.133
- **Local Server IP**: 192.168.1.163
- **External Ports**: 8080 (HTTP), 8443 (HTTPS)
- **Internal Ports**: 80 (HTTP), 443 (HTTPS)
- **Access URL**: https://asp-ai-agent.com:8443
- **Security**: Password-protected with HTTPS (SSL)

**Note**: Since ports 80 and 443 are already forwarded to another server on your network, this setup uses custom external ports 8080 and 8443.

## Prerequisites

- Domain asp-ai-agent.com purchased and DNS access available
- Router access for port forwarding configuration
- Server running at 192.168.1.163 (already configured)
- Root/sudo access to the server

## Step 1: Configure Domain DNS

Configure your domain's DNS settings to point to your static IP address.

**DNS Records to Create:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 50.5.30.133 | 3600 |
| A | www | 50.5.30.133 | 3600 |

**Instructions:**
1. Log into your domain registrar's control panel (where you purchased asp-ai-agent.com)
2. Navigate to DNS settings or DNS management
3. Create an **A record**:
   - Host/Name: `@` (represents root domain)
   - Value/Points to: `50.5.30.133`
   - TTL: `3600` (or leave default)
4. Create another **A record** for www:
   - Host/Name: `www`
   - Value/Points to: `50.5.30.133`
   - TTL: `3600` (or leave default)
5. Save changes

**Note:** DNS propagation can take 5 minutes to 48 hours. Test with:
```bash
# Check if domain resolves to your IP
dig asp-ai-agent.com +short
# Should return: 50.5.30.133
```

## Step 2: Configure Router Port Forwarding

You need to forward incoming traffic on ports 80 and 443 to your local server.

**Port Forwarding Rules:**

| Service | External Port | Internal IP | Internal Port | Protocol |
|---------|---------------|-------------|---------------|----------|
| HTTP | 8080 | 192.168.1.163 | 80 | TCP |
| HTTPS | 8443 | 192.168.1.163 | 443 | TCP |

**General Router Configuration Steps:**
1. Open your router's admin panel (usually http://192.168.1.1 or similar)
2. Navigate to "Port Forwarding" or "Virtual Servers" section
3. Create first rule:
   - Service Name: `ASP-AI-Agent-HTTP`
   - External/WAN Port: `8080`
   - Internal/LAN IP: `192.168.1.163`
   - Internal Port: `80`
   - Protocol: `TCP`
4. Create second rule:
   - Service Name: `ASP-AI-Agent-HTTPS`
   - External/WAN Port: `8443`
   - Internal/LAN IP: `192.168.1.163`
   - Internal Port: `443`
   - Protocol: `TCP`
5. Save and apply settings

**Test Port Forwarding:**
```bash
# From an external network (not your home network), test:
curl -I http://50.5.30.133:8080
# Should return HTTP response from your server
```

## Step 3: Set Up Password Authentication

Run the authentication setup script to create password-protected access:

```bash
sudo bash deploy/setup_auth.sh
```

You will be prompted to:
1. Enter a username (e.g., "fellowship_admin")
2. Enter a password (entered twice for confirmation)

**To add additional users later:**
```bash
sudo htpasswd /etc/nginx/auth/asp_ai_agent.htpasswd <username>
```

## Step 4: Verify Domain Resolution

Before requesting SSL certificate, verify that your domain is resolving correctly:

```bash
# Test DNS resolution
dig asp-ai-agent.com +short
# Should show: 50.5.30.133

# Test from external network
curl -I http://asp-ai-agent.com
# Should get response from your server
```

**IMPORTANT:** Do not proceed to Step 5 until:
- DNS points to 50.5.30.133
- Port 8080 is forwarded to 192.168.1.163:80
- You can access http://asp-ai-agent.com:8080 from outside your network

## Step 5: Install SSL Certificate (DNS Challenge)

Since port 80 is not available externally (already in use by another server), we'll use DNS-01 challenge instead of HTTP-01:

```bash
sudo bash deploy/setup_ssl_dns.sh
```

**During the process:**
1. Certbot will ask you to add a TXT record to your DNS
2. The record will look like:
   - **Type**: TXT
   - **Name**: `_acme-challenge` or `_acme-challenge.asp-ai-agent.com`
   - **Value**: (certbot will provide this)
   - **TTL**: 300
3. Add this record in your domain registrar's DNS panel
4. Wait 1-5 minutes for DNS propagation
5. Verify with: `dig _acme-challenge.asp-ai-agent.com TXT`
6. Press Enter in the terminal to continue

**Important**: DNS challenge certificates require **manual renewal** every 90 days. Auto-renewal is not possible with manual DNS challenge.

## Step 6: Deploy External Configuration

After SSL certificate is obtained, switch to the external Nginx configuration:

```bash
# Copy external configuration to sites-available
sudo cp deploy/nginx-asp-ai-agent-external.conf /etc/nginx/sites-available/asp-ai-agent

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

## Step 7: Verify External Access

Test your deployment:

1. **Test HTTPS access:**
   ```bash
   # From external network or use your phone's cellular data
   curl -u username:password https://asp-ai-agent.com:8443
   ```

2. **Visit in browser:**
   - Go to https://asp-ai-agent.com:8443 (note the :8443 port!)
   - You should be prompted for username/password
   - After authentication, you should see the ASP AI Agent interface

3. **Test HTTP redirect:**
   - Go to http://asp-ai-agent.com:8080 (with :8080)
   - Should automatically redirect to https://asp-ai-agent.com:8443

## Security Features

Your deployment includes:

- **HTTPS/SSL Encryption**: All traffic encrypted with TLS 1.2/1.3
- **HTTP Basic Authentication**: Username/password required for access
- **Rate Limiting**:
  - General endpoints: 10 requests/second per IP
  - API endpoints: 2 requests/second per IP
- **Security Headers**: HSTS, X-Frame-Options, X-Content-Type-Options
- **Automatic Certificate Renewal**: Certificates renew automatically before expiry

## Monitoring and Maintenance

### Check Service Status
```bash
# Application service
sudo systemctl status asp-ai-agent

# Nginx
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u asp-ai-agent -f
tail -f /home/david/projects/asp_ai_agent/logs/asp-ai-agent.log

# Nginx access logs
sudo tail -f /var/log/nginx/asp-ai-agent-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/asp-ai-agent-error.log
```

### Restart Services
```bash
# Restart application
sudo systemctl restart asp-ai-agent

# Reload Nginx (no downtime)
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx
```

### Update Application
```bash
# After code changes
cd /home/david/projects/asp_ai_agent
git pull
sudo systemctl restart asp-ai-agent
```

## Troubleshooting

### DNS Not Resolving
- Wait up to 48 hours for DNS propagation
- Use `dig asp-ai-agent.com +short` to check
- Verify A records in domain registrar panel

### Cannot Access from External Network
- Verify port forwarding rules are active (ports 8080 and 8443)
- Check router has saved configuration
- Test with `curl -I http://50.5.30.133:8080` from external network
- Check firewall isn't blocking ports 80/443 internally on the server

### SSL Certificate Request Fails (DNS Challenge)
- Ensure you added the TXT record correctly to your DNS
- Wait 5 minutes for DNS propagation
- Verify TXT record: `dig _acme-challenge.asp-ai-agent.com TXT`
- Check `/var/log/letsencrypt/letsencrypt.log` for errors
- Try the challenge again if DNS record is correct

### Password Not Working
- Verify password file exists: `ls -l /etc/nginx/auth/asp_ai_agent.htpasswd`
- Reset password: `sudo htpasswd /etc/nginx/auth/asp_ai_agent.htpasswd username`

### Application Not Starting
- Check logs: `sudo journalctl -u asp-ai-agent -n 100`
- Verify .env file exists with API keys
- Check Python environment: `/home/david/miniforge3/bin/python --version`

## Quick Reference Commands

```bash
# Check everything is running
sudo systemctl status asp-ai-agent nginx

# View live application logs
sudo journalctl -u asp-ai-agent -f

# Add new user
sudo htpasswd /etc/nginx/auth/asp_ai_agent.htpasswd newuser

# Renew SSL certificate manually
sudo certbot renew

# Test Nginx config
sudo nginx -t

# Reload Nginx (apply config changes)
sudo systemctl reload nginx
```

## Support

For issues or questions:
- Check application logs in `/home/david/projects/asp_ai_agent/logs/`
- Check Nginx logs in `/var/log/nginx/`
- Review systemd service status: `sudo systemctl status asp-ai-agent`
