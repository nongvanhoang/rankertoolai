# Google Ads System — RankerToolAI

## Tổng quan hệ thống

Hệ thống Google Ads cho rankertoolai.com gồm 4 modules:

```
google_ads/
├── setup/
│   ├── inject_tracking.py        # Inject GA4 + Ads tag vào tất cả pages
│   └── inject_utm_go.py          # UTM passthrough cho /go/ redirect
├── campaigns/
│   ├── generate_campaigns.py     # Tạo campaign CSV cho Google Ads Editor
│   └── generate_negative_keywords.py  # Danh sách negative keywords
├── landing_pages/
│   └── generate_lps.py           # Tạo /lp/[tool]/ landing pages
├── monitoring/
│   ├── dashboard.html            # Dashboard theo dõi realtime
│   └── budget_tracker.py         # Stop-loss + weekly report
└── data/
    ├── config.json               # Cấu hình IDs, budget, tools
    └── tracking_backup/          # Backup tất cả files trước khi sửa
```

---

## Bước 1 — Cấu hình IDs (BẮT BUỘC trước khi chạy)

Mở `data/config.json` và điền:

```json
{
  "ga4_id": "G-81KB8ECCVF",            // Đã có
  "google_ads_id": "AW-XXXXXXXXXX",    // << Lấy từ Google Ads > Tools > Tag
  "google_ads_conversion": {
    "affiliate_click": "AW-XXXXXXXXXX/YYYYYYYYYY",  // << Tạo trong Ads > Goals
    "page_view_60s": "AW-XXXXXXXXXX/ZZZZZZZZZZ"     // << Tạo trong Ads > Goals
  }
}
```

Cách lấy Google Ads ID:
- Đăng nhập ads.google.com
- Tools & Settings > Google tag
- Copy ID dạng AW-XXXXXXXXXX

Cách tạo Conversion Action:
- Goals > Conversions > New conversion action
- Tạo 2 actions: "Affiliate Click" + "Engaged Visit (60s)"
- Copy conversion tag IDs

Sau khi có IDs, chạy lại:
```
python setup/inject_tracking.py --apply
python setup/inject_utm_go.py --apply
```

---

## Bước 2 — Apply Tracking (đã chạy)

```bash
# Đã inject GA4 + Ads tag vào 143 pages
python setup/inject_tracking.py --apply

# Đã update 34 redirect pages với UTM passthrough
python setup/inject_utm_go.py --apply

# Verify
python setup/inject_tracking.py --verify
```

---

## Bước 3 — Landing Pages (đã tạo)

Landing pages tối ưu cho paid traffic tại `/lp/[tool]/`:

| URL | Tool | Headline |
|-----|------|---------|
| /lp/elevenlabs/ | ElevenLabs | Turn Text Into Studio-Quality Voice |
| /lp/jasper/ | Jasper AI | Write 10x More Marketing Content |
| /lp/surfer-seo/ | Surfer SEO | Rank Higher With AI Content Optimization |
| /lp/writesonic/ | Writesonic | Create SEO Content That Ranks 10x Faster |
| /lp/midjourney/ | Midjourney | Create Stunning AI Art in 60 Seconds |
| /lp/chatgpt/ | ChatGPT | World's Most Powerful AI Assistant |
| /lp/cursor/ | Cursor | Code 10x Faster With AI |

Tạo thêm:
```bash
python landing_pages/generate_lps.py --tool [slug]
```

---

## Bước 4 — Campaign Structure (đã tạo)

```bash
# Tạo tất cả campaigns (review + compare + best)
python campaigns/generate_campaigns.py

# Output: data/google_ads_campaign_all_YYYYMMDD.csv
# Import: Google Ads Editor > File > Import > From CSV
```

**3 Campaigns được tạo:**
1. `RankerToolAI - AI Tool Reviews` — 8 tools, 8 ad groups
2. `RankerToolAI - AI Tool Comparisons` — 10 pairs
3. `RankerToolAI - Best AI Tools` — 8 categories

```bash
# Negative keywords
python campaigns/generate_negative_keywords.py
# Upload: Tools > Shared Library > Negative Keyword Lists
```

---

## Bước 5 — Monitoring

### Dashboard (mở trong browser)
```
google_ads/monitoring/dashboard.html
```
- Nhập số liệu thủ công mỗi ngày
- Kiểm tra stop-loss rules tự động
- Hiển thị ROAS, CPA, spend vs budget

### Budget Tracker (command line)
```bash
# Xem trạng thái hôm nay
python monitoring/budget_tracker.py --status

# Log số liệu từ Google Ads
python monitoring/budget_tracker.py --log \
    --campaign "RankerToolAI - AI Tool Reviews" \
    --spend 15.50 --clicks 42 --impressions 1200 \
    --conversions 3 --conv-value 30.00

# Weekly report
python monitoring/budget_tracker.py --report
```

---

## Stop-Loss Rules

| Rule | Ngưỡng | Hành động |
|------|--------|-----------|
| Spend quá cao | > $50/ngày | PAUSE tất cả ngay |
| ROAS thấp | < 2.0x với spend > $10 | Giảm bid 30% |
| CPA cao | > $22.50 (1.5x target) | Review keywords/LPs |
| 0 conv cao | Spend > $20 + 0 conv | Pause + kiểm tra keywords |

---

## Decision Framework mỗi tuần

| ROAS | Hành động |
|------|-----------|
| > 3.0x | SCALE: tăng budget 20% |
| 2.0-3.0x | KEEP: giữ nguyên |
| 1.0-2.0x | REVIEW: optimize keywords, LP |
| < 1.0x | PAUSE: dừng campaign đó |

---

## Chiến lược khởi động (tuần 1-2)

1. Bắt đầu với **1 campaign**: Reviews
2. Chỉ chạy **3 tools đầu tiên**: ElevenLabs, Jasper, Surfer SEO
3. Budget: **$10/ngày** (không nhiều hơn)
4. Theo dõi mỗi ngày, không đợi tuần
5. Sau 7 ngày: scale tools có ROAS > 2x, pause tools < 1x

---

## Cấu trúc URL ads

```
Quảng cáo Google trỏ đến:   /lp/elevenlabs/?utm_source=google&utm_medium=cpc
User click CTA trên LP:      /go/elevenlabs/?utm_source=google&utm_medium=cpc
/go/ đọc UTM và pass qua:    https://elevenlabs.io/?from=rankertoolai&utm_source=google...
GA4 + Ads tag track event:   affiliate_click + conversion fired
```
