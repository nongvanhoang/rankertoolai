#!/usr/bin/env python3
import os, json, html as htmlmod

BASE = os.path.dirname(__file__)

def render(t):
    slug = t["slug"]
    name = t["name"]
    score = t["score"]
    stars = t["stars"]
    price_from = t["price_from"]
    category_badge = t["category_badge"]
    title = t["title"]
    meta_desc = t["meta_desc"]
    og_title = t["og_title"]
    og_desc = t["og_desc"]
    review_body = t["review_body"]
    sub = t["hero_sub"]
    verdict = t["verdict"]
    criteria = t["criteria"]  # list of (name, desc, score)
    pros = t["pros"]
    cons = t["cons"]
    feature_sections = t["feature_sections"]  # list of (h3, text)
    pricing_rows = t["pricing_rows"]  # list of (plan, price, col2, col3, best_for)
    pricing_cols = t["pricing_cols"]  # (col2_header, col3_header)
    pricing_note = t["pricing_note"]
    alternatives = t["alternatives"]  # list of (name_html, desc)
    faqs = t["faqs"]  # list of (q,a)
    related = t["related"]  # list of (slug, label) for related reviews
    go_slug = t["go_slug"]
    cta_label = t["cta_label"]
    free_note = t["free_note"]
    resources = t["resources"]  # list of (emoji, label, href)
    app_category = t["app_category"]
    offer_price = t["offer_price"]

    faq_json = [{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]
    review_ld = {
        "@context":"https://schema.org","@type":"Review","name":title,
        "reviewBody":review_body,"datePublished":"2026-06-30","dateModified":"2026-06-30",
        "author":{"@type":"Organization","name":"RankerToolAI","url":"https://rankertoolai.com"},
        "publisher":{"@type":"Organization","name":"RankerToolAI"},
        "itemReviewed":{"@type":"SoftwareApplication","name":name,"applicationCategory":app_category,"url":t["official_url"],"offers":{"@type":"Offer","price":offer_price,"priceCurrency":"USD"}},
        "reviewRating":{"@type":"Rating","ratingValue":str(score),"bestRating":"10","worstRating":"1"}
    }
    breadcrumb_ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":"https://rankertoolai.com/"},
        {"@type":"ListItem","position":2,"name":"Reviews","item":"https://rankertoolai.com/review/"},
        {"@type":"ListItem","position":3,"name":f"{name} Review","item":f"https://rankertoolai.com/review/{slug}/"}
    ]}
    software_ld = {"@context":"https://schema.org","@type":"SoftwareApplication","name":name,"applicationCategory":app_category,"operatingSystem":"Web","url":t["official_url"],
        "offers":{"@type":"Offer","price":offer_price,"priceCurrency":"USD","description":free_note},
        "aggregateRating":{"@type":"AggregateRating","ratingValue":str(score),"bestRating":"10","worstRating":"1","ratingCount":"1","reviewCount":"1"}}
    faq_ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":faq_json}

    criteria_rows = "\n".join(f'''          <tr>
            <td><strong>{c[0]}</strong><br><span style="font-size:0.8rem;color:rgba(148,163,184,0.6);">{c[1]}</span></td>
            <td style="font-weight:700;color:#f97316;">{c[2]}/10</td>
            <td><div class="score-bar"><div class="score-fill" style="width:{int(float(c[2])*10)}%"></div></div></td>
          </tr>''' for c in criteria)

    pros_li = "\n".join(f"            <li>{p}</li>" for p in pros)
    cons_li = "\n".join(f"            <li>{c}</li>" for c in cons)

    feature_html = "\n\n".join(f"      <h3>{h}</h3>\n      <p>{p}</p>" for h,p in feature_sections)

    pricing_header = f"<tr><th>Plan</th><th>{pricing_cols[0]}</th><th>{pricing_cols[1]}</th><th>Best For</th></tr>"
    pricing_body = "\n".join(
        f'          <tr{" style=\"background:rgba(249,115,22,0.06);\"" if len(r)>4 and r[4] else ""}><td><strong>{r[0]}</strong>{" ⭐" if len(r)>4 and r[4] else ""}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>'
        for r in pricing_rows
    )

    alt_li = "\n".join(f"        <li><strong>{a[0]}</strong> — {a[1]}</li>" for a in alternatives)

    faq_items = "\n".join(f'''        <div class="faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </div>''' for q,a in faqs)

    related_reading = "\n".join(f'          <a href="/review/{r[0]}/" style="color:var(--color-primary);text-decoration:none;font-size:0.9rem;">→ {r[1]}</a>' for r in related)
    related_sidebar = "\n".join(f'        <a href="/review/{r[0]}/" style="display:block;font-size:0.875rem;color:rgba(148,163,184,0.75);text-decoration:none;padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">{r[1].split(" — ")[0]} Review →</a>' for r in related)

    resource_pills = "\n".join(f'      <a href="{r[2]}" style="display:inline-flex;align-items:center;gap:0.4rem;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:999px;padding:0.4rem 1rem;font-size:0.85rem;color:#4ade80;text-decoration:none;" onmouseover="this.style.background=\'rgba(22,163,74,0.2)\'" onmouseout="this.style.background=\'rgba(255,255,255,0.05)\'">{r[0]} {r[1]}</a>' for r in resources)

    toc_html = '\n        <a href="#verdict">Our Verdict</a>\n        <a href="#scores">Scores</a>\n        <a href="#features">Features Tested</a>\n        <a href="#pricing">Pricing</a>\n        <a href="#alternatives">Alternatives</a>\n        <a href="#faq">FAQ</a>'

    out = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="https://rankertoolai.com/review/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:url" content="https://rankertoolai.com/review/{slug}/">
  <meta property="og:site_name" content="RankerToolAI">
  <meta property="og:image" content="https://rankertoolai.com/assets/images/og-review-{slug}.jpg">

  <script type="application/ld+json">{json.dumps(review_ld)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_ld)}</script>
  <script type="application/ld+json">{json.dumps(software_ld)}</script>
  <script type="application/ld+json">{json.dumps(faq_ld)}</script>
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
    .review-badge{{display:inline-flex;align-items:center;gap:0.35rem;background:rgba(249,115,22,0.15);border:1px solid rgba(249,115,22,0.3);border-radius:999px;padding:0.25rem 0.75rem;font-size:0.75rem;font-weight:700;color:#f97316;}}
    .review-hero-grid{{display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:start;}}
    @media(max-width:640px){{.review-hero-grid{{grid-template-columns:1fr;}}}}
    .review-hero h1{{color:#f1f5f9;margin-bottom:0.75rem;font-size:clamp(1.5rem,3.5vw,2.25rem);}}
    .review-hero-sub{{color:rgba(148,163,184,0.85);font-size:0.95rem;margin-bottom:1.25rem;line-height:1.65;}}
    .score-card{{background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(249,115,22,0.25);border-radius:var(--radius-xl);padding:1.5rem 2rem;text-align:center;min-width:160px;flex-shrink:0;}}
    .score-number{{font-size:3rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}}
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
    .score-fill{{height:100%;border-radius:999px;background:linear-gradient(90deg,#f97316,#fbbf24);}}
    .affiliate-box{{background:linear-gradient(135deg,#0d1224,#131c2e);border:2px solid rgba(249,115,22,0.3);border-radius:var(--radius-xl);padding:2rem;text-align:center;margin:2.5rem 0;}}
    .affiliate-box h3{{color:#f1f5f9;margin-bottom:0.5rem;}}
    .affiliate-box p{{color:rgba(148,163,184,0.8);font-size:0.9rem;margin-bottom:1.25rem;}}
    .btn-affiliate-lg{{display:inline-flex;align-items:center;gap:0.5rem;padding:0.875rem 2.5rem;background:linear-gradient(135deg,#f97316,#fbbf24);color:white;font-weight:800;font-size:1rem;border-radius:999px;text-decoration:none;box-shadow:0 4px 24px rgba(249,115,22,0.5);transition:all 0.2s;}}
    .btn-affiliate-lg:hover{{transform:translateY(-2px);box-shadow:0 8px 32px rgba(249,115,22,0.65);text-decoration:none;color:white;}}
    .affiliate-note{{font-size:0.75rem;color:rgba(148,163,184,0.4);margin-top:0.75rem;}}
    .review-layout{{display:grid;grid-template-columns:1fr 280px;gap:2.5rem;padding:2rem 0 4rem;}}
    @media(max-width:900px){{.review-layout{{grid-template-columns:1fr;}}}}
    .toc-sidebar{{position:sticky;top:80px;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.5rem;}}
    .toc-sidebar h4{{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:rgba(148,163,184,0.6);margin-bottom:1rem;font-weight:700;}}
    .toc-sidebar a{{display:block;font-size:0.875rem;color:rgba(148,163,184,0.7);text-decoration:none;padding:0.4rem 0;border-left:2px solid transparent;padding-left:0.75rem;transition:all 0.15s;}}
    .toc-sidebar a:hover{{color:#f97316;border-left-color:#f97316;}}
    .faq-item{{border-bottom:1px solid rgba(255,255,255,0.07);padding:1.25rem 0;}}
    .faq-item:last-child{{border-bottom:none;}}
    .faq-item h3{{font-size:1rem;color:#f1f5f9;margin-bottom:0.5rem;}}
    .faq-item p{{font-size:0.9rem;color:rgba(148,163,184,0.85);margin:0;line-height:1.7;}}
    #back-to-top{{display:none;position:fixed;bottom:1.5rem;right:1.5rem;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#f97316,#fbbf24);color:white;align-items:center;justify-content:center;font-size:1.25rem;cursor:pointer;border:none;box-shadow:0 4px 20px rgba(249,115,22,0.5);z-index:50;transition:all 0.15s;}}
  </style>

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-81KB8ECCVF"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-81KB8ECCVF');    document.addEventListener('DOMContentLoaded', function() {{
      document.querySelectorAll('a[href*="/go/"]').forEach(function(el) {{
        el.addEventListener('click', function() {{
          gtag('event', 'affiliate_click', {{'tool': el.href.split('/go/')[1]?.replace(/\\//g,'') || 'unknown','page': window.location.pathname}});
        }});
      }});
    }});
  </script>
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
      c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window,document,"clarity","script","x97zf4vn2v");
  </script>
  <script async src="/assets/js/pint.js"></script>
</head>
<body>
<button id="back-to-top" aria-label="Back to top">↑</button>

<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="/" class="site-logo" style="-webkit-text-fill-color:unset;background:none;display:flex;align-items:center;gap:0.5rem;text-decoration:none;">
        <img src="/assets/images/logo-dark.webp" onerror="this.src='/assets/images/logo-dark.png'" alt="RankerToolAI" style="height:38px;width:38px;object-fit:contain;">
        <span style="font-size:1.15rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">RankerTool<span style="background:linear-gradient(135deg,#22c55e,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"> AI</span></span>
      </a>
      <button id="nav-toggle" aria-expanded="false" aria-label="Toggle menu">☰</button>
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
      <a href="/">Home</a><span class="breadcrumb-sep">›</span>
      <a href="/review/">Reviews</a><span class="breadcrumb-sep">›</span>
      <span>{name}</span>
    </nav>
    <div class="review-hero-grid">
      <div>
        <div class="review-meta-row">
          <img src="/assets/images/logos/{slug}.svg" alt="{name}" width="44" height="44" style="border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);padding:4px;object-fit:contain;" loading="lazy" onerror="this.style.display='none'">
          <span class="review-badge">{category_badge}</span>
          <span style="font-size:0.8rem;color:rgba(148,163,184,0.5);">Last tested: June 2026</span>
        </div>
        <h1>{title}</h1>
        <p class="review-hero-sub">{sub}</p>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
          <a href="#verdict" class="btn btn-affiliate" style="background:linear-gradient(135deg,#f97316,#fbbf24);color:white;font-weight:700;">See Our Verdict →</a>
          <a href="#pricing" style="padding:0.6rem 1.25rem;border:1px solid rgba(255,255,255,0.15);border-radius:var(--radius);color:rgba(148,163,184,0.85);text-decoration:none;font-size:0.9rem;">View Pricing</a>
        </div>
      </div>
      <div class="score-card">
        <div class="score-number">{score}</div>
        <div class="score-stars">{stars}</div>
        <div class="score-label">Overall Score</div>
        <div style="margin-top:1rem;font-size:0.8rem;color:rgba(148,163,184,0.6);">From <strong style="color:#f1f5f9;">{price_from}</strong></div>
        <a href="/go/{go_slug}/" rel="nofollow sponsored" target="_blank" class="btn btn-primary" style="display:block;margin-top:0.75rem;font-size:0.85rem;padding:0.5rem 1rem;text-align:center;">{cta_label}</a>
        <div style="font-size:0.72rem;color:rgba(148,163,184,0.5);margin-top:0.4rem;text-align:center;">{free_note}</div>
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="review-layout">

    <article>
      <div style="margin-top:2rem;padding:1.25rem 1.5rem;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);">
        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8;margin-bottom:0.75rem;">Related Reading</div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
{related_reading}
        </div>
      </div>

      <div class="verdict-box" id="verdict">
        <h3>Our Verdict</h3>
        <p>{verdict}</p>
      </div>

      <h2 id="scores">How We Scored {name}</h2>
      <table class="criteria-table">
        <thead>
          <tr><th>Criterion</th><th>Score</th><th>Rating</th></tr>
        </thead>
        <tbody>
{criteria_rows}
        </tbody>
      </table>

      <div class="pros-cons">
        <div class="pros-box">
          <h3>✓ Pros</h3>
          <ul>
{pros_li}
          </ul>
        </div>
        <div class="cons-box">
          <h3>✗ Cons</h3>
          <ul>
{cons_li}
          </ul>
        </div>
      </div>

      <div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(16,185,129,0.08));border:1px solid rgba(34,197,94,0.25);border-radius:var(--radius-lg);padding:1.25rem 1.5rem;margin:1.5rem 0;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;">
        <div>
          <p style="margin:0;font-weight:600;color:rgba(248,250,252,0.95);">{name} — {free_note}</p>
          <p style="margin:0.25rem 0 0;font-size:0.85rem;color:rgba(148,163,184,0.8);">{sub}</p>
        </div>
        <a href="/go/{go_slug}/" class="btn btn-primary" rel="nofollow sponsored" target="_blank" style="white-space:nowrap;">{cta_label}</a>
      </div>

      <h2 id="features">{name} Features — Tested</h2>

{feature_html}

      <h2 id="pricing">{name} Pricing (2026)</h2>
      <table class="pricing-table">
        <thead>
          {pricing_header}
        </thead>
        <tbody>
{pricing_body}
        </tbody>
      </table>
      <p style="font-size:0.85rem;color:rgba(148,163,184,0.6);">{pricing_note}</p>

      <div class="affiliate-box">
        <h3>Try {name} — {free_note}</h3>
        <p>{sub}</p>
        <a href="/go/{go_slug}/" class="btn-affiliate-lg" rel="nofollow sponsored">{cta_label}</a>
        <p class="affiliate-note">Affiliate link — we may earn a commission if you upgrade, at no extra cost to you.</p>
      </div>

      <h2 id="alternatives">Best {name} Alternatives</h2>
      <p>{name} isn't for everyone. Here are the top alternatives depending on your needs:</p>
      <ul>
{alt_li}
      </ul>

      <h2 id="faq">Frequently Asked Questions</h2>
      <div>
{faq_items}
      </div>

      <div style="margin-top:1.5rem;"><a href="/go/{go_slug}/" rel="nofollow sponsored" target="_blank" class="btn btn-primary">{cta_label}</a></div>

      <div class="newsletter-section">
        <h3>Get Our Weekly AI Tool Roundup</h3>
        <p>New reviews, rankings &amp; deals — every Thursday. No spam, unsubscribe anytime.</p>
        <form class="newsletter-form" action="https://formsubmit.co/nongvanhoang1608@gmail.com" method="POST">
          <input type="hidden" name="_subject" value="Newsletter Signup — RankerToolAI">
          <input type="hidden" name="_next" value="https://rankertoolai.com/?subscribed=1">
          <input type="hidden" name="_captcha" value="false">
          <input type="hidden" name="source" value="inline_newsletter">
          <input type="email" name="email" placeholder="your@email.com" required autocomplete="email">
          <button type="submit">Subscribe Free →</button>
        </form>
      </div>
    </article>

    <aside>
      <div class="toc-sidebar">
        <h4>On This Page</h4>{toc_html}
      </div>
      <div style="margin-top:1.5rem;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.25rem;text-align:center;">
        <div style="font-size:2rem;font-weight:900;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{score}/10</div>
        <div style="color:#fbbf24;margin:0.25rem 0;">{stars}</div>
        <div style="font-size:0.75rem;color:rgba(148,163,184,0.6);margin-bottom:1rem;">RankerToolAI Score</div>
        <a href="/go/{go_slug}/" class="btn-affiliate-lg" rel="nofollow sponsored" style="padding:0.7rem 1.5rem;font-size:0.9rem;">{cta_label}</a>
        <div style="font-size:0.72rem;color:rgba(148,163,184,0.4);margin-top:0.5rem;">From {price_from}</div>
      </div>
      <div style="margin-top:1.5rem;background:linear-gradient(135deg,#131c2e,#0f1829);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-lg);padding:1.25rem;">
        <h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:rgba(148,163,184,0.6);margin-bottom:0.75rem;font-weight:700;">Related Reviews</h4>
{related_sidebar}
      </div>
    </aside>

  </div>
</div>

<div style="background:linear-gradient(135deg,rgba(22,163,74,0.08),rgba(21,128,61,0.04));border-top:1px solid rgba(22,163,74,0.2);border-bottom:1px solid rgba(22,163,74,0.2);padding:2rem 0;">
  <div class="container">
    <p style="font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#4ade80;margin-bottom:1rem;">More {name} Resources</p>
    <div style="display:flex;flex-wrap:wrap;gap:0.75rem;">
{resource_pills}
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
      <strong>Affiliate Disclosure:</strong> RankerToolAI participates in affiliate programs. When you click links and make a purchase, we may earn a commission at no extra cost to you. This never influences our ratings. <a href="/affiliate-disclosure/" style="color:#9ca3af;">Read full disclosure →</a>
    </div>
    <div class="footer-bottom">
      <span>© 2026 RankerToolAI. All rights reserved.</span>
      <span><a href="/sitemap.xml" style="color:#9ca3af;">Sitemap</a></span>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js"></script>
<script src="/assets/js/cookie-consent.js" defer></script>
<script src="/assets/js/compare-widget.js" defer></script>
</body>
</html>
'''
    outdir = os.path.join(BASE, "review", slug)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote review/{slug}/index.html")

if __name__ == "__main__":
    from review_data import TOOLS
    for t in TOOLS:
        render(t)
