$TaskName   = "RankerToolAI-Daily"
$Python     = "C:\Users\Admin\RankerToolAI\.venv\Scripts\python.exe"
$Script     = "C:\Users\Admin\RankerToolAI\social_agent\run_all.py"
$WorkingDir = "C:\Users\Admin\RankerToolAI\social_agent"
$Time       = "09:00"

$Action  = New-ScheduledTaskAction -Execute $Python -Argument $Script -WorkingDirectory $WorkingDir
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -RestartCount 1 -RestartInterval (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest -Force

Write-Host "Task created: $TaskName runs daily at $Time" -ForegroundColor Green
schtasks /query /tn $TaskName /fo LIST
