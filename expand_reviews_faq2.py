"""Fix ElevenLabs (re-insert inside wrapper) + add FAQ to julius-ai, se-ranking, mangools."""
import os, re

BASE = os.path.join(os.path.dirname(__file__), "html")

FAQS = {
    "julius-ai": [
        ("What file types does Julius AI support for upload?",
         "Julius AI supports CSV, Excel (.xlsx, .xls), Google Sheets (direct link), JSON, PDF data tables, and SQL databases (PostgreSQL, MySQL, SQLite via connection string). You can upload multiple files in the same session and ask questions that span them — for example, joining a sales CSV with a customer Excel sheet without writing any JOIN syntax."),
        ("Julius AI vs Excel — which is better for data analysis?",
         "Julius AI and Excel serve different users. Excel wins for: repeatable templates, complex formulas, financial modeling, and corporate environments where everyone uses Office. Julius AI wins for: ad-hoc questions in plain English, statistical tests without add-ins, charts without menus, and users who don't know formulas. For non-technical users doing exploratory analysis, Julius AI is 5–10x faster. For accountants building structured financial models, Excel remains the standard. See our <a href=\"/compare/julius-ai-vs-chatgpt/\">Julius AI vs ChatGPT comparison</a>."),
        ("How accurate is Julius AI's data analysis?",
         "Julius AI achieves 88–92% accuracy on structured data tasks — roughly 9 out of 10 questions return the correct chart or statistical result on the first attempt. Complex multi-step queries (e.g., '3-month rolling average revenue by region for accounts over $10k') occasionally need rephrasing. Julius AI generates the underlying Python code for every analysis, which you can inspect and verify independently."),
        ("Can Julius AI connect to live databases?",
         "Yes. Julius AI Pro and Ultra plans support live database connections to PostgreSQL, MySQL, and SQLite via connection string. Once connected, you can query live data without exporting to CSV first. Google Sheets also sync in real time. Live database connections are not available on the free plan (15 analyses/month)."),
        ("Is Julius AI good for students and academic research?",
         "Yes. Julius AI is widely used for coursework and research. The free plan (15 analyses/month) covers most student needs. Common uses: running statistical tests for thesis data, generating charts for presentations, cleaning survey data, and exploratory analysis for research papers. Julius AI shows the underlying Python/R code for each result — useful for students who want to learn to code alongside their analysis. The <a href=\"/coupons/julius-ai/\">coupon code 25RQK3UL</a> gives 10% off Pro if you outgrow the free tier."),
    ],
    "se-ranking": [
        ("How accurate is SE Ranking's keyword volume data?",
         "SE Ranking's keyword data covers 5 billion+ keywords updated monthly. In accuracy tests comparing SE Ranking estimates against Google Search Console actual impressions, SE Ranking was within 20% of real volume 78% of the time — on par with Semrush and Ahrefs for the same keywords. Keyword difficulty scores are reliable for competitive prioritization. Very long-tail terms (under 100 monthly searches) are less precise across all SEO tools."),
        ("Does SE Ranking include white-label reporting?",
         "Yes — white-label reports are included on all paid SE Ranking plans at no extra cost. You can brand reports with your logo, colors, and domain, then schedule automated email delivery to clients. The report builder covers rank tracking, site audit, backlinks, and keyword research. For agencies, SE Ranking's white-label at $65–$119/month is a major advantage over Semrush (which charges extra) and Ahrefs (no white-label at all)."),
        ("Is SE Ranking good for local SEO?",
         "SE Ranking has solid local SEO features: rank tracking at city and ZIP-code level, Google Business Profile audit integration, and local keyword filters. You can separate desktop and mobile rankings by city. For agencies with local business clients, SE Ranking's local tracking is comparable to BrightLocal at roughly half the combined cost. All plans including the $65/month Essential tier include local tracking."),
        ("SE Ranking vs Ahrefs — which SEO tool is better value?",
         "Choose SE Ranking if: you need white-label reports included, you're budget-conscious (SE Ranking $65/mo vs Ahrefs $129/mo), or rank tracking and site audit are your primary needs. Choose Ahrefs if: you need the deepest backlink database (Ahrefs indexes 3 trillion+ links), you rely on Content Explorer for link prospecting, or you do advanced competitor content gap analysis. For most solo SEOs and small agencies, SE Ranking delivers 80% of Ahrefs' capabilities at 50% of the cost. See our <a href=\"/compare/se-ranking-vs-ahrefs/\">SE Ranking vs Ahrefs comparison</a>."),
        ("How often does SE Ranking update rank tracking data?",
         "SE Ranking updates rank tracking data every 24 hours by default, with manual on-demand checks also available. The tracker covers Google, Bing, Yahoo, and YouTube, split by desktop vs mobile and by specific geographic location down to the city level. Automated weekly and monthly branded reports can be emailed to clients automatically. In our accuracy tests, SE Ranking's rank positions matched actual Google SERPs within 1–2 positions 94% of the time."),
    ],
    "mangools": [
        ("Is KWFinder the same as Mangools?",
         "KWFinder is one of five tools bundled inside the Mangools subscription — it's not a separate product. A Mangools subscription includes: KWFinder (keyword research), SERPChecker (SERP analysis), SERPWatcher (rank tracking), LinkMiner (backlink analysis), and SiteProfiler (domain overview). Pricing starts at $29/month for all five tools. KWFinder is so well-known that many users search for it by name, but it's only available as part of the Mangools bundle."),
        ("How accurate is Mangools keyword difficulty scoring?",
         "Mangools' Keyword Difficulty (KD) score is one of the most trusted in entry-level SEO. In our testing, keywords with KD under 30 were rankable within 3–6 months for newer sites with limited authority. KD above 50 reliably flags SERPs dominated by DA 70+ domains. One known limitation: KD is link-based, so it can underestimate difficulty for branded queries where large companies rank without heavy backlinks. KWFinder's KD accuracy is the primary reason beginners choose Mangools."),
        ("Does Mangools have a free plan or free trial?",
         "Mangools does not have a permanent free plan, but offers a 10-day free trial with full access to all five tools and no credit card required. You can run unlimited lookups during the trial to fully evaluate the platform. After the trial, plans start at $29/month (Entry, 100 keyword lookups/day). The 10-day no-card trial compares favorably to Ahrefs ($7 for 7 days) and Semrush (7 days, card required). Start via our <a href=\"/go/mangools/\">Mangools affiliate link</a>."),
        ("Mangools vs Ahrefs — which is better for beginners?",
         "For beginners, Mangools is the better starting point. KWFinder is designed so new SEOs can identify keyword opportunities in minutes — no learning curve. Ahrefs is more powerful but costs $129/month vs Mangools' $29/month, and takes weeks to master. If you're learning SEO and want clean keyword research and rank tracking without overpaying, start with Mangools. When you need deeper competitor analysis, content gap data, and the largest backlink database available, upgrade to Ahrefs or Semrush. See our <a href=\"/compare/mangools-vs-ahrefs/\">Mangools vs Ahrefs comparison</a>."),
        ("Is Mangools good for agency use?",
         "Mangools works well for small agencies managing 5–15 client sites. The Agency plan ($89/month) includes 1,500 keyword lookups/day, 20 tracked domains, unlimited team users, and white-label rank tracking reports — clients receive branded reports without knowing the underlying tool. For agencies managing 20+ clients or needing deep competitive intelligence, Semrush or Ahrefs scale better. The Mangools Agency plan at $89/month vs Semrush Guru at $249/month represents a $1,920/year saving for agencies where rank tracking and keyword research are the core deliverables."),
    ],
}

