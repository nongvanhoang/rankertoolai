#!/usr/bin/env python3
"""
Build RankerToolAI site dashboard.
Scans html/ directory, runs SEO audit, outputs html/dashboard/index.html

Usage:
  python build_dashboard.py
"""
import os, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from datetime import datetime

HTML_DIR = Path(__file__).parent / "html"
OUT_FILE = HTML_DIR / "dashboard" / "index.html"
SECTIONS = ["review", "compare", "alternatives", "best", "category"]

AFFILIATE_DB = {
    "jasper":           {"commission": "30% recurring", "status": "active",  "priority": 1, "color": "green"},
    "writesonic":       {"commission": "30% recurring", "status": "active",  "priority": 1, "color": "green"},
    "surfer-seo":       {"commission": "25% recurring", "status": "active",  "priority": 1, "color": "green"},
    "semrush":          {"commission": "40% recurring", "status": "pending", "priority": 1, "color": "orange"},
    "elevenlabs":       {"commission": "22% / 12mo",   "status": "active",  "priority": 2, "color": "green"},
    "copy-ai":          {"commission": "20% recurring", "status": "active",  "priority": 2, "color": "green"},
    "notion":           {"commission": "$10/referral",  "status": "active",  "priority": 2, "color": "green"},
    "canva-ai":         {"commission": "15%/sale",      "status": "pending", "priority": 2, "color": "orange"},
    "pictory":          {"commission": "20% recurring", "status": "active",  "priority": 3, "color": "green"},
    "runway":           {"commission": "TBD",           "status": "pending", "priority": 3, "color": "orange"},
    "grammarly":        {"commission": "$0.20 CPA",     "status": "active",  "priority": 3, "color": "green"},
    "cursor":           {"commission": "varies",        "status": "active",  "priority": 2, "color": "green"},
    "midjourney":       {"commission": "no program",    "status": "none",    "priority": 3, "color": "gray"},
    "chatgpt":          {"commission": "no program",    "status": "none",    "priority": 1, "color": "gray"},
    "claude":           {"commission": "no program",    "status": "none",    "priority": 1, "color": "gray"},
    "gemini":           {"commission": "no program",    "status": "none",    "priority": 1, "color": "gray"},
    "mangools":         {"commission": "30% recurring", "status": "active",  "priority": 1, "color": "green"},
    "se-ranking":       {"commission": "30% recurring", "status": "active",  "priority": 2, "color": "green"},
    "github-copilot":   {"commission": "no program",    "status": "none",    "priority": 2, "color": "gray"},
}

MIN_WORDS = {"review": 1500, "compare": 2000, "alternatives": 2500, "best": 2000, "category": 1000}

# ── Data collection ────────────────────────────────────────────────────────────

def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return len(text.split())

def get_schema_types(html: str):
    scripts = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
    types = []
    for raw in scripts:
        try:
            obj = json.loads(raw.strip())
            t = obj.get("@type", "")
            if isinstance(t, list):
                types.extend(t)
            elif t:
                types.append(t)
        except:
            pass
    return types

def count_affiliate_links(html: str) -> int:
    return len(re.findall(r'href=["\'][^"\']*\/go\/[^"\']+["\']', html, re.IGNORECASE))

