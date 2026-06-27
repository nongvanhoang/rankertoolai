#!/usr/bin/env python3
"""
Convert @graph JSON-LD schemas to separate <script> blocks.
This lets seo_audit.py detect FAQPage and Review types correctly.

Usage:
  python fix_schema_blocks.py          # fix all pages
  python fix_schema_blocks.py --dry    # preview only, no writes
"""
import sys, re, json, os, argparse
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

HTML_DIR = Path(__file__).parent / "html"
SECTIONS = ["review", "compare", "alternatives", "best", "category"]

SCRIPT_RE = re.compile(
    r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.IGNORECASE | re.DOTALL
)

def graph_to_blocks(html: str) -> tuple[str, bool]:
    """Return (new_html, changed). Converts @graph blocks to separate blocks."""
    changed = False

    def replace_block(m):
        nonlocal changed
        open_tag, raw, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            obj = json.loads(raw.strip())
        except json.JSONDecodeError:
            return m.group(0)

        if "@graph" not in obj:
            return m.group(0)

        graph_items = obj["@graph"]
        if not isinstance(graph_items, list) or not graph_items:
            return m.group(0)

        changed = True
        parts = []
        for item in graph_items:
            item_with_ctx = {"@context": "https://schema.org"}
            item_with_ctx.update(item)
            serialized = json.dumps(item_with_ctx, ensure_ascii=False, separators=(',', ':'))
            parts.append(f'<script type="application/ld+json">{serialized}</script>')
        return "\n  ".join(parts)

    new_html = SCRIPT_RE.sub(replace_block, html)
    return new_html, changed


def process_all(dry_run: bool = False):
    fixed = 0
    skipped = 0

    for section in SECTIONS:
        d = HTML_DIR / section
        if not d.exists():
            continue
        for slug in sorted(os.listdir(d)):
            p = d / slug / "index.html"
            if not p.exists():
                continue
            html = p.read_text(encoding="utf-8", errors="replace")
            new_html, changed = graph_to_blocks(html)
            if changed:
                if not dry_run:
                    p.write_text(new_html, encoding="utf-8")
                print(f"  {'[DRY]' if dry_run else 'FIXED'} {section}/{slug}")
                fixed += 1
            else:
                skipped += 1

    print(f"\nDone: {fixed} converted, {skipped} unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Preview only")
    args = parser.parse_args()
    process_all(dry_run=args.dry)
