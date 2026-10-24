#!/usr/bin/env python3
"""Joiin wave 3 (2026-10-24): pages for people who already know the Joiin name, plus Sage/MYOB guides.
  /compare/joiin-vs-fathom/
  /compare/joiin-vs-spotlight-reporting/
  /blog/how-to-consolidate-sage-companies/
  /blog/how-to-consolidate-myob-companies/
Organic only: Joiin bans its brand in paid ads, so these pages are never Ads Final URLs for brand keywords.
Reuses the shell/helpers of generate_joiin_cluster.py. Research-based, no hands-on test claims.
Facts checked 2026-10-24:
  Joiin pricing: joiin.co/pricing (table by company count; no separate per-plan prices any more).
  Joiin Sage: support.joiin.co article 42000109063 (direct: Sage Accounting US/UK/CA/IE; Sage 50/200/X3 via
    Manual Company Import). Joiin MYOB: joiin.co/integrations/myob (trial balance, daily sync, read-only OAuth).
  Fathom: fathomhq.com/pricing page script + feature list (Pro tiers $59/1, $315/10, $450/25, $805/50; Pro features).
  Spotlight: spotlightreporting.com/pricing (NZD) + /multi.
  MYOB: myob.com/au/support (consolidating reports for multiple company files = export/import to a master file).
  Sage Intacct: Sage help docs (Domestic / Global / Advanced Ownership consolidation subscriptions)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_joiin_cluster import (GO, BYLINE, build, page, prose, ul, table, cta_box, faq_html, faq_schema,
                                    related, toc, article_ld)

A = f'<a href="{GO}" rel="nofollow sponsored" target="_blank">'
JOIIN_PRICES = [("1", "$28", "$23"), ("2", "$36", "$29"), ("5", "$70", "$57"), ("10", "$111", "$92"),
                ("20", "$167", "$139"), ("50", "$217", "$174"), ("100", "$336", "$252")]
FATHOM_PRO = {"1": "$59", "2": "$118", "5": "$295", "10": "$315", "20": "$450", "50": "$805", "100": "$1,455"}
PRICE_NOTE = ("USD before sales tax, from each vendor's pricing page on October 24, 2026. Fathom uses the cheapest Pro tier "
              "for each count (Starter $59 +$59 per company, Silver $315 for 10 +$31, Gold $450 for 25 +$17, Platinum $805 for 50 +$13). "
              "Joiin's page shows one price table by company count, not separate prices per plan.")


def steps(items):
    return ('      <ol style="color:var(--color-text-muted);line-height:2;padding-left:1.5rem;">\n'
            + "\n".join(f"        <li>{x}</li>" for x in items) + "\n      </ol>")


def verdict_box(rows):
    return table(["", "Joiin", "Fathom"], rows, "Based on published pricing and feature pages, October 2026. Not a hands-on test.")


# ─────────────────────────── /compare/joiin-vs-fathom/ ───────────────────────────
F = "compare/joiin-vs-fathom"
F_FAQ = [
    ("Is Joiin cheaper than Fathom?",
     "Yes, on published prices, at every company count we checked. For two companies Joiin is $36/mo billed monthly ($29/mo annually) against $118/month on Fathom Pro; for 10 companies it's $111/mo ($92 annually) against $315; for 50 it's $217/mo ($174 annually) against $805. Fathom's Portfolio plan is cheaper per company ($67/month for 100) but doesn't include consolidation."),
    ("Which is better for consolidation, Joiin or Fathom?",
     "Both consolidate multiple entities with eliminations and multi-currency. Joiin is built around consolidation and connects natively to more ledgers, including Sage Accounting, Zoho Books, Pennylane and Fortnox. Fathom Pro adds three-way cash flow forecasting, custom exchange rates and client benchmarking on the same plan, and imports other systems via Excel."),
    ("Does Fathom work with Sage?",
     "Fathom's integrations list Xero, QuickBooks Online and Desktop, MYOB AccountRight (cloud and desktop), FreeAgent and Excel. Other systems such as Sage can be brought in through Excel import. Joiin connects directly to Sage Accounting (cloud) in the US, UK, Canada and Ireland."),
    ("Which has better forecasting?",
     "Fathom. Its Pro plan includes three-way cash flow forecasting, scenarios, driver-based and rolling forecasts and consolidated forecasts. Joiin includes budgets on every plan and forecasting from its Pro plan, but cash flow forecasting is Fathom's specialty."),
    ("Do both have a free trial?",
     "Yes. Both offer 14 days free. Joiin's trial runs on its full Max plan with no credit card required."),
    ("Can I use Joiin and Fathom together?",
     "Yes. One cost-effective mix is Fathom Portfolio ($67/month for 100 companies) for monitoring single-company clients, and Joiin for the clients that run groups and need consolidation, rather than moving every client onto Fathom Pro."),
]
F_SECTIONS = [
    toc([("verdict", "Quick Verdict"), ("pricing", "Pricing by Company Count"), ("consolidation", "Consolidation Features"),
         ("forecasting", "Reporting and Forecasting"), ("integrations", "Integrations"), ("users", "Users, Clients and Plans"),
         ("who", "Who Should Choose Which"), ("faq", "FAQ")]),
    f'''    <section id="verdict">
      <h2>Quick Verdict</h2>
{verdict_box([
        ["Price for 2 companies (monthly)", "$36", "$118 (Pro)"],
        ["Price for 10 companies (monthly)", "$111", "$315 (Pro)"],
        ["Consolidation & eliminations", "Every plan", "Pro"],
        ["Multi-currency", "Pro and Max", "Pro"],
        ["Your own FX rates", "Max", "Pro"],
        ["Cash flow forecasting", "Forecasting on Pro and Max", "Three-way forecasting on Pro"],
        ["Native ledger connections", "10, incl. Sage Accounting, Zoho Books, Fortnox", "Xero, QuickBooks, MYOB, FreeAgent + Excel import"],
        ["Users", "Unlimited", "Unlimited"],
        ["Free trial", "14 days, Max plan, no card", "14 days"],
    ])}
      <p>Choose <strong>Joiin</strong> if consolidation is the main job and you want the lowest price per company or a ledger Fathom doesn't connect to. Choose <strong>Fathom</strong> if your firm sells advisory work built on three-way cash flow forecasting, KPI analysis and client benchmarking, and the higher price is covered by that work.</p>
    </section>
''',
    cta_box("Test Joiin on your own group", "14 days on the full Max plan, no credit card. Rebuild one month's consolidated pack and compare it with Fathom."),
    prose("Pricing by Company Count", "pricing", [
        "Both tools price by the number of companies you connect, not by users. The difference is the size of the steps. Fathom Pro moves through four tiers (Starter, Silver, Gold and Platinum), and the page automatically applies the cheapest one for your count. Joiin publishes a single table by company count, with a discount for annual billing.",
        table(["Companies", "Fathom Pro (monthly)", "Joiin (monthly)", "Joiin (annual, per month)"],
              [[n, FATHOM_PRO[n], m, y] for n, m, y in JOIIN_PRICES], PRICE_NOTE),
        "On these numbers Fathom Pro costs roughly two to four times as much as Joiin at every size we checked. Fathom has one cheaper option, Fathom Portfolio, at $67/month for 100 companies, $189 for 300 or $405 for unlimited, but Portfolio is a monitoring plan for accounting firms and doesn't include consolidations. To consolidate a client on Fathom, that company has to be upgraded to Pro.",
        f"One caution on Joiin: its pricing page no longer lists separate prices for Core, Pro and Max, and multi-currency starts on Pro. If you need multi-currency or your own FX rates, confirm the price of that plan on {A}Joiin's pricing page</a> before you commit.",
    ]),
    prose("Consolidation Features", "consolidation", [
        "Both tools do real consolidation, not just side-by-side reports. Joiin includes chart of accounts mapping and intercompany eliminations on every plan, produces a consolidated P&amp;L, balance sheet, cash flow and trial balance, and lists intercompany management among its features. Multi-currency starts on Pro, and Max adds advanced FX so you can apply your own exchange rates.",
        "Fathom Pro's consolidation section lists consolidated financial reporting across systems, multi-currency, eliminations, adjustments, custom exchange rates, consolidated budgets, a custom chart of accounts, group forecasting and non-financial consolidation, for up to 300 entities. Custom exchange rates come with Pro, where Joiin keeps them for Max.",
        "In practice the core consolidation work is similar. Joiin's advantage is price and native ledger coverage; Fathom's is that consolidation sits inside a broader forecasting and advisory toolkit.",
    ]),
    prose("Reporting and Forecasting", "forecasting", [
        "This is where Fathom earns its higher price. Fathom Pro includes branded management reports per client, three-way cash flow forecasting, budgets, scenarios and what-ifs, custom KPIs and targets, an AI Commentary Writer, and benchmarking that ranks clients against each other. Its forecasting set includes driver-based, rolling and long-term forecasts and consolidated forecasts.",
        "Joiin covers the reporting side well for groups: financial statements, KPIs, sales and purchasing reports, budgets, custom layouts, dashboards and report packs on every plan, with PDF, CSV and Excel export. Forecasting starts on Pro, and Joiin Intelligence adds AI chat and summaries (AI agents on Pro, an MCP connection to Claude and ChatGPT on Max). If three-way cash flow forecasting is central to what you sell clients, test Fathom's version; if you mainly need consolidated management accounts and budgets, Joiin covers it for less.",
    ]),
    prose("Integrations", "integrations", [
        "Joiin's pricing page lists ten accounting connections: Xero, QuickBooks, Intuit Enterprise Suite, Sage, MYOB, FreeAgent, Puzzle, Pennylane, Zoho Books and Fortnox. Its direct Sage connection covers Sage Accounting (cloud) in the US, UK, Canada and Ireland; Sage 50, Sage 200 and X3 go through manual company import. Pro adds Stripe and non-financial data, and Max adds an API, Zapier and MCP.",
        "Fathom integrates with Xero, QuickBooks Online and Desktop, MYOB AccountRight (cloud and desktop) and FreeAgent, plus Excel import for any other system and Google Sheets for operational data. If a client is on QuickBooks Desktop or MYOB desktop, Fathom has the edge. If an entity is on Sage Accounting, Zoho Books, Pennylane or Fortnox, Joiin connects without spreadsheets.",
    ]),
    prose("Users, Clients and Plans", "users", [
        "Both include unlimited users. Joiin also states unlimited reports and clients on every plan, which is why accounting firms like it: the bill depends only on company count. Fathom's plan choice is about features. Portfolio is for monitoring a large client base cheaply, and Pro is for advanced reporting, forecasting and consolidation, with Enterprise quoted for 51+ companies.",
    ]),
    prose("Who Should Choose Which", "who", [
        ul([f"<strong>Business group with 2–20 entities:</strong> {A}Joiin</a>. Consolidation with eliminations on every plan and a much lower monthly cost.",
            "<strong>Group with an entity on Sage Accounting, Zoho Books, Pennylane or Fortnox:</strong> Joiin, for the native connection.",
            "<strong>Advisory firm selling cash flow forecasting and KPI work:</strong> Fathom Pro, for three-way forecasting, benchmarking and branded client reports.",
            "<strong>Firm with many single-company clients plus a few groups:</strong> Fathom Portfolio for monitoring and Joiin for the groups is a cost-effective mix.",
            "<strong>Clients on QuickBooks Desktop or MYOB desktop:</strong> Fathom, which lists both."]),
        f"The cheapest way to decide is to run both trials on the same group for the same month and compare the consolidated totals line by line. {A}Start with Joiin's 14-day trial</a>, which needs no card.",
    ]),
    prose("Switching From Fathom to Joiin", "switching", [
        steps(["Pick one group with intercompany activity and note last month's consolidated totals from Fathom.",
               "Start Joiin's trial and connect the same entities.",
               "Map the chart of accounts and set eliminations for the intercompany accounts.",
               "Compare Joiin's consolidated P&amp;L and balance sheet with Fathom's, line by line.",
               "Rebuild your monthly pack with Joiin's custom layouts and report packs, then price your real company count."]),
        "Keep Fathom running until the numbers agree for at least one full month. If you rely on Fathom's three-way cash flow forecasts, decide separately whether Joiin's forecasting (Pro and Max) covers them or whether that work stays in Fathom.",
    ]),
    cta_box("Joiin vs Fathom on your real numbers", "Connect your entities to Joiin's 14-day Max trial and check the consolidated P&amp;L before you pay anything."),
    faq_html(F_FAQ),
    related([("/review/joiin/", "Review", "Joiin Review"), ("/alternatives/fathom/", "Alternatives", "Fathom Alternatives"),
             ("/compare/joiin-vs-spotlight-reporting/", "Compare", "Joiin vs Spotlight Reporting"),
             ("/best/consolidation-software/", "Best Of", "Best Consolidation Software")]),
]

# ─────────────────────────── /compare/joiin-vs-spotlight-reporting/ ───────────────────────────
SP = "compare/joiin-vs-spotlight-reporting"
SP_FAQ = [
    ("Is Joiin cheaper than Spotlight Reporting?",
     "For most groups, yes. Joiin is $111/mo for 10 companies billed monthly ($92 annually, USD). Spotlight's Basic advisor plan is NZ$329/month excluding GST for up to 10 organisations, and Super VCFO 25 is NZ$495/month for up to 25. Spotlight's plans include training and advisory tools that Joiin doesn't, so compare on what you'll use."),
    ("Which is better for consolidation?",
     "Joiin is built around consolidation, with chart of accounts mapping and eliminations on every plan and ten native ledger connections. Spotlight's consolidation comes through Spotlight Multi, which aggregates and benchmarks up to 500 entities with multi-currency and suits franchises and networks; its page doesn't describe intercompany eliminations."),
    ("Which accounting systems do they connect to?",
     "Joiin lists Xero, QuickBooks, Intuit Enterprise Suite, Sage, MYOB, FreeAgent, Puzzle, Pennylane, Zoho Books and Fortnox. Spotlight's pages name Xero and QuickBooks and say other data can be imported or entered."),
    ("Is Spotlight Reporting only for accountants?",
     "Its advisor plans (Basic, Super VCFO 25 and 75, Enterprise) are designed for accounting and advisory firms, with training, account management and customer success support on the higher plans. Joiin sells the same plans to business groups and to accountants."),
    ("Do both offer a free trial?",
     "Yes, both offer 14 days free. Joiin's trial runs on its full Max plan without a credit card."),
    ("Does Spotlight Reporting handle intercompany eliminations?",
     "Spotlight's Multi page describes aggregation, benchmarking, multi-currency and use for consolidation, but it doesn't mention intercompany eliminations. If your companies trade with each other, ask Spotlight to show how eliminations work during the trial. Joiin includes chart of accounts mapping and eliminations on every plan."),
    ("Can a business group use Spotlight Reporting directly?",
     "Spotlight's published plans are advisor plans aimed at accounting and advisory firms, so a business group would usually reach it through its accountant. Joiin sells the same plans to business groups and to accountants, and its pricing depends only on how many companies you connect."),
    ("Which is easier to start with?",
     "Joiin's trial starts on its top plan without a card, so you can connect entities and see consolidated reports on day one. Spotlight's advisor plans include training sessions and, on Super VCFO, an account manager, which helps firms rolling it out to many clients."),
]
SP_SECTIONS = [
    toc([("verdict", "Quick Verdict"), ("pricing", "Pricing"), ("consolidation", "Consolidation and Multi-Entity"),
         ("advisory", "Reporting, Forecasting and Advisory"), ("integrations", "Integrations"), ("who", "Who Should Choose Which"), ("faq", "FAQ")]),
    f'''    <section id="verdict">
      <h2>Quick Verdict</h2>
{table(["", "Joiin", "Spotlight Reporting"], [
        ["Built for", "Business groups and accountants", "Accounting and advisory firms"],
        ["Pricing basis", "Company count, unlimited users and clients", "Advisor plans by number of organisations"],
        ["Entry price", "$28/mo (1 company), $23/mo annual", "NZ$329/mo excl. GST, up to 10 orgs"],
        ["Consolidation", "COA mapping + eliminations, every plan", "Spotlight Multi, up to 500 entities"],
        ["Multi-currency", "Pro and Max", "Yes (Multi)"],
        ["Ledgers named", "10 (Xero, QuickBooks, Sage, MYOB, FreeAgent and more)", "Xero, QuickBooks"],
        ["Training & account management", "Not listed on pricing page", "Included, more on Super VCFO plans"],
        ["Free trial", "14 days, Max plan, no card", "14 days"],
    ], "Based on each vendor's published pricing and feature pages, October 2026. Not a hands-on test.")}
      <p>Choose <strong>Joiin</strong> for consolidation across mixed ledgers at a per-company price. Choose <strong>Spotlight</strong> if you're an advisory firm that wants a packaged reporting, forecasting and dashboard service with training and customer success support, or you aggregate a franchise or network of many similar entities.</p>
    </section>
''',
    cta_box("Consolidating a group, not running an advisory practice?", "Joiin's 14-day Max trial needs no card. Connect your entities and see the consolidated reports first."),
    prose("Pricing", "pricing", [
        "The two price on different models. Joiin charges by the number of companies connected, with unlimited users, reports and clients:",
        table(["Companies", "Joiin monthly", "Joiin annual (per month)"], [[n, m, y] for n, m, y in JOIIN_PRICES],
              "USD, joiin.co/pricing, October 24, 2026. Over 100 companies: from $336/mo plus $2.80 per extra company."),
        "Spotlight sells advisor plans by organisation count. Its pricing page shows, in NZD excluding GST: Basic NZ$329/month for up to 10 organisations, Super VCFO 25 at NZ$495/month for up to 25, Super VCFO 75 at NZ$995/month for up to 75, and Enterprise on request. Its UK Basic price is £320/month. Pricing is also offered in AUD, USD, CAD and ZAR, so check your currency on Spotlight's page.",
        f"For a business group with a handful of entities, Joiin is the cheaper route. For an advisory firm, the comparison depends on how many client organisations you'd load and whether you'd use Spotlight's included training and account management. Check both at your real count; Joiin's {A}price table</a> is public.",
    ]),
    prose("Consolidation and Multi-Entity", "consolidation", [
        "Joiin's whole product is built around consolidation: chart of accounts mapping, intercompany eliminations and the full set of consolidated statements on every plan, with multi-currency from Pro and your own FX rates on Max.",
        "Spotlight handles groups through Spotlight Multi, described as a way to aggregate and benchmark at scale: financial and non-financial data for up to 500 entities, multiple currencies, and use for consolidation. Its customer examples are franchise systems and networks, such as consolidated reports for 200 stores. The Multi page doesn't mention intercompany eliminations, so if your group trades between its own companies, ask Spotlight how eliminations are handled before you choose it.",
    ]),
    prose("Reporting, Forecasting and Advisory", "advisory", [
        "Spotlight is an advisory suite. Its advisor plans include Reporting, Forecasting and Dashboard products, unlimited dashboards on Super VCFO and above, and ESG reporting through Spotlight Sustain as an option. The higher plans add training sessions, an account manager and customer success support, which matters to firms building an advisory service line.",
        "Joiin focuses on group reporting: P&amp;L, balance sheet, cash flow, trial balance, KPIs, sales and purchasing reports, budgets, custom layouts, dashboards and report packs on every plan, forecasting from Pro, and AI chat and summaries throughout. It doesn't sell training packages on its pricing page.",
    ]),
    prose("Integrations", "integrations", [
        "Joiin lists ten accounting connections, including Sage, MYOB, FreeAgent, Zoho Books, Pennylane and Fortnox alongside Xero and QuickBooks. Spotlight's pages name Xero and QuickBooks integrations and allow other data to be imported or entered. A group with an entity outside Xero and QuickBooks will find Joiin easier to keep in sync.",
    ]),
    prose("Who Should Choose Which", "who", [
        ul([f"<strong>Business group consolidating its own entities:</strong> {A}Joiin</a>, for eliminations on every plan and per-company pricing.",
            "<strong>Group with entities on Sage, MYOB or other ledgers:</strong> Joiin, for the wider native connection list.",
            "<strong>Advisory firm building a packaged CFO service:</strong> Spotlight, for its reporting, forecasting and dashboard suite plus training and support.",
            "<strong>Franchise or network benchmarking many similar entities:</strong> Spotlight Multi."]),
        f"If you're unsure, start with the tool whose trial asks least of you. {A}Joiin's trial</a> runs on its top plan and needs no card.",
    ]),
    prose("Cost Examples", "cost", [
        "Because the two price differently, here's how the published numbers compare for typical buyers (Joiin in USD, Spotlight in NZD excluding GST; convert before comparing):",
        ul(["<strong>A business group with 3 entities.</strong> Joiin falls between its 2-company ($36/mo monthly, $29 annual) and 5-company ($70/mo monthly, $57 annual) prices. Spotlight's smallest advisor plan, Basic, is NZ$329/month for up to 10 organisations.",
            "<strong>An accounting firm reporting on 10 client companies.</strong> Joiin is $111/mo monthly or $92/mo annually, with unlimited users and clients. Spotlight Basic covers up to 10 organisations for NZ$329/month and includes training.",
            "<strong>A firm with 25 client companies.</strong> Joiin lists $167/mo for 20 and $217/mo for 50 (monthly). Spotlight's Super VCFO 25 is NZ$495/month for up to 25 organisations, with an account manager and customer success support.",
            "<strong>A franchise network of 200 locations.</strong> Joiin is past its 100-company tier (from $336/mo plus $2.80 per extra company). Spotlight Multi is designed for this case and handles up to 500 entities; ask Spotlight for an Enterprise quote."]),
        "The pattern: Joiin is cheaper for groups and for firms that mainly need consolidated management accounts. Spotlight's price includes advisory tooling and support that a firm selling CFO services may value more than the difference.",
    ]),
    prose("What to Test in Each Trial", "trial", [
        "Both trials last 14 days. Use them to answer the questions that decide the choice:",
        ul(["<strong>Eliminations:</strong> consolidate one group with real intercompany transactions and check that the eliminations tie out.",
            "<strong>Ledgers:</strong> connect every system in the group, including any entity outside Xero and QuickBooks.",
            "<strong>Monthly effort:</strong> after the first setup, time how long next month's refresh takes.",
            "<strong>Output:</strong> produce the pack you actually send to a board or client and ask whether it's clearer than the current one.",
            "<strong>Support:</strong> ask each vendor one real question during the trial and note how quickly and how well they answer."]),
    ]),
    cta_box("See your group consolidated in Joiin", "Full Max plan free for 14 days. No credit card."),
    faq_html(SP_FAQ),
    related([("/review/joiin/", "Review", "Joiin Review"), ("/compare/joiin-vs-fathom/", "Compare", "Joiin vs Fathom"),
             ("/best/consolidation-software/", "Best Of", "Best Consolidation Software"),
             ("/best/management-reporting-software-for-accountants/", "Best Of", "Management Reporting Software for Accountants")]),
]

# ─────────────────────────── /blog/how-to-consolidate-sage-companies/ ───────────────────────────
SG = "blog/how-to-consolidate-sage-companies"
SG_FAQ = [
    ("Can Sage consolidate multiple companies?",
     "It depends on the Sage product. Sage Intacct has native multi-entity consolidation through its Domestic, Global and Advanced Ownership consolidation subscriptions. Sage Accounting (the cloud product for small businesses) reports one company at a time, so groups combine reports in a spreadsheet or use a consolidation app such as Joiin."),
    ("Does Joiin work with Sage 50?",
     "Not directly. Joiin's help centre says its direct connection covers Sage Accounting (cloud) in the US, UK, Canada and Ireland. Sage 50, Sage 200 Professional and Sage X3 can be used through Joiin's Manual Company Import feature."),
    ("Can I consolidate a Sage company with a Xero or QuickBooks company?",
     "Yes, with a tool that connects to both. Joiin connects to Sage Accounting, Xero, QuickBooks and seven other ledgers and maps their charts of accounts into one reporting structure, so a subsidiary doesn't need to migrate."),
    ("How much does it cost to consolidate Sage companies with Joiin?",
     "Joiin's published table is $36/mo for two companies billed monthly ($29/mo annually), $70/mo for five ($57 annually) and $111/mo for ten ($92 annually), in USD, with unlimited users. There's a 14-day free trial with no card."),
]
SG_SECTIONS = [
    toc([("options", "Which Sage Do You Use?"), ("intacct", "Sage Intacct: Built-In Consolidation"),
         ("spreadsheet", "Sage Accounting or Sage 50: The Spreadsheet Method"), ("joiin", "Using Joiin With Sage"),
         ("mixed", "Groups With Sage and Other Ledgers"), ("faq", "FAQ")]),
    prose("Which Sage Do You Use?", "options", [
        "\"Sage\" covers several different products, and the right way to consolidate depends on which one each company runs:",
        ul(["<strong>Sage Intacct</strong>: a mid-market cloud financial system with native multi-entity consolidation.",
            "<strong>Sage Accounting</strong> (formerly Sage Business Cloud Accounting / Sage One): cloud accounting for small businesses, one company per subscription.",
            "<strong>Sage 50 and Sage 200</strong>: desktop or hybrid products, each company in its own data file.",
            "<strong>Sage X3</strong>: an ERP for larger businesses."]),
        "For the last three, you need a way to bring several companies' figures together, remove intercompany transactions and produce one set of group reports.",
    ]),
    prose("Sage Intacct: Built-In Consolidation", "intacct", [
        "If your group already runs on Sage Intacct, use its own tools. Sage's documentation describes three consolidation subscriptions: Domestic Consolidation for fully owned entities in one base currency, Global Consolidation for fully owned entities in multiple base currencies, and Advanced Ownership Consolidation for more complex ownership structures. Intacct is a significant step up in cost and implementation from Sage Accounting, so it's usually a reason to migrate rather than something you add for reporting alone.",
    ]),
    prose("Sage Accounting or Sage 50: The Spreadsheet Method", "spreadsheet", [
        "For two companies with similar charts of accounts, a spreadsheet works:",
        steps(["Run the trial balance for the same period end in each company.",
               "Export each to Excel and paste it into its own tab.",
               "Map every account to one group chart of accounts with a lookup column.",
               "Add an eliminations column that reverses intercompany sales, recharges, loans and balances.",
               "Sum the mapped columns plus eliminations to get the consolidated trial balance, then build the P&amp;L and balance sheet from it."]),
        "It breaks down with more companies, foreign subsidiaries or monthly board packs: every new account breaks the mapping and eliminations are re-entered by hand each month.",
    ]),
    prose("Using Joiin With Sage", "joiin", [
        "Joiin connects directly to <strong>Sage Accounting</strong> in the US, UK, Canada and Ireland. Per Joiin's Sage page, data is kept in sync automatically, budgets can be imported from Sage, and multiple Sage companies can be consolidated with intercompany eliminations and multi-currency options. Sage 50, Sage 200 Professional and Sage X3 aren't directly connected; Joiin's help centre points them to its Manual Company Import feature instead.",
        "Setup follows the same logic as the spreadsheet, done once:",
        steps(["Start a free trial (14 days on the Max plan, no card).",
               "Connect each Sage Accounting company, and add any Sage 50 or Sage 200 company through Manual Company Import.",
               "Map each company's accounts to the group reporting structure.",
               "Set eliminations for your intercompany accounts.",
               "Choose the reporting currency (multi-currency needs Pro or Max) and run the consolidated P&amp;L, balance sheet and cash flow."]),
        table(["Companies", "Joiin monthly", "Joiin annual (per month)"], [[n, m, y] for n, m, y in JOIIN_PRICES[:5]],
              "USD, joiin.co/pricing, October 24, 2026. Unlimited users, reports and clients."),
    ]),
    cta_box("Consolidate your Sage companies", "Connect them to Joiin's 14-day Max trial, no credit card, and compare the consolidated totals with your spreadsheet."),
    prose("Groups With Sage and Other Ledgers", "mixed", [
        "Acquired subsidiaries often keep their own system. Because Joiin also connects to Xero, QuickBooks, MYOB, FreeAgent, Zoho Books, Pennylane and Fortnox, a group with one company on Sage Accounting and another on Xero can report together without migrating either. Fathom, a popular alternative, doesn't list a Sage connection and relies on Excel import for systems it doesn't integrate with. See our <a href=\"/best/consolidation-software/\">consolidation software comparison</a> for the full list.",
    ]),
    faq_html(SG_FAQ),
    related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software"), ("/review/joiin/", "Review", "Joiin Review"),
             ("/blog/how-to-consolidate-myob-companies/", "Guide", "How to Consolidate MYOB Companies"),
             ("/blog/how-to-consolidate-multiple-xero-organisations/", "Guide", "Consolidate Multiple Xero Organisations")]),
]

# ─────────────────────────── /blog/how-to-consolidate-myob-companies/ ───────────────────────────
MY = "blog/how-to-consolidate-myob-companies"
MY_FAQ = [
    ("Can MYOB produce consolidated reports for multiple companies?",
     "Not as a built-in group report. MYOB's own support guidance says that in most cases you export and import accounts into one master company file, and that there's no one-size-fits-all solution. Many groups use a reporting add-on instead."),
    ("Which tools consolidate MYOB companies?",
     "Joiin, Fathom and Calxa are among the tools that connect to MYOB. Joiin syncs each MYOB company's trial balance daily through a read-only connection and consolidates it with eliminations. Fathom connects to MYOB AccountRight cloud and desktop."),
    ("Does Joiin write anything back to MYOB?",
     "No. Joiin's MYOB page describes a one-way, read-only connection: data flows into Joiin and nothing is written back to MYOB."),
    ("How much does Joiin cost in Australia or New Zealand?",
     "Joiin bills in AUD and NZD as well as USD. In USD, its table is $36/mo for two companies billed monthly ($29/mo annually) and $111/mo for ten ($92 annually). Check the AUD or NZD figure on Joiin's pricing page."),
]
MY_SECTIONS = [
    toc([("native", "What MYOB Offers Natively"), ("master", "Option A: A Master Company File"),
         ("spreadsheet", "Option B: Combine Reports in Excel"), ("app", "Option C: A Consolidation App"),
         ("joiin", "Using Joiin With MYOB"), ("faq", "FAQ")]),
    prose("What MYOB Offers Natively", "native", [
        "MYOB Business and AccountRight keep each company in its own company file, and there's no built-in report that consolidates several files. MYOB's support guidance on consolidating reports for multiple company files says that in most cases you export and import accounts into one master company file, and that there's no one-size-fits-all solution. Its community also suggests exporting reports to Excel and combining them there.",
    ]),
    prose("Option A: A Master Company File", "master", [
        "MYOB's suggested route is to create a master company file, import each company's accounts into it and post the balances there. It keeps everything inside MYOB, but it's a manual monthly import, eliminations still have to be journalled by hand, and the master file has to be kept in step with every chart of accounts change in the subsidiaries.",
    ]),
    prose("Option B: Combine Reports in Excel", "spreadsheet", [
        steps(["Run the trial balance for the same period in each company file.",
               "Export to Excel, one tab per company.",
               "Map accounts to a group chart of accounts.",
               "Add an eliminations column for intercompany transactions and balances.",
               "Sum to a consolidated trial balance and build the group P&amp;L and balance sheet."]),
        "Fine for two simple companies; slow and error-prone beyond that.",
    ]),
    prose("Option C: A Consolidation App", "app", [
        "Reporting apps connect to each MYOB company and refresh automatically, so the mapping and eliminations are set once. Options that connect to MYOB include Joiin, Fathom (MYOB AccountRight cloud and desktop) and Calxa. Joiin is usually the cheapest for small groups, and it also connects to Xero, QuickBooks, Sage and others if part of the group runs a different ledger, which is common in Australia and New Zealand where Xero and MYOB sit side by side.",
    ]),
    prose("Using Joiin With MYOB", "joiin", [
        "According to Joiin's MYOB page, the connector suits any business or accounting firm using MYOB. It uses a secure OAuth connection with no API keys, imports each company's trial balance automatically and syncs daily. The connection is one-way and read-only, so nothing is written back to MYOB.",
        steps(["Start Joiin's free trial (14 days on the Max plan, no card).",
               "Connect each MYOB company through the OAuth prompt.",
               "Map each company's accounts to the group reporting structure.",
               "Set eliminations for intercompany accounts.",
               "Run the consolidated P&amp;L, balance sheet and cash flow, and save them as a monthly report pack."]),
        table(["Companies", "Joiin monthly", "Joiin annual (per month)"], [[n, m, y] for n, m, y in JOIIN_PRICES[:5]],
              "USD, joiin.co/pricing, October 24, 2026. Joiin also bills in AUD and NZD."),
    ]),
    cta_box("Consolidate your MYOB companies", "Connect them to Joiin's 14-day Max trial. No credit card, read-only connection."),
    faq_html(MY_FAQ),
    related([("/best/consolidation-software/", "Best Of", "Best Consolidation Software"), ("/review/joiin/", "Review", "Joiin Review"),
             ("/blog/how-to-consolidate-sage-companies/", "Guide", "How to Consolidate Sage Companies"),
             ("/blog/how-to-consolidate-multiple-xero-organisations/", "Guide", "Consolidate Multiple Xero Organisations")]),
]

if __name__ == "__main__":
    build(F, "Joiin vs Fathom (2026): Pricing, Consolidation &amp; Forecasting",
          "Joiin vs Fathom compared: price by company count, consolidation, forecasting and integrations. Which fits a business group or an accounting firm.",
          [("Home", "/"), ("Compare", "/compare/"), ("Joiin vs Fathom", f"/{F}/")],
          [article_ld("Joiin vs Fathom (2026): Pricing, Consolidation & Forecasting", F), faq_schema(F_FAQ)],
          page("Joiin vs Fathom (2026)", BYLINE,
               f"{A}<strong style=\"color:#4ade80;\">Joiin</strong></a> is cheaper at every company count we checked ($36/mo vs $118 for two companies, monthly) "
               "and connects natively to more ledgers. Fathom costs more but adds three-way cash flow forecasting, custom FX rates and client benchmarking on Pro.",
               F_SECTIONS))
    build(SP, "Joiin vs Spotlight Reporting (2026): Which Fits Your Group?",
          "Joiin vs Spotlight Reporting: consolidation, pricing, integrations and advisory features compared for business groups and accounting firms.",
          [("Home", "/"), ("Compare", "/compare/"), ("Joiin vs Spotlight Reporting", f"/{SP}/")],
          [article_ld("Joiin vs Spotlight Reporting (2026)", SP), faq_schema(SP_FAQ)],
          page("Joiin vs Spotlight Reporting (2026)", BYLINE,
               f"For consolidating a group across mixed ledgers at a per-company price, choose {A}<strong style=\"color:#4ade80;\">Joiin</strong></a>. "
               "For an advisory firm that wants a packaged reporting, forecasting and dashboard suite with training, or a franchise network, choose Spotlight.",
               SP_SECTIONS))
    build(SG, "How to Consolidate Multiple Sage Companies (2026 Guide)",
          "Consolidate Sage Accounting, Sage 50 or Sage 200 companies: the spreadsheet method, Sage Intacct, and apps like Joiin, with eliminations.",
          [("Home", "/"), ("Blog", "/blog/"), ("Consolidate Sage Companies", f"/{SG}/")],
          [article_ld("How to Consolidate Multiple Sage Companies", SG), faq_schema(SG_FAQ)],
          page("How to Consolidate Multiple Sage Companies", BYLINE.replace("Independent guide", "Guide"),
               "On Sage Intacct, use its built-in consolidation. On Sage Accounting, Sage 50 or Sage 200, either combine trial balances in a spreadsheet "
               f"or use an app: {A}<strong style=\"color:#4ade80;\">Joiin</strong></a> connects directly to Sage Accounting and imports Sage 50/200 manually, from $29/mo for two companies (annual).",
               SG_SECTIONS))
    build(MY, "How to Consolidate MYOB Companies (2026 Guide)",
          "MYOB has no built-in group report. Three ways to consolidate MYOB company files: a master file, Excel, or an app like Joiin with eliminations.",
          [("Home", "/"), ("Blog", "/blog/"), ("Consolidate MYOB Companies", f"/{MY}/")],
          [article_ld("How to Consolidate MYOB Companies", MY), faq_schema(MY_FAQ)],
          page("How to Consolidate MYOB Companies", BYLINE.replace("Independent guide", "Guide"),
               "MYOB doesn't consolidate company files on its own. Use a master company file or Excel for two simple companies; for more, connect them to "
               f"an app like {A}<strong style=\"color:#4ade80;\">Joiin</strong></a> (read-only daily sync, eliminations included).", MY_SECTIONS))
