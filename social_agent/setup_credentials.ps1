# RankerToolAI — Social Credentials Setup Guide
# Chạy script này để hướng dẫn setup credentials cho các platforms còn thiếu

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  RANKERTOOLAI — SOCIAL CREDENTIALS SETUP" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra .env file
$envFile = "$PSScriptRoot\.env"
if (Test-Path $envFile) {
    Write-Host "[OK] .env file found: $envFile" -ForegroundColor Green
} else {
    Write-Host "[!] .env file không tìm thấy. Tạo mới..." -ForegroundColor Yellow
    New-Item -ItemType File -Path $envFile -Force | Out-Null
    Write-Host "[OK] Tạo .env tại: $envFile" -ForegroundColor Green
}

# Load current .env
$currentEnv = @{}
Get-Content $envFile -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        $currentEnv[$Matches[1].Trim()] = $Matches[2].Trim()
    }
}

Write-Host ""
Write-Host "PLATFORMS STATUS:" -ForegroundColor Yellow
Write-Host "-----------------"

# Check each platform
$platforms = @{
    "Twitter/X"  = @("TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET")
    "Reddit"     = @("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD")
    "LinkedIn"   = @("LINKEDIN_ACCESS_TOKEN", "LINKEDIN_PERSON_URN")
    "Pinterest"  = @("PINTEREST_ACCESS_TOKEN", "PINTEREST_BOARD_ID")
    "Discord"    = @("DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_IDS")
    "Dev.to"     = @("DEVTO_API_KEY")
    "Medium"     = @("MEDIUM_ACCESS_TOKEN")
    "Hashnode"   = @("HASHNODE_ACCESS_TOKEN", "HASHNODE_PUBLICATION_ID")
    "Instagram"  = @("INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID")
}

foreach ($platform in $platforms.Keys) {
    $keys = $platforms[$platform]
    $allSet = $true
    foreach ($key in $keys) {
        if (-not $currentEnv.ContainsKey($key) -or $currentEnv[$key] -eq "") {
            $allSet = $false
        }
    }
    if ($allSet) {
        Write-Host "  [OK] $platform" -ForegroundColor Green
    } else {
        $missing = $keys | Where-Object { -not $currentEnv.ContainsKey($_) -or $currentEnv[$_] -eq "" }
        Write-Host "  [X] $platform — Missing: $($missing -join ', ')" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  HƯỚNG DẪN LẤY CREDENTIALS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "REDDIT (quan trọng nhất — intent traffic cao)" -ForegroundColor Yellow
Write-Host "  1. Vào: https://www.reddit.com/prefs/apps"
Write-Host "  2. Scroll xuống → 'create another app'"
Write-Host "  3. Name: rankertoolai | Type: script"
Write-Host "  4. redirect uri: http://localhost:8080"
Write-Host "  5. Copy client_id (dưới tên app) và client_secret"
Write-Host "  Thêm vào .env:"
Write-Host "    REDDIT_CLIENT_ID=your_client_id" -ForegroundColor DarkGray
Write-Host "    REDDIT_CLIENT_SECRET=your_client_secret" -ForegroundColor DarkGray
Write-Host "    REDDIT_USERNAME=rankertoolai" -ForegroundColor DarkGray
Write-Host "    REDDIT_PASSWORD=your_reddit_password" -ForegroundColor DarkGray

Write-Host ""
Write-Host "LINKEDIN" -ForegroundColor Yellow
Write-Host "  1. Vào: https://developer.linkedin.com/"
Write-Host "  2. Create App → điền tên + company LinkedIn page"
Write-Host "  3. Products tab → Request 'Share on LinkedIn'"
Write-Host "  4. Auth tab → OAuth 2.0 → Add redirect URL: http://localhost:8080/callback"
Write-Host "  5. Chạy: python social_agent/get_linkedin_token.py để lấy access token"
Write-Host "  Thêm vào .env:"
Write-Host "    LINKEDIN_ACCESS_TOKEN=your_token" -ForegroundColor DarkGray
Write-Host "    LINKEDIN_PERSON_URN=your_person_urn" -ForegroundColor DarkGray

Write-Host ""
Write-Host "PINTEREST" -ForegroundColor Yellow
Write-Host "  1. Vào: https://developers.pinterest.com/"
Write-Host "  2. My apps → Create app"
Write-Host "  3. Generate access token (60 days) hoặc dùng OAuth"
Write-Host "  4. Tạo board 'Best AI Tools 2026' → copy Board ID từ URL"
Write-Host "  Thêm vào .env:"
Write-Host "    PINTEREST_ACCESS_TOKEN=your_token" -ForegroundColor DarkGray
Write-Host "    PINTEREST_BOARD_ID=your_board_id" -ForegroundColor DarkGray

Write-Host ""
Write-Host "DEV.TO (nếu chưa set)" -ForegroundColor Yellow
Write-Host "  1. Vào: https://dev.to/settings/extensions"
Write-Host "  2. Generate API key"
Write-Host "  Thêm vào .env:"
Write-Host "    DEVTO_API_KEY=your_api_key" -ForegroundColor DarkGray

Write-Host ""
Write-Host "DISCORD BOT" -ForegroundColor Yellow
Write-Host "  1. Vào: https://discord.com/developers/applications"
Write-Host "  2. New Application → Bot → Add Bot"
Write-Host "  3. Copy Token"
Write-Host "  4. Invite bot vào server: OAuth2 → bot → send messages"
Write-Host "  5. Copy channel IDs (Enable Developer Mode → right-click channel)"
Write-Host "  Thêm vào .env:"
Write-Host "    DISCORD_BOT_TOKEN=your_bot_token" -ForegroundColor DarkGray
Write-Host "    DISCORD_CHANNEL_IDS=channel_id_1,channel_id_2" -ForegroundColor DarkGray

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "SAU KHI THÊM CREDENTIALS VÀO .ENV:" -ForegroundColor Yellow
Write-Host "  python social_agent/run_all.py --status   → Verify credentials"
Write-Host "  python social_agent/run_all.py --force    → Test chạy tất cả"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Offer to open .env in editor
$openEnv = Read-Host "Mở .env file để edit ngay? (y/n)"
if ($openEnv -eq "y") {
    Start-Process notepad $envFile
}
