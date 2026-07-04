#!/usr/bin/env python3
"""
RankerToolAI — Twitter/X Auto-Poster
Tự động tweet review 21 AI tools lên Twitter/X qua API v2.

SETUP:
  1. https://developer.x.com/en/portal/apps → Create app (Free tier)
  2. Lấy: API Key, API Secret, Access Token, Access Token Secret
  3. python social_agent/twitter_poster.py config
  4. python social_agent/twitter_poster.py post-all

DÙNG:
  python social_agent/twitter_poster.py post-all --limit 5
  python social_agent/twitter_poster.py post --slug chatgpt
  python social_agent/twitter_poster.py status
"""

import os, sys, json, time, hmac, hashlib, base64, random, string, argparse
import urllib.request, urllib.parse, urllib.error
from pathlib import Path
from datetime import datetime, date

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / 'twitter_config.json'
STATE_FILE  = SCRIPT_DIR / 'twitter_posted.json'

SITE = 'https://rankertoolai.com'
API  = 'https://api.twitter.com/2'

TOOLS = [
  {'name':'ChatGPT',       'slug':'chatgpt',        'score':8.8,'pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs'],'cons':['Free tier rate-limited fast'],'tags':['#ChatGPT','#OpenAI','#AITools'],'price':'Free / $20/mo'},
  {'name':'Claude',        'slug':'claude',          'score':9.2,'pros':['200K token context window','Best writing quality of any AI'],'cons':['No image generation'],'tags':['#Claude','#Anthropic','#AITools'],'price':'Free / $20/mo'},
  {'name':'Midjourney',    'slug':'midjourney',      'score':9.1,'pros':['Best image quality','V6 photorealism & art styles'],'cons':['No free tier'],'tags':['#Midjourney','#AIArt','#AITools'],'price':'From $10/mo'},
  {'name':'Cursor',        'slug':'cursor',          'score':9.2,'pros':['Writes multi-file code from scratch','Understands entire codebase'],'cons':['$20/mo for full power'],'tags':['#Cursor','#AICoding','#AITools'],'price':'Free / $20/mo'},
  {'name':'Semrush',       'slug':'semrush',         'score':9.1,'pros':['25B+ keyword database','Best competitor analysis'],'cons':['Expensive for solopreneurs'],'tags':['#Semrush','#SEO','#AITools'],'price':'Free / $139/mo'},
  {'name':'ElevenLabs',    'slug':'elevenlabs',      'score':9.2,'pros':['99 languages, 3,000+ voices','Clone voice in 1 minute'],'cons':['Free: 10K chars/month only'],'tags':['#ElevenLabs','#AIVoice','#AITools'],'price':'Free / $5/mo'},
  {'name':'GitHub Copilot','slug':'github-copilot',  'score':9.1,'pros':['Works in any editor','FREE for individuals'],'cons':['No multi-file editing'],'tags':['#GitHubCopilot','#AICoding','#AITools'],'price':'Free / $10/mo'},
  {'name':'Perplexity AI', 'slug':'perplexity',      'score':8.8,'pros':['Real-time search with citations','No ads or tracking'],'cons':['Free tier limited'],'tags':['#PerplexityAI','#AISearch','#AITools'],'price':'Free / $20/mo'},
  {'name':'Jasper AI',     'slug':'jasper',          'score':8.9,'pros':['50+ templates','Brand Voice feature'],'cons':['Expensive vs alternatives'],'tags':['#JasperAI','#AIWriting','#AITools'],'price':'$39/mo'},
  {'name':'Windsurf',      'slug':'windsurf',        'score':8.9,'pros':['Cascade AI multi-file editing','$5 cheaper than Cursor'],'cons':['Smaller community'],'tags':['#Windsurf','#AICoding','#AITools'],'price':'Free / $15/mo'},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'pros':['100% free & open source','10,000+ community models'],'cons':['Requires technical setup'],'tags':['#StableDiffusion','#AIArt','#FreeAI'],'price':'Free'},
  {'name':'Canva AI',      'slug':'canva-ai',        'score':8.7,'pros':['Magic Design generates layouts','1M+ templates'],'cons':['AI needs Pro plan'],'tags':['#CanvaAI','#AIDesign','#AITools'],'price':'Free / $15/mo'},
  {'name':'Grok 3',        'slug':'grok',            'score':8.4,'pros':['Real-time X data access','No content restrictions'],'cons':['Requires X subscription'],'tags':['#Grok','#XAI','#AITools'],'price':'X Premium $8/mo'},
  {'name':'Runway ML',     'slug':'runway',          'score':9.0,'pros':['Gen-3 Alpha best AI video','Text-to-video & image-to-video'],'cons':['Credits run out fast'],'tags':['#RunwayML','#AIVideo','#AITools'],'price':'Free / $15/mo'},
  {'name':'DeepSeek',      'slug':'deepseek',        'score':9.0,'pros':['100% free to use','$0.14/M tokens API'],'cons':['Data privacy concerns'],'tags':['#DeepSeek','#OpenSource','#FreeAI'],'price':'Free'},
  {'name':'Gemini',        'slug':'gemini',          'score':8.7,'pros':['Integrated with Google apps','Real-time search'],'cons':['Inconsistent vs Claude/ChatGPT'],'tags':['#Gemini','#GoogleAI','#AITools'],'price':'Free / $20/mo'},
  {'name':'Notion AI',     'slug':'notion',          'score':8.9,'pros':['AI in your workspace','Summarize in 1 click'],'cons':['Requires Notion subscription'],'tags':['#NotionAI','#Productivity','#AITools'],'price':'+$10/mo'},
  {'name':'Otter.ai',      'slug':'otter-ai',        'score':8.7,'pros':['95%+ transcription accuracy','Auto summaries & action items'],'cons':['300 min/month free limit'],'tags':['#OtterAI','#Transcription','#Productivity'],'price':'Free / $16.99/mo'},
  {'name':'HubSpot AI',    'slug':'hubspot',         'score':8.2,'pros':['Full CRM context','Best chatbot builder'],'cons':['$800+/mo for full AI suite'],'tags':['#HubSpot','#CRM','#MarketingAI'],'price':'Free CRM / $20/mo'},
  {'name':'Surfer SEO',    'slug':'surfer-seo',      'score':9.0,'pros':['Real-time NLP scoring','Google Docs integration'],'cons':['Pricey for solopreneurs'],'tags':['#SurferSEO','#SEO','#ContentMarketing'],'price':'$89/mo'},
  {'name':'Writesonic',    'slug':'writesonic',      'score':8.7,'pros':['Powered by GPT-4','Real-time web access'],'cons':['Inconsistent on long-form'],'tags':['#Writesonic','#AIWriting','#AITools'],'price':'Free / $16/mo'},
]

