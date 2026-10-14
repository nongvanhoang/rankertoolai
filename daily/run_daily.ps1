# Task Scheduler "Ranker_DangBaiHangNgay" (daily 06:30, catches up at boot) runs this file.
Set-Location "C:\Users\Admin\RankerToolAI_reels"
& "C:\Program Files\nodejs\node.exe" "daily\send_daily.js" *>> "daily\send_daily.log"
