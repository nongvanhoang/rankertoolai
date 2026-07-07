# RankerToolAI — Growth System
# Hệ thống tăng trưởng bài bản: SEO + Social + Google Ads

> **Mục tiêu:** $3,000/tháng affiliate revenue trong 90 ngày
> **3 trụ cột:** Content SEO → Social Free Traffic → Google Ads (khuếch đại)

---

## HIỆN TRẠNG (2026-06-27)

| Hạng mục | Trạng thái | Ghi chú |
|----------|-----------|---------|
| Website | ✅ Live | 90+ trang, Cloudflare Pages |
| Content Pipeline | ✅ Hoạt động | PIPELINE.md |
| Social auto-post | ⚠️ 4/9 platforms | Discord, Twitter, Dev.to, Quora đang chạy |
| Reddit | ❌ Thiếu credentials | Cần nhất — intent traffic cao |
| LinkedIn | ❌ Thiếu credentials | B2B audience |
| Pinterest | ❌ Thiếu credentials | Long-tail visual traffic |
| Instagram | ❌ Thiếu credentials | Cần Business account |
| Google Ads | ❌ Chưa khởi động | Scripts sẵn sàng, cần AW ID |
| Affiliate Semrush | ⚠️ Pending approval | 40% recurring — ưu tiên #1 |
| Email list | ❌ Chưa có | Cần build ngay |

---

## TRỤC DOANH THU — THỨ TỰ ƯU TIÊN

```
TIER 1 — Commission cao, recurring:
  Semrush:    40% recurring  → $51/sale/tháng  [Approval pending — PUSH ngay]
  Jasper:     30% lifetime   → $18/sale/tháng
  Writesonic: 30% recurring  → $12/sale/tháng

TIER 2 — Commission tốt:
  Surfer SEO: 25% recurring  → $22/sale/tháng
  ElevenLabs: 22% 12 tháng  → $11/sale/tháng

TIER 3 — Volume cao, commission thấp:
  Canva:      15%/sale       → đang pending
  Notion:     $10/referral   → volume play
```

---

## PILLAR 1 — CONTENT SEO (nền tảng)

### Mục tiêu tháng 1-3
- Tháng 1: 120 → 160 trang (2 trang/ngày)
- Tháng 2: 160 → 220 trang (2 trang/ngày)
- Tháng 3: Tối ưu trang có traffic, build backlinks

### Content priority theo revenue

```
TUẦN 1-2: High-commission compares (intent mua cao nhất)
  /compare/jasper-vs-writesonic/       P1 — 30%+30%
  /compare/surfer-seo-vs-semrush/      P1 — đã có, cần thêm nội dung
  /compare/semrush-vs-ahrefs/          P1 — Semrush 40%
  /compare/jasper-vs-copy-ai/          P1 — đã có

TUẦN 3-4: Alternatives pages (volume cao)
  /alternatives/semrush/               P1 — 40% commission
  /alternatives/jasper/                P1 — đã có
  /alternatives/surfer-seo/            P1 — đã có
  /alternatives/writesonic/            P1 — đã có

TUẦN 5-6: Best-for pages (SEO rộng)
  /best/ai-seo-tools/                  P1 — đã có, cần thêm tools
  /best/ai-writing-tools/              P1 — đã có
  /best/ai-tools-for-marketers/        NEW
  /best/ai-tools-for-bloggers/         NEW
  /best/ai-tools-for-agencies/         NEW
```

### Quy trình 2 trang/ngày

```
Sáng 8:00 — Mở PIPELINE.md → paste vào Claude
  Gõ: /compare [tool A] [tool B]
  Claude tạo HTML → lưu vào html/ → deploy

Chiều 14:00 — Trang thứ 2
  Gõ: /review [tool] hoặc /alternatives [tool]
  Lưu → deploy → update sitemap
```

### Command tạo ngay hôm nay

```
/compare semrush ahrefs
/compare jasper writesonic
/best ai-tools-for-marketers
/review hubspot
/alternatives semrush
```

---

## PILLAR 2 — SOCIAL FREE TRAFFIC

### 2.1 Platforms đang chạy (không cần làm gì)
- **Discord** — Mỗi ngày 9:00 AM ✅
- **Twitter** — Mỗi ngày 9:00 AM ✅
- **Dev.to** — Mon/Wed/Fri ✅
- **Quora** — Tue/Thu/Sat ✅

