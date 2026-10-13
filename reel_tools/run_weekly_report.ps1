# Weekly reels jobs (Windows Task Scheduler "RankerReels_WeeklyReport", Mondays 07:00):
# 1) price check (are the prices in our videos still live?), 2) GA4 report. Each pushes a
# social_posts/_... folder; the Telegram workflow delivers it to the owner.
Set-Location "C:\Users\Admin\RankerToolAI_reels"
& node "reel_tools\price_check.js" --push *>> "reel_tools\weekly_report.log"
& "C:\Users\Admin\AppData\Local\Python\bin\python.exe" "reel_tools\reels_report.py" --days 7 --push *>> "reel_tools\weekly_report.log"
