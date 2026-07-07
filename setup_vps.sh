#!/bin/bash
# RankerToolAI — Ubuntu VPS Setup Script
# Chay: bash setup_vps.sh

set -e
REMOTE_DIR="/root/rankertoolai"
VENV="$REMOTE_DIR/.venv"

echo ""
echo "================================================"
echo "  RankerToolAI VPS Setup"
echo "================================================"

echo ""
echo "[1] Update & Install Python3..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv curl wget

echo ""
echo "[2] Create project directory..."
mkdir -p "$REMOTE_DIR/data"
mkdir -p "$REMOTE_DIR/logs"
mkdir -p "$REMOTE_DIR/platforms"

echo ""
echo "[3] Create Python venv..."
python3 -m venv "$VENV"

echo ""
echo "[4] Install Python dependencies..."
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q anthropic requests python-dotenv praw schedule

echo ""
echo "[5] Setup cron jobs (9:00 + 15:00 moi ngay)..."
(crontab -l 2>/dev/null | grep -v rankertoolai; cat << 'CRONEOF'
0 9  * * * cd /root/rankertoolai/social_agent && /root/rankertoolai/.venv/bin/python auto_post_all.py >> /root/rankertoolai/logs/auto_post.log 2>&1
0 15 * * * cd /root/rankertoolai/social_agent && /root/rankertoolai/.venv/bin/python auto_post_all.py >> /root/rankertoolai/logs/auto_post.log 2>&1
CRONEOF
) | crontab -

echo ""
echo "[6] Current cron jobs:"
crontab -l

echo ""
echo "[7] Verify Python setup..."
"$VENV/bin/python" --version

echo ""
echo "================================================"
echo "  SETUP DONE!"
echo "  Thu muc: $REMOTE_DIR"
echo "  Venv:    $VENV"
echo "  Logs:    $REMOTE_DIR/logs/auto_post.log"
echo "  Cron:    9:00 + 15:00 UTC moi ngay"
echo "================================================"
echo ""
echo "BUOC TIEP THEO:"
echo "  1. Upload cac file tu Windows vao $REMOTE_DIR/"
echo "     (dung FileZilla hoac WinSCP)"
echo "  2. Upload file .env vao $REMOTE_DIR/.env"
echo "  3. Test: cd $REMOTE_DIR && .venv/bin/python auto_post_all.py"
echo ""
