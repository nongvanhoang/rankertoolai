#!/usr/bin/env python3
"""
RankerToolAI — LinkedIn Auto-Poster
Đăng AI tool reviews lên LinkedIn profile/page qua API v2.

SETUP:
  1. https://www.linkedin.com/developers/apps → Create app
  2. Permissions: w_member_social (+ r_liteprofile, r_emailaddress)
  3. python social_agent/linkedin_poster.py auth
  4. python social_agent/linkedin_poster.py post-all

DÙNG:
  python social_agent/linkedin_poster.py post-all --limit 3
  python social_agent/linkedin_poster.py post --slug chatgpt
  python social_agent/linkedin_poster.py status
"""

import os, sys, json, time, argparse, webbrowser, urllib.request, urllib.parse, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, date
from threading import Thread, Event

SCRIPT_DIR  = Path(__file__).resolve().parent
TOKEN_FILE  = SCRIPT_DIR / 'linkedin_tokens.json'
CONFIG_FILE = SCRIPT_DIR / 'linkedin_config.json'
STATE_FILE  = SCRIPT_DIR / 'linkedin_posted.json'

SITE         = 'https://rankertoolai.com'
API          = 'https://api.linkedin.com/v2'
REDIRECT_URI = 'http://localhost:8766/callback'
SCOPES       = 'openid profile w_member_social'

