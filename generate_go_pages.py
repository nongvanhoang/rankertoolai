#!/usr/bin/env python3
"""Upgrade bare go/ redirect pages to full countdown-timer bridge pages."""
import os, json

BASE = os.path.dirname(__file__)

TOOLS = [
  {
    "slug": "clearscope",
    "name": "Clearscope",
    "dest": "https://www.clearscope.io/",
    "title": "Clearscope — See Pricing & Request a Demo | RankerToolAI",
    "heading": "See Clearscope pricing &mdash; request a demo",
    "sub": "Clearscope is the most accurate NLP content grading tool available. See plans, or request a live demo to evaluate it for your team.",
    "badge_num": "A–F",
    "badge_label": "Content Grade",
    "badge_note": "Grade your content before publishing &middot; Google Docs + WordPress integration",
    "color_bg": "#0a0f1a",
    "color_card": "#0f1626",
    "color_border": "#1a2e4a",
    "color_accent": "#3b82f6",
    "color_accent2": "#2563eb",
    "badge_class": "blue",
    "benefits": [
      ("📊", "A–F Content Grade", "Scores your draft in real-time against top-ranking pages — writers know exactly what to improve"),
      ("🔍", "Best-in-class term reports", "NLP analysis of top SERP results gives writers the most accurate list of terms to include"),
      ("📄", "Google Docs &amp; WordPress", "Grade content without leaving the editor you already use"),
      ("📈", "Content Inventory", "Audits your entire published site and flags pages losing rankings"),
    ],
    "cta_text": "See Clearscope Pricing &rarr;",
    "countdown_note": "Redirecting to Clearscope",
    "footer_links": [
      ("/review/clearscope/", "Full Clearscope review"),
      ("/compare/clearscope-vs-surfer-seo/", "Clearscope vs Surfer SEO"),
      ("/alternatives/clearscope/", "Clearscope alternatives"),
    ],
    "tool_category": "Content SEO",
  },
  {
    "slug": "marketmuse",
    "name": "MarketMuse",
    "dest": "https://www.marketmuse.com/",
    "title": "MarketMuse Free Plan — Redirecting | RankerToolAI",
    "heading": "Try MarketMuse free &mdash; content strategy AI",
    "sub": "MarketMuse maps your entire topic cluster, calculates Personalized Difficulty for your specific domain, and auto-generates content briefs. Free plan available.",
    "badge_num": "Free",
    "badge_label": "Plan Available",
    "badge_note": "Free plan &middot; No credit card &middot; Standard from $149/mo",
    "color_bg": "#0a0f1a",
    "color_card": "#0f1828",
    "color_border": "#1a3048",
    "color_accent": "#6366f1",
    "color_accent2": "#4f46e5",
    "badge_class": "indigo",
    "benefits": [
      ("🗺️", "Topic cluster mapping", "See every subtopic in your niche — find gaps competitors aren't covering"),
      ("🎯", "Personalized Difficulty", "Ranking probability calculated for YOUR domain, not just a generic score"),
      ("📋", "Auto content briefs", "AI-generated briefs with recommended topics, questions, and word counts"),
      ("🔄", "Content Inventory", "Audits your published pages and flags which need refreshing to recover rankings"),
    ],
    "cta_text": "Try MarketMuse Free &rarr;",
    "countdown_note": "Redirecting to MarketMuse",
    "footer_links": [
      ("/review/marketmuse/", "Full MarketMuse review"),
      ("/compare/marketmuse-vs-clearscope/", "MarketMuse vs Clearscope"),
      ("/alternatives/marketmuse/", "MarketMuse alternatives"),
    ],
    "tool_category": "Content Strategy",
  },
  {
    "slug": "anyword",
    "name": "Anyword",
    "dest": "https://anyword.com/?via=rankertoolai",
    "title": "Anyword 7-Day Free Trial — Redirecting | RankerToolAI",
    "heading": "Start your Anyword free trial &mdash; 7 days",
    "sub": "Anyword's Predictive Performance Score shows you which ad copy will convert before you spend a dollar on ads. 7-day free trial, no card required.",
    "badge_num": "7",
    "badge_label": "Day Free Trial",
    "badge_note": "No credit card &middot; Full access to Performance Score &middot; Ad copy generation",
    "color_bg": "#0a0f1a",
    "color_card": "#0f1a24",
    "color_border": "#1a3844",
    "color_accent": "#f97316",
    "color_accent2": "#ea580c",
    "badge_class": "orange",
    "benefits": [
      ("📈", "Predictive Performance Score", "0–100 score estimates conversion rate before you run a single ad — trained on real performance data"),
      ("📣", "Ad copy variants at scale", "Generate dozens of variants per prompt for Meta, Google, and LinkedIn"),
      ("🎙️", "Custom Brand Voice", "Train Anyword on your brand tone so all generated copy stays on-message"),
      ("🔗", "Meta &amp; Google Ads integration", "Push copy directly into live campaigns and pull back real performance data"),
    ],
    "cta_text": "Start Free Trial &rarr;",
    "countdown_note": "Redirecting to Anyword",
    "footer_links": [
      ("/review/anyword/", "Full Anyword review"),
      ("/compare/anyword-vs-jasper/", "Anyword vs Jasper"),
      ("/alternatives/anyword/", "Anyword alternatives"),
    ],
    "tool_category": "AI Marketing Copy",
  },
  {
    "slug": "rytr",
    "name": "Rytr",
    "dest": "https://rytr.me/?via=rankertoolai",
    "title": "Rytr Free Plan — Redirecting | RankerToolAI",
    "heading": "Try Rytr free &mdash; 10,000 chars/month forever",
    "sub": "Rytr's free plan gives you 10,000 characters of AI writing per month — no credit card. The Unlimited plan is $29/month, the cheapest in the industry.",
    "badge_num": "10K",
    "badge_label": "Free Chars/Month",
    "badge_note": "Permanent free plan &middot; No credit card &middot; Unlimited from $29/mo",
    "color_bg": "#0a100f",
    "color_card": "#0f1a18",
    "color_border": "#1a3830",
    "color_accent": "#22c55e",
    "color_accent2": "#16a34a",
    "badge_class": "green",
    "benefits": [
      ("✍️", "40+ use case templates", "Emails, ads, product descriptions, social captions — purpose-built templates for every short-form task"),
      ("🌍", "30+ languages", "Generate content in English, Spanish, French, German, and 27 more languages"),
      ("🎭", "20+ tone presets", "Convincing, witty, formal, persuasive — tone settings that actually change the output"),
      ("💰", "Cheapest unlimited plan", "Unlimited generation at $29/mo — the most affordable serious AI writer available"),
    ],
    "cta_text": "Try Rytr Free &rarr;",
    "countdown_note": "Redirecting to Rytr",
    "footer_links": [
      ("/review/rytr/", "Full Rytr review"),
      ("/compare/rytr-vs-jasper/", "Rytr vs Jasper"),
      ("/alternatives/rytr/", "Rytr alternatives"),
    ],
    "tool_category": "Budget AI Writing",
  },
  {
    "slug": "speechify",
    "name": "Speechify",
    "dest": "https://speechify.com/?via=rankertoolai",
    "title": "Speechify Free Plan — Redirecting | RankerToolAI",
    "heading": "Try Speechify free &mdash; listen to anything",
    "sub": "Speechify turns articles, PDFs, emails, and physical book pages into audio you can listen to hands-free. Premium voices at up to 4.5x speed. Free plan available.",
    "badge_num": "4.5×",
    "badge_label": "Max Listening Speed",
    "badge_note": "Free plan available &middot; Premium from $11.58/mo &middot; All devices",
    "color_bg": "#0a0f1a",
    "color_card": "#0d1628",
    "color_border": "#1a2c50",
    "color_accent": "#8b5cf6",
    "color_accent2": "#7c3aed",
    "badge_class": "purple",
    "benefits": [
      ("🎧", "Premium voices at high speed", "AI voices stay natural and clear even at 2–3x speed — the real use case for power users"),
      ("📷", "OCR book scanning", "Point your camera at a physical page and Speechify reads it aloud — no other app does this as well"),
      ("🌐", "Chrome extension", "Read any webpage, email, or PDF with one click from the browser"),
      ("📱", "All devices", "iOS, Android, Mac, Windows, Chrome — synchronized across every device"),
    ],
    "cta_text": "Try Speechify Free &rarr;",
    "countdown_note": "Redirecting to Speechify",
    "footer_links": [
      ("/review/speechify/", "Full Speechify review"),
      ("/compare/speechify-vs-elevenlabs/", "Speechify vs ElevenLabs"),
      ("/alternatives/speechify/", "Speechify alternatives"),
    ],
    "tool_category": "Text-to-Speech",
  },
  {
    "slug": "playht",
    "name": "Play.ht",
    "dest": "https://play.ht/?via=rankertoolai",
    "title": "Play.ht Free Trial — Redirecting | RankerToolAI",
    "heading": "Try Play.ht free &mdash; 12,500 words included",
    "sub": "Play.ht is the best AI voice generator for podcasters and audiobook creators. 140+ language voices, developer API, and an unlimited-word plan. Free trial available.",
    "badge_num": "12,500",
    "badge_label": "Free Trial Words",
    "badge_note": "No credit card for trial &middot; 140+ languages &middot; Developer API",
    "color_bg": "#0a0c1a",
    "color_card": "#0d1028",
    "color_border": "#1a2050",
    "color_accent": "#6366f1",
    "color_accent2": "#4f46e5",
    "badge_class": "indigo",
    "benefits": [
      ("🎙️", "Ultra-realistic AI voices", "140+ languages and accents — ultra-realistic tier passes most naturalness tests"),
      ("🔌", "Developer API", "Well-documented REST API, up and running in minutes — best in category for programmatic voice generation"),
      ("🎧", "Long-form narration", "Consistent tone across full podcast episodes and audiobook chapters"),
      ("♾️", "Unlimited word plan", "Professional plan at $99/mo for unlimited generation — predictable cost for high-volume creators"),
    ],
    "cta_text": "Start Free Trial &rarr;",
    "countdown_note": "Redirecting to Play.ht",
    "footer_links": [
      ("/review/playht/", "Full Play.ht review"),
      ("/compare/playht-vs-elevenlabs/", "Play.ht vs ElevenLabs"),
      ("/alternatives/playht/", "Play.ht alternatives"),
    ],
    "tool_category": "AI Voice Generator",
  },
  {
    "slug": "codeium",
    "name": "Codeium",
    "dest": "https://codeium.com/",
    "title": "Codeium Free Plan — Redirecting | RankerToolAI",
    "heading": "Install Codeium free &mdash; AI code completion",
    "sub": "Codeium gives individual developers full-featured AI autocomplete and in-IDE chat across 70+ languages and every major IDE — completely free, forever.",
    "badge_num": "Free",
    "badge_label": "Forever for Individuals",
    "badge_note": "No credit card &middot; 70+ languages &middot; All major IDEs",
    "color_bg": "#0a0f12",
    "color_card": "#0d1620",
    "color_border": "#1a2e40",
    "color_accent": "#06b6d4",
    "color_accent2": "#0891b2",
    "badge_class": "cyan",
    "benefits": [
      ("⚡", "Unlimited autocomplete — free", "No daily limits, no credit card, no time restriction — the most generous free code completion plan available"),
      ("💬", "In-IDE chat assistant", "Explain, refactor, and generate code from natural language — also free"),
      ("🖥️", "All major IDEs", "VS Code, JetBrains, Vim, Sublime Text, Emacs, and more"),
      ("🌐", "70+ languages", "Python, JavaScript, TypeScript, Go, Rust, Java, and 65+ more fully supported"),
    ],
    "cta_text": "Install Codeium Free &rarr;",
    "countdown_note": "Redirecting to Codeium",
    "footer_links": [
      ("/review/codeium/", "Full Codeium review"),
      ("/compare/codeium-vs-github-copilot/", "Codeium vs GitHub Copilot"),
      ("/alternatives/codeium/", "Codeium alternatives"),
    ],
    "tool_category": "AI Code Completion",
  },
  {
    "slug": "tabnine",
    "name": "Tabnine",
    "dest": "https://www.tabnine.com/",
    "title": "Tabnine Free Plan — Redirecting | RankerToolAI",
    "heading": "Try Tabnine free &mdash; AI code completion",
    "sub": "Tabnine offers AI code completion with self-hosted and on-premises deployment for enterprises. Free individual plan available, Pro from $9/month.",
    "badge_num": "Free",
    "badge_label": "Plan Available",
    "badge_note": "Free individual plan &middot; Self-hostable &middot; Pro from $9/mo",
    "color_bg": "#0a0f1a",
    "color_card": "#0f1624",
    "color_border": "#1a2a44",
    "color_accent": "#3b82f6",
    "color_accent2": "#2563eb",
    "badge_class": "blue",
    "benefits": [
      ("🔒", "Self-hosted deployment", "Run entirely on your own infrastructure — code never sent to a third-party cloud"),
      ("🏢", "Enterprise compliance", "SOC 2, GDPR, and other certifications relevant to regulated industries"),
      ("⌨️", "Broad IDE support", "VS Code, JetBrains, Visual Studio, Vim, and more — all major editors covered"),
      ("🆓", "Free individual plan", "Full autocomplete capabilities available on the free tier — no time limit"),
    ],
    "cta_text": "Try Tabnine Free &rarr;",
    "countdown_note": "Redirecting to Tabnine",
    "footer_links": [
      ("/review/tabnine/", "Full Tabnine review"),
      ("/compare/tabnine-vs-codeium/", "Tabnine vs Codeium"),
      ("/alternatives/tabnine/", "Tabnine alternatives"),
    ],
    "tool_category": "AI Code Completion",
  },
  {
    "slug": "mistral",
    "name": "Mistral AI",
    "dest": "https://mistral.ai/",
    "title": "Mistral AI Le Chat Free — Redirecting | RankerToolAI",
    "heading": "Try Le Chat free &mdash; Mistral AI",
    "sub": "Mistral AI's Le Chat is a free, capable AI assistant powered by open-weight models. API access on La Plateforme has industry-competitive pricing. Free, no card needed.",
    "badge_num": "Free",
    "badge_label": "Le Chat Plan",
    "badge_note": "No credit card &middot; Open-weight models &middot; EU-based (France)",
    "color_bg": "#0a0f12",
    "color_card": "#0e1820",
    "color_border": "#1a3038",
    "color_accent": "#f59e0b",
    "color_accent2": "#d97706",
    "badge_class": "amber",
    "benefits": [
      ("🇪🇺", "EU-based &amp; open-weight", "France-based provider — GDPR-friendly, with self-hostable open-weight model releases"),
      ("💰", "Competitive API pricing", "La Plateforme API pricing beats major competitors at similar quality benchmarks"),
      ("🧠", "Strong reasoning &amp; coding", "Competitive on coding and reasoning benchmarks with much larger closed-weight models"),
      ("🆓", "Genuinely free tier", "Le Chat Pro features available on a real free plan — not a time-limited trial"),
    ],
    "cta_text": "Try Le Chat Free &rarr;",
    "countdown_note": "Redirecting to Mistral AI",
    "footer_links": [
      ("/review/mistral/", "Full Mistral AI review"),
      ("/compare/mistral-vs-chatgpt/", "Mistral vs ChatGPT"),
      ("/alternatives/mistral/", "Mistral alternatives"),
    ],
    "tool_category": "AI Assistant",
  },
]

