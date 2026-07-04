#!/usr/bin/env python3
"""
RankerToolAI — Threads Auto-Poster
Đăng AI tool reviews lên Threads (Meta) qua Threads API v1.0.

SETUP:
  1. Vào https://developers.facebook.com → Create App → Consumer
  2. Add product: Threads API
  3. Settings → Basic → App ID + App Secret
  4. python social_agent/threads_poster.py auth
  5. python social_agent/threads_poster.py post-all

DÙNG:
  python social_agent/threads_poster.py post-all --limit 5
  python social_agent/threads_poster.py post --slug chatgpt
  python social_agent/threads_poster.py status
"""

import os, sys, json, time, argparse, webbrowser, urllib.request, urllib.parse, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, date
from threading import Thread, Event

SCRIPT_DIR  = Path(__file__).resolve().parent
TOKEN_FILE  = SCRIPT_DIR / 'threads_tokens.json'
CONFIG_FILE = SCRIPT_DIR / 'threads_config.json'
STATE_FILE  = SCRIPT_DIR / 'threads_posted.json'

SITE         = 'https://rankertoolai.com'
API          = 'https://graph.threads.net/v1.0'
REDIRECT_URI = 'http://localhost:8767/callback'
SCOPES       = 'threads_basic,threads_content_publish'

TOOLS = [
  {'name':'ChatGPT',        'slug':'chatgpt',         'score':8.8,'tagline':'Most versatile AI — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo','tags':['ChatGPT','OpenAI','AI','AITools']},
  {'name':'Claude',         'slug':'claude',           'score':9.2,'tagline':'Best AI for writing — 200K context, most honest frontier model','price':'Free / $20/mo','tags':['Claude','Anthropic','AI','AIWriting']},
  {'name':'Midjourney',     'slug':'midjourney',       'score':9.1,'tagline':'Best AI image generator — studio-quality art in seconds','price':'From $10/mo','tags':['Midjourney','AIArt','ImageGeneration','AITools']},
  {'name':'Cursor',         'slug':'cursor',           'score':9.2,'tagline':'Best AI code editor — writes entire features from 1 prompt','price':'Free / $20/mo','tags':['Cursor','AICoding','Developer','Programming']},
  {'name':'Semrush',        'slug':'semrush',          'score':9.1,'tagline':'Most complete SEO platform — 25B+ keywords, AI content writer','price':'Free / $139/mo','tags':['SEO','Semrush','DigitalMarketing','ContentMarketing']},
  {'name':'ElevenLabs',     'slug':'elevenlabs',       'score':9.2,'tagline':'Most realistic AI voice — clone any voice in 60 seconds','price':'Free / $5/mo','tags':['ElevenLabs','AIVoice','TextToSpeech','ContentCreation']},
  {'name':'GitHub Copilot', 'slug':'github-copilot',   'score':9.1,'tagline':'Most-used AI coding assistant — free for individuals','price':'Free / $10/mo','tags':['GitHubCopilot','AICoding','GitHub','Developer']},
  {'name':'Perplexity AI',  'slug':'perplexity',       'score':8.8,'tagline':'Best AI search — real-time answers with cited sources','price':'Free / $20/mo','tags':['PerplexityAI','AISearch','Research','AI']},
  {'name':'Jasper AI',      'slug':'jasper',           'score':8.9,'tagline':'Best AI writer for marketing teams — Brand Voice + 50 templates','price':'$39/mo','tags':['JasperAI','AIWriting','ContentMarketing','MarketingTools']},
  {'name':'Windsurf',       'slug':'windsurf',         'score':8.9,'tagline':'Best value AI IDE — Cursor quality at $15/mo','price':'Free / $15/mo','tags':['Windsurf','AICoding','Developer','AITools']},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'tagline':'Best FREE image AI — unlimited generations, open source','price':'Free','tags':['StableDiffusion','AIArt','OpenSource','FreeAI']},
  {'name':'Canva AI',       'slug':'canva-ai',         'score':8.7,'tagline':'Best AI design tool for non-designers — 1M+ templates','price':'Free / $15/mo','tags':['CanvaAI','GraphicDesign','AIDesign','SocialMedia']},
  {'name':'Grok 3',         'slug':'grok',             'score':8.4,'tagline':"Elon Musk's AI — real-time X data, no content limits",'price':'X Premium $8/mo','tags':['Grok','XAI','AIChat','AITools']},
  {'name':'Runway ML',      'slug':'runway',           'score':9.0,'tagline':'Best AI video generator — Gen-3 Alpha for filmmakers','price':'Free / $15/mo','tags':['RunwayML','AIVideo','VideoCreation','ContentCreator']},
  {'name':'DeepSeek',       'slug':'deepseek',         'score':9.0,'tagline':'Open-source AI that beat GPT-4 — 100% free to use','price':'Free','tags':['DeepSeek','OpenSource','FreeAI','LLM']},
  {'name':'Gemini',         'slug':'gemini',           'score':8.7,'tagline':"Google's AI — best for G-Suite + real-time search",'price':'Free / $20/mo','tags':['Gemini','GoogleAI','AITools','Productivity']},
  {'name':'Notion AI',      'slug':'notion',           'score':8.9,'tagline':'AI inside the best workspace — summarize anything in 1 click','price':'+$10/mo','tags':['NotionAI','Productivity','PKM','WorkSmarter']},
  {'name':'Otter.ai',       'slug':'otter-ai',         'score':8.7,'tagline':'Best AI meeting notes — 95% accuracy, auto action items','price':'Free / $16.99/mo','tags':['OtterAI','Transcription','MeetingNotes','RemoteWork']},
  {'name':'HubSpot AI',     'slug':'hubspot',          'score':8.2,'tagline':'CRM-native AI — Breeze AI for sales & marketing','price':'Free CRM / $20/mo','tags':['HubSpot','CRM','MarketingAI','B2B']},
  {'name':'Surfer SEO',     'slug':'surfer-seo',       'score':9.0,'tagline':'Best SEO content optimizer — ranks pages consistently faster','price':'$89/mo','tags':['SurferSEO','SEO','ContentMarketing','Blogging']},
  {'name':'Writesonic',     'slug':'writesonic',       'score':8.7,'tagline':'Best budget AI writer — GPT-4 quality at $16/mo','price':'Free / $16/mo','tags':['Writesonic','AIWriting','ContentCreation','Freelance']},
]

