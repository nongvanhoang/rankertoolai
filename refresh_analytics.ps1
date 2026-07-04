# RankerToolAI - Refresh GA4 analytics dashboard and redeploy just that page.
# Usage:
#   .\refresh_analytics.ps1
# Run manually anytime, or scheduled daily via setup_ga4_scheduler.ps1.

$ErrorActionPreference = "Continue"
$Root    = $PSScriptRoot
$HtmlDir = "$Root\html"

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
}

& "$Root\update_analytics_data.ps1" -Force
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: update_analytics_data.ps1 failed."
    exit 1
}

Log "Committing dashboard update..."
# html/ is its own separate git repo nested inside $Root (not a submodule) -
# commit inside it directly, not from $Root, or the change never gets tracked.
git -C $HtmlDir add dashboard/index.html 2>$null
$status = git -C $HtmlDir status --porcelain -- dashboard/index.html
if ($status) {
    git -C $HtmlDir commit -m "chore: refresh analytics dashboard $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Log "Committed."
} else {
    Log "No changes to commit."
}

Log "Deploying to Cloudflare Pages..."
npx wrangler pages deploy $HtmlDir --project-name=rankertoolai
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: wrangler deploy failed."
    exit 1
}

Log "Done. https://rankertoolai.com/dashboard/"
