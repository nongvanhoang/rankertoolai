#!/usr/bin/env python3
"""
Google Search Console ranking tracker for rankertoolai.com.

Setup (one-time):
  1. Go to https://search.google.com/search-console/
  2. Add & verify rankertoolai.com as a property
  3. Go to https://console.cloud.google.com/
  4. Create project → Enable "Google Search Console API"
  5. Create OAuth2 credentials (Desktop app) → download client_secret.json
  6. Place client_secret.json in this directory
  7. Run: python gsc_tracker.py --auth
  8. After auth, run normally: python gsc_tracker.py

Usage:
  python gsc_tracker.py                  # weekly report (last 7 days)
  python gsc_tracker.py --days 28        # last 28 days
  python gsc_tracker.py --url /review/jasper/   # specific page
  python gsc_tracker.py --top 20         # top 20 pages by clicks
  python gsc_tracker.py --csv gsc.csv    # export to CSV
  python gsc_tracker.py --not-indexed    # show pages not indexed (0 impressions)
"""
import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")

SITE_URL      = "https://rankertoolai.com"
TOKEN_FILE    = Path(__file__).parent / "gsc_token.json"
SECRET_FILE   = Path(__file__).parent / "client_secret.json"
HTML_DIR      = Path(__file__).parent / "html"
SECTIONS      = ["review", "compare", "alternatives", "best", "category"]


def get_credentials():
    """Load or refresh OAuth2 credentials."""
    from google_oauth import get_credentials as _get_credentials
    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
    return _get_credentials(TOKEN_FILE, SECRET_FILE, SCOPES)


def build_service():
    from googleapiclient.discovery import build
    creds = get_credentials()
    return build("searchconsole", "v1", credentials=creds)


def fetch_performance(service, start_date: str, end_date: str,
                      dimensions: list, row_limit: int = 500,
                      url_filter: str = None) -> list:
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "startRow": 0,
    }
    if url_filter:
        body["dimensionFilterGroups"] = [{
            "filters": [{
                "dimension": "page",
                "operator": "equals",
                "expression": SITE_URL + url_filter,
            }]
        }]

    resp = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return resp.get("rows", [])


def discover_pages() -> list[str]:
    pages = ["/"]
    for section in SECTIONS:
        pages.append(f"/{section}/")
        section_dir = HTML_DIR / section
        if section_dir.exists():
            for entry in sorted(section_dir.iterdir()):
                if entry.is_dir() and (entry / "index.html").exists():
                    pages.append(f"/{section}/{entry.name}/")
    return pages


def date_range(days: int):
    end   = datetime.now(tz=timezone.utc).date() - timedelta(days=2)  # GSC data lag ~2 days
    start = end - timedelta(days=days - 1)
    return str(start), str(end)


def print_report(rows: list, title: str, top: int = 25):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"  {'URL':<45} {'Clicks':>7} {'Impr':>7} {'CTR':>6} {'Pos':>6}")
    print(f"  {'-'*45} {'-'*7} {'-'*7} {'-'*6} {'-'*6}")

    sorted_rows = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)
    for row in sorted_rows[:top]:
        url    = row["keys"][0].replace(SITE_URL, "") if row.get("keys") else ""
        clicks = int(row.get("clicks", 0))
        impr   = int(row.get("impressions", 0))
        ctr    = f"{row.get('ctr', 0)*100:.1f}%"
        pos    = f"{row.get('position', 0):.1f}"
        print(f"  {url:<45} {clicks:>7} {impr:>7} {ctr:>6} {pos:>6}")


def check_not_indexed(service, all_pages: list, start: str, end: str) -> list:
    """Pages with 0 impressions in the date range — may not be indexed yet."""
    rows = fetch_performance(service, start, end, ["page"], row_limit=1000)
    indexed_urls = {r["keys"][0] for r in rows}
    not_indexed = []
    for page in all_pages:
        full = SITE_URL + page
        if full not in indexed_urls:
            html_path = HTML_DIR / page.strip("/").replace("/", os.sep) / "index.html"
            if html_path.exists():
                age_days = (datetime.now(tz=timezone.utc).date() -
                            datetime.fromtimestamp(html_path.stat().st_mtime, tz=timezone.utc).date()).days
                not_indexed.append({"url": page, "age_days": age_days})
    return not_indexed


