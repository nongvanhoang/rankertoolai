#!/usr/bin/env python3
"""
Auto-generate sitemap.xml from html/ directory structure.
Run before every deploy:
  python generate_sitemap.py

Scans review/, compare/, alternatives/, best/, category/ for index.html files.
Uses file mtime as lastmod. Assigns priority by section type.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://rankertoolai.com"
HTML_DIR = Path(__file__).parent / "html"
SITEMAP_PATH = HTML_DIR / "sitemap.xml"

# Priority and changefreq by section
SECTION_CONFIG = {
    "review":       {"priority": "0.85", "changefreq": "monthly"},
    "compare":      {"priority": "0.82", "changefreq": "monthly"},
    "alternatives": {"priority": "0.80", "changefreq": "monthly"},
    "best":         {"priority": "0.78", "changefreq": "monthly"},
    "category":     {"priority": "0.75", "changefreq": "monthly"},
    "blog":         {"priority": "0.72", "changefreq": "monthly"},
    "coupons":      {"priority": "0.88", "changefreq": "weekly"},
    "tools":        {"priority": "0.82", "changefreq": "monthly"},
    "pricing":      {"priority": "0.86", "changefreq": "weekly"},
}

# Static entries always written first (not auto-discovered)
STATIC_ENTRIES = [
    {"loc": "/",                    "priority": "1.0",  "changefreq": "daily"},
    {"loc": "/review/",             "priority": "0.90", "changefreq": "weekly"},
    {"loc": "/compare/",            "priority": "0.90", "changefreq": "weekly"},
    {"loc": "/alternatives/",       "priority": "0.90", "changefreq": "weekly"},
    {"loc": "/best/",               "priority": "0.85", "changefreq": "weekly"},
    {"loc": "/category/",           "priority": "0.80", "changefreq": "weekly"},
    {"loc": "/deals/",              "priority": "0.80", "changefreq": "weekly"},
    {"loc": "/blog/",               "priority": "0.75", "changefreq": "weekly"},
    {"loc": "/pricing/",            "priority": "0.86", "changefreq": "weekly"},
    {"loc": "/coupons/",            "priority": "0.88", "changefreq": "weekly"},
    {"loc": "/about/",              "priority": "0.60", "changefreq": "monthly"},
    {"loc": "/methodology/",        "priority": "0.55", "changefreq": "monthly"},
    # /contact/, /affiliate-disclosure/, /privacy-policy/, /terms/, /cookie-policy/
    # are all noindex -- deliberately excluded from the sitemap to avoid sending
    # mixed signals to search engines.
]

# Sections that are /go/ redirects — exclude from sitemap
EXCLUDED_DIRS = {"go", "links", "assets", ".wrangler", "pages", "lp", "author"}


def file_lastmod(path: Path) -> str:
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")


def today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def discover_pages():
    pages = []
    for section, cfg in SECTION_CONFIG.items():
        section_dir = HTML_DIR / section
        if not section_dir.exists():
            continue
        for entry in sorted(section_dir.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name in EXCLUDED_DIRS:
                continue
            index = entry / "index.html"
            if not index.exists():
                continue
            slug = entry.name
            pages.append({
                "loc": f"/{section}/{slug}/",
                "lastmod": file_lastmod(index),
                "priority": cfg["priority"],
                "changefreq": cfg["changefreq"],
            })
    return pages


def build_sitemap(pages):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append("")
    lines.append("  <!-- Static Pages -->")

    for e in STATIC_ENTRIES:
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE_URL}{e['loc']}</loc>")
        lines.append(f"    <lastmod>{today()}</lastmod>")
        lines.append(f"    <changefreq>{e['changefreq']}</changefreq>")
        lines.append(f"    <priority>{e['priority']}</priority>")
        lines.append("  </url>")

    current_section = None
    for p in pages:
        section = p["loc"].split("/")[1]
        if section != current_section:
            current_section = section
            lines.append("")
            lines.append(f"  <!-- {section.title()} Pages -->")
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE_URL}{p['loc']}</loc>")
        lines.append(f"    <lastmod>{p['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        lines.append(f"    <priority>{p['priority']}</priority>")
        lines.append("  </url>")

    lines.append("")
    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    pages = discover_pages()
    xml = build_sitemap(pages)
    SITEMAP_PATH.write_text(xml, encoding="utf-8")

    total = len(STATIC_ENTRIES) + len(pages)
    print(f"Sitemap generated: {SITEMAP_PATH}")
    print(f"  Static entries : {len(STATIC_ENTRIES)}")
    print(f"  Dynamic pages  : {len(pages)}")
    print(f"  Total URLs     : {total}")

    by_section = {}
    for p in pages:
        sec = p["loc"].split("/")[1]
        by_section[sec] = by_section.get(sec, 0) + 1
    for sec, count in sorted(by_section.items()):
        print(f"    {sec:<16} {count}")


if __name__ == "__main__":
    main()
