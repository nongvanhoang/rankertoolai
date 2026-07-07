#!/usr/bin/env python3
"""
RankerToolAI — Reddit Auto-Poster
Đăng honest reviews lên các subreddit AI liên quan.

SETUP:
  1. https://www.reddit.com/prefs/apps → Create "script" app
  2. python social_agent/reddit_poster.py config
  3. python social_agent/reddit_poster.py post-all --limit 3

QUAN TRỌNG — Reddit anti-spam:
  - Tài khoản cần karma > 50 trước khi post nhiều subreddit
  - Không post quá 3-4 bài/ngày
  - Đọc rules từng subreddit trước khi post
  - Delay tối thiểu 15 phút giữa các bài
"""

import os, sys, json, time, argparse, urllib.request, urllib.parse, urllib.error, base64
from pathlib import Path
from datetime import datetime, date

SCRIPT_DIR  = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / 'reddit_config.json'
STATE_FILE  = SCRIPT_DIR / 'reddit_posted.json'

SITE = 'https://rankertoolai.com'

# Subreddit mapping: tool slug → list of subreddits to try
SUBREDDITS = {
    'chatgpt':         ['r/ChatGPT', 'r/artificial', 'r/OpenAI'],
    'claude':          ['r/ClaudeAI', 'r/artificial', 'r/AItools'],
    'midjourney':      ['r/midjourney', 'r/AIArt', 'r/artificial'],
    'cursor':          ['r/cursor', 'r/webdev', 'r/programming'],
    'semrush':         ['r/SEO', 'r/bigseo', 'r/digital_marketing'],
    'elevenlabs':      ['r/artificial', 'r/podcasting', 'r/AItools'],
    'github-copilot':  ['r/github', 'r/programming', 'r/webdev'],
    'perplexity':      ['r/perplexity_ai', 'r/artificial', 'r/AItools'],
    'jasper':          ['r/marketing', 'r/copywriting', 'r/content_marketing'],
    'windsurf':        ['r/webdev', 'r/programming', 'r/artificial'],
    'stable-diffusion':['r/StableDiffusion', 'r/AIArt', 'r/artificial'],
    'canva-ai':        ['r/graphic_design', 'r/smallbusiness', 'r/socialmedia'],
    'grok':            ['r/artificial', 'r/technology', 'r/ChatGPT'],
    'runway':          ['r/artificial', 'r/videoproduction', 'r/AItools'],
    'deepseek':        ['r/artificial', 'r/MachineLearning', 'r/ChatGPT'],
    'gemini':          ['r/GoogleGemini', 'r/artificial', 'r/AItools'],
    'notion':          ['r/Notion', 'r/productivity', 'r/selfimprovement'],
    'otter-ai':        ['r/productivity', 'r/remotework', 'r/freelance'],
    'hubspot':         ['r/marketing', 'r/sales', 'r/Entrepreneur'],
    'surfer-seo':      ['r/SEO', 'r/bigseo', 'r/blogging'],
    'writesonic':      ['r/freelance', 'r/blogging', 'r/content_marketing'],
}