TOOLS = [
  {'name':'ChatGPT',       'slug':'chatgpt',        'score':8.8,'tagline':'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo Plus','best_for':'Anyone needing an all-in-one AI for writing, code, and research','pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs','Browse the web in real-time'],'cons':['Free tier rate-limited fast','Occasionally hallucinates confidently'],'tags':['#ChatGPT','#OpenAI','#AITools','#ArtificialIntelligence']},
  {'name':'Claude',        'slug':'claude',          'score':9.2,'tagline':'Best AI for writing & reasoning — 200K context, safest frontier model','price':'Free / $20/mo Pro','best_for':'Writers, researchers & devs needing nuanced reasoning','pros':['200K token context window','Best writing quality of any AI','Stronger free tier than ChatGPT'],'cons':['No image generation','Smaller plugin ecosystem'],'tags':['#Claude','#Anthropic','#AITools','#AIWriting']},
  {'name':'Midjourney',    'slug':'midjourney',      'score':9.1,'tagline':'Best AI image generator — stunning quality preferred by designers','price':'From $10/mo','best_for':'Designers, artists & creators','pros':['Best image quality of any AI tool','V6 handles photorealism & art styles','Active creative community'],'cons':['No free tier','Commercial license needs Pro plan'],'tags':['#Midjourney','#AIArt','#DigitalArt','#AITools']},
  {'name':'Cursor',        'slug':'cursor',          'score':9.2,'tagline':'Best AI code editor that writes code faster than you','price':'Free / $20/mo Pro','best_for':'Developers who want AI to write, debug & refactor code','pros':['Composer writes multi-file code from scratch','Understands your entire codebase','Best autocomplete of any tool'],'cons':['$20/mo for full power','Can suggest outdated patterns'],'tags':['#Cursor','#AICoding','#Developer','#AITools']},
  {'name':'Semrush',       'slug':'semrush',         'score':9.1,'tagline':'Most complete SEO and marketing platform powered by AI','price':'Free / $139/mo Pro','best_for':'SEO pros, agencies & businesses needing competitor intelligence','pros':['25B+ keyword database','Best competitor analysis tool','ContentShake AI writes SEO content'],'cons':['Expensive for solopreneurs','Overwhelming for beginners'],'tags':['#SEO','#DigitalMarketing','#ContentMarketing','#AITools']},
  {'name':'ElevenLabs',    'slug':'elevenlabs',      'score':9.2,'tagline':'Most realistic AI voice generator in 2026','price':'Free / $5/mo Starter','best_for':'Creators, podcasters & marketers','pros':['99 languages, 3,000+ voices','Clone your voice in 1 minute','Lowest latency API'],'cons':['Free: 10K chars/month only','Voice cloning needs audio sample'],'tags':['#AIVoice','#TextToSpeech','#ContentCreation','#AITools']},
  {'name':'GitHub Copilot','slug':'github-copilot',  'score':9.1,'tagline':'Most-used AI coding assistant — real-time suggestions in every IDE','price':'Free / $10/mo Pro','best_for':'Developers wanting AI inside VS Code, JetBrains','pros':['Works in any editor','FREE for individual developers','Excellent autocomplete quality'],'cons':['Copilot Chat weaker than Cursor','No multi-file editing'],'tags':['#GitHubCopilot','#AICoding','#GitHub','#Developer']},
  {'name':'Perplexity AI', 'slug':'perplexity',      'score':8.8,'tagline':'Best AI for research — real-time answers with cited sources','price':'Free / $20/mo Pro','best_for':'Researchers, journalists & students','pros':['Real-time web search with citations','Pro unlocks GPT-4o & Claude','No ads or tracking'],'cons':['Free tier limited','Less conversational than ChatGPT'],'tags':['#AISearch','#Research','#AITools','#FutureOfSearch']},
  {'name':'Jasper AI',     'slug':'jasper',          'score':8.9,'tagline':'Best AI writing assistant for marketing teams','price':'$39/mo Creator','best_for':'Marketing teams, agencies & brands','pros':['50+ templates for every content type','Brand Voice learns your tone','Integrates with Surfer SEO'],'cons':['Expensive vs alternatives','Can hallucinate facts'],'tags':['#AIWriting','#ContentMarketing','#MarketingTools','#AITools']},
  {'name':'Windsurf',      'slug':'windsurf',        'score':8.9,'tagline':'Best value AI coding IDE — Cascade agent at $15/mo','price':'Free / $15/mo Pro','best_for':'Developers wanting Cursor-quality AI at lower price','pros':['Cascade AI agent for multi-file editing','VS Code compatible','$5 cheaper than Cursor'],'cons':['Smaller community than Cursor','Flow credit limits on free plan'],'tags':['#AICoding','#Developer','#CodingTools','#AITools']},
  {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'tagline':'Best free open-source AI image generator in 2026','price':'Free (self-hosted)','best_for':'Developers & designers wanting unlimited free generation','pros':['100% free and open source','Run locally — unlimited generations','10,000+ community models'],'cons':['Requires technical setup','Needs good GPU for speed'],'tags':['#StableDiffusion','#AIArt','#OpenSource','#FreeAI']},
  {'name':'Canva AI',      'slug':'canva-ai',        'score':8.7,'tagline':'Best AI design tool for non-designers in 2026','price':'Free / $15/mo Pro','best_for':'Non-designers, small businesses & social media managers','pros':['Magic Design generates full layouts','Dream Lab AI image generation','1M+ templates'],'cons':['AI features require Pro plan','Limited vs Photoshop'],'tags':['#GraphicDesign','#AIDesign','#SocialMedia','#AITools']},
  {'name':'Grok 3',        'slug':'grok',            'score':8.4,'tagline':"Elon Musk's AI chatbot with real-time X data access",'price':'X Premium $8/mo','best_for':'X/Twitter users needing real-time news','pros':['Real-time X/Twitter data access','No content restrictions','Included with X Premium'],'cons':['Requires X subscription','Smaller knowledge base'],'tags':['#Grok','#XAI','#AIChat','#AITools']},
  {'name':'Runway ML',     'slug':'runway',          'score':9.0,'tagline':'Best AI video generation platform for creators','price':'Free / $15/mo Standard','best_for':'Filmmakers, YouTubers & creators','pros':['Gen-3 Alpha highest quality AI video','Text-to-video and image-to-video','AI inpainting & motion brush'],'cons':['Credits run out fast','Render times 1-5 min per clip'],'tags':['#AIVideo','#VideoCreation','#ContentCreator','#AITools']},
  {'name':'DeepSeek',      'slug':'deepseek',        'score':9.0,'tagline':'Open-source AI that shocked Silicon Valley — free & GPT-4 quality','price':'Free / API $0.14/M tokens','best_for':'Developers & researchers wanting GPT-4 quality free','pros':['100% free to use','Cheapest API: $0.14 per 1M tokens','Matches GPT-4 on benchmarks'],'cons':['Chinese company — data privacy concerns','Occasional refusals'],'tags':['#DeepSeek','#OpenSource','#FreeAI','#AITools']},
  {'name':'Gemini',        'slug':'gemini',          'score':8.7,'tagline':"Google's AI — best for G-Suite users and real-time search",'price':'Free / $20/mo Advanced','best_for':'Google Workspace users','pros':['Deeply integrated with Google apps','Real-time search access','Most generous free tier'],'cons':['Inconsistent quality','Weaker at creative writing'],'tags':['#Gemini','#GoogleAI','#AITools','#Productivity']},
  {'name':'Notion AI',     'slug':'notion',          'score':8.9,'tagline':'AI writing & summarization built into the best productivity workspace','price':'+$10/mo add-on','best_for':'Teams & individuals using Notion','pros':['AI built directly into workspace','Summarize, rewrite, translate in 1 click','Best value for Notion users'],'cons':['Requires Notion subscription','Less powerful than standalone tools'],'tags':['#NotionAI','#Productivity','#PKM','#WorkSmarter']},
  {'name':'Otter.ai',      'slug':'otter-ai',        'score':8.7,'tagline':'Best AI meeting assistant — real-time transcription & action items','price':'Free / $16.99/mo Pro','best_for':'Remote workers & teams','pros':['95%+ transcription accuracy','Auto-generated summaries & action items','Integrates with Zoom & Google Meet'],'cons':['Free: 300 min/month limit','Accuracy drops with heavy accents'],'tags':['#MeetingNotes','#Transcription','#RemoteWork','#Productivity']},
  {'name':'HubSpot AI',    'slug':'hubspot',         'score':8.2,'tagline':'CRM-native AI — Breeze AI for sales & marketing teams','price':'Free CRM / $20/mo Starter','best_for':'Sales & marketing teams using HubSpot','pros':['AI has full CRM context','Best-in-class chatbot builder','Free CRM tier included'],'cons':['Full AI needs $800+/mo','Overkill for small businesses'],'tags':['#HubSpot','#CRM','#MarketingAI','#SalesTools']},
  {'name':'Surfer SEO',    'slug':'surfer-seo',      'score':9.0,'tagline':'Best AI content optimizer that ranks pages faster','price':'$89/mo Essential','best_for':'Content writers, SEO agencies & bloggers','pros':['Real-time NLP content scoring','Keyword density insights','Google Docs & Jasper integration'],'cons':['Pricey for solopreneurs','NLP suggestions take time to learn'],'tags':['#SEO','#ContentMarketing','#Blogging','#AITools']},
  {'name':'Writesonic',    'slug':'writesonic',      'score':8.7,'tagline':'Best budget AI writer with GPT-4 quality output','price':'Free / $16/mo','best_for':'Freelancers & small businesses','pros':['Powered by GPT-4','Real-time web access','Affordable — best value AI writer'],'cons':['Quality inconsistent on long-form','UI feels cluttered'],'tags':['#AIWriting','#ContentCreation','#Freelance','#AITools']},
]

