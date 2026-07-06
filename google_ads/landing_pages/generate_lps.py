"""
Module 2: Generate Google Ads landing pages for each tool.

These landing pages (/lp/[tool]/) are:
- Faster loading than full review pages
- Message-matched to ad copy (headline = ad headline)
- Conversion-focused: CTA above fold, trust signals, clear value prop
- UTM-aware: tracks source automatically
- No nav distraction (header is minimal)

Usage:
  python generate_lps.py                        # Generate all LPs
  python generate_lps.py --tool elevenlabs      # Generate single LP
  python generate_lps.py --list                 # List all tools
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

TOOLS_PATH = Path(__file__).parent.parent.parent / "social_agent" / "data" / "tools.json"
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
OUT_DIR = Path(__file__).parent.parent.parent / "lp"

EXTRA_DATA = {
    "pictory": {
        "hero": "Turn Blog Posts Into Videos in Minutes",
        "sub": "No editing skills needed. 3M+ licensed stock clips, auto-captions at 95%+ accuracy.",
        "cta": "Try Pictory Free",
        "badge": "Exclusive Checkout Discount",
        "trust": ["Blog-to-video in minutes", "Auto-captions 95%+ accuracy", "3M+ licensed stock clips", "No credit card for trial"],
        "urgency": "Use code RankerToolAI at checkout for an exclusive discount",
        "category": "AI Video Generator",
    },
    "elevenlabs": {
        "hero": "Turn Text Into Studio-Quality Voice in Seconds",
        "sub": "Used by 1M+ creators. Most realistic AI voice in 2026.",
        "cta": "Try ElevenLabs Free",
        "badge": "Free Plan Available",
        "trust": ["99 languages", "Voice cloning", "API access", "Used by 1M+ creators"],
        "urgency": "Free tier: 10,000 characters/month — no credit card needed",
        "category": "AI Voice Generator",
    },
    "jasper": {
        "hero": "Write 10x More Marketing Content With AI",
        "sub": "The AI writing tool trusted by 100,000+ marketing teams.",
        "cta": "Start Jasper Free Trial",
        "badge": "7-Day Free Trial",
        "trust": ["50+ templates", "Brand voice AI", "Integrates with Surfer SEO", "Team collaboration"],
        "urgency": "7-day free trial — cancel anytime",
        "category": "AI Writing Tool",
    },
    "surfer-seo": {
        "hero": "Rank Higher With AI-Powered Content Optimization",
        "sub": "Surfer SEO tells you exactly what to write to outrank competitors.",
        "cta": "Try Surfer SEO Free",
        "badge": "7-Day Free Trial",
        "trust": ["Real-time NLP scoring", "Google Docs integration", "500+ customers", "SERP analysis"],
        "urgency": "Get your first content score free — no card needed",
        "category": "AI SEO Tool",
    },
    "writesonic": {
        "hero": "Create SEO Content That Ranks — 10x Faster",
        "sub": "AI writer trained on top-ranking content. Loved by 1M+ users.",
        "cta": "Try Writesonic Free",
        "badge": "Free Plan Available",
        "trust": ["Factual AI content", "SEO mode built-in", "100+ templates", "1M+ users"],
        "urgency": "Free plan: 10,000 words/month",
        "category": "AI Writing Tool",
    },
    "copy-ai": {
        "hero": "Stop Staring at a Blank Page. Let AI Write It.",
        "sub": "Copy.AI writes ad copy, emails, and blogs in seconds.",
        "cta": "Try Copy.AI Free",
        "badge": "Free Forever Plan",
        "trust": ["10M+ users", "90+ tools", "Workflows automation", "Team plan"],
        "urgency": "Free plan available — unlimited AI chat",
        "category": "AI Copywriting Tool",
    },
    "midjourney": {
        "hero": "Create Stunning AI Art in Under 60 Seconds",
        "sub": "The most popular AI image generator used by designers worldwide.",
        "cta": "Try Midjourney",
        "badge": "From $10/month",
        "trust": ["Photorealistic output", "V6 model", "Active community", "Commercial license"],
        "urgency": "Plans from $10/month — 200 images included",
        "category": "AI Image Generator",
    },
    "chatgpt": {
        "hero": "The World's Most Powerful AI Assistant",
        "sub": "ChatGPT does it all: writing, coding, research, image generation.",
        "cta": "Try ChatGPT Free",
        "badge": "Free + Plus $20/mo",
        "trust": ["GPT-4o model", "Image generation", "Code interpreter", "100M+ users"],
        "urgency": "Free tier available — upgrade to Plus for GPT-4o",
        "category": "AI Assistant",
    },
    "cursor": {
        "hero": "Code 10x Faster With AI That Knows Your Codebase",
        "sub": "The AI code editor that understands your entire project.",
        "cta": "Download Cursor Free",
        "badge": "Free Plan Available",
        "trust": ["Codebase-aware AI", "Works with any language", "VS Code compatible", "250K+ devs"],
        "urgency": "Free plan: 50 slow requests/month",
        "category": "AI Coding Tool",
    },
    "julius-ai": {
        "hero": "Chat With Your Spreadsheets in Plain English",
        "sub": "Upload any CSV or Excel file and ask questions — get instant charts and stats.",
        "cta": "Try Julius AI Free",
        "badge": "Free Plan Available",
        "trust": ["Natural language queries", "Auto Python code", "15 free analyses/mo", "Statistical tests built-in"],
        "urgency": "Free: 15 analyses/month — code 25RQK3UL for 10% off Pro",
        "category": "AI Data Analysis Tool",
    },
    "mangools": {
        "hero": "The Most Beginner-Friendly SEO Toolkit — 5 Tools in One",
        "sub": "KWFinder, SERPWatcher, LinkMiner and more — from just $29/month.",
        "cta": "Start Mangools Free Trial",
        "badge": "10-Day Free Trial",
        "trust": ["Best-in-class keyword difficulty", "5 tools included", "No credit card for trial", "Loved by bloggers"],
        "urgency": "10-day free trial — no credit card needed",
        "category": "AI SEO Tool",
    },
    "se-ranking": {
        "hero": "Full SEO Suite at Half the Price of Semrush",
        "sub": "Rank tracking, keyword research, and site audits — from $65/month.",
        "cta": "Try SE Ranking Free",
        "badge": "14-Day Free Trial + 15% Off",
        "trust": ["Rank tracking + site audit", "30B+ keyword database", "14-day free trial", "Half the price of Semrush"],
        "urgency": "14-day trial — code welcome15 for 15% off first payment",
        "category": "AI SEO Tool",
    },
    "beehiiv": {
        "hero": "The Newsletter Platform Built to Grow and Monetize",
        "sub": "Email, website, and monetization — 0% platform commission on paid subs.",
        "cta": "Try beehiiv Free",
        "badge": "14-Day Trial + 20% Off",
        "trust": ["0% platform commission", "Free up to 2,500 subs", "Built-in ad network", "14-day Pro trial"],
        "urgency": "14-day trial — 20% off your first 3 months on paid plans",
        "category": "Newsletter Platform",
    },
    "wispr-flow": {
        "hero": "Speak Instead of Typing — In Any App",
        "sub": "AI dictation that cleans up filler words and grammar automatically.",
        "cta": "Try Wispr Flow Free",
        "badge": "14-Day Pro Trial",
        "trust": ["Works in any app", "4x faster than typing", "100+ languages", "2,000 free words/week"],
        "urgency": "Free: 2,000 words/week — 14-day Pro trial, no card",
        "category": "AI Productivity Tool",
    },
}

def load_tools():
    with open(TOOLS_PATH, encoding="utf-8") as f:
        return {t["slug"]: t for t in json.load(f)}

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_lp(tool: dict, extra: dict, cfg: dict) -> str:
    slug = tool["slug"]
    name = tool["name"]
    score = tool["score"]
    price = tool.get("price", "Free tier available")
    pros = tool.get("pros", [])[:3]
    best_for = tool.get("best_for", "")
    review_url = f"https://rankertoolai.com/review/{slug}/"
    go_url = f"https://rankertoolai.com/go/{slug}/"
    ga4 = cfg["ga4_id"]
    ads_id = cfg["google_ads_id"]
    ads_click = cfg["google_ads_conversion"]["affiliate_click"]
    clarity = cfg["clarity_id"]

    hero = extra.get("hero", f"Is {name} Right For You? Honest Review.")
    sub = extra.get("sub", f"Expert-tested. Unbiased score: {score}/10")
    cta = extra.get("cta", f"Try {name} Free")
    badge = extra.get("badge", "Free Trial Available")
    trust = extra.get("trust", pros)
    urgency = extra.get("urgency", f"Pricing from {price}")
    category = extra.get("category", tool.get("category", "AI Tool"))

    trust_items = "".join(f'<li class="lp-trust-item">✓ {t}</li>' for t in trust)
    pros_items = "".join(f'<li>{p}</li>' for p in pros)
    score_pct = int(score * 10)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{hero} | RankerToolAI</title>
  <meta name="description" content="{sub} Expert {name} review: score {score}/10. {best_for}">
  <meta name="robots" content="noindex">
  <link rel="canonical" href="https://rankertoolai.com/review/{slug}/">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/images/favicon-32.png">

  <!-- GA4 + Google Ads -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga4}', {{'page_title': 'LP-{slug}'}});
    gtag('config', '{ads_id}');
  </script>
  <!-- Microsoft Clarity -->
  <script>(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)}})(window,document,"clarity","script","{clarity}");</script>

  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--brand:#f97316;--brand2:#fbbf24;--bg:#080c18;--bg2:#0d1224;--border:rgba(255,255,255,0.08);--text:#f1f5f9;--muted:#94a3b8;--radius:0.75rem;--green:#22c55e}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}}
    .lp-header{{background:var(--bg2);border-bottom:1px solid var(--border);padding:1rem 1.5rem;display:flex;align-items:center;justify-content:space-between}}
    .lp-logo{{font-size:1.1rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}}
    .lp-badge{{background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.4);color:#4ade80;font-size:0.75rem;font-weight:700;padding:0.25rem 0.75rem;border-radius:9999px}}
    .lp-hero{{max-width:680px;margin:0 auto;padding:3rem 1.5rem 2rem;text-align:center}}
    .lp-category{{font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--brand);margin-bottom:1rem}}
    .lp-hero h1{{font-size:clamp(1.75rem,5vw,2.5rem);font-weight:900;line-height:1.2;margin-bottom:1rem;background:linear-gradient(135deg,#f1f5f9,#94a3b8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
    .lp-hero p{{font-size:1.125rem;color:var(--muted);margin-bottom:2rem}}
    .lp-cta-primary{{display:inline-block;background:linear-gradient(135deg,var(--brand),var(--brand2));color:#000;font-weight:900;font-size:1.1rem;padding:1rem 2.5rem;border-radius:var(--radius);text-decoration:none;transition:opacity 0.2s;width:100%;max-width:380px}}
    .lp-cta-primary:hover{{opacity:0.9}}
    .lp-urgency{{font-size:0.85rem;color:var(--green);margin-top:0.75rem}}
    .lp-trust{{display:flex;flex-wrap:wrap;justify-content:center;gap:0.5rem;margin:1.5rem 0;padding:0;list-style:none}}
    .lp-trust-item{{background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:9999px;padding:0.3rem 0.9rem;font-size:0.8rem;color:var(--muted)}}
    .lp-body{{max-width:680px;margin:0 auto;padding:0 1.5rem 3rem}}
    .lp-score-box{{background:var(--bg2);border:2px solid rgba(249,115,22,0.3);border-radius:var(--radius);padding:1.5rem;display:flex;align-items:center;gap:1.5rem;margin-bottom:2rem}}
    .lp-score-ring{{width:80px;height:80px;border-radius:50%;background:conic-gradient(var(--brand) {score_pct}%,#1e293b 0);display:flex;align-items:center;justify-content:center;flex-shrink:0}}
    .lp-score-inner{{width:64px;height:64px;border-radius:50%;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center}}
    .lp-score-num{{font-size:1.4rem;font-weight:900;color:var(--brand);line-height:1}}
    .lp-score-label{{font-size:0.6rem;color:var(--muted)}}
    .lp-score-text h3{{font-size:1.1rem;font-weight:700;margin-bottom:0.25rem}}
    .lp-score-text p{{font-size:0.875rem;color:var(--muted)}}
    .lp-section{{margin-bottom:2rem}}
    .lp-section h2{{font-size:1.15rem;font-weight:700;margin-bottom:0.75rem;border-bottom:1px solid var(--border);padding-bottom:0.5rem}}
    .lp-pros{{list-style:none;padding:0}}
    .lp-pros li{{padding:0.4rem 0;font-size:0.9rem;color:var(--text);display:flex;gap:0.5rem}}
    .lp-pros li::before{{content:"✓";color:var(--green);font-weight:700;flex-shrink:0}}
    .lp-cta-box{{background:linear-gradient(135deg,rgba(249,115,22,0.08),rgba(251,191,36,0.04));border:2px solid rgba(249,115,22,0.35);border-radius:var(--radius);padding:2rem;text-align:center}}
    .lp-cta-box p{{font-size:0.875rem;color:var(--muted);margin-top:0.75rem}}
    .lp-footer{{text-align:center;padding:1.5rem;border-top:1px solid var(--border);font-size:0.8rem;color:var(--muted)}}
    .lp-footer a{{color:var(--muted);text-decoration:none}}
    .lp-review-link{{display:block;text-align:center;margin-top:1rem;font-size:0.85rem;color:var(--muted);text-decoration:underline}}
    @media(max-width:480px){{.lp-score-box{{flex-direction:column;text-align:center}}}}
  </style>
</head>
<body>

<header class="lp-header">
  <a href="/" class="lp-logo">RankerTool<span style="background:linear-gradient(135deg,#22c55e,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">AI</span></a>
  <span class="lp-badge">{badge}</span>
</header>

<section class="lp-hero">
  <p class="lp-category">{category}</p>
  <h1>{hero}</h1>
  <p>{sub}</p>
  <a href="{go_url}" class="lp-cta-primary" id="cta-hero">{cta} →</a>
  <p class="lp-urgency">{urgency}</p>
  <ul class="lp-trust">{trust_items}</ul>
</section>

<div class="lp-body">

  <div class="lp-score-box">
    <div class="lp-score-ring">
      <div class="lp-score-inner">
        <span class="lp-score-num">{score}</span>
        <span class="lp-score-label">/10</span>
      </div>
    </div>
    <div class="lp-score-text">
      <h3>RankerToolAI Score</h3>
      <p>Tested by experts. Updated {datetime.now().strftime('%B %Y')}.<br>Category: {category}</p>
    </div>
  </div>

  <div class="lp-section">
    <h2>Why {name} Stands Out</h2>
    <ul class="lp-pros">{pros_items}</ul>
  </div>

  <div class="lp-section">
    <h2>Best For</h2>
    <p style="font-size:0.9rem;color:var(--muted)">{best_for}</p>
  </div>

  <div class="lp-cta-box">
    <a href="{go_url}" class="lp-cta-primary" id="cta-bottom">{cta} →</a>
    <p>{urgency}</p>
    <p style="margin-top:0.5rem;font-size:0.8rem">You'll be redirected to {name}'s official website</p>
  </div>

  <a href="{review_url}" class="lp-review-link">Read our full {name} review →</a>

</div>

<footer class="lp-footer">
  <p>© 2026 RankerToolAI · <a href="/affiliate-disclosure/">Affiliate Disclosure</a> · <a href="/privacy-policy/">Privacy</a></p>
  <p style="margin-top:0.4rem">This page may contain affiliate links. We earn a commission at no extra cost to you.</p>
</footer>

<script>
  // Track all CTA clicks as conversions
  document.querySelectorAll('a[href*="/go/"]').forEach(function(el) {{
    el.addEventListener('click', function() {{
      gtag('event', 'conversion', {{
        'send_to': '{ads_click}',
        'value': 1.0,
        'currency': 'USD'
      }});
      gtag('event', 'affiliate_click', {{
        'tool': '{slug}',
        'page_type': 'landing_page',
        'cta_id': el.id || 'unknown'
      }});
    }});
  }});

  // Pass UTM to /go/ links
  (function() {{
    var params = new URLSearchParams(window.location.search);
    var utmKeys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid'];
    document.querySelectorAll('a[href*="/go/"]').forEach(function(el) {{
      try {{
        var url = new URL(el.href);
        utmKeys.forEach(function(k) {{
          if (params.has(k)) url.searchParams.set(k, params.get(k));
        }});
        el.href = url.toString();
      }} catch(e) {{}}
    }});
  }})();
</script>

</body>
</html>"""

