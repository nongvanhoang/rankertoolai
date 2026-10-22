#!/usr/bin/env python3
"""Review + /go/ pages for 7 Reditus programs + ImagineArt (2026-10-22).
Reuses the templates in generate_anderro_reviews.py / generate_anderro_go_pages.py;
data lives in reditus_batch_data.py. Writes to html/ only (the clone that pushes)."""
import os
import generate_anderro_reviews as reviews
import generate_anderro_go_pages as go_pages
from reditus_batch_data import REVIEWS, GO_PAGES

HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html")
reviews.OUT_ROOTS = [HTML]
go_pages.OUT_ROOTS = [HTML]

# Impact short links: don't append utm/gclid, pass the sub id as Impact's subId1.
IMPACT_SLUGS = {"imagineart"}

def patch_impact(slug):
    path = os.path.join(HTML, "go", slug, "index.html")
    with open(path, encoding="utf-8") as f:
        page = f.read()
    page = page.replace("['utm_source','utm_medium','utm_campaign','utm_content','gclid'].forEach", "[].forEach")
    page = page.replace("dest.searchParams.set('subid', subid);", "dest.searchParams.set('subId1', subid);")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)

if __name__ == "__main__":
    for t in REVIEWS:
        reviews.render(t)
    for t in GO_PAGES:
        go_pages.render(t)
        if t["slug"] in IMPACT_SLUGS:
            patch_impact(t["slug"])
