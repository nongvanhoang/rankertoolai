#!/usr/bin/env python3
"""
Auto-update internal links after a new page is added.
Run immediately after saving a new HTML file.

Usage:
  python update_links.py review jasper "Jasper AI" 8.5 "AI Writing" "Best AI writer for teams"
  python update_links.py compare jasper-vs-writesonic "Jasper vs Writesonic" 0 "AI Writing" "Side-by-side comparison"
  python update_links.py alternatives chatgpt "ChatGPT Alternatives" 0 "AI Chatbots" "Top ChatGPT alternatives"
  python update_links.py best ai-writing-tools "Best AI Writing Tools" 0 "AI Writing" "Top-ranked AI writing tools"

Arguments:
  page_type  : review | compare | alternatives | best
  slug       : URL slug (e.g. jasper, jasper-vs-writesonic)
  name       : Display name
  score      : Score out of 10 (0 for non-review pages)
  category   : Category label (for data-cat filter)
  description: Short description (~100 chars)
"""
import sys
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

HTML_DIR = Path(__file__).parent / "html"

# Map page types to their index file and card structure
PAGE_CONFIG = {
    "review": {
        "index": "review/index.html",
        "grid_end_marker": "<!-- /review-grid -->",
        "url_pattern": "/review/{slug}/",
    },
    "compare": {
        "index": "compare/index.html",
        "grid_end_marker": "<!-- /compare-grid -->",
        "url_pattern": "/compare/{slug}/",
    },
    "alternatives": {
        "index": "alternatives/index.html",
        "grid_end_marker": "<!-- /alternatives-grid -->",
        "url_pattern": "/alternatives/{slug}/",
    },
    "best": {
        "index": "best/index.html",
        "grid_end_marker": "<!-- /best-grid -->",
        "url_pattern": "/best/{slug}/",
    },
}

# Category → category hub slug mapping
CATEGORY_HUBS = {
    "AI Writing":     "ai-writing",
    "AI Chatbots":    "ai-coding",
    "AI Coding":      "ai-coding",
    "AI Image":       "ai-image",
    "AI Video":       "ai-video",
    "AI Voice":       "ai-voice",
    "AI SEO":         "ai-seo",
    "AI Marketing":   "ai-marketing",
    "AI Data":        "ai-data",
    "AI Design":      "ai-design",
    "AI Productivity": "ai-productivity",
    # Non-AI categories (added 2026-07-12, see data/new_categories.json).
    # These hub pages don't exist yet — created one at a time in Phase 1
    # of the multi-category expansion, from templates/category_template.html.
    "SEO":                             "seo-tools",
    "Hosting & Domain":                "hosting-domain",
    "VPN":                             "vpn",
    "Password Manager":                "password-manager",
    "Antivirus & Security":            "antivirus-security",
    "Privacy & Compliance":            "privacy-compliance",
    "Backup & File Storage":           "backup-storage",
    "Productivity, PDF & System Tools": "productivity-tools",
    "Video, Design & Creative":        "video-design",
    "Email Marketing & Webinars":      "email-marketing",
    "Language Learning":               "language-learning",
}


def make_review_card(slug, name, score, category, description, url):
    score_display = f"{score}" if score else ""
    return f"""      <a href="{url}" style="text-decoration:none;color:inherit;" data-cat="{category}" data-score="{score_display}" data-name="{name}">
        <div class="review-card">
          <div class="review-card-header">
            <img src="/assets/images/logos/{slug}.svg" onerror="this.src='/assets/images/logos/{slug}.png'" alt="{name} logo" class="review-card-logo">
            <div><div class="review-card-title">{name}</div></div>
            {"<div class='review-card-score'>" + score_display + "</div>" if score_display else ""}
          </div>
          <p class="review-card-desc">{description}</p>
          <span class="btn btn-sm btn-secondary" style="font-size:0.8rem;">Read Review →</span>
        </div>
      </a>"""


def make_compare_card(slug, name, score, category, description, url):
    # compare/index.html's grid uses .compare-card/.compare-vs/.compare-tool-label/
    # .compare-vs-badge — NOT .review-card (that class isn't even defined on this
    # page). Match the established template so new cards aren't unstyled
    # (found 2026-07-06: 19 cards had silently rendered with zero CSS for months).
    if " vs " in name:
        tool_a, tool_b = name.split(" vs ", 1)
    else:
        parts = slug.split("-vs-")
        tool_a = parts[0].replace("-", " ").title()
        tool_b = parts[1].replace("-", " ").title() if len(parts) > 1 else ""
    return f"""      <a href="{url}" style="text-decoration:none;color:inherit;" data-cat="{category}" data-name="{name}">
        <div class="compare-card">
          <div class="compare-vs"><span class="compare-tool-label">{tool_a}</span><span class="compare-vs-badge">VS</span><span class="compare-tool-label">{tool_b}</span></div>
          <p style="font-size:0.875rem;color:var(--color-text-muted);margin-top:0.5rem;">{description}</p>
          <span style="font-size:0.875rem;color:var(--color-primary);font-weight:600;">Read comparison →</span>
        </div>
      </a>"""


def make_generic_card(slug, name, score, category, description, url, cta="View →"):
    return f"""      <a href="{url}" style="text-decoration:none;color:inherit;" data-cat="{category}" data-name="{name}">
        <div class="review-card">
          <div class="review-card-header">
            <div><div class="review-card-title">{name}</div></div>
          </div>
          <p class="review-card-desc">{description}</p>
          <span class="btn btn-sm btn-secondary" style="font-size:0.8rem;">{cta}</span>
        </div>
      </a>"""


