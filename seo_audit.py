#!/usr/bin/env python3
"""
Automated SEO audit for all HTML pages in html/.
Checks every index.html against 9 criteria without loading a browser.

Usage:
  python seo_audit.py                     # audit all pages
  python seo_audit.py review/jasper       # audit one page
  python seo_audit.py --csv audit.csv     # export results to CSV
  python seo_audit.py --fail-only         # show only failing pages

Exit code 0 = all pass, 1 = at least one critical failure.
"""
import os
import re
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

HTML_DIR = Path(__file__).parent / "html"
BASE_URL = "https://rankertoolai.com"
SECTIONS = ["review", "compare", "alternatives", "best", "category"]

MIN_WORDS = {"review": 1500, "compare": 2000, "alternatives": 2500, "best": 2000, "category": 1000}
MIN_AFFILIATE = {"review": 3, "compare": 4, "alternatives": 8, "best": 2, "category": 0}
TITLE_MIN, TITLE_MAX = 45, 65
DESC_MIN, DESC_MAX = 130, 160


# ── Parsers ───────────────────────────────────────────────────────────────────

def extract_tag(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_attr(html: str, tag: str, attr: str) -> str:
    pattern = rf'<{tag}[^>]*\s{attr}=["\']([^"\']*)["\'][^>]*>'
    m = re.search(pattern, html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_meta(html: str, name: str) -> str:
    # match content="..." and content='...' separately so a quote char used to
    # open the attribute isn't confused with an apostrophe inside the text
    pattern = rf'<meta\s[^>]*name=["\']{re.escape(name)}["\'][^>]*content="([^"]*)"'
    m = re.search(pattern, html, re.IGNORECASE)
    if not m:
        pattern = rf"<meta\s[^>]*name=[\"']{re.escape(name)}[\"'][^>]*content='([^']*)'"
        m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # alternate attribute order
    pattern2 = rf'<meta\s[^>]*content="([^"]*)"[^>]*name=["\']{re.escape(name)}["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    if not m2:
        pattern2 = rf"<meta\s[^>]*content='([^']*)'[^>]*name=[\"']{re.escape(name)}[\"']"
        m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else ""


def extract_og(html: str, prop: str) -> str:
    pattern = rf'<meta\s[^>]*property=["\']og:{re.escape(prop)}["\'][^>]*content=["\']([^"\']*)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    pattern2 = rf'<meta\s[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:{re.escape(prop)}["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else ""


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return len(text.split())


def count_h1(html: str) -> int:
    return len(re.findall(r"<h1[\s>]", html, re.IGNORECASE))


def has_valid_json_ld(html: str):
    schemas = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL
    )
    if not schemas:
        return False, []
    types_found = []
    for raw in schemas:
        try:
            obj = json.loads(raw.strip())
            for item in obj.get("@graph", [obj]):
                t = item.get("@type", "")
                if isinstance(t, list):
                    types_found.extend(t)
                elif t:
                    types_found.append(t)
        except json.JSONDecodeError as e:
            return False, [f"JSON parse error: {e}"]
    return True, types_found


def count_affiliate_links(html: str) -> int:
    return len(re.findall(r'href=["\'][^"\']*\/go\/[^"\']+["\']', html, re.IGNORECASE))


def has_raw_affiliate_url(html: str) -> bool:
    patterns = [r"jasper\.ai/\?fpr", r"writesonic\.com\?ref", r"app\.surfer\.seo\?ref"]
    return any(re.search(p, html, re.IGNORECASE) for p in patterns)


def count_internal_links(html: str) -> int:
    return len(re.findall(r'href=["\']\/(?!go\/)[^"\']*["\']', html, re.IGNORECASE))


def images_without_alt(html: str) -> int:
    imgs = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    return sum(1 for img in imgs if not re.search(r'alt=["\'][^"\']+["\']', img, re.IGNORECASE))


def has_disclosure(html: str) -> bool:
    return bool(re.search(r"affiliate\s+(disclosure|link)", html, re.IGNORECASE))


def has_canonical(html: str) -> str:
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if not m:
        m = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def has_robots_meta(html: str) -> bool:
    return bool(re.search(r'<meta[^>]*name=["\']robots["\']', html, re.IGNORECASE))


# ── Audit one page ────────────────────────────────────────────────────────────

def audit_page(section: str, slug: str) -> dict:
    html_path = HTML_DIR / section / slug / "index.html"
    if not html_path.exists():
        return {"section": section, "slug": slug, "error": "file not found"}

    html = html_path.read_text(encoding="utf-8", errors="replace")
    issues = []
    warnings = []

    # Meta title
    title = extract_tag(html, "title")
    tlen = len(title)
    if not title:
        issues.append("MISSING meta title")
    elif tlen < TITLE_MIN:
        warnings.append(f"Title too short ({tlen} chars, min {TITLE_MIN})")
    elif tlen > TITLE_MAX:
        warnings.append(f"Title too long ({tlen} chars, max {TITLE_MAX})")

    # Meta description
    desc = extract_meta(html, "description")
    dlen = len(desc)
    if not desc:
        issues.append("MISSING meta description")
    elif dlen < DESC_MIN:
        warnings.append(f"Description too short ({dlen} chars, min {DESC_MIN})")
    elif dlen > DESC_MAX:
        warnings.append(f"Description too long ({dlen} chars, max {DESC_MAX})")

    # Canonical
    canonical = has_canonical(html)
    if not canonical:
        issues.append("MISSING canonical tag")
    else:
        expected = f"{BASE_URL}/{section}/{slug}/"
        if canonical != expected:
            warnings.append(f"Canonical mismatch: {canonical} (expected {expected})")

    # H1
    h1_count = count_h1(html)
    if h1_count == 0:
        issues.append("MISSING H1")
    elif h1_count > 1:
        warnings.append(f"Multiple H1 tags ({h1_count})")

    # Word count
    wc = word_count(html)
    min_wc = MIN_WORDS.get(section, 1000)
    if wc < min_wc:
        issues.append(f"Too short: {wc} words (min {min_wc})")

    # Placeholder text — strip style/script blocks first to avoid false positives on CSS class names
    stripped = re.sub(r'<(style|script)[^>]*>.*?</(style|script)>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    body_text = re.sub(r'<[^>]+>', ' ', stripped)
    if re.search(r'\[INSERT[^\]]*\]|\bTODO\b|\bPLACEHOLDER\b|lorem ipsum', body_text, re.IGNORECASE):
        issues.append("Contains placeholder text")

    # Schema
    schema_ok, schema_types = has_valid_json_ld(html)
    if not schema_ok:
        issues.append(f"Invalid/missing JSON-LD schema: {schema_types}")
    else:
        if "FAQPage" not in schema_types:
            warnings.append("FAQPage schema missing")
        if section in ("review", "compare") and "Review" not in schema_types:
            warnings.append("Review schema missing")

    # Affiliate links
    aff_count = count_affiliate_links(html)
    min_aff = MIN_AFFILIATE.get(section, 0)
    if aff_count < min_aff:
        issues.append(f"Too few affiliate links: {aff_count} (min {min_aff})")
    if has_raw_affiliate_url(html):
        issues.append("Raw affiliate URL exposed (use /go/slug/ instead)")

    # Affiliate disclosure
    if section in ("review", "compare", "alternatives") and not has_disclosure(html):
        issues.append("MISSING affiliate disclosure")

    # Internal links
    int_links = count_internal_links(html)
    if int_links == 0:
        issues.append("ZERO internal links")
    elif int_links < 4:
        warnings.append(f"Low internal links: {int_links} (recommend 4+)")

    # OG tags
    og_title = extract_og(html, "title")
    og_desc  = extract_og(html, "description")
    og_image = extract_og(html, "image")
    if not og_title:
        warnings.append("Missing og:title")
    if not og_desc:
        warnings.append("Missing og:description")
    if not og_image:
        warnings.append("Missing og:image")

    # Images without alt
    no_alt = images_without_alt(html)
    if no_alt > 0:
        warnings.append(f"{no_alt} image(s) missing alt text")

    # Robots meta
    if not has_robots_meta(html):
        warnings.append("Missing <meta name='robots'>")

    verdict = "PASS" if not issues else "FAIL"
    return {
        "section": section,
        "slug": slug,
        "verdict": verdict,
        "title": title[:70] if title else "",
        "title_len": tlen,
        "desc_len": dlen,
        "word_count": wc,
        "h1_count": h1_count,
        "schema_types": ", ".join(schema_types),
        "affiliate_links": aff_count,
        "internal_links": int_links,
        "images_no_alt": no_alt,
        "issues": issues,
        "warnings": warnings,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SEO audit for RankerToolAI pages")
    parser.add_argument("target", nargs="?", help="section/slug to audit (e.g. review/jasper)")
    parser.add_argument("--csv", metavar="FILE", help="Export results to CSV")
    parser.add_argument("--fail-only", action="store_true", help="Show only failing pages")
    args = parser.parse_args()

    results = []

    if args.target:
        parts = args.target.strip("/").split("/")
        if len(parts) == 2:
            results.append(audit_page(parts[0], parts[1]))
        else:
            print(f"Invalid target: {args.target}. Use section/slug format.")
            sys.exit(1)
    else:
        for section in SECTIONS:
            section_dir = HTML_DIR / section
            if not section_dir.exists():
                continue
            for entry in sorted(section_dir.iterdir()):
                if entry.is_dir() and (entry / "index.html").exists():
                    results.append(audit_page(section, entry.name))

    # Print report
    total = len(results)
    failed = [r for r in results if r.get("verdict") == "FAIL"]
    passed = [r for r in results if r.get("verdict") == "PASS"]

    print(f"\n{'='*60}")
    print(f"SEO AUDIT — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"Total: {total}  |  PASS: {len(passed)}  |  FAIL: {len(failed)}")
    print(f"{'='*60}\n")

    display = failed if args.fail_only else results
    for r in display:
        if "error" in r:
            print(f"  ERROR  {r['section']}/{r['slug']}: {r['error']}")
            continue
        symbol = "FAIL" if r["verdict"] == "FAIL" else "PASS"
        print(f"  {symbol}  {r['section']}/{r['slug']}")
        if r["verdict"] == "FAIL":
            for issue in r["issues"]:
                print(f"         CRITICAL: {issue}")
        for w in r.get("warnings", []):
            print(f"         warning : {w}")

    print(f"\n{'='*60}")
    print(f"Summary: {len(failed)}/{total} pages need attention")

    if args.csv:
        csv_path = Path(args.csv)
        fieldnames = [
            "section", "slug", "verdict", "title_len", "desc_len",
            "word_count", "h1_count", "affiliate_links", "internal_links",
            "images_no_alt", "schema_types", "issues", "warnings"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                if "error" in r:
                    continue
                row = {k: r.get(k, "") for k in fieldnames}
                row["issues"]   = " | ".join(r.get("issues", []))
                row["warnings"] = " | ".join(r.get("warnings", []))
                writer.writerow(row)
        print(f"CSV exported: {csv_path}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
