#!/usr/bin/env python3
"""Review + /go/ pages for Leavo, Merlin AI and WriteHuman (2026-10-24).
Reuses the templates in generate_anderro_reviews.py / generate_anderro_go_pages.py (repo root);
data lives in batch_2026_10_24_data.py. Run from the repo root: python html/generate_batch_2026_10_24.py"""
import os
import sys

HTML = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HTML)
sys.path.insert(0, os.path.dirname(HTML))  # root templates win over html/'s older copy
import generate_anderro_reviews as reviews
import generate_anderro_go_pages as go_pages
from batch_2026_10_24_data import REVIEWS, GO_PAGES

reviews.OUT_ROOTS = [HTML]
go_pages.OUT_ROOTS = [HTML]

if __name__ == "__main__":
    for t in REVIEWS:
        reviews.render(t)
    for t in GO_PAGES:
        go_pages.render(t)