### 2.2 Cần kích hoạt ngay (thêm credentials)

#### Reddit — QUAN TRỌNG NHẤT
Lý do: r/SEO, r/artificial, r/ChatGPT — intent traffic cao, affiliate conversion tốt

```bash
# Lấy credentials:
# 1. Vào https://www.reddit.com/prefs/apps
# 2. Create App → script → tên: rankertoolai
# 3. Redirect URI: http://localhost:8080

# Thêm vào .env:
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USERNAME=rankertoolai
REDDIT_PASSWORD=xxx
REDDIT_USER_AGENT=RankerToolAI/1.0

# Chiến lược karma (QUAN TRỌNG):
# Tuần 1-2: Comment hữu ích trong r/SEO, r/artificial, r/ChatGPT
# Chưa post link trực tiếp — bị ban ngay
# Sau khi có >100 karma: bắt đầu post nhẹ nhàng
```

#### LinkedIn — B2B audience, conversion tốt
```bash
# LinkedIn Developer App: https://developer.linkedin.com/
# Tạo app → Products → Share on LinkedIn + Sign In with LinkedIn
# OAuth 2.0 → Get Access Token

# Thêm vào .env:
LINKEDIN_ACCESS_TOKEN=xxx
LINKEDIN_PERSON_URN=xxx  # Lấy từ /v2/userinfo sau khi auth
```

#### Pinterest — Long-tail visual SEO
```bash
# Pinterest Developer: https://developers.pinterest.com/
# Tạo app → Get access token
# Tạo board "Best AI Tools 2026" → lấy Board ID

# Thêm vào .env:
PINTEREST_ACCESS_TOKEN=xxx
PINTEREST_BOARD_ID=xxx
```

### 2.3 Lịch đăng bài tối ưu (đã config trong run_all.py)

```
Thứ 2: Dev.to + Reddit + Pinterest + Discord + Twitter
Thứ 3: Quora + LinkedIn + Discord + Twitter
Thứ 4: Dev.to + Reddit + Discord + Twitter + Instagram
Thứ 5: Quora + LinkedIn + Pinterest + Discord + Twitter
Thứ 6: Dev.to + Reddit + LinkedIn + Discord + Twitter
Thứ 7: Quora + Discord + Twitter
Chủ nhật: Instagram + Discord + Twitter
```

### 2.4 Instagram + TikTok (cần setup riêng)

Instagram và TikTok yêu cầu tài khoản Business + phê duyệt API.

**Cách nhanh nhất:** Dùng Buffer.com (free tier 3 kênh) hoặc đăng thủ công carousel ảnh trong `social_agent/output/`.

Carousel đã được tạo sẵn cho ElevenLabs và Surfer SEO trong:
```
social_agent/output/[tool]/carousel/*.png  → đăng Instagram
social_agent/output/[tool]/video_frames/  → ghép thành TikTok video
```

### 2.5 Reddit karma building strategy

```
Tuần 1: Tham gia r/SEO, r/artificial, r/ChatGPT
  → Comment kiến thức thực sự hữu ích (không spam link)
  → Trả lời câu hỏi về AI tools với thông tin từ rankertoolai.com
  → Mục tiêu: 50+ comment karma

Tuần 2: Bắt đầu chia sẻ giá trị
  → Post "I tested X tools, here's what I found" — data thật
  → Mention rankertoolai.com chỉ khi relevant
  → Mục tiêu: 100+ karma

Tuần 3+: Post thường xuyên
  → post_reddit.py bắt đầu chạy tự động
  → Subreddits: r/SEO, r/artificial, r/blogging, r/Entrepreneur, r/SideProject
```

### 2.6 Email List (revenue multiplier)

Mỗi subscriber = $1-2/tháng long-term revenue.

```html
<!-- Newsletter form đã có trong inject_premium.py -->
<!-- Cần: signup với beehiiv.com hoặc ConvertKit (free tier) -->

Mục tiêu:
  Tháng 1: 100 subscribers
  Tháng 2: 300 subscribers
  Tháng 3: 500 subscribers

Cách collect:
  1. Exit-intent popup (Sumo free tier)
  2. "Weekly AI Tool Deals" incentive
  3. Cuối mỗi review: "Get notified when we review [competitor]"
```

---

## PILLAR 3 — GOOGLE ADS (khuếch đại)

