# Quick Start Guide - External Access (Custom Ports)

Since ports 80 and 443 are already in use by another server, we'll use:
- **Port 8080** for HTTP (external) → Port 80 (internal on 192.168.1.163)
- **Port 8443** for HTTPS (external) → Port 443 (internal on 192.168.1.163)

Users will access: `https://asp-ai-agent.com:8443`

## Prerequisites Checklist

Before you begin, ensure you have:

- [x] Domain asp-ai-agent.com purchased
- [ ] Access to domain DNS settings
- [ ] Access to your router admin panel
- [ ] Static public IP: 50.5.30.133
- [ ] Local server running at 192.168.1.163
- [ ] Email address for SSL certificate notifications

## Setup Steps (In Order)

### 1. Configure DNS

Log into your domain registrar and create these DNS records:

```
Type: A    Name: @      Value: 50.5.30.133
Type: A    Name: www    Value: 50.5.30.133
```

**Wait 15-30 minutes** for DNS to propagate.

Test with:
```bash
dig asp-ai-agent.com +short
# Should return: 50.5.30.133
```

### 2. Configure Router Port Forwarding

In your router admin panel, create these **CUSTOM** port forwarding rules:

```
Rule 1: ASP AI Agent HTTP
  External Port: 8080
  Internal IP: 192.168.1.163
  Internal Port: 80
  Protocol: TCP

Rule 2: ASP AI Agent HTTPS
  External Port: 8443
  Internal IP: 192.168.1.163
  Internal Port: 443
  Protocol: TCP
```

**Test port forwarding:**
```bash
# From outside your network (use phone cellular data)
curl -I http://asp-ai-agent.com:8080
# Should return HTTP response
```

### 3. Set Up Password Protection

```bash
sudo bash deploy/setup_auth.sh
```

Enter username and password when prompted.

### 4. Install SSL Certificate (DNS Challenge)

Since port 80 is not available externally, we use DNS challenge:

**First, update email in the script:**
```bash
nano deploy/setup_ssl_dns.sh
# Change EMAIL="your-email@example.com" to your real email
```

**Then run the script:**
```bash
sudo bash deploy/setup_ssl_dns.sh
```

**During the process, you will be asked to:**
1. Add a TXT record to your DNS
2. The record name will be like: `_acme-challenge.asp-ai-agent.com`
3. You'll be given a specific value to use
4. Add this record in your domain registrar's DNS panel
5. Wait for DNS propagation (1-5 minutes)
6. Press Enter in the terminal to continue

**DNS TXT Record Example:**
```
Type: TXT
Name: _acme-challenge
Value: [will be provided by certbot]
TTL: 300
```

### 5. Deploy External Configuration

```bash
# Copy external configuration
sudo cp deploy/nginx-asp-ai-agent-external.conf /etc/nginx/sites-available/asp-ai-agent

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### 6. Test Access

Visit **https://asp-ai-agent.com:8443** in your browser. You should:
1. Be prompted for username/password
2. See the ASP AI Agent interface after logging in

**Note the :8443 port number in the URL!**

## Access URLs

- **HTTPS (secure, preferred):** https://asp-ai-agent.com:8443
- **HTTP (redirects to HTTPS):** http://asp-ai-agent.com:8080

## Troubleshooting

**DNS not working?**
```bash
dig asp-ai-agent.com +short
# If it doesn't show 50.5.30.133, wait longer or check DNS settings
```

**Can't access externally on port 8080?**
```bash
# Test from outside your network (use cellular)
curl -I http://50.5.30.133:8080
# Should get HTTP response
```

**SSL certificate DNS challenge fails?**
- Make sure you added the TXT record correctly
- Wait 5 minutes for DNS propagation
- Verify TXT record: `dig _acme-challenge.asp-ai-agent.com TXT`

**Port 8443 not working?**
- Check router port forwarding for 8443 → 192.168.1.163:443
- Ensure Nginx is running: `sudo systemctl status nginx`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/asp-ai-agent-error.log`

## Important Notes

1. **Users must include :8443 in the URL** when accessing via HTTPS
2. **SSL certificate renewal is manual** with DNS challenge (every 90 days)
3. **Firewall rules** - ensure your server allows traffic on ports 80 and 443 internally

## Need More Help?

See the full guide: `deploy/EXTERNAL_ACCESS_SETUP.md`
