#!/usr/bin/env bash
# setup-vps.sh — Run this on your VPS (93.188.206.72) to set up the bot from scratch.
#
# Usage:
#   ssh your-user@93.188.206.72
#   git clone https://github.com/dsankov/moodtracker_bot.git ~/moodtracker_bot
#   cd ~/moodtracker_bot
#   bash scripts/setup-vps.sh
#
# Or as a one-liner from your local machine:
#   ssh your-user@93.188.206.72 "cd ~/moodtracker_bot && bash scripts/setup-vps.sh"

set -euo pipefail

DOMAIN="skaters.top"
REPO_DIR="$HOME/moodtracker_bot"

echo "=== MoodTracker Bot — VPS Setup ==="
echo ""

# ── 1. Install Docker ────────────────────────────────────────
if ! command -v docker &> /dev/null; then
    echo "[1/5] Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo "Docker installed. You may need to log out and back in for group changes."
    echo "Re-run this script after logging back in."
    exit 0
else
    echo "[1/5] Docker already installed ✓"
fi

# ── 2. Install Certbot ───────────────────────────────────────
if ! command -v certbot &> /dev/null; then
    echo "[2/5] Installing Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
else
    echo "[2/5] Certbot already installed ✓"
fi

# ── 3. Configure nginx ───────────────────────────────────────
echo "[3/5] Configuring nginx..."
sudo cp "$REPO_DIR/nginx/moodtracker.conf" /etc/nginx/sites-available/moodtracker.conf
sudo ln -sf /etc/nginx/sites-available/moodtracker.conf /etc/nginx/sites-enabled/

# Remove default site if it exists (optional, uncomment if needed)
# sudo rm -f /etc/nginx/sites-enabled/default

if sudo nginx -t 2>/dev/null; then
    sudo systemctl reload nginx
    echo "nginx configured ✓"
else
    echo "nginx config test failed! Check /etc/nginx/sites-available/moodtracker.conf"
    exit 1
fi

# ── 4. SSL Certificate ───────────────────────────────────────
echo "[4/5] Obtaining SSL certificate..."
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "SSL certificate already exists ✓"
else
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "Dmitry.Sankov@gmail.com"
    echo "SSL certificate obtained ✓"
fi

# ── 5. Create .env if missing ────────────────────────────────
echo "[5/5] Checking .env file..."
if [ ! -f "$REPO_DIR/.env" ]; then
    cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
    echo ""
    echo "⚠️  .env created from .env.example — you MUST edit it before starting:"
    echo "    nano $REPO_DIR/.env"
    echo ""
    echo "Required values:"
    echo "    BOT_TOKEN=<your-telegram-bot-token>"
    echo "    ADMIN_IDS=[<your-telegram-id>]"
    echo "    APP_ENV=production"
    echo "    BASE_URL=https://$DOMAIN"
    echo ""
    echo "After editing .env, build and start the bot:"
    echo "    cd $REPO_DIR && make prod-build && make prod-up"
    exit 0
else
    echo ".env exists ✓"
fi

# ── Build & Start ────────────────────────────────────────────
echo ""
echo "Building and starting the bot..."
cd "$REPO_DIR"
make prod-build
make prod-up

echo ""
echo "=== Setup Complete ==="
echo "Bot should be running at https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  make prod-logs     — view logs"
echo "  make prod-down     — stop"
echo "  make deploy-prod   — update (git pull + rebuild + restart)"
echo ""
echo "Test: curl https://$DOMAIN/"
