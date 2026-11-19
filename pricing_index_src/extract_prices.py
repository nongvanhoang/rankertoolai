"""Extract pricing tables from RankerToolAI review pages into JSON."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])

def text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

# category map from category hub pages
cat_of = {}
for c in sorted((ROOT / "category").iterdir()):
    f = c / "index.html"
    if c.is_dir() and f.exists():
        for slug in set(re.findall(r'href="/review/([a-z0-9-]+)/', f.read_text(encoding="utf-8"))):
            cat_of.setdefault(slug, c.name)

MONTH = r"(January|February|March|April|May|June|July|August|September|October|November|December)"

def monthly(price):
    """Return monthly USD for a price cell, None if not a number, 0 if free."""
    p = price.lower()
    if re.search(r"\bfree\b", p) and not re.search(r"\$\s*[1-9]", p):
        return 0.0
    # strip add-on charges like "+ $20/seat" so they are not read as the plan price
    p = re.sub(r"\+\s*\$\s*[0-9.,]+\s*/?\s*\w*", "", p)
    vals = []
    for m in re.finditer(r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:/|per)?\s*(?:seat|user|member|inbox)?\s*/?\s*(mo|month|yr|year|annual|one-time|lifetime|3mo)?\b(?!ly)", p):
        v = float(m.group(1).replace(",", ""))
        unit = m.group(2) or ""
        if unit in ("one-time", "lifetime"):
            continue
        if unit in ("yr", "year"):
            v = v / 12
        if unit == "3mo":
            v = v / 3
        vals.append(v)
    if not vals:
        return None
    return round(min(vals), 2)

rows = []
for d in sorted((ROOT / "review").iterdir()):
    f = d / "index.html"
    if not f.exists():
        continue
    src = f.read_text(encoding="utf-8")
    name_m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    name = text(name_m.group(1)) if name_m else d.name
    h2 = re.search(r"<h2[^>]*>[^<]*[Pp]ric[^<]*</h2>", src)
    plans = []
    note = ""
    if h2:
        after = src[h2.end():]
        t = re.search(r"<table.*?</table>", after, re.S)
        if t and t.start() < 6000:
            for tr in re.findall(r"<tr.*?</tr>", t.group(0), re.S):
                cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
                if len(cells) >= 2 and cells[0].lower() not in ("plan", "tier", "plans"):
                    plans.append({"plan": cells[0].replace("⭐", "").strip(), "price": cells[1], "details": " | ".join(cells[2:])})
            note = text(after[t.end():t.end() + 800])[:400]
    full = text(src)
    chk = re.search(r"checked on " + MONTH + r" (\d{1,2}), (20\d\d)", full)
    dm = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', src)
    vals = [monthly(p["price"]) for p in plans]
    paid = [v for v in vals if v and v > 0]
    low = full.lower()
    rows.append({
        "slug": d.name,
        "name": name,
        "category": cat_of.get(d.name, ""),
        "plans": plans,
        "note": note,
        "free_plan": any(v == 0 for v in vals) or bool(re.search(r"\bfree (plan|tier|forever)\b", " ".join(p["plan"] + " " + p["price"] for p in plans).lower())),
        "free_trial": bool(re.search(r"free trial", low)),
        "per_seat": any(re.search(r"seat|per user|/user", p["price"].lower()) for p in plans),
        "contact_sales": any(re.search(r"contact|custom|quote", p["price"].lower()) for p in plans),
        "entry_paid_monthly": min(paid) if paid else None,
        "top_listed_monthly": max(paid) if paid else None,
        "price_checked": " ".join(chk.groups()) if chk else "",
        "date_modified": dm.group(1) if dm else "",
    })

OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(rows), "tools;", sum(1 for r in rows if r["plans"]), "with plans;", sum(1 for r in rows if r["entry_paid_monthly"]), "with paid price")
