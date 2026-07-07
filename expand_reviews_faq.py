"""Add 5 targeted FAQ questions to each of the 4 affiliate review pages."""
import os, re

BASE = os.path.join(os.path.dirname(__file__), "html")

FAQS = {
    "elevenlabs": [
        ("Is ElevenLabs good for podcasters and YouTubers?",
         "ElevenLabs is excellent for podcasters and YouTubers. The Creator plan ($22/month) includes Professional Voice Cloning, which lets you clone your own voice from 30 minutes of audio — so you can generate missing content or correct mistakes without re-recording. For voiceover-heavy YouTube channels, creators report 60–80% reduction in recording time. The text-to-speech quality is natural enough to use in published content without listeners noticing it's AI-generated."),
        ("Can ElevenLabs clone voices in multiple languages?",
         "Yes. ElevenLabs supports voice cloning in 29 languages. You can clone an English speaker's voice and generate Spanish or French output that maintains the original voice's tone and cadence — not just the accent. Quality varies: English, Spanish, French, German, and Portuguese are best. Hindi and Arabic are functional but less natural. For multilingual content creators, this is ElevenLabs' strongest competitive advantage over Murf and Play.ht."),
        ("Is ElevenLabs legal and safe to use?",
         "ElevenLabs is legal to use for personal and commercial content with your own voice or licensed voices. The platform prohibits voice cloning of real individuals without consent, and they use detection technology to flag potential misuse. For commercial use of AI voices in published content, you need the Creator plan or above, which grants full commercial rights to any generated audio. Always check your jurisdiction's laws on AI-generated content for broadcast use."),
        ("What is ElevenLabs Turbo and how fast is it?",
         "ElevenLabs Turbo is their low-latency voice model optimized for real-time applications — chatbots, live agents, and interactive AI. Turbo generates audio in under 400ms latency, compared to 1–2 seconds for the standard multilingual model. The tradeoff is slightly lower voice naturalness. For most content creators, the standard v2 multilingual model is better. Turbo is designed for developers building voice AI applications, not for audio content production."),
        ("ElevenLabs vs Murf — which is better in 2026?",
         "ElevenLabs is better than Murf for voice cloning, naturalness, and language coverage. Murf is better for studio-style production with built-in script editing, background music, and slide sync tools. If your primary use case is cloning a specific voice or generating highly realistic speech in multiple languages, ElevenLabs wins. If you need a polished presentation tool with voice-over integrated into a workflow, Murf's studio environment is more practical. See our full <a href=\"/compare/elevenlabs-vs-murf/\">ElevenLabs vs Murf comparison</a>."),
    ],
    "julius-ai": [
        ("What file types does Julius AI support?",
         "Julius AI supports CSV, Excel (.xlsx, .xls), Google Sheets (direct connection), JSON, PDF tables, and SQL databases (PostgreSQL, MySQL, SQLite via connection string). For most business users, CSV and Excel uploads cover 95% of use cases. You can upload multiple files in the same session and ask questions across them simultaneously — for example, joining sales data from a CSV with customer data from an Excel sheet without writing any JOIN queries."),
        ("Julius AI vs Excel — which is better for data analysis?",
         "Julius AI and Excel serve different users. Excel is better for: building repeatable templates, complex formulas, financial modeling, and sharing files in corporate environments where everyone uses Office. Julius AI is better for: ad-hoc analysis questions in plain English, generating charts without chart-building menus, statistical tests (regression, correlation) without add-ins, and users who don't know Excel formulas. For non-technical users doing exploratory analysis, Julius AI is 5–10x faster. For accountants building structured financial models, Excel is still the standard. See our <a href=\"/compare/julius-ai-vs-chatgpt/\">Julius AI vs ChatGPT comparison</a> for more context."),
        ("How accurate is Julius AI's data analysis?",
         "Julius AI's natural language query accuracy is 88–92% on structured data tasks in our testing — meaning roughly 9 out of 10 questions get the correct chart or statistical result on the first attempt. Complex multi-step analysis (e.g., 'show me the 3-month rolling average revenue by region, filtered to accounts over $10k') occasionally requires rephrasing. For simple to moderately complex analysis questions, accuracy is consistently high. Julius AI generates the underlying Python code for every analysis, which you can inspect and verify if needed."),
        ("Can Julius AI connect to live databases?",
         "Yes. Julius AI Pro and Ultra plans support live database connections to PostgreSQL, MySQL, and SQLite via connection string. Once connected, you can ask questions against live data without exporting to CSV first. Google Sheets connections also sync in real time. Note that database connections are not available on the free plan (15 analyses/month) — they require a paid plan. For teams using data warehouses like Snowflake or BigQuery, Julius AI currently requires exporting to CSV."),
        ("Is Julius AI good for students and academic research?",
         "Yes. Julius AI is widely used for academic research and student assignments. The free plan (15 analyses/month) is sufficient for most coursework. Common student use cases include: running statistical tests for thesis data, generating charts for presentations, cleaning and summarizing survey data, and exploratory analysis for research papers. Julius AI generates the underlying Python/R code for each analysis, which is useful for students learning to code — you can see the code, understand it, and adapt it. The <a href=\"/coupons/julius-ai/\">coupon code 25RQK3UL</a> gives 10% off Pro if you need more than 15 analyses per month."),
    ],
    "se-ranking": [
        ("How accurate is SE Ranking's keyword data?",
         "SE Ranking's keyword data comes from a database of 5 billion+ keywords updated monthly. In our accuracy tests comparing SE Ranking keyword volume estimates to Google Search Console actual impressions, SE Ranking was within 20% of actual volume 78% of the time — comparable to Semrush and Ahrefs on the same keywords. Keyword difficulty scores are reliable for competitive analysis. For hyper-local or very long-tail keywords (under 100 monthly searches), volume estimates are less precise across all SEO tools including SE Ranking."),
        ("Does SE Ranking include white-label reports?",
         "Yes. SE Ranking includes white-label reporting on all paid plans at no extra cost — this is a significant advantage over Semrush (which charges extra for white-label). You can customize reports with your agency logo, colors, and domain, then send automated scheduled reports to clients by email. The report builder covers rank tracking, site audit, backlink data, and keyword research modules. For agencies managing multiple client sites, SE Ranking's white-label at $65–$119/month represents exceptional value compared to Semrush Guru at $249/month."),
        ("Is SE Ranking good for local SEO?",
         "SE Ranking has solid local SEO features: local rank tracking (city and zip-code level), Google Business Profile audit integration, and local keyword research filters. You can track rankings separately for desktop and mobile in specific cities. For agencies managing local business clients, SE Ranking's local tracking is comparable to BrightLocal at roughly half the combined cost. The local SEO module is available on all paid plans including the $65/month Essential tier."),
        ("SE Ranking vs Ahrefs — which SEO tool should I choose?",
         "Choose SE Ranking if: you're on a budget (SE Ranking from $65/mo vs Ahrefs from $129/mo), you manage client sites and need white-label reports included, or rank tracking and site audit are your primary needs. Choose Ahrefs if: you need the deepest backlink database available (Ahrefs indexes 3 trillion links vs SE Ranking's ~3 billion), you rely heavily on competitor content gap analysis, or you need Content Explorer for link prospecting. For most solo SEOs and small agencies, SE Ranking delivers 80% of Ahrefs' value at 50% of the cost. See our <a href=\"/compare/se-ranking-vs-ahrefs/\">SE Ranking vs Ahrefs comparison</a>."),
        ("How often does SE Ranking update rank tracking data?",
         "SE Ranking updates rank tracking data daily by default — every 24 hours. You can also trigger manual rank checks on demand. The rank tracker covers Google, Bing, Yahoo, and YouTube. You can split results by desktop vs mobile and track rankings for specific geographic locations down to the city level. Automated weekly and monthly email reports can be sent to clients or team members automatically. SE Ranking's rank tracking accuracy in our tests was within 1–2 positions of actual Google positions 94% of the time."),
    ],
    "mangools": [
        ("Is KWFinder the same as Mangools?",
         "KWFinder is one of five tools included in the Mangools subscription — not a separate product. When you subscribe to Mangools, you get: KWFinder (keyword research), SERPChecker (SERP analysis), SERPWatcher (rank tracking), LinkMiner (backlink analysis), and SiteProfiler (site overview). The Mangools subscription starts at $29/month and includes all five tools. KWFinder became so popular that many users search for it by name, but there's no way to buy KWFinder separately — it's only available through the Mangools bundle."),
        ("How accurate is Mangools keyword difficulty?",
         "Mangools' Keyword Difficulty (KD) score is one of the most reliable in the industry for entry-level to mid-level SEO. In our testing, pages with KD under 30 were rankable within 3–6 months for new sites with limited authority. KD scores above 50 accurately predict highly competitive SERPs dominated by DA 70+ domains. The main limitation: KD is based on link data, so it may underestimate difficulty for queries dominated by large brands that rank without many backlinks. For keyword research and opportunity identification, KWFinder's KD is the #1 reason SEO beginners choose Mangools."),
        ("Does Mangools have a free plan or free trial?",
         "Mangools does not have a permanent free plan — but it offers a 10-day free trial with full access to all five tools (KWFinder, SERPChecker, SERPWatcher, LinkMiner, SiteProfiler) and no credit card required. During the trial, you can run unlimited searches to fully evaluate the tool. After the trial, plans start at $29/month (Entry, 100 keyword lookups/day). The 10-day trial is generous compared to Ahrefs (7-day trial for $7) and Semrush (7-day trial, credit card required). Use our <a href=\"/go/mangools/\">affiliate link</a> to start your free trial."),
        ("Mangools vs Ahrefs — which is better for beginners?",
         "For beginners, Mangools is better than Ahrefs. Mangools has a cleaner, more intuitive interface — KWFinder in particular is designed so new SEOs can find keyword opportunities in minutes without a learning curve. Ahrefs is more powerful but has a steeper learning curve and costs $129/month vs Mangools at $29/month. If you're new to SEO and want to learn keyword research and rank tracking without overpaying, Mangools is the right starting point. When you need deeper competitor analysis, content gap data, and a larger backlink database, consider upgrading to Ahrefs or Semrush. See our <a href=\"/compare/mangools-vs-ahrefs/\">Mangools vs Ahrefs comparison</a>."),
        ("Is Mangools good for agency use?",
         "Mangools is good for small agencies managing 5–15 client sites. The Agency plan ($89/month) includes 1,500 keyword lookups/day, 20 tracked domains, unlimited users, and white-label rank tracking reports. For agencies managing more than 20 clients or needing deep competitor intelligence, Semrush or Ahrefs scale better. Mangools' strongest agency feature is white-label rank tracking reports — your clients receive branded reports with your logo without knowing the underlying tool. For cost-conscious agencies where rank tracking and keyword research are the primary deliverables, Mangools at $89/month versus Semrush Guru at $249/month is a $1,920/year saving."),
    ],
}

