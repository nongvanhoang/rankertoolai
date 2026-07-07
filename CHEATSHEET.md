# RankerToolAI — Cheatsheet

## CÁCH SỬ DỤNG PIPELINE (3 BƯỚC)

```
Bước 1: Mở claude.ai (hoặc bất kỳ AI nào)
Bước 2: Mở file PIPELINE.md → Copy toàn bộ → Paste vào chat → Enter
Bước 3: Gõ lệnh bên dưới
```

---

## CÁC LỆNH

| Lệnh | Dùng khi nào | Ví dụ |
|------|-------------|-------|
| `/review [tool]` | Muốn tạo trang review | `/review jasper` |
| `/compare [A] [B]` | Muốn so sánh 2 công cụ | `/compare jasper writesonic` |
| `/alternatives [tool]` | Muốn trang alternatives | `/alternatives chatgpt` |
| `/best [use case]` | Muốn trang best-for | `/best ai writing tools` |
| `/audit [url]` | Muốn kiểm tra trang có sẵn | `/audit /review/jasper/` |
| `/affiliate [tool]` | Tra cứu affiliate info | `/affiliate surfer seo` |
| `/plan 10` | Lập kế hoạch N trang tiếp theo | `/plan 10` |
| `/status` | Xem tổng quan, nên làm gì tiếp | `/status` |

---

## THỨ TỰ ƯU TIÊN (làm cái nào trước)

```
🔴 P1 — Làm ngay (doanh thu cao nhất)
   /compare jasper writesonic       ← intent cao nhất
   /compare jasper copy-ai
   /alternatives jasper             ← switching intent
   /alternatives chatgpt            ← volume khổng lồ
   /review surfer-seo               ← 25% recurring

🟡 P2 — Tuần 2
   /best ai writing tools           ← pillar page
   /best ai seo tools
   /review notion                   ← volume cao
   /review midjourney               ← brand authority

🟢 P3 — Tháng 2
   /best ai tools for students
   /best free ai tools
   /category ai-writing
```

---

## PIPELINE TỰ ĐỘNG CHẠY 7 BƯỚC

Khi bạn gõ `/review jasper`, AI sẽ tự làm:

```
[1] Keyword Brief    → phân tích "jasper review"
[2] Content Brief    → outline + meta + FAQ questions
[3] HTML Output      → file hoàn chỉnh, production-ready
[4] SEO Check        → meta, schema, canonical
[5] Internal Links   → gợi ý link đi và link đến
[6] QA Verdict       → PASS ✅ hoặc FAIL ❌ với lý do
[7] Deploy Guide     → hướng dẫn lưu file + lệnh deploy
```

---

## OUTPUT MỖI LẦN CHẠY

Bạn nhận được:

- **HTML file** → lưu vào `html/[type]/[slug]/index.html`
- **QA Report** → biết ngay có vấn đề gì không
- **Redirect** → `html/go/[slug]/index.html` đã có sẵn 34 redirects (có GA4 tracking)
- **Sitemap entry** → thêm vào `html/sitemap.xml`
- **Deploy command** → copy-paste 1 lệnh là xong

---

## DEPLOY (Script tích hợp — 1 lệnh làm tất)

```powershell
# Deploy thường (tự generate sitemap + git commit + wrangler + verify)
.\deploy.ps1

# Deploy trang mới + verify + post social
.\deploy.ps1 -Url "/review/jasper/" -Social "jasper"

# Rollback nếu có lỗi
.\deploy.ps1 -Rollback
```

---

## QUY TRÌNH ĐẦY ĐỦ MỖI TRANG MỚI

```
1. Gõ lệnh trong Claude     →  /review jasper
2. Copy HTML từ Claude       →  lưu vào html/review/jasper/index.html
3. Cập nhật internal links   →  python update_links.py review jasper "Jasper AI" 8.5 "AI Writing" "Mô tả ngắn"
4. SEO audit trước khi deploy→  python seo_audit.py review/jasper
5. Deploy 1 lệnh             →  .\deploy.ps1 -Url "/review/jasper/" -Social "jasper"
   (tự động: sitemap + git + wrangler + verify + IndexNow + social post)
6. Kiểm tra live             →  mở browser vào rankertoolai.com/review/jasper/
```

