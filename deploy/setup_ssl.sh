#!/bin/bash
# Setup SSL Certificate with Let's Encrypt for ASP AI Agent
# Run AFTER domain is configured and pointing to your server
# Run with: sudo bash deploy/setup_ssl.sh

set -e

echo "=== ASP AI Agent SSL Certificate Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo bash deploy/setup_ssl.sh)"
    exit 1
fi

DOMAIN="asp-ai-agent.com"
EMAIL="your-email@example.com"  # Update this with your email

echo "IMPORTANT: Before running this script, ensure:"
echo "  1. Domain $DOMAIN points to 50.5.30.133"
echo "  2. Router port forwarding is configured:"
echo "     - Port 80 (HTTP) → 192.168.1.163:80"
echo "     - Port 443 (HTTPS) → 192.168.1.163:443"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Install certbot
echo "[1/5] Installing certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Create webroot directory for ACME challenge
echo "[2/5] Creating webroot directory..."
mkdir -p /var/www/certbot

# Install temporary Nginx config for initial certificate request
echo "[3/5] Setting up temporary Nginx configuration..."
cat > /etc/nginx/sites-available/asp-ai-agent-temp << 'EOF'
server {
    listen 80;
    server_name asp-ai-agent.com www.asp-ai-agent.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'ASP AI Agent - Certificate Setup';
        add_header Content-Type text/plain;
    }
}
EOF

# Enable temporary config
ln -sf /etc/nginx/sites-available/asp-ai-agent-temp /etc/nginx/sites-enabled/asp-ai-agent-temp
# Disable the current config temporarily
if [ -L /etc/nginx/sites-enabled/asp-ai-agent ]; then
    rm /etc/nginx/sites-enabled/asp-ai-agent
fi

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Obtain SSL certificate
echo "[4/5] Obtaining SSL certificate from Let's Encrypt..."
echo "This will request a certificate for $DOMAIN and www.$DOMAIN"
echo ""

certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

# Install production Nginx config with SSL
echo "[5/5] Installing production Nginx configuration..."
ln -sf /etc/nginx/sites-available/asp-ai-agent /etc/nginx/sites-enabled/asp-ai-agent
rm -f /etc/nginx/sites-enabled/asp-ai-agent-temp

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Setup automatic certificate renewal
echo ""
echo "Setting up automatic certificate renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "=== SSL Certificate Setup Complete! ==="
echo ""
echo "Your site is now accessible at:"
echo "  - https://asp-ai-agent.com/"
echo "  - https://www.asp-ai-agent.com/"
echo ""
echo "HTTP traffic will automatically redirect to HTTPS"
echo ""
echo "Certificate will automatically renew. Check status with:"
echo "  sudo systemctl status certbot.timer"
echo "  sudo certbot certificates"
echo ""
echo "To manually renew:"
echo "  sudo certbot renew"
echo ""