def main():
    parser = argparse.ArgumentParser(description="GSC ranking tracker for rankertoolai.com")
    parser.add_argument("--auth",       action="store_true", help="Force re-authentication")
    parser.add_argument("--days",       type=int, default=7, help="Date range in days (default: 7)")
    parser.add_argument("--url",        help="Filter to specific URL path, e.g. /review/jasper/")
    parser.add_argument("--top",        type=int, default=25, help="Show top N pages (default: 25)")
    parser.add_argument("--csv",        metavar="FILE", help="Export all data to CSV")
    parser.add_argument("--not-indexed", action="store_true", dest="not_indexed",
                        help="Show pages with 0 impressions (potentially not indexed)")
    parser.add_argument("--keywords",   action="store_true", help="Show top keywords instead of pages")
    args = parser.parse_args()

    if args.auth and TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print("Cleared cached token. Re-authenticating...")

    print("Connecting to Google Search Console...")
    service = build_service()

    start, end = date_range(args.days)
    print(f"Date range: {start} → {end} ({args.days} days)")

    if args.keywords:
        rows = fetch_performance(service, start, end, ["query"],
                                 row_limit=200, url_filter=args.url)
        title = f"Top Keywords — {args.days}d"
        if args.url:
            title += f" [{args.url}]"
        rows_display = [{"keys": [r["keys"][0]], **{k: r[k] for k in ["clicks","impressions","ctr","position"]}} for r in rows]
        print_report(rows_display, title, args.top)

    elif args.url:
        rows = fetch_performance(service, start, end, ["query"], row_limit=50, url_filter=args.url)
        print(f"\n{'='*70}")
        print(f"  Page: {args.url} — Top keywords ({args.days}d)")
        print(f"{'='*70}")
        print(f"  {'Keyword':<45} {'Clicks':>7} {'Impr':>7} {'CTR':>6} {'Pos':>6}")
        print(f"  {'-'*45} {'-'*7} {'-'*7} {'-'*6} {'-'*6}")
        for row in sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)[:args.top]:
            kw    = row["keys"][0]
            clicks = int(row.get("clicks", 0))
            impr   = int(row.get("impressions", 0))
            ctr    = f"{row.get('ctr', 0)*100:.1f}%"
            pos    = f"{row.get('position', 0):.1f}"
            print(f"  {kw:<45} {clicks:>7} {impr:>7} {ctr:>6} {pos:>6}")

    else:
        rows = fetch_performance(service, start, end, ["page"], row_limit=500)
        print_report(rows, f"Top Pages by Clicks — last {args.days} days", args.top)

        # Summary stats
        total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
        total_impr   = sum(int(r.get("impressions", 0)) for r in rows)
        avg_ctr      = (total_clicks / total_impr * 100) if total_impr else 0
        avg_pos      = sum(r.get("position", 0) for r in rows) / len(rows) if rows else 0

        print(f"\n  Total clicks: {total_clicks:,}")
        print(f"  Total impressions: {total_impr:,}")
        print(f"  Avg CTR: {avg_ctr:.2f}%")
        print(f"  Avg position: {avg_pos:.1f}")
        print(f"  Indexed pages with traffic: {len(rows)}")

    # Not-indexed check
    if args.not_indexed:
        all_pages = discover_pages()
        ni = check_not_indexed(service, all_pages, start, end)
        print(f"\n{'='*70}")
        print(f"  Pages with 0 impressions ({len(ni)} pages)")
        print(f"{'='*70}")
        for item in sorted(ni, key=lambda x: x["age_days"], reverse=True):
            flag = " ← ALERT: >14 days old!" if item["age_days"] > 14 else ""
            print(f"  {item['url']:<50} {item['age_days']}d old{flag}")

    # CSV export
    if args.csv:
        csv_path = Path(args.csv)
        all_rows = fetch_performance(service, start, end, ["page"], row_limit=1000)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "clicks", "impressions", "ctr", "position"])
            for row in sorted(all_rows, key=lambda r: r.get("clicks", 0), reverse=True):
                url = row["keys"][0].replace(SITE_URL, "")
                writer.writerow([
                    url,
                    int(row.get("clicks", 0)),
                    int(row.get("impressions", 0)),
                    f"{row.get('ctr', 0)*100:.2f}%",
                    f"{row.get('position', 0):.1f}",
                ])
        print(f"\nCSV exported: {csv_path}")

    print(f"\nDone. Run with --help to see all options.")


if __name__ == "__main__":
    main()
