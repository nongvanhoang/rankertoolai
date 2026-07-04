#!/usr/bin/env python3
"""
Inject compare-widget placeholder + script tag into all review pages.
Replaces the existing plain "Compare" sidebar widget with the rich visual one.
"""
import re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REVIEW_DIR = Path(__file__).parent / "html" / "review"
SCRIPT_TAG = '<script src="/assets/js/compare-widget.js" defer></script>'

updated = 0
for review_page in sorted(REVIEW_DIR.iterdir()):
    html_file = review_page / "index.html"
    if not html_file.exists() or review_page.name == "index.html":
        continue

    slug = review_page.name
    content = html_file.read_text(encoding="utf-8")

    # 1. Replace the plain "Compare" sidebar widget with our widget placeholder
    widget_placeholder = (
        f'<div data-compare-widget data-tool="{slug}" '
        f'style="margin-top:0;"></div>'
    )

    # Replace existing Compare sidebar-widget block
    old_pattern = re.compile(
        r'<div class="sidebar-widget" style="margin-top:1\.5rem;">\s*'
        r'<h4 class="sidebar-widget-title">Compare [^<]*</h4>.*?</div>',
        re.DOTALL
    )
    new_content = old_pattern.sub(widget_placeholder, content, count=1)

    # 2. Add script tag before </body> if not already present
    if 'compare-widget.js' not in new_content:
        new_content = new_content.replace(
            '</body>',
            f'{SCRIPT_TAG}\n</body>',
            1
        )

    if new_content != content:
        html_file.write_text(new_content, encoding="utf-8")
        updated += 1
        print(f"  updated  {slug}")
    else:
        print(f"  skip     {slug} (no change)")

print(f"\nDone: {updated} review pages updated")
