#!/usr/bin/env python3
"""Site-wide email capture completion:
 - Ensure every content page loads /assets/js/main.js (exit-intent popup + GA4 events)
 - Inject the inline newsletter section on pages that lack it
 - Point every newsletter form's _next to /newsletter/thanks/ (GA4/Ads conversion page)
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent

SECTIONS = ["review", "blog", "best", "alternatives", "compare", "coupons", "category"]

MAIN_JS_TAG = '<script src="/assets/js/main.js" defer></script>\n'

OLD_NEXT = "https://rankertoolai.com/?subscribed=1"
NEW_NEXT = "https://rankertoolai.com/newsletter/thanks/"


def newsletter_html(source):
    return f"""
  <!-- Newsletter -->
  <div class="newsletter-section">
    <h3>Get Our Weekly AI Tool Roundup</h3>
    <p>New reviews, rankings &amp; deals — every Thursday. No spam, unsubscribe anytime.</p>
    <form class="newsletter-form" action="https://formsubmit.co/nongvanhoang1608@gmail.com" method="POST">
      <input type="hidden" name="_subject" value="Newsletter Signup — RankerToolAI">
      <input type="hidden" name="_next" value="{NEW_NEXT}">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="source" value="{source}">
      <input type="email" name="email" placeholder="your@email.com" required autocomplete="email">
      <button type="submit">Subscribe Free →</button>
    </form>
  </div>
"""


stats = {"js": 0, "form": 0, "next": 0}

pages = []
for section in SECTIONS:
    for d in sorted((ROOT / section).iterdir()):
        f = d / "index.html"
        if d.is_dir() and f.exists():
            pages.append((section, f))

for section, f in pages:
    content = f.read_text(encoding="utf-8")
    new = content

    # 1. main.js (exit popup + analytics events) on every page
    if "assets/js/main.js" not in new and "</body>" in new:
        new = new.replace("</body>", MAIN_JS_TAG + "</body>", 1)
        stats["js"] += 1

    # 2. inline newsletter section — only where the shared stylesheet exists
    if "newsletter-section" not in new and "assets/css/base.css" in new:
        block = newsletter_html(f"newsletter_{section}")
        if "</article>" in new:
            new = new.replace("</article>", block + "\n</article>", 1)
            stats["form"] += 1
        elif '<footer class="site-footer">' in new:
            new = new.replace('<footer class="site-footer">',
                              f'<div class="container" style="max-width:800px;">{block}</div>\n<footer class="site-footer">', 1)
            stats["form"] += 1
        elif "</main>" in new:
            new = new.replace("</main>", block + "\n</main>", 1)
            stats["form"] += 1

    # 3. conversion page redirect
    if OLD_NEXT in new:
        stats["next"] += new.count(OLD_NEXT)
        new = new.replace(OLD_NEXT, NEW_NEXT)

    if new != content:
        f.write_text(new, encoding="utf-8")

# Homepage + exit popup in main.js: update _next as well
for extra in [ROOT / "index.html", ROOT / "assets" / "js" / "main.js"]:
    content = extra.read_text(encoding="utf-8")
    if OLD_NEXT in content:
        stats["next"] += content.count(OLD_NEXT)
        extra.write_text(content.replace(OLD_NEXT, NEW_NEXT), encoding="utf-8")

print(f"main.js added   : {stats['js']} pages")
print(f"newsletter added: {stats['form']} pages")
print(f"_next updated   : {stats['next']} forms")
