#!/usr/bin/env python3
"""Joiin content cluster (2026-10-24): 4 landing pages so each Joiin XL ad group
lands on a page that matches its keywords instead of all 58 keywords hitting
/review/joiin/.
  /best/consolidation-software/                          — ledgers, multi-currency, group reporting, other-tool alternatives
  /alternatives/fathom/                                  — Fathom alternatives
  /blog/how-to-consolidate-multiple-xero-organisations/  — Xero consolidation guide
  /best/management-reporting-software-for-accountants/   — management reporting + budgeting groups
Shell copied from /best/web-hosting/ (same pattern as generate_dropmagic_extra.py).
Research-based, no hands-on test claims. Facts (checked 2026-10-24):
  Joiin: our /review/joiin/ (joiin.co/pricing 2026-10-01).
  Fathom: fathomhq.com/pricing page script, USD excl. tax (Pro tiers: Starter $59 for 1 +$59 each, Silver $315 for 10 +$31,
  Gold $450 for 25 +$17, Platinum $805 for 50 +$13, cheapest tier applies; Portfolio $67/100, $189/300, $405 -- no consolidation).
  Spotlight: spotlightreporting.com/pricing (NZD excl GST: Basic $329 up to 10 orgs, Super VCFO 25 $495, 75 $995) + /multi.
  Syft: Xero acquisition announced Sept 2024 (FNN/AAP); vendor pricing not visible, third-party trackers disagree -> no price quoted.
  LiveFlow: liveflow.com (QuickBooks Online, Google Sheets/Excel, consolidation; demo-based pricing).
  Xero: productideas.xero.com — consolidated reporting "not currently planned".
  Intuit Enterprise Suite: quickbooks.intuit.com multi-entity pages."""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))           # html/
OUT_ROOTS = [BASE]                                           # html/ only (root clone has diverged; it pulls from origin)
SITE = "https://rankertoolai.com"
TEMPLATE = "best/web-hosting/index.html"
GO = "/go/joiin/"


def read(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def faq_schema(faq):
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
        for q, a in faq]})


def crumbs_ld(items):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]})


def crumbs_nav(items):
    parts = [f'    <a href="{u}">{n}</a><span class="breadcrumb-sep">›</span>' for n, u in items[:-1]]
    parts.append(f"    <span>{items[-1][0]}</span>")
    return '<nav class="breadcrumb">\n' + "\n".join(parts) + "\n  </nav>"


def article_ld(headline, path):
    return ld({"@context": "https://schema.org", "@type": "Article", "headline": headline,
               "datePublished": "2026-10-24", "dateModified": "2026-10-24",
               "author": {"@type": "Organization", "name": "RankerToolAI", "url": SITE},
               "publisher": {"@type": "Organization", "name": "RankerToolAI", "url": SITE},
               "mainEntityOfPage": f"{SITE}/{path}/"})


def sub1(pattern, repl, s):
    new, n = re.subn(pattern, lambda m: repl, s, count=1, flags=re.S)
    assert n == 1, pattern
    return new


FOOTER = ('<div class="footer-col"><h5>This Category</h5><ul><li><a href="/review/joiin/">Joiin Review</a></li>'
          '<li><a href="/best/consolidation-software/">Consolidation Software</a></li>'
          '<li><a href="/alternatives/fathom/">Fathom Alternatives</a></li></ul></div>')


