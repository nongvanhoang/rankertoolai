#!/usr/bin/env python3
"""
RankerToolAI — Medium Auto-Poster
Đăng full AI tool reviews lên Medium qua Integration Token API.

SETUP:
  1. Vào https://medium.com/me/settings → "Integration tokens" → Generate token
  2. python social_agent/medium_poster.py config
  3. python social_agent/medium_poster.py post --slug chatgpt

DÙNG:
  python social_agent/medium_poster.py post-all --limit 3
  python social_agent/medium_poster.py post --slug chatgpt
  python social_agent/medium_poster.py status
"""

import os, sys, json, time, argparse, urllib.request, urllib.parse, urllib.error
from pathlib import Path
from datetime import datetime, date

SCRIPT_DIR  = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / 'medium_config.json'
STATE_FILE  = SCRIPT_DIR / 'medium_posted.json'

SITE = 'https://rankertoolai.com'
API  = 'https://api.medium.com/v1'

TOOLS = [
  {'name':'ChatGPT',        'slug':'chatgpt',         'score':8.8,'tagline':'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo Plus','best_for':'Anyone needing an all-in-one AI for writing, code, and research','pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs','Browse the web in real-time','Most recognized AI brand globally'],'cons':['Free tier rate-limited fast','Occasionally hallucinates confidently','Privacy concerns with data usage'],'tags':['ChatGPT','OpenAI','AITools','ArtificialIntelligence','Productivity']},
  {'name':'Claude',         'slug':'claude',           'score':9.2,'tagline':'Best AI for writing & reasoning — 200K context, safest frontier model','price':'Free / $20/mo Pro','best_for':'Writers, researchers & devs needing nuanced reasoning','pros':['200K token context window','Best writing quality of any AI','Stronger free tier than ChatGPT','No hallucination on facts it knows'],'cons':['No image generation','Smaller plugin ecosystem'],'tags':['Claude','Anthropic','AITools','AIWriting','LLM']},
  {'name':'Midjourney',     'slug':'midjourney',       'score':9.1,'tagline':'Best AI image generator — stunning quality preferred by designers worldwide','price':'From $10/mo','best_for':'Designers, artists & visual creators','pros':['Best image quality of any AI tool','V6 handles photorealism & abstract art','Active community with billions of images','Excellent prompt adherence'],'cons':['No free tier','Commercial license needs Pro plan','Discord-only interface'],'tags':['Midjourney','AIArt','DigitalArt','AITools','ImageGeneration']},
  {'name':'Cursor',         'slug':'cursor',           'score':9.2,'tagline':'Best AI code editor that writes entire features from a single prompt','price':'Free / $20/mo Pro','best_for':'Developers who want AI to write, debug & refactor code','pros':['Composer writes multi-file code from scratch','Understands your entire codebase','Best autocomplete of any tool','Tab prediction for next edit'],'cons':['$20/mo for full power','Can suggest outdated patterns'],'tags':['Cursor','AICoding','Developer','AITools','Programming']},
  {'name':'Semrush',        'slug':'semrush',          'score':9.1,'tagline':'Most complete SEO and marketing platform powered by AI in 2026','price':'Free / $139/mo Pro','best_for':'SEO pros, agencies & businesses needing competitor intelligence','pros':['25B+ keyword database','Best competitor analysis tool','ContentShake AI writes SEO content','Position tracking for 500+ keywords'],'cons':['Expensive for solopreneurs','Overwhelming for beginners'],'tags':['SEO','DigitalMarketing','ContentMarketing','AITools','Semrush']},
  {'name':'ElevenLabs',     'slug':'elevenlabs',       'score':9.2,'tagline':'Most realistic AI voice generator in 2026 — clone any voice in 60 seconds','price':'Free / $5/mo Starter','best_for':'Creators, podcasters & developers','pros':['99 languages, 3,000+ voices','Clone your voice in 1 minute','Lowest latency API for real-time use','Emotion and pacing controls'],'cons':['Free: 10K chars/month only','Voice cloning needs audio sample'],'tags':['AIVoice','TextToSpeech','ContentCreation','AITools','ElevenLabs']},
  {'name':'GitHub Copilot', 'slug':'github-copilot',   'score':9.1,'tagline':'Most-used AI coding assistant — real-time suggestions in every IDE','price':'Free / $10/mo Pro','best_for':'Developers wanting AI inside VS Code, JetBrains, Neovim','pros':['Works in any editor','FREE for individual developers','Excellent autocomplete quality','GitHub integration for code review'],'cons':['Copilot Chat weaker than Cursor','No multi-file editing'],'tags':['GitHubCopilot','AICoding','GitHub','Developer','Programming']},
  {'name':'Perplexity AI',  'slug':'perplexity',       'score':8.8,'tagline':'Best AI for research — real-time answers with cited sources, no hallucinations','price':'Free / $20/mo Pro','best_for':'Researchers, journalists & students','pros':['Real-time web search with citations','Pro unlocks GPT-4o & Claude','No ads or tracking','Spaces for collaborative research'],'cons':['Free tier limited to 5 Pro searches/day','Less conversational than ChatGPT'],'tags':['AISearch','Research','AITools','PerplexityAI','SearchEngine']},
  {'name':'Jasper AI',      'slug':'jasper',           'score':8.9,'tagline':'Best AI writing assistant built for marketing teams and agencies','price':'$39/mo Creator','best_for':'Marketing teams, agencies & brands','pros':['50+ templates for every content type','Brand Voice learns your tone','Integrates with Surfer SEO','Campaigns feature for multi-asset creation'],'cons':['Expensive vs alternatives','Can hallucinate facts'],'tags':['AIWriting','ContentMarketing','MarketingTools','AITools','JasperAI']},
  {'name':'Windsurf',       'slug':'windsurf',         'score':8.9,'tagline':'Best value AI coding IDE — Cascade agent writes entire apps at $15/mo','price':'Free / $15/mo Pro','best_for':'Developers wanting Cursor-quality AI at lower price','pros':['Cascade AI agent for multi-file editing','VS Code compatible — import all extensions','$5 cheaper than Cursor','Codebase-aware from day one'],'cons':['Smaller community than Cursor','Flow credit limits on free plan'],'tags':['AICoding','Developer','CodingTools','AITools','Windsurf']},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'tagline':'Best free open-source AI image generator in 2026 — unlimited generations','price':'Free (self-hosted)','best_for':'Developers & designers wanting unlimited free generation','pros':['100% free and open source','Run locally — unlimited generations','10,000+ community fine-tuned models','Full control over outputs'],'cons':['Requires technical setup','Needs good GPU for speed'],'tags':['StableDiffusion','AIArt','OpenSource','FreeAI','ImageGeneration']},
  {'name':'Canva AI',       'slug':'canva-ai',         'score':8.7,'tagline':'Best AI design tool for non-designers — no Photoshop skills needed','price':'Free / $15/mo Pro','best_for':'Non-designers, small businesses & social media managers','pros':['Magic Design generates full layouts','Dream Lab AI image generation','1M+ templates','Resize for any platform instantly'],'cons':['AI features require Pro plan','Limited vs Photoshop for pros'],'tags':['GraphicDesign','AIDesign','SocialMedia','AITools','CanvaAI']},
  {'name':'Grok 3',         'slug':'grok',             'score':8.4,'tagline':"Elon Musk's AI chatbot — real-time X data, no content restrictions",'price':'X Premium $8/mo','best_for':'X/Twitter power users needing real-time news analysis','pros':['Real-time X/Twitter data access','No content restrictions vs ChatGPT','Included with X Premium subscription'],'cons':['Requires X subscription','Smaller knowledge base than GPT-4'],'tags':['Grok','XAI','AIChat','AITools','ElonMusk']},
  {'name':'Runway ML',      'slug':'runway',           'score':9.0,'tagline':'Best AI video generation platform for filmmakers and creators in 2026','price':'Free / $15/mo Standard','best_for':'Filmmakers, YouTubers & creative agencies','pros':['Gen-3 Alpha highest quality AI video','Text-to-video and image-to-video','AI inpainting & motion brush','Used by major film studios'],'cons':['Credits run out fast','Render times 1-5 min per clip'],'tags':['AIVideo','VideoCreation','ContentCreator','AITools','RunwayML']},
  {'name':'DeepSeek',       'slug':'deepseek',         'score':9.0,'tagline':'Open-source AI that shocked Silicon Valley — free & GPT-4 quality','price':'Free / API $0.14/M tokens','best_for':'Developers & researchers wanting GPT-4 quality completely free','pros':['100% free to use via web','Cheapest API: $0.14 per 1M tokens','Matches GPT-4 on coding benchmarks','Open weights available'],'cons':['Chinese company — data privacy concerns','Occasional refusals on sensitive topics'],'tags':['DeepSeek','OpenSource','FreeAI','AITools','LLM']},
  {'name':'Gemini',         'slug':'gemini',           'score':8.7,'tagline':"Google's most capable AI — best for G-Suite and real-time search",'price':'Free / $20/mo Advanced','best_for':'Google Workspace users and students','pros':['Deeply integrated with Google apps','Real-time search access','Most generous free tier of any major AI','Multimodal from day one'],'cons':['Inconsistent quality vs Claude/ChatGPT','Weaker at creative writing'],'tags':['Gemini','GoogleAI','AITools','Productivity','GoogleWorkspace']},
  {'name':'Notion AI',      'slug':'notion',           'score':8.9,'tagline':'AI writing & summarization built into the best productivity workspace','price':'+$10/mo add-on','best_for':'Teams & individuals already using Notion','pros':['AI built directly into your workspace','Summarize, rewrite, translate in 1 click','Best value for existing Notion users','Q&A across all your notes'],'cons':['Requires Notion subscription','Less powerful than standalone tools'],'tags':['NotionAI','Productivity','PKM','WorkSmarter','AITools']},
  {'name':'Otter.ai',       'slug':'otter-ai',         'score':8.7,'tagline':'Best AI meeting assistant — real-time transcription, summaries & action items','price':'Free / $16.99/mo Pro','best_for':'Remote workers, managers & teams','pros':['95%+ transcription accuracy in English','Auto-generated summaries & action items','Integrates with Zoom, Teams & Google Meet','Speaker identification'],'cons':['Free: 300 min/month limit','Accuracy drops with heavy accents'],'tags':['MeetingNotes','Transcription','RemoteWork','Productivity','OtterAI']},
  {'name':'HubSpot AI',     'slug':'hubspot',          'score':8.2,'tagline':'CRM-native AI — Breeze AI for sales & marketing teams in 2026','price':'Free CRM / $20/mo Starter','best_for':'Sales & marketing teams using HubSpot CRM','pros':['AI has full CRM context','Best-in-class chatbot builder','Free CRM tier included','Breeze AI across all hubs'],'cons':['Full AI suite needs $800+/mo','Overkill for small businesses'],'tags':['HubSpot','CRM','MarketingAI','SalesTools','B2BSaaS']},
  {'name':'Surfer SEO',     'slug':'surfer-seo',       'score':9.0,'tagline':'Best AI content optimizer that consistently ranks pages faster','price':'$89/mo Essential','best_for':'Content writers, SEO agencies & bloggers','pros':['Real-time NLP content scoring','Keyword density & structure insights','Google Docs & Jasper integration','SERP Analyzer built-in'],'cons':['Pricey for solopreneurs at $89/mo','NLP suggestions take time to learn'],'tags':['SEO','ContentMarketing','Blogging','AITools','SurferSEO']},
  {'name':'Writesonic',     'slug':'writesonic',       'score':8.7,'tagline':'Best budget AI writer with GPT-4 quality — $16/mo for unlimited words','price':'Free / $16/mo','best_for':'Freelancers & small businesses needing affordable AI writing','pros':['Powered by GPT-4 & Claude','Real-time web access for research','Best value AI writer under $20/mo','Chatsonic for conversational AI'],'cons':['Quality inconsistent on long-form','UI feels cluttered vs Jasper'],'tags':['AIWriting','ContentCreation','Freelance','AITools','Writesonic']},
]

