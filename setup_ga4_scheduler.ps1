# One-time: register a Windows Scheduled Task that refreshes the analytics
# dashboard (GA4 data + rebuild + redeploy) every day.
# Usage: .\setup_ga4_scheduler.ps1

$TaskName = "RankerToolAI-AnalyticsRefresh"
$Script   = "C:\Users\Admin\RankerToolAI\refresh_analytics.ps1"
$WorkDir  = "C:\Users\Admin\RankerToolAI"
$Time     = "07:30"

$Action   = New-ScheduledTaskAction -Execute "powershell.exe" `
              -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`"" `
              -WorkingDirectory $WorkDir
$Trigger  = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
              -RestartCount 1 -RestartInterval (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Force

Write-Host "Task created: $TaskName runs daily at $Time" -ForegroundColor Green
schtasks /query /tn $TaskName /fo LIST
