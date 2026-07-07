#!/usr/bin/env python3
"""
Run automatically after every wrangler deploy.
Usage:
  python after_deploy.py                        # verify all pages
  python after_deploy.py /review/jasper/        # verify + ping specific new URL
  python after_deploy.py --social jasper        # also trigger social post for tool slug

Steps:
  1. Verify deployed pages return HTTP 200
  2. Ping IndexNow (Bing + Google) for new/updated URLs
  3. Optionally trigger social agent for a specific tool
"""
import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://rankertoolai.com"
INDEXNOW_KEY = "rankertoolai2026"          # must match html/rankertoolai2026.txt
INDEXNOW_HOST = "rankertoolai.com"
HTML_DIR = Path(__file__).parent / "html"

SECTIONS = ["review", "compare", "alternatives", "best", "category"]

STATIC_URLS = [
    "/",
    "/review/", "/compare/", "/alternatives/", "/best/", "/category/",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def http_status(url: str, timeout: int = 10) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ── Step 1: Verify pages ──────────────────────────────────────────────────────

def discover_urls() -> list[str]:
    urls = list(STATIC_URLS)
    for section in SECTIONS:
        section_dir = HTML_DIR / section
        if not section_dir.exists():
            continue
        for entry in sorted(section_dir.iterdir()):
            if entry.is_dir() and (entry / "index.html").exists():
                urls.append(f"/{section}/{entry.name}/")
    return urls


def verify_pages(specific_url: str | None = None) -> bool:
    urls_to_check = [specific_url] if specific_url else discover_urls()
    failed = []
    log(f"Verifying {len(urls_to_check)} URL(s)...")

    for path in urls_to_check:
        full_url = BASE_URL + path
        status = http_status(full_url)
        symbol = "OK" if status == 200 else "FAIL"
        if status != 200:
            failed.append((path, status))
            log(f"  {symbol}  {status}  {path}")
        else:
            log(f"  {symbol}  {status}  {path}")

    if failed:
        log(f"\nFAILED ({len(failed)}):")
        for p, s in failed:
            log(f"  {s}  {BASE_URL}{p}")
        return False

    log(f"All {len(urls_to_check)} pages verified OK.")
    return True


# ── Step 2: IndexNow ping ─────────────────────────────────────────────────────

def ping_indexnow(urls: list[str]):
    """
    Ping Bing IndexNow with new/updated URLs.
    Bing relays to Google automatically.
    API docs: https://www.indexnow.org/documentation
    """
    endpoint = "https://api.indexnow.org/indexnow"
    payload = {
        "host": INDEXNOW_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt",
        "urlList": [BASE_URL + u for u in urls],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            log(f"IndexNow ping: HTTP {r.status} — {len(urls)} URL(s) submitted")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:200]
        log(f"IndexNow ping failed: HTTP {e.code} — {body}")
        return False
    except Exception as ex:
        log(f"IndexNow ping error: {ex}")
        return False


# ── Step 3: Social trigger ────────────────────────────────────────────────────

def trigger_social(tool_slug: str):
    log(f"Triggering social post for tool: {tool_slug}")
    social_dir = Path(__file__).parent / "social_agent"
    main_py = social_dir / "main.py"
    if not main_py.exists():
        log("social_agent/main.py not found — skipping social trigger")
        return

    python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        python = Path(sys.executable)

    import subprocess
    result = subprocess.run(
        [str(python), str(main_py), "--tool", tool_slug],
        cwd=str(social_dir),
        capture_output=False,
    )
    if result.returncode == 0:
        log(f"Social post triggered successfully for {tool_slug}")
    else:
        log(f"Social post returned exit code {result.returncode}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post-deploy verification + IndexNow ping")
    parser.add_argument("url", nargs="?", help="Specific URL path to verify, e.g. /review/jasper/")
    parser.add_argument("--social", metavar="SLUG", help="Also trigger social post for this tool slug")
    parser.add_argument("--ping-all", action="store_true", help="Ping IndexNow for all discovered pages")
    args = parser.parse_args()

    log("=== After-Deploy Script ===")

    # Step 1: Verify
    ok = verify_pages(args.url)

    # Step 2: IndexNow ping
    if args.url:
        urls_to_ping = [args.url]
    elif args.ping_all:
        urls_to_ping = discover_urls()
    else:
        urls_to_ping = [args.url] if args.url else STATIC_URLS[:1]

    time.sleep(2)
    ping_indexnow(urls_to_ping)

    # Step 3: Social trigger
    if args.social:
        time.sleep(3)
        trigger_social(args.social)

    log("=== Done ===")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
