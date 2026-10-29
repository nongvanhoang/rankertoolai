# Task Scheduler "Ranker_HenGioTuan" (Sunday 18:00, catches up at boot) runs this file.
Set-Location "C:\Users\Admin\RankerToolAI_reels"
& "C:\Program Files\nodejs\node.exe" "daily\weekly_schedule.js" *>> "daily\weekly_schedule.log"
