#!/usr/bin/env python3
"""
Inject premium upgrades into all review pages:
 - Updated badge (styled green chip next to date)
 - Related Tools section (before Final Verdict)
 - Newsletter inline section (after Final Verdict)
"""
import re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REVIEW_DIR = Path(__file__).parent / "html" / "review"

# Related tools data per slug
RELATED = {
    "chatgpt":       [("claude","Claude","9.2"),("gemini","Gemini","8.7"),("perplexity","Perplexity AI","8.8")],
    "claude":        [("chatgpt","ChatGPT","8.8"),("gemini","Gemini","8.7"),("deepseek","DeepSeek","9.0")],
    "gemini":        [("chatgpt","ChatGPT","8.8"),("claude","Claude","9.2"),("perplexity","Perplexity AI","8.8")],
    "deepseek":      [("chatgpt","ChatGPT","8.8"),("claude","Claude","9.2"),("gemini","Gemini","8.7")],
    "grok":          [("chatgpt","ChatGPT","8.8"),("claude","Claude","9.2"),("deepseek","DeepSeek","9.0")],
    "perplexity":    [("chatgpt","ChatGPT","8.8"),("claude","Claude","9.2"),("gemini","Gemini","8.7")],
    "midjourney":    [("stable-diffusion","Stable Diffusion","8.9"),("canva-ai","Canva AI","8.7"),("runway","Runway ML","9.0")],
    "stable-diffusion":[("midjourney","Midjourney","9.1"),("canva-ai","Canva AI","8.7"),("runway","Runway ML","9.0")],
    "runway":        [("midjourney","Midjourney","9.1"),("stable-diffusion","Stable Diffusion","8.9"),("canva-ai","Canva AI","8.7")],
    "canva-ai":      [("midjourney","Midjourney","9.1"),("stable-diffusion","Stable Diffusion","8.9"),("runway","Runway ML","9.0")],
    "cursor":        [("github-copilot","GitHub Copilot","9.1"),("windsurf","Windsurf","8.9"),("claude","Claude","9.2")],
    "windsurf":      [("cursor","Cursor","9.2"),("github-copilot","GitHub Copilot","9.1"),("claude","Claude","9.2")],
    "github-copilot":[("cursor","Cursor","9.2"),("windsurf","Windsurf","8.9"),("chatgpt","ChatGPT","8.8")],
    "elevenlabs":    [("otter-ai","Otter.ai","8.7"),("notion","Notion AI","8.9"),("canva-ai","Canva AI","8.7")],
    "jasper":        [("writesonic","Writesonic","8.7"),("surfer-seo","Surfer SEO","9.0"),("semrush","Semrush","9.1")],
    "writesonic":    [("jasper","Jasper AI","8.9"),("surfer-seo","Surfer SEO","9.0"),("semrush","Semrush","9.1")],
    "notion":        [("otter-ai","Otter.ai","8.7"),("cursor","Cursor","9.2"),("chatgpt","ChatGPT","8.8")],
    "otter-ai":      [("notion","Notion AI","8.9"),("claude","Claude","9.2"),("chatgpt","ChatGPT","8.8")],
    "semrush":       [("surfer-seo","Surfer SEO","9.0"),("jasper","Jasper AI","8.9"),("hubspot","HubSpot AI","8.2")],
    "hubspot":       [("semrush","Semrush","9.1"),("jasper","Jasper AI","8.9"),("writesonic","Writesonic","8.7")],
    "surfer-seo":    [("semrush","Semrush","9.1"),("jasper","Jasper AI","8.9"),("writesonic","Writesonic","8.7")],
    "adobe-firefly": [("midjourney","Midjourney","9.1"),("stable-diffusion","Stable Diffusion","8.9"),("canva-ai","Canva AI","8.7")],
}

def related_html(slug):
    tools = RELATED.get(slug, [])
    if not tools:
        return ""
    cards = ""
    for (sl, name, score) in tools:
        cards += f"""    <a href="/review/{sl}/" style="flex:1;min-width:140px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1rem;text-decoration:none;color:inherit;transition:border-color 0.2s,background 0.2s;" onmouseover="this.style.borderColor='rgba(249,115,22,0.4)';this.style.background='rgba(249,115,22,0.05)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.08)';this.style.background='rgba(255,255,255,0.03)'">
      <img src="/assets/images/logos/{sl}.png" onerror="this.style.display='none'" alt="{name}" style="width:36px;height:36px;object-fit:contain;border-radius:8px;margin-bottom:0.5rem;">
      <div style="font-weight:700;font-size:0.875rem;margin-bottom:0.2rem;">{name}</div>
      <div style="font-size:0.75rem;color:#f97316;font-weight:800;">{score}/10</div>
    </a>
"""
    return f"""
  <!-- Related Tools -->
  <div class="feature-section" style="margin-top:2rem;">
    <h2 style="font-size:1.05rem;margin-bottom:1rem;">Related Tool Reviews</h2>
    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
{cards.rstrip()}
    </div>
  </div>
"""

NEWSLETTER_HTML = """
  <!-- Newsletter -->
  <div class="newsletter-section">
    <h3>Get Our Weekly AI Tool Roundup</h3>
    <p>New reviews, rankings &amp; deals — every Thursday. No spam, unsubscribe anytime.</p>
    <form class="newsletter-form" action="https://formsubmit.co/nongvanhoang1608@gmail.com" method="POST">
      <input type="hidden" name="_subject" value="Newsletter Signup — RankerToolAI">
      <input type="hidden" name="_next" value="https://rankertoolai.com/?subscribed=1">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="source" value="inline_newsletter">
      <input type="email" name="email" placeholder="your@email.com" required autocomplete="email">
      <button type="submit">Subscribe Free →</button>
    </form>
  </div>
"""

updated = 0

for review_page in sorted(REVIEW_DIR.iterdir()):
    html_file = review_page / "index.html"
    if not html_file.exists() or review_page.name == "index.html":
        continue

    slug = review_page.name
    content = html_file.read_text(encoding="utf-8")
    new_content = content

    # 1. Style the "Updated" date text → replace inline grey span with badge
    new_content = re.sub(
        r'<span style="color:var\(--color-text-muted\);font-size:0\.875rem;">(Updated [^<]+)</span>',
        r'<span style="color:var(--color-text-muted);font-size:0.875rem;">\1</span> <span class="updated-badge">Fresh 2026</span>',
        new_content,
        count=1
    )

    # 2. Inject Related Tools before Final Verdict block (only if not already present)
    if "Related Tool Reviews" not in new_content:
        rel_html = related_html(slug)
        if rel_html:
            if "<!-- Final Verdict -->" in new_content:
                new_content = new_content.replace("<!-- Final Verdict -->", rel_html + "<!-- Final Verdict -->", 1)
            elif re.search(r'<h2[^>]*>(?:Our Verdict|Final Verdict)', new_content):
                new_content = re.sub(
                    r'(<h2[^>]*>(?:Our Verdict|Final Verdict))',
                    rel_html + r'\1',
                    new_content,
                    count=1
                )

    # 3. Inject Newsletter (before </article> or before </main> as fallback)
    if "newsletter-section" not in new_content:
        if '</article>' in new_content:
            new_content = new_content.replace('</article>', NEWSLETTER_HTML + '\n</article>', 1)
        else:
            new_content = new_content.replace('</main>', NEWSLETTER_HTML + '\n</main>', 1)

    if new_content != content:
        html_file.write_text(new_content, encoding="utf-8")
        updated += 1
        print(f"  updated  {slug}")
    else:
        print(f"  skip     {slug}")

print(f"\nDone: {updated} review pages updated")