ACCENT_VARS = {
  "blue":   ("#3b82f6", "#2563eb", "#60a5fa"),
  "indigo": ("#6366f1", "#4f46e5", "#818cf8"),
  "orange": ("#f97316", "#ea580c", "#fb923c"),
  "green":  ("#22c55e", "#16a34a", "#4ade80"),
  "purple": ("#8b5cf6", "#7c3aed", "#a78bfa"),
  "cyan":   ("#06b6d4", "#0891b2", "#22d3ee"),
  "amber":  ("#f59e0b", "#d97706", "#fbbf24"),
}

def render(t):
    a1, a2, a3 = ACCENT_VARS.get(t["badge_class"], ("#f97316", "#ea580c", "#fbbf24"))
    benefit_html = "\n".join(
        f'''    <div class="benefit">
      <span class="icon">{b[0]}</span>
      <span><strong>{b[1]}</strong> &mdash; {b[2]}</span>
    </div>'''
        for b in t["benefits"]
    )
    footer_links = " &middot; ".join(f'<a href="{l[0]}">{l[1]}</a>' for l in t["footer_links"])
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t["title"]}</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="canonical" href="https://rankertoolai.com/go/{t["slug"]}/">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-81KB8ECCVF"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-81KB8ECCVF');
  </script>
  <script async src="/assets/js/pint.js"></script>

  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: {t["color_bg"]};
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .card {{
      background: {t["color_card"]};
      border: 1px solid {t["color_border"]};
      border-radius: 16px;
      max-width: 520px;
      width: 100%;
      padding: 40px 36px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }}
    .logo-row {{
      display: flex; align-items: center; justify-content: center;
      gap: 12px; margin-bottom: 24px; font-size: 13px; color: #888;
    }}
    .arrow {{ font-size: 18px; color: #555; }}
    .heading {{ font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 8px; line-height: 1.3; }}
    .sub {{ color: #aaa; font-size: 14px; margin-bottom: 28px; line-height: 1.6; }}

    .badge {{
      background: linear-gradient(135deg, {a2}, {a1});
      border-radius: 12px;
      padding: 22px 24px;
      margin-bottom: 28px;
    }}
    .badge-num {{ font-size: 48px; font-weight: 900; color: #fff; line-height: 1; }}
    .badge-label {{ font-size: 17px; font-weight: 700; color: rgba(255,255,255,0.9); margin-top: 4px; }}
    .badge-note {{ font-size: 13px; color: rgba(255,255,255,0.75); margin-top: 8px; }}

    .benefits {{ text-align: left; margin-bottom: 28px; }}
    .benefit {{
      display: flex; align-items: flex-start; gap: 10px;
      padding: 8px 0; border-bottom: 1px solid {t["color_border"]};
      color: #ccc; font-size: 14px; line-height: 1.5;
    }}
    .benefit:last-child {{ border-bottom: none; }}
    .benefit .icon {{ font-size: 18px; flex-shrink: 0; margin-top: 1px; }}

    .cta-btn {{
      display: block; width: 100%;
      background: linear-gradient(135deg, {a1}, {a2});
      color: #fff; font-size: 16px; font-weight: 700;
      padding: 16px 24px; border-radius: 10px; text-decoration: none;
      border: none; cursor: pointer;
      transition: opacity 0.2s, transform 0.15s;
      margin-bottom: 12px;
    }}
    .cta-btn:hover {{ opacity: 0.92; transform: translateY(-1px); }}

    .countdown-row {{ font-size: 13px; color: #666; }}
    .countdown-row span {{ color: {a3}; font-weight: 600; }}
    .skip-link {{
      color: #666; font-size: 12px; text-decoration: underline; cursor: pointer;
      background: none; border: none; display: block; margin-top: 8px;
    }}
    .skip-link:hover {{ color: #aaa; }}
    .footer-note {{ margin-top: 24px; font-size: 11px; color: #555; line-height: 1.6; }}
    .footer-note a {{ color: {a1}; text-decoration: none; }}
  </style>
</head>
<body>

<div class="card">
  <div class="logo-row">
    <span>RankerToolAI</span>
    <span class="arrow">&#8594;</span>
    <span>{t["name"]}</span>
  </div>

  <h1 class="heading">{t["heading"]}</h1>
  <p class="sub">{t["sub"]}</p>

  <div class="badge">
    <div class="badge-num">{t["badge_num"]}</div>
    <div class="badge-label">{t["badge_label"]}</div>
    <div class="badge-note">{t["badge_note"]}</div>
  </div>

  <div class="benefits">
{benefit_html}
  </div>

  <a id="ctaBtn" href="{t["dest"]}" rel="nofollow sponsored" class="cta-btn">
    {t["cta_text"]}
  </a>
  <div class="countdown-row">{t["countdown_note"]} in <span id="timer">5</span> seconds</div>
  <button class="skip-link" onclick="goNow()">Skip countdown</button>

  <div class="footer-note">
    {footer_links}
  </div>
</div>

<script>
(function() {{
  var DEST_BASE = '{t["dest"]}';
  var countdown = 5;
  var redirected = false;

  var params = new URLSearchParams(window.location.search);
  var ref = document.referrer ? new URL(document.referrer).pathname : 'direct';
  var subid = params.get('ref') || ref.replace(/\\//g,'_').replace(/^_|_$/g,'') || 'direct';

  var dest = new URL(DEST_BASE);
  ['utm_source','utm_medium','utm_campaign','utm_content','gclid'].forEach(function(k){{
    if (params.has(k)) dest.searchParams.set(k, params.get(k));
  }});
  dest.searchParams.set('ref', subid);
  var finalUrl = dest.toString();

  document.getElementById('ctaBtn').href = finalUrl;

  if (typeof gtag !== 'undefined') {{
    gtag('event', 'affiliate_click', {{ tool: '{t["slug"]}', source_path: ref, sub_id: subid, page_type: 'bridge' }});
  }}

  var timerEl = document.getElementById('timer');
  var interval = setInterval(function() {{
    countdown--;
    timerEl.textContent = countdown;
    if (countdown <= 0) {{ clearInterval(interval); goNow(); }}
  }}, 1000);

  window.goNow = function() {{
    if (redirected) return;
    redirected = true;
    clearInterval(interval);
    window.location.replace(finalUrl);
  }};
}})();
</script>
</body>
</html>
'''
    outdir = os.path.join(BASE, "go", t["slug"])
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote go/{t['slug']}/index.html ({len(page.splitlines())} lines)")

if __name__ == "__main__":
    for t in TOOLS:
        render(t)
