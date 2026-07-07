#!/usr/bin/env python3
"""Inject affiliate CTA section into blog posts and category pages missing affiliate links.
Inserts a 'Recommended Tools' box before </main>.
"""
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")

HTML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html")

def make_cta_box(heading, tools):
    cards = ""
    for slug, name, price, desc in tools:
        cards += f"""        <a href="{slug}" rel="nofollow sponsored" target="_blank" style="display:block;padding:0.9rem;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:8px;text-decoration:none;" onmouseover="this.style.borderColor='rgba(249,115,22,0.4)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'">
          <div style="font-weight:700;color:#f1f5f9;font-size:0.9rem;margin-bottom:0.2rem;">{name}</div>
          <div style="color:rgba(148,163,184,0.7);font-size:0.8rem;line-height:1.4;">{desc}</div>
          <div style="color:#f97316;font-size:0.8rem;font-weight:600;margin-top:0.35rem;">{price} &rarr;</div>
        </a>\n"""
    return f"""
  <div style="padding:0 0 2rem;">
    <div style="border:1px solid rgba(249,115,22,0.25);border-radius:12px;padding:1.5rem;background:rgba(249,115,22,0.04);">
      <h3 style="color:#f1f5f9;font-size:1rem;font-weight:800;margin:0 0 1rem;">{heading}</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:0.75rem;">
{cards.rstrip()}
      </div>
    </div>
  </div>
"""

