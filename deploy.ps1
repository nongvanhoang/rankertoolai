# RankerToolAI - Full Deploy Script (Windows PowerShell)
# Usage:
#   .\deploy.ps1                              # deploy all changes
#   .\deploy.ps1 -Url "/review/jasper/"       # deploy + verify specific URL
#   .\deploy.ps1 -Social "jasper"             # deploy + trigger social post
#   .\deploy.ps1 -Url "/review/jasper/" -Social "jasper"
#   .\deploy.ps1 -Rollback                    # rollback to previous commit

param(
    [string]$Url     = "",
    [string]$Social  = "",
    [switch]$Rollback
)

$ErrorActionPreference = "Stop"
$Root    = $PSScriptRoot
$Python  = "$Root\.venv\Scripts\python.exe"
$HtmlDir = "$Root\html"

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
}

# -- Rollback mode -------------------------------------------------------------
if ($Rollback) {
    Log "ROLLBACK: reverting to previous git commit..."
    $prev = git -C $Root rev-parse HEAD~1 2>$null
    if (-not $prev) {
        Log "ERROR: No previous commit to rollback to."
        exit 1
    }
    git -C $Root checkout $prev -- html/
    Log "Files restored from commit $($prev.Substring(0,8)). Deploying..."
    npx wrangler pages deploy $HtmlDir --project-name=rankertoolai
    Log "Rollback deployed. Verify: https://rankertoolai.com$Url"
    exit 0
}

# -- Step 1: Generate sitemap --------------------------------------------------
Log "Step 1/6 - Generating sitemap..."
& $Python "$Root\generate_sitemap.py"
if ($LASTEXITCODE -ne 0) { Log "ERROR: sitemap generation failed"; exit 1 }

# -- Step 2: Refresh analytics dashboard ---------------------------------------
Log "Step 2/6 - Refreshing analytics dashboard..."
& "$Root\update_analytics_data.ps1"
if ($LASTEXITCODE -ne 0) { Log "WARNING: analytics dashboard refresh failed." }

# -- Step 3: Git commit --------------------------------------------------------
Log "Step 3/6 - Git commit..."
git -C $Root add html/ generate_sitemap.py after_deploy.py ga4_tracker.py build_dashboard.py gsc_tracker.py google_oauth.py deploy.ps1 refresh_analytics.ps1 update_analytics_data.ps1 setup_ga4_scheduler.ps1 .gitignore 2>$null
$status = git -C $Root status --porcelain
if ($status) {
    $msg = "deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    if ($Url) { $msg += " - $Url" }
    git -C $Root commit -m $msg
    Log "Committed: $msg"
} else {
    Log "No changes to commit."
}

# -- Step 4: Wrangler deploy ---------------------------------------------------
Log "Step 4/6 - Deploying to Cloudflare Pages..."
npx wrangler pages deploy $HtmlDir --project-name=rankertoolai
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: wrangler deploy failed. To rollback: .\deploy.ps1 -Rollback"
    exit 1
}
Log "Deploy complete."

# -- Step 5: After-deploy verification + IndexNow -----------------------------
Log "Step 5/6 - Post-deploy verification..."
Start-Sleep -Seconds 5   # give Cloudflare a moment to propagate

$afterArgs = @()
if ($Url)    { $afterArgs += $Url }
if ($Social) { $afterArgs += "--social"; $afterArgs += $Social }

& $Python "$Root\after_deploy.py" @afterArgs
if ($LASTEXITCODE -ne 0) {
    Log "WARNING: some pages failed verification. Check output above."
}

# -- Step 6: Summary -----------------------------------------------------------
Log "Step 6/6 - Done."
Log "Live URL: https://rankertoolai.com$Url"
if ($Social) { Log "Social post triggered for: $Social" }
Log "Rollback anytime: .\deploy.ps1 -Rollback"
