#!/usr/bin/env python3
"""/tools/consolidation-software-cost-calculator/ (2026-10-24): monthly cost of Joiin vs Fathom Pro vs
Spotlight Reporting for a chosen company count. Prices hard-coded from each vendor's pricing page on
2026-10-24 (see generate_joiin_brand_pages.py docstring); update PRICES below when vendors reprice.
  Joiin: only the published company counts (1,2,5,10,20,50,100) plus the 100+ formula -- the page doesn't
         say how counts in between are billed, so the calculator only offers published counts.
  Fathom Pro (USD): cheapest of Starter/Silver/Gold/Platinum, same formula as the fathomhq.com page script.
  Spotlight (NZD excl. GST): smallest advisor plan whose org limit covers the count; Enterprise above 75.
Reuses the shell/helpers of generate_joiin_cluster.py."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_joiin_cluster import GO, build, prose, ul, faq_html, faq_schema, related, cta_box, ld, SITE

P = "tools/consolidation-software-cost-calculator"
PRICES = {
    "joiin": {"1": [28, 23], "2": [36, 29], "5": [70, 57], "10": [111, 92], "20": [167, 139], "50": [217, 174], "100": [336, 252],
              "over100_base": 336, "over100_each": 2.80},
    "fathom": {"base": [59, 315, 450, 805], "included": [1, 10, 25, 50], "more": [59, 31, 17, 13],
               "names": ["Starter", "Silver", "Gold", "Platinum"]},
    "spotlight": [[10, 329, "Basic"], [25, 495, "Super VCFO 25"], [75, 995, "Super VCFO 75"]],
}
COUNTS = [1, 2, 5, 10, 20, 50, 100, 150, 200, 300]

FAQ = [
    ("How is consolidation software priced?",
     "Mostly by the number of companies (entities) you connect. Joiin publishes one price per company count with unlimited users. Fathom Pro uses four tiers and applies the cheapest one for your count. Spotlight sells advisor plans by number of organisations. None of the three charges per user."),
    ("Why does the calculator only offer some company counts?",
     "Joiin publishes prices for 1, 2, 5, 10, 20, 50 and 100 companies, plus a formula above 100. Its page doesn't say how counts in between are billed, so we only show counts we can price from published figures."),
    ("Are these prices exact?",
     "They're the list prices shown on each vendor's pricing page on October 24, 2026, before sales tax or GST. Joiin and Fathom are in USD; Spotlight is in NZD. Vendors change prices, and Joiin's page no longer lists separate prices for its Core, Pro and Max plans, so confirm the final figure with the vendor."),
    ("What about Fathom Portfolio?",
     "Fathom Portfolio costs $67/month for 100 companies, $189 for 300 or $405 for unlimited, but it doesn't include consolidations. It's a monitoring plan for accounting firms, so the calculator compares Fathom Pro."),
    ("Which tool is cheapest for consolidation?",
     "On published prices, Joiin is the cheapest of the three at every count the calculator covers. Fathom and Spotlight include advisory features such as three-way cash flow forecasting (Fathom) or training and account management (Spotlight) that may justify their price for an accounting firm."),
]

CALC_HTML = '''    <section id="calculator">
      <div class="tool-card featured" style="padding:1.5rem;">
        <h2 style="margin-top:0;">Calculate Your Monthly Cost</h2>
        <div style="display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end;margin-bottom:1.25rem;">
          <label style="display:flex;flex-direction:column;gap:0.35rem;font-weight:600;">Companies to consolidate
            <select id="cc-count" style="padding:0.6rem;border-radius:8px;font-size:1rem;min-width:140px;">__OPTIONS__</select>
          </label>
          <label style="display:flex;flex-direction:column;gap:0.35rem;font-weight:600;">Joiin billing
            <select id="cc-billing" style="padding:0.6rem;border-radius:8px;font-size:1rem;min-width:140px;">
              <option value="1">Annual</option><option value="0">Monthly</option>
            </select>
          </label>
        </div>
        <div style="overflow-x:auto;">
          <table class="comparison-table" aria-live="polite">
            <thead><tr><th>Tool</th><th>Monthly cost</th><th>Per company</th><th>Plan used</th></tr></thead>
            <tbody id="cc-body"></tbody>
          </table>
        </div>
        <p id="cc-summary" style="font-weight:600;margin:1rem 0 0.5rem;"></p>
        <p style="font-size:0.8rem;color:rgba(148,163,184,0.7);margin:0;">List prices from each vendor's pricing page on October 24, 2026, before tax. Joiin and Fathom in USD, Spotlight in NZD excluding GST. Fathom Pro uses the cheapest tier for your count. Confirm final prices with each vendor.</p>
        <div style="margin-top:1.25rem;"><a href="__GO__" class="btn btn-affiliate" rel="nofollow sponsored" target="_blank">Try Joiin Free for 14 Days →</a></div>
      </div>
    </section>
<script>
(function () {
  var P = __PRICES__;
  function fmt(n, cur) { return cur + (Math.round(n * 100) / 100).toLocaleString('en-US', {minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2}); }
  function joiin(n, annual) {
    if (P.joiin[String(n)]) return {price: P.joiin[String(n)][annual ? 1 : 0], plan: annual ? 'Annual billing' : 'Monthly billing'};
    if (n > 100) return {price: annual ? null : P.joiin.over100_base + P.joiin.over100_each * (n - 100), plan: 'From $336 + $2.80 per company over 100 (monthly)'};
    return {price: null, plan: 'Not published'};
  }
  function fathom(n) {
    var f = P.fathom, best = null;
    for (var i = 0; i < 4; i++) {
      var t = f.base[i] + Math.max(0, n - f.included[i]) * f.more[i];
      if (best === null || t < best.price) best = {price: t, plan: 'Pro ' + f.names[i] + (n > 50 ? ' (Enterprise quotes 51+)' : '')};
    }
    return best;
  }
  function spotlight(n) {
    for (var i = 0; i < P.spotlight.length; i++) if (n <= P.spotlight[i][0]) return {price: P.spotlight[i][1], plan: P.spotlight[i][2] + ' (up to ' + P.spotlight[i][0] + ' orgs)'};
    return {price: null, plan: 'Enterprise (quote)'};
  }
  function row(name, r, cur, n) {
    var cost = r.price === null ? 'Quote / not published' : fmt(r.price, cur);
    var per = r.price === null ? '–' : fmt(r.price / n, cur);
    return '<tr><td><strong>' + name + '</strong></td><td>' + cost + '</td><td>' + per + '</td><td>' + r.plan + '</td></tr>';
  }
  function run() {
    var n = parseInt(document.getElementById('cc-count').value, 10);
    var annual = document.getElementById('cc-billing').value === '1';
    var j = joiin(n, annual), f = fathom(n), s = spotlight(n);
    document.getElementById('cc-body').innerHTML = row('Joiin', j, '$', n) + row('Fathom Pro', f, '$', n) + row('Spotlight (NZD)', s, 'NZ$', n);
    var sum = '';
    if (j.price !== null) sum = 'For ' + n + (n === 1 ? ' company' : ' companies') + ', Joiin costs ' + fmt(j.price, '$') + '/mo vs ' + fmt(f.price, '$') + '/mo on Fathom Pro, about ' + fmt((f.price - j.price) * 12, '$') + ' less a year.';
    document.getElementById('cc-summary').textContent = sum;
  }
  document.getElementById('cc-count').addEventListener('change', run);
  document.getElementById('cc-billing').addEventListener('change', run);
  run();
})();
</script>
'''


def main_html():
    opts = "".join(f'<option value="{n}"{" selected" if n == 5 else ""}>{n}</option>' for n in COUNTS)
    calc = (CALC_HTML.replace("__OPTIONS__", opts).replace("__GO__", GO)
            .replace("__PRICES__", json.dumps(PRICES, separators=(",", ":"))))
    sections = [
        calc,
        prose("How Each Tool Prices Consolidation", "how", [
            ul(["<strong>Joiin</strong> publishes one price per company count, with unlimited users, reports and clients and a discount for annual billing. Over 100 companies it's $336/mo plus $2.80 per extra company. Its page no longer lists separate prices for Core, Pro and Max; multi-currency starts on Pro.",
                "<strong>Fathom Pro</strong> has four tiers: Starter $59/month for 1 company (+$59 each extra), Silver $315 for 10 (+$31), Gold $450 for 25 (+$17) and Platinum $805 for 50 (+$13). Its pricing page applies the cheapest tier for your count. Enterprise is quoted for 51+ companies.",
                "<strong>Spotlight Reporting</strong> sells advisor plans in NZD excluding GST: Basic NZ$329 for up to 10 organisations, Super VCFO 25 at NZ$495 and Super VCFO 75 at NZ$995, then Enterprise on request."]),
            "Per-company price falls as you add companies on all three, but at very different rates. The calculator shows both the monthly total and the cost per company, which is the fairest way to compare.",
        ]),
        prose("What the Price Doesn't Show", "beyond", [
            ul(["<strong>Features on the plan you'd buy.</strong> Joiin's eliminations are on every plan but multi-currency needs Pro and own FX rates need Max. Fathom Pro includes multi-currency, custom FX rates and three-way cash flow forecasting.",
                "<strong>Ledgers.</strong> Joiin connects natively to ten systems including Sage Accounting, Zoho Books and Fortnox. Fathom lists Xero, QuickBooks (Online and Desktop), MYOB and FreeAgent, plus Excel import. Spotlight names Xero and QuickBooks.",
                "<strong>Support and training.</strong> Spotlight's advisor plans include training and, on Super VCFO, account management.",
                "<strong>Tax and currency.</strong> Prices exclude sales tax or GST, and Joiin and Fathom also bill in other currencies."]),
            "For full comparisons see <a href=\"/compare/joiin-vs-fathom/\">Joiin vs Fathom</a>, <a href=\"/compare/joiin-vs-spotlight-reporting/\">Joiin vs Spotlight Reporting</a> and our <a href=\"/best/consolidation-software/\">best consolidation software</a> roundup.",
        ]),
        cta_box("Check the numbers on your own entities", "Joiin's 14-day trial runs on its full Max plan with no credit card."),
        faq_html(FAQ),
        related([("/compare/joiin-vs-fathom/", "Compare", "Joiin vs Fathom"), ("/best/consolidation-software/", "Best Of", "Best Consolidation Software"),
                 ("/review/joiin/", "Review", "Joiin Review"), ("/alternatives/fathom/", "Alternatives", "Fathom Alternatives")]),
    ]
    return f'''<main class="container" style="padding-top:1rem;padding-bottom:4rem;">
  <div style="max-width:760px;">
    <h1 style="font-size:clamp(1.6rem,4vw,2.25rem);margin-bottom:0.5rem;">Consolidation Software Cost Calculator</h1>
    <p style="color:var(--color-text-muted);font-size:1rem;margin-bottom:0.5rem;">Compare the monthly cost of Joiin, Fathom and Spotlight Reporting for your number of companies. Free tool by RankerToolAI · Prices updated October 24, 2026.</p>
    <p style="font-size:0.8rem;color:rgba(148,163,184,0.7);margin-bottom:1rem;">Disclosure: this page contains affiliate links, including to Joiin. We may earn a commission if you buy through them, at no extra cost to you. <a href="/affiliate-disclosure/">Read our disclosure</a>.</p>

{"".join(sections)}  </div>
</main>'''


if __name__ == "__main__":
    app = ld({"@context": "https://schema.org", "@type": "WebApplication", "name": "Consolidation Software Cost Calculator",
              "url": f"{SITE}/{P}/", "applicationCategory": "FinanceApplication", "operatingSystem": "Any",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}})
    build(P, "Consolidation Software Cost Calculator (Joiin, Fathom, Spotlight)",
          "Free calculator: monthly cost of Joiin, Fathom Pro and Spotlight Reporting for 1 to 300 companies, with cost per company. Prices updated October 2026.",
          [("Home", "/"), ("Consolidation Cost Calculator", f"/{P}/")],
          [app, faq_schema(FAQ)], main_html())