def generate(tool_slug=None):
    tools = load_tools()
    cfg = load_config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = [tool_slug] if tool_slug else list(EXTRA_DATA.keys())
    generated = 0

    for slug in targets:
        if slug not in tools:
            print(f"  [SKIP] {slug} not found in tools.json")
            continue
        if slug not in EXTRA_DATA:
            print(f"  [SKIP] {slug} has no landing page copy in EXTRA_DATA")
            continue

        tool = tools[slug]
        extra = EXTRA_DATA[slug]
        html = build_lp(tool, extra, cfg)

        lp_dir = OUT_DIR / slug
        lp_dir.mkdir(parents=True, exist_ok=True)
        (lp_dir / "index.html").write_text(html, encoding="utf-8")
        generated += 1
        print(f"  [OK] /lp/{slug}/  — '{extra['hero'][:50]}...'")

    print(f"\n  Generated {generated} landing pages -> {OUT_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", help="Generate LP for a single tool slug")
    parser.add_argument("--list", action="store_true", help="List available tools")
    args = parser.parse_args()

    if args.list:
        print("Available tools for landing pages:")
        for s in sorted(EXTRA_DATA.keys()):
            print(f"  {s}")
    else:
        print(f"\n[generate_lps] Generating landing pages...\n")
        generate(tool_slug=args.tool)
