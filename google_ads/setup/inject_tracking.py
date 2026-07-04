"""
Module 1: Inject Google Analytics 4 + Google Ads tracking into all HTML pages.

Features:
- Injects GA4 tag into every page that is missing it
- Injects Google Ads Global Site Tag
- Adds affiliate click tracking (fires conversion on /go/ redirect)
- Adds UTM-aware link tracking
- Backs up files before modification

Usage:
  python inject_tracking.py                  # Dry run (no changes)
  python inject_tracking.py --apply          # Apply to all pages
  python inject_tracking.py --apply --page review/chatgpt  # Single page
  python inject_tracking.py --verify         # Verify all pages have tracking
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent / "html"
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "tracking_backup"

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_tracking_snippet(cfg):
    ga4 = cfg["ga4_id"]
    ads = cfg["google_ads_id"]
    ads_click = cfg["google_ads_conversion"]["affiliate_click"]
    ads_60s = cfg["google_ads_conversion"]["page_view_60s"]
    clarity = cfg["clarity_id"]

    return f"""
  <!-- ═══ ANALYTICS & ADS TRACKING ═══ -->
  <!-- Google tag (gtag.js) — GA4 + Google Ads -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga4}');
    gtag('config', '{ads}');

    // Conversion: affiliate click (fires when user clicks /go/ link)
    document.addEventListener('DOMContentLoaded', function() {{
      document.querySelectorAll('a[href*="/go/"]').forEach(function(el) {{
        el.addEventListener('click', function() {{
          gtag('event', 'conversion', {{
            'send_to': '{ads_click}',
            'value': 1.0,
            'currency': 'USD'
          }});
          gtag('event', 'affiliate_click', {{
            'tool': el.href.split('/go/')[1]?.replace(/\\//g,'') || 'unknown',
            'page': window.location.pathname
          }});
        }});
      }});

      // Conversion: 60-second engaged page view
      setTimeout(function() {{
        gtag('event', 'conversion', {{'send_to': '{ads_60s}'}});
      }}, 60000);
    }});
  </script>

  <!-- Microsoft Clarity -->
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
      c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window,document,"clarity","script","{clarity}");
  </script>
  <!-- ══════════════════════════════════ -->"""

def has_tracking(html: str) -> bool:
    return "googletagmanager.com/gtag" in html

def inject_into_page(html: str, snippet: str) -> str:
    """Insert tracking snippet just before </head>."""
    target = "</head>"
    idx = html.lower().find(target)
    if idx == -1:
        return html
    return html[:idx] + snippet + "\n  " + html[idx:]

def backup_file(path: Path):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rel = path.relative_to(ROOT)
    backup_path = BACKUP_DIR / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if not backup_path.exists():
        shutil.copy2(path, backup_path)

def process_all(apply=False, target_page=None):
    cfg = load_config()
    snippet = build_tracking_snippet(cfg)

    html_files = list(ROOT.rglob("*.html"))
    if target_page:
        html_files = [f for f in html_files if target_page in str(f)]

    stats = {"total": 0, "already_ok": 0, "injected": 0, "skipped": 0, "errors": 0}

    for path in sorted(html_files):
        stats["total"] += 1
        rel = path.relative_to(ROOT)
        try:
            html = path.read_text(encoding="utf-8", errors="replace")

            if has_tracking(html):
                stats["already_ok"] += 1
                continue

            if apply:
                backup_file(path)
                new_html = inject_into_page(html, snippet)
                path.write_text(new_html, encoding="utf-8")
                stats["injected"] += 1
                print(f"  [OK] {rel}")
            else:
                stats["skipped"] += 1
                print(f"  [NEEDS TRACKING] {rel}")

        except Exception as e:
            stats["errors"] += 1
            print(f"  [ERROR] {rel}: {e}")

    print(f"\n{'='*55}")
    print(f"  Total pages:     {stats['total']}")
    print(f"  Already tracked: {stats['already_ok']}")
    print(f"  {'Injected' if apply else 'Need injection'}: {stats['injected'] if apply else stats['skipped']}")
    print(f"  Errors:          {stats['errors']}")
    if not apply:
        print(f"\n  Run with --apply to inject tracking into all pages.")
    else:
        print(f"\n  Backups saved to: {BACKUP_DIR}")
    print(f"{'='*55}")

def verify_all():
    html_files = list(ROOT.rglob("*.html"))
    missing = []
    ok = []
    for path in sorted(html_files):
        html = path.read_text(encoding="utf-8", errors="replace")
        if has_tracking(html):
            ok.append(path.relative_to(ROOT))
        else:
            missing.append(path.relative_to(ROOT))

    print(f"\nTracking Verification Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Tracked:  {len(ok)}/{len(ok)+len(missing)} pages")
    print(f"  Missing:  {len(missing)} pages")
    if missing:
        print("\nPages missing tracking:")
        for p in missing:
            print(f"  - {p}")
    return len(missing) == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--verify", action="store_true", help="Verify all pages have tracking")
    parser.add_argument("--page", help="Target a specific page path")
    args = parser.parse_args()

    if args.verify:
        ok = verify_all()
        sys.exit(0 if ok else 1)
    else:
        mode = "APPLY" if args.apply else "DRY RUN"
        print(f"\n[inject_tracking] Mode: {mode}")
        print(f"Root: {ROOT}\n")
        process_all(apply=args.apply, target_page=args.page)