# ── OAuth 1.0a ─────────────────────────────────────────────────────────────────
def _oauth_header(method, url, body_params, cfg):
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    ts    = str(int(time.time()))
    oauth = {
        'oauth_consumer_key':     cfg['api_key'],
        'oauth_nonce':            nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp':        ts,
        'oauth_token':            cfg['access_token'],
        'oauth_version':          '1.0',
    }
    all_params = {**body_params, **oauth}
    enc = lambda s: urllib.parse.quote(str(s), safe='')
    param_str = '&'.join(f'{enc(k)}={enc(v)}' for k, v in sorted(all_params.items()))
    base      = f'{method}&{enc(url)}&{enc(param_str)}'
    sign_key  = f'{enc(cfg["api_secret"])}&{enc(cfg["access_token_secret"])}'
    sig       = base64.b64encode(hmac.new(sign_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    oauth['oauth_signature'] = sig
    header = 'OAuth ' + ', '.join(f'{enc(k)}="{enc(v)}"' for k, v in sorted(oauth.items()))
    return header

# ── Config / state ─────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {'api_key':'','api_secret':'','access_token':'','access_token_secret':'','delay':60,'daily_limit':15}

def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

# ── Tweet variants ─────────────────────────────────────────────────────────────
def build_tweets(tool):
    u = f'{SITE}/review/{tool["slug"]}/'
    t1 = (
        f'{tool["name"]} honest review ({tool["score"]}/10):\n\n'
        f'+ {tool["pros"][0]}\n+ {tool["pros"][1]}\n- {tool["cons"][0]}\n\n'
        f'Price: {tool["price"]}\n\n{u}'
    )[:280]
    t2 = (
        f'Hot take: {tool["name"]} '
        f'{"is genuinely worth it" if tool["score"] >= 9 else "is underrated in 2026"}\n\n'
        f'Pro: {tool["pros"][0]}\nCon: {tool["cons"][0]}\n\n'
        f'{" ".join(tool["tags"][:2])}\n{u}'
    )[:280]
    t3 = (
        f'Just published: {tool["name"]} Review 2026\n'
        f'Score: {tool["score"]}/10\n\n'
        f'{" ".join(tool["tags"][:3])}\n\n{u}'
    )[:280]
    return [t1, t2, t3]

# ── API call ───────────────────────────────────────────────────────────────────
def post_tweet(text, cfg):
    url  = f'{API}/tweets'
    body = json.dumps({'text': text}).encode()
    auth = _oauth_header('POST', url, {}, cfg)
    req  = urllib.request.Request(
        url, data=body,
        headers={'Authorization': auth, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_config(args):
    cfg = load_config()
    print('\n  Twitter/X Config (Enter = giữ nguyên)\n')
    def ask(k, lbl):
        v = input(f'  {lbl} [{cfg.get(k,"")}]: ').strip()
        return v or cfg.get(k, '')
    cfg['api_key']              = ask('api_key',              'API Key (Consumer Key)')
    cfg['api_secret']           = ask('api_secret',           'API Secret')
    cfg['access_token']         = ask('access_token',         'Access Token')
    cfg['access_token_secret']  = ask('access_token_secret',  'Access Token Secret')
    cfg['delay']                = int(ask('delay',            'Delay giữa tweets (giây)') or 60)
    cfg['daily_limit']          = int(ask('daily_limit',      'Giới hạn tweets/ngày') or 15)
    save_config(cfg)
    print('  ✓ Config đã lưu\n')

def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool: print(f'  ✗ Slug không hợp lệ: {args.slug}'); sys.exit(1)
    cfg   = load_config()
    state = load_state()
    tweets = build_tweets(tool)
    # Pick variant (rotate: 0→1→2→0…)
    existing = state.get(tool['slug'], {})
    variant  = existing.get('variant', 0)
    text     = tweets[variant % len(tweets)]

    print(f'\n  🐦 Tweeting: {tool["name"]}')
    print(f'  Tweet:\n  {text[:100]}…\n')
    try:
        r = post_tweet(text, cfg)
        tid = r.get('data', {}).get('id', '')
        url = f'https://twitter.com/i/web/status/{tid}'
        print(f'  ✓ Posted: {url}')
        state[tool['slug']] = {'posted_at': datetime.now().isoformat(), 'tweet_id': tid, 'url': url, 'variant': (variant+1) % len(tweets)}
        save_state(state)
    except urllib.error.HTTPError as e:
        print(f'  ✗ HTTP {e.code}: {e.read().decode()[:150]}')
        raise

def cmd_post_all(args):
    cfg   = load_config()
    state = load_state()
    today = date.today().isoformat()
    posted_today = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))
    quota = cfg['daily_limit'] - posted_today
    if quota <= 0:
        print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} tweets/ngày'); return

    unposted = [t for t in TOOLS if t['slug'] not in state]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = args.delay or cfg['delay']

    print(f'\n  🐦 Twitter Auto-Poster  |  {len(to_post)} tweets  |  delay {delay}s')
    ok = err = 0
    for i, tool in enumerate(to_post):
        print(f'  [{i+1}/{len(to_post)}] {tool["name"]:<22}', end='', flush=True)
        tweets  = build_tweets(tool)
        variant = state.get(tool['slug'], {}).get('variant', 0)
        try:
            r   = post_tweet(tweets[variant % len(tweets)], cfg)
            tid = r.get('data', {}).get('id', '')
            print(f' ✓  https://twitter.com/i/web/status/{tid}')
            state[tool['slug']] = {'posted_at': datetime.now().isoformat(), 'tweet_id': tid, 'variant': (variant+1) % len(tweets)}
            save_state(state); ok += 1
        except urllib.error.HTTPError as e:
            print(f' ✗  {e.code}: {e.read().decode()[:60]}'); err += 1
            if e.code == 429: print('  ⚠ Rate limited — chờ 15 phút…'); time.sleep(900); continue
        if i < len(to_post)-1: time.sleep(delay)

    print(f'\n  ✓ {ok} thành công  ✗ {err} lỗi\n')

def cmd_status(args):
    state = load_state()
    print(f'\n  🐦 Twitter Status  |  {len(state)}/{len(TOOLS)} đã tweet\n')
    for t in TOOLS:
        info = state.get(t['slug'])
        mark = f"✓  {info['posted_at'][:10]}" if info else '○  chưa post'
        print(f'  {mark}  {t["name"]}')
    print()

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('config')
    sub.add_parser('status')
    sp = sub.add_parser('post'); sp.add_argument('--slug', required=True)
    sa = sub.add_parser('post-all')
    sa.add_argument('--limit', type=int, default=0)
    sa.add_argument('--delay', type=int, default=0)
    args = p.parse_args()
    {'config':cmd_config,'status':cmd_status,'post':cmd_post,'post-all':cmd_post_all}.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