def build(path, title, desc, crumbs, schemas, main_html):
    s = read(TEMPLATE)
    url = f"{SITE}/{path}/"
    s = sub1(r"<title>.*?</title>", f"<title>{title}</title>", s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s)
    s = sub1(r'(  <script type="application/ld\+json">.*?</script>\n)+',
             "".join("  " + x + "\n" for x in schemas + [crumbs_ld(crumbs)]), s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', s)
    s = sub1(r'<nav class="breadcrumb">.*?</nav>', crumbs_nav(crumbs), s)
    s = sub1(r'<main .*?</main>', main_html.strip(), s)
    s = sub1(r'<div class="footer-col"><h5>This Category</h5>.*?</div>', FOOTER, s)
    s = re.sub(r"<span>Updated: [A-Za-z]+ 2026</span>", "<span>Updated: October 2026</span>", s)
    assert "Hosting" not in re.sub(r"<script.*?</script>", "", s, flags=re.S), path
    for root in OUT_ROOTS:
        out = os.path.join(root, path.replace("/", os.sep))
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(s)
        print("Wrote", os.path.join(out, "index.html"), len(s.split()), "words(raw)")


# ─────────────────────────── shared tool facts ───────────────────────────
JOIIN = dict(id="joiin", name="Joiin", featured=True, aff=True,
             cta=(GO, "Try Joiin Free for 14 Days →"), more=("/review/joiin/", "Read our Joiin review"))
FATHOM = dict(id="fathom", name="Fathom", featured=False, aff=False,
              cta=("https://www.fathomhq.com/", "Visit Fathom →"), more=("/alternatives/fathom/", "Fathom alternatives"))
SPOTLIGHT = dict(id="spotlight-reporting", name="Spotlight Reporting", featured=False, aff=False,
                 cta=("https://www.spotlightreporting.com/", "Visit Spotlight →"), more=None)
SYFT = dict(id="syft", name="Syft Analytics", featured=False, aff=False,
            cta=("https://www.syftanalytics.com/", "Visit Syft →"), more=None)
LIVEFLOW = dict(id="liveflow", name="LiveFlow", featured=False, aff=False,
                cta=("https://www.liveflow.com/", "Visit LiveFlow →"), more=None)
IES = dict(id="intuit-enterprise-suite", name="Intuit Enterprise Suite", featured=False, aff=False,
           cta=("https://quickbooks.intuit.com/see-all-product/", "Visit Intuit →"), more=None)


def card(t, i, badge, tagline, meta, tags, body, pros, cons):
    href, label = t["cta"]
    rel = "nofollow sponsored" if t["aff"] else "nofollow noopener"
    tags_html = "".join(f'<span class="tag">{x}</span>' for x in tags)
    more = f'\n          <a href="{t["more"][0]}" class="btn btn-secondary">{t["more"][1]}</a>' if t["more"] else ""
    li = lambda xs: "\n".join(f"          <li>{x}</li>" for x in xs)
    return f'''    <section id="{t["id"]}">
      <div class="tool-card{' featured' if t['featured'] else ''}">
        <div class="rank-badge{' top3' if i < 3 else ''}">#{i + 1} &middot; {badge}</div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;margin-bottom:1rem;">
          <div><h2 style="margin:0.5rem 0 0.25rem;">{i + 1}. {t["name"]}</h2><p style="color:var(--color-text-muted);margin:0;">{tagline}</p></div>
          <div class="tool-score">{meta}</div>
        </div>
        <div style="margin-bottom:1rem;">{tags_html}</div>
        {body}
        <h4>Pros</h4>
        <ul>
{li(pros)}
        </ul>
        <h4>Cons</h4>
        <ul>
{li(cons)}
        </ul>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.25rem;">
          <a href="{href}" class="btn btn-affiliate" rel="{rel}" target="_blank">{label}</a>{more}
        </div>
      </div>
    </section>
'''


def toc(items):
    return ('    <div class="toc" style="margin-bottom:2rem;">\n      <h4>Quick Navigation</h4>\n      <ol>\n'
            + "\n".join(f'        <li><a href="#{a}">{t}</a></li>' for a, t in items)
            + "\n      </ol>\n    </div>\n")


def faq_html(faq):
    return ('    <section id="faq">\n      <h2>FAQ</h2>\n'
            + "".join(f'      <div class="faq-item"><h3>{q}</h3><p>{a}</p></div>\n' for q, a in faq)
            + "    </section>\n")


def prose(heading, anchor, paras):
    body = "\n".join(p if p.lstrip().startswith("<") else
                     f'      <p style="color:var(--color-text-muted);line-height:1.8;">{p}</p>' for p in paras)
    return (f'    <section id="{anchor}" style="margin-top:3rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,0.08);">\n'
            f'      <h2 style="font-size:1.3rem;color:#f1f5f9;margin-bottom:1rem;">{heading}</h2>\n{body}\n    </section>\n')


def ul(items):
    return ('      <ul style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
            + "\n".join(f"        <li>{x}</li>" for x in items) + "\n      </ul>")


def table(head, rows, note):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "\n".join("            <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'''      <div style="overflow-x:auto;">
        <table class="comparison-table">
          <thead>
            <tr>{th}</tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
      </div>
      <p style="font-size:0.8rem;color:rgba(148,163,184,0.6);margin-top:0.5rem;">{note}</p>'''


def cta_box(q, sub, label="Start a Free Joiin Trial →"):
    return f'''    <div style="background:linear-gradient(135deg,rgba(74,222,128,0.10),rgba(34,197,94,0.05));border:1px solid rgba(74,222,128,0.3);border-radius:var(--radius-lg);padding:1.5rem;margin:2rem 0;text-align:center;">
      <p style="margin:0 0 0.25rem;font-weight:700;font-size:1.1rem;color:#f1f5f9;">{q}</p>
      <p style="margin:0 0 1rem;font-size:0.875rem;color:rgba(148,163,184,0.8);">{sub}</p>
      <a href="{GO}" class="btn btn-primary" rel="nofollow sponsored" target="_blank" style="font-weight:800;padding:0.75rem 2rem;">{label}</a>
      <p style="margin:0.75rem 0 0;font-size:0.75rem;color:rgba(148,163,184,0.6);">Affiliate link. We may earn a commission at no extra cost to you.</p>
    </div>
'''


def related(items):
    cards = "\n".join(f'        <a href="{u}" class="related-card"><div class="related-card-label">{l}</div><div class="related-card-title">{t}</div></a>'
                      for u, l, t in items)
    return f'''    <div style="margin-top:3rem;">
      <h3>Related</h3>
      <div class="related-grid">
{cards}
      </div>
    </div>
'''


def page(h1, byline, intro_box, sections):
    return f'''<main class="container" style="padding-top:1rem;padding-bottom:4rem;">
  <div style="max-width:760px;">
    <h1 style="font-size:clamp(1.6rem,4vw,2.25rem);margin-bottom:0.5rem;">{h1}</h1>
    <p style="color:var(--color-text-muted);font-size:1rem;margin-bottom:0.5rem;">{byline}</p>
    <p style="font-size:0.8rem;color:rgba(148,163,184,0.7);margin-bottom:1rem;">Disclosure: this page contains affiliate links, including to Joiin. We may earn a commission if you buy through them, at no extra cost to you. <a href="/affiliate-disclosure/">Read our disclosure</a>.</p>

    <div class="winner-box">
      <strong style="color:#4ade80;">Quick Answer</strong>
      <p style="margin:0.5rem 0 0;color:#e2e8f0;font-size:0.9rem;">{intro_box}</p>
    </div>

{"".join(sections)}  </div>
</main>'''


BYLINE = ("Independent guide by RankerToolAI · Updated October 2026 · Based on each vendor's published pricing and "
          "feature pages, not a hands-on test. See our <a href=\"/methodology/\">methodology</a>.")

# Joiin card text reused across pages
JOIIN_BODY = ("<p>Joiin connects to the ledgers of every company in a group and produces one consolidated set of reports. "
              "Its pricing page lists ten accounting connections: Xero, QuickBooks, Intuit Enterprise Suite, Sage, MYOB, FreeAgent, "
              "Puzzle, Pennylane, Zoho Books and Fortnox, so entities don't have to share a system. Chart of accounts mapping and "
              "intercompany eliminations are on every plan, along with P&amp;L, balance sheet, cash flow, trial balance, KPIs, budgets, "
              "dashboards and report packs. Users, reports and clients are unlimited, and the price depends only on plan and company count: "
              "Billed annually it's $23/mo for one company, $29/mo for two, $92/mo for ten and $252/mo for 100 ($28/mo for one company billed monthly). "
              "Multi-currency starts on Pro, and the 14-day trial runs on Max with no credit card.</p>")
JOIIN_PROS = ["COA mapping and eliminations on every plan, not only the top tier",
              "Unlimited users, reports and clients, so firms aren't billed per seat",
              "Widest ledger list here, including Sage, MYOB and FreeAgent",
              "Lowest published entry price for real consolidation ($23/mo for one company, annual)",
              "14-day trial of the full Max plan, no card"]
JOIIN_CONS = ["Multi-currency needs Pro; Core reports in one currency",
              "Forecasting starts on Pro; API and BI connections are Max-only",
              "Separate prices for Core, Pro and Max are no longer listed",
              "White labelling is still marked coming soon"]

FATHOM_BODY = ("<p>Fathom is a long-established management reporting and forecasting tool used heavily by accounting firms. "
               "On its pricing page, <strong>Fathom Pro</strong> is priced in tiers by company count (USD, excluding sales tax): $59/month for one company "
               "(+$59 per extra), $315 for 10 (+$31 each extra), $450 for 25 (+$17) and $805 for 50 (+$13), and the cheapest tier for your count applies. "
               "Pro includes multi-currency consolidations with eliminations; consolidated groups are free to create. "
               "<strong>Fathom Portfolio</strong> is $67/month for 100 companies (about $0.67 each), but it doesn't include consolidations: "
               "you upgrade a company to Pro for that. Enterprise is custom-priced. Integrations listed include Xero, QuickBooks Online and "
               "Desktop, MYOB, FreeAgent and Excel. There's a 14-day free trial.</p>")
SPOTLIGHT_BODY = ("<p>Spotlight Reporting is an advisory suite from New Zealand covering reporting, forecasting and dashboards, with "
                  "<strong>Spotlight Multi</strong> for aggregating and benchmarking up to 500 entities, multi-currency included. Its pricing page "
                  "lists advisor plans in NZD excluding GST: Basic $329/month for up to 10 organisations, Super VCFO 25 at $495/month and "
                  "Super VCFO 75 at $995/month, with Enterprise on request. Integrations named are Xero and QuickBooks, and every plan has a "
                  "14-day free trial.</p>")
SYFT_BODY = ("<p>Syft Analytics covers dashboards, consolidations, forecasts and reports. Xero announced it was buying Syft in "
             "September 2024 (up to US$70 million) and said Syft would stay a standalone product for now while its features are folded "
             "into Xero over time. Syft doesn't show prices on its pricing page without a sign-up, and third-party trackers list "
             "contradictory figures, so we don't quote one here. Check which ledgers and currencies it supports for your group before "
             "you commit.</p>")
LIVEFLOW_BODY = ("<p>LiveFlow takes a different approach: instead of its own report builder, it syncs QuickBooks Online data into "
                 "Google Sheets and Excel in real time, and it lists multi-entity consolidation of QuickBooks companies as a feature. "
                 "It suits finance teams that already live in spreadsheets. Its site only mentions QuickBooks (plus a Ramp integration), "
                 "and pricing is quoted after a demo.</p>")

# ─────────────────────────── 1. /best/consolidation-software/ ───────────────────────────
P1 = "best/consolidation-software"
P1_FAQ = [
    ("What is the best consolidation software for small business groups?",
     "For most small and mid-sized groups, Joiin is the most direct fit: consolidation features (COA mapping and eliminations) are on every plan, it connects to ten ledgers including Xero, QuickBooks, Sage and MYOB, and published pricing starts at $23/mo for one company billed annually. Fathom and Spotlight are stronger choices for accounting firms that want a broad advisory suite and are happy to pay for a bundle of companies."),
    ("Can Xero consolidate multiple organisations on its own?",
     "No. Xero has no built-in consolidated reporting across organisations, and Xero has said on its product ideas forum that it isn't currently planned. Groups either combine exports in a spreadsheet or use a connected app such as Joiin, Fathom, Spotlight or Syft. See our guide to consolidating multiple Xero organisations."),
    ("Can I consolidate companies that use different accounting software?",
     "Yes, if the tool supports every ledger in your group. Joiin lists ten connections, including Xero, QuickBooks, Sage, MYOB and FreeAgent, so a group with one company on Xero and another on Sage can consolidate without migrating. Fathom lists Xero, QuickBooks, MYOB and FreeAgent. Always check every entity's system before you subscribe."),
    ("Do I need multi-currency consolidation?",
     "Only if a subsidiary keeps its books in a different currency. On Joiin, multi-currency starts on the Pro plan and Max adds your own FX rates. Fathom Pro and Spotlight Multi both include multi-currency."),
    ("How is consolidation software priced?",
     "Mostly by company count. Joiin charges per connected company with unlimited users. Fathom Pro is tiered: $59/month for one company, $315 for 10, $450 for 25 and $805 for 50, plus a fee per extra company. Spotlight's advisor plans are priced by number of organisations (from NZ$329/month for up to 10). Compare the price for your exact entity count, not the headline figure."),
    ("What does intercompany elimination mean?",
     "When companies in the same group trade with each other, those sales, costs, loans and balances would be double-counted if you simply added the ledgers together. Eliminations remove them so the consolidated figures only show the group's dealings with the outside world."),
]
P1_SECTIONS = [
    toc([("joiin", "Joiin: Best Overall for Multi-Entity Groups"), ("fathom", "Fathom: Best for Large Accounting Firms"),
         ("spotlight-reporting", "Spotlight Reporting: Best Advisory Suite"), ("syft", "Syft Analytics: Best for Xero-Centric Firms"),
         ("liveflow", "LiveFlow: Best for QuickBooks in Spreadsheets"), ("intuit-enterprise-suite", "Intuit Enterprise Suite: Native QuickBooks Route"),
         ("compare", "Comparison Table"), ("ledgers", "Sage, MYOB, FreeAgent and QuickBooks Groups"),
         ("multi-currency", "Multi-Currency and Group Reporting"), ("choose", "How to Choose"), ("faq", "FAQ")]),
    card(JOIIN, 0, "Best Overall", "Consolidated reporting across ten accounting systems", "From $23/mo",
         ["Per-company pricing", "Unlimited users", "10 ledgers", "14-day Max trial"], JOIIN_BODY, JOIIN_PROS, JOIIN_CONS),
    card(FATHOM, 1, "Best for Large Accounting Firms", "Management reporting, KPIs and forecasting for advisors", "Pro from $59/mo",
         ["Pro includes consolidation", "Multi-currency", "Xero · QBO · MYOB · FreeAgent"], FATHOM_BODY,
         ["Mature reporting and forecasting, widely used by advisors", "Pro includes multi-currency consolidations with eliminations",
          "Good value per company once you have 25+ clients on Pro"],
         ["Costs climb quickly for small groups: $295/month for 5 companies on Pro", "The cheaper Portfolio plan has no consolidation",
          "No Sage connection listed"]),
    card(SPOTLIGHT, 2, "Best Advisory Suite", "Reporting, forecasting, dashboards and Spotlight Multi", "From NZ$329/mo",
         ["Up to 10 orgs on Basic", "Multi-currency (Multi)", "Xero · QuickBooks"], SPOTLIGHT_BODY,
         ["Full advisory suite: reports, forecasts and dashboards", "Spotlight Multi aggregates up to 500 entities, built for franchises and networks",
          "Training and support included on advisor plans"],
         ["Plans are built for advisors, not a single business group", "Only Xero and QuickBooks named",
          "Intercompany eliminations aren't described on the Multi page"]),
    card(SYFT, 3, "Best for Xero-Centric Firms", "Dashboards, consolidations, forecasts and reports", "Now owned by Xero",
         ["Consolidations", "Dashboards", "Forecasts"], SYFT_BODY,
         ["Backed by Xero, so integration is likely to stay close", "Covers dashboards, reports, forecasts and consolidation in one tool"],
         ["Prices not shown publicly", "Long-term roadmap depends on how Xero folds it in"]),
    card(LIVEFLOW, 4, "Best for QuickBooks in Spreadsheets", "Live QuickBooks Online data in Google Sheets and Excel", "Demo-based pricing",
         ["QuickBooks Online", "Google Sheets &amp; Excel", "Consolidation"], LIVEFLOW_BODY,
         ["Keeps your existing spreadsheet models, refreshed live", "Consolidates multiple QuickBooks companies"],
         ["QuickBooks only, per its site", "You still build and maintain the reports yourself", "No public pricing"]),
    card(IES, 5, "Native QuickBooks Route", "Intuit's mid-market multi-entity product", "Separate product",
         ["Consolidated reporting", "Intercompany controls", "Replaces QBO"], (
         "<p>If your whole group is on QuickBooks and outgrowing it, Intuit Enterprise Suite is Intuit's own multi-entity product, "
         "with consolidated reporting, automated allocations and controls for intercompany transactions. It's a separate, higher-priced "
         "subscription that replaces QuickBooks Online rather than an add-on, so it's a migration decision, not a reporting tool. "
         "Joiin also lists Intuit Enterprise Suite as a connection, which helps if part of the group moves and the rest doesn't.</p>"),
         ["Consolidation inside the ledger itself", "No second tool to sync"],
         ["Means migrating your books", "QuickBooks-only groups; no help for Xero or Sage entities"]),
    f'''    <section id="compare">
      <h2>Comparison Table</h2>
{table(["Tool", "Ledgers named", "Consolidation", "Multi-currency", "Published entry price"], [
        ["<strong>Joiin</strong>", "Xero, QuickBooks, Intuit Enterprise Suite, Sage, MYOB, FreeAgent, Puzzle, Pennylane, Zoho Books, Fortnox", "Every plan", "Pro and Max", "$23/mo, 1 company (annual)"],
        ["<strong>Fathom</strong>", "Xero, QuickBooks, MYOB, FreeAgent, Excel", "Pro and Enterprise", "Pro", "Pro $59/mo (1 company)"],
        ["<strong>Spotlight</strong>", "Xero, QuickBooks", "Yes (Spotlight Multi)", "Multi", "NZ$329/mo, up to 10 orgs"],
        ["<strong>Syft</strong>", "Check with vendor", "Yes", "Check with vendor", "Not published"],
        ["<strong>LiveFlow</strong>", "QuickBooks Online", "Yes", "Not stated", "Demo / quote"],
        ["<strong>Intuit Enterprise Suite</strong>", "Its own ledger", "Yes", "Check with Intuit", "Quote"],
    ], "Prices as shown on each vendor's pricing page in October 2026 (Spotlight in NZD excluding GST; Joiin and Fathom before sales tax). Confirm current pricing with each vendor before you buy.")}
    </section>
''',
    cta_box("Want to see your own group consolidated?", "Joiin's 14-day trial runs on the full Max plan with no credit card. Connect your entities and check the consolidated P&amp;L before you pay."),
    prose("Sage, MYOB, FreeAgent and QuickBooks Groups", "ledgers", [
        "Most consolidation tools grew up around Xero and QuickBooks, so the ledger list is where they differ most. If any company in your group runs <strong>Sage</strong>, Joiin is the only tool in this list that names a Sage connection on its pricing page. Its direct connection covers Sage Accounting (cloud) in the US, UK, Canada and Ireland; Sage 50, Sage 200 and Sage X3 go in through its manual company import (see <a href=\"/blog/how-to-consolidate-sage-companies/\">how to consolidate Sage companies</a>). For <strong>MYOB</strong> groups in Australia and New Zealand, both Joiin and Fathom list MYOB. For <strong>FreeAgent</strong> users, mostly UK small businesses and contractors, Joiin and Fathom both list it too.",
        "For <strong>QuickBooks Online</strong>, the standard Simple Start, Essentials and Plus plans don't produce consolidated reports across separate company files. QuickBooks Advanced can pull several companies into Excel through Spreadsheet Sync, but accounts only line up if the charts of accounts match exactly, and it doesn't handle eliminations or currency translation. A connected tool (Joiin, Fathom, Spotlight, LiveFlow) or a move to Intuit Enterprise Suite are the usual next steps.",
        "Running <strong>Xero</strong>? We cover the options in detail in <a href=\"/blog/how-to-consolidate-multiple-xero-organisations/\">How to Consolidate Multiple Xero Organisations</a>.",
    ]),
    prose("Multi-Currency and Group Reporting", "multi-currency", [
        "If a subsidiary keeps its books in another currency, the consolidation tool has to translate its figures into the group's reporting currency before adding them up. That's where entry plans often stop. On Joiin, Core reports in a single currency, Pro adds multi-currency, and Max adds advanced FX so you can apply your own rates, which matters when auditors or group policy specify them. Fathom Pro includes multi-currency consolidations, and Spotlight Multi handles multiple currencies for multi-national reporting.",
        "A full group pack usually needs four statements: a consolidated profit and loss, a consolidated balance sheet, a consolidated cash flow, and intercompany reconciliation so the eliminations tie out. Joiin includes P&amp;L, balance sheet, cash flow and trial balance on every plan. Whichever tool you trial, test it with a month that has real intercompany transactions, because that's where manual spreadsheets usually break.",
    ]),
    prose("How to Choose", "choose", [
        "Start with three questions:",
        ul(["<strong>Does it connect to every ledger in the group?</strong> A tool that misses one entity's system sends you back to spreadsheets for that entity.",
            "<strong>Which plan includes eliminations and multi-currency?</strong> The headline price is often for a plan that doesn't include them.",
            "<strong>What does the price depend on?</strong> Per company (Joiin), a bundle of companies (Fathom Pro, Spotlight) or a quote (Syft, LiveFlow, Intuit). Price your actual entity count."]),
        "For a business group with a handful of entities, Joiin's per-company pricing with consolidation on every plan is usually the cheapest way to get real consolidated reports. For an accounting firm already reporting on dozens of clients, Fathom Portfolio is very cheap for single-company clients ($67/month for 100, without consolidation), and Fathom's and Spotlight's advisory features go further.",
    ]),
    faq_html(P1_FAQ),
    related([("/review/joiin/", "Review", "Joiin Review 2026"), ("/alternatives/fathom/", "Alternatives", "Fathom Alternatives"),
             ("/best/management-reporting-software-for-accountants/", "Best Of", "Management Reporting Software for Accountants"),
             ("/blog/how-to-consolidate-multiple-xero-organisations/", "Guide", "Consolidate Multiple Xero Organisations")]),
]
P1_TITLE = "Best Consolidation Software for Xero, QuickBooks and Sage (2026)"
P1_DESC = ("Joiin, Fathom, Spotlight, Syft, LiveFlow and Intuit Enterprise Suite compared: ledgers supported, "
           "eliminations, multi-currency and 2026 pricing.")

# ─────────────────────────── 2. /alternatives/fathom/ ───────────────────────────
P2 = "alternatives/fathom"
P2_FAQ = [
    ("What is the best alternative to Fathom?",
     "For consolidation, Joiin is the closest alternative at a lower entry price: consolidation is on every plan from $23/mo for one company (annual), compared with Fathom Pro's $59/month for one company and $295/month for five. For a full advisory suite similar to Fathom, look at Spotlight Reporting."),
    ("Is there a cheaper alternative to Fathom?",
     "For a single group with a few entities, yes. Fathom Pro costs $118/month for two companies and $295/month for five. Joiin charges by company count, from $23/mo for one company or $29/mo for two (annual), with eliminations and unlimited users included. Joiin stays cheaper at every company count we checked, so Fathom's case rests on its reporting and forecasting features rather than price."),
    ("Does Fathom Portfolio include consolidation?",
     "No. Fathom's pricing page says Portfolio ($67/month for 100 companies) doesn't include consolidations. You need to upgrade a company to Fathom Pro to consolidate it."),
    ("Which Fathom alternative works with Sage?",
     "Joiin lists Sage among its ten accounting connections. Fathom's own pricing page names Xero, QuickBooks, MYOB, FreeAgent and Excel, but not Sage."),
    ("Is Spotlight Reporting cheaper than Fathom?",
     "It depends on your client count and currency. Spotlight's advisor plans are priced in NZD excluding GST: Basic is NZ$329/month for up to 10 organisations, Super VCFO 25 is NZ$495/month and Super VCFO 75 is NZ$995/month. Fathom Pro is $315/month for 10 companies and $450 for 25, and Portfolio is $67/month for 100 (without consolidation). Convert to your currency and compare at your real number of organisations."),
    ("Can I keep Fathom and add a consolidation tool alongside it?",
     "Yes. One option is to keep Fathom Portfolio for single-company clients, because it's very cheap per company, and use a per-company consolidation tool such as Joiin only for the clients that run groups. That avoids moving every client onto Fathom Pro when only a few need consolidation."),
    ("Is there a Fathom alternative for QuickBooks users who prefer spreadsheets?",
     "LiveFlow syncs QuickBooks Online data into Google Sheets and Excel in real time and can consolidate multiple QuickBooks companies, so you keep your own spreadsheet models."),
]
P2_SECTIONS = [
    prose("Why People Look for Fathom Alternatives", "why", [
        "Fathom is a well-regarded management reporting and forecasting tool, so most people searching for an alternative aren't unhappy with the reports. The reasons are usually structural:",
        ul(["<strong>Price for small groups.</strong> Fathom Pro, which includes consolidations, costs $59/month for one company and adds $59 for each extra company up to its 10-company tier ($315). A group with three entities pays $177/month.",
            "<strong>Portfolio has no consolidation.</strong> The $67/month Portfolio plan covers 100 companies but excludes consolidations, so it doesn't solve group reporting.",
            "<strong>Ledger coverage.</strong> Fathom lists Xero, QuickBooks, MYOB, FreeAgent and Excel. Groups with an entity on Sage, Zoho Books or another system need a tool that connects to it.",
            "<strong>Spreadsheet workflows.</strong> Some finance teams want live data in their own Excel or Google Sheets models rather than a separate report builder."]),
    ]),
    toc([("joiin", "Joiin: Best Fathom Alternative for Consolidation"), ("spotlight-reporting", "Spotlight Reporting: Closest Advisory Suite"),
         ("syft", "Syft Analytics: Xero-Owned Option"), ("liveflow", "LiveFlow: For Spreadsheet-First Teams"),
         ("compare", "Fathom vs Alternatives Table"), ("verdict", "Which Should You Pick?"), ("faq", "FAQ")]),
    card(JOIIN, 0, "Best Fathom Alternative for Consolidation", "Consolidation on every plan, priced per company", "From $23/mo",
         ["Per-company pricing", "Unlimited users", "Sage, MYOB, Xero, QuickBooks", "14-day Max trial"],
         JOIIN_BODY + "<p>Against Fathom, the trade-off is simple: Joiin is cheaper to start and connects to more ledgers, while Fathom's forecasting and advisory tooling is more established. If consolidation is the reason you looked at Fathom, start with Joiin's trial.</p>",
         JOIIN_PROS, JOIIN_CONS),
    card(SPOTLIGHT, 1, "Closest Advisory Suite", "Reporting, forecasting, dashboards and Multi", "From NZ$329/mo",
         ["Advisor plans", "Spotlight Multi", "Xero · QuickBooks"], SPOTLIGHT_BODY,
         ["Similar scope to Fathom: reports, forecasts and dashboards", "Multi handles franchises and networks of up to 500 entities"],
         ["Also priced for advisors, not single groups", "Fewer ledgers named than Joiin"]),
    card(SYFT, 2, "Xero-Owned Option", "Dashboards, consolidations, forecasts and reports", "Owned by Xero",
         ["Consolidations", "Forecasts"], SYFT_BODY,
         ["Close to Xero", "Covers reporting, forecasting and consolidation"], ["No public pricing", "Roadmap tied to Xero's plans"]),
    card(LIVEFLOW, 3, "For Spreadsheet-First Teams", "Live QuickBooks data in Sheets and Excel", "Demo-based pricing",
         ["QuickBooks Online", "Sheets &amp; Excel"], LIVEFLOW_BODY,
         ["Keeps your own models", "Live refresh from QuickBooks"], ["QuickBooks only", "No report builder of its own"]),
    f'''    <section id="compare">
      <h2>Fathom vs Alternatives Table</h2>
{table(["", "Consolidation from", "Pricing basis", "Ledgers named", "Free trial"], [
        ["<strong>Fathom</strong>", "Pro: $59/mo (1 company)", "Tiers by company count", "Xero, QuickBooks, MYOB, FreeAgent, Excel", "14 days"],
        ['<strong><a href="/go/joiin/" rel="nofollow sponsored" target="_blank">Joiin</a></strong>', "$23/mo (1 company, annual)", "Per company, unlimited users", "10 incl. Sage, MYOB, Xero, QuickBooks", "14 days, no card"],
        ["<strong>Spotlight</strong>", "Basic: NZ$329/mo (up to 10 orgs)", "Plan by organisation count", "Xero, QuickBooks", "14 days"],
        ["<strong>Syft</strong>", "Not published", "Check with vendor", "Check with vendor", "Check with vendor"],
        ["<strong>LiveFlow</strong>", "Quote", "Demo-based", "QuickBooks Online", "Not stated"],
    ], "From each vendor's pricing page, October 2026. Fathom and Joiin before sales tax; Spotlight in NZD excluding GST.")}
    </section>
''',
    prose("Cost Examples: Fathom vs Joiin", "cost", [
        "Headline prices hide how each tool scales, so here's how the published numbers play out. All figures are before sales tax; Joiin prices are billed annually.",
        ul(["<strong>A group with 2 companies.</strong> Fathom Pro is $118/month (two companies on its $59 Starter tier). Joiin is $36/mo billed monthly or $29/mo billed annually, with eliminations and unlimited users. If a subsidiary reports in another currency you need Joiin's Pro plan, so confirm that plan's price.",
            "<strong>A group with 5 companies.</strong> Fathom Pro is $295/month. Joiin is $70/mo monthly or $57/mo annually.",
            "<strong>A firm with 25 single-company clients that don't need consolidation.</strong> Fathom Portfolio is $67/month for up to 100 companies, which is hard to beat. This is the case where staying on Fathom usually makes sense.",
            "<strong>A firm with 25 clients, several of them groups.</strong> Fathom Pro's Gold tier is $450/month for 25 companies (about $18 each), plus $17 per extra company. Joiin's <a href=\"/go/joiin/\" rel=\"nofollow sponsored\" target=\"_blank\">price table</a> lists $139/mo for 20 companies and $174/mo for 50 (annual), so 25 companies falls between the two; confirm the exact figure before deciding.",
            "<strong>A group with an entity on Sage.</strong> Fathom doesn't list a Sage connection, so that entity would be handled outside the tool. Joiin lists Sage, which removes the manual step."]),
        table(["Companies", "Fathom Pro (monthly)", "Joiin (monthly)", "Joiin (annual, per month)"], [
            ["1", "$59", "$28", "$23"], ["2", "$118", "$36", "$29"], ["5", "$295", "$70", "$57"],
            ["10", "$315", "$111", "$92"], ["20", "$450", "$167", "$139"], ["50", "$805", "$217", "$174"],
            ["100", "$1,455", "$336", "$252"],
        ], "USD before sales tax, from each vendor's pricing page on October 24, 2026. Fathom figures use the cheapest Pro tier for each count "
           "(Starter $59 +$59 per company, Silver $315 for 10 +$31, Gold $450 for 25 +$17, Platinum $805 for 50 +$13). Joiin's page shows one price "
           "table by company count and no separate prices per plan, so confirm the price of the plan you need."),
        "The pattern: on the published prices Joiin is cheaper than Fathom Pro at every company count we checked, from 2 companies to 100. Fathom only wins on price with Portfolio, for single-company clients that don't need consolidation.",
    ]),
    prose("Where Fathom Is Still Strong", "strengths", [
        "To be fair to Fathom, there are good reasons it's so widely used. Its management reporting, KPI analysis and forecasting have been developed over many years for advisors, and the Portfolio plan makes it very cheap to roll out to a large book of single-company clients. Pro includes multi-currency consolidations with eliminations, and consolidated groups don't cost extra once the companies are on Pro. Fathom also lists QuickBooks Desktop and MYOB AccountRight desktop connections, which matters for clients who haven't moved to the cloud.",
        "If those are the features you rely on, an alternative needs to match them, not just undercut the price. That's why we suggest a side-by-side trial rather than switching on price alone.",
    ]),
    prose("What to Check Before You Switch", "checklist", [
        ul(["<strong>Every ledger in the group connects.</strong> List each entity's accounting system and confirm it's supported. Joiin's ten connections are listed on its <a href=\"/go/joiin/\" rel=\"nofollow sponsored\" target=\"_blank\">pricing page</a>.",
            "<strong>Eliminations and multi-currency are on the plan you'll buy.</strong> On Joiin, eliminations are on every plan and multi-currency starts on Pro.",
            "<strong>Your report formats can be rebuilt.</strong> Joiin includes custom layouts and report packs on every plan; recreate your most-used Fathom report during the trial.",
            "<strong>Forecasting needs.</strong> Joiin includes budgets on every plan and forecasting from Pro. If rolling forecasts drive your advisory work, test them early.",
            "<strong>Data out.</strong> If consolidated data feeds Power BI, Tableau or a warehouse, Joiin's API and Zapier access are on Max.",
            "<strong>Historical data.</strong> Check how many past periods load from the ledger on connection, so year-on-year comparisons still work."]),
    ]),
    prose("How to Run a Side-by-Side Trial", "trial", [
        '      <ol style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
        "        <li>Pick one real group or client with at least two entities and some intercompany activity.</li>\n"
        "        <li>Start a <a href=\"/go/joiin/\" rel=\"nofollow sponsored\" target=\"_blank\">Joiin trial</a> (14 days on Max, no card) and connect the same entities you report on in Fathom.</li>\n"
        "        <li>Map the chart of accounts and set the eliminations.</li>\n"
        "        <li>Rebuild last month's consolidated P&amp;L and balance sheet and compare the totals line by line with your Fathom output.</li>\n"
        "        <li>Recreate your standard monthly pack and time how long the next refresh takes.</li>\n"
        "        <li>Price both tools at your real company count, including any extra-company fees.</li>\n"
        "      </ol>",
        "Two weeks is enough to see whether the numbers agree and whether the workflow is faster. If they don't, you've lost nothing, because the trial needs no card.",
    ]),
    prose("Which Should You Pick?", "verdict", [
        "If you're a <strong>business group</strong> that needs consolidated reports for a few entities, <a href=\"/go/joiin/\" rel=\"nofollow sponsored\" target=\"_blank\">Joiin</a> is the most cost-effective switch from Fathom: consolidation and eliminations are on its cheapest plan, and it costs less than Fathom Pro at every company count we checked.",
        "If you're an <strong>accounting firm</strong> that wants a full advisory toolkit across many clients, Spotlight Reporting is the closest like-for-like alternative, and Fathom itself may still be the right answer if its forecasting and advisory tools are what you rely on.",
        "If your team <strong>lives in spreadsheets on QuickBooks</strong>, LiveFlow keeps your models and refreshes the data for you.",
    ]),
    cta_box("Switching from Fathom for group reporting?", "Try Joiin's full Max plan for 14 days, no credit card, and rebuild one month's consolidated pack to compare."),
    faq_html(P2_FAQ),
    related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software 2026"), ("/tools/consolidation-software-cost-calculator/", "Tool", "Consolidation Cost Calculator"), ("/review/joiin/", "Review", "Joiin Review"),
             ("/best/management-reporting-software-for-accountants/", "Best Of", "Management Reporting Software for Accountants")]),
]
P2_TITLE = "4 Best Fathom Alternatives 2026: Cheaper Consolidation Tools"
P2_DESC = ("Fathom alternatives compared: Joiin, Spotlight Reporting, Syft and LiveFlow. Consolidation pricing, "
           "ledgers supported and who each tool fits.")

# ─────────────────────────── 3. /blog/how-to-consolidate-multiple-xero-organisations/ ───────────────────────────
P3 = "blog/how-to-consolidate-multiple-xero-organisations"
P3_FAQ = [
    ("Does Xero have a consolidation feature?",
     "No. Xero reports on one organisation at a time. On Xero's product ideas forum, Xero has said consolidated reporting is not currently planned and points users to apps in the Xero App Store."),
    ("Can I use tracking categories instead of separate Xero organisations?",
     "Only if the business is legally one entity. Tracking categories split one organisation's figures by branch, department or project. Separate companies need separate Xero organisations, with their own tax registrations and balance sheets, so tracking categories can't consolidate them."),
    ("How do I remove intercompany transactions when consolidating Xero?",
     "Code intercompany sales, costs, loans and recharges to dedicated accounts in each organisation, then reverse them in the consolidation. A spreadsheet needs manual elimination entries every month; consolidation apps such as Joiin let you set elimination rules once."),
    ("What does it cost to consolidate Xero organisations with an app?",
     "Joiin starts at $23/mo for one company or $29/mo for two (billed annually), with eliminations included. Fathom Pro starts at $59/month for one company and $315 for 10. Spotlight Reporting starts at NZ$329/month for up to 10 organisations."),
    ("Can I consolidate Xero organisations in different currencies?",
     "Yes, with a tool that supports multi-currency consolidation. In Joiin that starts on the Pro plan, and Max lets you apply your own exchange rates. Fathom Pro and Spotlight Multi also handle multiple currencies."),
]
P3_SECTIONS = [
    toc([("why", "Why Xero Can't Do It Natively"), ("prep", "Step 1: Prepare Each Organisation"),
         ("spreadsheet", "Option A: Consolidate in a Spreadsheet"), ("app", "Option B: Use a Consolidation App"),
         ("joiin-steps", "How the App Route Works in Joiin"), ("multi-currency", "Groups With Foreign Subsidiaries"),
         ("tools", "Xero Consolidation Apps Compared"), ("faq", "FAQ")]),
    prose("Why Xero Can't Do It Natively", "why", [
        "Every Xero organisation is a separate set of books, and Xero's reports only run inside one organisation. There's no built-in report that adds two or more organisations together. Consolidation has been a long-running request on Xero's product ideas forum, and Xero's reply there is that developing consolidated reporting is not currently planned; it points users to third-party apps instead.",
        "Tracking categories don't solve it either. They split one organisation's figures by branch or department. If your group has separate legal entities, each with its own balance sheet and tax registration, they belong in separate organisations, and you need to consolidate them outside Xero.",
    ]),
    prose("Step 1: Prepare Each Organisation", "prep", [
        "Whichever route you choose, these steps save hours every month:",
        ul(["<strong>Align the chart of accounts</strong> where you can. Matching codes and names across organisations make mapping much faster.",
            "<strong>Create intercompany accounts</strong> in each organisation (for example \"Intercompany receivable – Company B\" and \"Management fees – intercompany\"), and make sure both sides of every intercompany transaction are coded to them.",
            "<strong>Reconcile intercompany balances</strong> before month-end close: Company A's receivable from B should equal B's payable to A.",
            "<strong>Lock the period</strong> in each organisation once reconciled, so the numbers don't move after you've consolidated."]),
    ]),
    prose("Option A: Consolidate in a Spreadsheet", "spreadsheet", [
        "For two organisations with simple structures, a spreadsheet works:",
        '      <ol style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
        "        <li>Export the trial balance from each organisation for the same period end, in the same reporting currency.</li>\n"
        "        <li>Paste each into its own tab and map every account to a single group chart of accounts with a lookup column.</li>\n"
        "        <li>Add an eliminations column that reverses intercompany sales, costs, receivables, payables and loans.</li>\n"
        "        <li>Sum the mapped columns plus eliminations to produce the consolidated trial balance.</li>\n"
        "        <li>Build the consolidated P&amp;L and balance sheet from that trial balance, and check that the balance sheet still balances.</li>\n"
        "      </ol>",
        "Our <a href=\"/free/consolidation-excel-template/\">free consolidation Excel template</a> sets this up for you, with eliminations and balance checks built in. The problem is maintenance. Every new account breaks the mapping, every month needs a fresh export, and eliminations are manual. Once you have three or more entities, a foreign subsidiary, or a board that wants a pack every month, the spreadsheet usually costs more in time than an app costs in fees.",
    ]),
    prose("Option B: Use a Consolidation App", "app", [
        "Apps in the Xero App Store connect to each organisation through Xero's API and refresh automatically. You do the mapping and elimination setup once, then each month's consolidated reports are ready when the books are. Users on Xero's own forum most often name Fathom and Joiin for this, and Spotlight Reporting and Syft Analytics (which Xero agreed to buy in 2024) also consolidate Xero data.",
    ]),
    prose("How the App Route Works in Joiin", "joiin-steps", [
        "Using Joiin's published feature set as the example, setup follows the same order as the spreadsheet method, but you only do it once:",
        '      <ol style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
        "        <li><strong>Connect</strong> each Xero organisation (and any entity on QuickBooks, Sage, MYOB or another supported ledger).</li>\n"
        "        <li><strong>Map</strong> each organisation's accounts to a group reporting structure with chart of accounts mapping.</li>\n"
        "        <li><strong>Set eliminations</strong> for the intercompany accounts you created in Step 1.</li>\n"
        "        <li><strong>Choose the reporting currency.</strong> Multi-currency needs Pro or Max.</li>\n"
        "        <li><strong>Run the reports</strong>: consolidated P&amp;L, balance sheet, cash flow, trial balance, KPIs and budgets, then save them as a report pack to export to PDF, Excel or CSV each month.</li>\n"
        "      </ol>",
        "Joiin's 14-day trial runs on the full Max plan with no credit card, so you can test this on your real organisations before paying. It costs $23/mo for one company or $29/mo for two, billed annually, with unlimited users. Read our <a href=\"/review/joiin/\">full Joiin review</a> for plan details.",
    ]),
    cta_box("Consolidate your Xero organisations in one place", "Connect your organisations to Joiin's 14-day Max trial, no card required, and check the consolidated P&amp;L against your spreadsheet."),
    prose("Groups With Foreign Subsidiaries", "multi-currency", [
        "If one organisation keeps its books in a different base currency, its figures have to be translated before consolidation: typically the period's average rate for P&amp;L lines and the closing rate for balance sheet lines, with the difference going to a translation reserve. Doing this by hand in a spreadsheet is error-prone. In Joiin, multi-currency starts on Pro, and Max's advanced FX lets you use your own rates if your auditors require specific ones. Fathom Pro and Spotlight Multi also include multi-currency.",
    ]),
    f'''    <section id="tools" style="margin-top:3rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,0.08);">
      <h2 style="font-size:1.3rem;color:#f1f5f9;margin-bottom:1rem;">Xero Consolidation Apps Compared</h2>
{table(["App", "Consolidation from", "Other ledgers", "Best for"], [
        ['<strong><a href="/review/joiin/">Joiin</a></strong>', "$23/mo, 1 company (annual)", "QuickBooks, Sage, MYOB, FreeAgent + more", "Business groups, mixed ledgers"],
        ["<strong>Fathom</strong>", "Pro from $59/mo (1 company)", "QuickBooks, MYOB, FreeAgent", "Accounting firms with many clients"],
        ["<strong>Spotlight Reporting</strong>", "NZ$329/mo (up to 10 orgs)", "QuickBooks", "Advisory firms, franchise networks"],
        ["<strong>Syft Analytics</strong>", "Not published", "Check with vendor", "Xero-centric firms"],
    ], "Vendor pricing pages, October 2026. See our full <a href='/best/consolidation-software/'>consolidation software comparison</a>.")}
    </section>
''',
    faq_html(P3_FAQ),
    related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software 2026"), ("/tools/consolidation-software-cost-calculator/", "Tool", "Consolidation Cost Calculator"), ("/review/joiin/", "Review", "Joiin Review"),
             ("/alternatives/fathom/", "Alternatives", "Fathom Alternatives")]),
]
P3_TITLE = "How to Consolidate Multiple Xero Organisations (2026 Guide)"
P3_DESC = ("Xero has no built-in consolidation. Step by step: prepare each organisation, use a spreadsheet or an app "
           "like Joiin, and handle eliminations and FX.")

# ─────────────────────────── 4. /best/management-reporting-software-for-accountants/ ───────────────────────────
P4 = "best/management-reporting-software-for-accountants"
P4_FAQ = [
    ("What is the best management reporting software for accountants?",
     "It depends on your client base. Fathom and Spotlight Reporting are full advisory suites priced in bundles of client companies. Joiin is priced per company with unlimited users and clients, and is the strongest pick when clients have more than one entity to consolidate. LiveFlow suits firms that build management reports in Excel or Google Sheets on QuickBooks."),
    ("Which tools include budget vs actual reporting?",
     "All of the tools here offer budgets. On Joiin, budgets, dashboards and report packs are on every plan, with forecasting from Pro. Fathom and Spotlight both include forecasting in their advisor offerings."),
    ("How do accounting firms pay for management reporting software?",
     "Fathom Portfolio is $67/month for 100 companies (no consolidation), and Fathom Pro is tiered from $59/month for one company to $450 for 25. Spotlight's advisor plans start at NZ$329/month for up to 10 organisations. Joiin charges by connected company with unlimited users and clients. Compare on your actual number of client entities."),
    ("Can I send clients a monthly board pack automatically?",
     "Most tools let you save a report pack and refresh it each month. Joiin includes report packs and custom layouts on every plan, with PDF, Excel and CSV export; Max adds report-pack templates."),
]
P4_SECTIONS = [
    toc([("joiin", "Joiin: Best for Multi-Entity Clients"), ("fathom", "Fathom: Best for Large Client Books"),
         ("spotlight-reporting", "Spotlight Reporting: Best Advisory Bundle"), ("liveflow", "LiveFlow: Best for Spreadsheet Reporting"),
         ("syft", "Syft Analytics: Xero-Owned Dashboards"), ("compare", "Comparison Table"),
         ("kpi", "KPIs, Board Packs and Budget vs Actual"), ("choose", "How to Choose"), ("faq", "FAQ")]),
    card(JOIIN, 0, "Best for Multi-Entity Clients", "Management reporting plus consolidation, unlimited clients", "From $23/mo",
         ["Unlimited clients &amp; users", "Report packs", "Budgets", "Forecasting on Pro"],
         JOIIN_BODY + "<p>For a firm, the key detail is that clients and users are unlimited: you pay for the companies you connect, not for staff seats or client logins. Report packs and custom layouts let you match your firm's management-accounts format.</p>",
         JOIIN_PROS, JOIIN_CONS),
    card(FATHOM, 1, "Best for Large Client Books", "Management reporting, KPIs and forecasting", "From $67/mo (Portfolio)",
         ["Portfolio: 100 companies", "Pro: consolidation", "14-day trial"], FATHOM_BODY,
         ["Portfolio's $67/month for 100 companies is very low per client", "Mature KPI, reporting and forecasting tooling"],
         ["Consolidation needs Pro (from $59/month per company, $450 for 25)", "No Sage connection listed"]),
    card(SPOTLIGHT, 2, "Best Advisory Bundle", "Reporting, forecasting and dashboards for advisors", "From NZ$329/mo",
         ["Up to 10 orgs on Basic", "Training included", "Xero · QuickBooks"], SPOTLIGHT_BODY,
         ["Reporting, forecasting and dashboards in one advisor plan", "Account management and training on Super VCFO plans"],
         ["NZD pricing; check your local currency on its pricing page", "Fewer ledgers named"]),
    card(LIVEFLOW, 3, "Best for Spreadsheet Reporting", "Live QuickBooks data in Sheets and Excel", "Demo-based pricing",
         ["QuickBooks Online", "Sheets &amp; Excel"], LIVEFLOW_BODY,
         ["Keeps your firm's own templates", "Live refresh, no re-exporting"], ["QuickBooks only", "No public pricing"]),
    card(SYFT, 4, "Xero-Owned Dashboards", "Dashboards, reports, forecasts and consolidations", "Owned by Xero",
         ["Dashboards", "Forecasts"], SYFT_BODY,
         ["Close to Xero", "Dashboards and forecasts in one place"], ["No public pricing", "Roadmap tied to Xero"]),
    f'''    <section id="compare">
      <h2>Comparison Table</h2>
{table(["Tool", "Pricing basis", "Entry price", "Consolidation", "Forecasting"], [
        ["<strong>Joiin</strong>", "Per company, unlimited clients &amp; users", "$23/mo, 1 company (annual)", "Every plan", "Pro and Max"],
        ["<strong>Fathom</strong>", "Bundles of companies", "Portfolio $67/mo (100)", "Pro (from $59/mo)", "Yes"],
        ["<strong>Spotlight</strong>", "Plans by organisation count", "NZ$329/mo (up to 10)", "Spotlight Multi", "Yes"],
        ["<strong>LiveFlow</strong>", "Quote", "Demo", "QuickBooks companies", "In your spreadsheet"],
        ["<strong>Syft</strong>", "Not published", "Not published", "Yes", "Yes"],
    ], "Vendor pricing pages, October 2026. Confirm current pricing and plan contents before you buy.")}
    </section>
''',
    prose("KPIs, Board Packs and Budget vs Actual", "kpi", [
        "Monthly management reporting for clients usually comes down to the same few deliverables:",
        ul(["<strong>A KPI dashboard</strong> with revenue, gross margin, overheads, cash and debtor days, compared to last month and last year.",
            "<strong>Budget vs actual</strong> by month and year to date, so the conversation is about variances, not raw numbers.",
            "<strong>A board pack</strong>: P&amp;L, balance sheet, cash flow and commentary, delivered as a PDF in the same format every month.",
            "<strong>A forecast</strong> rolling the budget forward with actuals, for clients who need cash planning."]),
        "Every tool here can do the first three. The differences are what each plan includes, which ledgers you can connect, and how pricing scales as your client list grows. If some clients run groups of companies, pick a tool that consolidates on the plan you'll actually be on.",
    ]),
    prose("What to Test During a Free Trial", "trial", [
        "Joiin, Fathom and Spotlight all offer 14-day trials, which is enough to answer the questions that matter for a firm:",
        ul(["<strong>Time to first pack.</strong> Connect one real client and time how long it takes to produce a finished monthly pack in your firm's format.",
            "<strong>Refresh effort.</strong> Next month, how much manual work does the refresh need? This is where the tools save, or don't save, staff hours.",
            "<strong>Client-facing output.</strong> Send the PDF to a friendly client and ask whether it's clearer than what they get now.",
            "<strong>Budget and forecast workflow.</strong> Load a budget, check budget vs actual, and if you offer forecasting, roll it forward with actuals.",
            "<strong>Groups.</strong> If any client has more than one entity, consolidate them and check eliminations against your working papers.",
            "<strong>Real cost.</strong> Price each tool at your actual number of client companies, including extra-company fees and the plan that includes the features you used."]),
    ]),
    prose("How to Choose", "choose", [
        "Count your client entities and check how many need consolidation. A firm with 100 single-company Xero clients will find Fathom Portfolio hard to beat on price. A firm whose clients include groups, use Sage or MYOB alongside Xero, or want unlimited logins for their own teams will usually get more from Joiin's per-company model. Firms that want a packaged advisory service with training should trial Spotlight.",
    ]),
    cta_box("Have clients with more than one company?", "Joiin includes consolidation, report packs and unlimited users on every plan. Try the Max plan free for 14 days."),
    faq_html(P4_FAQ),
    related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software 2026"), ("/tools/consolidation-software-cost-calculator/", "Tool", "Consolidation Cost Calculator"), ("/review/joiin/", "Review", "Joiin Review"),
             ("/alternatives/fathom/", "Alternatives", "Fathom Alternatives"), ("/best/ai-data-tools/", "Best Of", "Best AI Data Tools")]),
]
P4_TITLE = "5 Best Management Reporting Software for Accountants (2026)"
P4_DESC = ("Joiin, Fathom, Spotlight, LiveFlow and Syft compared for accounting firms: KPI dashboards, board packs, "
           "budget vs actual and real pricing.")


def item_list(name, path, tools):
    return ld({"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(tools),
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t["name"], "url": f"{SITE}/{path}/#{t['id']}"}
                                   for i, t in enumerate(tools)]})


if __name__ == "__main__":
    build(P1, P1_TITLE, P1_DESC,
          [("Home", "/"), ("Best Tools", "/best/"), ("Best Consolidation Software", f"/{P1}/")],
          [item_list("Best Consolidation Software 2026", P1, [JOIIN, FATHOM, SPOTLIGHT, SYFT, LIVEFLOW, IES]), faq_schema(P1_FAQ)],
          page("6 Best Consolidation Software for Xero, QuickBooks, Sage &amp; MYOB (2026)", BYLINE,
               "Business group with a few entities, or entities on different ledgers: <strong>Joiin</strong> (consolidation on every plan, from $23/mo). "
               "Accounting firm with 25+ clients: <strong>Fathom</strong>. Advisory bundle or franchise network: <strong>Spotlight Reporting</strong>. "
               "Xero-centric firm: <strong>Syft</strong>. QuickBooks data in your own spreadsheets: <strong>LiveFlow</strong>.", P1_SECTIONS))
    build(P2, P2_TITLE, P2_DESC,
          [("Home", "/"), ("Alternatives", "/alternatives/"), ("Fathom Alternatives", f"/{P2}/")],
          [item_list("Fathom Alternatives 2026", P2, [JOIIN, SPOTLIGHT, SYFT, LIVEFLOW]), faq_schema(P2_FAQ)],
          page("4 Best Fathom Alternatives in 2026", BYLINE,
               "Fathom Pro costs $59/month for one company and $295 for five, and the cheaper Portfolio plan has no consolidation. For group consolidation at a lower price, "
               "<strong><a href=\"/go/joiin/\" rel=\"nofollow sponsored\" target=\"_blank\" style=\"color:#4ade80;\">Joiin</a></strong> includes eliminations on every plan from $23/mo for one company. For a similar advisory suite, try <strong>Spotlight Reporting</strong>.",
               P2_SECTIONS))
    build(P3, P3_TITLE, P3_DESC,
          [("Home", "/"), ("Blog", "/blog/"), ("Consolidate Multiple Xero Organisations", f"/{P3}/")],
          [article_ld("How to Consolidate Multiple Xero Organisations", P3), faq_schema(P3_FAQ)],
          page("How to Consolidate Multiple Xero Organisations", BYLINE.replace("Independent guide", "Guide"),
               "Xero can't consolidate organisations on its own. For two simple entities, export trial balances into a spreadsheet and add eliminations by hand. "
               "For three or more, foreign subsidiaries or monthly board packs, connect the organisations to a consolidation app such as <strong>Joiin</strong> "
               "(from $23/mo, eliminations included) and set the mapping once.", P3_SECTIONS))
    build(P4, P4_TITLE, P4_DESC,
          [("Home", "/"), ("Best Tools", "/best/"), ("Management Reporting for Accountants", f"/{P4}/")],
          [item_list("Best Management Reporting Software for Accountants 2026", P4, [JOIIN, FATHOM, SPOTLIGHT, LIVEFLOW, SYFT]), faq_schema(P4_FAQ)],
          page("5 Best Management Reporting Software for Accountants (2026)", BYLINE,
               "Clients with more than one company: <strong>Joiin</strong> (per-company pricing, unlimited clients and users). Lots of single-company clients: "
               "<strong>Fathom</strong> Portfolio ($67/mo for 100). Packaged advisory service: <strong>Spotlight Reporting</strong>. "
               "Spreadsheet-based reporting on QuickBooks: <strong>LiveFlow</strong>.", P4_SECTIONS))
