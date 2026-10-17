# Gói bài đăng hàng ngày → Telegram

## Bảng việc (từ 17/10/2026)
Mỗi video là 1 thẻ = file MP4 gốc (không nén) + nút bấm: ☐/✅ từng kênh (bấm khi đăng xong, bấm lại để bỏ), 📋 Caption (chọn kênh → caption chạm-để-copy), 💬 Bình luận (bình luận ghim / đầu tiên), ⏭ Bỏ qua.
Lệnh trong nhóm: /homnay · /chuadang (bài còn nợ 14 ngày) · /tuan · /help. Gõ trong chủ đề nào thì chỉ xem thương hiệu đó.
Nút bấm do Cloudflare Worker `ranker-posting` xử lý (daily/worker, D1 `ranker-posting`), chạy cả khi máy tắt. Máy tính gửi thẻ lúc 6:30 rồi đăng ký với Worker (`config.json` board_url + biến môi trường RANKER_BOT_API_KEY). Worker lỗi → gói tự gửi kiểu cũ (caption từng tin).
Sửa Worker: `cd daily/worker && npx wrangler deploy` (đăng nhập `npx wrangler login`, BỎ biến CLOUDFLARE_API_TOKEN vì khoá đó chỉ dùng cho web).
Video đăng rồi trên kênh nào thì thẻ sau có cùng video hiện sẵn ✅ và không cho đánh dấu lại (chống trùng). Ngày máy tắt được gửi bù (tối đa 3 ngày); bài chưa xong hiện ở mục “📌 Còn nợ” mỗi sáng.

Mỗi sáng 6:30, máy tính gửi vào nhóm Telegram **"Đăng bài hàng ngày"** (2 mục: RankerToolAI, RankerNest):
video của hôm nay, rồi mỗi kênh 1 tin nhắn (caption trong khung, chạm để copy), cuối cùng là danh sách việc.
Tác vụ Windows: **Ranker_DangBaiHangNgay** chạy `daily/run_daily.ps1` (máy tắt lúc 6:30 thì gửi khi bật máy). Nhật ký: `daily/send_daily.log`.

## Cài đặt lần đầu (chủ tài khoản)
1. Lưu khoá bot (lấy trong @BotFather → /mybots → bot → API Token), chạy trong PowerShell:
   `[Environment]::SetEnvironmentVariable('TELEGRAM_BOT_TOKEN','<khoá>','User')`
2. Telegram: tạo nhóm, bật **Chủ đề (Topics)**, thêm `@rankernest_reels_bot` làm **quản trị viên**,
   tạo 2 chủ đề **RankerToolAI** và **RankerNest**, gõ `/rta` trong chủ đề đầu, `/rn` trong chủ đề sau (có dấu /, vì bot không phải quản trị viên chỉ đọc được lệnh).
3. `node daily/setup_telegram.js` rồi `node daily/setup_telegram.js --test`

## Lệnh hay dùng
| Việc | Lệnh |
|---|---|
| Xem trước gói của 1 ngày (không gửi) | `node daily/send_daily.js --dry-run --date 2026-10-20` |
| Gửi lại gói hôm nay | `node daily/send_daily.js --force` |
| Chỉ 1 thương hiệu | thêm `--only rn` hoặc `--only rta` |
| Gửi báo cáo tuần mới | `node daily/send_reports.js` (tự chạy sau báo cáo thứ Hai) |

## Dữ liệu
- `calendar.json` ← `build_calendar.js` từ `calendar_source.json` (lịch 14/10–12/11). Sửa lịch: sửa source rồi chạy lại build.
- `rn_queue.json` ← `RankerNest/social/launch/export_queue_tg.py` (32 bài hàng đợi RankerNest; tự bỏ bài có ảnh chưa được phép).
  Ngày RankerNest không có reel trong lịch (hoặc reel bị hoãn/hết hạn) sẽ lấy bài kế tiếp trong hàng đợi.
- `config.json`: nhóm, 2 chủ đề, thư mục video, `hold` = sản phẩm tạm hoãn (vd. EC200 hết hàng). Xoá khỏi `hold` khi có hàng lại.
- `state.json` (không commit): ngày nào đã gửi, vị trí hàng đợi, báo cáo đã gửi.
- Video đọc từ `C:\Users\Admin\Videos\RankerToolAI_reels\<tên reel>.mp4`; caption từ `social_posts/<reel>/tg/` và `social_videos/<reel>/caption.txt`.
- Kênh mỗi thương hiệu (quyết định 13/10): RankerNest = Instagram (chia sẻ sang Trang Facebook) · YouTube · TikTok (+ Pinterest qua CSV);
  RankerToolAI = Instagram · YouTube · TikTok, thêm Pinterest/LinkedIn/X theo lịch. RankerNest không làm Threads/X/LinkedIn.
- Kit có dòng "Không đăng sau YYYY-MM-DD" (vd. SilkSilky sale 22/10) tự bị bỏ qua sau ngày đó.
