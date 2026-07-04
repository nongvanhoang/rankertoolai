# Shared step: refresh ga4_report.json (unless already fresh) + rebuild the
# dashboard HTML. Does NOT commit or deploy - callers (deploy.ps1,
# refresh_analytics.ps1) own that. Not meant to be the only thing you run;
# see refresh_analytics.ps1 for the full commit+deploy flow.
#
# Usage:
#   .\update_analytics_data.ps1              # skip GA4 refetch if data < 6h old
#   .\update_analytics_data.ps1 -Force       # always refetch
#   .\update_analytics_data.ps1 -MaxAgeHours 1

param(
    [switch]$Force,
    [int]$MaxAgeHours = 6
)

$Root       = $PSScriptRoot
$Python     = "$Root\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$ReportFile = "$Root\ga4_report.json"

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
}

$needsFetch = $true
if (-not $Force -and (Test-Path $ReportFile)) {
    $ageHours = ((Get-Date) - (Get-Item $ReportFile).LastWriteTime).TotalHours
    if ($ageHours -lt $MaxAgeHours) {
        $needsFetch = $false
        Log "ga4_report.json is $([math]::Round($ageHours,1))h old (< ${MaxAgeHours}h) - skipping GA4 refetch."
    }
}

if ($needsFetch) {
    Log "Fetching latest GA4 data..."
    & $Python "$Root\ga4_tracker.py" --json $ReportFile
    if ($LASTEXITCODE -ne 0) {
        Log "WARNING: ga4_tracker.py failed (not authenticated / configured yet?). Dashboard will show fallback/stale data."
    }
}

Log "Rebuilding dashboard..."
& $Python "$Root\build_dashboard.py"
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: build_dashboard.py failed."
    exit 1
}
