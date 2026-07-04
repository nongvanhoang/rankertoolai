#!/usr/bin/env python3
"""
RankerToolAI — Pinterest Auto-Poster
Tự động đăng 21 AI tool reviews lên Pinterest qua API v5.

SETUP (1 lần):
  1. Tạo app: https://developers.pinterest.com/apps/
  2. python social_agent/pinterest_poster.py auth
  3. python social_agent/pinterest_poster.py boards   ← copy board_id
  4. python social_agent/pinterest_poster.py config   ← gán board_id

DÙNG HÀNG NGÀY:
  python social_agent/pinterest_poster.py post-all          # đăng tất cả chưa đăng
  python social_agent/pinterest_poster.py post-all --limit 5 # đăng 5 cái
  python social_agent/pinterest_poster.py post --slug chatgpt # đăng 1 tool
  python social_agent/pinterest_poster.py status             # xem tiến độ
"""

import os, sys, json, time, argparse, webbrowser, urllib.request, urllib.error, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread, Event
from datetime import datetime, date

SCRIPT_DIR   = Path(__file__).resolve().parent
TOKEN_FILE   = SCRIPT_DIR / 'pinterest_tokens.json'
STATE_FILE   = SCRIPT_DIR / 'pinterest_posted.json'
CONFIG_FILE  = SCRIPT_DIR / 'pinterest_config.json'

SITE         = 'https://rankertoolai.com'
API          = 'https://api.pinterest.com/v5'
REDIRECT_URI = 'http://localhost:8765/callback'
SCOPES       = 'boards:read,boards:write,pins:read,pins:write'