def make_alt_index_card(slug, name, score, category, description, url):
    # alternatives/index.html's grid uses .alt-index-card/.alt-count/.alt-top-pick —
    # NOT .review-card (found 2026-07-06, same bug as compare's card mismatch).
    # "Top Pick" needs an editorial claim we can't reliably auto-extract from the
    # page, so that line is omitted rather than guessed.
    title = name if name.lower().endswith("alternatives") else f"Best {name} Alternatives"
    return f"""      <a href="{url}" style="text-decoration:none;color:inherit;" data-cat="{category}" data-name="{name}">
        <div class="alt-index-card">
          <h3>{title}</h3>
          <p class="review-card-desc">{description}</p>
          <span style="font-size:0.875rem;color:var(--color-primary);font-weight:600;">See alternatives →</span>
        </div>
      </a>"""


BEST_EMOJI = {
    "agencies": "🏢", "bloggers": "✍️", "developers": "👨‍💻",
    "marketers": "📈", "students": "🎓",
}


def make_best_card(slug, name, score, category, description, url):
    # best/index.html's "Deep-Dive Best-Of Lists" grid has no CSS class at all —
    # every card is hand-styled inline (found 2026-07-06). Match that structure
    # so a new card isn't left completely unstyled.
    emoji = "🤖"
    for key, e in BEST_EMOJI.items():
        if key in slug:
            emoji = e
            break
    return f"""    <a href="{url}" style="text-decoration:none;display:block;border:1px solid rgba(249,115,22,0.35);border-radius:var(--radius-lg);padding:1.25rem;background:linear-gradient(135deg,rgba(249,115,22,0.07),rgba(251,191,36,0.03));color:inherit;" data-cat="{category}" data-name="{name}">
      <div style="font-size:1.5rem;margin-bottom:0.5rem;">{emoji}</div>
      <div style="font-weight:800;font-size:1rem;margin-bottom:0.35rem;">{name}</div>
      <div style="font-size:0.8rem;color:var(--color-text-muted);">{description}</div>
      <div style="margin-top:0.75rem;font-size:0.8rem;color:#f97316;font-weight:600;">Read →</div>
    </a>"""


def inject_card_into_index(page_type, slug, name, score, category, description):
    cfg = PAGE_CONFIG.get(page_type)
    if not cfg:
        print(f"Unknown page type: {page_type}")
        return False

    index_path = HTML_DIR / cfg["index"]
    if not index_path.exists():
        print(f"Index not found: {index_path}")
        return False

    url = cfg["url_pattern"].format(slug=slug)
    content = index_path.read_text(encoding="utf-8")

    # Check if link already exists
    if url in content:
        print(f"  [skip] {url} already in {cfg['index']}")
        return False

    # Build the card HTML
    if page_type == "review":
        card = make_review_card(slug, name, score, category, description, url)
        cta = "Read Review →"
    elif page_type == "compare":
        card = make_compare_card(slug, name, score, category, description, url)
        cta = "Compare →"
    elif page_type == "alternatives":
        card = make_alt_index_card(slug, name, score, category, description, url)
        cta = "See Alternatives →"
    elif page_type == "best":
        card = make_best_card(slug, name, score, category, description, url)
        cta = "Read →"
    else:
        card = make_generic_card(slug, name, score, category, description, url, "View →")
        cta = "View →"

    marker = cfg["grid_end_marker"]
    if marker not in content:
        # Fallback: inject before </main>
        if "</main>" in content:
            content = content.replace("</main>", card + "\n</main>", 1)
        else:
            print(f"  [warn] No injection marker found in {cfg['index']}")
            return False
    else:
        content = content.replace(marker, card + "\n      " + marker, 1)

    index_path.write_text(content, encoding="utf-8")
    print(f"  [added] {url} → {cfg['index']}")
    return True


def add_to_category_hub(slug, name, page_type, category, description):
    hub_slug = CATEGORY_HUBS.get(category)
    if not hub_slug:
        print(f"  [skip] No category hub for: {category}")
        return False

    hub_path = HTML_DIR / "category" / hub_slug / "index.html"
    if not hub_path.exists():
        print(f"  [skip] Category hub not found: {hub_path}")
        return False

    url = f"/{page_type}/{slug}/"
    content = hub_path.read_text(encoding="utf-8")

    if url in content:
        print(f"  [skip] {url} already in category/{hub_slug}/")
        return False

    link = f'<a href="{url}">{name}</a>'
    # Try to inject before </section> or </ul> or </main>
    injected = False
    for target in ["</section>", "</ul>", "</main>"]:
        if target in content:
            content = content.replace(target, f"      {link}\n{target}", 1)
            injected = True
            break

    if not injected:
        print(f"  [warn] Could not find injection point in category/{hub_slug}/")
        return False

    hub_path.write_text(content, encoding="utf-8")
    print(f"  [added] {url} → category/{hub_slug}/index.html")
    return True


def main():
    if len(sys.argv) < 7:
        print("Usage: python update_links.py <type> <slug> <name> <score> <category> <description>")
        print("Example: python update_links.py review jasper 'Jasper AI' 8.5 'AI Writing' 'Best AI writer'")
        sys.exit(1)

    page_type   = sys.argv[1]
    slug        = sys.argv[2]
    name        = sys.argv[3]
    score       = float(sys.argv[4]) if sys.argv[4] else 0
    category    = sys.argv[5]
    description = sys.argv[6]

    print(f"\nUpdating internal links for: {page_type}/{slug}")
    print(f"  Name: {name} | Score: {score} | Category: {category}")

    changed = 0
    if inject_card_into_index(page_type, slug, name, score, category, description):
        changed += 1
    if add_to_category_hub(slug, name, page_type, category, description):
        changed += 1

    print(f"\nDone: {changed} file(s) updated.")
    print(f"Next: run '.\\deploy.ps1 -Url /{page_type}/{slug}/' to deploy")


if __name__ == "__main__":
    main()