### Nguyên tắc: Chỉ chạy khi organic đủ mạnh để prove conversion

**Điều kiện bắt đầu Google Ads:**
- Website có ít nhất 90 ngày hoạt động ✅
- Có ít nhất 1 conversion từ organic (affiliate click)
- Budget sẵn sàng: $300 cho tháng đầu test

### Bước khởi động (đã có scripts sẵn)

```
BƯỚC 1 — Lấy Google Ads ID
  ads.google.com → Tạo tài khoản → Tools > Tag
  Copy ID: AW-XXXXXXXXXX
  Điền vào: google_ads/data/config.json

BƯỚC 2 — Tạo Conversion Actions
  Goals > Conversions > New conversion action
  Action 1: "Affiliate Click" (count mỗi click vào /go/)
  Action 2: "Engaged Visit 60s"
  Copy IDs → điền vào config.json

BƯỚC 3 — Inject tracking
  cd google_ads
  python setup/inject_tracking.py --apply
  python setup/inject_utm_go.py --apply

BƯỚC 4 — Generate campaigns
  python campaigns/generate_campaigns.py
  → Output: data/google_ads_campaign_all_YYYYMMDD.csv

BƯỚC 5 — Upload lên Google Ads Editor
  Tải Google Ads Editor (desktop app)
  File > Import > From CSV
  Review → Upload to Google Ads

BƯỚC 6 — Khởi động chiến lược tuần 1
  Chỉ chạy: Campaign "Reviews" — 3 tools đầu tiên
  Budget: $10/ngày mỗi campaign
  Theo dõi hàng ngày bằng: python monitoring/budget_tracker.py --status
```

### Campaign structure đã được tạo

```
Campaign 1: RankerToolAI - AI Tool Reviews
  Ad Group: ElevenLabs Review
    Keywords: "elevenlabs review", "is elevenlabs worth it", "elevenlabs pricing"
    LP: /lp/elevenlabs/
    CTA: → /go/elevenlabs/
  
  Ad Group: Jasper Review
    Keywords: "jasper ai review", "jasper ai pricing", "jasper vs", "is jasper worth it"
    LP: /lp/jasper/

  Ad Group: Surfer SEO Review
    Keywords: "surfer seo review", "surfer seo pricing", "surfer seo worth it"
    LP: /lp/surfer-seo/

Campaign 2: RankerToolAI - Comparisons
  [keywords: "tool A vs tool B", "best [tool] alternative"]

Campaign 3: RankerToolAI - Best AI Tools
  [keywords: "best ai writing tools", "best ai seo tools", etc]
```

### ROAS targets & decision rules

```
Mỗi ngày nhập số liệu từ Google Ads vào:
  python google_ads/monitoring/budget_tracker.py --log \
    --campaign "Reviews" --spend 10.00 --clicks 25 \
    --conversions 2 --conv-value 20.00

Quyết định hàng tuần:
  ROAS > 3.0x  →  SCALE: tăng budget 20%
  ROAS 2-3x    →  KEEP: giữ nguyên, test thêm ad copies
  ROAS 1-2x    →  OPTIMIZE: review keywords, sửa LP
  ROAS < 1x    →  PAUSE: dừng, điều tra

Stop-loss tuyệt đối:
  > $50 spend/ngày mà 0 conversion → PAUSE ngay
  > $20 spend với ROAS < 1 → Pause campaign đó
```

### Landing page optimization

Landing pages tại `/lp/[tool]/` cần:
1. **Above fold CTA** — nút rõ ràng, màu cam
2. **Social proof** — "9.2/10 sau 30 ngày test"
3. **Trust signals** — "Independent review, not sponsored"
4. **Fast load** — Cloudflare CDN đã xử lý

---

## LỊCH TUẦN VẬN HÀNH

### Thứ 2 sáng (30 phút)
```bash
# 1. Check social stats
cd social_agent && python run_all.py --status

# 2. Check GSC rankings
python gsc_tracker.py

# 3. Tạo 2 trang content mới
# Mở PIPELINE.md → paste vào Claude → /compare hoặc /review

# 4. Check Google Ads (nếu đang chạy)
python google_ads/monitoring/budget_tracker.py --status
```

### Hàng ngày (5 phút)
```bash
# Kiểm tra social agent đã chạy chưa
type social_agent\data\run_log.txt | tail -20

# Nếu có lỗi → kiểm tra credentials
python social_agent/run_all.py --status
```

