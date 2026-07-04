"""
Generate negative keyword list for Google Ads — prevents wasted spend.

Saves a CSV file ready to upload to Google Ads as a shared negative keyword list.

Usage:
  python generate_negative_keywords.py
"""

import csv
from pathlib import Path
from datetime import datetime

OUT_DIR = Path(__file__).parent.parent / "data"

NEGATIVE_KEYWORDS = {
    "Job / Career (not buyers)": [
        "job", "jobs", "career", "careers", "hire", "hiring", "salary",
        "internship", "work at", "work for", "employee", "apply",
    ],
    "Free / Cracked (non-buyers)": [
        "free download", "crack", "cracked", "pirate", "torrent", "nulled",
        "keygen", "serial key", "license key free", "activate free",
    ],
    "Education / Research (low purchase intent)": [
        "thesis", "dissertation", "essay", "homework", "assignment",
        "what is", "definition", "how does", "history of", "wikipedia",
        "research paper", "academic",
    ],
    "News / General Info (informational, no purchase)": [
        "news", "latest news", "update", "announcement", "press release",
        "stock", "ipo", "funding", "valuation",
    ],
    "Complaints (avoid negative sentiment)": [
        "scam", "fraud", "fake", "legit", "safe", "dangerous",
        "hacked", "data breach", "privacy issue", "cancelled",
    ],
    "Competitor-specific (if not running comparison)": [],
    "Unrelated Tools": [
        "photoshop", "microsoft word", "excel", "google docs",
        "powerpoint", "gmail", "outlook", "slack", "zoom",
        "tiktok", "instagram", "facebook", "youtube creator",
    ],
    "Support / Customer Service": [
        "customer service", "support number", "help desk", "refund",
        "cancel subscription", "contact", "phone number",
    ],
    "Coding / Technical for wrong audience": [
        "github repo", "open source", "self hosted", "docker", "kubernetes",
        "api documentation", "sdk tutorial",
    ],
}

def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = OUT_DIR / f"negative_keywords_{ts}.csv"

    rows = [["Keyword", "Match Type", "Campaign / List", "Notes"]]
    total = 0

    for category, keywords in NEGATIVE_KEYWORDS.items():
        for kw in keywords:
            # Add as both broad and phrase for maximum coverage
            rows.append([kw, "Broad", "All Campaigns", category])
            rows.append([f'"{kw}"', "Phrase", "All Campaigns", category])
            total += 2

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\n[negative_keywords] Generated {total} negative keywords")
    print(f"  File: {out_path}")
    print(f"\n  Upload in Google Ads:")
    print(f"  Tools -> Shared Library -> Negative Keyword Lists -> Upload CSV")
    return out_path

if __name__ == "__main__":
    generate()
