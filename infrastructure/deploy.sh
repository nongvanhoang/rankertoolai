#!/bin/bash
# RankerToolAI — Deployment Script
# Usage: ./deploy.sh [commit-message]
# Runs on VPS. Pulls from git main, validates, reloads Nginx.

set -e

SITE_DIR="/var/www/rankertoolai/html"
LOG_FILE="/var/log/rankertoolai/deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
COMMIT_MSG="${1:-auto-deploy: $(date '+%Y%m%d-%H%M%S')}"

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log "=== Deploy started ==="

# Pull latest from git
cd "$SITE_DIR"
git fetch origin main
CHANGES=$(git diff HEAD origin/main --name-only)

if [ -z "$CHANGES" ]; then
    log "No changes detected. Exiting."
    exit 0
fi

log "Changes detected:"
echo "$CHANGES" | tee -a "$LOG_FILE"

# Pull
git pull origin main
log "Git pull complete."

# Validate Nginx config
sudo nginx -t
if [ $? -ne 0 ]; then
    log "ERROR: Nginx config test failed. Aborting."
    exit 1
fi

# Reload Nginx
sudo systemctl reload nginx
log "Nginx reloaded."

# Verify homepage returns 200
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" https://rankertoolai.com)
if [ "$HTTP_STATUS" != "200" ]; then
    log "ERROR: Site returned HTTP $HTTP_STATUS after deploy!"
    exit 1
fi

log "Verification: HTTP $HTTP_STATUS — OK"
log "=== Deploy complete ==="