TOOLS = [
  {'name':'ChatGPT',       'slug':'chatgpt',        'score':8.8,'tagline':'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo Plus','best_for':'Anyone needing an all-in-one AI','pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs','Browse the web in real-time'],'cons':['Free tier rate-limited fast','Occasionally hallucinates confidently']},
  {'name':'Claude',        'slug':'claude',          'score':9.2,'tagline':'Best AI for writing & reasoning — 200K context, safest frontier model','price':'Free / $20/mo Pro','best_for':'Writers, researchers & devs needing nuanced reasoning','pros':['200K token context window','Best writing quality of any AI','Stronger free tier than ChatGPT'],'cons':['No image generation','Smaller plugin ecosystem']},
  {'name':'Midjourney',    'slug':'midjourney',      'score':9.1,'tagline':'Best AI image generator — stunning quality preferred by designers','price':'From $10/mo','best_for':'Designers, artists & creators','pros':['Best image quality of any AI tool','V6 handles photorealism & art styles','Active creative community'],'cons':['No free tier','Commercial license needs Pro plan']},
  {'name':'Cursor',        'slug':'cursor',          'score':9.2,'tagline':'Best AI code editor that writes code faster than you','price':'Free / $20/mo Pro','best_for':'Developers who want AI to write, debug & refactor code','pros':['Composer writes multi-file code from scratch','Understands your entire codebase','Best autocomplete of any tool'],'cons':['$20/mo for full power','Can suggest outdated patterns']},
  {'name':'Semrush',       'slug':'semrush',         'score':9.1,'tagline':'Most complete SEO and marketing platform powered by AI','price':'Free / $139/mo Pro','best_for':'SEO pros, agencies & businesses','pros':['25B+ keyword database','Best competitor analysis tool','ContentShake AI writes SEO content'],'cons':['Expensive for solopreneurs','Overwhelming for beginners']},
  {'name':'ElevenLabs',    'slug':'elevenlabs',      'score':9.2,'tagline':'Most realistic AI voice generator in 2026','price':'Free / $5/mo Starter','best_for':'Creators, podcasters & marketers','pros':['99 languages, 3,000+ voices','Clone your voice in 1 minute','Lowest latency API'],'cons':['Free: 10K chars/month only','Voice cloning needs audio sample']},
  {'name':'GitHub Copilot','slug':'github-copilot',  'score':9.1,'tagline':'Most-used AI coding assistant — real-time suggestions in every IDE','price':'Free / $10/mo Pro','best_for':'Developers wanting AI inside VS Code, JetBrains','pros':['Works in any editor','FREE for individual developers','Excellent autocomplete quality'],'cons':['Copilot Chat weaker than Cursor','No multi-file editing']},
  {'name':'Perplexity AI', 'slug':'perplexity',      'score':8.8,'tagline':'Best AI for research — real-time answers with cited sources','price':'Free / $20/mo Pro','best_for':'Researchers, journalists & students','pros':['Real-time web search with citations','Pro unlocks GPT-4o & Claude','No ads or tracking'],'cons':['Free tier limited to standard model','Less conversational than ChatGPT']},
  {'name':'Jasper AI',     'slug':'jasper',          'score':8.9,'tagline':'Best AI writing assistant for marketing teams','price':'$39/mo Creator','best_for':'Marketing teams, agencies & brands','pros':['50+ templates for every content type','Brand Voice learns your tone','Integrates with Surfer SEO'],'cons':['Expensive vs alternatives','Can hallucinate facts']},
  {'name':'Windsurf',      'slug':'windsurf',        'score':8.9,'tagline':'Best value AI coding IDE — Cascade agent at $15/mo','price':'Free / $15/mo Pro','best_for':'Developers wanting Cursor-quality at lower price','pros':['Cascade AI agent for multi-file editing','VS Code compatible','$5 cheaper than Cursor'],'cons':['Smaller community than Cursor','Flow credit limits on free plan']},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'tagline':'Best free open-source AI image generator in 2026','price':'Free (self-hosted)','best_for':'Developers & designers wanting unlimited free generation','pros':['100% free and open source','Run locally — unlimited generations','10,000+ community models'],'cons':['Requires technical setup','Needs good GPU for speed']},
  {'name':'Canva AI',      'slug':'canva-ai',        'score':8.7,'tagline':'Best AI design tool for non-designers in 2026','price':'Free / $15/mo Pro','best_for':'Non-designers, small businesses & social media managers','pros':['Magic Design generates full layouts','Dream Lab AI image generation','1M+ templates'],'cons':['AI features require Pro plan','Limited vs Photoshop']},
  {'name':'Grok 3',        'slug':'grok',            'score':8.4,'tagline':"Elon Musk's AI chatbot with real-time X data access",'price':'X Premium $8/mo','best_for':'X/Twitter users needing real-time news','pros':['Real-time X/Twitter data access','No content restrictions','Included with X Premium'],'cons':['Requires X subscription','Smaller knowledge base than GPT-4']},
  {'name':'Runway ML',     'slug':'runway',          'score':9.0,'tagline':'Best AI video generation platform for creators','price':'Free / $15/mo Standard','best_for':'Filmmakers, YouTubers & creators needing AI video','pros':['Gen-3 Alpha highest quality AI video','Text-to-video and image-to-video','AI inpainting & motion brush'],'cons':['Credits run out fast','Render times 1-5 min per clip']},
  {'name':'DeepSeek',      'slug':'deepseek',        'score':9.0,'tagline':'Open-source AI that shocked Silicon Valley — free & GPT-4 quality','price':'Free / API $0.14/M tokens','best_for':'Developers & researchers wanting GPT-4 quality at open-source prices','pros':['100% free to use','Cheapest API: $0.14 per 1M tokens','Matches GPT-4 on benchmarks'],'cons':['Chinese company — data privacy concerns','Occasional refusals on sensitive topics']},
  {'name':'Gemini',        'slug':'gemini',          'score':8.7,'tagline':"Google's AI — best for G-Suite users and real-time search",'price':'Free / $20/mo Advanced','best_for':'Google Workspace users','pros':['Deeply integrated with Google apps','Real-time search access','Most generous free tier'],'cons':['Inconsistent quality vs Claude/ChatGPT','Weaker at creative writing']},
  {'name':'Notion AI',     'slug':'notion',          'score':8.9,'tagline':'AI writing & summarization built into the best productivity workspace','price':'+$10/mo add-on','best_for':'Teams & individuals already using Notion','pros':['AI built directly into your workspace','Summarize, rewrite, translate in 1 click','Best value for Notion users'],'cons':['Requires Notion subscription','Less powerful than standalone tools']},
  {'name':'Otter.ai',      'slug':'otter-ai',        'score':8.7,'tagline':'Best AI meeting assistant — real-time transcription & action items','price':'Free / $16.99/mo Pro','best_for':'Remote workers & teams who hate manual meeting notes','pros':['95%+ transcription accuracy','Auto-generated summaries & action items','Integrates with Zoom & Google Meet'],'cons':['Free: 300 min/month limit','Accuracy drops with heavy accents']},
  {'name':'HubSpot AI',    'slug':'hubspot',         'score':8.2,'tagline':'CRM-native AI — Breeze AI for sales & marketing teams','price':'Free CRM / $20/mo Starter','best_for':'Sales & marketing teams already using HubSpot','pros':['AI has full CRM context','Best-in-class chatbot builder','Free CRM tier included'],'cons':['Full AI suite needs $800+/mo Pro','Overkill for small businesses']},
  {'name':'Surfer SEO',    'slug':'surfer-seo',      'score':9.0,'tagline':'Best AI content optimizer that ranks pages faster','price':'$89/mo Essential','best_for':'Content writers, SEO agencies & bloggers','pros':['Real-time NLP content scoring','Keyword density insights','Integrates with Google Docs & Jasper'],'cons':['Pricey for solopreneurs','NLP suggestions take time to learn']},
  {'name':'Writesonic',    'slug':'writesonic',      'score':8.7,'tagline':'Best budget AI writer with GPT-4 quality output','price':'Free / $16/mo','best_for':'Freelancers & small businesses needing affordable AI writing','pros':['Powered by GPT-4','Chatsonic has real-time web access','Affordable — best value AI writer'],'cons':['Quality inconsistent on long-form','UI feels cluttered']},
]

