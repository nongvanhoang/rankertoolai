#!/usr/bin/env python3
"""Review + /go/ pages for ClipTalk (cliptalk.pro) (2026-10-18).
Reuses the templates in generate_anderro_reviews.py / generate_anderro_go_pages.py;
data lives in cliptalk_data.py. Writes to html/ only (the clone that pushes)."""
import os
import generate_anderro_reviews as reviews
import generate_anderro_go_pages as go_pages
from cliptalk_data import REVIEWS, GO_PAGES

HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html")
reviews.OUT_ROOTS = [HTML]
go_pages.OUT_ROOTS = [HTML]

if __name__ == "__main__":
    for t in REVIEWS:
        reviews.render(t)
    for t in GO_PAGES:
        go_pages.render(t)
