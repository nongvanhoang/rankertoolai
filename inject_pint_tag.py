#!/usr/bin/env python3
"""Inject Pinterest pixel script tag into all HTML pages in html/."""
import re
from pathlib import Path

HTML_DIR = Path("html")
TAG_LINE  = '  <script async src="/assets/js/pint.js"></script>\n'
MARKER    = 'pint.js'

def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER in text:
        return False  # already injected
    if "</head>" not in text:
        return False  # no head tag
    new_text = text.replace("</head>", TAG_LINE + "</head>", 1)
    path.write_text(new_text, encoding="utf-8")
    return True

done = skipped = 0
for html in sorted(HTML_DIR.rglob("*.html")):
    if inject(html):
        done += 1
    else:
        skipped += 1

print(f"Injected: {done} files | Already done / skipped: {skipped}")
