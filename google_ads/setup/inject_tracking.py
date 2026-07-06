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
import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "tracking_backup"

# Directories to never walk into, whichever root is targeted — avoids
# corrupting backups, python venvs, tooling caches, etc.
EXCLUDE_DIR_NAMES = {
    "node_modules", ".venv", ".git", ".claude", "__pycache__",
    "google_ads", ".wrangler", "html",
}

def resolve_root(target: str) -> Path:
    """'html' = the legacy VPS/nginx mirror (DEPLOY.md); 'site' = the repo-root
    content folders (go/, review/, alternatives/, ...) that Cloudflare Pages
    actually serves. Confirm with the user which one is live before assuming."""
    return REPO_ROOT / "html" if target == "html" else REPO_ROOT

def iter_html_files(root: Path):
    for p in root.rglob("*.html"):
        rel_parts = p.relative_to(root).parts
        if any(part in EXCLUDE_DIR_NAMES for part in rel_parts):
            continue
        yield p

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
    # Informational only (dry-run stats) — NOT used to skip re-injection,
    # since older pages may already carry a stale snippet (e.g. placeholder
    # AW-XXXXXXXXXX ads id) that still needs to be refreshed with real IDs.
    return "ANALYTICS & ADS TRACKING" in html

OLD_BLOCK_RE = re.compile(
    r'\s*<!-- ═══ ANALYTICS & ADS TRACKING ═══ -->[\s\S]*?'
    r'<!-- ══════════════════════════════════ -->',
)

def strip_old_block(html: str) -> str:
    """Remove a previously-injected tracking block (any version, including
    ones built with stale/placeholder IDs) so it can be replaced cleanly."""
    return OLD_BLOCK_RE.sub("", html, count=1)

def strip_bare_ga4(html: str, ga4_id: str) -> str:
    """Remove the pre-existing bare GA4-only gtag snippet so the full
    Ads+GA4 snippet we inject doesn't load gtag.js / init dataLayer twice
    (which would double-count GA4 pageviews)."""
    pattern = re.compile(
        r'\s*<script async src="https://www\.googletagmanager\.com/gtag/js\?id='
        + re.escape(ga4_id) +
        r'"></script>\s*<script>\s*window\.dataLayer[\s\S]*?gtag\(\'config\',\s*\''
        + re.escape(ga4_id) +
        r'\'\);\s*</script>',
        re.IGNORECASE,
    )
    return pattern.sub("", html, count=1)

def inject_into_page(html: str, snippet: str, ga4_id: str) -> str:
    """Strip any previous tracking (stale full block or bare GA4-only tag),
    then insert the current tracking snippet just before </head>."""
    html = strip_old_block(html)
    html = strip_bare_ga4(html, ga4_id)
    target = "</head>"
    idx = html.lower().find(target)
    if idx == -1:
        return html
    return html[:idx] + snippet + "\n  " + html[idx:]

def backup_file(path: Path, root: Path, root_tag: str):
    dest_dir = BACKUP_DIR / root_tag
    dest_dir.mkdir(parents=True, exist_ok=True)
    rel = path.relative_to(root)
    backup_path = dest_dir / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if not backup_path.exists():
        shutil.copy2(path, backup_path)

def process_all(apply=False, target_page=None, root_target="html"):
    cfg = load_config()
    snippet = build_tracking_snippet(cfg)
    root = resolve_root(root_target)

    html_files = list(iter_html_files(root))
    if target_page:
        html_files = [f for f in html_files if target_page in str(f)]

    stats = {"total": 0, "already_ok": 0, "injected": 0, "skipped": 0, "errors": 0}

    for path in sorted(html_files):
        stats["total"] += 1
        rel = path.relative_to(root)
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
            was_tracked = has_tracking(html)
            if was_tracked:
                stats["already_ok"] += 1

            if apply:
                backup_file(path, root, root_target)
                new_html = inject_into_page(html, snippet, cfg["ga4_id"])
                path.write_text(new_html, encoding="utf-8")
                stats["injected"] += 1
                print(f"  [{'REFRESHED' if was_tracked else 'OK'}] {rel}")
            elif not was_tracked:
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
        print(f"\n  Backups saved to: {BACKUP_DIR / root_target}")
    print(f"{'='*55}")

def verify_all(root_target="html"):
    root = resolve_root(root_target)
    html_files = list(iter_html_files(root))
    missing = []
    ok = []
    for path in sorted(html_files):
        html = path.read_text(encoding="utf-8", errors="replace")
        if has_tracking(html):
            ok.append(path.relative_to(root))
        else:
            missing.append(path.relative_to(root))

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
    parser.add_argument("--root", choices=["html", "site"], default="html",
                         help="'html' = legacy VPS mirror; 'site' = repo-root content folders")
    args = parser.parse_args()

    if args.verify:
        ok = verify_all(root_target=args.root)
        sys.exit(0 if ok else 1)
    else:
        mode = "APPLY" if args.apply else "DRY RUN"
        print(f"\n[inject_tracking] Mode: {mode}")
        print(f"Root: {resolve_root(args.root)}\n")
        process_all(apply=args.apply, target_page=args.page, root_target=args.root)
