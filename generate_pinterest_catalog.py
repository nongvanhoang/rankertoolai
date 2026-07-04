#!/usr/bin/env python3
"""Generate Pinterest product catalog CSV from tools.json."""
import json, re, csv
from pathlib import Path

DATA  = Path("social_agent/data/tools.json")
OUT   = Path("html/catalog.csv")
BASE  = "https://rankertoolai.com"

CATEGORY_MAP = {
    "AI Chatbot":           "Software",
    "AI Coding Tool":       "Software",
    "AI Coding IDE":        "Software",
    "AI Writing Tool":      "Software",
    "AI SEO Tool":          "Software",
    "AI SEO Suite":         "Software",
    "AI Image Generator":   "Software",
    "AI Design Tool":       "Software",
    "AI Video Generator":   "Software",
    "AI Voice Generator":   "Software",
    "AI Productivity Tool": "Software",
    "AI CRM & Marketing":   "Software",
    "AI Search Tool":       "Software",
    "AI Data Analysis Tool":"Software",
}

def extract_price(price_str):
    """Return lowest numeric price found, e.g. '20.00 USD'."""
    amounts = re.findall(r'\$(\d+(?:\.\d+)?)', price_str)
    if not amounts:
        return "0.00 USD"
    lowest = min(float(a) for a in amounts)
    return f"{lowest:.2f} USD"

def main():
    tools = json.loads(DATA.read_text(encoding="utf-8"))
    rows = []
    for t in tools:
        slug = t["slug"]
        # Use Pinterest vertical image (1000x1500, 2:3 ratio — ideal for Pinterest catalog)
        image_url = f"{BASE}/assets/images/pin-{slug}.jpg"
        desc = f"{t['tagline']}. Best for: {t['best_for']}. Rated {t['score']}/10."
        rows.append({
            "id":                    slug,
            "title":                 t["name"],
            "description":           desc[:500],
            "link":                  t["url"],
            "image_link":            image_url,
            "price":                 extract_price(t["price"]),
            "availability":          "in stock",
            "condition":             "new",
            "brand":                 "RankerToolAI",
            "google_product_category": CATEGORY_MAP.get(t["category"], "Software"),
        })

    fields = ["id","title","description","link","image_link","price",
              "availability","condition","brand","google_product_category"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Done! {len(rows)} products -> {OUT}")
    print(f"  Feed URL: {BASE}/catalog.csv")

if __name__ == "__main__":
    main()
