#!/usr/bin/env bash
# deploy.sh — Robust deploy script for VPS.
# Usage: bash scripts/deploy.sh <branch>
# Called by GitHub Actions or manually: bash scripts/deploy.sh develop
#
# Features:
#   - Checks out the specified branch and pulls latest
#   - Rebuilds and restarts Docker containers
#   - Runs a health check after restart
#   - Rolls back to the previous image on failure

set -euo pipefail

BRANCH="${1:-master}"
REPO_DIR="$HOME/moodtracker_bot"
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_URL="http://127.0.0.1:8000/"
HEALTH_TIMEOUT=30

echo "=== Deploy started ==="
echo "Branch : $BRANCH"
echo "Time   : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

cd "$REPO_DIR"

# ── 1. Save current image for rollback ────────────────────────
PREV_IMAGE=""
if docker compose -f "$COMPOSE_FILE" images --format json 2>/dev/null | grep -q "app"; then
    PREV_IMAGE=$(docker compose -f "$COMPOSE_FILE" images --format json 2>/dev/null \
        | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('Image',''))" 2>/dev/null || true)
fi
echo "[1/5] Previous image: ${PREV_IMAGE:-none}"

# ── 2. Git pull ───────────────────────────────────────────────
echo "[2/5] Pulling $BRANCH..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
echo "Checked out: $(git rev-parse --short HEAD)"

# ── 3. Build ──────────────────────────────────────────────────
echo "[3/5] Building..."
docker compose -f "$COMPOSE_FILE" build

# ── 4. Restart ────────────────────────────────────────────────
echo "[4/5] Restarting containers..."
docker compose -f "$COMPOSE_FILE" up -d

# ── 5. Health check ───────────────────────────────────────────
echo "[5/5] Health check (timeout ${HEALTH_TIMEOUT}s)..."
ELAPSED=0
until curl -sf "$HEALTH_URL" -o /dev/null; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ "$ELAPSED" -ge "$HEALTH_TIMEOUT" ]; then
        echo ""
        echo "❌ Health check FAILED after ${HEALTH_TIMEOUT}s"
        echo ""
        if [ -n "$PREV_IMAGE" ]; then
            echo "Rolling back to previous image: $PREV_IMAGE"
            docker compose -f "$COMPOSE_FILE" down
            docker tag "$PREV_IMAGE" "moodtracker_bot-app:latest" 2>/dev/null || true
            docker compose -f "$COMPOSE_FILE" up -d
            echo "Rollback attempted. Check logs: make prod-logs"
        else
            echo "No previous image available for rollback."
            echo "Check logs: docker compose -f $COMPOSE_FILE logs"
        fi
        exit 1
    fi
done

echo ""
echo "✅ Deploy successful — $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Commit: $(git rev-parse --short HEAD)"
docker compose -f "$COMPOSE_FILE" ps
