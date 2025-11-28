#!/bin/bash
# Setup SSL Certificate with Let's Encrypt using DNS-01 challenge
# Use this when port 80 is not available externally
# Run with: sudo bash deploy/setup_ssl_dns.sh

set -e

echo "=== ASP AI Agent SSL Certificate Setup (DNS Challenge) ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo bash deploy/setup_ssl_dns.sh)"
    exit 1
fi

DOMAIN="asp-ai-agent.com"
EMAIL="dbhaslam@gmail.com"  # Update this with your email

echo "This script uses DNS-01 challenge (doesn't require port 80)"
echo ""
echo "You will need to manually add a TXT record to your DNS when prompted."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Install certbot
echo "[1/4] Installing certbot..."
apt-get update
apt-get install -y certbot

# Create webroot directory
echo "[2/4] Creating directories..."
mkdir -p /var/www/certbot

# Obtain SSL certificate using DNS challenge
echo "[3/4] Obtaining SSL certificate from Let's Encrypt..."
echo ""
echo "IMPORTANT: You will be prompted to add a TXT record to your DNS."
echo "Log into your domain registrar and add the TXT record when asked."
echo ""

certbot certonly \
    --manual \
    --preferred-challenges dns \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo ""
echo "[4/4] Certificate obtained!"
echo ""

# Note about renewal
echo ""
echo "=== SSL Certificate Setup Complete! ==="
echo ""
echo "IMPORTANT: Manual DNS challenge certificates don't auto-renew."
echo "You'll need to renew manually every 90 days using the same command."
echo ""
echo "Certificate location:"
echo "  /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "Next steps:"
echo "  1. Update Nginx config to use this certificate"
echo "  2. Test Nginx config: sudo nginx -t"
echo "  3. Reload Nginx: sudo systemctl reload nginx"
echo ""
