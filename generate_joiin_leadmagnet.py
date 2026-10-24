#!/usr/bin/env python3
"""Lead magnet (2026-10-24): free multi-entity consolidation Excel template.
  /free/consolidation-excel-template/          -- landing page with email form + direct download
  /free/consolidation-excel-template/thanks/   -- FormSubmit _next target
File: assets/downloads/multi-entity-consolidation-template.xlsx (build_consolidation_template.py).
Form posts to the same FormSubmit alias as the playbook form; main.js mirrors it to /api/subscribe with
source "consolidation-template" (functions/api/subscribe.js adds BREVO_LIST_ID_CONSOLIDATION when set)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_joiin_cluster import GO, build, prose, ul, faq_html, faq_schema, related, cta_box, article_ld
from xlsx_preview import Book, render

P = "free/consolidation-excel-template"
FILE = "/assets/downloads/multi-entity-consolidation-template.xlsx"
FORMSUBMIT = "https://formsubmit.co/b21365b0716308a5caecd30f63ea8e22"
AUTORESPONSE = ("Thanks for downloading the Multi-Entity Consolidation Template! Get the Excel file here: "
                f"https://rankertoolai.com{FILE} - Start with the 'Start Here' sheet. When monthly consolidation becomes a chore, "
                "compare the software options at https://rankertoolai.com/best/consolidation-software/ - The RankerToolAI team")

FAQ = [
    ("Is the template really free?", "Yes. You can download it directly without an email. If you enter your email we'll also send the link to your inbox and a few short emails on consolidation; unsubscribe anytime."),
    ("Which accounting software does it work with?", "Any that can export a trial balance to Excel or CSV, including Xero, QuickBooks, Sage, MYOB and FreeAgent. You paste each company's trial balance into its own sheet."),
    ("How many companies does it handle?", "Three company sheets are included. To add more, copy a company sheet and add a column for it on the Consolidated TB sheet."),
    ("Does it handle foreign currency?", "No. Translate each subsidiary's trial balance into the group currency before you paste it. Consolidation software such as Joiin (Pro and Max plans) or Fathom Pro handles multi-currency automatically."),
    ("What are the eliminations for?", "When group companies trade with each other, those sales, costs and balances would be double-counted. The Eliminations sheet removes them, with two lines per elimination that cancel out."),
]


def form(tag):
    return f'''      <form action="{FORMSUBMIT}" method="POST" class="lead-form" aria-label="Get the consolidation template ({tag})">
        <input type="hidden" name="_subject" value="New Consolidation Template Lead - RankerToolAI">
        <input type="hidden" name="_next" value="https://rankertoolai.com/{P}/thanks/">
        <input type="hidden" name="_captcha" value="false">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_autoresponse" value="{AUTORESPONSE}">
        <input type="hidden" name="source" value="consolidation-template">
        <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
        <input type="email" name="email" placeholder="your@email.com" required autocomplete="email" class="lead-input">
        <button type="submit" class="lead-btn">Email Me the Template →</button>
      </form>
      <p style="font-size:0.75rem;color:rgba(148,163,184,0.6);margin-top:0.75rem;">No spam. Unsubscribe anytime. <a href="{FILE}" download>Skip the email, download directly →</a></p>'''


BOX = '''    <div class="tool-card featured" style="padding:1.5rem;margin:1.5rem 0;">
      <h2 style="margin-top:0;">{h}</h2>
      <p>{p}</p>
{form}
    </div>
'''


PREVIEW_CSS = """    <style>
      .xp-tabs{display:flex;flex-wrap:wrap;gap:.4rem;margin:.75rem 0;}
      .xp-tab{background:rgba(255,255,255,.05);border:1px solid rgba(148,163,184,.25);color:var(--color-text-muted);padding:.4rem .8rem;border-radius:999px;font-size:.85rem;font-weight:600;cursor:pointer;}
      .xp-tab[aria-selected="true"]{background:#16a34a;border-color:#16a34a;color:#fff;}
      .xp-scroll{overflow-x:auto;border:1px solid rgba(148,163,184,.2);border-radius:10px;}
      .xp-table{width:100%;border-collapse:collapse;font-size:.85rem;font-variant-numeric:tabular-nums;}
      .xp-table th{background:#14532d;color:#f0fdf4;text-align:left;padding:.45rem .6rem;white-space:nowrap;}
      .xp-table td{padding:.4rem .6rem;border-top:1px solid rgba(148,163,184,.15);white-space:nowrap;}
      .xp-table td.num{text-align:right;}
      .xp-table td.ok{color:#22c55e;font-weight:800;}
      .xp-table tr.total td{font-weight:700;background:rgba(34,197,94,.08);}
      .xp-table td:first-child{white-space:normal;min-width:7rem;}
      .xp-table th:first-child,.xp-table td:first-child{position:sticky;left:0;z-index:1;background:#0b1120;}
      .xp-table th:first-child{background:#14532d;}
      .xp-table tr.total td:first-child{background:#0f2a1c;}
      @media(max-width:640px){.xp-table{font-size:.78rem;}.xp-table th,.xp-table td{padding:.35rem .45rem;}}
    </style>
"""


def preview_html():
    """Tabbed preview of the real template values (computed from the .xlsx itself)."""
    b = Book(os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE.lstrip("/").replace("/", os.sep)))
    pl = b.table("P&L", 3, "ABCDEF", 4, 8)
    bs = b.table("Balance Sheet", 3, "ABCDEF", 4, 13)
    ca = b.table("Company A", 4, "BCDEF", 5, 66)
    el = b.table("Eliminations", 4, "ABCDE", 5, 34)
    el[1].append(["Total net (should be 0)", "", "", "", b.val("Eliminations", "E36")])
    el[1].append(["Check", "", "", "", b.val("Eliminations", "E37")])
    tb = b.table("Consolidated TB", 3, "ADEFGH", 4, 42)
    tabs = [("pl", "P&amp;L", render(*pl, check_rows=("Net profit",))),
            ("bs", "Balance Sheet", render(*bs, check_rows=("Total equity", "Check (net assets = equity)"))),
            ("tb", "Consolidated TB", render(*tb, check_rows=("Total (should be 0)", "Check"))),
            ("ca", "Company A", render(*ca, check_rows=("Totals", "Check: balances?"))),
            ("el", "Eliminations", render(*el, check_rows=("Total net (should be 0)", "Check")))]
    buttons = "".join(f'<button type="button" class="xp-tab" role="tab" aria-selected="{str(i == 0).lower()}" data-xp="{k}">{t}</button>'
                      for i, (k, t, _) in enumerate(tabs))
    panels = "".join(f'<div class="xp-panel" data-xp="{k}"{"" if i == 0 else " hidden"}>{tbl}</div>' for i, (k, _, tbl) in enumerate(tabs))
    return f"""{PREVIEW_CSS}    <section id="preview" style="margin:2rem 0;">
      <h2 style="font-size:1.3rem;color:#f1f5f9;margin-bottom:.5rem;">Preview the Template</h2>
      <p style="color:var(--color-text-muted);">These are the example figures that come in the file, calculated by its own formulas: Company A charges Company B a 10,000 management fee, and the eliminations remove it from the group totals. Every check reads OK. Figures in brackets are credits.</p>
      <div class="xp-tabs" role="tablist">{buttons}</div>
      {panels}
    </section>
    <script>
      document.querySelectorAll('.xp-tab').forEach(function(t){{t.addEventListener('click',function(){{
        document.querySelectorAll('.xp-tab').forEach(function(x){{x.setAttribute('aria-selected',x===t?'true':'false');}});
        document.querySelectorAll('.xp-panel').forEach(function(p){{p.hidden=p.getAttribute('data-xp')!==t.getAttribute('data-xp');}});
      }});}});
    </script>
"""


def main_html():
    sections = [
        BOX.format(h="Get the Free Excel Template", p="Combine up to three companies' trial balances into a consolidated P&amp;L and balance sheet, with an eliminations sheet and built-in balance checks.", form=form("top")),
        prose("What's Inside", "inside", [
            ul(["<strong>Start Here</strong>: five-step instructions.",
                "<strong>Group Lines</strong>: your group chart of accounts, each line tagged to a statement and section. Edit it to match your management accounts.",
                "<strong>Company A, B and C</strong>: paste each trial balance and pick a group line per account from a dropdown. Each sheet checks that debits equal credits and flags unmapped accounts.",
                "<strong>Eliminations</strong>: enter both sides of each intercompany balance or transaction; a check confirms they net to zero.",
                "<strong>Consolidated TB</strong>: sums every company plus eliminations by group line, automatically.",
                "<strong>P&amp;L and Balance Sheet</strong>: consolidated statements by company, eliminations and group total, with a net assets = equity check."]),
            "Companies A and B come with example figures (A charges B a 10,000 management fee that B hasn't paid yet), so you can see the eliminations working before you paste your own numbers.",
        ]),
        preview_html(),
        prose("How to Use It", "how", [
            '      <ol style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
            "        <li>Export each company's trial balance for the same period end from Xero, QuickBooks, Sage, MYOB or your ledger.</li>\n"
            "        <li>Paste each one into a company sheet and map every account to a group line.</li>\n"
            "        <li>Enter the intercompany eliminations: sales and costs between group companies, and the balances they owe each other.</li>\n"
            "        <li>Check every \"Check\" cell says OK.</li>\n"
            "        <li>Copy the consolidated P&amp;L and balance sheet into your monthly pack.</li>\n"
            "      </ol>",
            "Step-by-step guides for each ledger: <a href=\"/blog/how-to-consolidate-multiple-xero-organisations/\">Xero</a>, <a href=\"/blog/how-to-consolidate-sage-companies/\">Sage</a> and <a href=\"/blog/how-to-consolidate-myob-companies/\">MYOB</a>.",
        ]),
        prose("When to Move Beyond a Spreadsheet", "beyond", [
            "A spreadsheet is fine for two or three simple companies. It starts costing more time than it saves when:",
            ul(["you consolidate every month and re-export each trial balance by hand,",
                "a subsidiary reports in another currency,",
                "new accounts keep breaking the mapping, or",
                "a board, bank or investor wants the same pack on a fixed date."]),
            f"At that point a consolidation app connects to each ledger and refreshes automatically. <a href=\"{GO}\" rel=\"nofollow sponsored\" target=\"_blank\">Joiin</a> starts at $23/mo for one company billed annually ($29/mo for two), with eliminations on every plan. Compare the options in our <a href=\"/best/consolidation-software/\">consolidation software roundup</a> or price your company count in the <a href=\"/tools/consolidation-software-cost-calculator/\">cost calculator</a>.",
        ]),
        BOX.format(h="Download the Template", p="Free Excel file. Works with any ledger that exports a trial balance.", form=form("bottom")),
        faq_html(FAQ),
        related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software"),
                 ("/tools/consolidation-software-cost-calculator/", "Tool", "Consolidation Cost Calculator"),
                 ("/blog/how-to-consolidate-multiple-xero-organisations/", "Guide", "Consolidate Multiple Xero Organisations")]),
    ]
    return f'''<main class="container" style="padding-top:1rem;padding-bottom:4rem;">
  <div style="max-width:760px;">
    <h1 style="font-size:clamp(1.6rem,4vw,2.25rem);margin-bottom:0.5rem;">Free Multi-Entity Consolidation Excel Template</h1>
    <p style="color:var(--color-text-muted);font-size:1rem;margin-bottom:0.5rem;">Consolidate two or three companies' trial balances with eliminations and balance checks. By RankerToolAI · October 2026.</p>
    <p style="font-size:0.8rem;color:rgba(148,163,184,0.7);margin-bottom:1rem;">Disclosure: this page contains affiliate links, including to Joiin. We may earn a commission if you buy through them, at no extra cost to you. <a href="/affiliate-disclosure/">Read our disclosure</a>.</p>
{"".join(sections)}  </div>
</main>'''


THANKS = f'''<main class="container" style="padding-top:2rem;padding-bottom:4rem;">
  <div style="max-width:640px;">
    <h1>Your Template Is on Its Way</h1>
    <p>We've emailed you the download link. You can also get it right now:</p>
    <p><a href="{FILE}" class="btn btn-primary" download>Download the Excel Template →</a></p>
    <p style="color:var(--color-text-muted);">Start with the <strong>Start Here</strong> sheet. Companies A and B contain example figures you can delete.</p>
    <h2 style="margin-top:2rem;">Next Steps</h2>
    <ul style="line-height:2;">
      <li><a href="/blog/how-to-consolidate-multiple-xero-organisations/">How to consolidate multiple Xero organisations</a></li>
      <li><a href="/tools/consolidation-software-cost-calculator/">Consolidation software cost calculator</a></li>
      <li><a href="/best/consolidation-software/">Best consolidation software 2026</a></li>
    </ul>
  </div>
</main>'''

if __name__ == "__main__":
    build(P, "Free Multi-Entity Consolidation Excel Template (2026)",
          "Free Excel template to consolidate up to three companies: map trial balances, eliminate intercompany items and get a consolidated P&L and balance sheet.",
          [("Home", "/"), ("Free Consolidation Template", f"/{P}/")],
          [article_ld("Free Multi-Entity Consolidation Excel Template", P), faq_schema(FAQ)], main_html())
    build(P + "/thanks", "Your Consolidation Template | RankerToolAI",
          "Download your free multi-entity consolidation Excel template.",
          [("Home", "/"), ("Free Consolidation Template", f"/{P}/"), ("Thanks", f"/{P}/thanks/")],
          [], THANKS)
    # FormSubmit landing page: keep it out of the index (same as the playbook thanks page)
    t = os.path.join(os.path.dirname(os.path.abspath(__file__)), P.replace("/", os.sep), "thanks", "index.html")
    h = open(t, encoding="utf-8").read().replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex, follow">', 1)
    open(t, "w", encoding="utf-8", newline="\n").write(h)