### Thứ 6 (weekly review — 1 tiếng)
```bash
# 1. Weekly content report
python weekly_ops.py

# 2. Google Ads weekly report
python google_ads/monitoring/budget_tracker.py --report

# 3. Quyết định content tuần tới (dựa trên traffic GSC)
# 4. Check affiliate payments đến chưa
```

---

## 90-DAY ROADMAP

### Tháng 1 (Tuần 1-4): Build

| Tuần | Content | Social | Ads | Revenue target |
|------|---------|--------|-----|----------------|
| 1 | +14 trang (compare focus) | Kích hoạt Reddit | Setup Google Ads account | $0 (seed) |
| 2 | +14 trang | Kích hoạt LinkedIn | Upload campaigns, $10/ngày | $50-100 |
| 3 | +14 trang | Pinterest running | Optimize top performers | $100-200 |
| 4 | +14 trang | Review toàn bộ | Scale ROAS > 2x | $200-400 |

### Tháng 2 (Tuần 5-8): Scale

| Tuần | Focus | Revenue target |
|------|-------|----------------|
| 5-6 | Content velocity + email list 100+ subs | $400-700 |
| 7-8 | Scale Google Ads, backlink outreach | $700-1,200 |

### Tháng 3 (Tuần 9-12): Compound

| Tuần | Focus | Revenue target |
|------|-------|----------------|
| 9-10 | YouTube 5 videos, Reddit community | $1,200-2,000 |
| 11-12 | Email campaigns, Semrush volume | $2,000-3,000 |

---

## CHECKLIST NGAY HÔM NAY

### Priority 1 (hôm nay)
- [ ] Đăng ký Semrush affiliate (Impact.com hoặc trực tiếp semrush.com/affiliates/)
- [ ] Tạo Reddit app để lấy credentials: reddit.com/prefs/apps
- [ ] Tạo LinkedIn app: developer.linkedin.com
- [ ] Tạo beehiiv.com account cho email list (free)
- [ ] Tạo 1 trang content mới: `/compare/semrush-vs-ahrefs/`

### Priority 2 (tuần này)
- [ ] Hoàn thiện Google Ads config.json với AW ID
- [ ] Chạy `python google_ads/campaigns/generate_campaigns.py`
- [ ] Upload CSV vào Google Ads Editor
- [ ] Pinterest Developer account + board setup
- [ ] Viết 5 Reddit comments kiến thức thực sự (build karma)

### Priority 3 (tháng này)
- [ ] YouTube: 3 video đầu tiên (dùng script từ content_ready.md)
- [ ] Backlink: guest post trên Indie Hackers, Dev.to
- [ ] Semrush approval → tạo /review/semrush/ hoàn chỉnh
- [ ] Email list: 100 subscribers đầu tiên

---

## REVENUE PROJECTION

```
Giả định: Convert rate 1% organic + 2% paid

Tháng 1 (100 organic visitors/ngày):
  Affiliate clicks: ~30/ngày × 1% = 0.3 sale/ngày
  ACV: $30-50/sale → $270-450/tháng

Tháng 2 (300 visitors/ngày organic + 50 paid):
  Affiliate clicks: ~100/ngày × 1.5% = 1.5 sale/ngày
  → $1,350-2,250/tháng

Tháng 3 (600 visitors/ngày + email 300 subs):
  Organic: ~200 clicks/ngày × 1.5% = 3 sales/ngày
  Email: 3% CTR × 3% = 0.09 sale/email send
  Paid: ROAS 2.5x = break-even, scale budget
  → $2,700-4,500/tháng
```

---

## FILES QUAN TRỌNG

```
GROWTH_SYSTEM.md         ← File này (master playbook)
PIPELINE.md              ← Tạo content
CHEATSHEET.md            ← Tham khảo nhanh
deploy.ps1               ← Deploy lên Cloudflare
weekly_ops.py            ← Weekly operations script

social_agent/
  run_all.py             ← Orchestrator (chạy bởi Task Scheduler)
  data/run_log.txt       ← Xem gì đã chạy
  data/tools.json        ← Danh sách tools

google_ads/
  README.md              ← Hướng dẫn đầy đủ
  data/config.json       ← Cần điền AW ID
  campaigns/             ← Generate CSV
  monitoring/            ← Dashboard + tracker
```
