"""
Module 3: Generate Google Ads campaign structure.

Outputs a CSV file ready to import into Google Ads Editor.
Structure:
  Campaign: RankerToolAI - AI Tools [Review/Compare/Best]
  Ad Groups: One per tool or category
  Keywords: 5-10 per ad group (exact + phrase match)
  Ads: 3 Responsive Search Ads per ad group (15 headlines, 4 descriptions)

Usage:
  python generate_campaigns.py               # Generate all campaigns
  python generate_campaigns.py --tool jasper # Single tool
  python generate_campaigns.py --type review # Type: review | compare | best | all
  python generate_campaigns.py --preview     # Print without saving
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

TOOLS_PATH = Path(__file__).parent.parent.parent / "social_agent" / "data" / "tools.json"
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
OUT_DIR = Path(__file__).parent.parent / "data"

def load_tools():
    with open(TOOLS_PATH, encoding="utf-8") as f:
        return json.load(f)

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── KEYWORD TEMPLATES ────────────────────────────────────────────────────────

def review_keywords(name: str, slug: str) -> list[dict]:
    n = name
    return [
        # Exact match — highest intent
        {"keyword": f"{n.lower()} review",           "match": "Exact", "bid": 2.00},
        {"keyword": f"{n.lower()} reviews 2026",     "match": "Exact", "bid": 2.00},
        {"keyword": f"is {n.lower()} worth it",      "match": "Exact", "bid": 2.20},
        {"keyword": f"{n.lower()} pros and cons",    "match": "Exact", "bid": 1.80},
        {"keyword": f"{n.lower()} pricing",          "match": "Exact", "bid": 1.60},
        # Phrase match — broader
        {"keyword": f"{n.lower()} review",           "match": "Phrase", "bid": 1.50},
        {"keyword": f"{n.lower()} honest review",    "match": "Phrase", "bid": 1.80},
        {"keyword": f"best {n.lower()} plan",        "match": "Phrase", "bid": 1.40},
    ]

def compare_keywords(name1: str, name2: str) -> list[dict]:
    a, b = name1.lower(), name2.lower()
    return [
        {"keyword": f"{a} vs {b}",           "match": "Exact",  "bid": 2.50},
        {"keyword": f"{b} vs {a}",           "match": "Exact",  "bid": 2.50},
        {"keyword": f"{a} or {b}",           "match": "Exact",  "bid": 2.00},
        {"keyword": f"{a} vs {b} comparison","match": "Phrase", "bid": 2.00},
        {"keyword": f"difference between {a} and {b}", "match": "Phrase", "bid": 1.80},
    ]

def alternative_keywords(name: str) -> list[dict]:
    n = name.lower()
    return [
        {"keyword": f"{n} alternatives",            "match": "Exact",  "bid": 2.20},
        {"keyword": f"best {n} alternatives",       "match": "Exact",  "bid": 2.20},
        {"keyword": f"{n} alternative free",        "match": "Exact",  "bid": 2.00},
        {"keyword": f"alternatives to {n}",         "match": "Phrase", "bid": 1.80},
        {"keyword": f"{n} competitors",             "match": "Phrase", "bid": 1.60},
    ]

def best_keywords(category: str) -> list[dict]:
    c = category.lower()
    return [
        {"keyword": f"best {c}",              "match": "Exact",  "bid": 2.00},
        {"keyword": f"best {c} 2026",         "match": "Exact",  "bid": 2.20},
        {"keyword": f"top {c}",               "match": "Exact",  "bid": 1.80},
        {"keyword": f"{c} comparison",        "match": "Phrase", "bid": 1.60},
        {"keyword": f"{c} review",            "match": "Phrase", "bid": 1.60},
    ]

def deal_keywords(name: str, has_code: bool) -> list[dict]:
    n = name.lower()
    kws = [
        {"keyword": f"{n} discount",          "match": "Exact", "bid": 1.00},
        {"keyword": f"{n} deal",              "match": "Exact", "bid": 1.00},
        {"keyword": f"{n} free trial",        "match": "Exact", "bid": 1.10},
    ]
    if has_code:
        kws += [
            {"keyword": f"{n} coupon code",   "match": "Exact", "bid": 0.90},
            {"keyword": f"{n} promo code",    "match": "Exact", "bid": 0.90},
            {"keyword": f"{n} discount code 2026", "match": "Exact", "bid": 0.90},
        ]
    return kws

# ── AD COPY TEMPLATES ─────────────────────────────────────────────────────────

def review_ads(tool: dict, cfg: dict) -> list[dict]:
    name = tool["name"]
    score = tool["score"]
    slug = tool["slug"]
    site = cfg["site_url"]
    url = f"{site}/lp/{slug}/"

    return [{
        "type": "Responsive Search Ad",
        "final_url": url,
        "display_url_path1": "Review",
        "display_url_path2": name.replace(" ", "-")[:15],
        "headlines": [
            f"{name} Review 2026",
            f"Is {name} Worth It? ({score}/10)",
            f"Honest {name} Review",
            f"{name} — Expert Score: {score}/10",
            f"We Tested {name} for 100hrs",
            f"{name} Pros, Cons & Pricing",
            "Unbiased AI Tool Reviews",
            "Expert-Tested AI Tools",
            f"Try {name} Risk-Free",
            f"{name} Free Trial Available",
            "No Affiliate Bias",
            "Updated July 2026",
            f"Is {name} Right For You?",
            f"See Full {name} Breakdown",
            f"{name} — Real User Rating",
        ][:15],
        "descriptions": [
            f"We spent 100+ hours testing {name}. Score: {score}/10. See full breakdown of features, pricing, and real use cases.",
            f"Independent {name} review by AI tool experts. No bias. Pros, cons, pricing — everything you need before you buy.",
            f"Compare {name} with alternatives. Updated weekly. Find the best AI tool for your needs at RankerToolAI.",
            f"{name} review: who should use it, how much it costs, and whether it's worth the money in 2026.",
        ][:4],
    }]

def compare_ads(tool1: dict, tool2: dict, cfg: dict) -> list[dict]:
    n1, n2 = tool1["name"], tool2["name"]
    slug1, slug2 = tool1["slug"], tool2["slug"]
    site = cfg["site_url"]
    url = f"{site}/compare/{slug1}-vs-{slug2}/"

    return [{
        "type": "Responsive Search Ad",
        "final_url": url,
        "display_url_path1": "Compare",
        "display_url_path2": f"{n1[:7]}-vs-{n2[:7]}",
        "headlines": [
            f"{n1} vs {n2} — 2026",
            f"Which Is Better: {n1} or {n2}?",
            f"{n1} vs {n2} Compared",
            f"See Head-to-Head Comparison",
            f"Which AI Tool Wins in 2026?",
            f"Expert Side-by-Side Comparison",
            f"{n1} vs {n2} — Pricing & Features",
            "Unbiased Head-to-Head Test",
            f"We Tested Both {n1} & {n2}",
            "Find the Better AI Tool",
            "Compare Features & Pricing",
            "Updated July 2026",
            f"{n1} or {n2}? Find Out Now",
            f"Side-by-Side: {n1} vs {n2}",
            "Free Comparison Report",
        ][:15],
        "descriptions": [
            f"We tested {n1} and {n2} head-to-head. See full feature comparison, pricing breakdown, and our expert verdict.",
            f"{n1} vs {n2}: which AI tool performs better? Honest comparison with scores, pros, cons, and best use cases.",
            f"Can't decide between {n1} and {n2}? Our side-by-side comparison shows exactly which one fits your workflow.",
            f"Expert comparison: {n1} vs {n2}. See speed, accuracy, pricing, and which one wins for your specific use case.",
        ][:4],
    }]

def best_ads(category: str, tools_list: list, cfg: dict) -> list[dict]:
    site = cfg["site_url"]
    slug = category.lower().replace(" ", "-")
    url = f"{site}/best/{slug}/"

    names = [t["name"] for t in tools_list[:3]]
    top3 = ", ".join(names)

    return [{
        "type": "Responsive Search Ad",
        "final_url": url,
        "display_url_path1": "Best",
        "display_url_path2": slug[:15],
        "headlines": [
            f"Best {category} 2026",
            f"Top {len(tools_list)} {category} Ranked",
            f"Expert-Ranked {category}",
            f"{top3} & More",
            "We Tested 20+ AI Tools",
            "Find the Right AI Tool",
            f"#1 Ranked: {names[0] if names else 'Top AI Tool'}",
            "Reviewed by Experts",
            "Updated July 2026",
            "Free Tier Options Included",
            "Pricing Comparison Inside",
            "Best Value AI Tools",
            f"{category} — Full Rankings",
            "Compare Top-Rated Options",
            "No Paid Rankings",
        ][:15],
        "descriptions": [
            f"We tested the top {category} in 2026. Expert scores, pricing comparison, and our top pick. Updated weekly.",
            f"Find the best {category} for your budget. Ranked by performance, ease of use, and value for money.",
            f"Our experts tested {len(tools_list)}+ {category}. See which ones are worth your money in 2026.",
            f"Compare the top {category}: features, pricing, free trials. No sponsored placements — just honest rankings.",
        ][:4],
    }]

def deal_ads(tool: dict, deal: dict, cfg: dict) -> list[dict]:
    name = tool["name"]
    slug = tool["slug"]
    site = cfg["site_url"]
    url = f"{site}/go/{slug}/"
    offer = deal["offer"]
    code = deal.get("code")

    code_line = f"Use code {code} at checkout. " if code else ""
    headlines = [
        f"{name} {offer}",
        f"{name} Coupon Code" if code else f"{name} Free Trial",
        f"{name}: {offer}",
        f"Get {offer} on {name}",
        code if code else f"{name} Deal Verified",
        "Verified July 2026",
        f"{name} Discount — Apply Now",
        f"No Card Needed" if "trial" in offer.lower() else f"{name} Checkout Discount",
        f"{name} Official Deal",
        f"Best {name} Price 2026",
        f"{name} — Exclusive Reader Deal",
        f"Apply {code}" if code else f"Try {name} Free",
        f"{name} Savings Inside",
        "Limited-Time Offer",
        f"{name} Pricing + Discount",
    ][:15]
    descriptions = [
        f"{code_line}{offer} on {name}. Verified working July 2026. Click through for details.",
        f"Exclusive {name} deal for RankerToolAI readers: {offer}. {code_line}No hidden fees.",
        f"{name}: {offer}. See how it compares before you buy — full review + deal details inside.",
        f"Save on {name} today. {code_line}Offer verified and updated regularly.",
    ][:4]

    return [{
        "type": "Responsive Search Ad",
        "final_url": url,
        "display_url_path1": "Deal",
        "display_url_path2": name.replace(" ", "-")[:15],
        "headlines": headlines,
        "descriptions": descriptions,
    }]

# ── CSV EXPORT ────────────────────────────────────────────────────────────────

# Minimum-budget test set — tools with a live affiliate link + confirmed real
# offer (coupon code or verified % off / trial). One campaign each so spend
# and conversions can be compared cleanly instead of sharing one campaign budget.
DEAL_TOOLS = {
    "julius-ai":  {"offer": "10% Off First Payment", "code": "25RQK3UL"},
    "se-ranking": {"offer": "15% Off First Purchase", "code": "welcome15"},
    "pictory":    {"offer": "Exclusive Checkout Discount", "code": "RankerToolAI"},
    "elevenlabs": {"offer": "50% Off First Month", "code": None},
    "beehiiv":    {"offer": "14-Day Trial + 20% Off 3 Months", "code": None},
    "mangools":   {"offer": "10-Day Free Trial", "code": None},
    "wispr-flow": {"offer": "14-Day Free Pro Trial", "code": None},
}

COMPARE_PAIRS = [
    ("chatgpt", "claude"), ("chatgpt", "gemini"), ("claude", "gemini"),
    ("cursor", "github-copilot"), ("cursor", "windsurf"),
    ("jasper", "writesonic"),
    ("elevenlabs", "murf"), ("elevenlabs", "lovo-ai"), ("elevenlabs", "descript"),
    ("surfer-seo", "semrush"),
    ("midjourney", "stable-diffusion"),
]

BEST_CATEGORIES = {
    "ai-writing-tools": "AI Writing Tool",
    "ai-image-generators": "AI Image Generator",
    "ai-coding-tools": "AI Coding Tool",
    "ai-seo-tools": "AI SEO Tool",
    "ai-voice-tools": "AI Voice Generator",
    "ai-video-tools": "AI Video Tool",
    "ai-chatbots": "AI Chatbot",
    "ai-productivity-tools": "AI Productivity Tool",
}

def generate_csv(campaign_type="all", tool_slug=None, preview=False):
    tools_list = load_tools()
    cfg = load_config()
    tools = {t["slug"]: t for t in tools_list}
    budget = cfg["budget"]

    rows = []
    rows.append(["Type", "Campaign", "Ad Group", "Match Type", "Keyword / Ad Element", "Value", "Max CPC", "Status", "Final URL"])

    def add_campaign(name, daily_budget):
        rows.append(["Campaign", name, "", "", "", "", "", "Enabled", ""])
        rows.append(["Campaign Budget", name, "", "", "Daily Budget", str(daily_budget), "", "", ""])

    def add_ad_group(campaign, group_name):
        rows.append(["Ad Group", campaign, group_name, "", "", "", "", "Enabled", ""])

    def add_keyword(campaign, group, kw):
        rows.append(["Keyword", campaign, group, kw["match"], kw["keyword"], "", str(kw["bid"]), "Enabled", ""])

    def add_ad(campaign, group, ad):
        for i, h in enumerate(ad["headlines"], 1):
            rows.append([f"Headline {i}", campaign, group, "", h[:30], "", "", "", ad["final_url"]])
        for i, d in enumerate(ad["descriptions"], 1):
            rows.append([f"Description {i}", campaign, group, "", d[:90], "", "", "", ""])
        rows.append(["Display URL Path 1", campaign, group, "", ad.get("display_url_path1",""), "", "", "", ""])
        rows.append(["Display URL Path 2", campaign, group, "", ad.get("display_url_path2",""), "", "", "", ""])

    # ── REVIEW CAMPAIGN ────────────────────────────────────────────────────────
    if campaign_type in ("all", "review"):
        campaign = "RankerToolAI - AI Tool Reviews"
        add_campaign(campaign, budget["daily_budget_usd"] * 0.5)

        targets = [tools[tool_slug]] if tool_slug and tool_slug in tools else [
            tools[s] for s in cfg["priority_tools"] if s in tools
        ]
        for tool in targets:
            group = f"{tool['name']} Review"
            add_ad_group(campaign, group)
            for kw in review_keywords(tool["name"], tool["slug"]):
                add_keyword(campaign, group, kw)
            for ad in review_ads(tool, cfg):
                add_ad(campaign, group, ad)

    # ── COMPARE CAMPAIGN ───────────────────────────────────────────────────────
    if campaign_type in ("all", "compare") and not tool_slug:
        campaign = "RankerToolAI - AI Tool Comparisons"
        add_campaign(campaign, budget["daily_budget_usd"] * 0.3)

        for s1, s2 in COMPARE_PAIRS:
            if s1 in tools and s2 in tools:
                t1, t2 = tools[s1], tools[s2]
                group = f"{t1['name']} vs {t2['name']}"
                add_ad_group(campaign, group)
                for kw in compare_keywords(t1["name"], t2["name"]):
                    add_keyword(campaign, group, kw)
                for ad in compare_ads(t1, t2, cfg):
                    add_ad(campaign, group, ad)

    # ── DEAL TEST CAMPAIGN (minimum-budget, one campaign per tool) ─────────────
    if campaign_type in ("all", "deals"):
        deal_daily_budget = budget.get("deal_test_daily_budget_usd", 3)
        deal_targets = {tool_slug: DEAL_TOOLS[tool_slug]} if tool_slug and tool_slug in DEAL_TOOLS else DEAL_TOOLS
        for slug, deal in deal_targets.items():
            if slug not in tools:
                continue
            tool = tools[slug]
            campaign = f"RankerToolAI - Deal Test - {tool['name']}"
            add_campaign(campaign, deal_daily_budget)
            group = f"{tool['name']} Deal"
            add_ad_group(campaign, group)
            for kw in deal_keywords(tool["name"], has_code=bool(deal.get("code"))):
                add_keyword(campaign, group, kw)
            for ad in deal_ads(tool, deal, cfg):
                add_ad(campaign, group, ad)

    # ── BEST-OF CAMPAIGN ───────────────────────────────────────────────────────
    if campaign_type in ("all", "best") and not tool_slug:
        campaign = "RankerToolAI - Best AI Tools"
        add_campaign(campaign, budget["daily_budget_usd"] * 0.2)

        for slug, category in BEST_CATEGORIES.items():
            cat_tools = [t for t in tools_list if category.lower() in t.get("category","").lower()][:5]
            if not cat_tools:
                continue
            group = f"Best {category}"
            add_ad_group(campaign, group)
            for kw in best_keywords(category):
                add_keyword(campaign, group, kw)
            for ad in best_ads(category, cat_tools, cfg):
                add_ad(campaign, group, ad)

    if preview:
        # Print first 40 rows
        for row in rows[:40]:
            print(" | ".join(str(c) for c in row))
        print(f"\n... ({len(rows)} total rows)")
        return

    # Save CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"google_ads_campaign_{campaign_type}_{ts}.csv"
    out_path = OUT_DIR / filename
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\n[generate_campaigns] Campaign CSV generated:")
    print(f"  File:  {out_path}")
    print(f"  Rows:  {len(rows)}")
    print(f"\n  Import into Google Ads Editor:")
    print(f"  File -> Import -> From CSV")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", default="all", choices=["all","review","compare","best","deals"])
    parser.add_argument("--tool", help="Single tool slug")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    generate_csv(campaign_type=args.type, tool_slug=args.tool, preview=args.preview)
