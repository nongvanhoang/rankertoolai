# Setup Windows Task Scheduler de chay run_all.py luc 9h sang moi ngay
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1

$python = (Get-Command python).Source
$script = "C:\Users\Admin\RankerToolAI\social_agent\run_all.py"
$taskName = "RankerToolAI_Social"

$action = New-ScheduledTaskAction -Execute $python -Argument $script -WorkingDirectory "C:\Users\Admin\RankerToolAI\social_agent"

$trigger = New-ScheduledTaskTrigger -Daily -At "09:00AM"

$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force

Write-Host ""
Write-Host "Task Scheduler configured:"
Write-Host "  Name: $taskName"
Write-Host "  Runs: Every day at 9:00 AM"
Write-Host "  Script: $script"
Write-Host ""
Write-Host "To run manually now:"
Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
Write-Host ""
Write-Host "To check logs:"
Write-Host "  cat C:\Users\Admin\RankerToolAI\social_agent\data\run_log.txt"
