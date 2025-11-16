#!/bin/bash
# Setup HTTP Basic Authentication for ASP AI Agent
# Run with: sudo bash deploy/setup_auth.sh

set -e

echo "=== Setting up HTTP Basic Authentication ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo bash deploy/setup_auth.sh)"
    exit 1
fi

# Install apache2-utils for htpasswd command
echo "[1/2] Installing apache2-utils..."
apt-get update
apt-get install -y apache2-utils

# Create password file directory
echo "[2/2] Creating password file..."
mkdir -p /etc/nginx/auth

# Prompt for username and password
echo ""
echo "Enter username for asp_ai_agent.com access:"
read -r USERNAME

# Create password file (will prompt for password)
htpasswd -c /etc/nginx/auth/asp_ai_agent.htpasswd "$USERNAME"

# Set proper permissions
chmod 640 /etc/nginx/auth/asp_ai_agent.htpasswd
chown root:www-data /etc/nginx/auth/asp_ai_agent.htpasswd

echo ""
echo "=== Authentication Setup Complete! ==="
echo ""
echo "Password file created: /etc/nginx/auth/asp_ai_agent.htpasswd"
echo ""
echo "To add more users later, run:"
echo "  sudo htpasswd /etc/nginx/auth/asp_ai_agent.htpasswd <username>"
echo ""
