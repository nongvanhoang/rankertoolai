# Weekly reels jobs (Windows Task Scheduler "RankerReels_WeeklyReport", Mondays 07:00):
# 1) price check (are the prices in our videos still live?), 2) GA4 report. Each writes a
# social_posts/_... folder (and pushes it on this branch); 3) send_reports.js delivers the new
# folders straight to the daily-posting Telegram group from this PC.
Set-Location "C:\Users\Admin\RankerToolAI_reels"
& node "reel_tools\price_check.js" --push *>> "reel_tools\weekly_report.log"
& "C:\Users\Admin\AppData\Local\Python\bin\python.exe" "reel_tools\reels_report.py" --days 7 --push *>> "reel_tools\weekly_report.log"
& node "daily\send_reports.js" *>> "reel_tools\weekly_report.log"