def get_meta(html: str, name: str) -> str:
    m = re.search(rf'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    return m.group(1) if m else ""

def scan_pages():
    pages = []
    for section in SECTIONS:
        d = HTML_DIR / section
        if not d.exists():
            continue
        for slug in sorted(os.listdir(d)):
            if slug == "index.html":
                continue
            p = d / slug / "index.html"
            if not p.exists():
                continue
            html = p.read_text(encoding="utf-8", errors="replace")
            wc = word_count(html)
            min_wc = MIN_WORDS.get(section, 1000)
            schema_types = get_schema_types(html)
            aff_links = count_affiliate_links(html)

            issues = []
            if wc < min_wc:
                issues.append(f"Short ({wc}w)")
            if "FAQPage" not in schema_types:
                issues.append("No FAQ schema")
            if section in ("review", "compare") and "Review" not in schema_types:
                issues.append("No Review schema")

            pages.append({
                "section": section,
                "slug": slug,
                "wc": wc,
                "min_wc": min_wc,
                "schemas": schema_types,
                "aff_links": aff_links,
                "issues": issues,
                "ok": len(issues) == 0,
            })
    return pages

def count_go_pages():
    go_dir = HTML_DIR / "go"
    if not go_dir.exists():
        return 0
    return sum(1 for x in os.listdir(go_dir) if (go_dir / x).is_dir())

def build_affiliate_table(pages):
    review_slugs = {p["slug"] for p in pages if p["section"] == "review"}
    compare_slugs = {p["slug"] for p in pages if p["section"] == "compare"}
    alt_slugs = {p["slug"] for p in pages if p["section"] == "alternatives"}

    rows = []
    for tool, info in sorted(AFFILIATE_DB.items(), key=lambda x: (x[1]["priority"], x[0])):
        has_review = tool in review_slugs
        has_compare = any(tool in s for s in compare_slugs)
        has_alt = tool in alt_slugs
        rows.append({
            "tool": tool,
            "commission": info["commission"],
            "status": info["status"],
            "priority": info["priority"],
            "color": info["color"],
            "has_review": has_review,
            "has_compare": has_compare,
            "has_alt": has_alt,
            "coverage": sum([has_review, has_compare, has_alt]),
        })
    return rows

# ── HTML generation ────────────────────────────────────────────────────────────

SECTION_COLORS = {
    "review": "#f97316",
    "compare": "#6366f1",
    "alternatives": "#22c55e",
    "best": "#eab308",
    "category": "#06b6d4",
}

def badge(text, color="#6366f1"):
    return f'<span style="background:rgba(99,102,241,0.15);color:{color};border:1px solid rgba(99,102,241,0.3);border-radius:6px;padding:0.15rem 0.5rem;font-size:0.72rem;font-weight:600;white-space:nowrap">{text}</span>'

def status_badge(status):
    if status == "active":
        return badge("ACTIVE", "#22c55e")
    elif status == "pending":
        return badge("PENDING", "#f97316")
    else:
        return badge("NONE", "#64748b")

def check_icon(ok):
    if ok:
        return '<span style="color:#22c55e;font-size:1rem">✓</span>'
    return '<span style="color:#ef4444;font-size:0.85rem">✗</span>'

def build_html(pages, affiliate_rows, generated_at):
    total = len(pages)
    passing = sum(1 for p in pages if p["ok"])
    pass_pct = round(passing / total * 100) if total else 0
    go_count = count_go_pages()

    section_counts = {}
    for p in pages:
        section_counts[p["section"]] = section_counts.get(p["section"], 0) + 1

    # Section summary cards HTML
    section_cards = ""
    for s, cnt in section_counts.items():
        col = SECTION_COLORS.get(s, "#6366f1")
        section_cards += f"""
        <div style="background:#0d1224;border:1px solid #1e293b;border-left:3px solid {col};border-radius:10px;padding:1rem 1.25rem;min-width:130px">
          <div style="font-size:1.8rem;font-weight:900;color:{col}">{cnt}</div>
          <div style="font-size:0.72rem;color:#64748b;text-transform:capitalize;margin-top:0.2rem">{s} pages</div>
        </div>"""

    # Content table rows
    content_rows = ""
    for p in pages:
        col = SECTION_COLORS.get(p["section"], "#6366f1")
        wc_pct = min(100, round(p["wc"] / p["min_wc"] * 100))
        bar_col = "#22c55e" if wc_pct >= 100 else "#f97316" if wc_pct >= 80 else "#ef4444"
        issues_html = " ".join(f'<span style="background:rgba(239,68,68,0.1);color:#f87171;border:1px solid rgba(239,68,68,0.2);border-radius:4px;padding:0.1rem 0.4rem;font-size:0.65rem">{i}</span>' for i in p["issues"]) or '<span style="color:#22c55e;font-size:0.72rem">✓ OK</span>'
        schemas_str = ", ".join(p["schemas"]) if p["schemas"] else "—"
        content_rows += f"""
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><span style="color:{col};font-size:0.7rem;font-weight:700;text-transform:uppercase">{p["section"]}</span></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.8rem;color:#cbd5e1"><a href="https://rankertoolai.com/{p['section']}/{p['slug']}/" target="_blank" style="color:#94a3b8;text-decoration:none">{p['slug']}</a></td>
          <td style="padding:0.65rem 0.75rem">
            <div style="display:flex;align-items:center;gap:0.5rem">
              <div style="flex:1;height:4px;background:#1e293b;border-radius:2px;min-width:50px"><div style="width:{wc_pct}%;height:4px;background:{bar_col};border-radius:2px"></div></div>
              <span style="font-size:0.72rem;color:#64748b;white-space:nowrap">{p['wc']:,}</span>
            </div>
          </td>
          <td style="padding:0.65rem 0.75rem;font-size:0.7rem;color:#475569">{schemas_str[:45]}{'…' if len(schemas_str) > 45 else ''}</td>
          <td style="padding:0.65rem 0.75rem;text-align:center;font-size:0.8rem;color:#94a3b8">{p['aff_links']}</td>
          <td style="padding:0.65rem 0.75rem">{issues_html}</td>
        </tr>"""

    # Affiliate table rows
    aff_rows_html = ""
    for r in affiliate_rows:
        col = "#22c55e" if r["color"] == "green" else "#f97316" if r["color"] == "orange" else "#475569"
        p_badge = badge(f"P{r['priority']}", col)
        aff_rows_html += f"""
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem">
            <div style="display:flex;align-items:center;gap:0.5rem">
              {p_badge}
              <span style="font-size:0.82rem;color:#cbd5e1;font-weight:600">{r['tool']}</span>
            </div>
          </td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#f97316;font-weight:600">{r['commission']}</td>
          <td style="padding:0.65rem 0.75rem">{status_badge(r['status'])}</td>
          <td style="padding:0.65rem 0.75rem;text-align:center">{check_icon(r['has_review'])}</td>
          <td style="padding:0.65rem 0.75rem;text-align:center">{check_icon(r['has_compare'])}</td>
          <td style="padding:0.65rem 0.75rem;text-align:center">{check_icon(r['has_alt'])}</td>
          <td style="padding:0.65rem 0.75rem">
            <div style="display:flex;gap:2px">
              {"".join(f'<div style="width:8px;height:8px;border-radius:2px;background:{"#22c55e" if i < r["coverage"] else "#1e293b"}"></div>' for i in range(3))}
            </div>
          </td>
        </tr>"""

    pass_color = "#22c55e" if pass_pct == 100 else "#f97316" if pass_pct >= 90 else "#ef4444"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>RankerToolAI — Site Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#060a14;color:#e2e8f0;min-height:100vh}}
::-webkit-scrollbar{{width:5px}}::-webkit-scrollbar-track{{background:#0a0f1e}}::-webkit-scrollbar-thumb{{background:#1e293b;border-radius:3px}}
a{{color:#f97316;text-decoration:none}}a:hover{{text-decoration:underline}}
.header{{background:#0a0f1e;border-bottom:1px solid #1e293b;padding:0.875rem 2rem;display:flex;align-items:center;gap:0.75rem;position:sticky;top:0;z-index:100}}
.logo{{font-weight:900;font-size:1.1rem;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.header-meta{{margin-left:auto;display:flex;align-items:center;gap:1rem}}
.ts{{font-size:0.72rem;color:#334155}}
.tab-bar{{display:flex;gap:0;border-bottom:1px solid #1e293b;background:#0a0f1e;padding:0 2rem}}
.tab{{padding:0.75rem 1.25rem;font-size:0.8rem;font-weight:600;color:#475569;cursor:pointer;border-bottom:2px solid transparent;transition:0.15s;white-space:nowrap}}
.tab:hover{{color:#94a3b8}}
.tab.active{{color:#f97316;border-bottom-color:#f97316}}
.panel{{display:none;padding:1.5rem 2rem;max-width:1400px;margin:0 auto}}
.panel.active{{display:block}}
.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:1.5rem}}
.metric{{background:#0d1224;border:1px solid #1e293b;border-radius:12px;padding:1.25rem 1.5rem}}
.metric-val{{font-size:2.25rem;font-weight:900;line-height:1}}
.metric-lbl{{font-size:0.72rem;color:#475569;margin-top:0.35rem;text-transform:uppercase;letter-spacing:0.05em}}
.metric-sub{{font-size:0.72rem;color:#334155;margin-top:0.25rem}}
.card{{background:#0d1224;border:1px solid #1e293b;border-radius:12px;overflow:hidden;margin-bottom:1.5rem}}
.card-hdr{{padding:1rem 1.25rem;border-bottom:1px solid #1e293b;display:flex;align-items:center;gap:0.75rem}}
.card-title{{font-size:0.85rem;font-weight:700;color:#f1f5f9}}
.card-meta{{font-size:0.72rem;color:#334155;margin-left:auto}}
table{{width:100%;border-collapse:collapse}}
th{{padding:0.65rem 0.75rem;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#334155;text-align:left;background:#080c18;border-bottom:1px solid #1e293b}}
tr:hover{{background:rgba(255,255,255,0.015)}}
.section-bar{{display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1.5rem}}
.link-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}
.link-card{{background:#0d1224;border:1px solid #1e293b;border-radius:10px;padding:1.25rem;display:flex;flex-direction:column;gap:0.5rem}}
.link-card a{{color:#f97316;font-weight:700;font-size:0.9rem}}
.link-card p{{font-size:0.78rem;color:#475569;line-height:1.5}}
.cmd{{background:#080c18;border:1px solid #1e293b;border-radius:6px;padding:0.5rem 0.75rem;font-family:monospace;font-size:0.78rem;color:#94a3b8;margin-top:0.5rem}}
.issues-summary{{display:flex;flex-wrap:wrap;gap:0.5rem;padding:1rem 1.25rem}}
.filter-row{{display:flex;gap:0.5rem;padding:0.75rem 1.25rem;border-bottom:1px solid #1e293b;flex-wrap:wrap}}
.filter-btn{{font-size:0.72rem;font-weight:600;padding:0.3rem 0.75rem;border-radius:20px;border:1px solid #1e293b;background:transparent;color:#475569;cursor:pointer;transition:0.15s}}
.filter-btn:hover,.filter-btn.on{{background:rgba(249,115,22,0.1);border-color:rgba(249,115,22,0.3);color:#f97316}}
.search{{font-size:0.78rem;background:#080c18;border:1px solid #1e293b;border-radius:6px;padding:0.3rem 0.6rem;color:#94a3b8;outline:none;width:200px}}
.search:focus{{border-color:#334155}}
.ga-frame{{width:100%;height:600px;border:none;border-radius:8px;background:#0d1224}}
</style>
</head>
<body>

<div class="header">
  <div class="logo">RankerToolAI</div>
  <span style="color:#1e293b;font-size:1.2rem">|</span>
  <span style="font-size:0.8rem;font-weight:600;color:#475569">Site Dashboard</span>
  <div class="header-meta">
    <span class="ts">Generated: {generated_at}</span>
    <a href="/" style="font-size:0.78rem;color:#334155">← Live Site</a>
  </div>
</div>

<div class="tab-bar">
  <div class="tab active" onclick="showTab('overview')">Overview</div>
  <div class="tab" onclick="showTab('content')">Content ({total})</div>
  <div class="tab" onclick="showTab('affiliate')">Affiliate ({len(affiliate_rows)})</div>
  <div class="tab" onclick="showTab('analytics')">Analytics</div>
  <div class="tab" onclick="showTab('tools')">Quick Actions</div>
</div>

<!-- OVERVIEW -->
<div class="panel active" id="tab-overview">
  <div class="metric-grid">
    <div class="metric">
      <div class="metric-val" style="color:#f97316">{total}</div>
      <div class="metric-lbl">Total Content Pages</div>
      <div class="metric-sub">{go_count} go/ redirects</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:{pass_color}">{pass_pct}%</div>
      <div class="metric-lbl">SEO Audit Pass Rate</div>
      <div class="metric-sub">{passing}/{total} pages passing</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#22c55e">{sum(1 for r in affiliate_rows if r['status']=='active')}</div>
      <div class="metric-lbl">Active Affiliates</div>
      <div class="metric-sub">{sum(1 for r in affiliate_rows if r['status']=='pending')} pending approval</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#6366f1">{section_counts.get('compare',0)}</div>
      <div class="metric-lbl">Compare Pages</div>
      <div class="metric-sub">Highest buyer intent</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#eab308">{section_counts.get('review',0)}</div>
      <div class="metric-lbl">Review Pages</div>
      <div class="metric-sub">Core affiliate content</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#06b6d4">{section_counts.get('alternatives',0)+section_counts.get('best',0)}</div>
      <div class="metric-lbl">Alt + Best Pages</div>
      <div class="metric-sub">Comparison funnel</div>
    </div>
  </div>

  <div class="section-bar">
    {section_cards}
  </div>

  <div class="card">
    <div class="card-hdr">
      <span class="card-title">Content Breakdown</span>
      <span class="card-meta">{total} pages scanned</span>
    </div>
    <div style="padding:1.25rem;display:flex;gap:1rem;flex-wrap:wrap">
      {chr(10).join(f'''<div style="flex:1;min-width:160px">
        <div style="font-size:0.72rem;color:#475569;margin-bottom:0.35rem;text-transform:capitalize">{s}</div>
        <div style="background:#1e293b;border-radius:4px;height:8px;overflow:hidden">
          <div style="width:{round(section_counts.get(s,0)/total*100)}%;height:8px;background:{SECTION_COLORS.get(s,'#6366f1')};border-radius:4px"></div>
        </div>
        <div style="font-size:0.72rem;color:#334155;margin-top:0.25rem">{section_counts.get(s,0)} pages · {round(section_counts.get(s,0)/total*100)}%</div>
      </div>''' for s in SECTIONS)}
    </div>
  </div>

  <div class="card">
    <div class="card-hdr"><span class="card-title">SEO Issues Summary</span></div>
    <div class="issues-summary">
      {_issues_summary(pages)}
    </div>
  </div>
</div>

<!-- CONTENT -->
<div class="panel" id="tab-content">
  <div class="card">
    <div class="card-hdr">
      <span class="card-title">All Pages</span>
      <span class="card-meta">{total} total</span>
    </div>
    <div class="filter-row">
      <input class="search" type="text" placeholder="Filter by slug..." oninput="filterTable(this.value)" id="search-content">
      {"".join(f'<button class="filter-btn on" onclick="toggleSection(this,\'{s}\')" data-section="{s}">{s}</button>' for s in SECTIONS)}
      <button class="filter-btn" onclick="filterIssuesOnly(this)" id="btn-issues">Issues only</button>
    </div>
    <div style="overflow-x:auto">
    <table id="content-table">
      <thead>
        <tr>
          <th style="width:90px">Type</th>
          <th>Page</th>
          <th style="width:160px">Word Count</th>
          <th>Schema</th>
          <th style="width:60px;text-align:center">Aff.</th>
          <th style="width:200px">Status</th>
        </tr>
      </thead>
      <tbody>
        {content_rows}
      </tbody>
    </table>
    </div>
  </div>
</div>

<!-- AFFILIATE -->
<div class="panel" id="tab-affiliate">
  <div class="metric-grid">
    <div class="metric">
      <div class="metric-val" style="color:#22c55e">{sum(1 for r in affiliate_rows if r['status']=='active')}</div>
      <div class="metric-lbl">Active Programs</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#f97316">{sum(1 for r in affiliate_rows if r['status']=='pending')}</div>
      <div class="metric-lbl">Pending Approval</div>
      <div class="metric-sub">Need to join</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#6366f1">{sum(1 for r in affiliate_rows if r['has_review'])}</div>
      <div class="metric-lbl">Have Review Page</div>
    </div>
    <div class="metric">
      <div class="metric-val" style="color:#eab308">{sum(1 for r in affiliate_rows if r['has_compare'])}</div>
      <div class="metric-lbl">Have Compare Page</div>
    </div>
  </div>

  <div class="card">
    <div class="card-hdr"><span class="card-title">Affiliate Programs</span><span class="card-meta">Sorted by priority</span></div>
    <div style="overflow-x:auto">
    <table>
      <thead>
        <tr>
          <th>Tool</th>
          <th style="width:160px">Commission</th>
          <th style="width:110px">Status</th>
          <th style="width:70px;text-align:center">Review</th>
          <th style="width:70px;text-align:center">Compare</th>
          <th style="width:70px;text-align:center">Alts</th>
          <th style="width:90px">Coverage</th>
        </tr>
      </thead>
      <tbody>{aff_rows_html}</tbody>
    </table>
    </div>
  </div>

  <div class="card" style="margin-top:1rem">
    <div class="card-hdr"><span class="card-title">Action Required</span></div>
    <div style="padding:1.25rem;display:flex;flex-direction:column;gap:0.75rem">
      <div style="background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.2);border-radius:8px;padding:1rem">
        <div style="font-size:0.82rem;font-weight:700;color:#f97316;margin-bottom:0.35rem">Semrush — 40% Recurring (Highest Commission)</div>
        <div style="font-size:0.78rem;color:#64748b">Status: Pending. Join at <a href="https://impact.com" target="_blank">impact.com</a> → search "Semrush". Replace redirect URL in html/go/semrush/index.html with your Impact Radius tracking link.</div>
      </div>
      <div style="background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.2);border-radius:8px;padding:1rem">
        <div style="font-size:0.82rem;font-weight:700;color:#f97316;margin-bottom:0.35rem">Canva — 15%/sale</div>
        <div style="font-size:0.78rem;color:#64748b">Status: Pending. Apply at canva.com/affiliates. Replace ?via=rankertoolai with your official affiliate link from the dashboard.</div>
      </div>
    </div>
  </div>
</div>

<!-- ANALYTICS -->
<div class="panel" id="tab-analytics">
  <div style="margin-bottom:1rem;padding:1rem;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);border-radius:10px;font-size:0.82rem;color:#94a3b8">
    GA4 property: <strong style="color:#f97316">G-81KB8ECCVF</strong> · Clarity: <strong style="color:#f97316">x97zf4vn2v</strong> · Cần login Google Account để xem data.
  </div>

  <div class="link-grid" style="margin-bottom:1.5rem">
    <div class="link-card">
      <a href="https://analytics.google.com/analytics/web/" target="_blank">GA4 Dashboard →</a>
      <p>Sessions, users, pageviews, bounce rate. Xem tab Realtime để thấy người dùng đang online ngay lúc này.</p>
    </div>
    <div class="link-card">
      <a href="https://search.google.com/search-console/performance/search-analytics" target="_blank">Google Search Console →</a>
      <p>Impressions, clicks, CTR, average position. Filter by Page để xem keyword nào rank cho từng review page.</p>
    </div>
    <div class="link-card">
      <a href="https://clarity.microsoft.com" target="_blank">Microsoft Clarity →</a>
      <p>Session recordings + heatmaps. Xem user thực sự làm gì: click đâu, scroll đến đâu, rage click. ID: x97zf4vn2v</p>
    </div>
    <div class="link-card">
      <a href="https://dash.cloudflare.com" target="_blank">Cloudflare Analytics →</a>
      <p>Total requests, bandwidth, bot vs human traffic. Không cần JS — track cả các visit bị adblock chặn GA4.</p>
    </div>
  </div>

  <div class="card">
    <div class="card-hdr"><span class="card-title">Events đang track — Cách xem trong GA4</span><span class="card-meta">GA4 → Reports → Engagement → Events</span></div>
    <table>
      <thead><tr><th>Event</th><th>Ý nghĩa</th><th>Cách xem trong GA4</th><th>Dùng để làm gì</th></tr></thead>
      <tbody>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#f97316;font-size:0.78rem">affiliate_click</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Click vào /go/ link từ review/compare pages</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → affiliate_click → dim: event_label = tool name</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Tool nào được click nhiều nhất</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#6366f1;font-size:0.78rem">cta_click</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Click CTA với context vị trí (hero/verdict/table/faq...)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → cta_click → dim: cta_context</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">CTA ở vị trí nào convert tốt nhất</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#22c55e;font-size:0.78rem">scroll_depth</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Scroll đến 25% / 50% / 75% / 95% trang</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → scroll_depth → dim: depth_pct</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">User đọc đến đâu thì bỏ — biết chỗ nào cần cải thiện</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#22c55e;font-size:0.78rem">engaged</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Ở lại page 15s / 30s / 60s / 120s / 300s</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → engaged → dim: seconds</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Content quality: user có thực sự đọc không</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#eab308;font-size:0.78rem">form_submit</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Submit newsletter form (inline + exit popup)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → form_submit → dim: form_id</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Email list growth rate</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#eab308;font-size:0.78rem">form_start</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">User click vào ô email (intent to subscribe)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → form_start</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">form_start ÷ form_submit = completion rate</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#06b6d4;font-size:0.78rem">outbound_click</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Click link ra ngoài không qua /go/ (chatgpt.com, etc.)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → outbound_click → dim: outbound_domain</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">User thoát sang đâu — cơ hội thêm affiliate link</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#06b6d4;font-size:0.78rem">internal_navigate</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Click link nội bộ (review→compare→alternatives)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → internal_navigate → dim: destination</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">User journey funnel: đọc review → đi đâu tiếp</td>
        </tr>
        <tr style="border-bottom:1px solid #0d1224">
          <td style="padding:0.65rem 0.75rem"><code style="color:#94a3b8;font-size:0.78rem">site_search</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Tìm kiếm trên site (search overlay)</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → site_search → dim: search_term</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Keyword gap: user tìm gì nhưng chưa có trang</td>
        </tr>
        <tr>
          <td style="padding:0.65rem 0.75rem"><code style="color:#94a3b8;font-size:0.78rem">faq_expand</code></td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#94a3b8">Click mở FAQ item</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">Events → faq_expand → dim: faq_question</td>
          <td style="padding:0.65rem 0.75rem;font-size:0.78rem;color:#64748b">FAQ nào được xem nhiều nhất</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card" style="margin-top:1.5rem">
    <div class="card-hdr"><span class="card-title">Cách xem user journey trong GA4</span></div>
    <div style="padding:1.25rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;font-size:0.8rem">
      <div style="background:#080c18;border-radius:8px;padding:1rem">
        <div style="color:#f97316;font-weight:700;margin-bottom:0.5rem">Traffic vào từ đâu</div>
        <div style="color:#64748b;line-height:1.8">GA4 → Reports → Acquisition → Traffic Acquisition<br>Phân tích: Organic Search / Direct / Social / Referral</div>
      </div>
      <div style="background:#080c18;border-radius:8px;padding:1rem">
        <div style="color:#6366f1;font-weight:700;margin-bottom:0.5rem">Trang nào được xem nhiều</div>
        <div style="color:#64748b;line-height:1.8">GA4 → Reports → Engagement → Pages and Screens<br>Sort by Views → xem top review pages</div>
      </div>
      <div style="background:#080c18;border-radius:8px;padding:1rem">
        <div style="color:#22c55e;font-weight:700;margin-bottom:0.5rem">User làm gì trên page</div>
        <div style="color:#64748b;line-height:1.8">Clarity → Recordings → filter by page<br>Xem session recording theo từng review page</div>
      </div>
      <div style="background:#080c18;border-radius:8px;padding:1rem">
        <div style="color:#eab308;font-weight:700;margin-bottom:0.5rem">Funnel affiliate</div>
        <div style="color:#64748b;line-height:1.8">GA4 → Explore → Funnel Exploration<br>Step 1: page_view (review) → Step 2: cta_click → Step 3: affiliate_click</div>
      </div>
    </div>
  </div>

  <div class="card" style="margin-top:1.5rem">
    <div class="card-hdr"><span class="card-title">Heatmap & Session Recording</span><span class="card-meta">Microsoft Clarity — không cần setup thêm</span></div>
    <div style="padding:1.25rem;font-size:0.82rem;color:#64748b;line-height:1.8">
      <p>Clarity đã được cài trên toàn bộ site (ID: <code style="color:#f97316">x97zf4vn2v</code>). Vào <a href="https://clarity.microsoft.com" target="_blank" style="color:#f97316">clarity.microsoft.com</a> → chọn project rankertoolai.com:</p>
      <ul style="margin:0.5rem 0 0 1.25rem;display:flex;flex-direction:column;gap:0.35rem">
        <li><strong style="color:#94a3b8">Heatmaps</strong> — xem user click đâu, scroll đến đâu trên từng trang</li>
        <li><strong style="color:#94a3b8">Recordings</strong> — xem lại toàn bộ session của từng user (ẩn danh)</li>
        <li><strong style="color:#94a3b8">Rage clicks</strong> — chỗ nào user click nhiều lần liên tiếp (UX bug)</li>
        <li><strong style="color:#94a3b8">Dead clicks</strong> — click vào element không có action</li>
      </ul>
    </div>
  </div>
</div>

<!-- TOOLS -->
<div class="panel" id="tab-tools">
  <div class="link-grid">
    <div class="link-card">
      <a href="#" onclick="copyCmd('python seo_audit.py --fail-only');return false">Run SEO Audit →</a>
      <p>Scan all 87 pages for critical issues. Shows only failing pages.</p>
      <div class="cmd">python seo_audit.py --fail-only</div>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('python generate_sitemap.py && python build_dashboard.py');return false">Refresh Dashboard →</a>
      <p>Regenerate sitemap + rebuild this dashboard with latest data.</p>
      <div class="cmd">python generate_sitemap.py && python build_dashboard.py</div>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('npx wrangler pages deploy html/ --project-name=rankertoolai');return false">Deploy to Cloudflare →</a>
      <p>Deploy all changes to rankertoolai.com via Cloudflare Pages.</p>
      <div class="cmd">npx wrangler pages deploy html/ --project-name=rankertoolai</div>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('python after_deploy.py');return false">Post-Deploy Ping →</a>
      <p>Verify HTTP 200, ping IndexNow (Bing + Google), trigger social post.</p>
      <div class="cmd">python after_deploy.py</div>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('python fix_schema_blocks.py');return false">Fix Schema Blocks →</a>
      <p>Convert @graph JSON-LD to separate blocks for correct schema detection.</p>
      <div class="cmd">python fix_schema_blocks.py</div>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('python gsc_tracker.py');return false">GSC Tracker →</a>
      <p>Pull ranking data from Google Search Console. Requires client_secret.json OAuth setup.</p>
      <div class="cmd">python gsc_tracker.py</div>
    </div>
    <div class="link-card">
      <a href="https://rankertoolai.com" target="_blank">Live Site →</a>
      <p>Open rankertoolai.com in a new tab to verify deployed changes.</p>
    </div>
    <div class="link-card">
      <a href="#" onclick="copyCmd('python seo_audit.py --csv audit_results.csv');return false">Export Audit CSV →</a>
      <p>Export full audit results to CSV for spreadsheet analysis.</p>
      <div class="cmd">python seo_audit.py --csv audit_results.csv</div>
    </div>
  </div>

  <div class="card" style="margin-top:1.5rem">
    <div class="card-hdr"><span class="card-title">Content Pipeline</span></div>
    <div style="padding:1.25rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;font-size:0.8rem">
      <div>
        <div style="color:#f97316;font-weight:700;margin-bottom:0.35rem">P1 — High Revenue</div>
        <div style="color:#64748b;line-height:1.8">/compare/jasper-vs-writesonic/<br>/alternatives/jasper/<br>/alternatives/chatgpt/<br>/compare/semrush-vs-ahrefs/</div>
      </div>
      <div>
        <div style="color:#6366f1;font-weight:700;margin-bottom:0.35rem">P2 — Content Gaps</div>
        <div style="color:#64748b;line-height:1.8">/review/perplexity/<br>/review/adobe-firefly/<br>/best/ai-tools-for-marketers/<br>/compare/cursor-vs-replit/</div>
      </div>
      <div>
        <div style="color:#22c55e;font-weight:700;margin-bottom:0.35rem">P3 — Authority Build</div>
        <div style="color:#64748b;line-height:1.8">/category/ai-writing/<br>/blog/ content<br>/best/free-ai-tools/<br>/pricing/ pages</div>
      </div>
    </div>
  </div>
</div>

<script>
function showTab(name) {{
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  event.currentTarget.classList.add('active');
}}

let sectionFilters = new Set({json.dumps(SECTIONS)});
let issuesOnly = false;

function filterTable(q) {{
  const rows = document.querySelectorAll('#content-table tbody tr');
  rows.forEach(r => {{
    const slug = r.cells[1]?.textContent.toLowerCase() || '';
    const section = r.cells[0]?.textContent.toLowerCase().trim() || '';
    const hasIssue = r.cells[5]?.querySelector('span[style*="ef4444"]');
    const matchSearch = !q || slug.includes(q.toLowerCase());
    const matchSection = sectionFilters.has(section);
    const matchIssue = !issuesOnly || hasIssue;
    r.style.display = matchSearch && matchSection && matchIssue ? '' : 'none';
  }});
}}

function toggleSection(btn, section) {{
  btn.classList.toggle('on');
  if (sectionFilters.has(section)) sectionFilters.delete(section);
  else sectionFilters.add(section);
  filterTable(document.getElementById('search-content').value);
}}

function filterIssuesOnly(btn) {{
  issuesOnly = !issuesOnly;
  btn.classList.toggle('on');
  filterTable(document.getElementById('search-content').value);
}}

function copyCmd(cmd) {{
  navigator.clipboard.writeText(cmd).then(() => {{
    const toast = document.createElement('div');
    toast.textContent = 'Copied!';
    toast.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;background:#22c55e;color:#fff;padding:0.5rem 1rem;border-radius:6px;font-size:0.8rem;font-weight:700;z-index:999;transition:opacity 0.3s';
    document.body.appendChild(toast);
    setTimeout(() => {{ toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }}, 1500);
  }});
}}
</script>
</body>
</html>"""


def _issues_summary(pages):
    issue_counts = {}
    for p in pages:
        for issue in p["issues"]:
            key = re.sub(r'\d+', 'N', issue)
            issue_counts[key] = issue_counts.get(key, 0) + 1

    if not issue_counts:
        return '<div style="color:#22c55e;font-size:0.85rem;font-weight:700">✓ All pages passing — no critical issues found</div>'

    html = ""
    for issue, cnt in sorted(issue_counts.items(), key=lambda x: -x[1]):
        col = "#ef4444" if cnt > 5 else "#f97316" if cnt > 2 else "#eab308"
        html += f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:0.5rem 0.75rem;display:flex;align-items:center;gap:0.5rem"><span style="font-size:1rem;font-weight:900;color:{col}">{cnt}</span><span style="font-size:0.78rem;color:#94a3b8">{issue}</span></div>'
    return html


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Scanning pages...")
    pages = scan_pages()
    affiliate_rows = build_affiliate_table(pages)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"Found {len(pages)} pages. Building dashboard...")
    html = build_html(pages, affiliate_rows, generated_at)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUT_FILE}")
    print(f"Deploy → open https://rankertoolai.com/dashboard/")