# ── OAuth helpers ──────────────────────────────────────────────────────────────
_code, _evt = None, Event()

class _CB(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        global _code
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in q:
            _code = q['code'][0]
            self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers()
            self.wfile.write(b'<h2>LinkedIn authorised! You can close this tab.</h2><script>window.close()</script>')
        else:
            self.send_response(400); self.end_headers()
        _evt.set()

def load_config():
    if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text())
    return {'client_id':'','client_secret':'','delay':120,'daily_limit':5,'org_id':'','use_page':False}
def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_tokens():
    if TOKEN_FILE.exists(): return json.loads(TOKEN_FILE.read_text())
    return {}
def save_tokens(t): TOKEN_FILE.write_text(json.dumps(t, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

def get_valid_token():
    cfg = load_config(); tok = load_tokens()
    if not tok: print('  ✗ Chưa auth. Chạy: python linkedin_poster.py auth'); sys.exit(1)
    if time.time() > tok.get('expires_at', 0) - 3600:
        print('  ✗ Token hết hạn. Chạy: python linkedin_poster.py auth'); sys.exit(1)
    # Use org URN if company page configured, else personal URN
    if cfg.get('use_page') and cfg.get('org_id'):
        author_urn = f'urn:li:organization:{cfg["org_id"]}'
    else:
        author_urn = tok.get('person_urn', '')
    return tok['access_token'], author_urn

# ── API helpers ────────────────────────────────────────────────────────────────
def li_get(path, token):
    req = urllib.request.Request(f'{API}{path}',
        headers={'Authorization':f'Bearer {token}','X-Restli-Protocol-Version':'2.0.0'})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def li_post(path, body, token):
    req = urllib.request.Request(f'{API}{path}',
        data=json.dumps(body).encode(),
        headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','X-Restli-Protocol-Version':'2.0.0'},
        method='POST')
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

# ── Content builder ────────────────────────────────────────────────────────────
def build_linkedin_post(tool):
    u    = f'{SITE}/review/{tool["slug"]}/'
    pros = '\n'.join(f'{i+1}. {p}' for i, p in enumerate(tool['pros']))
    text = (
        f'Tôi vừa công bố review về {tool["name"]} sau nhiều tuần sử dụng.\n\n'
        f'Đánh giá: {tool["score"]}/10 — {tool["tagline"]}\n\n'
        f'Những điểm nổi bật:\n\n{pros}\n\n'
        f'Hạn chế chính:\n{tool["cons"][0]}\n\n'
        f'Phù hợp nhất: {tool["best_for"]}\n'
        f'Giá: {tool["price"]}\n\n'
        f'Review đầy đủ với bảng so sánh:\n{u}\n\n'
        f'{" ".join(tool["tags"][:4])} #AIReview #TechReview'
    )
    return text[:3000], u

def create_share(token, person_urn, text, url, title, desc):
    body = {
        'author':         person_urn,
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary':    {'text': text},
                'shareMediaCategory': 'ARTICLE',
                'media': [{
                    'status':      'READY',
                    'description': {'text': desc[:256]},
                    'originalUrl': url,
                    'title':       {'text': title[:400]},
                }]
            }
        },
        'visibility': {'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'}
    }
    return li_post('/ugcPosts', body, token)

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_auth(args):
    cfg = load_config()
    if not cfg['client_id']:
        print('\n  Nhập LinkedIn App credentials:')
        cfg['client_id']     = input('  Client ID    : ').strip()
        cfg['client_secret'] = input('  Client Secret: ').strip()
        save_config(cfg)

    auth_url = (
        'https://www.linkedin.com/oauth/v2/authorization'
        f'?response_type=code&client_id={cfg["client_id"]}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&scope={urllib.parse.quote(SCOPES)}'
        f'&state=rta2026'
    )
    print(f'\n  Opening browser for LinkedIn authorization…')
    srv = HTTPServer(('localhost', 8766), _CB)
    Thread(target=srv.serve_forever, daemon=True).start()
    webbrowser.open(auth_url)
    print('  Đang chờ callback…')
    _evt.wait(120); srv.shutdown()

    if not _code: print('  ✗ Timeout'); sys.exit(1)

    # Exchange code for token
    body = urllib.parse.urlencode({
        'grant_type':'authorization_code','code':_code,
        'redirect_uri':REDIRECT_URI,
        'client_id':cfg['client_id'],'client_secret':cfg['client_secret']
    }).encode()
    req = urllib.request.Request('https://www.linkedin.com/oauth/v2/accessToken', data=body,
        headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=30) as r:
        tok_data = json.loads(r.read())

    access = tok_data['access_token']

    # Get person URN via OpenID userinfo
    req2 = urllib.request.Request('https://api.linkedin.com/v2/userinfo',
        headers={'Authorization':f'Bearer {access}'})
    with urllib.request.urlopen(req2, timeout=15) as r:
        profile = json.loads(r.read())
    person_id  = profile.get('sub','')
    person_urn = f'urn:li:person:{person_id}'
    name       = f'{profile.get("given_name","")} {profile.get("family_name","")}'.strip()

    save_tokens({'access_token':access,'person_urn':person_urn,
                 'name':name,'expires_at':time.time()+tok_data.get('expires_in',5184000)})
    print(f'  ✓ Logged in as: {name}  ({person_urn})')
    print('  ✓ Token saved → linkedin_tokens.json')

    # Ask if posting as Company Page
    print('\n  Bạn muốn đăng từ Company Page hay Personal Profile?')
    print('  [1] Company Page (RankerToolAI page) — khuyến nghị')
    print('  [2] Personal Profile')
    choice = input('  Chọn [1/2]: ').strip()
    if choice == '1':
        print('\n  Mở trang LinkedIn Page của bạn → URL sẽ có dạng:')
        print('  https://www.linkedin.com/company/rankertoolai/')
        print('  Hoặc vào Admin view → Settings → copy Organization ID (số)')
        org_id = input('\n  Nhập Organization ID (chỉ số, vd: 12345678): ').strip()
        if org_id.isdigit():
            cfg['org_id']   = org_id
            cfg['use_page'] = True
            save_config(cfg)
            print(f'  ✓ Sẽ đăng từ Company Page: urn:li:organization:{org_id}')
        else:
            print('  ⚠ Bỏ qua — có thể nhập sau: python linkedin_poster.py config')
    else:
        cfg['use_page'] = False
        save_config(cfg)
        print(f'  ✓ Sẽ đăng từ Personal Profile: {person_urn}')

    print('\n  Tiếp: python linkedin_poster.py post-all --limit 2\n')

