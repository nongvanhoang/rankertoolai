# RankerToolAI — Complete Deployment Plan
**Target:** Ubuntu VPS + Nginx + Cloudflare
**Date:** 2026-06-17
**Status:** Ready to execute

---

## PRE-FLIGHT CHECKLIST

Before running any commands, confirm you have:

- [ ] SSH access to VPS (key-based, not password)
- [ ] Domain `rankertoolai.com` pointed to VPS IP in Cloudflare
- [ ] Cloudflare account access (for DNS + bot settings)
- [ ] Affiliate program URLs (for /go/ redirects in Nginx)
- [ ] Let's Encrypt certbot installed OR Cloudflare SSL active
- [ ] Local files in `C:\Users\Admin\RankerToolAI\`

---

# PART 1: FILE MAPPING

## 1.1 Infrastructure Files

| Local Path | Server Destination | Purpose |
|-----------|-------------------|---------|
| `infrastructure/robots.txt` | `/var/www/rankertoolai/html/robots.txt` | SEO — AI crawlers unlocked |
| `infrastructure/nginx-site.conf` | `/etc/nginx/sites-available/rankertoolai.com` | Nginx virtual host |
| `infrastructure/deploy.sh` | `/usr/local/bin/deploy-rankertoolai.sh` | Deployment script |
| `infrastructure/sitemap-template.xml` | `/var/www/rankertoolai/html/sitemap.xml` | XML sitemap for Google |

## 1.2 Template Files

| Local Path | Server Destination | Purpose |
|-----------|-------------------|---------|
| `templates/base.css` | `/var/www/rankertoolai/html/assets/css/base.css` | Global design system |
| `templates/review-template.html` | `/var/www/rankertoolai/html/templates/review-template.html` | OpenClaw template |
| `templates/comparison-template.html` | `/var/www/rankertoolai/html/templates/comparison-template.html` | OpenClaw template |
| `templates/alternatives-template.html` | `/var/www/rankertoolai/html/templates/alternatives-template.html` | OpenClaw template |

## 1.3 Pages Files

| Local Path | Server Destination | Purpose |
|-----------|-------------------|---------|
| `pages/affiliate-disclosure.html` | `/var/www/rankertoolai/html/affiliate-disclosure/index.html` | FTC compliance — REQUIRED |
| `pages/methodology.html` | `/var/www/rankertoolai/html/methodology/index.html` | E-E-A-T trust signal |

## 1.4 VPS Directory Structure (target state)

```
/var/www/rankertoolai/
└── html/
    ├── index.html                        ← Homepage
    ├── robots.txt                        ← DEPLOY
    ├── sitemap.xml                       ← DEPLOY
    ├── 404.html                          ← CREATE
    ├── 500.html                          ← CREATE
    │
    ├── assets/
    │   ├── css/
    │   │   └── base.css                  ← DEPLOY
    │   └── images/
    │       └── logos/                    ← Tool logos (PNG)
    │
    ├── templates/                        ← OpenClaw reads these
    │   ├── review-template.html          ← DEPLOY
    │   ├── comparison-template.html      ← DEPLOY
    │   └── alternatives-template.html    ← DEPLOY
    │
    ├── review/                           ← Individual reviews
    │   ├── index.html                    ← Reviews index
    │   ├── jasper/index.html
    │   ├── writesonic/index.html
    │   └── [tool]/index.html
    │
    ├── compare/                          ← VS comparisons
    │   ├── index.html
    │   ├── jasper-vs-writesonic/index.html
    │   └── [a]-vs-[b]/index.html
    │
    ├── alternatives/                     ← Alternatives pages
    │   ├── index.html
    │   ├── jasper/index.html
    │   └── [tool]/index.html
    │
    ├── best/                             ← Best-for pages
    │   └── [use-case]/index.html
    │
    ├── category/                         ← Category hubs
    │   ├── ai-writing/index.html
    │   ├── ai-image/index.html
    │   └── [category]/index.html
    │
    ├── about/index.html
    ├── methodology/index.html            ← DEPLOY
    ├── affiliate-disclosure/index.html   ← DEPLOY
    ├── privacy-policy/index.html
    ├── terms/index.html
    ├── contact/index.html
    ├── deals/index.html
    └── go/                              ← Handled by Nginx (301 redirects, not files)
