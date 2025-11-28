# Quick Start Guide - External Access Setup

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Domain asp-ai-agent.com purchased
- [ ] Access to domain DNS settings
- [ ] Access to your router admin panel
- [ ] Static public IP: 50.5.30.133
- [ ] Local server running at 192.168.1.163
- [ ] Email address for SSL certificate notifications

## Setup Steps (In Order)

### 1. Configure DNS (Do This First!)

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

In your router admin panel, create these port forwarding rules:

```
Rule 1:
  External Port: 80
  Internal IP: 192.168.1.163
  Internal Port: 80
  Protocol: TCP

Rule 2:
  External Port: 443
  Internal IP: 192.168.1.163
  Internal Port: 443
  Protocol: TCP
```

### 3. Set Up Password Protection

```bash
sudo bash deploy/setup_auth.sh
```

Enter username and password when prompted.

### 4. Update Email in SSL Script

```bash
nano deploy/setup_ssl.sh
# Change EMAIL="your-email@example.com" to your real email
```

### 5. Install SSL Certificate

**IMPORTANT:** Only run this after DNS is working (Step 1 complete)!

```bash
sudo bash deploy/setup_ssl.sh
```

### 6. Deploy External Configuration

```bash
sudo cp deploy/nginx-asp-ai-agent-external.conf /etc/nginx/sites-available/asp-ai-agent
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Test Access

Visit https://asp-ai-agent.com in your browser. You should:
1. Be prompted for username/password
2. See the ASP AI Agent interface after logging in

## Troubleshooting

**DNS not working?**
```bash
dig asp-ai-agent.com +short
# If it doesn't show 50.5.30.133, wait longer or check DNS settings
```

**Can't access externally?**
```bash
# Test from outside your network
curl -I http://50.5.30.133
# Should get HTTP response
```

**SSL certificate fails?**
- Verify DNS is working (step 1)
- Verify port 80 is forwarded (step 2)
- Check logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`

## Need More Help?

See the full guide: `deploy/EXTERNAL_ACCESS_SETUP.md`
