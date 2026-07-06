# Google Ads Launch Checklist — RankerToolAI

> **Thời gian thực hiện:** 2-3 giờ
> **Budget khởi động:** $300/tháng ($10/ngày)
> **Mục tiêu tuần 1:** Tìm được 1-2 keywords có ROAS > 2x

---

> **Cập nhật 2026-07-06:** Bước 1–4 đã xong (account AW-17663925702, 2 conversion actions,
> config.json + tracking đã inject, campaign CSV đã generate lại 2026-07-06 sau khi
> sửa 9 URL đích bị 404 trong generator — dùng file `google_ads_campaign_all_20260706_0452.csv`
> và `negative_keywords_20260706_0450.csv`, generator giờ tự cảnh báo nếu URL đích không tồn tại).
> CSV đã audit đạt chuẩn Editor 2026-07-06: format wide (1 dòng/entity, cột Headline 1-15,
> Description 1-4), headline ≤30 ký tự không cắt cụt, description ≤90 kết thúc trọn câu,
> display path ≤15, không headline trùng, không xung đột negative↔keyword, 32/32 URL đích tồn tại.
> **Còn lại: BƯỚC 5 (upload qua Google Ads Editor) + BƯỚC 6 (bật campaign, set budget).**

## PRE-LAUNCH (cần hoàn thành trước)

- [x] Website có ít nhất 10 landing pages (/lp/) ✅ đã có 14
- [x] GA4 tracking đang hoạt động (G-81KB8ECCVF) ✅
- [x] /go/ redirect tracking đang hoạt động ✅
- [x] Đã test conversion flow: LP → /go/ → affiliate site ✅ (test tự động 2026-07-06: LP render, click CTA bắn conversion AW-17663925702, /go/ redirect đúng link affiliate)

**Gợi ý thêm (2026-07-06):** tạo thêm conversion action thứ 3 — "Newsletter Signup",
loại Page view, đích là `https://rankertoolai.com/newsletter/thanks/` (mọi form newsletter
trên site giờ redirect về trang này, event `newsletter_confirmed` cũng tự bắn qua GA4).

---

## BƯỚC 1 — Tạo Google Ads Account (30 phút) ✅ XONG (AW-17663925702)

```
1. Vào: https://ads.google.com
2. Tạo tài khoản mới (hoặc dùng Google account hiện có)
3. Chọn: "Switch to Expert Mode" (không dùng Smart Campaign)
4. Bỏ qua wizard → vào Dashboard

5. Lấy Account ID (Customer ID): góc trên phải — dạng XXX-XXX-XXXX

6. Lấy Google Ads Tag ID:
   Tools & Settings > Tag > Google tag
   Copy: AW-XXXXXXXXXX
```

---

## BƯỚC 2 — Tạo Conversion Actions (20 phút) ✅ XONG (2 actions, labels trong config.json)

```
Goals > Conversions > New conversion action > Website

ACTION 1: Affiliate Click
  Category: Purchase (gần nhất với affiliate)
  Name: Affiliate Click
  Value: Use same value (default $15 — ACV affiliate)
  Count: Every
  Click-through window: 30 days
  → Copy Conversion ID + Label

ACTION 2: Engaged Visit
  Category: Page view
  Name: Engaged Visit 60s
  Value: Don't use (0)
  Count: Once per session
  → Copy Conversion ID + Label
```

---

## BƯỚC 3 — Update config.json (5 phút) ✅ XONG (tracking đã inject site-wide)

Mở file: `google_ads/data/config.json`

```json
{
  "ga4_id": "G-81KB8ECCVF",
  "google_ads_id": "AW-XXXXXXXXXX",
  "google_ads_conversion": {
    "affiliate_click": "AW-XXXXXXXXXX/YYYYYYYYYY",
    "page_view_60s":   "AW-XXXXXXXXXX/ZZZZZZZZZZ"
  }
}
```

Sau đó inject tracking:
```bash
cd google_ads
python setup/inject_tracking.py --apply
python setup/inject_utm_go.py --apply
python setup/inject_tracking.py --verify
```

---

## BƯỚC 4 — Generate Campaign CSV (10 phút) ✅ XONG (data/google_ads_campaign_all_20260706_0452.csv + negative_keywords_20260706_0450.csv)

```bash
python google_ads/campaigns/generate_campaigns.py
# Output: google_ads/data/google_ads_campaign_all_YYYYMMDD.csv

python google_ads/campaigns/generate_negative_keywords.py
# Output: google_ads/data/negative_keywords.csv
```

---

## BƯỚC 5 — Upload via Google Ads Editor (30 phút)

```
1. Download Google Ads Editor: https://ads.google.com/home/tools/ads-editor/

2. Connect account: File > Connect Account > nhập Customer ID

3. Import campaigns:
   File > Import > From File (CSV)
   Chọn: google_ads_campaign_all_YYYYMMDD.csv
   Review changes

4. Upload negative keywords:
   Tools > Shared Library > Negative Keyword Lists > Create new list
   Name: "RankerToolAI Master Negatives"
   Import từ: negative_keywords.csv

5. Gắn negative list vào tất cả campaigns

6. Review final:
   - Kiểm tra bid strategy: Manual CPC
   - Kiểm tra daily budget đúng không
   - Kiểm tra destination URLs trỏ đến /lp/

7. Post changes → Upload to Google Ads
```

---

## BƯỚC 6 — Cài đặt Ads trong Google Ads UI (20 phút)

