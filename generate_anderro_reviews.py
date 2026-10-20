#!/usr/bin/env python3
"""Generate review pages for the 4 new Anderro-marketplace tools (climbX, PostSnag,
ViralityAI, SkySnail), matching the existing full review template style
(see review/getresponse/index.html for the reference this was modeled on).
Writes to both clones (root + html/) since they're two git clones of the same repo.
"""
import os

BASE = os.path.dirname(__file__)
OUT_ROOTS = [BASE, os.path.join(BASE, "html")]

TOOLS = [
  {
    "slug": "climbx",
    "name": "ClimbX",
    "domain": "climbx.so",
    "go_dest": "https://climbx.so?ref=hongnngvnw7xhnai",
    "category_badge": "AI Marketing",
    "category_slug": "ai-marketing",
    "title": "ClimbX Review 2026: Is This AI X (Twitter) Growth Tool Worth It?",
    "meta_desc": "ClimbX review 2026: AI co-writing, voice learning, and scheduling for growing on X/Twitter. Independent breakdown of the $29/mo founding rate, features, and who it's actually for.",
    "h1": "ClimbX Review 2026: Is This AI X (Twitter) Growth Tool Worth It?",
    "hero_sub": "Based on ClimbX's published feature set and pricing, here's an honest, research-based look at whether its AI co-writing and voice-learning tools are worth it for growing on X. This is not a hands-on lab test — it's an independent breakdown of pricing, features, and fit.",
    "score": "7.6",
    "price_note": "From $29/mo (founding rate, limited spots)",
    "price_short": "~$29/mo",
    "updated": "September 2026",
    "date_iso": "2026-09-16",
    "date_human": "September 16, 2026",
    "verdict": "ClimbX targets a specific, real problem for X creators: staying consistent without sounding like a bot. Its Voice Learning feature (trained on your last 100 posts) and an Inspiration Engine that surfaces proven angles from your niche are the two features that actually differentiate it from a generic AI writing tool pointed at X. The founding-rate pricing ($29/mo, locked for life, limited to the first 100 members) makes it a reasonable bet for an early adopter, but the regular $39/mo rate is a fair chunk for a single-platform tool, and the 10 posts/day cap will matter to very high-frequency posters. This verdict is built from ClimbX's own published pricing and feature pages — RankerToolAI has not run a hands-on lab test of ClimbX.",
    "scores_table": [
      ("AI Capability", "Voice learning &amp; co-writing quality", 7.5),
      ("Feature Depth", "Inspiration, Studio, Engage, Analytics", 7.5),
      ("Value for Money", "Founding rate vs. regular $39/mo", 8.0),
      ("Ease of Use", "One-platform focus, guided setup", 8.0),
      ("Scalability", "Multi-account (3), API/MCP access", 7.0),
    ],
    "pros": [
      "Voice Learning trains on your actual last 100 posts, not a generic tone preset",
      "Inspiration Engine surfaces proven angles from your specific niche, not just trending topics globally",
      "Founding rate ($29/mo, locked for life) is genuinely cheaper than most niche AI social tools",
      "API &amp; MCP access for developers who want to build on top of it",
      "7-day free trial, $0 charged during trial, cancel anytime with one click",
    ],
    "cons": [
      "Founding rate is limited to the first 100 members — most new signups will land on $39/mo",
      "10 posts/day cap could constrain very high-frequency accounts",
      "Single-platform (X only) — no built-in cross-posting to other networks",
      "Credit card required to start the free trial, even though $0 is charged upfront",
    ],
    "features": [
      ("Inspiration Engine", "Surfaces proven topics and angles from your specific niche rather than generic trending-topic lists, aiming to shortcut the \"what do I even post about\" problem."),
      ("AI Co-Writer (Studio)", "Generates multiple draft variations in your voice for you to review and edit, rather than a single auto-post — you stay the final editor."),
      ("Voice Learning", "Analyzes your last 100 posts to match your existing tone, vocabulary, and post format, which is the feature most likely to matter for anyone worried AI-assisted posts will sound off-brand."),
      ("Engage Feed", "A curated queue of relevant conversations in your niche worth joining, aimed at the reply/engagement side of growth, not just original posting."),
      ("Scheduling &amp; Analytics", "Approve and schedule posts for optimal timing, with daily AI analysis and impression predictions to gauge what's working."),
      ("Multi-Account &amp; API/MCP Access", "Connect up to 3 X accounts on one plan, plus API and MCP access for developers who want to integrate ClimbX into their own workflow."),
    ],
    "pricing_rows": [
      ("Founding Rate", "$29/mo", "Locked for life &middot; first 100 members only", True),
      ("Regular Price", "$39/mo", "Applies once founding spots are gone", False),
    ],
    "pricing_note": "All tiers include 10 posts/day, scheduling, analytics, and API access — ClimbX doesn't feature-gate by price, it prices on the founding-vs-regular timing instead. Check <a href=\"/go/climbx/\" rel=\"nofollow sponsored\" target=\"_blank\">ClimbX's current pricing</a> for real-time spot availability.",
    "alternatives": [
      ("Typefully", "A popular X scheduling/writing tool with a more established user base, though without ClimbX's specific voice-learning-from-history approach."),
      ("Hypefury", "Broader X growth-automation feature set (evergreen recycling, auto-DMs), at a generally higher price point."),
      ("Jasper", "A general-purpose AI writing tool that can be prompted for X posts, but without ClimbX's built-in scheduling, analytics, or niche-specific inspiration engine — see our <a href=\"/review/jasper/\">Jasper review</a>."),
    ],
    "faq": [
      ("Is ClimbX worth it?", "For a creator who wants to post consistently on X without sounding generic, ClimbX's Voice Learning and Inspiration Engine solve a real problem. The founding rate ($29/mo, locked for life) makes it a reasonable bet while spots remain; at the regular $39/mo it's a fair price for a single-platform tool, worth it mainly for creators treating X as a primary growth channel."),
      ("Does ClimbX have a free plan?", "No permanent free plan — ClimbX offers a 7-day free trial with $0 charged upfront (card required to start), and you can cancel anytime with one click before being billed."),
      ("How many posts can I schedule with ClimbX?", "Every tier includes up to 10 posts/day, scheduling, analytics, and full API access — ClimbX doesn't restrict features by plan, only by founding-vs-regular pricing timing."),
      ("Does ClimbX support multiple X accounts?", "Yes, up to 3 X accounts can be connected on a single ClimbX plan, which suits agencies or creators managing more than one brand."),
      ("What are the best ClimbX alternatives?", "Typefully and Hypefury are the closest direct alternatives for X-specific scheduling and growth tools; Jasper is a broader AI writer that can be adapted for X but lacks ClimbX's voice-learning and niche-inspiration features."),
    ],
    "related_review": ("/review/jasper/", "Jasper Review"),
    "related_best": ("/best/ai-marketing-tools/", "Best AI Marketing Tools"),
    "footer_category": "More AI Marketing Resources",
  },
  {
    "slug": "postsnag",
    "name": "PostSnag",
    "domain": "postsnag.com",
    "go_dest": "https://postsnag.com?ref=hongnngvnwdd5b8m",
    "category_badge": "AI Marketing",
    "category_slug": "ai-marketing",
    "title": "PostSnag Review 2026: Is This Facebook Swipe File Tool Worth It?",
    "meta_desc": "PostSnag review 2026: a Chrome extension for capturing and organizing high-performing Facebook posts into a searchable swipe file. Independent breakdown of pricing, features, and who it's for.",
    "h1": "PostSnag Review 2026: Is This Facebook Swipe File Tool Worth It?",
    "hero_sub": "Based on PostSnag's published feature set and pricing, here's an honest, research-based look at whether this Facebook content-research extension is worth it. This is not a hands-on lab test — it's an independent breakdown of pricing, features, and fit for marketers and agencies.",
    "score": "7.3",
    "price_note": "Free plan available &middot; Pro from $19/mo &middot; Lifetime $139",
    "price_short": "Free &ndash; $19/mo",
    "updated": "September 2026",
    "date_iso": "2026-09-16",
    "date_human": "September 16, 2026",
    "verdict": "PostSnag solves a narrow but real problem: Facebook doesn't give marketers a good native way to save and organize posts they want to learn from later. As a Chrome extension, it captures any post type (text, photo, video, reel, link, album) along with engagement metrics, and lets you sort captures into boards or browse a community library of what's already working for other creators. The JSON export for AI tools is a nice touch for anyone feeding swiped examples into a writing assistant. The main open question is the free plan's exact limits, which PostSnag doesn't spell out clearly on its pricing page — worth checking directly before assuming it covers your use case. The $139 lifetime option is attractive if you're confident you'll use this long-term. This verdict is built from PostSnag's own published pricing and feature pages — RankerToolAI has not run a hands-on lab test of PostSnag.",
    "scores_table": [
      ("Feature Depth", "Capture, boards, community library, export", 7.5),
      ("Value for Money", "Free tier + $139 lifetime option", 8.0),
      ("Ease of Use", "Chrome extension, one-click capture", 8.0),
      ("Data Portability", "JSON export compatible with AI tools", 7.5),
      ("Scalability", "Agency/team use across many boards", 6.5),
    ],
    "pros": [
      "Captures every Facebook post type — text, photo, video, reel, link, album — with engagement metrics attached",
      "Community library lets you discover top-performing posts beyond just your own saves",
      "JSON export makes captured posts directly usable as prompts/examples for AI writing tools",
      "$139 lifetime option is a rare pricing choice in a market that's mostly gone subscription-only",
      "Free plan exists, so you can try the core capture workflow before paying",
    ],
    "cons": [
      "Free plan's exact limits aren't clearly published — confirm on PostSnag's own pricing page before relying on it",
      "Chrome-extension-only — no evidence of a standalone web app or other-browser support",
      "Facebook-specific — doesn't cover Instagram, TikTok, or other platforms in the same tool",
      "Newer, smaller product — fewer independent third-party reviews to cross-check against so far",
    ],
    "features": [
      ("Universal Post Capture", "One-click capture of any Facebook post type — text, photo, video, reel, link, or album — with the post's engagement metrics saved alongside it, not just a screenshot."),
      ("Custom Boards", "Organize captured posts into your own boards by topic, campaign, or client, and bookmark entire creator profiles to revisit later."),
      ("Community Library", "Browse top-performing posts other PostSnag users have captured across niches, useful for research beyond your own saved set."),
      ("JSON Export", "Export your swipe file in a structured JSON format built to be compatible with AI writing tools — feed real examples into a prompt instead of describing them from memory."),
    ],
    "pricing_rows": [
      ("Free", "$0", "Core capture workflow (exact limits not published)", False),
      ("Pro", "$19/mo", "Full feature set", True),
      ("Lifetime", "$139 one-time", "Pay once, use indefinitely", False),
    ],
    "pricing_note": "PostSnag's own pricing page doesn't spell out the free tier's exact caps — check <a href=\"/go/postsnag/\" rel=\"nofollow sponsored\" target=\"_blank\">PostSnag's current pricing</a> directly before assuming what's included.",
    "alternatives": [
      ("Foreplay", "A more established ad/creative swipe-file tool, generally broader than Facebook-only but at a higher price point aimed at agencies."),
      ("Manual bookmarking/screenshots", "The free default most marketers already use — PostSnag's pitch is replacing this with structured, searchable, metrics-attached captures."),
      ("Metricool or similar social analytics suites", "Broader multi-platform analytics tools that include some competitor-tracking, but without PostSnag's specific swipe-file/capture-and-organize workflow."),
    ],
    "faq": [
      ("Is PostSnag worth it?", "For a marketer, agency, or creator who studies competitor and top-performing Facebook content regularly, PostSnag replaces ad-hoc screenshotting with a structured, searchable swipe file that keeps engagement metrics attached. It's a narrow tool, so it's worth it specifically if Facebook content research is a recurring task, not a one-off."),
      ("Does PostSnag have a free plan?", "Yes, a free plan exists, though PostSnag's pricing page doesn't clearly spell out its exact limits — check directly on their site before assuming it covers your volume of captures."),
      ("Is PostSnag a lifetime deal?", "Yes — alongside the $19/mo Pro subscription, PostSnag offers a $139 one-time Lifetime plan, a pricing model most competitors in this space have moved away from."),
      ("Does PostSnag work on platforms other than Facebook?", "Based on its published feature set, PostSnag is currently Facebook-specific (posts, groups, reels) — there's no indication of Instagram, TikTok, or other platform support yet."),
      ("What are the best PostSnag alternatives?", "Foreplay is a more established swipe-file tool aimed at ad creatives, generally pricier and broader than Facebook-only. Manual screenshotting/bookmarking remains the free fallback PostSnag is designed to replace."),
    ],
    "related_review": ("/review/beehiiv/", "beehiiv Review"),
    "related_best": ("/best/ai-marketing-tools/", "Best AI Marketing Tools"),
    "footer_category": "More AI Marketing Resources",
  },
  {
    "slug": "viralityai",
    "name": "ViralityAI",
    "domain": "viralityai.net",
    "go_dest": "https://viralityai.net?ref=hongnngvnwrrvx2m",
    "category_badge": "AI Video Tools",
    "category_slug": "ai-video",
    "title": "ViralityAI Review 2026: Can It Really Predict a Viral Video?",
    "meta_desc": "ViralityAI review 2026: AI-scored virality prediction, trend discovery, and 10-parameter video analysis for TikTok, Instagram, and YouTube. Independent breakdown of pricing and features.",
    "h1": "ViralityAI Review 2026: Can It Really Predict a Viral Video?",
    "hero_sub": "Based on ViralityAI's published feature set and pricing, here's an honest, research-based look at whether its viral-score predictions and trend discovery are worth it. This is not a hands-on lab test — it's an independent breakdown of pricing, features, and fit for creators and agencies.",
    "score": "7.7",
    "price_note": "Free plan available &middot; Pro from $5.99/mo (annual)",
    "price_short": "Free &ndash; $9.99/mo",
    "updated": "September 2026",
    "date_iso": "2026-09-16",
    "date_human": "September 16, 2026",
    "verdict": "ViralityAI's pitch is analyzing your video before you post it — a viral score from 0-100 with a 10-parameter breakdown (hook strength, retention curve, CTA power, and more) rather than just guessing and checking analytics after the fact. No tool can guarantee virality, and that's not really the claim here; the more honest framing is that it's a structured pre-flight checklist backed by pattern analysis across trending content on TikTok, Instagram, and YouTube. The free plan (100 searches/month, 4 viral ideas) is generous enough to genuinely evaluate the discovery side before paying, and the $5.99/mo annual Pro tier is inexpensive for unlimited searches plus 20 video analyses/month. This verdict is built from ViralityAI's own published pricing and feature pages — RankerToolAI has not run a hands-on lab test of ViralityAI.",
    "scores_table": [
      ("AI Capability", "10-parameter video scoring, trend detection", 8.0),
      ("Feature Depth", "Discovery + analysis + audio/trend tools", 8.0),
      ("Value for Money", "Free tier + $5.99/mo annual Pro", 8.5),
      ("Ease of Use", "Keyword search under 2 seconds", 7.5),
      ("Scalability", "Max/Enterprise tiers for agencies", 6.5),
    ],
    "pros": [
      "Free plan includes 100 searches/month and 4 viral ideas — enough to genuinely test the discovery tools before paying",
      "10-parameter video breakdown (hook strength, retention curve, CTA power, etc.) goes well beyond a single opaque score",
      "Live trend tracking refreshed every 24 hours by country and niche, not a static global list",
      "Pro tier at $5.99/mo (annual) is inexpensive relative to the feature set",
      "No credit card required for the free plan, with a stated satisfaction guarantee",
    ],
    "cons": [
      "A \"viral score\" is inherently a prediction, not a guarantee — treat it as a pre-flight checklist, not a promise",
      "Max plan ($79.99/mo) is a steep jump from Pro if you need more than 20 analyses/month",
      "Per-analysis top-ups on the Max plan ($0.50 each) can add up for high-volume agency use",
      "Newer product — fewer independent third-party reviews to cross-check its scoring accuracy against so far",
    ],
    "features": [
      ("Keyword &amp; Trend Discovery", "Returns viral content across TikTok, Instagram, and YouTube for a given keyword in under 2 seconds, with live trend tracking refreshed every 24 hours by country and niche."),
      ("Viral Score (0-100)", "Scores a video before you post it, broken down across 10 parameters including hook strength, retention curve, and CTA power, with specific optimization suggestions and predicted performance lifts."),
      ("Competitor &amp; Creator Monitoring", "Real-time tracking of specific competitors or creators, useful for agencies watching multiple accounts at once."),
      ("Audio &amp; Transcription Tools", "Audio transcription plus trending-sound suggestions, so audio choice isn't left out of the pre-post optimization pass."),
    ],
    "pricing_rows": [
      ("Free", "$0/mo", "100 searches, 4 viral ideas, basic trends", False),
      ("Pro", "$5.99&ndash;$9.99/mo", "Unlimited searches, 20 analyses/mo, global trends", True),
      ("Max", "$79.99/mo", "300 analyses/mo, $0.50/analysis top-ups", False),
      ("Enterprise", "Custom", "SOC 2 Type II, dedicated team", False),
    ],
    "pricing_note": "Pro is $5.99/mo billed annually or $9.99/mo billed monthly. Check <a href=\"/go/viralityai/\" rel=\"nofollow sponsored\" target=\"_blank\">ViralityAI's current pricing</a> for the exact figure and any active promotions.",
    "alternatives": [
      ("Vidooly / analytics-first tools", "Broader post-publish analytics suites that report on what already happened, rather than ViralityAI's pre-post scoring focus."),
      ("Native platform analytics (TikTok/Instagram Insights)", "Free, but entirely retrospective — no pre-post prediction or cross-platform trend discovery."),
      ("Pictory.ai", "Focused on AI video editing/repurposing rather than virality scoring — a complement rather than a direct substitute; see our <a href=\"/review/pictory/\">Pictory review</a> if one exists, or <a href=\"/best/ai-video-tools/\">Best AI Video Tools</a>."),
    ],
    "faq": [
      ("Is ViralityAI worth it?", "For a creator or agency posting regularly across TikTok, Instagram, or YouTube, ViralityAI's pre-post scoring and 24-hour-refreshed trend tracking add a structured layer most people currently skip. The free plan is generous enough to test real value before committing, and Pro is inexpensive at $5.99/mo annual."),
      ("Can ViralityAI actually predict if a video will go viral?", "No tool can guarantee virality — ViralityAI's viral score is a pattern-based prediction across 10 parameters (hook, retention, CTA, etc.), best treated as a pre-flight optimization checklist rather than a certainty."),
      ("Does ViralityAI have a free plan?", "Yes — 100 searches/month, 4 viral ideas, and basic trend access, with no credit card required to start."),
      ("What platforms does ViralityAI cover?", "Instagram, TikTok, and YouTube are all covered for both trend discovery and video analysis, based on ViralityAI's published feature set."),
      ("What are the best ViralityAI alternatives?", "Native platform analytics (TikTok/Instagram Insights) are free but purely retrospective. Broader analytics suites report on what already happened rather than scoring a video before you post it, which is ViralityAI's specific differentiator."),
    ],
    "related_review": ("/best/ai-video-tools/", "Best AI Video Tools"),
    "related_best": ("/best/ai-video-tools/", "Best AI Video Tools"),
    "footer_category": "More AI Video Resources",
  },
]

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-5Z86G265');</script>
<!-- End Google Tag Manager -->

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="https://rankertoolai.com/review/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="https://rankertoolai.com/review/{slug}/">
  <meta property="og:site_name" content="RankerToolAI">
  <meta property="og:image" content="https://rankertoolai.com/assets/images/og-image.png">

  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Review","name":"{name} Review 2026","reviewBody":"{verdict_escaped}","datePublished":"{date_iso}","dateModified":"{date_iso}","author":{{"@type":"Organization","name":"RankerToolAI Editorial Team","url":"https://rankertoolai.com/about/"}},"publisher":{{"@type":"Organization","name":"RankerToolAI"}},"itemReviewed":{{"@type":"SoftwareApplication","name":"{name}","applicationCategory":"BusinessApplication","url":"https://{domain}"}},"reviewRating":{{"@type":"Rating","ratingValue":"{score}","bestRating":"10","worstRating":"1"}}}}</script>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://rankertoolai.com/"}},{{"@type":"ListItem","position":2,"name":"Reviews","item":"https://rankertoolai.com/review/"}},{{"@type":"ListItem","position":3,"name":"{name} Review","item":"https://rankertoolai.com/review/{slug}/"}}]}}</script>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"{name}","applicationCategory":"BusinessApplication","operatingSystem":"Web","url":"https://{domain}","offers":{{"@type":"Offer","price":"0","priceCurrency":"USD","description":"{price_note_plain}"}}}}</script>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_json}]}}</script>
  <link rel="icon" type="image/x-icon" href="/assets/images/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/images/favicon-32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"></noscript>
  <link rel="stylesheet" href="/assets/css/base.css">
  <style>
    #nav-toggle{{display:flex;align-items:center;justify-content:center;width:40px;height:40px;border:1px solid var(--color-border);border-radius:var(--radius);background:none;cursor:pointer;font-size:1.25rem;color:var(--color-text);}}
    @media(min-width:768px){{#nav-toggle{{display:none;}}}}
    #nav-menu{{display:none;}}
    #nav-menu.is-open{{display:flex;flex-direction:column;position:absolute;top:64px;left:0;right:0;background:#080c18;border-bottom:1px solid rgba(255,255,255,0.08);padding:1rem;z-index:200;box-shadow:0 10px 40px rgba(0,0,0,0.6);}}
    @media(min-width:768px){{#nav-menu{{display:flex!important;flex-direction:row;position:static;border:none;padding:0;box-shadow:none;}}}}
    .site-header{{position:relative;}}
    .review-hero{{background:linear-gradient(160deg,#060a14 0%,#0b1120 100%);border-bottom:1px solid rgba(255,255,255,0.06);padding:2.5rem 0;}}
    .review-meta-row{{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:1.25rem;}}
    .review-badge{{display:inline-flex;align-items:center;gap:0.35rem;background:rgba(22,163,74,0.15);border:1px solid rgba(22,163,74,0.3);border-radius:999px;padding:0.25rem 0.75rem;font-size:0.75rem;font-weight:700;color:#4ade80;}}
    .review-hero-grid{{display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:start;}}
    @media(max-width:640px){{.review-hero-grid{{grid-template-columns:1fr;}}}}
    .review-hero h1{{color:#f1f5f9;margin-bottom:0.75rem;font-size:clamp(1.5rem,3.5vw,2.25rem);}}
    .review-hero-sub{{color:rgba(148,163,184,0.85);font-size:0.95rem;margin-bottom:1.25rem;line-height:1.65;}}
    .score-card{{background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(22,163,74,0.25);border-radius:var(--radius-xl);padding:1.5rem 2rem;text-align:center;min-width:160px;flex-shrink:0;}}
    .score-number{{font-size:3rem;font-weight:900;background:linear-gradient(135deg,#16a34a,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}}
    .score-label{{font-size:0.7rem;color:rgba(148,163,184,0.6);font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:0.25rem;}}
    .score-stars{{color:#fbbf24;font-size:1.1rem;margin:0.5rem 0;}}
    .verdict-box{{background:linear-gradient(135deg,rgba(34,197,94,0.08),rgba(22,163,74,0.05));border:1px solid rgba(34,197,94,0.25);border-radius:var(--radius-lg);padding:1.5rem;margin:2rem 0;}}
    .verdict-box h3{{color:#4ade80;margin-bottom:0.5rem;font-size:1rem;}}
    .verdict-box p{{color:rgba(148,163,184,0.9);margin:0;font-size:0.95rem;line-height:1.7;}}
    .pros-cons{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:2rem 0;}}
    @media(max-width:580px){{.pros-cons{{grid-template-columns:1fr;}}}}
    .pros-box,.cons-box{{border-radius:var(--radius-lg);padding:1.5rem;}}
    .pros-box{{background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2);}}
    .cons-box{{background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);}}
    .pros-box h3{{color:#4ade80;margin-bottom:1rem;font-size:1rem;}}
    .cons-box h3{{color:#f87171;margin-bottom:1rem;font-size:1rem;}}
    .pros-box li,.cons-box li{{font-size:0.875rem;color:rgba(148,163,184,0.9);line-height:1.8;}}
    .criteria-table{{width:100%;border-collapse:collapse;margin:1.5rem 0;}}
    .criteria-table th{{text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:rgba(148,163,184,0.6);padding:0.75rem 1rem;border-bottom:1px solid rgba(255,255,255,0.08);}}
    .criteria-table td{{padding:0.875rem 1rem;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.9rem;color:rgba(148,163,184,0.85);}}
    .criteria-table tr:last-child td{{border-bottom:none;}}
    .score-bar{{background:rgba(255,255,255,0.06);border-radius:999px;height:8px;overflow:hidden;width:120px;}}
    .score-fill{{height:100%;border-radius:999px;background:linear-gradient(90deg,#16a34a,#4ade80);}}
    .affiliate-box{{background:linear-gradient(135deg,#0d1224,#131c2e);border:2px solid rgba(22,163,74,0.3);border-radius:var(--radius-xl);padding:2rem;text-align:center;margin:2.5rem 0;}}
    .affiliate-box h3{{color:#f1f5f9;margin-bottom:0.5rem;}}
    .affiliate-box p{{color:rgba(148,163,184,0.8);font-size:0.9rem;margin-bottom:1.25rem;}}
    .btn-affiliate-lg{{display:inline-flex;align-items:center;gap:0.5rem;padding:0.875rem 2.5rem;background:linear-gradient(135deg,#16a34a,#4ade80);color:white;font-weight:800;font-size:1rem;border-radius:999px;text-decoration:none;box-shadow:0 4px 24px rgba(22,163,74,0.5);transition:all 0.2s;}}
    .btn-affiliate-lg:hover{{transform:translateY(-2px);box-shadow:0 8px 32px rgba(22,163,74,0.65);text-decoration:none;color:white;}}
    .affiliate-note{{font-size:0.75rem;color:rgba(148,163,184,0.4);margin-top:0.75rem;}}
    .review-layout{{display:grid;grid-template-columns:1fr 280px;gap:2.5rem;padding:2rem 0 4rem;}}
    @media(max-width:900px){{.review-layout{{grid-template-columns:1fr;}}}}
    .toc-sidebar{{position:sticky;top:80px;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.5rem;}}
    .toc-sidebar h4{{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:rgba(148,163,184,0.6);margin-bottom:1rem;font-weight:700;}}
    .toc-sidebar a{{display:block;font-size:0.875rem;color:rgba(148,163,184,0.7);text-decoration:none;padding:0.4rem 0;border-left:2px solid transparent;padding-left:0.75rem;transition:all 0.15s;}}
    .toc-sidebar a:hover{{color:#4ade80;border-left-color:#4ade80;}}
    .faq-item{{border-bottom:1px solid rgba(255,255,255,0.07);padding:1.25rem 0;}}
    .faq-item:last-child{{border-bottom:none;}}
    .faq-item h3{{font-size:1rem;color:#f1f5f9;margin-bottom:0.5rem;}}
    .faq-item p{{font-size:0.9rem;color:rgba(148,163,184,0.85);margin:0;line-height:1.7;}}
    #back-to-top{{display:none;position:fixed;bottom:1.5rem;right:1.5rem;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#16a34a,#4ade80);color:white;align-items:center;justify-content:center;font-size:1.25rem;cursor:pointer;border:none;box-shadow:0 4px 20px rgba(22,163,74,0.5);z-index:50;transition:all 0.15s;}}
    .sticky-cta{{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(90deg,#0a0f1e,#0d1528);border-top:1px solid rgba(22,163,74,0.3);padding:0.75rem 1.5rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;z-index:100;transform:translateY(100%);transition:transform 0.3s ease;backdrop-filter:blur(12px);}}
    .sticky-cta.visible{{transform:translateY(0);}}
    .sticky-cta-btn{{flex-shrink:0;padding:0.55rem 1.25rem;background:linear-gradient(135deg,#16a34a,#4ade80);color:white;font-weight:700;border-radius:var(--radius);text-decoration:none;font-size:0.85rem;white-space:nowrap;}}
    .sticky-cta-btn:hover{{color:white;text-decoration:none;}}
  </style>
  <script async src="/assets/js/pint.js"></script>

  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7922606734780809" crossorigin="anonymous"></script>

  <!-- ═══ ANALYTICS & ADS TRACKING ═══ -->
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      var passKeys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid'];
      var incoming = new URLSearchParams(window.location.search);
      document.querySelectorAll('a[href*="/go/"]').forEach(function(el) {{
        el.addEventListener('click', function() {{
          try {{
            var dest = new URL(el.href, window.location.href);
            passKeys.forEach(function(k) {{
              if (incoming.has(k) && !dest.searchParams.has(k)) dest.searchParams.set(k, incoming.get(k));
            }});
            el.href = dest.toString();
          }} catch (e) {{}}

          var _tool = el.href.split('/go/')[1]?.replace(/\\//g,'') || 'unknown';
          var _comm = (window.AFFILIATE_COMMISSIONS && window.AFFILIATE_COMMISSIONS[_tool]) || {{value:1.0,currency:'USD'}};
          dataLayer.push({{
            event: 'affiliate_click',
            tool: _tool,
            page: window.location.pathname,
            value: _comm.value,
            currency: _comm.currency
          }});
        }});
      }});

      setTimeout(function() {{
        dataLayer.push({{event: 'engaged_60s'}});
      }}, 60000);
    }});
  </script>

  <!-- Microsoft Clarity -->
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
      c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window,document,"clarity","script","x97zf4vn2v");
  </script>
  <!-- ══════════════════════════════════ -->
  </head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5Z86G265"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->

<div class="sticky-cta" id="sticky-cta">
  <div style="display:flex;align-items:center;gap:0.75rem;min-width:0;">
    <div style="font-size:0.875rem;color:#f1f5f9;font-weight:700;white-space:nowrap;">{name}</div>
    <div style="font-size:0.8rem;color:#94a3b8;white-space:nowrap;">{score}/10 &middot; {category_badge} &middot; {price_short}</div>
  </div>
  <a href="/go/{slug}/" class="sticky-cta-btn" rel="nofollow sponsored" target="_blank">Try {name} &rarr;</a>
</div>
<button id="back-to-top" aria-label="Back to top">&uarr;</button>

<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="/" class="site-logo" style="-webkit-text-fill-color:unset;background:none;display:flex;align-items:center;gap:0.5rem;text-decoration:none;">
        <img src="/assets/images/logo-dark.webp" onerror="this.src='/assets/images/logo-dark.png'" alt="RankerToolAI" style="height:38px;width:38px;object-fit:contain;">
        <span style="font-size:1.15rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">RankerTool<span style="background:linear-gradient(135deg,#22c55e,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"> AI</span></span>
      </a>
      <button id="nav-toggle" aria-expanded="false" aria-label="Toggle menu">&#9776;</button>
      <ul class="nav-primary" id="nav-menu" role="list">
        <li><a href="/review/">Reviews</a></li>
        <li><a href="/compare/">Compare</a></li>
        <li><a href="/alternatives/">Alternatives</a></li>
        <li><a href="/best/">Best Tools</a></li>
        <li><a href="/category/">Categories</a></li>
      </ul>
    </div>
  </div>
</header>

<div class="review-hero">
  <div class="container">
    <nav class="breadcrumb" style="margin-bottom:1rem;">
      <a href="/">Home</a><span class="breadcrumb-sep">&rsaquo;</span>
      <a href="/review/">Reviews</a><span class="breadcrumb-sep">&rsaquo;</span>
      <span>{name}</span>
    </nav>
    <div class="review-hero-grid">
      <div>
        <div class="review-meta-row">
          <span class="review-badge">{category_badge}</span>
          <span style="font-size:0.8rem;color:rgba(148,163,184,0.5);">Updated: {updated}</span>
        </div>
        <h1>{h1}</h1>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.75rem;font-size:0.8rem;color:#64748b;">By <a href="/about/" style="color:#f97316;">RankerToolAI Editorial Team</a> &middot; {date_human}</div>

        <p class="review-hero-sub">{hero_sub}</p>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
          <a href="/go/{slug}/" rel="nofollow sponsored" target="_blank" class="btn btn-affiliate" style="background:linear-gradient(135deg,#16a34a,#15803d);color:white;font-weight:800;border-radius:var(--radius);padding:0.6rem 1.4rem;text-decoration:none;">Try {name} &rarr;</a>
          <a href="#verdict" style="padding:0.6rem 1.25rem;border:1px solid rgba(255,255,255,0.15);border-radius:var(--radius);color:rgba(148,163,184,0.85);text-decoration:none;font-size:0.9rem;">See Verdict</a>
        </div>
        <div style="font-size:0.72rem;color:rgba(148,163,184,0.5);margin-top:0.5rem;">{price_note}</div>
      </div>
      <div class="score-card">
        <div class="score-number">{score}</div>
        <div class="score-stars">&#9733;&#9733;&#9733;&#9733;</div>
        <div class="score-label">Overall Score</div>
        <div style="margin-top:1rem;font-size:0.8rem;color:rgba(148,163,184,0.6);">{price_short}</div>
        <a href="/go/{slug}/" rel="nofollow sponsored" target="_blank" class="btn btn-primary" style="display:block;margin-top:0.75rem;font-size:0.85rem;padding:0.5rem 1rem;text-align:center;">Try {name} &rarr;</a>
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="review-layout">

    <article>
      <div class="verdict-box" id="verdict">
        <h3>Our Verdict</h3>
        <p>{verdict}</p>
      </div>

      <h2 id="scores">How {name} Scores</h2>
      <table class="criteria-table">
        <thead><tr><th>Criterion</th><th>Score</th><th>Rating</th></tr></thead>
        <tbody>
{scores_rows}
        </tbody>
      </table>

      <div class="pros-cons">
        <div class="pros-box">
          <h3>&#10003; Pros</h3>
          <ul>
{pros_li}
          </ul>
        </div>
        <div class="cons-box">
          <h3>&#10007; Cons</h3>
          <ul>
{cons_li}
          </ul>
        </div>
      </div>

      <div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(16,185,129,0.08));border:1px solid rgba(34,197,94,0.25);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;margin:1.5rem 0;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;">
        <div>
          <p style="margin:0;font-weight:600;color:rgba(248,250,252,0.95);">{name}</p>
          <p style="margin:0.25rem 0 0;font-size:0.85rem;color:rgba(148,163,184,0.8);">{price_note}</p>
        </div>
        <a href="/go/{slug}/" class="btn btn-primary" rel="nofollow sponsored" target="_blank" style="white-space:nowrap;">Try {name} &rarr;</a>
      </div>

      <h2 id="features">What {name} Offers</h2>
{features_html}

      <h2 id="pricing">{name} Pricing (2026)</h2>
      <table class="pricing-table">
        <thead><tr><th>Plan</th><th>Price</th><th>Details</th></tr></thead>
        <tbody>
{pricing_rows_html}
        </tbody>
      </table>
      <p style="font-size:0.85rem;color:rgba(148,163,184,0.6);">{pricing_note}</p>

      <div class="affiliate-box">
        <h3>Try {name}</h3>
        <p>{price_note}</p>
        <a href="/go/{slug}/" class="btn-affiliate-lg" rel="nofollow sponsored" target="_blank">Try {name} &rarr;</a>
        <p class="affiliate-note">Affiliate link &mdash; we earn a commission if you upgrade, at no extra cost to you.</p>
      </div>

      <h2 id="alternatives">Best {name} Alternatives</h2>
      <p>{name} isn't the only option in this space. Here's how the leading alternatives compare:</p>
      <ul>
{alternatives_li}
      </ul>

      <h2 id="faq">Frequently Asked Questions</h2>
      <div>
{faq_html}
      </div>

      <div style="margin-top:1.5rem;"><a href="/go/{slug}/" rel="nofollow sponsored" target="_blank" class="btn btn-primary">Try {name} &rarr;</a></div>

      <div class="newsletter-section">
        <h3>Get Our Weekly AI Tool Roundup</h3>
        <p>New reviews, rankings &amp; deals &mdash; every Thursday. No spam, unsubscribe anytime.</p>
        <form class="newsletter-form" action="https://formsubmit.co/b21365b0716308a5caecd30f63ea8e22" method="POST">
          <input type="hidden" name="_subject" value="Newsletter Signup — RankerToolAI">
          <input type="hidden" name="_next" value="https://rankertoolai.com/?subscribed=1">
          <input type="hidden" name="_captcha" value="false">
          <input type="hidden" name="source" value="inline_newsletter">
          <input type="email" name="email" placeholder="your@email.com" required autocomplete="email">
          <button type="submit">Subscribe Free &rarr;</button>
        </form>
      </div>
    </article>

    <aside>
      <div class="toc-sidebar">
        <h4>On This Page</h4>
        <a href="#verdict">Our Verdict</a>
        <a href="#scores">Scores</a>
        <a href="#features">Features</a>
        <a href="#pricing">Pricing</a>
        <a href="#alternatives">Alternatives</a>
        <a href="#faq">FAQ</a>
      </div>
      <div style="margin-top:1.5rem;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.25rem;text-align:center;">
        <div style="font-size:2rem;font-weight:900;background:linear-gradient(135deg,#16a34a,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{score}/10</div>
        <div style="color:#fbbf24;margin:0.25rem 0;">&#9733;&#9733;&#9733;&#9733;</div>
        <div style="font-size:0.75rem;color:rgba(148,163,184,0.6);margin-bottom:1rem;">RankerToolAI Score</div>
        <a href="/go/{slug}/" class="btn-affiliate-lg" rel="nofollow sponsored" target="_blank" style="padding:0.7rem 1.5rem;font-size:0.9rem;">Try {name} &rarr;</a>
        <div style="font-size:0.72rem;color:rgba(148,163,184,0.4);margin-top:0.5rem;">{price_short}</div>
      </div>
      <div style="margin-top:1.5rem;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.25rem;">
        <h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:rgba(148,163,184,0.6);margin-bottom:0.75rem;font-weight:700;">Related</h4>
        <a href="{related_review_href}" style="display:block;font-size:0.875rem;color:rgba(148,163,184,0.75);text-decoration:none;padding:0.4rem 0;">{related_review_label} &rarr;</a>
        <a href="{related_best_href}" style="display:block;font-size:0.875rem;color:rgba(148,163,184,0.75);text-decoration:none;padding:0.4rem 0;">{related_best_label} &rarr;</a>
      </div>
    </aside>

  </div>
</div>

<div style="background:linear-gradient(135deg,rgba(22,163,74,0.08),rgba(21,128,61,0.04));border-top:1px solid rgba(22,163,74,0.2);border-bottom:1px solid rgba(22,163,74,0.2);padding:2rem 0;">
  <div class="container">
    <p style="font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#4ade80;margin-bottom:1rem;">{footer_category}</p>
    <div style="display:flex;flex-wrap:wrap;gap:0.75rem;">
      <a href="{related_best_href}" style="display:inline-flex;align-items:center;gap:0.4rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:999px;padding:0.4rem 1rem;font-size:0.85rem;color:#4ade80;text-decoration:none;" onmouseover="this.style.background='rgba(22,163,74,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'">{related_best_label}</a>
      <a href="/deals/" style="display:inline-flex;align-items:center;gap:0.4rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:999px;padding:0.4rem 1rem;font-size:0.85rem;color:#4ade80;text-decoration:none;" onmouseover="this.style.background='rgba(22,163,74,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'">&#128176; All Software Deals</a>
    </div>
  </div>
</div>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" style="display:flex;align-items:center;gap:0.5rem;text-decoration:none;margin-bottom:0.75rem;">
          <img src="/assets/images/logo-dark.webp" onerror="this.src='/assets/images/logo-dark.png'" alt="Dark logo" style="height:32px;width:32px;object-fit:contain;" loading="lazy">
          <span style="font-size:1rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">RankerTool AI</span>
        </a>
        <p class="footer-tagline">Independent reviews and comparisons of the best AI tools. We help you find the right tool without the guesswork.</p>
      </div>
      <div class="footer-col">
        <h5>Reviews</h5>
        <ul>
          <li><a href="/category/ai-writing/">AI Writing Tools</a></li>
          <li><a href="/category/ai-image/">AI Image Generators</a></li>
          <li><a href="/category/ai-video/">AI Video Tools</a></li>
          <li><a href="/category/ai-seo/">AI SEO Tools</a></li>
          <li><a href="/review/">All Reviews</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>Compare</h5>
        <ul>
          <li><a href="/compare/">All Comparisons</a></li>
          <li><a href="/alternatives/">Alternatives</a></li>
          <li><a href="/best/">Best Tools</a></li>
          <li><a href="/deals/">Deals &amp; Discounts</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>Company</h5>
        <ul>
          <li><a href="/about/">About Us</a></li>
          <li><a href="/methodology/">Our Methodology</a></li>
          <li><a href="/affiliate-disclosure/">Affiliate Disclosure</a></li>
          <li><a href="/privacy-policy/">Privacy Policy</a></li>
          <li><a href="/terms/">Terms of Service</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> RankerToolAI participates in affiliate programs. When you click links and make a purchase, we may earn a commission at no extra cost to you. This never influences our ratings. <a href="/affiliate-disclosure/" style="color:#9ca3af;">Read full disclosure &rarr;</a>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 RankerToolAI. All rights reserved.</span>
      <span><a href="/sitemap.xml" style="color:#9ca3af;">Sitemap</a></span>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js?v=20261013"></script>
<script src="/assets/js/cookie-consent.js" defer></script>
<script src="/assets/js/compare-widget.js" defer></script>
<script>
  const stickyCta = document.getElementById('sticky-cta');
  const btn = document.getElementById('back-to-top');
  window.addEventListener('scroll', () => {{
    if(window.scrollY > 300){{ stickyCta.classList.add('visible'); btn.style.display='flex'; }}
    else {{ stickyCta.classList.remove('visible'); btn.style.display='none'; }}
  }});
  btn.addEventListener('click', () => window.scrollTo({{top:0,behavior:'smooth'}}));
</script>
</body>
</html>
'''

def esc(s):
    return s.replace('"', '\\"').replace("\n", " ")

def render(t):
    scores_rows = "\n".join(
        f'''          <tr>
            <td><strong>{c[0]}</strong><br><span style="font-size:0.8rem;color:rgba(148,163,184,0.6);">{c[1]}</span></td>
            <td style="font-weight:700;color:#4ade80;">{c[2]}/10</td>
            <td><div class="score-bar"><div class="score-fill" style="width:{int(c[2]*10)}%"></div></div></td>
          </tr>'''
        for c in t["scores_table"]
    )
    pros_li = "\n".join(f"            <li>{p}</li>" for p in t["pros"])
    cons_li = "\n".join(f"            <li>{c}</li>" for c in t["cons"])
    features_html = "\n".join(f"      <h3>{f[0]}</h3>\n      <p>{f[1]}</p>\n" for f in t["features"])
    pricing_rows_html = "\n".join(
        f'''          <tr{' style="background:rgba(22,163,74,0.06);"' if r[3] else ''}><td><strong>{r[0]}</strong>{' ⭐' if r[3] else ''}</td><td>{r[1]}</td><td>{r[2]}</td></tr>'''
        for r in t["pricing_rows"]
    )
    alternatives_li = "\n".join(f"        <li><strong>{a[0]}</strong> &mdash; {a[1]}</li>" for a in t["alternatives"])
    faq_html = "\n".join(
        f'''        <div class="faq-item">
          <h3>{q[0]}</h3>
          <p>{q[1]}</p>
        </div>'''
        for q in t["faq"]
    )
    faq_json = ",".join(
        f'{{"@type":"Question","name":"{esc(q[0])}","acceptedAnswer":{{"@type":"Answer","text":"{esc(q[1])}"}}}}'
        for q in t["faq"]
    )

    page = TEMPLATE.format(
        title=t["title"], meta_desc=t["meta_desc"], slug=t["slug"], name=t["name"],
        domain=t["domain"], score=t["score"], date_iso=t["date_iso"], date_human=t["date_human"],
        verdict_escaped=esc(t["verdict"]), price_note_plain=t["price_note"].replace("&middot;", "-"),
        faq_json=faq_json, category_badge=t["category_badge"], price_short=t["price_short"],
        h1=t["h1"], updated=t["updated"], hero_sub=t["hero_sub"], price_note=t["price_note"],
        verdict=t["verdict"], scores_rows=scores_rows, pros_li=pros_li, cons_li=cons_li,
        features_html=features_html, pricing_rows_html=pricing_rows_html, pricing_note=t["pricing_note"],
        alternatives_li=alternatives_li, faq_html=faq_html,
        related_review_href=t["related_review"][0], related_review_label=t["related_review"][1],
        related_best_href=t["related_best"][0], related_best_label=t["related_best"][1],
        footer_category=t["footer_category"],
    )
    for root in OUT_ROOTS:
        outdir = os.path.join(root, "review", t["slug"])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
        print(f"Wrote {outdir}\\index.html ({len(page.splitlines())} lines)")

if __name__ == "__main__":
    for t in TOOLS:
        render(t)