def cmd_post(args):
    tool = next((t for t in TOOLS if t['slug'] == args.slug), None)
    if not tool: print(f'  ✗ Slug không hợp lệ: {args.slug}'); sys.exit(1)
    token, person_urn = get_valid_token()
    text, url         = build_linkedin_post(tool)
    title             = f'{tool["name"]} Review 2026: {tool["score"]}/10 — {tool["tagline"]}'
    desc              = tool['tagline']

    cfg = load_config()
    mode = f'Company Page ({cfg["org_id"]})' if cfg.get('use_page') else 'Personal Profile'
    print(f'\n  💼 Posting to LinkedIn [{mode}]: {tool["name"]}')
    try:
        r  = create_share(token, person_urn, text, url, title, desc)
        eid = r.get('id','').split(':')[-1]
        post_url = f'https://www.linkedin.com/feed/update/urn:li:ugcPost:{eid}/'
        print(f'  ✓ Posted: {post_url}')
        state = load_state()
        state[tool['slug']] = {'posted_at':datetime.now().isoformat(),'post_id':eid,'url':post_url}
        save_state(state)
    except urllib.error.HTTPError as e:
        print(f'  ✗ {e.code}: {e.read().decode()[:200]}')

def cmd_post_all(args):
    cfg              = load_config()
    token, urn       = get_valid_token()
    state            = load_state()
    today            = date.today().isoformat()
    posted_today     = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))
    quota            = cfg['daily_limit'] - posted_today
    if quota <= 0: print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} posts/ngày'); return

    unposted = [t for t in TOOLS if t['slug'] not in state]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = args.delay or cfg['delay']

    cfg2 = load_config()
    mode = f'Company Page ({cfg2["org_id"]})' if cfg2.get('use_page') else 'Personal Profile'
    print(f'\n  💼 LinkedIn Auto-Poster [{mode}]  |  {len(to_post)} posts  |  delay {delay}s')
    ok = err = 0
    for i, tool in enumerate(to_post):
        text, url = build_linkedin_post(tool)
        title     = f'{tool["name"]} Review 2026: {tool["score"]}/10 — {tool["tagline"]}'
        print(f'  [{i+1}/{len(to_post)}] {tool["name"]:<22}', end='', flush=True)
        try:
            r   = create_share(token, urn, text, url, title, tool['tagline'])
            eid = r.get('id','').split(':')[-1]
            post_url = f'https://www.linkedin.com/feed/update/urn:li:ugcPost:{eid}/'
            print(f' ✓  {post_url}')
            state[tool['slug']] = {'posted_at':datetime.now().isoformat(),'post_id':eid,'url':post_url}
            save_state(state); ok += 1
        except urllib.error.HTTPError as e:
            print(f' ✗  {e.code}: {e.read().decode()[:80]}'); err += 1
            if e.code == 429: print('  ⚠ Rate limited — wait 10 min…'); time.sleep(600); continue
        if i < len(to_post)-1: time.sleep(delay)
    print(f'\n  ✓ {ok} thành công  ✗ {err} lỗi\n')

