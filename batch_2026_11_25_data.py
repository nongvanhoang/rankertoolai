"""Review + /go/ page data for Content Harmony, Ranked AI, GoEnhance AI and Answrr (2026-11-25). Rendered by generate_batch_2026_11_25.py.
Facts fetched 2026-11-25 from contentharmony.com/pricing, ranked.ai/pricing, goenhance.ai/pricing, tryanswrr.com/pricing + /features + /terms.
Research-based, not hands-on lab tests: each verdict says so.
Affiliate rules (read 25/11/2026):
- Content Harmony (Rewardful, #via=): 20% lifetime, 60-day cookie, PayPal, $50 min. Paid ads OK, NO branded keywords. The # fragment must stay.
- Ranked AI (Dub): 20% lifetime. Ad rules not published -> no Ads until asked.
- GoEnhance (Tolt): 10% x 12 months. NO Google/Bing ads, NO PPC, NO coupon/deal sites -> do not list its sales on deal pages.
- Answrr: 30% lifetime, Tremendous. NO bidding on Answrr/AIQ Labs trademarks. Referral redirect sets no cookie (25/11) -> confirm clicks in dashboard."""


def _hero(name, url, what):
    return ("Based on <a href=\"%s\" target=\"_blank\">%s</a>'s published pricing and feature list, here's an honest, research-based look at whether %s. "
            "This is not a hands-on lab test &mdash; it's an independent breakdown of pricing, limits and fit." % (url, name, what))


def _note(slug, name, text):
    return text + " Check <a href=\"/go/%s/\" rel=\"nofollow sponsored\" target=\"_blank\">%s's current pricing</a> before you subscribe." % (slug, name)


_D = {"updated": "November 2026", "date_iso": "2026-11-25", "date_human": "November 25, 2026"}

