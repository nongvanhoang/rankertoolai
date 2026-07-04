# Archive — không còn dùng trong pipeline chính thức

Ngày archive: 2026-07-03. Cập nhật: 2026-07-03 (kết hợp lại 2 pipeline sau khi
phát hiện Gen2 một mình không đủ credentials cho nhiều platform).

## Hai pipeline chính thức đang chạy song song (không trùng platform)

**A. `scheduler.py`** (task `RankerToolAI_Scheduler`, chạy `run-once` mỗi giờ)
+ `daily_run.py` (chạy tay/menu) — sở hữu: **LinkedIn, Discord, Dev.to,
Instagram** qua `linkedin_poster.py`, `post_discord.py`, `post_devto_auto.py`,
`post_instagram.py`. Twitter/Pinterest/Reddit/Threads/Medium/Quora cũng có
trong `scheduler.py` nhưng **chưa có credentials thật** (config JSON rỗng) —
chạy nhưng không đăng được gì (schedule_log ghi "ok" giả do exit code 0 dù
post lỗi âm thầm).

**B. `auto_post_all.py`** (task `RankerToolAI_Morning`, mỗi ngày) — sở hữu:
**Twitter (OAuth2, có credentials thật), Pinterest + LinkedIn(qua Buffer),
Bluesky, Reddit(nếu có key), Hashnode, Medium**. Có `GEN2_OWNED_PLATFORMS =
{linkedin, discord, devto}` để tự loại các platform đã thuộc pipeline A,
tránh đăng trùng. **`ZERNIO_PAUSED = True`** (tạm khoá Facebook+Instagram qua
Zernio) vì tài khoản Facebook/Instagram vừa bị Meta cảnh báo automation
2026-07-03 — xem `risky_browser_automation/` bên dưới. Gỡ cờ này trong
`auto_post_all.py` khi tài khoản ổn định trở lại.

## gen1_post_scripts/
Thế hệ code cũ nhất (20-24/6/2026), được `run_all.py` gọi qua Windows Task
Scheduler task `RankerToolAI-Daily` / `RankerToolAI_Social_Auto` — cả hai task
này đã bị tắt (disable) vì chạy trùng lịch, gây đăng bài lặp và rate-limit
error. `RankerToolAI_Social_Auto` cần quyền Admin để tắt — có thể vẫn đang
"Ready", tự tắt bằng: `schtasks /Change /TN RankerToolAI_Social_Auto /DISABLE`
(chạy PowerShell as Administrator).

`post_instagram.py` đã được đưa trở lại `social_agent/` (2026-07-03) và thêm
vào SCHEDULE của `scheduler.py` — đã sửa bug schema `posts.db` (cột
`posted_at` không tồn tại, gây log_post() luôn fail âm thầm) và thêm chế độ
mặc định (post 1 tool least-posted có carousel sẵn, khớp pattern discord/devto).
Cần cấu hình `INSTAGRAM_ACCESS_TOKEN` + `INSTAGRAM_BUSINESS_ID` trong `.env`
(xem hướng dẫn trong docstring đầu file, hoặc chạy `get_instagram_token.py`)
trước khi hoạt động thật.

## gen3_platforms_pipeline/
`auto_post_all.py`, `post_zernio.py`, `post_buffer.py`, `post_bluesky.py`, và
thư mục `platforms/` **đã được khôi phục về `social_agent/`** (2026-07-03) —
đây là pipeline B ở trên, không còn nằm trong archive nữa. Chỉ còn lại
`main.py` trong thư mục này — một CLI thủ công dùng chung `platforms/*.py`,
không được task nào gọi, giữ nguyên trong archive vì trùng chức năng với
`auto_post_all.py`.

## risky_browser_automation/  ⚠️
`browser_agent.py` + `computer_use_agent.py` — agent dùng AI điều khiển trình
duyệt thật (browser-use / Claude Computer Use) để tự đăng nhập và thao tác
trên Reddit/Twitter/Pinterest/Facebook nhằm tự tạo dev app / lấy API key.

**Đã gây cảnh báo "Hoạt động tự động của tài khoản" từ Meta trên tài khoản
Facebook/Instagram thật (2026-07-03)** sau khi chạy thử để liên kết Instagram
Business. Meta coi đây là automation mô phỏng hành vi con người — vi phạm
chính sách, có rủi ro khóa tài khoản nếu lặp lại.

**KHÔNG chạy lại 2 file này nhắm vào tài khoản mạng xã hội thật.** Nếu cần
lấy API key/token cho platform mới, dùng các helper OAuth chuẩn kiểu
`get_reddit_token.py` / `get_pinterest_token.py` / `get_linkedin_token.py` /
`get_instagram_token.py` (chỉ mở trình duyệt cho người dùng tự đăng nhập qua
OAuth thật, không mô phỏng thao tác) — không dùng agent tự động click.

## Ghi chú chung
Các file trong đây không bị xoá — chỉ archive để tránh nhầm lẫn khi bảo trì
hoặc vô tình chạy lại. Nếu muốn khôi phục một luồng nào (trừ
risky_browser_automation/), chuyển file trở lại `social_agent/` và bật lại
task tương ứng trong Task Scheduler.
