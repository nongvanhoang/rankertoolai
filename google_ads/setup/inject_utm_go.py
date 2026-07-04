"""
Module 1b: Upgrade /go/ affiliate redirect pages to pass UTM parameters.

Before: /go/elevenlabs/ → redirects to https://elevenlabs.io/?from=rankertoolai
After:  /go/elevenlabs/?utm_source=google&utm_medium=cpc&... → same URL + UTMs preserved

The redirect page reads UTM params from the URL and appends them to the destination.
Also fires Google Ads affiliate_click conversion event before redirecting.

Usage:
  python inject_utm_go.py              # Dry run
  python inject_utm_go.py --apply      # Apply changes
"""

import os
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent / "html" / "go"
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_redirect_page(tool_slug: str, dest_url: str, tool_name: str, cfg: dict) -> str:
    ads_id = cfg["google_ads_id"]
    ads_click = cfg["google_ads_conversion"]["affiliate_click"]
    ga4_id = cfg["ga4_id"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redirecting to {tool_name} | RankerToolAI</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="canonical" href="https://rankertoolai.com/go/{tool_slug}/">

  <!-- GA4 + Google Ads on redirect page -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga4_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga4_id}');
    gtag('config', '{ads_id}');
  </script>
</head>
<body>
  <p>Redirecting you to <a href="{dest_url}" rel="nofollow sponsored">{tool_name}</a>...</p>

  <script>
    (function() {{
      // Fire conversion event before redirect
      gtag('event', 'conversion', {{
        'send_to': '{ads_click}',
        'value': 1.0,
        'currency': 'USD'
      }});
      gtag('event', 'affiliate_click', {{
        'tool': '{tool_slug}',
        'source': document.referrer || 'direct'
      }});

      // Read UTM params from current URL and append to destination
      var params = new URLSearchParams(window.location.search);
      var dest = new URL("{dest_url}");
      var utmKeys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term'];
      utmKeys.forEach(function(k) {{
        if (params.has(k)) dest.searchParams.set(k, params.get(k));
      }});

      // Also pass gclid for Google Ads auto-tagging
      if (params.has('gclid')) dest.searchParams.set('gclid', params.get('gclid'));

      // Delay 300ms to let gtag fire
      setTimeout(function() {{
        window.location.replace(dest.toString());
      }}, 300);
    }})();
  </script>
</body>
</html>"""

TOOL_NAMES = {
    "adcreative-ai": "AdCreative AI", "adobe-firefly": "Adobe Firefly",
    "akkio": "Akkio", "canva-ai": "Canva AI", "chatgpt": "ChatGPT",
    "claude": "Claude", "codeium": "Codeium", "copy-ai": "Copy.AI",
    "cursor": "Cursor", "deepseek": "DeepSeek", "elevenlabs": "ElevenLabs",
    "frase": "Frase", "gemini": "Gemini", "github-copilot": "GitHub Copilot",
    "grok": "Grok", "heygen": "HeyGen", "hubspot": "HubSpot",
    "jasper": "Jasper AI", "julius-ai": "Julius AI", "midjourney": "Midjourney",
    "murf": "Murf AI", "notion": "Notion", "otter-ai": "Otter AI",
    "perplexity": "Perplexity", "play-ht": "Play.ht", "polymer": "Polymer",
    "runway": "Runway ML", "semrush": "SEMrush", "speechify": "Speechify",
    "stable-diffusion": "Stable Diffusion", "surfer-seo": "Surfer SEO",
    "synthesia": "Synthesia", "windsurf": "Windsurf", "writesonic": "Writesonic",
}

DEST_URLS = {
    "adcreative-ai": "https://www.adcreative.ai/?via=rankertoolai",
    "adobe-firefly": "https://firefly.adobe.com/",
    "akkio": "https://www.akkio.com/",
    "canva-ai": "https://www.canva.com/?via=rankertoolai",
    "chatgpt": "https://chat.openai.com/",
    "claude": "https://claude.ai/",
    "codeium": "https://codeium.com/",
    "copy-ai": "https://www.copy.ai/?via=rankertoolai",
    "cursor": "https://www.cursor.com/",
    "deepseek": "https://www.deepseek.com/",
    "elevenlabs": "https://elevenlabs.io/?from=rankertoolai",
    "frase": "https://www.frase.io/?via=rankertoolai",
    "gemini": "https://gemini.google.com/",
    "github-copilot": "https://github.com/features/copilot",
    "grok": "https://grok.com/?via=rankertoolai",
    "heygen": "https://www.heygen.com/?sid=rankertoolai",
    "hubspot": "https://www.hubspot.com/?via=rankertoolai",
    "jasper": "https://www.jasper.ai/?fpr=rankertoolai",
    "julius-ai": "https://julius.ai/",
    "midjourney": "https://www.midjourney.com/",
    "murf": "https://murf.ai/?via=rankertoolai",
    "notion": "https://www.notion.so/?via=rankertoolai",
    "otter-ai": "https://otter.ai/",
    "perplexity": "https://www.perplexity.ai/",
    "play-ht": "https://play.ht/?via=rankertoolai",
    "polymer": "https://polymersearch.com/",
    "runway": "https://runwayml.com/",
    "semrush": "https://www.semrush.com/",
    "speechify": "https://speechify.com/?via=rankertoolai",
    "stable-diffusion": "https://stability.ai/?via=rankertoolai",
    "surfer-seo": "https://surferseo.com/?fpr=rankertoolai",
    "synthesia": "https://www.synthesia.io/?via=rankertoolai",
    "windsurf": "https://windsurf.com/",
    "writesonic": "https://writesonic.com/?via=rankertoolai",
}

def process(apply=False):
    cfg = load_config()
    stats = {"total": 0, "updated": 0, "skipped": 0}

    for slug, dest_url in DEST_URLS.items():
        page_dir = ROOT / slug
        page_path = page_dir / "index.html"
        stats["total"] += 1

        if not page_path.exists():
            print(f"  [MISSING] {slug}/index.html")
            continue

        new_html = build_redirect_page(slug, dest_url, TOOL_NAMES.get(slug, slug), cfg)
        current = page_path.read_text(encoding="utf-8", errors="replace")

        if "URLSearchParams(window.location.search)" in current:
            stats["skipped"] += 1
            continue

        if apply:
            page_path.write_text(new_html, encoding="utf-8")
            stats["updated"] += 1
            print(f"  [UPDATED] /go/{slug}/")
        else:
            print(f"  [NEEDS UPDATE] /go/{slug}/")
            stats["skipped"] += 1

    print(f"\n{'='*50}")
    print(f"  Total:   {stats['total']}")
    print(f"  {'Updated' if apply else 'Need update'}: {stats['updated'] if apply else stats['skipped']}")
    if not apply:
        print(f"\n  Run with --apply to update redirect pages.")
    print(f"{'='*50}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"\n[inject_utm_go] Mode: {mode}\n")
    process(apply=args.apply)
