#!/usr/bin/env python3
"""
Add a new affiliate merchant to a new-category hub page + registry.

Usage:
  python add_merchant.py <category-slug> <merchant-slug> "<Name>" "<Tagline>" "<Price label>" [--deals]

Prereqs (create these by hand first):
  - html/go/<merchant-slug>/index.html   (bridge page, see html/go/nordpass/ for the pattern)
  - html/category/<category-slug>/index.html  (hub page, created once per category from
    templates/category_template.html — this script will not create it)
  - <category-slug> must already be a key in data/new_categories.json

What it does:
  1. Appends the merchant to data/new_categories.json
  2. Injects a .tool-item card into the category hub page between the
     TOOL_LIST_START / TOOL_LIST_END markers
  3. With --deals, also injects a lightweight deal-card into html/deals/index.html

Does NOT touch the html/ clone's copy — mirror + commit + push both remotes by hand
after running this, same as the manual process used for the first 3 pilot merchants.
"""
import sys
import json
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent
HTML_DIR = ROOT / "html"
REGISTRY_PATH = ROOT / "data" / "new_categories.json"


def make_tool_item(slug, name, tagline, price_label, go_url):
    return f'''    <a href="{go_url}" class="tool-item" rel="nofollow sponsored" target="_blank">
      <div class="tool-logo-wrap"><img src="/assets/images/logos/{slug}.png" onerror="this.style.display='none'" alt="{name}" style="width:36px;height:36px;object-fit:contain;border-radius:6px;" loading="lazy"></div>
      <div class="tool-info">
        <div class="tool-top"><span class="tool-name">{name}</span></div>
        <p class="tool-desc">{tagline}</p>
        <div class="tool-meta"><span>{price_label}</span></div>
      </div>
    </a>
'''


def make_deal_card(name, tagline, price_label, go_url):
    return f'''    <!-- {name} -->
    <div class="deal-card">
      <div class="deal-card-top">
        <div class="deal-tool-name" style="display:flex;align-items:center;gap:0.5rem;">{name}</div>
        <div class="deal-description">{tagline}</div>
      </div>
      <div class="deal-card-bottom">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:0.5rem;flex-wrap:wrap;">
          <div><span class="deal-price">{price_label}</span></div>
          <a href="{go_url}" rel="nofollow sponsored" target="_blank" class="btn btn-primary" style="font-size:0.875rem;padding:0.5rem 1rem;">Get Deal →</a>
        </div>
        <div style="margin-top:0.5rem;display:flex;gap:0.75rem;flex-wrap:wrap;">
          <span class="deal-expires">Ongoing offer</span>
        </div>
      </div>
    </div>

'''


def main():
    if len(sys.argv) < 6:
        print('Usage: python add_merchant.py <category-slug> <merchant-slug> "<Name>" "<Tagline>" "<Price label>" [--deals]')
        sys.exit(1)

    category_slug = sys.argv[1]
    merchant_slug = sys.argv[2]
    name = sys.argv[3]
    tagline = sys.argv[4]
    price_label = sys.argv[5]
    add_deals = "--deals" in sys.argv[6:]

    go_path = HTML_DIR / "go" / merchant_slug / "index.html"
    if not go_path.exists():
        print(f"ERROR: {go_path} does not exist. Create the go/ bridge page first.")
        sys.exit(1)

    hub_path = HTML_DIR / "category" / category_slug / "index.html"
    if not hub_path.exists():
        print(f"ERROR: {hub_path} does not exist.")
        print("Bootstrap this category's hub page from templates/category_template.html first.")
        sys.exit(1)

    if not REGISTRY_PATH.exists():
        print(f"ERROR: {REGISTRY_PATH} not found.")
        sys.exit(1)

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if category_slug not in registry:
        print(f"ERROR: '{category_slug}' not found in {REGISTRY_PATH}. Add it there first.")
        sys.exit(1)

    go_url = f"/go/{merchant_slug}/"

    # 1. Registry
    existing_slugs = {m["slug"] for m in registry[category_slug]["merchants"]}
    if merchant_slug in existing_slugs:
        print(f"[skip] {merchant_slug} already in registry for {category_slug}")
    else:
        registry[category_slug]["merchants"].append({
            "slug": merchant_slug,
            "name": name,
            "tagline": tagline,
            "price_label": price_label,
            "go_url": go_url,
            "added": date.today().isoformat(),
        })
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[added] {merchant_slug} -> data/new_categories.json ({category_slug})")

    # 2. Category hub page
    hub_content = hub_path.read_text(encoding="utf-8")
    if go_url in hub_content:
        print(f"[skip] {go_url} already linked in category/{category_slug}/")
    else:
        marker = "<!-- TOOL_LIST_END -->"
        if marker not in hub_content:
            print(f"ERROR: marker '{marker}' not found in {hub_path}")
            print("Was this hub page created from templates/category_template.html?")
            sys.exit(1)
        card = make_tool_item(merchant_slug, name, tagline, price_label, go_url)
        hub_content = hub_content.replace(marker, card + marker)
        hub_path.write_text(hub_content, encoding="utf-8")
        print(f"[added] {go_url} -> category/{category_slug}/index.html")

    # 3. Optional deals card
    if add_deals:
        deals_path = HTML_DIR / "deals" / "index.html"
        deals_content = deals_path.read_text(encoding="utf-8")
        if go_url in deals_content:
            print(f"[skip] {go_url} already on deals/index.html")
        else:
            target = "\n  </div>\n\n  <!-- Tips box -->"
            if target not in deals_content:
                print("ERROR: expected deals-grid closing pattern not found in deals/index.html — insert manually.")
            else:
                card = make_deal_card(name, tagline, price_label, go_url)
                deals_content = deals_content.replace(target, "\n" + card + "  </div>\n\n  <!-- Tips box -->", 1)
                deals_path.write_text(deals_content, encoding="utf-8")
                print(f"[added] {name} -> deals/index.html")

    print("\nDone. Next: mirror touched files into the html/ clone, commit+push both remotes,")
    print("run generate_sitemap.py if this is a brand-new category hub, deploy via wrangler, verify live.")


if __name__ == "__main__":
    main()