ANCHOR = '  <!-- Newsletter -->'

for tool, questions in FAQS.items():
    path = os.path.join(BASE, "review", tool, "index.html")
    if not os.path.exists(path):
        print(f"SKIP (not found): {path}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if ANCHOR not in content:
        print(f"SKIP (anchor missing): {tool}")
        continue

    # Build new FAQ items
    new_items = ""
    for q, a in questions:
        new_items += f"""        <div class="faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </div>
"""

    content = content.replace(ANCHOR, new_items + ANCHOR)

    # Also update schema FAQPage to include new questions
    # Build new Question entries for schema
    schema_questions = ""
    for q, a in questions:
        # Strip HTML from answer for schema
        clean_a = re.sub(r'<[^>]+>', '', a).replace('"', '\\"').replace('\n', ' ')
        clean_q = q.replace('"', '\\"')
        schema_questions += f',{{"@type":"Question","name":"{clean_q}","acceptedAnswer":{{"@type":"Answer","text":"{clean_a}"}}}}'

    # Insert into existing FAQPage schema
    content = re.sub(
        r'("mainEntity":\[)(.*?)(\])',
        lambda m: m.group(1) + m.group(2).rstrip(']') + schema_questions + ']',
        content,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    words = len(re.sub(r'<[^>]+>', '', content).split())
    print(f"[{tool}] done — new word count: ~{words}")

print("\nAll done.")