# Define CTA content per page
INJECTIONS = {
    # Blog posts
    "blog/how-to-use-ai-for-seo": {
        "heading": "Top AI SEO Tools — Get Started",
        "tools": [
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Best for content optimization & NLP scoring"),
            ("/go/semrush/", "Semrush", "$129.95/mo", "Full SEO platform — 7-day free trial"),
            ("/go/frase/", "Frase", "$45/mo", "AI content briefs from top SERP results"),
            ("/go/se-ranking/", "SE Ranking", "$52/mo", "Agency SEO at 60% less than Semrush"),
        ]
    },
    "blog/ai-tools-for-small-business": {
        "heading": "Best AI Tools for Small Business — Try Free",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "AI writing for all marketing content"),
            ("/go/semrush/", "Semrush", "$129.95/mo", "SEO & competitor intelligence"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "Marketing copy at scale"),
            ("/go/canva-ai/", "Canva AI", "Free+", "AI design for non-designers"),
        ]
    },
    "blog/best-ai-tools-for-students": {
        "heading": "Top AI Tools for Students — Try Free",
        "tools": [
            ("/go/notion/", "Notion AI", "$8/mo", "Notes, research & AI writing in one"),
            ("/go/grammarly/", "Grammarly", "Free+", "AI proofreading & writing improvement"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "AI essays, summaries & content"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "AI writing — free plan available"),
        ]
    },
    "blog/best-free-ai-image-generators": {
        "heading": "AI Image Tools — Try Now",
        "tools": [
            ("/go/midjourney/", "Midjourney", "$10/mo", "Best quality AI image generation"),
            ("/go/canva-ai/", "Canva AI", "Free+", "AI design — Magic Design & text-to-image"),
            ("/go/adobe-firefly/", "Adobe Firefly", "Free+", "IP-safe AI images with Photoshop"),
            ("/go/ideogram/", "Ideogram", "Free+", "Best free text-in-image AI generator"),
        ]
    },
    "blog/chatgpt-vs-claude-for-writing": {
        "heading": "Best AI Writing Tools — Try Free",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Best brand voice AI writer — 7-day trial"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "Budget AI writing with SEO mode"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "AI workflows for content teams"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Optimize AI content to actually rank"),
        ]
    },
    "blog/chatgpt-vs-claude-vs-gemini": {
        "heading": "Top AI Tools That Enhance ChatGPT, Claude & Gemini",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Consistent brand voice across all AI output"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "Web-connected AI writer for SEO content"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Optimize any AI article to rank on Google"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "Automated content workflows at scale"),
        ]
    },
    "blog/deepseek-vs-chatgpt": {
        "heading": "Best AI Tools to Complement ChatGPT & DeepSeek",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Best AI writer for content teams"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "AI writing with live web search"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Turn AI drafts into ranking articles"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "AI marketing workflow automation"),
        ]
    },
    "blog/how-to-use-chatgpt": {
        "heading": "Tools That Make ChatGPT Even More Powerful",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Brand-consistent AI writing at scale"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "ChatGPT alternative with web access"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Optimize ChatGPT content to rank"),
            ("/go/frase/", "Frase", "$45/mo", "AI content briefs before you write"),
        ]
    },
    "blog/how-to-use-midjourney": {
        "heading": "More AI Image Tools to Try",
        "tools": [
            ("/go/canva-ai/", "Canva AI", "Free+", "AI design — easier than Midjourney for graphics"),
            ("/go/adobe-firefly/", "Adobe Firefly", "Free+", "IP-safe AI images inside Photoshop"),
            ("/go/ideogram/", "Ideogram", "Free+", "Best free Midjourney alternative"),
            ("/go/stable-diffusion/", "Stable Diffusion", "Free", "Open-source, unlimited image generation"),
        ]
    },
    "blog/how-to-use-perplexity-ai": {
        "heading": "More AI Research & Writing Tools",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Turn Perplexity research into full articles"),
            ("/go/writesonic/", "Writesonic", "$16/mo", "AI writing with built-in web search"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Optimize articles for Google ranking"),
            ("/go/frase/", "Frase", "$45/mo", "AI-powered content briefs from SERP data"),
        ]
    },
    "blog/how-to-use-claude-ai": {
        "heading": "More AI Tools to Supercharge Your Workflow",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Claude alternative with Brand Voice features"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Optimize Claude content to rank on Google"),
            ("/go/notion/", "Notion AI", "$8/mo", "Combine Claude-style AI with your notes"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "AI marketing workflows and automation"),
        ]
    },
    "blog/best-ai-tools-for-solopreneurs": {
        "heading": "Top AI Tools for Solopreneurs — Start Free",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "Brand voice AI — write content 10x faster"),
            ("/go/semrush/", "Semrush", "$129.95/mo", "SEO platform — 7-day free trial"),
            ("/go/notion/", "Notion AI", "$8/mo", "All-in-one workspace + AI assistant"),
            ("/go/canva-ai/", "Canva AI", "Free+", "AI design for social & marketing assets"),
        ]
    },
    "blog/best-ai-tools-for-freelancers": {
        "heading": "Best AI Tools for Freelancers — Try Free",
        "tools": [
            ("/go/jasper/", "Jasper AI", "$39/mo", "AI writing that adapts to client brand voice"),
            ("/go/grammarly/", "Grammarly", "Free+", "AI proofreading for every deliverable"),
            ("/go/surfer-seo/", "Surfer SEO", "$89/mo", "Deliver content that actually ranks"),
            ("/go/copy-ai/", "Copy.ai", "$49/mo", "AI workflows for marketing freelancers"),
        ]
    },
    # Category pages
    "category/ai-video": {
        "heading": "Best AI Video Tools — Try Free",
        "tools": [
            ("/go/synthesia/", "Synthesia", "From $147/mo", "AI video from text — 140+ languages"),
            ("/go/heygen/", "HeyGen", "Free+", "AI avatar videos for marketing"),
            ("/go/runway/", "Runway", "Free+", "AI video generation & editing"),
            ("/go/elevenlabs/", "ElevenLabs", "$5/mo", "Human-quality AI voiceover"),
        ]
    },
    "category/ai-image": {
        "heading": "Best AI Image Tools — Try Now",
        "tools": [
            ("/go/midjourney/", "Midjourney", "$10/mo", "Best quality AI image generation"),
            ("/go/canva-ai/", "Canva AI", "Free+", "AI design for non-designers"),
            ("/go/adobe-firefly/", "Adobe Firefly", "Free+", "IP-safe AI with Photoshop integration"),
            ("/go/stable-diffusion/", "Stable Diffusion", "Free", "Open-source, unlimited generation"),
        ]
    },
}

def inject_cta(slug, config):
    path = os.path.join(HTML_DIR, slug, "index.html")
    if not os.path.exists(path):
        print(f"  SKIP (not found): {slug}")
        return False

    html = open(path, encoding='utf-8', errors='replace').read()

    # Check if already has affiliate links
    existing_aff = len(re.findall(r'href=["\'][^"\']*\/go\/[^"\']+["\']', html))
    if existing_aff >= 3:
        print(f"  SKIP  {slug}: already has {existing_aff} affiliate links")
        return False

    cta_html = make_cta_box(config["heading"], config["tools"])

    # Inject before </main>
    if "</main>" not in html:
        print(f"  SKIP  {slug}: no </main> found")
        return False

    new_html = html.replace("</main>", cta_html + "</main>", 1)

    if new_html != html:
        open(path, 'w', encoding='utf-8').write(new_html)
        new_count = len(re.findall(r'href=["\'][^"\']*\/go\/[^"\']+["\']', new_html))
        print(f"  FIXED {slug}: {existing_aff} → {new_count} affiliate links")
        return True
    return False

print(f"Injecting affiliate CTAs into {len(INJECTIONS)} pages...")
fixed = 0
for slug, config in INJECTIONS.items():
    if inject_cta(slug, config):
        fixed += 1
print(f"\nDone. Fixed {fixed}/{len(INJECTIONS)} pages.")
