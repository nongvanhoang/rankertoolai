"""
Move internal automation/business-ops files out of html/ before running
`wrangler pages deploy html`, so they can never be uploaded to the public
Cloudflare Pages deployment. Restore them afterward with deploy_restore.py.

The exclusion list (deploy_quarantine_list.txt) is checked into git so it
survives across sessions — a prior version of this list lived only in an
ephemeral scratchpad and silently missed 17 files (including update_links.py,
seo_audit.py, build_dashboard.py, and social_agent/data/tools.json) for an
unknown period, which is how those ended up served from a public URL.

IMPORTANT: always run deploy_restore.py again right after the deploy
finishes, in the same session/terminal — never leave html/ in the
quarantined state, and never delete .deploy_quarantine_holding/ without
restoring its contents first (that emptied it once already, see the
2026-07-07 postmortem in the project memory).

Usage:
  python deploy_quarantine.py
  npx wrangler pages deploy html --project-name=rankertoolai
  python deploy_restore.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
HTML_DIR = ROOT / "html"
HOLDING = ROOT / ".deploy_quarantine_holding"
LIST_FILE = ROOT / "deploy_quarantine_list.txt"

HOLDING.mkdir(parents=True, exist_ok=True)
files = LIST_FILE.read_text(encoding="utf-8-sig").splitlines()

moved = 0
for rel in files:
    rel = rel.strip()
    if not rel:
        continue
    src = HTML_DIR / rel
    if not src.exists():
        continue
    dst = HOLDING / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    moved += 1

print(f"Moved {moved} files out of html/ into {HOLDING}.")
print("Run deploy_restore.py immediately after the deploy finishes.")
