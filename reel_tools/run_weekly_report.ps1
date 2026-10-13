# Weekly reels report (Windows Task Scheduler "RankerReels_WeeklyReport", Mondays 07:00).
# Runs reels_report.py and pushes the result; the Telegram workflow delivers it.
Set-Location "C:\Users\Admin\RankerToolAI_reels"
& "C:\Users\Admin\AppData\Local\Python\bin\python.exe" "reel_tools\reels_report.py" --days 7 --push *>> "reel_tools\weekly_report.log"