# ── OAuth callback ─────────────────────────────────────────────────────────────
_code, _evt = None, Event()

class _CB(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        global _code
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in q:
            _code = q['code'][0]
            self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers()
            self.wfile.write(b'<h2>Threads authorised! You can close this tab.</h2><script>window.close()</script>')
        else:
            self.send_response(400); self.end_headers()
        _evt.set()

def load_config():
    if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text())
    return {'app_id':'','app_secret':'','delay':60,'daily_limit':10}
def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_tokens():
    if TOKEN_FILE.exists(): return json.loads(TOKEN_FILE.read_text())
    return {}
def save_tokens(t): TOKEN_FILE.write_text(json.dumps(t, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

def get_token():
    tok = load_tokens()
    if not tok: print('  ✗ Chưa auth. Chạy: python threads_poster.py auth'); sys.exit(1)
    return tok['access_token'], tok.get('user_id','')

# ── Post builder ───────────────────────────────────────────────────────────────
def build_thread(tool):
    u    = f'{SITE}/review/{tool["slug"]}/'
    tags = ' '.join(f'#{t}' for t in tool['tags'][:3])
    text = (
        f'{tool["name"]} — {tool["score"]}/10\n\n'
        f'{tool["tagline"]}\n\n'
        f'Price: {tool["price"]}\n\n'
        f'Full review: {u}\n\n'
        f'{tags} #AITools #TechReview'
    )
    return text[:500]

# ── Threads API ────────────────────────────────────────────────────────────────
def threads_post(path, params, token):
    params['access_token'] = token
    data = urllib.parse.urlencode(params).encode()
    req  = urllib.request.Request(f'{API}{path}', data=data, method='POST',
        headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def publish_text(user_id, token, text):
    # Step 1: create container
    r1 = threads_post(f'/{user_id}/threads', {
        'media_type': 'TEXT',
        'text':       text,
    }, token)
    creation_id = r1.get('id','')
    if not creation_id: raise ValueError(f'No creation_id: {r1}')
    time.sleep(3)

    # Step 2: publish
    r2 = threads_post(f'/{user_id}/threads/publish', {
        'creation_id': creation_id,
    }, token)
    return r2.get('id','')

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_auth(args):
    cfg = load_config()
    if not cfg['app_id']:
        print('\n  Threads App Credentials:')
        print('  Tạo tại: https://developers.facebook.com → Apps → Create → Consumer')
        print('  Sau đó add product: Threads API\n')
        cfg['app_id']     = input('  App ID    : ').strip()
        cfg['app_secret'] = input('  App Secret: ').strip()
        save_config(cfg)

    auth_url = (
        f'https://threads.net/oauth/authorize'
        f'?client_id={cfg["app_id"]}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&scope={urllib.parse.quote(SCOPES)}'
        f'&response_type=code'
    )
    print(f'\n  Opening browser for Threads authorization…')
    srv = HTTPServer(('localhost', 8767), _CB)
    Thread(target=srv.serve_forever, daemon=True).start()
    webbrowser.open(auth_url)
    print('  Waiting for callback…')
    _evt.wait(120); srv.shutdown()

    if not _code: print('  ✗ Timeout'); sys.exit(1)

    # Exchange code for short-lived token
    body = urllib.parse.urlencode({
        'client_id':     cfg['app_id'],
        'client_secret': cfg['app_secret'],
        'grant_type':    'authorization_code',
        'redirect_uri':  REDIRECT_URI,
        'code':          _code,
    }).encode()
    req = urllib.request.Request('https://graph.threads.net/oauth/access_token', data=body,
        headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=30) as r:
        short = json.loads(r.read())
    short_token = short['access_token']
    user_id     = str(short['user_id'])

    # Exchange for long-lived token (60 days)
    params = urllib.parse.urlencode({
        'grant_type':        'th_exchange_token',
        'client_secret':     cfg['app_secret'],
        'access_token':      short_token,
    })
    req2 = urllib.request.Request(f'{API}/access_token?{params}')
    with urllib.request.urlopen(req2, timeout=30) as r:
        long = json.loads(r.read())
    long_token = long.get('access_token', short_token)

    save_tokens({'access_token':long_token,'user_id':user_id,
                 'expires_at':time.time()+long.get('expires_in',5184000)})
    print(f'  ✓ Threads authenticated! User ID: {user_id}')
    print('  ✓ Token saved (valid 60 days)')
    print('\n  Tiếp: python threads_poster.py post-all --limit 5\n')

def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool: print(f'  ✗ Slug không hợp lệ: {args.slug}'); sys.exit(1)
    token, user_id = get_token()
    text = build_thread(tool)
    print(f'\n  🧵 Posting to Threads: {tool["name"]}')
    try:
        post_id = publish_text(user_id, token, text)
        url     = f'https://www.threads.net/@rankertoolai/post/{post_id}'
        print(f'  ✓ Posted: {url}')
        state = load_state()
        state[tool['slug']] = {'posted_at': datetime.now().isoformat(), 'post_id': post_id, 'url': url}
        save_state(state)
    except urllib.error.HTTPError as e:
        print(f'  ✗ {e.code}: {e.read().decode()[:200]}')
    except Exception as e:
        print(f'  ✗ {e}')

def cmd_post_all(args):
    token, user_id = get_token()
    state = load_state()
    today = date.today().isoformat()
    cfg   = load_config()
    posted_today = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))
    quota = cfg['daily_limit'] - posted_today
    if quota <= 0: print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} posts/ngày'); return

    unposted = [t for t in TOOLS if t['slug'] not in state]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = args.delay or cfg['delay']

    print(f'\n  🧵 Threads Auto-Poster  |  {len(to_post)} posts  |  delay {delay}s\n')
    ok = err = 0
    for i, tool in enumerate(to_post):
        print(f'  [{i+1}/{len(to_post)}] {tool["name"]:<22}', end='', flush=True)
        try:
            post_id = publish_text(user_id, token, build_thread(tool))
            url     = f'https://www.threads.net/p/{post_id}'
            print(f' ✓  {url}')
            state[tool['slug']] = {'posted_at':datetime.now().isoformat(),'post_id':post_id,'url':url}
            save_state(state); ok += 1
        except urllib.error.HTTPError as e:
            print(f' ✗  {e.code}: {e.read().decode()[:60]}'); err += 1
        except Exception as e:
            print(f' ✗  {e}'); err += 1
        if i < len(to_post)-1: time.sleep(delay)
    print(f'\n  ✓ {ok} thành công  ✗ {err} lỗi\n')