def cmd_status(args):
    state = load_state()
    print(f'\n  💼 LinkedIn Status  |  {len(state)}/{len(TOOLS)} đã post\n')
    for t in TOOLS:
        info = state.get(t['slug'])
        print(f'  {"✓" if info else "○"}  {t["name"]:<22} {info["posted_at"][:10] if info else "chưa post"}')
    print()

def cmd_config(args):
    cfg = load_config()
    print('\n  LinkedIn Config\n')
    def ask(k,l,default=''): v=input(f'  {l} [{cfg.get(k,default)}]: ').strip(); return v or cfg.get(k,default)
    cfg['client_id']    = ask('client_id',    'Client ID')
    cfg['client_secret']= ask('client_secret','Client Secret')
    cfg['delay']        = int(ask('delay',    'Delay giữa posts (giây)', '120') or 120)
    cfg['daily_limit']  = int(ask('daily_limit','Posts/ngày', '5') or 5)
    org = ask('org_id', 'Organization ID (để trống = personal profile)', '')
    cfg['org_id']  = org
    cfg['use_page'] = bool(org)
    if org: print(f'  ✓ Sẽ đăng từ Company Page: urn:li:organization:{org}')
    else:   print(f'  ✓ Sẽ đăng từ Personal Profile')
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
    {'auth':cmd_auth,'config':cmd_config,'status':cmd_status,'post':cmd_post,'post-all':cmd_post_all}.get(args.cmd, lambda _:p.print_help())(args)

if __name__ == '__main__': main()