REVIEWS = [
dict(_D, **{
    "slug": "content-harmony", "name": "Content Harmony", "domain": "contentharmony.com",
    "go_dest": "https://www.contentharmony.com/#via=rankertoolai-com",
    "category_badge": "Content Briefs &amp; SEO", "category_slug": "ai-seo",
    "title": "Content Harmony Review 2026: Pricing, Briefs & Content Grader",
    "meta_desc": "Content Harmony review 2026: keyword reports, content briefs and a content grader in one workflow. Plans from $50/mo, unlimited users, and a $10 trial with 10 workflow credits.",
    "h1": "Content Harmony Review 2026: Is It Worth Paying for Better Content Briefs?",
    "hero_sub": _hero("Content Harmony", "https://www.contentharmony.com", "this content brief platform fits your editorial process"),
    "score": "8.2",
    "price_note": "$10 trial (10 workflows, no time limit, no auto-renewal) &middot; from $50/mo for 5 workflows &middot; $99/mo for 12 &middot; $199/mo for 25 &middot; Enterprise from $1,000/mo",
    "price_short": "$50 &ndash; $799/mo",
    "verdict": "Content Harmony is built around one job: turning a keyword into a brief a writer can use. Each Content Workflow includes a keyword report (search intent, overlapping keywords and entities, competitor structure, questions and sources), a shareable content brief, and a content grader that scores a draft against a topic model. Pricing depends only on how many workflows you need each month. The smallest plan is $50 a month for 5 workflows (about $42 billed annually), then $99 for 12, $199 for 25, $299 for 50, $599 for 100 and $799 for 150, with Enterprise from $1,000 a month. Every plan includes unlimited users, unlimited projects and free team training, and monthly credits stay valid for 90 days. The trial is unusual: you pay $10 for 10 workflows, there is no time limit and it does not renew automatically. The trade-offs: cost per workflow is high if you publish a lot of short pages (about $8 to $10 each on the small plans), there is no free plan, and it is a research and briefing tool rather than a full rank tracker or backlink suite. It suits agencies and in-house teams that brief freelance writers. Solo bloggers who mostly want a content score may find a cheaper optimizer enough. This verdict is built from Content Harmony's published pages &mdash; RankerToolAI has not run a hands-on lab test of Content Harmony.",
    "scores_table": [
        ("Brief Quality", "Intent, questions, outlines and sources in one brief", 8.8),
        ("Team Use", "Unlimited users and projects on every plan", 9.0),
        ("Trial Terms", "$10, no time limit, no auto-renewal", 8.5),
        ("Value for Money", "About $5 to $10 per workflow", 7.5),
        ("Scope", "Briefs and grading, not a full SEO suite", 7.2),
    ],
    "pros": ["Keyword report, brief and grader included in every workflow", "Unlimited users and projects on every plan",
             "Monthly credits stay valid for 90 days", "$10 trial has no time limit and does not auto-renew",
             "Shareable briefs for clients, freelancers and editors"],
    "cons": ["No free plan", "Around $8 to $10 per workflow on the smaller plans",
             "Not a backlink or site audit suite", "Early API access is listed only for Enterprise"],
    "features": [
        ("Keyword Reports", "Search intent, related keywords and entities, competitor structure and reader questions in one report."),
        ("Content Briefs", "Standardized briefs you can outline, edit and share with writers, clients and designers."),
        ("Content Grader", "Scores drafts and existing pages against a topic model so you can spot gaps."),
        ("Search Intent Analysis", "Classifies intent so the format of your page matches what searchers want."),
        ("Unlimited Seats", "Invite the whole team and as many projects as you need on any plan."),
        ("Rollover Credits", "Monthly credits last 90 days; annual plans get the full year's credits upfront."),
    ],
    "pricing_rows": [
        ("Trial", "$10 once", "10 workflow credits &middot; no time limit &middot; no automatic billing", False),
        ("Standard 5", "$50/mo", "About $42/mo billed annually &middot; 5 workflows a month", False),
        ("Standard 12", "$99/mo", "About $89/mo billed annually &middot; 12 workflows a month", True),
        ("Standard 25", "$199/mo", "About $179/mo billed annually &middot; 25 workflows a month", False),
        ("Standard 50 to 150", "$299 &ndash; $799/mo", "50, 100 or 150 workflows a month", False),
        ("Enterprise", "from $1,000/mo", "200+ workflows &middot; procurement support &middot; early API access", False),
    ],
    "pricing_note": _note("content-harmony", "Content Harmony", "Prices were read from the vendor's pricing page on November 25, 2026."),
    "alternatives": [
        ("Content optimizers (e.g. Surfer SEO)", "Stronger on live editing and content scoring; briefs are one part of a wider toolkit."),
        ("AI-first brief tools (e.g. Frase)", "Combine briefs with AI writing in one editor."),
    ],
    "faq": [
        ("How much does Content Harmony cost?", "Plans start at $50/mo for 5 content workflows, then $99/mo for 12, $199/mo for 25 and up to $799/mo for 150. Enterprise starts from $1,000/mo."),
        ("Does Content Harmony have a free trial?", "It has a paid trial: $10 for your first 10 workflow credits, with no time limit and no automatic billing afterwards."),
        ("What is a Content Workflow?", "One workflow covers one page of content and includes a keyword report, a content brief and a content grader."),
        ("Do Content Harmony credits expire?", "Monthly plan credits are valid for 90 days. Annual plans receive the full year's credits upfront."),
        ("How many users can I add?", "Every plan includes unlimited users and unlimited projects."),
    ],
    "related_review": ("/review/surfer-seo/", "Surfer SEO Review"),
    "related_best": ("/best/geo-tools/", "Best GEO Tools"),
    "footer_category": "More AI SEO Resources",
}),
dict(_D, **{
    "slug": "ranked-ai", "name": "Ranked AI", "domain": "ranked.ai",
    "go_dest": "https://try.ranked.ai/ranker-tool-ai",
    "category_badge": "Managed SEO Service", "category_slug": "ai-seo",
    "title": "Ranked AI Review 2026: Managed SEO Pricing, Plans & Limits",
    "meta_desc": "Ranked AI review 2026: done-for-you SEO with articles, backlinks, on-page fixes and AI visibility tracking. Standard $99/mo, Plus $198/mo, Enterprise $349/mo, 7-day free trial.",
    "h1": "Ranked AI Review 2026: Can a $99 Managed SEO Plan Really Deliver?",
    "hero_sub": _hero("Ranked AI", "https://www.ranked.ai", "this done-for-you SEO service fits your business"),
    "score": "7.8",
    "price_note": "7-day free trial &middot; Standard $99/mo &middot; Plus $198/mo &middot; Enterprise $349/mo &middot; 20% less billed yearly &middot; priced per website",
    "price_short": "$99 &ndash; $349/mo",
    "verdict": "Ranked AI sits between an SEO tool and an SEO agency. You pay a flat monthly price per website, and its team writes and publishes articles, makes on-page and technical fixes, builds links and reports progress in a dashboard you can watch. Standard is $99 a month for 25 focus keywords, one article a week and about 4 backlinks a month. Plus is $198 for 50 focus keywords, two articles a week and about 8 backlinks, and Enterprise is $349 for 100 focus keywords, four articles a week, about 16 backlinks and a dedicated account executive. Yearly billing is 20% cheaper. All plans list unlimited tracked keywords and AI prompts, unlimited team members, white-label reports, daily rank tracking and AI visibility tracking across ChatGPT, Claude, Gemini, Perplexity, Grok and Meta. There is a 7-day free trial and you can cancel any time. Be realistic about what this price buys: one article a week and a handful of links is a modest programme, it will not fix a weak offer, and no service can guarantee rankings. Ask for examples of links and articles before you commit, and keep approval of anything published on your site. Trustpilot showed a 4.7 rating from 229 reviews when we checked on November 25, 2026, while some forum posters have questioned those reviews, so use the trial to judge for yourself. This verdict is built from published pages &mdash; RankerToolAI has not run a hands-on lab test of Ranked AI.",
    "scores_table": [
        ("Hands-Off Delivery", "Content, links and fixes done for you", 8.5),
        ("Included Software", "Rank and AI visibility tracking on every plan", 8.5),
        ("Contract Terms", "Month to month with a 7-day trial", 8.5),
        ("Output Volume", "One article a week on Standard", 7.2),
        ("Independent Proof", "Check sample work before committing", 6.8),
    ],
    "pros": ["Content, links, on-page fixes and publishing are handled for you", "Month to month, with a 7-day free trial",
             "Unlimited tracked keywords and AI prompts on every plan", "White-label dashboard and reports on every plan",
             "AI visibility tracking across six assistants"],
    "cons": ["Priced per website", "Standard includes only one article and about one backlink a week",
             "Dedicated account executive only on Enterprise", "Rankings cannot be guaranteed by any service",
             "You need to review what is published in your name"],
    "features": [
        ("Articles &amp; Web Copy", "One, two or four blog articles a week depending on plan, plus unlimited web copy pages."),
        ("Backlink Outreach", "About 4, 8 or 16 backlinks a month, described by the vendor as white-hat outreach."),
        ("On-Page &amp; Technical", "On-page optimization, schema and Core Web Vitals fixes, implemented for you."),
        ("AI Visibility Tracking", "Prompt tracking across ChatGPT, Claude, Gemini, Perplexity, Grok and Meta."),
        ("Rank Tracking &amp; Audits", "Daily tracking on desktop, mobile, Maps and AI Mode, plus audits and heatmaps."),
        ("White Label", "Your logo on the dashboard, client portal and reports for agencies."),
    ],
    "pricing_rows": [
        ("Standard", "$99/mo", "25 focus keywords &middot; 1 article a week &middot; about 4 backlinks a month", True),
        ("Plus", "$198/mo", "50 focus keywords &middot; 2 articles a week &middot; about 8 backlinks a month", False),
        ("Enterprise", "$349/mo", "100 focus keywords &middot; 4 articles a week &middot; about 16 backlinks a month &middot; account executive", False),
    ],
    "pricing_note": _note("ranked-ai", "Ranked AI", "AI SEO plans shown, per website, billed monthly; yearly billing is 20% less. Google Ads and ChatGPT Ads management have their own plans."),
    "alternatives": [
        ("Self-serve SEO suites (e.g. SE Ranking)", "You keep full control and do the work yourself with rank tracking, audits and research tools."),
        ("Specialist agencies", "Usually higher monthly fees, with more senior strategy time and custom scope."),
    ],
    "faq": [
        ("How much does Ranked AI cost?", "AI SEO plans are $99/mo (Standard), $198/mo (Plus) and $349/mo (Enterprise) per website. Yearly billing is 20% less."),
        ("Does Ranked AI have a free trial?", "Yes, its pricing page lists a 7-day free trial and month-to-month plans with no contract."),
        ("Is Ranked AI software or a service?", "Both. Its team does the SEO work and the tracking and reporting software is included in the plan."),
        ("How many articles and backlinks do I get?", "Standard lists one article a week and about 4 backlinks a month; Plus doubles that, and Enterprise lists four articles a week and about 16 backlinks."),
        ("Can agencies white-label Ranked AI?", "Yes. White-label dashboards and reports are listed on every plan."),
    ],
    "related_review": ("/review/se-ranking/", "SE Ranking Review"),
    "related_best": ("/best/geo-tools/", "Best GEO Tools"),
    "footer_category": "More AI SEO Resources",
}),
dict(_D, **{
    "slug": "goenhance", "name": "GoEnhance AI", "domain": "goenhance.ai",
    "go_dest": "https://www.goenhance.ai/?aff=rankertoolai-com",
    "category_badge": "AI Video Generator", "category_slug": "ai-video",
    "title": "GoEnhance AI Review 2026: Pricing, Tokens & Video Models",
    "meta_desc": "GoEnhance AI review 2026: text, image and video-to-video generation with many AI models in one place. Free tokens, Basic $9.99/mo, Standard $24.99/mo, Pro $49.99/mo, Mega $99.99/mo.",
    "h1": "GoEnhance AI Review 2026: Many AI Video Models Under One Subscription?",
    "hero_sub": _hero("GoEnhance AI", "https://www.goenhance.ai", "this multi-model AI video platform fits your projects"),
    "score": "7.9",
    "price_note": "Free tokens to try &middot; Basic $9.99/mo &middot; Standard $24.99/mo &middot; Pro $49.99/mo &middot; Mega $99.99/mo &middot; lower prices billed yearly",
    "price_short": "$0 &ndash; $99.99/mo",
    "verdict": "GoEnhance AI puts a long list of video and image models behind one login: its model list includes Veo 3.1, Kling 3.0, Sora 2, Seedance, Wan and Runway for video, plus image models such as Nano Banana Pro and FLUX.2. Around that sit video-to-video style transfer for turning footage into animation, character animation, lip sync, talking avatars, upscaling and a library of effects. You spend tokens. Basic is $9.99 a month for 600 tokens, Standard $24.99 for 1,600, Pro $49.99 for 3,500 and Mega $99.99 for 8,000, and yearly billing is cheaper. One-time packs of 500 tokens cost $10 and do not expire. Read the limits carefully. Basic is for personal use only, so anyone making client or monetized content needs Standard or higher for the commercial license. Video-to-video clips max out at 20 seconds on Standard and 60 seconds on Pro and Mega. Unlimited relaxed-mode generation covers only certain models and the list changes over time. Most important, GoEnhance says it does not offer refunds, so use the free tokens first. Only use faces, voices and footage you have permission to use. For creators who want to try several models without several subscriptions, Standard is a sensible start. This verdict is built from GoEnhance's published pages &mdash; RankerToolAI has not run a hands-on lab test of GoEnhance.",
    "scores_table": [
        ("Model Choice", "Many video and image models in one login", 9.0),
        ("Video-to-Video", "Style transfer and animation tools", 8.3),
        ("Entry Price", "Basic at $9.99 a month", 8.0),
        ("License Clarity", "Commercial use starts at Standard", 7.5),
        ("Refund Terms", "No refunds offered", 5.5),
    ],
    "pros": ["Wide choice of video and image models in one account", "Free tokens to try before paying",
             "No watermark and private generation on paid plans", "One-time token packs do not expire",
             "Video-to-video, lip sync, avatars and upscaling included"],
    "cons": ["No refunds", "Basic plan is limited to personal use", "Token costs make monthly output hard to predict",
             "Unlimited models vary by plan and over time", "Video-to-video is capped at 20 seconds on Standard"],
    "features": [
        ("Text &amp; Image to Video", "Generate clips with models including Veo 3.1, Kling 3.0, Sora 2, Seedance and Wan."),
        ("Video to Video", "Restyle existing footage as animation or another look; up to 20 or 60 seconds by plan."),
        ("Character Animation", "Animate a character or keep one consistent across clips."),
        ("Lip Sync &amp; Avatars", "Sync lips to audio or turn a photo into a talking avatar."),
        ("Image Generation", "Text-to-image, editing and upscaling with several image models."),
        ("Upscaling", "Enhance images and videos; the vendor lists output up to 4K and 60fps."),
    ],
    "pricing_rows": [
        ("Free", "$0", "A small amount of tokens to try the tools &middot; personal use", False),
        ("Basic", "$9.99/mo", "600 tokens &middot; no watermark &middot; personal use only", False),
        ("Standard", "$24.99/mo", "1,600 tokens &middot; commercial license &middot; video-to-video up to 20 seconds", True),
        ("Pro", "$49.99/mo", "3,500 tokens &middot; 6 fast jobs at once &middot; video-to-video up to 60 seconds", False),
        ("Mega", "$99.99/mo", "8,000 tokens &middot; 12 fast jobs at once &middot; video-to-video up to 60 seconds", False),
    ],
    "pricing_note": _note("goenhance", "GoEnhance AI", "Regular monthly prices shown; yearly billing is cheaper. Extra packs of 500 tokens are $10."),
    "alternatives": [
        ("Article-to-video tools (e.g. Pictory)", "Better for turning scripts and blog posts into finished videos with voiceover."),
        ("Social video generators (e.g. Zebracat)", "Aimed at faceless social clips with captions and publishing."),
    ],
    "faq": [
        ("Is GoEnhance AI free?", "It gives new accounts a small amount of free tokens. Paid plans start at $9.99/mo."),
        ("How much does GoEnhance AI cost?", "Basic is $9.99, Standard $24.99, Pro $49.99 and Mega $99.99 a month. Yearly billing is cheaper."),
        ("Can I use GoEnhance videos commercially?", "Commercial use is allowed on Standard, Pro and Mega. Free and Basic are for personal use only."),
        ("Does GoEnhance AI offer refunds?", "No. Its refund policy says it cannot offer refunds because of GPU costs, so try the free tokens first."),
        ("Which AI models does GoEnhance include?", "Its list includes Veo 3.1, Kling 3.0, Sora 2, Seedance, Wan, Runway and several image models. Availability can change."),
    ],
    "related_review": ("/review/zebracat/", "Zebracat Review"),
    "related_best": ("/best/ai-video-tools/", "Best AI Video Tools"),
    "footer_category": "More AI Video Resources",
}),
dict(_D, **{
    "slug": "answrr", "name": "Answrr", "domain": "tryanswrr.com",
    "go_dest": "https://tryanswrr.com/ref/6dc9c864",
    "category_badge": "AI Receptionist", "category_slug": "ai-voice",
    "title": "Answrr Review 2026: AI Receptionist Pricing & Minutes",
    "meta_desc": "Answrr review 2026: AI receptionist that answers calls 24/7, books appointments and sends summaries. Solo $49/mo (250 min), Growth $99/mo (700 min), Pro $199/mo, 14-day free trial.",
    "h1": "Answrr Review 2026: Is This AI Receptionist Right for a Small Business?",
    "hero_sub": _hero("Answrr", "https://tryanswrr.com", "this AI phone receptionist fits your business"),
    "score": "8.0",
    "price_note": "14-day free trial &middot; Solo $49/mo (250 min) &middot; Growth $99/mo (700 min) &middot; Pro $199/mo (1,600 min) &middot; agency plans from $247/mo",
    "price_short": "$49 &ndash; $497/mo",
    "verdict": "Answrr is an AI receptionist for small businesses that miss calls. It answers day and night, replies from your own price list and documents, books appointments through a connected scheduler, transfers callers to the right person, and sends a summary, transcript and recording afterwards. Pricing is simple: every plan includes every feature and a free setup call, and you pay for minutes. Solo is $49 a month for 250 minutes and up to 3 receptionists, Growth is $99 for 700 minutes and up to 10, and Pro is $199 for 1,600 minutes and up to 25. Top-ups cost $0.25, $0.20 and $0.15 a minute. Agencies can resell it from $247 a month for 2,000 pooled minutes, or take the White-Label plan at $497 for 6,000. The trade-offs: the vendor's terms say unused minutes do not roll over and subscription fees are non-refundable, booking relies on connecting a scheduler through MCP or an API, and the AI can still misunderstand callers, so keep a human transfer option. You are responsible for telling callers they are speaking with AI and for call recording consent where the law requires it. Start with the trial, forward only after-hours calls, and read the transcripts for a week. This verdict is built from Answrr's published pages &mdash; RankerToolAI has not run a hands-on lab test of Answrr.",
    "scores_table": [
        ("Pricing Clarity", "Every feature on every plan", 9.0),
        ("Setup Help", "Free setup call included", 8.5),
        ("Call Handling", "Booking, transfers, summaries and recordings", 8.3),
        ("Value for Money", "About $0.12 to $0.20 per included minute", 7.8),
        ("Flexibility of Terms", "No rollover and non-refundable fees", 6.5),
    ],
    "pros": ["Every feature included from the $49 plan", "Free setup call on every plan",
             "Answers from your own documents and price list", "Summary, transcript and recording after each call",
             "White-label plans for agencies"],
    "cons": ["Unused minutes do not roll over", "Subscription fees are non-refundable under its terms",
             "Booking needs a scheduler connected by MCP or API", "AI can misunderstand callers; keep human transfer on",
             "Recording consent and AI disclosure are your responsibility"],
    "features": [
        ("24/7 Answering", "Picks up every call with a voice and greeting you choose."),
        ("Knowledge Base", "Upload PDFs, documents or your site so answers come from your information."),
        ("Appointment Booking", "Checks availability and books during the call through a connected scheduler."),
        ("Smart Transfers", "Routes callers to sales, support or a manager with context."),
        ("Summaries &amp; Transcripts", "Summary, sentiment, transcript and recording by dashboard, email or webhook."),
        ("Agency Portals", "Client portals on your domain, pooled minutes and templates on agency plans."),
    ],
    "pricing_rows": [
        ("Solo", "$49/mo", "250 minutes &middot; 3 receptionists &middot; top-ups $0.25/min", True),
        ("Growth", "$99/mo", "700 minutes &middot; 10 receptionists &middot; top-ups $0.20/min", False),
        ("Pro", "$199/mo", "1,600 minutes &middot; 25 receptionists &middot; top-ups $0.15/min", False),
        ("Agency Reseller", "$247/mo", "2,000 pooled minutes &middot; 100 receptionists &middot; top-ups $0.10/min", False),
        ("Agency White-Label", "$497/mo", "6,000 pooled minutes &middot; 100 receptionists &middot; top-ups $0.08/min", False),
    ],
    "pricing_note": _note("answrr", "Answrr", "Every plan includes a free setup call. The pricing page lists a 14-day free trial."),
    "alternatives": [
        ("Other AI voice agents (e.g. Macaws)", "Compare voices, minute rates and integrations for your type of calls."),
        ("Human answering services", "Better for sensitive or complex calls, usually at a higher price per minute."),
    ],
    "faq": [
        ("How much does Answrr cost?", "Solo is $49/mo for 250 minutes, Growth $99/mo for 700 and Pro $199/mo for 1,600. Agency plans start at $247/mo."),
        ("Does Answrr have a free trial?", "Yes, the pricing page lists a 14-day free trial."),
        ("Can I keep my phone number?", "Yes. You can forward your existing business line to Answrr or use a new number."),
        ("Do unused minutes roll over?", "No. Answrr's terms say unused minutes or credits do not roll over."),
        ("Can Answrr book appointments?", "Yes, when your scheduler is connected through MCP or an API it can check availability and book during the call."),
    ],
    "related_review": ("/review/macaws/", "Macaws Review"),
    "related_best": ("/category/ai-voice/", "AI Voice Tools"),
    "footer_category": "More AI Voice Resources",
}),
]


