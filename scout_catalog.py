#!/usr/bin/env python3
"""
Regenerate scout_reports/CATALOG.md from scout_log.json.

Usage:
  python3 scout_catalog.py [--published-slugs path/to/list.txt]

Without --published-slugs, every tool is marked "chưa lên bài" since this
script only has access to whatever's checked out on this branch (scout-log),
which doesn't track main's review/alternatives directories. To mark tools as
published, pass a text file with one slug per line (e.g. dumped from
`ls review/ alternatives/` on main).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent
LOG_FILE = ROOT / "scout_log.json"
OUT_FILE = ROOT / "scout_reports" / "CATALOG.md"

# Ghi chú thủ công cho từng slug — không tự sinh được từ scout_log.json,
# nên giữ ở đây để mỗi lần chạy lại script không bị mất.
NOTES = {
    "twelvelabs": "đã gọi vốn $100M Series B — không có affiliate công khai",
}


def load_rows(published_slugs):
    data = json.loads(LOG_FILE.read_text())
    rows = []
    for slug, t in data.get("tools", {}).items():
        history = t.get("tier_history", [])
        if not history:
            continue
        latest = history[-1]
        rows.append({
            "slug": slug,
            "name": t.get("name", slug),
            "first_seen": t.get("first_seen"),
            "last_seen": t.get("last_seen"),
            "tier": latest.get("tier"),
            "composite": latest.get("composite"),
            "count": len(history),
            "published": slug in published_slugs,
        })
    return rows


def render_table(rows):
    lines = ["| Công cụ | Composite mới nhất | Phát hiện lần đầu | Thấy gần nhất | Số lần xuất hiện | Đã lên bài? |",
             "|---|---|---|---|---|---|"]
    footnotes = []
    for r in sorted(rows, key=lambda r: (-r["composite"], r["last_seen"])):
        published = "✅ Đã lên bài + affiliate active" if r["published"] else "⏳ Chưa"
        note = NOTES.get(r["slug"])
        name = f"{r['name']} [^{r['slug']}]" if note else r["name"]
        if note:
            footnotes.append(f"[^{r['slug']}]: {note}")
        lines.append(
            f"| **{name}** | {r['composite']} | {r['first_seen']} | {r['last_seen']} | {r['count']} | {published} |"
        )
    if footnotes:
        lines.append("")
        lines.extend(footnotes)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--published-slugs", type=Path, default=None)
    args = parser.parse_args()

    published_slugs = set()
    if args.published_slugs and args.published_slugs.exists():
        published_slugs = {l.strip() for l in args.published_slugs.read_text().splitlines() if l.strip()}

    rows = load_rows(published_slugs)
    hot = [r for r in rows if r["tier"] == "HOT"]
    watch = [r for r in rows if r["tier"] == "WATCH"]
    published_count = sum(1 for r in rows if r["published"])

    body = f"""# Danh mục tổng hợp — tất cả công cụ AI Scout đã phát hiện

File này khác với `scout_reports/{{ngày}}.md` (báo cáo chi tiết từng ngày) và `INDEX.md` (chỉ đếm số lượng theo ngày). Đây là **danh sách gộp theo từng công cụ**, mỗi công cụ 1 dòng.

Sinh tự động bởi `scout_catalog.py` từ `scout_log.json`. Đừng sửa tay — chạy lại script để cập nhật.

## 🔥 Tier HOT ({len(hot)})

{render_table(hot)}

## 👀 Tier WATCH ({len(watch)})

{render_table(watch)}

---

**Tổng:** {len(rows)} công cụ đã log · {len(hot)} HOT · {len(watch)} WATCH · {published_count} đã lên bài & có affiliate · {len(rows) - published_count} vẫn chưa khai thác.

**Gợi ý đọc bảng:** "Số lần xuất hiện" cao (vd. TwelveLabs, Mina Meeting Assistant) nghĩa là công cụ này lặp lại nhiều lần trong các đợt quét nhưng composite không đủ để lên HOT — thường do thiếu affiliate program công khai hoặc thị trường đã đông cạnh tranh. Xem report của ngày ở cột "Thấy gần nhất" trong `scout_reports/{{ngày}}.md` để đọc lý do chi tiết.

Danh sách này **không** bao gồm các công cụ đang chờ hoàn tất đăng ký affiliate (Semrush, Canva, Lovable, Gamma...) — những công cụ đó nằm sẵn trong `AFFILIATE_DB` trên `main` từ trước khi Scout bắt đầu track, không có trong `scout_log.json`. Xem mục "Still pending your signup" trong report ngày gần nhất để lấy link đăng ký.
"""
    OUT_FILE.write_text(body)
    print(f"Wrote {OUT_FILE} ({len(rows)} tools, {published_count} marked published)")


if __name__ == "__main__":
    main()
