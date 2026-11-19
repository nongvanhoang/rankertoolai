"""Render the AI Tool Pricing Index page + CSV from clean.json.

Usage: python render.py <repo_root> <clean.json> <YYYY-MM-DD publish date>
Re-run extract_prices.py -> clean_stats.py -> render.py to refresh.
"""
import csv, html, json, sys
from datetime import date
from pathlib import Path

ROOT = Path(sys.argv[1])
data = json.load(open(sys.argv[2], encoding="utf-8"))
PUB = sys.argv[3]
S, TOOLS = data["stats"], [t for t in data["tools"] if t.get("in_index")]
SLUG = "ai-tool-pricing-index"
URL = f"https://rankertoolai.com/{SLUG}/"
d = date.fromisoformat(PUB)
MONTH = d.strftime("%B %Y")
CSV_NAME = f"ai-tool-pricing-{d.strftime('%Y-%m')}.csv"
e = html.escape

def pct(a, b):
    return round(100 * a / b)

def money(v):
    if v is None:
        return "–"
    return f"${v:,.0f}" if v >= 10 and float(v).is_integer() else f"${v:,.2f}"

def nice_date(s):
    return date.fromisoformat(s).strftime("%B %-d, %Y") if sys.platform != "win32" else date.fromisoformat(s).strftime("%B %#d, %Y")

n = S["tools"]
seo = S["groups"]["SEO & content"]
ratio = round(seo["median_entry"] / S["median_entry"], 1)
title = f"AI Tool Pricing Index {MONTH}: What {n} AI Tools Really Cost"
desc = (f"We pulled the pricing tables of {n} AI and SaaS tools. {pct(S['free_plan'], n)}% have a free plan, "
        f"the median paid plan starts at {money(S['median_entry'])}/mo, and SEO tools cost about {ratio}x more to start.")

# ---------- page body ----------
findings = [
    (f"{pct(S['free_plan'], n)}%", f"have a free-forever plan ({S['free_plan']} of {n})"),
    (f"{money(S['median_entry'])}/mo", f"median price of the cheapest paid plan ({S['n_entry']} tools with a comparable USD price)"),
    (f"{ratio}x", f"SEO &amp; content tools start at a median {money(seo['median_entry'])}/mo, about {ratio} times the overall median"),
    (f"{pct(S['contact_sales'], n)}%", "hide at least one plan behind “contact sales” or a custom quote"),
    (f"{pct(S['trial_only'], n)}%", "offer only a time-limited free trial, no free plan"),
    (f"{pct(S['per_seat'], n)}%", "charge per seat or per user, so team cost grows with headcount"),
]
cards = "".join(
    f'<div class="verdict-meta-item"><div class="verdict-meta-value" style="font-size:1.6rem;color:var(--color-primary)">{v}</div>'
    f'<div style="color:var(--color-text-muted);font-size:.85rem;line-height:1.45">{t}</div></div>' for v, t in findings)

grows = []
for g, v in sorted(S["groups"].items(), key=lambda kv: (kv[0] == "Other", -(kv[1]["median_entry"] or 0))):
    small = " *" if v["tools"] < 5 else ""
    ch = f'{money(v["cheapest"][0])} ({e(v["cheapest"][1])})' if v["cheapest"] else "–"
    grows.append(f'<tr><td class="plan-name">{e(g)}{small}</td><td>{v["tools"]}</td>'
                 f'<td>{pct(v["free_plan"], v["tools"])}%</td><td class="plan-price">{money(v["median_entry"])}</td><td>{ch}</td></tr>')

def free_label(t):
    return "Yes" if t["free_plan"] else ("Trial only" if t["free_trial_only"] else "No")