```
LOCATION: United States, United Kingdom, Canada, Australia
(nơi affiliate commission cao nhất)

LANGUAGE: English

AD SCHEDULE: 6 AM - 11 PM (multiple time zones)
→ Pause từ 11 PM - 6 AM (thấp conversion)

DEVICE BID ADJUSTMENTS:
  Mobile: -20% (conversion thấp hơn desktop)
  Desktop: 0% (base)
  Tablet: -10%

BIDDING (tuần 1):
  Dùng: Manual CPC với Enhanced CPC bật
  Max CPC ban đầu: $1.50 (test trước khi optimize)
```

---

## BƯỚC 7 — Viết Ad Copies (40 phút)

Mỗi ad group cần **3 responsive search ads** (15 headlines, 4 descriptions):

### Template cho Review campaigns:

**ElevenLabs Review Ad:**
```
Headlines (viết 15, Google chọn tổ hợp tốt nhất):
  ElevenLabs Review 2026
  Is ElevenLabs Worth It?
  ElevenLabs: 9.2/10 Score
  Independent AI Voice Review
  We Tested ElevenLabs 30 Days
  ElevenLabs Pricing Breakdown
  Real ElevenLabs User Review
  ElevenLabs vs Competition
  Best AI Voice Generator?
  ElevenLabs Pros & Cons
  Honest ElevenLabs Review
  ElevenLabs Free Tier Tested
  AI Voice That Fools Humans
  ElevenLabs: Worth $5/Month?
  See Our ElevenLabs Score

Descriptions (viết 4):
  Independent review after 30 days of real testing. Score: 9.2/10. See full breakdown.
  We tested 10 AI voice generators. ElevenLabs wins on quality. Full comparison inside.
  Not sponsored. Our honest rating after testing voice cloning, languages, and API.
  9.2/10 score with real audio samples. Is ElevenLabs right for you? Find out now.

Final URL: https://rankertoolai.com/lp/elevenlabs/?utm_source=google&utm_medium=cpc
```

**Jasper Review Ad:**
```
Headlines:
  Jasper AI Review 2026
  Is Jasper Worth $39/Month?
  Jasper AI: 8.9/10 Score
  Honest Jasper AI Review
  We Used Jasper for 30 Days
  Jasper AI Pricing Guide
  Jasper vs Writesonic Review
  Best AI Writing Tool 2026?
  Jasper Pros & Cons Tested
  Independent Jasper Review
  Jasper AI Templates Reviewed
  Jasper Brand Voice Feature
  AI Writing Worth the Price?
  Jasper AI Free Trial Info
  Real Jasper User Score

Descriptions:
  30-day honest review of Jasper AI. Score 8.9/10. See if it's worth the price.
  We compared Jasper vs 8 alternatives. Full feature breakdown and pricing inside.
  Independent review — not sponsored. Brand voice, templates, and SEO mode tested.
  Is Jasper right for your business? Our 30-day test reveals the real pros and cons.

Final URL: https://rankertoolai.com/lp/jasper/?utm_source=google&utm_medium=cpc
```

---

## BƯỚC 8 — Khởi động tuần 1

```
CHIẾN LƯỢC TUẦN 1 — Validation, không phải scale:

  Chỉ chạy Campaign 1 (Reviews) với 3 tools:
  - ElevenLabs (22% commission, search volume trung bình)
  - Jasper (30% commission, intent cao)
  - Surfer SEO (25% commission, niche rõ)

  Budget: $10/ngày × 3 tools = $30/ngày tối đa
  Keyword match: Phrase match và Exact match (không dùng Broad)
  
  Theo dõi hàng ngày:
  python google_ads/monitoring/budget_tracker.py --status
```

---

## MONITORING HÀNG NGÀY

```bash
# Nhập số liệu từ Google Ads dashboard vào tracker:
python google_ads/monitoring/budget_tracker.py --log \
  --campaign "Reviews" \
  --spend 28.50 \
  --clicks 95 \
  --impressions 3200 \
  --conversions 4 \
  --conv-value 60.00

# Xem status + alerts
python google_ads/monitoring/budget_tracker.py --status

# Weekly report (chạy thứ 6)
python google_ads/monitoring/budget_tracker.py --report
```

---

## QUYẾT ĐỊNH CUỐI TUẦN 1

Sau 7 ngày, đánh giá từng tool:

| Tool | ROAS | Hành động |
|------|------|-----------|
| Jasper | > 2.5x | Scale: +20% budget, thêm keywords |
| ElevenLabs | 1.5-2.5x | Keep: optimize landing page |
| Surfer SEO | < 1x | Pause: review search intent |

**Scale roadmap:**
- Tuần 1: $10/ngày/tool (test)
- Tuần 2-3: Scale winners → $20-30/ngày
- Tháng 2: Mở Campaign 2 (Comparisons)
- Tháng 3: Mở Campaign 3 (Best AI Tools)

---

## OPTIMIZATION CHECKLIST (Tuần 2+)

### Search Terms Report (weekly)
```
Google Ads UI > Keywords > Search Terms
→ Exclude irrelevant terms (add to negatives)
→ Identify high-intent terms → add as Exact match
```

### Landing Page A/B Test
```
Test LP variant với:
  A: /lp/jasper/ (current)
  B: /review/jasper/ (organic page)
→ Whichever converts better → route paid traffic there
```

### Ad Copy Rotation
```
Sau 2 tuần: Pause ads có CTR < 3%
→ Viết ad mới thay thế
→ Mục tiêu: CTR > 5% cho review keywords
```

---

## BUDGET SCALING PLAN

```
Tháng 1: $300 (test & validate)
Tháng 2: $600 (scale winners 2x)
Tháng 3: $1,200 (full campaign, proven ROAS)

Target ROAS: 3x minimum để profitable
  $1,200 spend → $3,600 revenue → ~$900 net profit (sau khi trừ 25% commission costs)
```