# ── Config / state ─────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text())
    return {'client_id':'','client_secret':'','username':'','password':'','delay':900,'daily_limit':4}
def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

# ── Reddit OAuth (script flow) ─────────────────────────────────────────────────
def get_token(cfg):
    creds  = base64.b64encode(f'{cfg["client_id"]}:{cfg["client_secret"]}'.encode()).decode()
    body   = urllib.parse.urlencode({'grant_type':'password','username':cfg['username'],'password':cfg['password']}).encode()
    req    = urllib.request.Request(
        'https://www.reddit.com/api/v1/access_token', data=body,
        headers={'Authorization': f'Basic {creds}', 'User-Agent': 'RankerToolAI/1.0 (by u/RankerToolAI)'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    if 'error' in data: raise Exception(f'Reddit auth error: {data}')
    return data['access_token']

def reddit_post(token, subreddit, title, text, url=None, kind='self'):
    sub = subreddit.lstrip('r/')
    body = {
        'sr':        sub,
        'kind':      kind,
        'title':     title[:300],
        'nsfw':      False,
        'spoiler':   False,
        'resubmit':  True,
    }
    if kind == 'self': body['text'] = text
    if kind == 'link': body['url']  = url

    req = urllib.request.Request(
        'https://oauth.reddit.com/api/submit',
        data=urllib.parse.urlencode(body).encode(),
        headers={
            'Authorization': f'Bearer {token}',
            'User-Agent': 'RankerToolAI/1.0 (by u/RankerToolAI)',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# ── Content builder ────────────────────────────────────────────────────────────
def build_reddit_post(tool):
    u = f'{SITE}/review/{tool["slug"]}/'
    title = f'Honest review of {tool["name"]} after testing it for weeks — {tool["score"]}/10. Here\'s what they don\'t tell you.'
    body  = (
        f'I\'ve been using {tool["name"]} for the past few weeks and wanted to share my honest take.\n\n'
        f'**TL;DR: {tool["score"]}/10 — {tool["tagline"]}**\n\n---\n\n'
        f'**What I liked:**\n'
        + '\n'.join(f'- {p}' for p in tool['pros']) +
        f'\n\n**What I didn\'t like:**\n'
        + '\n'.join(f'- {c}' for c in tool['cons']) +
        f'\n\n**Pricing:** {tool["price"]}\n'
        f'**Best for:** {tool["best_for"]}\n\n---\n\n'
        f'Full written review with comparison tables: {u}\n\n'
        f'Happy to answer any questions in the comments.'
    )
    return title, body, u

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_config(args):
    cfg = load_config()
    print('\n  Reddit Config\n')
    def ask(k, lbl):
        v = input(f'  {lbl} [{cfg.get(k,"")}]: ').strip()
        return v or cfg.get(k,'')
    cfg['client_id']     = ask('client_id',    'Client ID (14-char string)')
    cfg['client_secret'] = ask('client_secret','Client Secret')
    cfg['username']      = ask('username',     'Reddit username')
    cfg['password']      = ask('password',     'Reddit password')
    cfg['delay']         = int(ask('delay',    'Delay giữa posts (giây, min 900)') or 900)
    cfg['daily_limit']   = int(ask('daily_limit','Giới hạn posts/ngày (max 4)') or 4)
    save_config(cfg)
    print('  ✓ Config đã lưu\n')
    print('  Test auth:')
    try:
        tok = get_token(cfg)
        print(f'  ✓ Auth OK — token: {tok[:20]}…\n')
    except Exception as e:
        print(f'  ✗ Auth thất bại: {e}\n')

def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool: print(f'  ✗ Slug không hợp lệ: {args.slug}'); sys.exit(1)
    cfg   = load_config()
    token = get_token(cfg)
    subs  = SUBREDDITS.get(tool['slug'], ['r/artificial'])
    sub   = args.subreddit or subs[0]
    title, body, u = build_reddit_post(tool)

    print(f'\n  💬 Posting to {sub}: {tool["name"]}')
    r = reddit_post(token, sub, title, body)
    err = r.get('json',{}).get('errors',[])
    if err: print(f'  ✗ Reddit error: {err}'); return

    post_url = r.get('json',{}).get('data',{}).get('url','')
    print(f'  ✓ Posted: {post_url}')
    state = load_state()
    state.setdefault(tool['slug'], []).append({'posted_at': datetime.now().isoformat(), 'subreddit': sub, 'url': post_url})
    save_state(state)

def cmd_post_all(args):
    cfg   = load_config()
    state = load_state()
    today = date.today().isoformat()
    posted_today = sum(
        1 for posts in state.values() for p in (posts if isinstance(posts, list) else [])
        if p.get('posted_at','').startswith(today)
    )
    quota = min(cfg['daily_limit'], 4) - posted_today
    if quota <= 0: print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} posts/ngày'); return

    unposted = [t for t in TOOLS if not state.get(t['slug'])]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = max(args.delay or cfg['delay'], 900)

    print(f'\n  💬 Reddit Auto-Poster  |  {len(to_post)} posts  |  delay {delay}s ({delay//60}min)')
    print(f'  ⚠ Delay {delay//60} menit antar post để tránh spam filter\n')

    token = get_token(cfg)
    ok = err = 0
    for i, tool in enumerate(to_post):
        subs  = SUBREDDITS.get(tool['slug'], ['r/artificial'])
        sub   = subs[0]
        title, body, u = build_reddit_post(tool)
        print(f'  [{i+1}/{len(to_post)}] 💬 {tool["name"]:<22} → {sub}', end='', flush=True)
        try:
            r    = reddit_post(token, sub, title, body)
            errs = r.get('json',{}).get('errors',[])
            if errs: raise Exception(str(errs))
            post_url = r.get('json',{}).get('data',{}).get('url','')
            print(f' ✓  {post_url}')
            state.setdefault(tool['slug'], []).append({'posted_at': datetime.now().isoformat(), 'subreddit': sub, 'url': post_url})
            save_state(state); ok += 1
        except Exception as e:
            print(f' ✗  {str(e)[:80]}'); err += 1
        if i < len(to_post)-1:
            print(f'  ⏳ Chờ {delay//60} phút…')
            time.sleep(delay)

    print(f'\n  ✓ {ok} thành công  ✗ {err} lỗi\n')

def cmd_status(args):
    state = load_state()
    done  = sum(1 for v in state.values() if v)
    print(f'\n  💬 Reddit Status  |  {done}/{len(TOOLS)} đã post\n')
    for t in TOOLS:
        posts = state.get(t['slug'], [])
        if posts:
            last = posts[-1]
            print(f'  ✓  {t["name"]:<22} {last["posted_at"][:10]}  {last.get("subreddit","")}')
        else:
            print(f'  ○  {t["name"]:<22} chưa post')
    print()

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('config')
    sub.add_parser('status')
    sp = sub.add_parser('post')
    sp.add_argument('--slug', required=True)
    sp.add_argument('--subreddit', default='')
    sa = sub.add_parser('post-all')
    sa.add_argument('--limit', type=int, default=0)
    sa.add_argument('--delay', type=int, default=0)
    args = p.parse_args()
    {'config':cmd_config,'status':cmd_status,'post':cmd_post,'post-all':cmd_post_all}.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