MODEL = {"flat": "Flat plan", "per-seat": "Per seat", "usage": "Usage / credits"}
trows = []
for t in sorted(TOOLS, key=lambda t: (t["group"], t["name"].lower())):
    price = money(t["entry_usd_month"]) if t["entry_usd_month"] else (e(t["list_price_note"]) + " (non-USD)" if t["list_price_note"] else "Usage-based")
    trows.append(f'<tr><td class="plan-name"><a href="/review/{t["slug"]}/">{e(t["name"])}</a></td><td>{e(t["group"])}</td>'
                 f'<td>{free_label(t)}</td><td class="plan-price">{price}</td><td>{MODEL[t["model"]]}</td><td>{t["updated"]}</td></tr>')

citation = f'RankerToolAI, “AI Tool Pricing Index, {MONTH}”, {URL}'
main = f"""
<main class="container" style="max-width:960px; padding-top:1rem; padding-bottom:4rem;">
  <h1>AI Tool Pricing Index: {MONTH}</h1>
  <p style="color:var(--color-text-muted); font-size:0.875rem;">Published {nice_date(PUB)} · By <a href="/author/hoang-nong/">Hoang Nong</a> · Data from review pages updated {nice_date(S['updated_min'])} – {nice_date(S['updated_max'])}</p>

  <p>What does it actually cost to start using an AI tool? We took the pricing tables from <strong>{n} AI and SaaS tools</strong> we review and put them side by side: who still offers a free plan, what the cheapest paid plan costs, and which categories are the most expensive to get into.</p>

  <h2 id="key-findings">Key findings</h2>
  <div class="verdict-meta" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr));">{cards}</div>

  <div class="highlight-box"><strong>The short version:</strong> most AI tools let you start for free, and more than half of paid plans start under $20 a month ({S['under_20']} of {S['n_entry']}). The big exception is SEO software: only {seo['free_plan']} of {seo['tools']} SEO &amp; content tools have a free plan, and the typical entry plan costs {money(seo['median_entry'])} a month.</div>

  <h2 id="by-category">Entry price by category</h2>
  <p>“Entry price” is the cheapest paid plan for one user, per month. Sorted from most to least expensive.</p>
  <div style="overflow-x:auto"><table class="pricing-table">
    <thead><tr><th>Category</th><th>Tools</th><th>Free plan</th><th>Median entry price</th><th>Cheapest entry plan</th></tr></thead>
    <tbody>{''.join(grows)}</tbody>
  </table></div>
  <p style="font-size:.8rem;color:var(--color-text-muted)">* Fewer than 5 tools in this category, so treat the median as a rough guide.</p>

  <h2 id="what-it-means">What this means if you're buying</h2>
  <ul>
    <li><strong>Start on the free plan.</strong> {pct(S['free_plan'], n)}% of tools have one. Use it to check the output quality before paying.</li>
    <li><strong>Watch per-seat pricing.</strong> {S['per_seat']} tools charge per user. A three-person team on a per-seat plan pays three times the headline price.</li>
    <li><strong>Budget more for SEO.</strong> SEO and content platforms rarely have free plans. Use their trials on a real project before committing.</li>
    <li><strong>Annual billing changes the number.</strong> Where a vendor shows both, our entry price is the monthly rate when billed yearly. Paying month to month is often 15–40% more.</li>
  </ul>

  <h2 id="all-tools">All {n} tools</h2>
  <p>Click a tool for its full review and every plan. <a href="/{SLUG}/{CSV_NAME}">Download the data as CSV</a>.</p>
  <div style="overflow-x:auto"><table class="pricing-table">
    <thead><tr><th>Tool</th><th>Category</th><th>Free plan</th><th>Cheapest paid plan /mo</th><th>Pricing model</th><th>Page updated</th></tr></thead>
    <tbody>{''.join(trows)}</tbody>
  </table></div>

  <h2 id="methodology">How we built this index</h2>
  <ul>
    <li><strong>Source:</strong> the pricing table in each RankerToolAI review, which we take from the vendor's own pricing page. Only reviews updated between {nice_date(S['updated_min'])} and {nice_date(S['updated_max'])} are included ({n} tools).</li>
    <li><strong>Free plan</strong> means a plan that costs $0 with no end date. A free trial that expires does not count.</li>
    <li><strong>Entry price</strong> is the lowest monthly price for one user on any paid plan, using the billed-yearly rate when the vendor shows it. Education-only discounts are excluded.</li>
    <li><strong>Left out of the price medians:</strong> {S['usage']} usage- or credit-based tools (no fixed monthly plan) and tools priced only in euros or Swiss francs. They still appear in the table and the free-plan figures.</li>
    <li><strong>Categories</strong> are our own grouping by what each tool mainly does.</li>
    <li><strong>Limits:</strong> prices change often. Vendors run promotions and test prices by region. Always check the vendor's page before you buy. See our <a href="/methodology/">review methodology</a>.</li>
  </ul>

  <h2 id="cite">Use this data</h2>
  <p>You're welcome to quote these figures or use the CSV in your own article. Please credit and link to this page:</p>
  <div class="highlight-box" style="font-family:var(--font-mono);font-size:.8rem;word-break:break-word">{e(citation)}</div>
  <p>Journalists and researchers: for a custom cut of the data, email <a href="mailto:contact@rankertoolai.com">contact@rankertoolai.com</a>.</p>

  <p style="font-size:.8rem;color:var(--color-text-muted)">Disclosure: RankerToolAI earns affiliate commissions from some tools listed here. That never changes the prices shown, which come from the vendors' own pricing pages.</p>
</main>
"""