# ── Tools (mirrors dashboard) ──────────────────────────────────────────────────
TOOLS = [
  {'name':'ChatGPT',       'slug':'chatgpt',        'score':8.8,'cat':'AI Chatbot',          'tagline':'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo Plus','best_for':'Anyone needing an all-in-one AI for writing, code, and research','pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs','Browse the web in real-time'],'cons':['Free tier rate-limited fast','Occasionally hallucinates confidently'],'tags':['#ChatGPT','#OpenAI','#GPT4','#AITools','#ArtificialIntelligence'],'board':'AI Chatbot Reviews 2026'},
  {'name':'Claude',        'slug':'claude',          'score':9.2,'cat':'AI Chatbot',          'tagline':'Best AI for writing & reasoning — 200K context, safest frontier model','price':'Free / $20/mo Pro','best_for':'Writers, researchers & devs needing nuanced reasoning','pros':['200K token context window','Best writing quality of any AI','Stronger free tier than ChatGPT'],'cons':['No image generation','Smaller plugin ecosystem'],'tags':['#Claude','#Anthropic','#AITools','#AIWriting'],'board':'AI Chatbot Reviews 2026'},
  {'name':'Midjourney',    'slug':'midjourney',      'score':9.1,'cat':'AI Image Generator',  'tagline':'Best AI image generator — stunning quality preferred by designers','price':'From $10/mo','best_for':'Designers, artists & creators needing highest quality AI images','pros':['Best image quality of any AI tool','V6 handles photorealism & art styles','Active creative community'],'cons':['No free tier','Commercial license needs Pro plan'],'tags':['#Midjourney','#AIArt','#AIImage','#DigitalArt'],'board':'AI Image Generator Reviews 2026'},
  {'name':'Cursor',        'slug':'cursor',          'score':9.2,'cat':'AI Coding Tool',      'tagline':'Best AI code editor that writes code faster than you','price':'Free / $20/mo Pro','best_for':'Developers who want AI to write, debug & refactor code','pros':['Composer writes multi-file code from scratch','Understands your entire codebase','Best autocomplete of any tool'],'cons':['$20/mo for full power','Can suggest outdated patterns'],'tags':['#Cursor','#AICoding','#Developer','#AITools'],'board':'AI Coding Tools Reviews 2026'},
  {'name':'Semrush',       'slug':'semrush',         'score':9.1,'cat':'AI SEO Suite',        'tagline':'Most complete SEO and marketing platform powered by AI','price':'Free / $139/mo Pro','best_for':'SEO pros, agencies & businesses needing competitor intelligence','pros':['25B+ keyword database','Best competitor analysis tool','ContentShake AI writes SEO content'],'cons':['Expensive for solopreneurs','Overwhelming for beginners'],'tags':['#Semrush','#SEO','#DigitalMarketing','#AITools'],'board':'AI SEO & Marketing Tools 2026'},
  {'name':'ElevenLabs',    'slug':'elevenlabs',      'score':9.2,'cat':'AI Voice Generator',  'tagline':'Most realistic AI voice generator in 2026','price':'Free / $5/mo Starter','best_for':'Creators, podcasters & marketers needing human-like AI voices','pros':['99 languages, 3,000+ voices','Clone your voice in 1 minute','Lowest latency API'],'cons':['Free: 10K chars/month only','Voice cloning needs audio sample'],'tags':['#ElevenLabs','#AIVoice','#TextToSpeech','#AITools'],'board':'AI Voice & TTS Tool Reviews 2026'},
  {'name':'GitHub Copilot','slug':'github-copilot',  'score':9.1,'cat':'AI Coding Tool',      'tagline':'Most-used AI coding assistant — real-time suggestions in every IDE','price':'Free / $10/mo Pro','best_for':'Developers wanting AI inside VS Code, JetBrains, or Neovim','pros':['Works in any editor','FREE for individual developers','Excellent autocomplete quality'],'cons':['Copilot Chat weaker than Cursor','No multi-file editing'],'tags':['#GitHubCopilot','#AICoding','#GitHub','#AITools'],'board':'AI Coding Tools Reviews 2026'},
  {'name':'Perplexity AI', 'slug':'perplexity',      'score':8.8,'cat':'AI Search Tool',      'tagline':'Best AI for research — real-time answers with cited sources','price':'Free / $20/mo Pro','best_for':'Researchers, journalists & students needing verified info','pros':['Real-time web search with citations','Pro unlocks GPT-4o & Claude','No ads or tracking'],'cons':['Free tier limited to standard model','Less conversational than ChatGPT'],'tags':['#PerplexityAI','#AISearch','#Research','#AITools'],'board':'Best AI Tools 2026 — RankerToolAI'},
  {'name':'Jasper AI',     'slug':'jasper',          'score':8.9,'cat':'AI Writing Tool',     'tagline':'Best AI writing assistant for marketing teams','price':'$39/mo Creator','best_for':'Marketing teams, agencies & brands needing consistent AI content','pros':['50+ templates for every content type','Brand Voice learns your tone','Integrates with Surfer SEO'],'cons':['Expensive vs alternatives','Can hallucinate facts'],'tags':['#JasperAI','#AIWriting','#ContentMarketing','#AITools'],'board':'AI Writing Tools Reviews 2026'},
  {'name':'Windsurf',      'slug':'windsurf',        'score':8.9,'cat':'AI Coding IDE',       'tagline':'Best value AI coding IDE — Cascade agent at $15/mo','price':'Free / $15/mo Pro','best_for':'Developers wanting Cursor-quality AI coding at $5/mo less','pros':['Cascade AI agent for multi-file editing','VS Code compatible','$5 cheaper than Cursor'],'cons':['Smaller community than Cursor','Flow credit limits on free plan'],'tags':['#Windsurf','#AICoding','#Developer','#AITools'],'board':'AI Coding Tools Reviews 2026'},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'cat':'AI Image Generator','tagline':'Best free open-source AI image generator in 2026','price':'Free / $10/mo DreamStudio','best_for':'Developers & designers wanting unlimited free image generation','pros':['100% free and open source','Run locally — unlimited generations','10,000+ community models'],'cons':['Requires technical setup','Needs good GPU for speed'],'tags':['#StableDiffusion','#AIArt','#OpenSource','#FreeAI'],'board':'AI Image Generator Reviews 2026'},
  {'name':'Canva AI',      'slug':'canva-ai',        'score':8.7,'cat':'AI Design Tool',      'tagline':'Best AI design tool for non-designers in 2026','price':'Free / $15/mo Pro','best_for':'Non-designers, small businesses & social media managers','pros':['Magic Design generates full layouts','Dream Lab AI image generation','1M+ templates'],'cons':['AI features require Pro plan','Limited vs Photoshop'],'tags':['#CanvaAI','#GraphicDesign','#AIDesign','#AITools'],'board':'AI Image Generator Reviews 2026'},
  {'name':'Grok 3',        'slug':'grok',            'score':8.4,'cat':'AI Chatbot',          'tagline':"Elon Musk's AI chatbot with real-time X data access",'price':'X Premium $8/mo','best_for':'X/Twitter users needing real-time news & trending topics','pros':['Real-time X/Twitter data access','No content restrictions','Included with X Premium'],'cons':['Requires X subscription','Smaller knowledge base than GPT-4'],'tags':['#Grok','#XAI','#AIChat','#AITools'],'board':'AI Chatbot Reviews 2026'},
  {'name':'Runway ML',     'slug':'runway',          'score':9.0,'cat':'AI Video Generator',  'tagline':'Best AI video generation platform for creators','price':'Free / $15/mo Standard','best_for':'Filmmakers, YouTubers & creators needing AI video','pros':['Gen-3 Alpha highest quality AI video','Text-to-video and image-to-video','AI inpainting & motion brush'],'cons':['Credits run out fast','Render times 1-5 min per clip'],'tags':['#RunwayML','#AIVideo','#VideoCreation','#AITools'],'board':'AI Video Tools Reviews 2026'},
  {'name':'DeepSeek',      'slug':'deepseek',        'score':9.0,'cat':'AI Chatbot',          'tagline':'Open-source AI that shocked Silicon Valley — free & GPT-4 quality','price':'Free / API $0.14/M tokens','best_for':'Developers & researchers wanting GPT-4 quality at open-source prices','pros':['100% free to use','Cheapest API: $0.14 per 1M tokens','Matches GPT-4 on benchmarks'],'cons':['Chinese company — data privacy concerns','Occasional refusals on sensitive topics'],'tags':['#DeepSeek','#OpenSource','#FreeAI','#AITools'],'board':'AI Chatbot Reviews 2026'},
  {'name':'Gemini',        'slug':'gemini',          'score':8.7,'cat':'AI Chatbot',          'tagline':"Google's AI — best for G-Suite users and real-time search",'price':'Free / $20/mo Advanced','best_for':'Google Workspace users wanting AI in Gmail, Docs & Sheets','pros':['Deeply integrated with Google apps','Real-time search access','Most generous free tier'],'cons':['Inconsistent quality vs Claude/ChatGPT','Weaker at creative writing'],'tags':['#Gemini','#GoogleAI','#AITools','#AIChat'],'board':'AI Chatbot Reviews 2026'},
  {'name':'Notion AI',     'slug':'notion',          'score':8.9,'cat':'AI Productivity Tool','tagline':'AI writing & summarization built into the best productivity workspace','price':'+$10/mo add-on','best_for':'Teams & individuals already using Notion for notes & project mgmt','pros':['AI built directly into your workspace','Summarize, rewrite, translate in 1 click','Best value for Notion users'],'cons':['Requires Notion subscription','Less powerful than standalone tools'],'tags':['#NotionAI','#Productivity','#AITools','#PKM'],'board':'AI Productivity Tools Reviews 2026'},
  {'name':'Otter.ai',      'slug':'otter-ai',        'score':8.7,'cat':'AI Productivity Tool','tagline':'Best AI meeting assistant — real-time transcription & action items','price':'Free / $16.99/mo Pro','best_for':'Remote workers & teams who never want to take manual meeting notes','pros':['95%+ transcription accuracy','Auto-generated summaries & action items','Integrates with Zoom & Google Meet'],'cons':['Free: 300 min/month limit','Accuracy drops with heavy accents'],'tags':['#OtterAI','#MeetingNotes','#Transcription','#Productivity'],'board':'AI Productivity Tools Reviews 2026'},
  {'name':'HubSpot AI',    'slug':'hubspot',         'score':8.2,'cat':'AI CRM & Marketing',  'tagline':'CRM-native AI — Breeze AI for sales & marketing teams','price':'Free CRM / $20/mo Starter','best_for':'Sales & marketing teams already using HubSpot CRM','pros':['AI has full CRM context','Best-in-class chatbot builder','Free CRM tier included'],'cons':['Full AI suite needs $800+/mo Pro','Overkill for small businesses'],'tags':['#HubSpot','#CRM','#MarketingAI','#AITools'],'board':'AI SEO & Marketing Tools 2026'},
  {'name':'Surfer SEO',    'slug':'surfer-seo',      'score':9.0,'cat':'AI SEO Tool',         'tagline':'Best AI content optimizer that ranks pages faster','price':'$89/mo Essential','best_for':'Content writers, SEO agencies & bloggers wanting data-driven rankings','pros':['Real-time NLP content scoring','Keyword density insights','Integrates with Google Docs & Jasper'],'cons':['Pricey for solopreneurs','NLP suggestions take time to learn'],'tags':['#SurferSEO','#SEO','#ContentMarketing','#AITools'],'board':'AI SEO & Marketing Tools 2026'},
  {'name':'Writesonic',    'slug':'writesonic',      'score':8.7,'cat':'AI Writing Tool',     'tagline':'Best budget AI writer with GPT-4 quality output','price':'Free / $16/mo Chatsonic','best_for':'Freelancers & small businesses needing affordable AI writing','pros':['Powered by GPT-4','Chatsonic has real-time web access','Affordable — best value AI writer'],'cons':['Quality inconsistent on long-form','UI feels cluttered'],'tags':['#Writesonic','#AIWriting','#ContentCreation','#AITools'],'board':'AI Writing Tools Reviews 2026'},
]