```

---

# PART 2: VPS COMMANDS

Execute in this exact order. Each section is one SSH session block.

## BLOCK A — System Preparation

```bash
# SSH into your VPS
ssh -i ~/.ssh/your-key ubuntu@YOUR_VPS_IP

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  nginx \
  certbot \
  python3-certbot-nginx \
  git \
  fail2ban \
  ufw \
  curl \
  unattended-upgrades \
  logrotate

# Enable automatic security updates
sudo dpkg-reconfigure --priority=low unattended-upgrades
# Select "Yes" when prompted
```

## BLOCK B — User & Directory Setup

```bash
# Create dedicated web user (no login shell, no home dir)
sudo useradd -r -s /usr/sbin/nologin www-deploy

# Create directory structure
sudo mkdir -p /var/www/rankertoolai/html/assets/css
sudo mkdir -p /var/www/rankertoolai/html/assets/images/logos
sudo mkdir -p /var/www/rankertoolai/html/templates
sudo mkdir -p /var/www/rankertoolai/html/review
sudo mkdir -p /var/www/rankertoolai/html/compare
sudo mkdir -p /var/www/rankertoolai/html/alternatives
sudo mkdir -p /var/www/rankertoolai/html/best
sudo mkdir -p /var/www/rankertoolai/html/category
sudo mkdir -p /var/www/rankertoolai/html/affiliate-disclosure
sudo mkdir -p /var/www/rankertoolai/html/methodology
sudo mkdir -p /var/www/rankertoolai/html/about
sudo mkdir -p /var/www/rankertoolai/html/privacy-policy
sudo mkdir -p /var/www/rankertoolai/html/terms
sudo mkdir -p /var/www/rankertoolai/html/contact
sudo mkdir -p /var/log/rankertoolai
sudo mkdir -p /backups/rankertoolai

# Set ownership
sudo chown -R www-data:www-data /var/www/rankertoolai
sudo chown ubuntu:ubuntu /var/www/rankertoolai/html

