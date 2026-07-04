# inject_sticky_cta.py
# Add sticky CTA bar to alternatives pages that are missing it.

import os, re

HTML_DIR = os.path.join(os.path.dirname(__file__), "html")
ALT_DIR  = os.path.join(HTML_DIR, "alternatives")

# ── CTA mapping: slug → (brand, tagline, go_url) ─────────────────────────────
CTAS = {
    # Voice → ElevenLabs
    "speechify": ("ElevenLabs", "best Speechify alternative · 10,000 chars/mo FREE", "/go/elevenlabs/"),
    "playht":    ("ElevenLabs", "better voice realism than Play.ht · free plan",      "/go/elevenlabs/"),
    "elevenlabs":("Murf AI",    "best ElevenLabs alternative · built-in video studio", "/go/murf/"),
    # SEO
    "semrush":    ("SE Ranking", "14-day free trial · no credit card · from $65/mo",       "/go/se-ranking/"),
    "mangools":   ("SE Ranking", "14-day free trial · no credit card · 5-tool SEO suite",  "/go/se-ranking/"),
    "se-ranking": ("Mangools",   "10-day free trial · keyword research from $29/mo",        "/go/mangools/"),
    "surfer-seo": ("SE Ranking", "best budget Surfer SEO alternative · 14-day free trial",  "/go/se-ranking/"),
    "clearscope": ("Surfer SEO", "best Clearscope alternative · save 50%+ · free trial",    "/go/surfer-seo/"),
    "marketmuse": ("Surfer SEO", "best MarketMuse alternative · save 70%+ · free trial",    "/go/surfer-seo/"),
    "frase":      ("Surfer SEO", "best Frase alternative · more features at $89/mo",        "/go/surfer-seo/"),
    # AI Writing
    "jasper":     ("Writesonic", "best Jasper alternative · 10,000 words/month FREE",       "/go/writesonic/"),
    "writesonic": ("Jasper",     "7-day free trial · unlimited words during trial",          "/go/jasper/"),
    "copy-ai":    ("Jasper",     "7-day free trial · best AI writing alternative",           "/go/jasper/"),
    "rytr":       ("Writesonic", "best Rytr alternative · 10,000 words/month FREE",          "/go/writesonic/"),
    "anyword":    ("Jasper",     "7-day free trial · best AI writer for marketers",          "/go/jasper/"),
    "grammarly":  ("Jasper",     "7-day free trial · AI writer + grammar in one",            "/go/jasper/"),
    # AI Chat
    "chatgpt":    ("Julius AI",  "best data analysis AI · free plan + code: 25RQK3UL",      "/go/julius-ai/"),
    "gemini":     ("Julius AI",  "10% off first Pro payment · code: 25RQK3UL",              "/go/julius-ai/"),
    "deepseek":   ("Julius AI",  "best AI data analyst · free plan available",              "/go/julius-ai/"),
    "mistral":    ("Julius AI",  "best AI data analyst · free plan available",              "/go/julius-ai/"),
    # AI Coding
    "cursor":     ("GitHub Copilot", "2,000 completions/month FREE · 1.8M+ devs use it",   "/go/github-copilot/"),
    "codeium":    ("Cursor",         "#1 AI code editor · free plan · 2k completions/mo",   "/go/cursor/"),
    "tabnine":    ("Cursor",         "#1 AI code editor · better AI · free plan",            "/go/cursor/"),
    # AI Image
    "midjourney": ("Ideogram",   "best free alternative · daily free generations · no Discord", "/go/ideogram/"),
    # Productivity
    "julius-ai":  ("Julius AI",  "10% off first payment with code: 25RQK3UL · free plan",  "/go/julius-ai/"),
    "notion":     ("Notion AI",  "20 free AI responses · no credit card required",          "/go/notion/"),
    # Other
    "pictory":    ("ElevenLabs", "add AI voiceover to your videos · 10,000 chars/mo FREE", "/go/elevenlabs/"),
    "deepseek":   ("Julius AI",  "best AI data analyst · free plan available",              "/go/julius-ai/"),
}