# ── Config helpers ─────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    return {'client_id':'','client_secret':'','default_board_id':'','board_map':{},'delay':45,'daily_limit':25}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')

def load_tokens():
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text(encoding='utf-8'))
    return {}

def save_tokens(tok):
    TOKEN_FILE.write_text(json.dumps(tok, indent=2), encoding='utf-8')

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {}

def save_state(st):
    STATE_FILE.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding='utf-8')


# ── OAuth 2.0 ──────────────────────────────────────────────────────────────────
_auth_code = None
_auth_event = Event()

class _OAuthHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            _auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h2>&#10003; Pinterest authorised!</h2><p>You can close this tab.</p><script>window.close()</script>')
        else:
            self.send_response(400)
            self.end_headers()
        _auth_event.set()

def _exchange_code(client_id, client_secret, code):
    body = urllib.parse.urlencode({
        'grant_type':   'authorization_code',
        'code':         code,
        'redirect_uri': REDIRECT_URI,
    }).encode()
    creds = urllib.parse.quote(f'{client_id}:{client_secret}')
    req = urllib.request.Request(
        'https://api.pinterest.com/v5/oauth/token',
        data=body,
        headers={
            'Authorization': f'Basic {__import__("base64").b64encode(f"{client_id}:{client_secret}".encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def _refresh_token(client_id, client_secret, refresh_tok):
    body = urllib.parse.urlencode({
        'grant_type':    'refresh_token',
        'refresh_token': refresh_tok,
    }).encode()
    req = urllib.request.Request(
        'https://api.pinterest.com/v5/oauth/token',
        data=body,
        headers={
            'Authorization': f'Basic {__import__("base64").b64encode(f"{client_id}:{client_secret}".encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get_valid_token():
    cfg  = load_config()
    tok  = load_tokens()
    if not tok:
        print('\n  ✗ Chưa auth. Chạy: python pinterest_poster.py auth\n')
        sys.exit(1)

    # Refresh if expired (or within 1 day of expiry)
    expires = tok.get('expires_at', 0)
    if time.time() > expires - 86400:
        print('  ↻ Refreshing access token…')
        try:
            new = _refresh_token(cfg['client_id'], cfg['client_secret'], tok['refresh_token'])
            tok.update({
                'access_token':  new['access_token'],
                'refresh_token': new.get('refresh_token', tok['refresh_token']),
                'expires_at':    time.time() + new.get('expires_in', 2592000),
            })
            save_tokens(tok)
            print('  ✓ Token refreshed')
        except Exception as e:
            print(f'  ✗ Token refresh failed: {e}')
            print('  Re-run: python pinterest_poster.py auth')
            sys.exit(1)

    return tok['access_token']


# ── Pinterest API calls ────────────────────────────────────────────────────────
def api_get(path, token):
    req = urllib.request.Request(
        f'{API}{path}',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_post(path, body, token):
    req = urllib.request.Request(
        f'{API}{path}',
        data=json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def list_boards(token):
    data = api_get('/boards?page_size=50', token)
    return data.get('items', [])

def create_pin(token, board_id, title, description, link, image_url, alt_text=''):
    body = {
        'link':         link,
        'title':        title[:100],
        'description':  description[:500],
        'board_id':     board_id,
        'alt_text':     alt_text[:500],
        'media_source': {'source_type': 'image_url', 'url': image_url},
    }
    return api_post('/pins', body, token)


# ── Content builder ────────────────────────────────────────────────────────────
def build_pin_content(tool):
    u     = f'{SITE}/review/{tool["slug"]}/'
    pros3 = '\n'.join(f'+ {p}' for p in tool['pros'][:3])
    cons1 = f'- {tool["cons"][0]}'
    tags  = ' '.join(tool['tags'][:5])

    title = f'{tool["name"]} Review 2026: {tool["score"]}/10 — {tool["tagline"]}'[:100]
    desc  = (
        f'{tool["tagline"]}\n\n'
        f'{pros3}\n{cons1}\n\n'
        f'Giá: {tool["price"]}\n'
        f'Phù hợp nhất: {tool["best_for"]}\n\n'
        f'Review đầy đủ: {u}\n\n'
        f'{tags}'
    )[:500]

    img_url = f'{SITE}/assets/images/pin-{tool["slug"]}.jpg'
    return title, desc, u, img_url


def get_board_id(tool, cfg):
    board_name = tool.get('board', '')
    # Try exact match in board_map
    for name, bid in cfg.get('board_map', {}).items():
        if name.lower() in board_name.lower() or board_name.lower() in name.lower():
            return bid
    return cfg.get('default_board_id', '')


def today_str():
    return date.today().isoformat()


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_auth(args):
    cfg = load_config()

    if not cfg['client_id']:
        print('\n  Nhập thông tin Pinterest App:')
        cfg['client_id']     = input('  Client ID    : ').strip()
        cfg['client_secret'] = input('  Client Secret: ').strip()
        save_config(cfg)

    auth_url = (
        f'https://www.pinterest.com/oauth/'
        f'?client_id={cfg["client_id"]}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&response_type=code'
        f'&scope={SCOPES}'
    )

    print(f'\n  Mở browser để authorize Pinterest…')
    print(f'  URL: {auth_url}\n')

    # Start local callback server
    server = HTTPServer(('localhost', 8765), _OAuthHandler)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    webbrowser.open(auth_url)

    print('  Đang chờ callback từ Pinterest…')
    _auth_event.wait(timeout=120)
    server.shutdown()

    if not _auth_code:
        print('  ✗ Timeout. Thử lại.')
        sys.exit(1)

    print('  ✓ Authorization code nhận được. Đang lấy tokens…')
    tok_data = _exchange_code(cfg['client_id'], cfg['client_secret'], _auth_code)

    tokens = {
        'access_token':  tok_data['access_token'],
        'refresh_token': tok_data.get('refresh_token', ''),
        'expires_at':    time.time() + tok_data.get('expires_in', 2592000),
        'obtained_at':   datetime.now().isoformat(),
    }
    save_tokens(tokens)
    print('  ✓ Tokens đã lưu vào pinterest_tokens.json')
    print('\n  Tiếp theo: python pinterest_poster.py boards\n')


def cmd_boards(args):
    token  = get_valid_token()
    boards = list_boards(token)
    if not boards:
        print('  Không tìm thấy board nào.')
        return

    print(f'\n  {"Board Name":<45} {"ID":<30} Pins')
    print('  ' + '-'*80)
    for b in boards:
        name = b.get('name','')[:44]
        bid  = b.get('id','')
        pins = b.get('pin_count', '?')
        print(f'  {name:<45} {bid:<30} {pins}')

    print(f'\n  Dùng ID để gán vào config:')
    print(f'  python pinterest_poster.py config\n')


def cmd_config(args):
    cfg = load_config()

    print('\n  ── Pinterest Config ──')
    print('  (Enter để giữ nguyên giá trị hiện tại)\n')

    def ask(key, label, current):
        val = input(f'  {label} [{current}]: ').strip()
        return val if val else current

    cfg['client_id']         = ask('client_id',         'Client ID',          cfg['client_id'])
    cfg['client_secret']     = ask('client_secret',     'Client Secret',      cfg['client_secret'])
    cfg['default_board_id']  = ask('default_board_id',  'Default Board ID',   cfg['default_board_id'])
    cfg['delay']             = int(ask('delay',          'Delay giữa pins (s)',str(cfg['delay'])))
    cfg['daily_limit']       = int(ask('daily_limit',    'Giới hạn pins/ngày', str(cfg['daily_limit'])))

    print('\n  Gán board theo từng nhóm (Enter để bỏ qua):')
    boards_to_map = [
        ('AI Chatbot Reviews 2026',          'AI Chatbot Reviews 2026'),
        ('AI Image Generator Reviews 2026',  'AI Image Generator Reviews 2026'),
        ('AI Coding Tools Reviews 2026',     'AI Coding Tools Reviews 2026'),
        ('AI SEO & Marketing Tools 2026',    'AI SEO & Marketing Tools 2026'),
        ('AI Writing Tools Reviews 2026',    'AI Writing Tools Reviews 2026'),
        ('AI Voice & TTS Tool Reviews 2026', 'AI Voice & TTS Tool Reviews 2026'),
        ('AI Video Tools Reviews 2026',      'AI Video Tools Reviews 2026'),
        ('AI Productivity Tools Reviews 2026','AI Productivity Tools Reviews 2026'),
        ('Best AI Tools 2026 — RankerToolAI','Best AI Tools 2026 — RankerToolAI'),
    ]
    for board_name, label in boards_to_map:
        cur = cfg['board_map'].get(board_name, '')
        val = input(f'  {label[:45]:<45} ID [{cur}]: ').strip()
        if val:
            cfg['board_map'][board_name] = val

    save_config(cfg)
    print('\n  ✓ Config đã lưu vào pinterest_config.json')
    print('  Tiếp theo: python pinterest_poster.py post-all --limit 3\n')


def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool:
        print(f'  ✗ Không tìm thấy tool: {args.slug}')
        print(f'  Slug hợp lệ: {", ".join(t["slug"] for t in TOOLS)}')
        sys.exit(1)

    cfg      = load_config()
    token    = get_valid_token()
    board_id = get_board_id(tool, cfg)

    if not board_id:
        print('  ✗ Chưa gán board_id. Chạy: python pinterest_poster.py config')
        sys.exit(1)

    title, desc, link, img_url = build_pin_content(tool)
    print(f'\n  🎨 Posting: {tool["name"]}')
    print(f'     Board : {tool.get("board","")}')
    print(f'     Image : {img_url}')

    try:
        result = create_pin(token, board_id, title, desc, link, img_url, alt_text=title)
        pin_id  = result.get('id','')
        pin_url = f'https://pinterest.com/pin/{pin_id}/'
        print(f'  ✓ Pin created: {pin_url}')

        state = load_state()
        state[tool['slug']] = {'posted_at': datetime.now().isoformat(), 'pin_id': pin_id, 'pin_url': pin_url}
        save_state(state)
        return pin_id

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'  ✗ HTTP {e.code}: {body[:200]}')
        raise


def cmd_post_all(args):
    cfg   = load_config()
    token = get_valid_token()
    state = load_state()

    if not cfg['default_board_id'] and not cfg['board_map']:
        print('  ✗ Chưa config boards. Chạy: python pinterest_poster.py config')
        sys.exit(1)

    # Count today's posts
    today = today_str()
    posted_today = sum(
        1 for v in state.values()
        if isinstance(v, dict) and v.get('posted_at','').startswith(today)
    )
    remaining_quota = cfg['daily_limit'] - posted_today

    if remaining_quota <= 0:
        print(f'  ✓ Đã đạt giới hạn {cfg["daily_limit"]} pins/ngày hôm nay. Thử lại ngày mai.')
        return

    # Select tools to post
    unposted = [t for t in TOOLS if t['slug'] not in state or args.repost]
    if not unposted:
        print('  ✓ Tất cả 21 tools đã được post lên Pinterest!')
        cmd_status(args)
        return

    limit     = min(args.limit or remaining_quota, remaining_quota, len(unposted))
    to_post   = unposted[:limit]
    delay     = args.delay or cfg['delay']

    print(f'\n  📌 Pinterest Auto-Poster')
    print(f'  Đăng: {len(to_post)} pins  |  Đã hôm nay: {posted_today}/{cfg["daily_limit"]}  |  Delay: {delay}s\n')

    ok = err = 0
    for i, tool in enumerate(to_post):
        board_id = get_board_id(tool, cfg)
        if not board_id:
            print(f'  ⚠ Skip {tool["name"]} — không có board_id (thêm vào config)')
            err += 1
            continue

        title, desc, link, img_url = build_pin_content(tool)
        print(f'  [{i+1}/{len(to_post)}] 🎨 {tool["name"]:<22}', end='', flush=True)

        try:
            result  = create_pin(token, board_id, title, desc, link, img_url, alt_text=title)
            pin_id  = result.get('id','')
            pin_url = f'https://pinterest.com/pin/{pin_id}/'
            print(f' ✓  {pin_url}')

            state[tool['slug']] = {
                'posted_at': datetime.now().isoformat(),
                'pin_id':    pin_id,
                'pin_url':   pin_url,
                'board':     tool.get('board',''),
            }
            save_state(state)
            ok += 1

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f' ✗  HTTP {e.code}: {body[:80]}')
            err += 1
            if e.code == 429:
                print('  ⚠ Rate limited — chờ 5 phút...')
                time.sleep(300)
                continue

        if i < len(to_post) - 1:
            print(f'  ⏳ Chờ {delay}s…')
            time.sleep(delay)

    print(f'\n  Kết quả: ✓ {ok} thành công  ✗ {err} lỗi')
    print(f'  State lưu tại: {STATE_FILE}')
    cmd_status(args)


def cmd_status(args):
    state = load_state()
    today = today_str()
    total = len(TOOLS)
    done  = len(state)
    today_count = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))

    print(f'\n  📊 Pinterest Status')
    print(f'  Đã post: {done}/{total} tools  |  Hôm nay: {today_count}')
    print()
    for tool in TOOLS:
        info = state.get(tool['slug'])
        if info:
            dt = info.get('posted_at','')[:10]
            print(f'  ✓  {tool["name"]:<22} {dt}  {info.get("pin_url","")}')
        else:
            print(f'  ○  {tool["name"]:<22} chưa post')
    print()

    # Export JS for dashboard sync
    if state:
        lines = []
        for slug, v in state.items():
            if isinstance(v, dict):
                lines.append(f"(function(){{var d=JSON.parse(localStorage.getItem('rta_done_v3')||'{{}}');if(!d['{slug}'])d['{slug}']={{}};d['{slug}']['pinterest']={{done:true,ts:{int(time.time()*1000)}}};localStorage.setItem('rta_done_v3',JSON.stringify(d));}})()")
        js_path = SCRIPT_DIR / 'sync_dashboard_pinterest.js'
        js_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f'  Sync dashboard: F12 → Console → paste {js_path.name}')


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Pinterest Auto-Poster for RankerToolAI')
    sub    = parser.add_subparsers(dest='cmd')

    sub.add_parser('auth',    help='OAuth flow — lấy access token')
    sub.add_parser('boards',  help='Liệt kê tất cả boards + ID')
    sub.add_parser('config',  help='Cấu hình board IDs và settings')
    sub.add_parser('status',  help='Xem tiến độ đã post')

    p_post = sub.add_parser('post', help='Post một tool cụ thể')
    p_post.add_argument('--slug', required=True, help='Tool slug, vd: chatgpt')

    p_all = sub.add_parser('post-all', help='Post tất cả tools chưa đăng')
    p_all.add_argument('--limit',  type=int, default=0,    help='Giới hạn số pins (0 = theo daily_limit)')
    p_all.add_argument('--delay',  type=int, default=0,    help='Giây giữa mỗi pin (0 = dùng config)')
    p_all.add_argument('--repost', action='store_true',    help='Post lại kể cả đã post rồi')

    args = parser.parse_args()

    cmds = {
        'auth':     cmd_auth,
        'boards':   cmd_boards,
        'config':   cmd_config,
        'status':   cmd_status,
        'post':     cmd_post,
        'post-all': cmd_post_all,
    }

    if args.cmd not in cmds:
        parser.print_help()
        sys.exit(0)

    cmds[args.cmd](args)


if __name__ == '__main__':
    main()
