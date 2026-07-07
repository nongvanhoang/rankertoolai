"""Remove Google Ads AW-XXXXXXXXXX placeholders from all HTML files."""
import os, re

HTML_DIR = os.path.join(os.path.dirname(__file__), "html")

# Patterns to remove (entire lines containing these)
REMOVE_PATTERNS = [
    r"\s*gtag\('config',\s*'AW-XXXXXXXXXX'\);\n",
    r"\s*'send_to':\s*'AW-XXXXXXXXXX/[A-Z]+',\n",
    r"\s*gtag\('event',\s*'conversion',\s*\{'send_to':\s*'AW-XXXXXXXXXX/[A-Z]+'\}\);\n",
]

combined = re.compile("|".join(REMOVE_PATTERNS))

fixed = 0
for root, dirs, files in os.walk(HTML_DIR):
    dirs[:] = [d for d in dirs if d != ".wrangler"]
    for fname in files:
        if not fname.endswith(".html"):
            continue
        path = os.path.join(root, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "AW-XXXXXXXXXX" not in content:
            continue
        new_content = combined.sub("", content)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1

print(f"Fixed {fixed} files — removed AW-XXXXXXXXXX placeholders")
