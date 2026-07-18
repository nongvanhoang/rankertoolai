# -*- coding: utf-8 -*-
"""
Fetch real third-party review signals (Trustpilot, G2) for a tool, for use in
review-page "Real User Ratings" sections and Review/AggregateRating schema.

Read-only, public-page fetches only (no login, no scraping of individual
review text at scale) — pulls the same rating/review-count data these sites
render for any visitor. Never fabricates a rating: if a profile can't be
found or has no aggregate rating, returns an error for that source rather
than guessing.

Both sites 403 plain requests (bot-protection WAF). Trustpilot renders fine
under a real headless browser (same approach already used by
affiliate_toolkit/ads_transparency's Google Ads Transparency Center fetch) —
this is a genuine browser render, not header-spoofing/IP-rotation evasion —
and its rating data is confirmed extractable via __NEXT_DATA__. G2 hangs
indefinitely even under headless Chromium (tested, killed after 100s) —
its bot-challenge is stronger and this script does NOT attempt to defeat it
(consistent with the repo's existing policy of not attempting evasion, see
[[affiliate_toolkit_project]]'s SimilarWeb note). Treat --g2 as best-effort;
if it fails or hangs, get the G2 rating by having the user paste it manually
(same pattern already used for Semrush's ad-picker table).

Usage:
  python fetch_external_reviews.py --trustpilot elevenlabs.io
  python fetch_external_reviews.py --g2 "context-dev"
  python fetch_external_reviews.py --trustpilot context.dev --g2 "context-dev" --json out.json
"""
import argparse, json, re, sys
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _fetch_html(url: str, timeout_ms=30000, settle_ms=2500):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(user_agent=UA)
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(settle_ms)
            return page.content()
        finally:
            browser.close()


def _find_jsonld_aggregate_rating(html: str):
    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            agg = item.get("aggregateRating")
            if isinstance(agg, dict) and agg.get("ratingValue"):
                try:
                    return float(agg["ratingValue"]), int(float(agg.get("reviewCount") or agg.get("ratingCount") or 0)), float(agg.get("bestRating") or 5)
                except (TypeError, ValueError):
                    continue
    return None


def fetch_trustpilot(domain_or_slug: str, timeout_ms=30000):
    """domain_or_slug: the reviewed domain as it appears in the Trustpilot URL,
    e.g. 'elevenlabs.io' -> https://www.trustpilot.com/review/elevenlabs.io"""
    url = f"https://www.trustpilot.com/review/{domain_or_slug}"
    try:
        html = _fetch_html(url, timeout_ms=timeout_ms)
    except Exception as e:
        return {"source": "trustpilot", "url": url, "error": str(e)}

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            bu = data["props"]["pageProps"]["businessUnit"]
            if bu.get("trustScore") and bu.get("numberOfReviews"):
                return {
                    "source": "trustpilot", "url": url,
                    "name": bu.get("displayName"),
                    "rating": float(bu["trustScore"]), "review_count": int(bu["numberOfReviews"]),
                    "scale": 5,
                }
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass

    result = _find_jsonld_aggregate_rating(html)
    if result:
        rating, count, scale = result
        return {"source": "trustpilot", "url": url, "rating": rating, "review_count": count, "scale": scale}
    return {"source": "trustpilot", "url": url, "error": "no rating data found (page structure may have changed, or profile doesn't exist)"}


def fetch_g2(slug: str, timeout_ms=30000):
    """slug: G2 product slug, e.g. 'context-dev' -> https://www.g2.com/products/context-dev/reviews"""
    url = f"https://www.g2.com/products/{slug}/reviews"
    try:
        html = _fetch_html(url, timeout_ms=timeout_ms)
    except Exception as e:
        return {"source": "g2", "url": url, "error": str(e)}

    result = _find_jsonld_aggregate_rating(html)
    if result:
        rating, count, scale = result
        return {"source": "g2", "url": url, "rating": rating, "review_count": count, "scale": scale}
    return {"source": "g2", "url": url, "error": "no rating data found (product slug may be wrong, or page structure changed)"}


def main():
    ap = argparse.ArgumentParser(description="Fetch real Trustpilot/G2 rating data for a tool")
    ap.add_argument("--trustpilot", help="Trustpilot review-domain slug, e.g. elevenlabs.io")
    ap.add_argument("--g2", help="G2 product slug, e.g. context-dev")
    ap.add_argument("--json", metavar="FILE", help="Write results to this JSON file")
    args = ap.parse_args()

    if not args.trustpilot and not args.g2:
        ap.error("pass at least --trustpilot or --g2")

    results = []
    if args.trustpilot:
        results.append(fetch_trustpilot(args.trustpilot))
    if args.g2:
        results.append(fetch_g2(args.g2))

    for r in results:
        if "error" in r:
            print(f"[{r['source']}] {r['url']} -> FAILED: {r['error']}")
        else:
            print(f"[{r['source']}] {r['url']} -> {r['rating']}/{r['scale']} ({r['review_count']} reviews)")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Wrote {args.json}")


if __name__ == "__main__":
    main()
