# Tao Windows Task Scheduler chay social agent moi ngay
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\Admin\RankerToolAI\.venv\Scripts\python.exe" `
    -Argument "C:\Users\Admin\RankerToolAI\social_agent\main.py --platform devto" `
    -WorkingDirectory "C:\Users\Admin\RankerToolAI\social_agent"

# Chay luc 9:00 sang moi ngay
$trigger1 = New-ScheduledTaskTrigger -Daily -At "09:00AM"
# Chay luc 3:00 chieu moi ngay
$trigger2 = New-ScheduledTaskTrigger -Daily -At "03:00PM"

$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName "RankerToolAI_DevTo_Post" `
    -Action $action `
    -Trigger $trigger1,$trigger2 `
    -Settings $settings `
    -Description "Auto post AI tool reviews to Dev.to" `
    -RunLevel Highest `
    -Force

Write-Host "Task Scheduler da duoc tao!" -ForegroundColor Green
Write-Host "Kiem tra tai: Task Scheduler > Task Scheduler Library > RankerToolAI_DevTo_Post"