def _go(i, title, heading, sub, num, label, note, colors, benefits, cta, best, cat):
    r = REVIEWS[i]
    bg, card, border, a1, a2, cls = colors
    return {"slug": r["slug"], "name": r["name"], "dest": r["go_dest"],
            "title": "%s — %s — Redirecting | RankerToolAI" % (r["name"], title),
            "heading": heading, "sub": sub, "badge_num": num, "badge_label": label, "badge_note": note,
            "color_bg": bg, "color_card": card, "color_border": border, "color_accent": a1, "color_accent2": a2, "badge_class": cls,
            "benefits": benefits, "cta_text": cta, "countdown_note": "Redirecting to " + r["name"],
            "footer_links": [("/review/%s/" % r["slug"], "Full %s review" % r["name"]), best], "tool_category": cat}


_BLUE = ("#0a0f1a", "#111a2c", "#22324f", "#38bdf8", "#0ea5e9", "blue")
_GREEN = ("#0b1214", "#122024", "#203a40", "#2dd4bf", "#14b8a6", "green")
_PINK = ("#100a14", "#1c1224", "#35213f", "#ff5ca8", "#e83d8c", "green")

GO_PAGES = [
    _go(0, "$10 Trial", "Build better content briefs &mdash; 10 workflows for $10", "Keyword report, content brief and content grader in one workflow, with unlimited users.",
        "$10", "Trial", "10 workflows, no auto-renewal", _BLUE,
        [("🔎", "Keyword report", "Intent &amp; entities"), ("📑", "Content brief", "Shareable"), ("✅", "Content grader", "Find gaps"), ("👥", "Unlimited users", "Every plan")],
        "Try Content Harmony &rarr;", ("/best/geo-tools/", "Best GEO tools"), "Content SEO"),
    _go(1, "7-Day Free Trial", "Managed SEO from $99 a month &mdash; try Ranked AI", "Articles, backlinks, on-page fixes and AI visibility tracking handled by its team.",
        "7", "Day Free Trial", "Month to month", _GREEN,
        [("📝", "Articles", "1 to 4 a week"), ("🔗", "Backlinks", "Outreach included"), ("🤖", "AI visibility", "6 assistants"), ("🏷️", "White label", "Every plan")],
        "Start Ranked AI Trial &rarr;", ("/best/geo-tools/", "Best GEO tools"), "Managed SEO"),
    _go(2, "Free Tokens", "Many AI video models in one place &mdash; try GoEnhance", "Text, image and video-to-video generation, lip sync, avatars and upscaling.",
        "Free", "Tokens to Try", "Paid plans from $9.99/mo", _PINK,
        [("🎬", "Video models", "Veo, Kling, Sora"), ("🎨", "Video to video", "Restyle clips"), ("🗣️", "Lip sync", "&amp; avatars"), ("🔼", "Upscale", "Images &amp; video")],
        "Try GoEnhance Free &rarr;", ("/best/ai-video-tools/", "Best AI video tools"), "AI Video"),
    _go(3, "14-Day Free Trial", "Never miss a call &mdash; try the Answrr AI receptionist", "Answers 24/7, books appointments and sends a summary of every call.",
        "14", "Day Free Trial", "Plans from $49/mo", _BLUE,
        [("📞", "24/7", "Every call"), ("📅", "Booking", "During the call"), ("🧾", "Summaries", "&amp; transcripts"), ("🛠️", "Setup call", "Included free")],
        "Try Answrr &rarr;", ("/category/ai-voice/", "AI voice tools"), "AI Receptionist"),
]
