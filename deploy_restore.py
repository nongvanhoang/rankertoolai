"""
Restore files quarantined by deploy_quarantine.py back into html/ after a
`wrangler pages deploy` finishes. See deploy_quarantine.py for the full
workflow and the reason this exists.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
HTML_DIR = ROOT / "html"
HOLDING = ROOT / ".deploy_quarantine_holding"

restored = 0
for src in HOLDING.rglob("*"):
    if src.is_file():
        rel = src.relative_to(HOLDING)
        dst = HTML_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        restored += 1

print(f"Restored {restored} files back into html/.")
