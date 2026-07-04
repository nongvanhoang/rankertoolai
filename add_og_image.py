#!/usr/bin/env python3
"""
Them og:image tag vao tat ca HTML pages con thieu.
- Review pages: dung anh rieng og-review-{slug}.jpg
- Tat ca trang khac: dung og-default.jpg

Usage: python add_og_image.py
"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HTML_DIR    = Path(__file__).parent / "html"
SITE        = "https://rankertoolai.com"
DEFAULT_OG  = f"{SITE}/assets/images/og-default.jpg"

SCAN_DIRS = ["review", "blog", "compare", "category", "best", "alternatives"]

fixed   = 0
skipped = 0


def insert_og_image(html_file, image_url):
    global fixed, skipped
    content = html_file.read_text(encoding="utf-8")

    if 'property="og:image"' in content or "property='og:image'" in content:
        skipped += 1
        return

    tag = f'  <meta property="og:image" content="{image_url}">\n'

    insert_after = None
    for pattern in [
        r'(<meta property="og:site_name"[^>]*>)',
        r'(<meta property="og:url"[^>]*>)',
        r'(<meta property="og:description"[^>]*>)',
        r'(<meta property="og:title"[^>]*>)',
    ]:
        m = re.search(pattern, content)
        if m:
            insert_after = m.end()
            break

    if insert_after is None:
        print(f"  SKIP (no og: anchor): {html_file.relative_to(HTML_DIR)}")
        return

    new_content = content[:insert_after] + "\n" + tag + content[insert_after:]
    html_file.write_text(new_content, encoding="utf-8")
    print(f"  OK  {html_file.relative_to(HTML_DIR)}")
    fixed += 1


# ── Review pages: dùng ảnh riêng từng tool ───────────────────────────────────
review_dir = HTML_DIR / "review"
if review_dir.exists():
    for html_file in review_dir.rglob("index.html"):
        slug = html_file.parent.name          # vd: "chatgpt", "cursor"
        tool_img = f"{SITE}/assets/images/og-review-{slug}.jpg"
        # Kiểm tra file ảnh tồn tại
        img_path = HTML_DIR / "assets" / "images" / f"og-review-{slug}.jpg"
        image_url = tool_img if img_path.exists() else DEFAULT_OG
        insert_og_image(html_file, image_url)

# ── Các section khác: dùng ảnh default ───────────────────────────────────────
for section in ["blog", "compare", "category", "best", "alternatives"]:
    section_dir = HTML_DIR / section
    if not section_dir.exists():
        continue
    for html_file in section_dir.rglob("index.html"):
        insert_og_image(html_file, DEFAULT_OG)

# ── Homepage ──────────────────────────────────────────────────────────────────
index_file = HTML_DIR / "index.html"
if index_file.exists():
    insert_og_image(index_file, DEFAULT_OG)

# ── Section index pages ───────────────────────────────────────────────────────
for section_index in ["review/index.html", "blog/index.html", "compare/index.html"]:
    f = HTML_DIR / section_index
    if f.exists():
        insert_og_image(f, DEFAULT_OG)

print(f"\nXong! Da them og:image: {fixed} files | Da co roi: {skipped} files")
