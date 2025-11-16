#!/bin/bash
# Production Deployment Setup for ASP AI Agent
# Run with: sudo bash deploy/setup_production.sh

set -e

echo "=== ASP AI Agent Production Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo bash deploy/setup_production.sh)"
    exit 1
fi

# 1. Install Nginx if not already installed
echo "[1/6] Installing Nginx..."
apt update
apt install -y nginx

# 2. Create logs directory
echo "[2/6] Creating logs directory..."
mkdir -p /home/david/projects/asp_ai_agent/logs
chown david:david /home/david/projects/asp_ai_agent/logs

# 3. Copy systemd service file
echo "[3/6] Installing systemd service..."
cp /home/david/projects/asp_ai_agent/deploy/asp-ai-agent.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable asp-ai-agent.service

# 4. Copy Nginx configuration
echo "[4/6] Installing Nginx configuration..."
cp /home/david/projects/asp_ai_agent/deploy/nginx-asp-ai-agent.conf /etc/nginx/sites-available/asp-ai-agent
ln -sf /etc/nginx/sites-available/asp-ai-agent /etc/nginx/sites-enabled/asp-ai-agent

# 5. Test Nginx configuration
echo "[5/6] Testing Nginx configuration..."
nginx -t

# 6. Start services
echo "[6/6] Starting services..."
systemctl start asp-ai-agent.service
systemctl restart nginx

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Service status:"
systemctl status asp-ai-agent.service --no-pager -l
echo ""
echo "Access your application at:"
echo "  - http://192.168.1.163/"
echo "  - http://localhost/"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status asp-ai-agent    # Check service status"
echo "  sudo systemctl restart asp-ai-agent   # Restart service"
echo "  sudo journalctl -u asp-ai-agent -f    # View live logs"
echo "  tail -f /home/david/projects/asp_ai_agent/logs/asp-ai-agent.log"
echo ""