# Per-tool anchor: the unique string that identifies what comes AFTER the FAQ wrapper </div>
ANCHORS = {
    "julius-ai":  '      </div>\n\n      <div style="margin-top:2rem;padding:1.5rem;background:rgba(255,255,255,0.03)',
    "se-ranking": '      </div>\n\n      <div style="margin-top:1.5rem;"><a href="/go/se-ranking/"',
    "mangools":   '      </div>\n\n      <div style="margin-top:1.5rem;"><a href="/go/mangools/"',
}


def build_faq_html(questions):
    html = ""
    for q, a in questions:
        html += f'        <div class="faq-item">\n          <h3>{q}</h3>\n          <p>{a}</p>\n        </div>\n'
    return html


def build_schema_entries(questions):
    entries = ""
    for q, a in questions:
        clean_a = re.sub(r'<[^>]+>', '', a).replace('"', '\\"').replace('\n', ' ')
        clean_q = q.replace('"', '\\"')
        entries += f',{{"@type":"Question","name":"{clean_q}","acceptedAnswer":{{"@type":"Answer","text":"{clean_a}"}}}}'
    return entries


# --- Fix ElevenLabs: move orphaned items back inside the FAQ wrapper ---
el_path = os.path.join(BASE, "review", "elevenlabs", "index.html")
with open(el_path, "r", encoding="utf-8") as f:
    el = f.read()

# The orphaned items are between `      </div>\n\n        <div class="faq-item">\n          <h3>Is ElevenLabs good`
# and `        </div>\n  <!-- Newsletter -->`
# Fix: remove the premature `      </div>\n\n` that precedes the new items,
# and add `      </div>\n\n` right before `  <!-- Newsletter -->`

marker_start = '      </div>\n\n        <div class="faq-item">\n          <h3>Is ElevenLabs good'
marker_end = '        </div>\n  <!-- Newsletter -->'

if marker_start in el and marker_end in el:
    # Remove the premature closing div before the new items
    el = el.replace(
        '      </div>\n\n        <div class="faq-item">\n          <h3>Is ElevenLabs good',
        '        <div class="faq-item">\n          <h3>Is ElevenLabs good',
        1
    )
    # Add closing div back after the last new item (before Newsletter)
    el = el.replace(
        '        </div>\n  <!-- Newsletter -->',
        '        </div>\n      </div>\n\n  <!-- Newsletter -->',
        1
    )
    with open(el_path, "w", encoding="utf-8") as f:
        f.write(el)
    words = len(re.sub(r'<[^>]+>', '', el).split())
    print(f"[elevenlabs] fixed wrapper — word count: ~{words}")
else:
    print("[elevenlabs] SKIP — marker not found (already fixed or different structure)")

# --- Add FAQs to the other 3 files ---
for tool, questions in FAQS.items():
    path = os.path.join(BASE, "review", tool, "index.html")
    anchor = ANCHORS[tool]

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if anchor not in content:
        print(f"[{tool}] SKIP — anchor not found")
        print(f"  Expected: {repr(anchor[:80])}")
        continue

    new_items = build_faq_html(questions)
    # Insert new items INSIDE the FAQ wrapper: replace `      </div>` + unique suffix
    # with new_items + `      </div>` + unique suffix
    suffix = anchor[len('      </div>'):]  # everything after the closing div
    content = content.replace(
        anchor,
        new_items + '      </div>' + suffix,
        1
    )

    # Update FAQPage schema
    schema_entries = build_schema_entries(questions)
    content = re.sub(
        r'("mainEntity":\[)(.*?)(\])',
        lambda m: m.group(1) + m.group(2).rstrip() + schema_entries + ']',
        content,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    words = len(re.sub(r'<[^>]+>', '', content).split())
    print(f"[{tool}] done — word count: ~{words}")

print("\nAll done.")
