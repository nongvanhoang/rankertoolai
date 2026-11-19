"""Clean extracted pricing data and compute index stats."""
import json, re, statistics, sys
from pathlib import Path

rows = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = Path(sys.argv[2])

# Categories for tools not on a category hub (assigned from what each tool does)
EXTRA_CAT = {
 "ahaslides": "ai-productivity", "aidetector": "ai-writing", "algomo": "ai-marketing",
 "answerthis": "ai-writing", "audiorista": "ai-voice", "buzz-ai": "ai-marketing",
 "capcut": "ai-video", "chatgpt": "ai-assistants", "claude": "ai-assistants", "clearscope": "ai-seo",
 "climbx": "ai-seo", "cliptalk": "ai-video", "clonable": "ai-marketing", "codeium": "ai-coding",
 "customgpt": "ai-assistants", "deepseek": "ai-assistants", "dropmagic": "ai-marketing",
 "frase": "ai-seo", "gemini": "ai-assistants", "geo-targetly": "ai-marketing", "getresponse": "ai-marketing",
 "grok": "ai-assistants", "handoff": "ai-productivity", "headshotpro": "ai-image", "higgsfield": "ai-video",
 "imagineart": "ai-image", "insightful": "ai-productivity", "leavo": "ai-productivity",
 "livechat": "ai-marketing", "llm-pulse": "ai-seo", "macaws": "ai-voice", "magiclight": "ai-video",
 "marketmuse": "ai-seo", "mentionagent": "ai-seo", "mera-work": "ai-productivity",
 "merlin-ai": "ai-assistants", "mistral": "ai-assistants", "murf-ai": "ai-voice", "omnisend": "ai-marketing",
 "page-pulse": "ai-data", "perplexity": "ai-assistants", "pixverse": "ai-video", "playht": "ai-voice",
 "reditus": "ai-marketing", "robofy": "ai-marketing", "rytr": "ai-writing", "sai": "ai-marketing",
 "salestarget-ai": "ai-marketing", "shopify": "ai-marketing", "signeasy": "ai-productivity",
 "siift": "ai-productivity", "skysnail": "ai-image", "socialdesk": "ai-marketing",
 "syncee": "ai-marketing", "tabnine": "ai-coding", "tunee-ai": "ai-voice", "viktor": "ai-productivity",
 "viralityai": "ai-marketing", "woodpecker": "ai-marketing", "writehuman": "ai-writing", "yeta": "ai-productivity",
 "speechify": "ai-voice",
}
CAT_NAME = {
 "ai-assistants": "AI chat assistants", "ai-coding": "AI coding", "ai-data": "Data & analytics",
 "ai-design": "Design & image", "ai-image": "Design & image", "ai-marketing": "Marketing & sales",
 "ai-productivity": "Productivity & teams", "ai-seo": "SEO & content", "ai-video": "Video",
 "ai-voice": "Voice & audio", "ai-writing": "Writing", "gaming-network-tools": "Other",
 "password-manager": "Other", "privacy-compliance": "Other",
}
# Usage/credit/pack pricing: no comparable monthly entry price
USAGE = {"deepseek", "grape-leads", "emaillistverify", "woodpecker", "joiin", "headshotpro", "audiorista"}
# Non-USD list prices: kept in the table, excluded from USD medians
NON_USD = {"clonable": "€49", "llm-pulse": "€49", "macaws": "€99", "orateur": "€49",
           "signitic": "€1/user", "rankbolt": "CHF 69"}
# No table on page
NO_TABLE = {"frase", "stable-diffusion"}
# Manual fixes after reading the pages' tables
ENTRY_FIX = {"ahaslides": 9.45,  # Edu tier is education-only; Essential is the general entry plan
             "clipto": 9.99, "gearup-booster": 4.49,
             # list prices, not first-month or launch-code promos
             "synthesia": 19.0, "siift": 29.0}

def is_trial(p):
    s = (p["plan"] + " " + p["price"]).lower()
    return "trial" in s or re.search(r"for \d+ days", s) is not None

def is_free(p):
    s = p["price"].lower().replace(" ", "")
    return (s.startswith("$0") or s.startswith("free") or s.startswith("€0") or s == "0") and not is_trial(p)

out = []
for r in rows:
    slug = r["slug"]
    cat = r["category"] or EXTRA_CAT.get(slug, "")
    plans = r["plans"]
    free_plan = any(is_free(p) for p in plans) or slug in {"codeium", "tabnine", "canva-ai"}
    trial = any(is_trial(p) for p in plans) or bool(re.search(r"free trial", r["note"].lower()))
    entry = ENTRY_FIX.get(slug, r["entry_paid_monthly"])
    model = "usage" if slug in USAGE else ("per-seat" if r["per_seat"] else "flat")
    if slug in USAGE or slug in NON_USD or slug in NO_TABLE:
        entry = None
    out.append({
        "slug": slug, "name": re.sub(r"\s+Review.*$", "", r["name"]).strip(),
        "group": CAT_NAME.get(cat, "Other"),
        "free_plan": free_plan, "free_trial_only": (not free_plan) and trial,
        "entry_usd_month": entry, "list_price_note": NON_USD.get(slug, ""),
        "model": model, "contact_sales_tier": r["contact_sales"],
        "plans": plans, "updated": r["date_modified"], "no_table": slug in NO_TABLE,
    })

CUTOFF = sys.argv[3] if len(sys.argv) > 3 else "2026-10-01"
for o in out:
    o["in_index"] = (not o["no_table"]) and o["updated"] >= CUTOFF
usable = [o for o in out if o["in_index"]]
n = len(usable)
paid = [o["entry_usd_month"] for o in usable if o["entry_usd_month"]]
stats = {
 "tools": n, "cutoff": CUTOFF,
 "updated_min": min(o["updated"] for o in usable), "updated_max": max(o["updated"] for o in usable),
 "free_plan": sum(o["free_plan"] for o in usable),
 "trial_only": sum(o["free_trial_only"] for o in usable),
 "no_free": sum((not o["free_plan"]) and (not o["free_trial_only"]) for o in usable),
 "per_seat": sum(o["model"] == "per-seat" for o in usable),
 "usage": sum(o["model"] == "usage" for o in usable),
 "contact_sales": sum(o["contact_sales_tier"] for o in usable),
 "median_entry": statistics.median(paid), "n_entry": len(paid),
 "under_20": sum(1 for v in paid if v < 20), "over_100": sum(1 for v in paid if v >= 100),
 "groups": {},
}
for g in sorted({o["group"] for o in usable}):
    gs = [o for o in usable if o["group"] == g]
    gp = sorted((o["entry_usd_month"], o["name"]) for o in gs if o["entry_usd_month"])
    stats["groups"][g] = {"tools": len(gs), "free_plan": sum(o["free_plan"] for o in gs),
        "median_entry": statistics.median([v for v, _ in gp]) if gp else None,
        "cheapest": gp[0] if gp else None, "priciest": gp[-1] if gp else None, "n_entry": len(gp)}
OUT.write_text(json.dumps({"stats": stats, "tools": out}, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(stats, indent=1))
print("uncategorised:", [o["slug"] for o in out if o["group"] == "Other"])
