#!/usr/bin/env python3
"""Fix meta description length warnings across the site.
Too short < 130 chars → replace with crafted description.
Too long > 160 chars → truncate at word boundary.
Title contains '| RankerToolAI' suffix → remove it.
"""
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")

HTML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html")

# Hardcoded improved descriptions for pages that are too short
IMPROVED_DESCS = {
    "review/grok": "Grok AI review 2026: We tested xAI's Grok 3 on reasoning, coding, and creativity tasks. Score 8.4/10. Pricing, free access, and honest verdict vs ChatGPT.",
    "review/jasper": "Jasper AI review 2026: We tested every template, Brand Voice, and long-form feature across 3 weeks. Score 9.0/10. Is it worth $39/month? Honest verdict inside.",
    "review/adobe-firefly": "Adobe Firefly review 2026: IP-safe AI image generation with Photoshop integration tested. Score 8.6/10. Pricing, features, and is it worth it for creatives.",
    "review/deepseek": "DeepSeek R1 review 2026: benchmark scores, real performance tests, free API access, pricing vs ChatGPT, and honest verdict on safety and capabilities.",
    "review/stable-diffusion": "Stable Diffusion review 2026: the best open-source AI image generator. Free, unlimited images, fully customizable. Score 8.9/10. Full setup guide included.",
    "compare/midjourney-vs-firefly": "Midjourney vs Adobe Firefly 2026: image quality, commercial safety, pricing, and use cases compared head-to-head. Which AI image generator wins in 2026?",
    "compare/notion-vs-chatgpt": "Notion AI vs ChatGPT 2026: which is better for productivity? Side-by-side comparison of features, pricing, and real-world use cases for teams and solo users.",
    "compare/perplexity-vs-google": "Perplexity AI vs Google Search 2026: which gives better answers for research? Honest comparison on accuracy, source citations, and everyday search quality.",
    "compare/surfer-seo-vs-clearscope": "Surfer SEO vs Clearscope 2026: which content optimizer ranks your content faster? Compared on NLP scoring accuracy, pricing, integrations, and ease of use.",
    "alternatives/elevenlabs": "8 best ElevenLabs alternatives in 2026: Murf AI, Play.ht, Speechify, Resemble AI, and more. Compared by voice quality, pricing, and language support.",
    "alternatives/gemini": "8 best Google Gemini alternatives in 2026: ChatGPT, Claude, Perplexity, and more. Compared by reasoning ability, speed, pricing, and specific use case fit.",
    "alternatives/surfer-seo": "8 best Surfer SEO alternatives in 2026: Clearscope, Frase, Semrush, and more. Compared by content scoring accuracy, pricing, integrations, and team features.",
    "best/ai-coding-tools": "Best AI coding tools 2026: Cursor, GitHub Copilot, Windsurf, and more — ranked by code quality, autocomplete speed, language support, and productivity gain.",
    "best/ai-data-tools": "Best AI data analysis tools 2026: Julius AI, ChatGPT Code Interpreter, and more — ranked by ease of use, accuracy, chart quality, and value for money.",
    "best/ai-marketing-tools": "Best AI marketing tools 2026: Jasper, Writesonic, Semrush, and more — ranked by ROI, ease of adoption, and measurable impact on traffic and conversion rates.",
    "best/ai-productivity-tools": "Best AI productivity tools 2026: Claude, Notion AI, Otter.ai, and more — ranked by time saved per week, ease of adoption, and impact on daily workflows.",
    "best/ai-tools-for-developers": "Best AI tools for developers 2026: Cursor, GitHub Copilot, Claude, and more — ranked by code completion quality, language support, IDE integration, and pricing.",
    "best/ai-tools-for-marketers": "Best AI tools for marketers 2026: Jasper, Semrush, Canva AI, and more — ranked by impact on content production, SEO performance, and overall campaign ROI.",
}

def truncate_desc(desc, max_len=158):
    """Truncate at last word boundary before max_len."""
    if len(desc) <= max_len:
        return desc
    truncated = desc[:max_len]
    last_space = truncated.rfind(' ')
    if last_space > max_len - 20:
        truncated = truncated[:last_space]
    # Remove trailing punctuation except period
    truncated = truncated.rstrip(',:;—- ')
    if not truncated.endswith('.'):
        truncated += '.'
    return truncated

def remove_site_suffix(title):
    """Remove ' | RankerToolAI' from title."""
    return re.sub(r'\s*\|\s*RankerToolAI\s*$', '', title).strip()

def fix_file(slug):
    path = os.path.join(HTML_DIR, slug, "index.html")
    if not os.path.exists(path):
        print(f"  SKIP (not found): {slug}")
        return

    html = open(path, encoding='utf-8', errors='replace').read()
    original = html
    changed = []

    # ── Fix meta description ──────────────────────────────────────────────────
    # Match both name="description" and name='description' with content after
    desc_pattern = re.compile(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])([^"\']*?)(["\'][^>]*/?>)',
        re.IGNORECASE
    )
    # Also try reversed attribute order
    desc_pattern2 = re.compile(
        r'(<meta\s+content=["\'])([^"\']*?)(["\'][^>]*name=["\']description["\'][^>]*/?>)',
        re.IGNORECASE
    )

    def fix_desc(m):
        prefix, desc, suffix = m.group(1), m.group(2), m.group(3)
        new_desc = desc

        if slug in IMPROVED_DESCS:
            new_desc = IMPROVED_DESCS[slug]
        elif len(desc) > 160:
            new_desc = truncate_desc(desc)

        if new_desc != desc:
            changed.append(f"desc: {len(desc)} → {len(new_desc)} chars")
        return prefix + new_desc + suffix

    new_html = desc_pattern.sub(fix_desc, html)
    if new_html == html:
        new_html = desc_pattern2.sub(fix_desc, html)
    html = new_html

    # ── Fix title: remove | RankerToolAI suffix ──────────────────────────────
    title_pattern = re.compile(r'(<title>)(.*?)(</title>)', re.IGNORECASE | re.DOTALL)
    def fix_title(m):
        title = m.group(2)
        new_title = remove_site_suffix(title)
        if len(new_title) > 65:
            # Already fixed suffix, still long — leave as-is
            new_title = new_title
        if new_title != title:
            changed.append(f"title: {len(title)} → {len(new_title)} chars")
        return m.group(1) + new_title + m.group(3)

    html = title_pattern.sub(fix_title, html)

    if html != original:
        open(path, 'w', encoding='utf-8').write(html)
        print(f"  FIXED {slug}: {', '.join(changed)}")
    else:
        print(f"  SKIP  {slug}: no change needed")

# Pages to process
PAGES = [
    "review/grok",
    "review/jasper",
    "review/adobe-firefly",
    "review/deepseek",
    "review/julius-ai",
    "review/perplexity",
    "review/runway",
    "review/semrush",
    "review/stable-diffusion",
    "compare/midjourney-vs-firefly",
    "compare/notion-vs-chatgpt",
    "compare/perplexity-vs-google",
    "compare/surfer-seo-vs-clearscope",
    "alternatives/cursor",
    "alternatives/deepseek",
    "alternatives/elevenlabs",
    "alternatives/gemini",
    "alternatives/notion",
    "alternatives/surfer-seo",
    "best/ai-coding-tools",
    "best/ai-data-tools",
    "best/ai-marketing-tools",
    "best/ai-productivity-tools",
    "best/ai-tools-for-developers",
    "best/ai-tools-for-marketers",
    "best/ai-tools-for-students",
]

print(f"Fixing meta descriptions/titles for {len(PAGES)} pages...")
for slug in PAGES:
    fix_file(slug)
print("Done.")