def cmd_status(args):
    state = load_state()
    print(f'\n  🧵 Threads Status  |  {len(state)}/{len(TOOLS)} đã post\n')
    for t in TOOLS:
        info = state.get(t['slug'])
        print(f'  {"✓" if info else "○"}  {t["name"]:<22} {info["posted_at"][:10] if info else "chưa post"}')
    print()

def cmd_config(args):
    cfg = load_config()
    print('\n  Threads Config\n')
    def ask(k,l,d=''): v=input(f'  {l} [{cfg.get(k,d)}]: ').strip(); return v or cfg.get(k,d)
    cfg['app_id']     = ask('app_id',     'App ID')
    cfg['app_secret'] = ask('app_secret', 'App Secret')
    cfg['delay']      = int(ask('delay','Delay (giây)','60') or 60)
    cfg['daily_limit']= int(ask('daily_limit','Posts/ngày','10') or 10)
    save_config(cfg); print('  ✓ Saved\n')

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('auth'); sub.add_parser('config'); sub.add_parser('status')
    sp = sub.add_parser('post'); sp.add_argument('--slug', required=True)
    sa = sub.add_parser('post-all')
    sa.add_argument('--limit', type=int, default=0)
    sa.add_argument('--delay', type=int, default=0)
    args = p.parse_args()
    {'auth':cmd_auth,'config':cmd_config,'status':cmd_status,'post':cmd_post,'post-all':cmd_post_all}.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