---

## AFFILIATE DATABASE (tóm tắt)

| Công cụ | Hoa hồng | Redirect |
|---------|----------|---------|
| Jasper | 30% lifetime | `/go/jasper/` ✅ |
| Writesonic | 30% recurring | `/go/writesonic/` ✅ |
| Surfer SEO | 25% recurring | `/go/surfer-seo/` ✅ |
| ElevenLabs | 22% / 12 tháng | `/go/elevenlabs/` ✅ |
| Copy.ai | 20% recurring | `/go/copy-ai/` ✅ |
| Semrush | 40% recurring | `/go/semrush/` ✅ |
| Notion | $10/referral | `/go/notion/` ✅ |
| Pictory | 20% recurring | `/go/pictory/` ✅ |
| Cursor | — | `/go/cursor/` ✅ |
| ChatGPT | ❌ không có | link trực tiếp |
| Midjourney | ❌ không có | link trực tiếp |
| Claude | ❌ không có | link trực tiếp |
| Gemini | ❌ không có | link trực tiếp |

*Tất cả redirects đã có trong `html/_redirects`*

---

## QUY TẮC KHÔNG ĐƯỢC VI PHẠM

```
❌ Không dùng URL affiliate trực tiếp → luôn dùng /go/[slug]/
❌ Không deploy trang thiếu affiliate link
❌ Không để placeholder text trong HTML
✅ Luôn có affiliate disclosure đầu trang
✅ Luôn dùng rel="nofollow sponsored" trên CTA links
✅ Luôn verify trên browser sau khi deploy
```

---

## VÍ DỤ PHIÊN LÀM VIỆC

```
Bạn mở Claude → paste PIPELINE.md → Enter

Claude: "✅ RankerToolAI Pipeline sẵn sàng. Lệnh nào?"

Bạn: /review jasper

Claude: [Xuất HTML + QA report + hướng dẫn deploy]

Bạn:
  → Lưu HTML vào html/review/jasper/index.html
  → Chạy: npx wrangler pages deploy ... --project-name=rankertoolai
  → Mở browser kiểm tra ✅

Bạn: /compare jasper writesonic
... lặp lại
```

---

## CÔNG CỤ MỚI (sau nâng cấp)

```
deploy.ps1            ← Deploy 1 lệnh (sitemap + git + wrangler + verify + social)
generate_sitemap.py   ← Auto tạo sitemap từ html/ (chạy tự động trong deploy.ps1)
after_deploy.py       ← Verify HTTP 200 + ping IndexNow (chạy tự động trong deploy.ps1)
update_links.py       ← Cập nhật internal links sau trang mới
seo_audit.py          ← Audit SEO tất cả trang (phát hiện issues trước khi deploy)
gsc_tracker.py        ← Xem ranking từ Google Search Console
social_agent/         ← Auto post 9 platform (rotation 6 loại content)
```

## FILE QUAN TRỌNG

```
PIPELINE.md           ← paste vào Claude để bắt đầu (DÙNG HÀNG NGÀY)
CHEATSHEET.md         ← file này, xem nhanh
html/_redirects       ← affiliate redirects (đã có sẵn 15 redirects)
html/sitemap.xml      ← TỰ ĐỘNG tạo bởi generate_sitemap.py (không edit tay)
agents/               ← 14 agent files (backup)
```

## SEO AUDIT (chạy định kỳ)

```powershell
# Audit tất cả trang + export CSV
python seo_audit.py --fail-only --csv audit_results.csv

# Audit 1 trang trước khi deploy
python seo_audit.py review/jasper

# Xem ranking từ GSC (sau khi setup credentials)
python gsc_tracker.py                    # top pages 7 ngày
python gsc_tracker.py --days 28 --top 30
python gsc_tracker.py --not-indexed      # trang chưa được index
python gsc_tracker.py --url /review/jasper/ --keywords  # keywords của 1 trang
```

---

## KẾT QUẢ KỲ VỌNG

```
Tuần 1:  10 trang live → first affiliate clicks
Tuần 2:  Google index → first organic traffic
Tháng 2: $100–$500/tháng (50+ trang)
Tháng 4: $1,000+/tháng (100+ trang, rankings ổn định)
```
