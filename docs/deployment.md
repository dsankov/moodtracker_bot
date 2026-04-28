# Deployment Guide — MoodTracker Bot on VPS

## VPS Info

| Item       | Value              |
|------------|--------------------|
| IP         | 93.188.206.72      |
| OS         | Ubuntu             |
| Domain     | skaters.top        |
| Web server | nginx              |

---

## Quick Start (Copy-Paste)

### Upload repo to GitHub

```bash
# From your local machine (in the project directory)
git init                          # if not already a git repo
git add .
git commit -m "Initial commit"

# Create the repo on GitHub first: https://github.com/new
# Then:
git remote add origin git@github.com:dsankov/moodtracker_bot.git
git branch -M main
git push -u origin main
```

### Deploy to VPS (one-liner from local machine)

Replace `YOUR_USER` with your VPS SSH username:

```bash
# Clone & setup (first time only)
ssh YOUR_USER@93.188.206.72 "git clone https://github.com/dsankov/moodtracker_bot.git ~/moodtracker_bot && cd ~/moodtracker_bot && bash scripts/setup-vps.sh"
```

### Update VPS after pushing new code to GitHub

```bash
# From your local machine
git push
ssh YOUR_USER@93.188.206.72 "cd ~/moodtracker_bot && make deploy-prod"
```

`make deploy-prod` runs: `git pull` → `docker build` → `docker up -d`

---

## 1. Environment Variable: `APP_ENV`

The bot uses `APP_ENV` to switch between **development** and **production** modes.

| `APP_ENV`      | Webhook source           | Ngrok required |
|----------------|--------------------------|----------------|
| `development`  | ngrok tunnel URL (auto)  | Yes            |
| `production`   | `BASE_URL` directly      | No             |

### `.env` for production

```env
BOT_TOKEN=<your-bot-token>
ADMIN_IDS=[112033576]
APP_ENV=production
BASE_URL=https://skaters.top
```

### `.env` for local development

```env
BOT_TOKEN=<your-bot-token>
ADMIN_IDS=[112033576]
APP_ENV=development
BASE_URL=heroic-concise-halibut.ngrok-free.app
NGROK_AUTHTOKEN=<your-ngrok-token>
NGROK_URL=heroic-concise-halibut.ngrok-free.app
```

When `APP_ENV=production`, the [`hook_url`](app/config.py:60) property returns `{BASE_URL}/webhook` directly — no ngrok API call is made.

---

## 2. Architecture (Production)

```
Telegram ──▶ skaters.top (nginx/443) ──▶ 127.0.0.1:8000 (Docker/FastAPI)
```

- **nginx** terminates TLS (Let's Encrypt) and reverse-proxies to the Docker container on port 8000.
- The Docker container only binds to `127.0.0.1:8000` (not exposed to the public).
- No ngrok is used in production.

---

## 3. Initial VPS Setup

### 3.1 Install Docker

```bash
ssh your-user@93.188.206.72

# Install Docker + Compose
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and back in for group to take effect
```

### 3.2 Install Certbot (Let's Encrypt)

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 3.3 Configure nginx

Copy the provided config:

```bash
sudo cp nginx/moodtracker.conf /etc/nginx/sites-available/moodtracker.conf
sudo ln -sf /etc/nginx/sites-available/moodtracker.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3.4 Obtain SSL Certificate

```bash
sudo certbot --nginx -d skaters.top
```

Certbot will modify the nginx config to point to the real certificate paths and set up auto-renewal via systemd timer.

---

## 4. Deploying / Syncing Code to VPS

Three strategies, pick one:

### Strategy A: Git Pull (Recommended — simplest)

The project is already on GitHub at `dsankov/moodtracker_bot`.

```bash
# On VPS — first time
git clone https://github.com/dsankov/moodtracker_bot.git ~/moodtracker_bot
cd ~/moodtracker_bot

# Create production .env
cp .env.example .env
nano .env   # fill in BOT_TOKEN, ADMIN_IDS, APP_ENV=production, BASE_URL=https://skaters.top

# Build & start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

**To update** (one-liner from your local machine):

```bash
ssh your-user@93.188.206.72 \
  "cd ~/moodtracker_bot && git pull && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d"
```

Add this as a Makefile target (already included — `make deploy-prod`).

### Strategy B: Docker Hub / GHCR (pre-built images)

Push the image to a registry from CI or locally:

```bash
# Build and push (local or CI)
docker build -t dsankov/moodtracker-bot:latest .
docker push dsankov/moodtracker-bot:latest

# On VPS — pull and restart
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

For this, replace the `build:` section in `docker-compose.prod.yml` with:

```yaml
image: dsankov/moodtracker-bot:latest
# remove the build: block
```

### Strategy C: rsync (no Git on VPS)

```bash
rsync -avz --exclude='.git' --exclude='.venv' --exclude='data' \
  ./ your-user@93.188.206.72:~/moodtracker_bot/
```

Then SSH in and rebuild:

```bash
ssh your-user@93.188.206.72 \
  "cd ~/moodtracker_bot && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d"
```

---

## 5. Makefile Commands (Production)

| Command               | Description                                      |
|-----------------------|--------------------------------------------------|
| `make prod-build`     | Build production Docker image                    |
| `make prod-up`        | Start production containers                      |
| `make prod-down`      | Stop production containers                       |
| `make prod-logs`      | Tail production logs                             |
| `make prod-restart`   | Restart production containers                    |
| `make deploy-prod`    | Git pull + rebuild + restart (run on VPS)        |

---

## 6. DNS Setup

Point `skaters.top` to your VPS:

| Type | Name           | Value           |
|------|----------------|-----------------|
| A    | `skaters.top`  | `93.188.206.72` |
| A    | `www.skaters.top` | `93.188.206.72` |

---

## 7. Troubleshooting

### Check if bot is running

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=50
```

### Check nginx

```bash
sudo nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Test webhook endpoint

```bash
curl -k https://skaters.top/
# Should return {"message":"Hello, World!"}
```

### Renew SSL manually

```bash
sudo certbot renew
```

### Database location

The SQLite database is persisted at `./data/db.sqlite3` on the VPS (mounted as a Docker volume). Back it up with:

```bash
cp ~/moodtracker_bot/data/db.sqlite3 ~/db-backup-$(date +%Y%m%d).sqlite3
```