# ── Config / state ─────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text())
    return {'token':'','delay':300,'daily_limit':5,'user_id':'','username':''}
def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

# ── API helpers ────────────────────────────────────────────────────────────────
def med_get(path, token):
    req = urllib.request.Request(f'{API}{path}',
        headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r: return json.loads(r.read())

def med_post(path, body, token):
    req = urllib.request.Request(f'{API}{path}',
        data=json.dumps(body).encode(),
        headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

# ── Article builder ────────────────────────────────────────────────────────────
def build_article(tool):
    u    = f'{SITE}/review/{tool["slug"]}/'
    pros = '\n'.join(f'- **{p}**' for p in tool['pros'])
    cons = '\n'.join(f'- {c}' for c in tool['cons'])
    tags = ', '.join(f'`{t}`' for t in tool['tags'][:5])

    content = f"""# {tool['name']} Review 2026: {tool['score']}/10 — Is It Worth It?

> **TL;DR**: {tool['tagline']}. Best for {tool['best_for']}. Pricing: {tool['price']}.

After spending several weeks testing {tool['name']} across real-world use cases, here's my comprehensive, no-BS review.

## Quick Verdict: {tool['score']}/10

{'⭐ Excellent — one of the best tools in its category.' if tool['score'] >= 9.0 else '✅ Very Good — solid choice for most users.' if tool['score'] >= 8.5 else '👍 Good — worth it for the right audience.'}

---

## What Is {tool['name']}?

{tool['name']} is {tool['tagline'].lower()}. It's designed primarily for {tool['best_for']}, and pricing starts at **{tool['price']}**.

## What {tool['name']} Does Best

{pros}

## Where {tool['name']} Falls Short

{cons}

## Who Should Use {tool['name']}?

**Perfect for:** {tool['best_for']}

If you match this profile, {tool['name']} is likely worth it at {tool['price']}.

## Pricing Breakdown

**{tool['price']}**

{'The free tier is genuinely useful for getting started.' if 'Free' in tool['price'] else 'There is no free tier, so make sure to use a trial period.'}

## Final Score: {tool['score']}/10

{tool['name']} earns a **{tool['score']}/10** in my testing. {'It consistently outperforms alternatives in its category.' if tool['score'] >= 9.0 else 'It\'s a strong performer with a few areas for improvement.' if tool['score'] >= 8.5 else 'It does what it promises, though there are some notable limitations.'}

---

*For a full comparison including alternatives and a side-by-side breakdown, read my complete review on [RankerToolAI]({u})*

Tags: {tags}
"""
    return content

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_config(args):
    cfg = load_config()
    print('\n  Medium Config\n')
    print('  Cách lấy Integration Token:')
    print('  1. Vào https://medium.com/me/settings')
    print('  2. Kéo xuống "Integration tokens"')
    print('  3. Gõ tên token (vd: "RankerToolAI") → Generate\n')
    def ask(k,l,d=''): v=input(f'  {l} [{cfg.get(k,d)}]: ').strip(); return v or cfg.get(k,d)
    cfg['token']       = ask('token','Integration Token')
    cfg['delay']       = int(ask('delay','Delay giữa posts (giây)','300') or 300)
    cfg['daily_limit'] = int(ask('daily_limit','Posts/ngày max','5') or 5)
    # Auto-fetch user info
    if cfg['token']:
        try:
            r = med_get('/me', cfg['token'])
            cfg['user_id']  = r['data']['id']
            cfg['username'] = r['data']['username']
            print(f'  ✓ Logged in: @{cfg["username"]} (id: {cfg["user_id"]})')
        except Exception as e:
            print(f'  ✗ Could not verify token: {e}')
    save_config(cfg); print('  ✓ Saved\n')

def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool: print(f'  ✗ Slug không hợp lệ: {args.slug}'); sys.exit(1)
    cfg   = load_config()
    if not cfg.get('token'): print('  ✗ Token chưa set. Chạy: python medium_poster.py config'); sys.exit(1)
    if not cfg.get('user_id'):
        try:
            r = med_get('/me', cfg['token'])
            cfg['user_id'] = r['data']['id']
            save_config(cfg)
        except Exception as e:
            print(f'  ✗ Token invalid: {e}'); sys.exit(1)

    content = build_article(tool)
    title   = f'{tool["name"]} Review 2026: {tool["score"]}/10 — {tool["tagline"]}'
    body    = {
        'title':         title,
        'contentFormat': 'markdown',
        'content':       content,
        'tags':          tool['tags'][:5],
        'publishStatus': 'public',
        'canonicalUrl':  f'{SITE}/review/{tool["slug"]}/',
        'notifyFollowers': True,
    }

    print(f'\n  📝 Publishing to Medium: {tool["name"]}')
    try:
        r   = med_post(f'/users/{cfg["user_id"]}/posts', body, cfg['token'])
        url = r['data']['url']
        print(f'  ✓ Published: {url}')
        state = load_state()
        state[tool['slug']] = {'posted_at': datetime.now().isoformat(), 'url': url, 'title': title}
        save_state(state)
    except urllib.error.HTTPError as e:
        print(f'  ✗ {e.code}: {e.read().decode()[:200]}')

def cmd_post_all(args):
    cfg   = load_config()
    if not cfg.get('token'): print('  ✗ Chạy: python medium_poster.py config'); return
    if not cfg.get('user_id'):
        try:
            r = med_get('/me', cfg['token']); cfg['user_id'] = r['data']['id']; save_config(cfg)
        except Exception as e:
            print(f'  ✗ Token invalid: {e}'); return

    state = load_state()
    today = date.today().isoformat()
    posted_today = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))
    quota = cfg['daily_limit'] - posted_today
    if quota <= 0: print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} posts/ngày'); return

    unposted = [t for t in TOOLS if t['slug'] not in state]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = args.delay or cfg['delay']

    print(f'\n  📝 Medium Auto-Poster  |  {len(to_post)} articles  |  delay {delay}s\n')
    ok = err = 0
    for i, tool in enumerate(to_post):
        print(f'  [{i+1}/{len(to_post)}] {tool["name"]:<22}', end='', flush=True)
        content = build_article(tool)
        title   = f'{tool["name"]} Review 2026: {tool["score"]}/10 — {tool["tagline"]}'
        body    = {'title':title,'contentFormat':'markdown','content':content,
                   'tags':tool['tags'][:5],'publishStatus':'public',
                   'canonicalUrl':f'{SITE}/review/{tool["slug"]}/','notifyFollowers':True}
        try:
            r   = med_post(f'/users/{cfg["user_id"]}/posts', body, cfg['token'])
            url = r['data']['url']
            print(f' ✓  {url}')
            state[tool['slug']] = {'posted_at':datetime.now().isoformat(),'url':url,'title':title}
            save_state(state); ok += 1
        except urllib.error.HTTPError as e:
            print(f' ✗  {e.code}: {e.read().decode()[:80]}'); err += 1
            if e.code == 429: print('  ⚠ Rate limited — chờ 30 phút…'); time.sleep(1800); continue
        if i < len(to_post)-1: time.sleep(delay)
    print(f'\n  ✓ {ok} thành công  ✗ {err} lỗi\n')

def cmd_status(args):
    state = load_state()
    print(f'\n  📝 Medium Status  |  {len(state)}/{len(TOOLS)} đã publish\n')
    for t in TOOLS:
        info = state.get(t['slug'])
        mark = f"✓  {info['posted_at'][:10]}  {info.get('url','')}" if info else '○  chưa post'
        print(f'  {"✓" if info else "○"}  {t["name"]:<22} {info["posted_at"][:10] if info else "chưa post"}')
    print()

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('config'); sub.add_parser('status')
    sp = sub.add_parser('post'); sp.add_argument('--slug', required=True)
    sa = sub.add_parser('post-all')
    sa.add_argument('--limit', type=int, default=0)
    sa.add_argument('--delay', type=int, default=0)
    args = p.parse_args()
    {'config':cmd_config,'status':cmd_status,'post':cmd_post,'post-all':cmd_post_all}.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