# Set permissions
sudo chmod -R 755 /var/www/rankertoolai/html
sudo chmod 644 /var/www/rankertoolai/html/*.html 2>/dev/null || true
```

## BLOCK C — Git Version Control

```bash
# Initialize git on web root
cd /var/www/rankertoolai/html
git init
git config user.email "deploy@rankertoolai.com"
git config user.name "RankerToolAI Deploy"

# Add .gitignore
cat > .gitignore << 'EOF'
*.log
*.tmp
.DS_Store
Thumbs.db
EOF

# Initial commit (existing files)
git add -A
git commit -m "initial: existing site content"

# Add remote (create private repo on GitHub first)
# git remote add origin git@github.com:YOUR_ORG/rankertoolai-content.git
# git push -u origin main
```

## BLOCK D — Upload Local Files (run from Windows PowerShell)

```powershell
# Run these on your LOCAL Windows machine (PowerShell)
# Replace YOUR_VPS_IP with actual IP
# Replace your-key with your SSH key path

$VPS = "ubuntu@YOUR_VPS_IP"
$KEY = "C:\Users\Admin\.ssh\your-key"
$LOCAL = "C:\Users\Admin\RankerToolAI"

# Upload infrastructure files
scp -i $KEY "$LOCAL\infrastructure\robots.txt" "${VPS}:/var/www/rankertoolai/html/robots.txt"
scp -i $KEY "$LOCAL\infrastructure\sitemap-template.xml" "${VPS}:/var/www/rankertoolai/html/sitemap.xml"
scp -i $KEY "$LOCAL\infrastructure\deploy.sh" "${VPS}:/usr/local/bin/deploy-rankertoolai.sh"

# Upload CSS
scp -i $KEY "$LOCAL\templates\base.css" "${VPS}:/var/www/rankertoolai/html/assets/css/base.css"

# Upload HTML templates
scp -i $KEY "$LOCAL\templates\review-template.html" "${VPS}:/var/www/rankertoolai/html/templates/review-template.html"
scp -i $KEY "$LOCAL\templates\comparison-template.html" "${VPS}:/var/www/rankertoolai/html/templates/comparison-template.html"
scp -i $KEY "$LOCAL\templates\alternatives-template.html" "${VPS}:/var/www/rankertoolai/html/templates/alternatives-template.html"

# Upload pages
scp -i $KEY "$LOCAL\pages\affiliate-disclosure.html" "${VPS}:/var/www/rankertoolai/html/affiliate-disclosure/index.html"
scp -i $KEY "$LOCAL\pages\methodology.html" "${VPS}:/var/www/rankertoolai/html/methodology/index.html"

# Upload Nginx config
scp -i $KEY "$LOCAL\infrastructure\nginx-site.conf" "${VPS}:/tmp/rankertoolai.conf"
```

## BLOCK E — Nginx Configuration (back on VPS)

```bash
# Move Nginx config to correct location
sudo mv /tmp/rankertoolai.conf /etc/nginx/sites-available/rankertoolai.com

# BEFORE enabling: edit your affiliate URLs in the config
sudo nano /etc/nginx/sites-available/rankertoolai.com
# Update these lines with your real affiliate tracking URLs:
#   location = /go/jasper/     → your Jasper affiliate URL
#   location = /go/writesonic/ → your Writesonic affiliate URL
#   (etc.)

# Harden global Nginx config
sudo nano /etc/nginx/nginx.conf
# Add inside http {} block:
# ----------------------------------------
# server_tokens off;
# client_max_body_size 10M;
# limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;
# limit_req_zone $binary_remote_addr zone=static:10m rate=100r/m;
# ----------------------------------------

# Remove default Nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Enable RankerToolAI site
sudo ln -s /etc/nginx/sites-available/rankertoolai.com /etc/nginx/sites-enabled/

# Test Nginx config — MUST pass before reload
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx

# Verify Nginx is running
sudo systemctl status nginx
```

## BLOCK F — SSL Certificate

```bash
# Option A: Let's Encrypt (recommended if not using Cloudflare SSL)
sudo certbot --nginx -d rankertoolai.com -d www.rankertoolai.com \
  --non-interactive --agree-tos \
  --email your@email.com

# Verify auto-renewal works
sudo certbot renew --dry-run

# Option B: If using Cloudflare SSL (Origin Certificate)
# 1. In Cloudflare → SSL/TLS → Origin Server → Create Certificate
# 2. Download the cert and key files
# 3. Upload to VPS:
#    sudo mkdir -p /etc/ssl/rankertoolai
#    sudo nano /etc/ssl/rankertoolai/fullchain.pem  (paste cert)
#    sudo nano /etc/ssl/rankertoolai/privkey.pem    (paste key)
#    sudo chmod 600 /etc/ssl/rankertoolai/privkey.pem
# 4. Update nginx-site.conf ssl_certificate paths accordingly
```

## BLOCK G — Firewall (UFW)

```bash
# Reset to defaults
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT: do this BEFORE enabling UFW)
# If you changed SSH port from 22:
sudo ufw allow 2222/tcp comment 'SSH'
# If still on default port 22:
sudo ufw allow 22/tcp comment 'SSH'

# Allow web traffic
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Allow Cloudflare IPs only (optional hardening — blocks direct VPS access)
# Cloudflare IPv4 ranges (current as of 2026):
for ip in 173.245.48.0/20 103.21.244.0/22 103.22.200.0/22 103.31.4.0/22 \
          141.101.64.0/18 108.162.192.0/18 190.93.240.0/20 188.114.96.0/20 \
          197.234.240.0/22 198.41.128.0/17 162.158.0.0/15 104.16.0.0/13 \
          104.24.0.0/14 172.64.0.0/13 131.0.72.0/22; do
  sudo ufw allow from $ip to any port 80 comment 'Cloudflare'
  sudo ufw allow from $ip to any port 443 comment 'Cloudflare'
done

# Enable UFW
sudo ufw --force enable

# Verify
sudo ufw status verbose
```

## BLOCK H — Fail2ban

```bash
# Create jail config
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 86400
findtime = 600
maxretry = 5
backend  = systemd

[sshd]
enabled  = true
port     = ssh,2222
maxretry = 3
bantime  = 604800

[nginx-http-auth]
enabled  = true
port     = http,https

[nginx-botsearch]
enabled  = true
port     = http,https
logpath  = /var/log/nginx/rankertoolai.error.log
maxretry = 2
EOF

# Enable and start
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status
```

## BLOCK I — Deploy Script & Permissions

```bash
# Make deploy script executable
sudo chmod +x /usr/local/bin/deploy-rankertoolai.sh

# Create log directory
sudo mkdir -p /var/log/rankertoolai
sudo touch /var/log/rankertoolai/deploy.log
sudo chown ubuntu:ubuntu /var/log/rankertoolai/deploy.log

# Create backup script
sudo tee /usr/local/bin/backup-rankertoolai.sh << 'BACKUP'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/rankertoolai/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/html.tar.gz" /var/www/rankertoolai/html/
tar -czf "$BACKUP_DIR/nginx.tar.gz" /etc/nginx/
find /backups/rankertoolai -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +
echo "Backup complete: $BACKUP_DIR"
BACKUP

sudo chmod +x /usr/local/bin/backup-rankertoolai.sh

# Set up cron jobs
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-rankertoolai.sh >> /var/log/rankertoolai/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * certbot renew --quiet") | crontab -

# Verify cron
crontab -l
```

## BLOCK J — Log Rotation

```bash
sudo tee /etc/logrotate.d/rankertoolai << 'EOF'
/var/log/nginx/rankertoolai.*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        nginx -s reopen 2>/dev/null || true
    endscript
}

/var/log/rankertoolai/*.log {
    weekly
    missingok
    rotate 8
    compress
    notifempty
    create 0644 ubuntu ubuntu
}
EOF

# Test log rotation config
sudo logrotate --debug /etc/logrotate.d/rankertoolai
```

## BLOCK K — SSH Hardening

```bash
# Backup current SSH config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d)

# Apply hardening
sudo tee /etc/ssh/sshd_config.d/rankertoolai-hardening.conf << 'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
MaxSessions 3
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowAgentForwarding no
PermitEmptyPasswords no
LoginGraceTime 30
EOF

# Test SSH config (DO NOT reload until you verify your key works)
sudo sshd -t

# Only if test passes:
sudo systemctl reload sshd

# VERIFY: Open a NEW terminal window and test SSH login before closing current session
```

## BLOCK L — Final File Permissions & Git Commit

```bash
# Set correct permissions on all web files
sudo find /var/www/rankertoolai/html -type d -exec chmod 755 {} \;
sudo find /var/www/rankertoolai/html -type f -exec chmod 644 {} \;
sudo chown -R www-data:www-data /var/www/rankertoolai/html

# Allow ubuntu user to write (for deployments)
sudo setfacl -R -m u:ubuntu:rwx /var/www/rankertoolai/html
sudo setfacl -R -d -m u:ubuntu:rwx /var/www/rankertoolai/html

# Git commit all deployed files
cd /var/www/rankertoolai/html
git add -A
git commit -m "deploy: infrastructure + templates + trust pages [$(date +%Y%m%d)]"
```

---

# PART 3: CLOUDFLARE CONFIGURATION

## 3.1 DNS Settings

Log in to Cloudflare → Select `rankertoolai.com` → DNS

```
Type  Name    Content          Proxy   TTL
────────────────────────────────────────────
A     @       YOUR_VPS_IP      ✅ ON    Auto
A     www     YOUR_VPS_IP      ✅ ON    Auto
CNAME mail    YOUR_MAIL_HOST   ❌ OFF  Auto  (if applicable)
```

**Critical:** Both A records must have orange cloud (proxy) enabled.

## 3.2 SSL/TLS Settings

Cloudflare → SSL/TLS → Overview

```
SSL/TLS encryption mode: Full (strict)
```

Cloudflare → SSL/TLS → Edge Certificates:

```
✅ Always Use HTTPS: ON
✅ HTTP Strict Transport Security (HSTS):
    - Status: Enabled
    - Max Age: 12 months
    - Include subdomains: ON
    - Preload: ON (only after site is stable)
✅ Minimum TLS Version: TLS 1.2
✅ TLS 1.3: ON
✅ Opportunistic Encryption: ON
✅ Automatic HTTPS Rewrites: ON
```

## 3.3 AI Bot Settings (CRITICAL — fixes robots.txt issue)

### Method 1: Cloudflare Dashboard (preferred)

```
Cloudflare → Security → Bots → Bot Fight Mode
```

OR

```
Cloudflare → Security → AI Scrapers and Crawlers
```

Set the following bots to **ALLOW**:

| Bot | Action | Why |
|-----|--------|-----|
| Google-Extended | ✅ Allow | Google AI Overviews (critical for AI search traffic) |
| GPTBot | ✅ Allow | ChatGPT citations and recommendations |
| ClaudeBot | ✅ Allow | Claude AI citations |
| meta-externalagent | ✅ Allow | Meta AI (Llama-based) |
| Applebot-Extended | ✅ Allow | Apple Intelligence |
| Amazonbot | ❌ Block | No SEO value |
| Bytespider | ❌ Block | TikTok scraper |

### Method 2: If Cloudflare UI does not show bot options

The Cloudflare-managed robots.txt section is injected via Cloudflare's "Verified Bots" policy. Override it by uploading a custom robots.txt via a Cloudflare Worker:

```javascript
// Cloudflare Worker — replace robots.txt response
addEventListener('fetch', event => {
  if (event.request.url.endsWith('/robots.txt')) {
    event.respondWith(handleRobots())
  }
})

async function handleRobots() {
  const robotsContent = `User-agent: *
Allow: /
Disallow: /go/

User-agent: Amazonbot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

Sitemap: https://rankertoolai.com/sitemap.xml`

  return new Response(robotsContent, {
    headers: { 'Content-Type': 'text/plain' }
  })
}
```

Deploy at: Cloudflare → Workers & Pages → Create Worker → paste above → Deploy → Add Route: `rankertoolai.com/robots.txt`

## 3.4 Performance Settings

Cloudflare → Speed → Optimization:

```
✅ Auto Minify: HTML ✓, CSS ✓, JavaScript ✓
✅ Brotli: ON
✅ Early Hints: ON
✅ Rocket Loader: OFF (causes issues with inline scripts)
✅ Mirage: OFF (not needed for static HTML)
```

Cloudflare → Caching → Configuration:

```
Caching Level: Standard
Browser Cache TTL: 4 hours
Always Online: ON
```

## 3.5 Cache Rules

Cloudflare → Caching → Cache Rules → Create Rule:

**Rule 1: Cache static assets aggressively**
```
Name: Static Assets Long Cache
When: File extension matches css, js, jpg, jpeg, png, gif, webp, svg, woff, woff2
Then:
  - Cache status: Eligible for cache
  - Edge Cache TTL: 1 month
  - Browser TTL: 1 month
```

**Rule 2: HTML pages short cache**
```
Name: HTML Short Cache
When: File extension matches html OR URI path ends with /
Then:
  - Cache status: Eligible for cache
  - Edge Cache TTL: 1 hour
  - Browser TTL: 1 hour
```

**Rule 3: Never cache /go/ redirects**
```
Name: No Cache Affiliate Redirects
When: URI path starts with /go/
Then:
  - Cache status: Bypass cache
```

## 3.6 Security Settings

Cloudflare → Security → Settings:

```
Security Level: Medium
Challenge Passage: 30 minutes
Browser Integrity Check: ON
Privacy Pass Support: ON
```

Cloudflare → Security → WAF → Managed Rules:

```
✅ Cloudflare Managed Ruleset: ON (default)
✅ Cloudflare OWASP Core Ruleset: ON
   - Sensitivity: Low (start here, increase if no false positives)
```

## 3.7 Page Rules (if on Free plan, max 3 rules)

```
Rule 1: Redirect www to non-www
  URL: www.rankertoolai.com/*
  Setting: Forwarding URL (301)
  Destination: https://rankertoolai.com/$1

Rule 2: Force HTTPS
  URL: http://rankertoolai.com/*
  Setting: Always Use HTTPS
```

---

# PART 4: ROLLBACK PLAN

## Nginx Rollback

```bash
# If Nginx config breaks the site:

# Option A: Restore from backup
sudo cp /etc/nginx/sites-available/rankertoolai.com /etc/nginx/sites-available/rankertoolai.com.bad
sudo cp /etc/nginx/sites-available/rankertoolai.com.backup /etc/nginx/sites-available/rankertoolai.com
sudo nginx -t && sudo systemctl reload nginx

# Option B: Disable site, restore default
sudo rm /etc/nginx/sites-enabled/rankertoolai.com
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

## Content Rollback (Git)

```bash
# View recent commits
cd /var/www/rankertoolai/html
git log --oneline -10

# Rollback to previous commit
git revert HEAD         # Creates new commit undoing last change (safest)
# OR
git reset --hard HEAD~1 # Hard reset to 1 commit ago (destructive — use with caution)

# After rollback, reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

## robots.txt Rollback

```bash
# Restore original robots.txt (re-block all AI crawlers)
cat > /var/www/rankertoolai/html/robots.txt << 'EOF'
User-agent: *
Allow: /
Sitemap: https://rankertoolai.com/sitemap.xml
EOF
```

## Cloudflare Rollback

```
If Cloudflare WAF causes false positives (blocking real users):
  Security → WAF → Managed Rules → Sensitivity → Lower to "Off"
  Then investigate and re-enable rule by rule

If Cloudflare cache serves stale content:
  Caching → Configuration → Purge Everything

If SSL breaks:
  SSL/TLS → Overview → Switch from "Full (strict)" to "Full"
```

## Full Emergency Rollback (site down)

```bash
# Step 1: Disable Cloudflare proxy (grey cloud) — bypasses CF, hits VPS directly
# Cloudflare → DNS → click orange cloud on A records → set to grey

# Step 2: Verify VPS is responding directly
curl -I http://YOUR_VPS_IP

# Step 3: Fix on VPS
# Step 4: Re-enable Cloudflare proxy
```

---

# PART 5: VALIDATION CHECKLIST

Run these checks AFTER deployment. Check each one before marking complete.

## 5.1 Infrastructure Checks

```bash
# On VPS — run all at once
echo "=== NGINX STATUS ===" && sudo systemctl status nginx | grep Active
echo "=== NGINX CONFIG ===" && sudo nginx -t
echo "=== UFW STATUS ===" && sudo ufw status verbose
echo "=== FAIL2BAN ===" && sudo fail2ban-client status
echo "=== SSL CERT ===" && sudo certbot certificates
echo "=== DISK SPACE ===" && df -h /
echo "=== OPEN PORTS ===" && sudo ss -tlnp
echo "=== CRON JOBS ===" && crontab -l
```

Expected output: Nginx active, config OK, UFW enabled with correct ports, Fail2ban running, SSL cert valid 60+ days, disk < 70%, only ports 22/2222/80/443 open.

## 5.2 HTTP Checks

```bash
# Run from local machine (or VPS with curl)

# Test 1: HTTP → HTTPS redirect
curl -I http://rankertoolai.com
# Expected: 301 → https://rankertoolai.com/

# Test 2: www → non-www redirect
curl -I https://www.rankertoolai.com
# Expected: 301 → https://rankertoolai.com/

# Test 3: Homepage returns 200
curl -I https://rankertoolai.com
# Expected: 200 OK

# Test 4: Affiliate redirect works
curl -I https://rankertoolai.com/go/jasper/
# Expected: 301 → your Jasper affiliate URL

# Test 5: robots.txt accessible
curl https://rankertoolai.com/robots.txt
# Expected: Content without "Disallow: /" for Google-Extended

# Test 6: Sitemap accessible
curl -I https://rankertoolai.com/sitemap.xml
# Expected: 200 OK, Content-Type: application/xml

# Test 7: Affiliate disclosure page
curl -I https://rankertoolai.com/affiliate-disclosure/
# Expected: 200 OK

# Test 8: Methodology page
curl -I https://rankertoolai.com/methodology/
# Expected: 200 OK

# Test 9: 404 handling
curl -I https://rankertoolai.com/this-page-does-not-exist/
# Expected: 404 (not 200 or 500)
```

## 5.3 Security Header Checks

```bash
curl -I https://rankertoolai.com 2>/dev/null | grep -E \
  "X-Frame-Options|X-Content-Type|Strict-Transport|Referrer-Policy|Permissions-Policy|Content-Security"
```

Expected (all 6 headers must be present):
```
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff
strict-transport-security: max-age=31536000; includeSubDomains
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), microphone=(), camera=()
content-security-policy: default-src 'self'; ...
```

## 5.4 SSL Check

```bash
# Check SSL grade
curl -s "https://api.ssllabs.com/api/v3/analyze?host=rankertoolai.com&publish=off&all=done" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('endpoints',[{}])[0].get('grade','pending — retry in 60s'))"

# Or check manually: https://www.ssllabs.com/ssltest/
# Target: Grade A or A+
```

## 5.5 SEO Checks

```bash
# Check robots.txt content
curl -s https://rankertoolai.com/robots.txt | grep -E "Google-Extended|GPTBot|ClaudeBot"
# Expected: NO "Disallow: /" lines for these bots

# Check sitemap is valid XML
curl -s https://rankertoolai.com/sitemap.xml | python3 -c \
  "import sys; import xml.etree.ElementTree as ET; ET.parse(sys.stdin); print('Sitemap XML: VALID')"
```

## 5.6 Performance Check

```bash
# Check Gzip is working
curl -H "Accept-Encoding: gzip,deflate" -I https://rankertoolai.com | grep -i content-encoding
# Expected: content-encoding: gzip (or br for Brotli)

# Check cache headers on CSS
curl -I https://rankertoolai.com/assets/css/base.css | grep -i cache-control
# Expected: cache-control: public, immutable (or similar long cache)

# Check response time
time curl -o /dev/null -s https://rankertoolai.com
# Target: < 500ms TTFB
```

## 5.7 Google Search Console (manual — do within 24 hours)

```
1. Go to: https://search.google.com/search-console/
2. Add property: https://rankertoolai.com/
3. Verify ownership (HTML tag or DNS TXT record via Cloudflare DNS)
4. Submit sitemap: Sitemaps → Add sitemap URL → sitemap.xml
5. Request indexing of:
   - https://rankertoolai.com/
   - https://rankertoolai.com/affiliate-disclosure/
   - https://rankertoolai.com/methodology/
6. Monitor: Coverage → check for crawl errors
```

## 5.8 Cloudflare Validation (check in dashboard)

```
✅ SSL/TLS mode: Full (strict)
✅ Always Use HTTPS: ON
✅ DNS: Both A records orange cloud (proxied)
✅ Cache Rules: 3 rules active
✅ WAF: Cloudflare Managed Ruleset enabled
✅ AI Crawlers: Google-Extended, GPTBot allowed
✅ Analytics: Cloudflare Web Analytics enabled
✅ Bot Fight Mode: ON (ensure legitimate bots still allowed)
```

## 5.9 Final Sign-Off Checklist

```
INFRASTRUCTURE
[ ] Nginx serving site — HTTP 200 on homepage
[ ] HTTP → HTTPS redirect working
[ ] www → non-www redirect working
[ ] SSL cert valid, Grade A or higher
[ ] UFW firewall active, only 22/80/443 open
[ ] Fail2ban running
[ ] Git initialized, initial commit done
[ ] Backups cron scheduled (daily 2AM)
[ ] Log rotation configured

SEO
[ ] robots.txt accessible — no block on Google-Extended, GPTBot
[ ] sitemap.xml accessible — valid XML
[ ] Canonical tags present in all templates
[ ] Structured data (JSON-LD) in all templates
[ ] Google Search Console verified and sitemap submitted

AFFILIATE
[ ] /go/jasper/ redirects to Jasper affiliate URL
[ ] /go/writesonic/ redirects to Writesonic affiliate URL
[ ] /go/copy-ai/ redirects to Copy.ai affiliate URL
[ ] /go/surfer-seo/ redirects to Surfer affiliate URL
[ ] /go/elevenlabs/ redirects to ElevenLabs affiliate URL
[ ] All /go/ redirects return HTTP 301

TRUST & LEGAL
[ ] /affiliate-disclosure/ returns 200
[ ] /methodology/ returns 200
[ ] Footer contains link to affiliate disclosure on all pages

SECURITY
[ ] All 6 security headers present in HTTP response
[ ] server_tokens off (Nginx version hidden in headers)
[ ] Cloudflare WAF active
[ ] SSH: PasswordAuthentication no
[ ] SSH: PermitRootLogin no

PERFORMANCE
[ ] Gzip/Brotli compression active
[ ] Static assets served with long cache headers
[ ] HTML served with 1-hour cache header
[ ] Cloudflare proxy active (orange cloud on DNS)
```

---

## POST-DEPLOYMENT: NEXT STEPS

```
Day 1 (after deploy):
  → Monitor Nginx error log: sudo tail -f /var/log/nginx/rankertoolai.error.log
  → Check GSC for crawl errors (check again after 24-48 hours)
  → Verify Cloudflare is caching (CF-Cache-Status: HIT in headers)

Day 2-7:
  → Run Review Agent: generate first 5 review pages
  → Run Comparison Agent: generate first 3 VS pages
  → Add each new page to sitemap.xml
  → Ping Google after each batch: https://search.google.com/ping?sitemap=https://rankertoolai.com/sitemap.xml

Week 2:
  → Check GSC Coverage — confirm pages are indexed
  → Check GSC Performance — confirm first impressions
  → Set up Google Analytics 4 or Plausible Analytics
```

---

*Deployment plan generated by RankerToolAI Website Completion Agent | 2026-06-17*