CSS_INJECT = """\
    #back-to-top{display:none;position:fixed;bottom:80px;right:1.5rem;width:44px;height:44px;border-radius:50%;background:var(--color-primary);color:white;align-items:center;justify-content:center;font-size:1.25rem;cursor:pointer;border:none;box-shadow:var(--shadow-lg);z-index:50;}
    .sticky-cta{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(90deg,#0a0f1e,#0d1528);border-top:1px solid rgba(249,115,22,0.3);padding:0.75rem 1.5rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;z-index:100;transform:translateY(100%);transition:transform 0.3s ease;backdrop-filter:blur(12px);}
    .sticky-cta.visible{transform:translateY(0);}
    .sticky-cta-btn{flex-shrink:0;padding:0.55rem 1.25rem;background:linear-gradient(135deg,#f97316,#fbbf24);color:white;font-weight:700;border-radius:var(--radius);text-decoration:none;font-size:0.85rem;white-space:nowrap;}
    .sticky-cta-btn:hover{color:white;text-decoration:none;}"""

JS_INJECT = """\
  var stickyCta = document.getElementById('sticky-cta');
  window.addEventListener('scroll', function() {
    if (window.scrollY > 300) stickyCta.classList.add('visible');
    else stickyCta.classList.remove('visible');
  });"""

def make_cta_html(brand, tagline, go_url):
    return (
        f'<button id="back-to-top" aria-label="Back to top" style="display:none;">↑</button>\n'
        f'<div class="sticky-cta" id="sticky-cta">\n'
        f'  <div style="font-size:0.875rem;color:#94a3b8;"><strong style="color:#f97316;">{brand}</strong> — {tagline}</div>\n'
        f'  <a href="{go_url}" class="sticky-cta-btn" rel="nofollow sponsored" target="_blank">Try Free →</a>\n'
        f'</div>\n'
    )

def inject(slug, html, brand, tagline, go_url):
    # 1. Replace old back-to-top CSS + add sticky CTA CSS before </style>
    old_back = r'#back-to-top\{[^}]+\}'
    html = re.sub(old_back, '', html)
    html = html.replace('</style>', CSS_INJECT + '\n  </style>', 1)

    # 2. Insert sticky CTA HTML right after <body>
    cta_div = make_cta_html(brand, tagline, go_url)
    html = re.sub(r'(<body[^>]*>)\s*(<button[^>]+back-to-top[^>]+>[^<]*</button>)?',
                  r'\1\n' + cta_div, html, count=1)

    # 3. Add scroll JS before closing </script> in the inline script block at end
    # Find last <script> block and inject before its closing
    # Pattern: the back-to-top / nav-toggle JS at end of file
    if 'stickyCta' not in html:
        html = html.replace(
            "  tog.addEventListener('click', function() { var open = menu.classList.toggle('is-open'); tog.setAttribute('aria-expanded', open); });",
            "  tog.addEventListener('click', function() { var open = menu.classList.toggle('is-open'); tog.setAttribute('aria-expanded', open); });\n" + JS_INJECT
        )

    return html


fixed = []
skipped = []

for slug, (brand, tagline, go_url) in CTAS.items():
    path = os.path.join(ALT_DIR, slug, "index.html")
    if not os.path.exists(path):
        skipped.append(f"NOT FOUND: {slug}")
        continue

    html = open(path, encoding='utf-8').read()

    if 'sticky-cta' in html:
        skipped.append(f"ALREADY HAS: {slug}")
        continue

    html_new = inject(slug, html, brand, tagline, go_url)
    open(path, 'w', encoding='utf-8').write(html_new)
    fixed.append(slug)
    print(f"OK {slug} -> {brand}")

print(f"\nDone: {len(fixed)} fixed, {len(skipped)} skipped")
for s in skipped:
    print(f"  {s}")