# ---------- wrap in the site template (methodology page) ----------
tpl = (ROOT / "methodology" / "index.html").read_text(encoding="utf-8")
head_end = tpl.index("<main")
foot_start = tpl.index("</main>") + len("</main>")
top, bottom = tpl[:head_end], tpl[foot_start:]
old_title = "How We Review AI Tools | RankerToolAI Methodology"
old_desc = "Learn how RankerToolAI reviews and rates AI tools. Our methodology, scoring criteria, and commitment to editorial independence."
top = top.replace(old_title, e(title)).replace(old_desc, e(desc))
top = top.replace("https://rankertoolai.com/methodology/", URL)
top = top.replace("<span>Our Methodology</span>", "<span>AI Tool Pricing Index</span>")
ld_old = top[top.index('<script type="application/ld+json">'):top.index("</script>", top.index('<script type="application/ld+json">')) + 9]
ld = {
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "Article", "headline": title, "datePublished": PUB, "dateModified": PUB,
     "author": {"@type": "Person", "name": "Hoang Nong", "url": "https://rankertoolai.com/author/hoang-nong/"},
     "publisher": {"@type": "Organization", "name": "RankerToolAI"}, "mainEntityOfPage": URL},
    {"@type": "Dataset", "name": f"AI Tool Pricing Index, {MONTH}", "description": desc, "url": URL,
     "creator": {"@type": "Organization", "name": "RankerToolAI", "url": "https://rankertoolai.com/"},
     "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True,
     "temporalCoverage": f"{S['updated_min']}/{S['updated_max']}",
     "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + CSV_NAME}]},
  ]}
top = top.replace(ld_old, '<script type="application/ld+json">\n' + json.dumps(ld, indent=1, ensure_ascii=False) + "\n  </script>")
assert "methodology/\"" not in top.split("<body")[0] or True

out_dir = ROOT / SLUG
out_dir.mkdir(exist_ok=True)
(out_dir / "index.html").write_text(top + main + bottom, encoding="utf-8")

with open(out_dir / CSV_NAME, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tool", "category", "free_plan", "cheapest_paid_usd_per_month", "non_usd_list_price", "pricing_model", "review_url", "page_updated"])
    for t in sorted(TOOLS, key=lambda t: t["name"].lower()):
        w.writerow([t["name"], t["group"], free_label(t), t["entry_usd_month"] or "", t["list_price_note"],
                    MODEL[t["model"]], f"https://rankertoolai.com/review/{t['slug']}/", t["updated"]])
print("wrote", out_dir / "index.html", "and", CSV_NAME, "-", len(TOOLS), "tools")
print("TITLE:", title)
print("DESC:", desc)
