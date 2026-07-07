#!/usr/bin/env python3
"""
RankerToolAI — Quora Auto-Poster
Tự động tạo và đăng answers cho 21 AI tools lên Quora.
Dùng session cookie từ browser (không cần API key).

SETUP:
  1. Đăng nhập Quora trong browser
  2. F12 → Application → Cookies → quora.com → copy giá trị "m-b"
  3. python social_agent/quora_poster.py config
  4. python social_agent/quora_poster.py post --slug chatgpt

DÙNG:
  python social_agent/quora_poster.py post --slug chatgpt
  python social_agent/quora_poster.py post-all --limit 3
  python social_agent/quora_poster.py status
  python social_agent/quora_poster.py open --slug chatgpt   # mở browser + copy answer
"""

import os, sys, json, time, re, argparse, webbrowser, subprocess, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, date

SCRIPT_DIR  = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / 'quora_config.json'
STATE_FILE  = SCRIPT_DIR / 'quora_posted.json'

SITE = 'https://rankertoolai.com'

# ── Pre-mapped high-traffic Quora questions per tool ──────────────────────────
QUESTIONS = {
    'chatgpt':          ['What-is-ChatGPT-and-how-does-it-work','What-are-the-best-uses-of-ChatGPT','Is-ChatGPT-Plus-worth-it'],
    'claude':           ['What-is-Claude-AI','How-does-Claude-compare-to-ChatGPT','Is-Anthropic-Claude-better-than-ChatGPT'],
    'midjourney':       ['What-is-the-best-AI-image-generator','How-good-is-Midjourney','What-are-the-best-AI-art-generators'],
    'cursor':           ['What-is-the-best-AI-code-editor','Is-Cursor-AI-worth-it','What-are-the-best-AI-coding-tools'],
    'semrush':          ['What-is-the-best-SEO-tool','Is-SEMrush-worth-the-money','What-are-the-best-SEO-tools-for-beginners'],
    'elevenlabs':       ['What-is-the-best-AI-voice-generator','How-good-is-ElevenLabs','What-is-the-best-text-to-speech-AI'],
    'github-copilot':   ['Is-GitHub-Copilot-worth-it','What-is-the-best-AI-coding-assistant','How-good-is-GitHub-Copilot'],
    'perplexity':       ['What-is-Perplexity-AI','Is-Perplexity-AI-better-than-Google','What-is-the-best-AI-search-engine'],
    'jasper':           ['What-is-the-best-AI-writing-tool','Is-Jasper-AI-worth-it','What-are-the-best-AI-content-writers'],
    'windsurf':         ['What-is-Windsurf-AI','Windsurf-vs-Cursor-which-is-better','What-is-the-best-AI-IDE'],
    'stable-diffusion': ['What-is-Stable-Diffusion','How-do-I-get-started-with-Stable-Diffusion','Is-Stable-Diffusion-free'],
    'canva-ai':         ['What-is-the-best-AI-design-tool','Is-Canva-AI-good','What-are-the-best-graphic-design-AI-tools'],
    'grok':             ['What-is-Grok-AI','How-good-is-Elon-Musks-Grok-AI','Grok-vs-ChatGPT-which-is-better'],
    'runway':           ['What-is-the-best-AI-video-generator','How-good-is-Runway-ML','What-is-the-best-AI-for-video-creation'],
    'deepseek':         ['What-is-DeepSeek-AI','Is-DeepSeek-as-good-as-GPT-4','What-is-the-best-free-AI-chatbot'],
    'gemini':           ['What-is-Google-Gemini-AI','Is-Google-Gemini-better-than-ChatGPT','How-good-is-Google-Gemini'],
    'notion':           ['What-is-Notion-AI','Is-Notion-AI-worth-it','What-is-the-best-AI-productivity-tool'],
    'otter-ai':         ['What-is-the-best-AI-meeting-transcription-tool','Is-Otter-ai-good','What-is-the-best-AI-note-taker'],
    'hubspot':          ['What-is-the-best-CRM-with-AI','Is-HubSpot-AI-good','What-are-the-best-AI-marketing-tools'],
    'surfer-seo':       ['What-is-the-best-SEO-content-optimization-tool','Is-Surfer-SEO-worth-it','How-good-is-Surfer-SEO'],
    'writesonic':       ['What-is-the-best-affordable-AI-writer','Is-Writesonic-good','Writesonic-vs-Jasper-which-is-better'],
}

TOOLS = {
    'chatgpt':          {'name':'ChatGPT',       'score':8.8,'tagline':'Most versatile AI assistant','price':'Free / $20/mo','best_for':'anyone needing an all-in-one AI','pros':['GPT-4o with vision, voice & DALL-E 3','1,000+ plugins & Custom GPTs','Browse the web in real-time'],'cons':['Free tier rate-limited fast','Occasionally hallucinates']},
    'claude':           {'name':'Claude',         'score':9.2,'tagline':'Best AI for writing & reasoning','price':'Free / $20/mo','best_for':'writers, researchers & developers','pros':['200K token context window','Best writing quality of any AI','Stronger free tier than ChatGPT'],'cons':['No image generation','Smaller plugin ecosystem']},
    'midjourney':       {'name':'Midjourney',     'score':9.1,'tagline':'Best AI image generator','price':'From $10/mo','best_for':'designers and artists','pros':['Best image quality','V6 handles photorealism','Active community'],'cons':['No free tier','Commercial license needs Pro plan']},
    'cursor':           {'name':'Cursor',         'score':9.2,'tagline':'Best AI code editor','price':'Free / $20/mo','best_for':'developers wanting AI to write code','pros':['Composer writes multi-file code','Understands entire codebase','Best autocomplete'],'cons':['$20/mo for full power','Can suggest outdated patterns']},
    'semrush':          {'name':'Semrush',        'score':9.1,'tagline':'Most complete SEO platform','price':'Free / $139/mo','best_for':'SEO pros and agencies','pros':['25B+ keyword database','Best competitor analysis','ContentShake AI'],'cons':['Expensive for solopreneurs','Overwhelming for beginners']},
    'elevenlabs':       {'name':'ElevenLabs',     'score':9.2,'tagline':'Most realistic AI voice generator','price':'Free / $5/mo','best_for':'creators and podcasters','pros':['99 languages, 3,000+ voices','Clone voice in 1 minute','Lowest latency API'],'cons':['Free: 10K chars/month','Needs audio sample for cloning']},
    'github-copilot':   {'name':'GitHub Copilot', 'score':9.1,'tagline':'Most-used AI coding assistant','price':'Free / $10/mo','best_for':'developers in VS Code or JetBrains','pros':['Works in any editor','FREE for individuals','Excellent autocomplete'],'cons':['Weaker chat vs Cursor','No multi-file editing']},
    'perplexity':       {'name':'Perplexity AI',  'score':8.8,'tagline':'Best AI search engine','price':'Free / $20/mo','best_for':'researchers and students','pros':['Real-time search with citations','No ads','Pro unlocks GPT-4o & Claude'],'cons':['Free tier limited','Less conversational than ChatGPT']},
    'jasper':           {'name':'Jasper AI',      'score':8.9,'tagline':'Best AI writing tool for marketing','price':'$39/mo','best_for':'marketing teams and agencies','pros':['50+ templates','Brand Voice feature','Surfer SEO integration'],'cons':['Expensive vs alternatives','Can hallucinate facts']},
    'windsurf':         {'name':'Windsurf',       'score':8.9,'tagline':'Best value AI coding IDE','price':'Free / $15/mo','best_for':'developers wanting Cursor at lower price','pros':['Cascade AI multi-file editing','VS Code compatible','$5 cheaper than Cursor'],'cons':['Smaller community','Flow credit limits']},
    'stable-diffusion': {'name':'Stable Diffusion','score':8.9,'tagline':'Best free open-source image AI','price':'Free (self-hosted)','best_for':'developers wanting unlimited free generation','pros':['100% free & open source','10,000+ community models','Run locally'],'cons':['Requires technical setup','Needs good GPU']},
    'canva-ai':         {'name':'Canva AI',       'score':8.7,'tagline':'Best AI design tool for non-designers','price':'Free / $15/mo','best_for':'non-designers and small businesses','pros':['Magic Design generates layouts','Dream Lab AI images','1M+ templates'],'cons':['AI needs Pro plan','Limited vs Photoshop']},
    'grok':             {'name':'Grok 3',         'score':8.4,'tagline':"Elon Musk's AI with real-time X data",'price':'X Premium $8/mo','best_for':'X/Twitter users needing real-time news','pros':['Real-time X data access','No content restrictions','Included with X Premium'],'cons':['Requires X subscription','Smaller knowledge base']},
    'runway':           {'name':'Runway ML',      'score':9.0,'tagline':'Best AI video generation platform','price':'Free / $15/mo','best_for':'filmmakers and YouTubers','pros':['Gen-3 Alpha highest quality','Text-to-video and image-to-video','AI inpainting'],'cons':['Credits run out fast','1-5 min render times']},
    'deepseek':         {'name':'DeepSeek',       'score':9.0,'tagline':'Open-source AI that shocked Silicon Valley','price':'Free / API $0.14/M tokens','best_for':'developers wanting GPT-4 quality free','pros':['100% free to use','$0.14 per 1M tokens','Matches GPT-4 on benchmarks'],'cons':['Chinese company data concerns','Occasional refusals']},
    'gemini':           {'name':'Gemini',         'score':8.7,'tagline':"Google's AI for G-Suite users",'price':'Free / $20/mo','best_for':'Google Workspace users','pros':['Integrated with Google apps','Real-time search','Most generous free tier'],'cons':['Inconsistent quality','Weaker at creative writing']},
    'notion':           {'name':'Notion AI',      'score':8.9,'tagline':'AI writing built into the best workspace','price':'+$10/mo','best_for':'teams using Notion','pros':['AI in your workspace','Summarize in 1 click','Best value for Notion users'],'cons':['Requires Notion subscription','Less powerful standalone']},
    'otter-ai':         {'name':'Otter.ai',       'score':8.7,'tagline':'Best AI meeting assistant','price':'Free / $16.99/mo','best_for':'remote workers and teams','pros':['95%+ transcription accuracy','Auto action items','Zoom & Meet integration'],'cons':['300 min/month free limit','Accuracy drops with accents']},
    'hubspot':          {'name':'HubSpot AI',     'score':8.2,'tagline':'CRM-native AI for sales teams','price':'Free CRM / $20/mo','best_for':'sales and marketing teams','pros':['AI has full CRM context','Best chatbot builder','Free CRM tier'],'cons':['Full AI needs $800+/mo','Overkill for small biz']},
    'surfer-seo':       {'name':'Surfer SEO',     'score':9.0,'tagline':'Best AI content optimizer for SEO','price':'$89/mo','best_for':'content writers and SEO agencies','pros':['Real-time NLP scoring','Keyword density insights','Google Docs integration'],'cons':['Pricey for solopreneurs','NLP takes time to learn']},
    'writesonic':       {'name':'Writesonic',     'score':8.7,'tagline':'Best budget AI writer with GPT-4 quality','price':'Free / $16/mo','best_for':'freelancers and small businesses','pros':['Powered by GPT-4','Real-time web access','Best value AI writer'],'cons':['Inconsistent on long-form','UI feels cluttered']},
}

# ── Config / state ─────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists(): return json.loads(CONFIG_FILE.read_text())
    return {'cookie_mb':'','delay':900,'daily_limit':3,'formkey':''}
def save_config(c): CONFIG_FILE.write_text(json.dumps(c, indent=2))
def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}
def save_state(s): STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

# ── Answer builder ─────────────────────────────────────────────────────────────
def build_answer(slug):
    t = TOOLS[slug]
    u = f'{SITE}/review/{slug}/'
    pros = '\n'.join(f'- **{p}**' for p in t['pros'])
    cons = '\n'.join(f'- {c}' for c in t['cons'])
    answer = f"""**{t['name']} Review 2026: {t['score']}/10 — {t['tagline']}**

After extensively testing {t['name']} for several weeks, here's my honest take:

**What it does best:**
{pros}

**Where it falls short:**
{cons}

**Pricing:** {t['price']}
**Best for:** {t['best_for']}

**Bottom line:** {t['name']} scores {t['score']}/10 in my testing. {'It\'s genuinely one of the best tools in its category right now.' if t['score'] >= 9.0 else 'It\'s a solid choice, especially for its target audience.' if t['score'] >= 8.5 else 'It has some notable limitations worth considering before paying.'}

I wrote a detailed comparison including alternatives at RankerToolAI: {u}

Hope this helps!"""
    return answer

# ── Clipboard helper (Windows) ────────────────────────────────────────────────
def copy_to_clipboard(text):
    try:
        subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
        return True
    except Exception:
        return False

# ── API posting via session cookie ────────────────────────────────────────────
def get_formkey(session_headers):
    req = urllib.request.Request('https://www.quora.com/', headers=session_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        m = re.search(r'formkey["\s:=]+(["\'])([a-f0-9]{32})\1', html)
        if m: return m.group(2)
        m = re.search(r'"formkey":"([a-f0-9]{32})"', html)
        if m: return m.group(1)
    except: pass
    return None

def post_answer_api(question_slug, answer_text, cfg):
    cookie  = cfg.get('cookie_mb', '')
    if not cookie: return False, 'No session cookie'

    headers = {
        'Cookie':     f'm-b={cookie}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer':    'https://www.quora.com/',
    }

    # Get formkey
    formkey = cfg.get('formkey') or get_formkey(headers)
    if not formkey: return False, 'Could not get formkey — cookie may be invalid'
    cfg['formkey'] = formkey; save_config(cfg)

    # Get question ID via API
    q_url = f'https://www.quora.com/{question_slug}'
    req   = urllib.request.Request(q_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        m = re.search(r'"qid":(\d+)', html) or re.search(r'questionId["\s:=]+(\d+)', html)
        if not m: return False, 'Could not find question ID'
        qid = m.group(1)
    except Exception as e:
        return False, f'Could not load question: {e}'

    # Post answer via GraphQL
    payload = json.dumps({
        'queryName': 'AddAnswerMutation',
        'variables': {
            'questionId': int(qid),
            'answerText': answer_text,
        }
    }).encode()

    post_headers = {**headers,
        'Content-Type':    'application/json',
        'quora-formkey':   formkey,
        'quora-page-creator': 'answer',
        'X-Requested-With':'XMLHttpRequest',
    }
    req2 = urllib.request.Request(
        'https://www.quora.com/graphql/gql_para_post',
        data=payload, headers=post_headers, method='POST'
    )
    try:
        with urllib.request.urlopen(req2, timeout=20) as r:
            resp = json.loads(r.read())
        if resp.get('data'): return True, resp
        return False, str(resp)
    except Exception as e:
        return False, str(e)

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_config(args):
    cfg = load_config()
    print('\n  Quora Config\n')
    print('  Cách lấy cookie m-b:')
    print('  1. Đăng nhập quora.com trong Chrome')
    print('  2. F12 → Application → Cookies → https://www.quora.com')
    print('  3. Tìm cookie tên "m-b" → copy Value\n')
    def ask(k,l,d=''): v=input(f'  {l} [{cfg.get(k,d)}]: ').strip(); return v or cfg.get(k,d)
    cfg['cookie_mb']    = ask('cookie_mb',  'Cookie m-b')
    cfg['delay']        = int(ask('delay',  'Delay giữa posts (giây)', '900') or 900)
    cfg['daily_limit']  = int(ask('daily_limit','Posts/ngày max', '3') or 3)
    cfg['formkey']      = ''  # reset formkey on new config
    save_config(cfg); print('  ✓ Saved\n')

def cmd_open(args):
    """Mở browser đến câu hỏi + copy answer vào clipboard."""
    slug = args.slug
    if slug not in TOOLS: print(f'  ✗ Slug không hợp lệ: {slug}'); return
    qs     = QUESTIONS.get(slug, [])
    answer = build_answer(slug)
    idx    = getattr(args, 'q', 0) % len(qs) if qs else 0
    q_slug = qs[idx] if qs else ''
    url    = f'https://www.quora.com/{q_slug}'

    copied = copy_to_clipboard(answer)
    print(f'\n  📋 Quora Answer: {TOOLS[slug]["name"]}')
    print(f'  Question: {url}')
    if copied:
        print(f'  ✓ Answer đã copy vào clipboard — Ctrl+V vào ô trả lời')
    else:
        print(f'  Answer:\n\n{answer}\n')
    webbrowser.open(url)

def cmd_post(args):
    slug = args.slug
    if slug not in TOOLS: print(f'  ✗ Slug không hợp lệ: {slug}'); return
    cfg    = load_config()
    state  = load_state()
    answer = build_answer(slug)
    qs     = QUESTIONS.get(slug, [])
    if not qs: print(f'  ✗ Không có câu hỏi cho: {slug}'); return

    # Pick next unanswered question for this slug
    answered = [v.get('question','') for v in [state.get(slug,{})] if v]
    q_slug   = next((q for q in qs if q not in answered), qs[0])
    url      = f'https://www.quora.com/{q_slug}'

    print(f'\n  💬 Quora post: {TOOLS[slug]["name"]}')
    print(f'  Question: {q_slug}')

    if not cfg.get('cookie_mb'):
        print('  ✗ Cookie chưa set. Chạy: python quora_poster.py config')
        print(f'  → Fallback: mở browser + copy clipboard')
        copy_to_clipboard(answer); webbrowser.open(url); return

    ok, result = post_answer_api(q_slug, answer, cfg)
    if ok:
        print(f'  ✓ Posted! {url}')
        state[slug] = {'posted_at': datetime.now().isoformat(), 'question': q_slug, 'url': url}
        save_state(state)
    else:
        print(f'  ✗ API failed: {str(result)[:100]}')
        print(f'  → Fallback: mở browser + copy clipboard')
        copied = copy_to_clipboard(answer)
        webbrowser.open(url)
        if copied: print('  ✓ Answer copied to clipboard — paste vào Quora')
        # Ask if manually posted
        confirm = input('  Bạn đã post xong chưa? [y/n]: ').strip().lower()
        if confirm == 'y':
            state[slug] = {'posted_at': datetime.now().isoformat(), 'question': q_slug, 'url': url, 'method': 'manual'}
            save_state(state)
            print('  ✓ Đã ghi lại')

def cmd_post_all(args):
    cfg   = load_config()
    state = load_state()
    today = date.today().isoformat()
    posted_today = sum(1 for v in state.values() if isinstance(v,dict) and v.get('posted_at','').startswith(today))
    quota = cfg['daily_limit'] - posted_today
    if quota <= 0: print(f'  ✓ Đạt giới hạn {cfg["daily_limit"]} posts/ngày'); return

    unposted = [s for s in TOOLS if s not in state]
    limit    = min(args.limit or quota, quota, len(unposted))
    to_post  = unposted[:limit]
    delay    = args.delay or cfg['delay']

    print(f'\n  💬 Quora Auto-Poster  |  {len(to_post)} answers  |  delay {delay}s\n')
    for i, slug in enumerate(to_post):
        print(f'  [{i+1}/{len(to_post)}] {TOOLS[slug]["name"]}')
        a = argparse.Namespace(slug=slug, q=0)
        cmd_post(a)
        if i < len(to_post)-1:
            print(f'  Chờ {delay}s…'); time.sleep(delay)
    print(f'\n  Xong!\n')

def cmd_status(args):
    state = load_state()
    print(f'\n  💬 Quora Status  |  {len(state)}/{len(TOOLS)} đã answer\n')
    for slug, t in TOOLS.items():
        info = state.get(slug)
        mark = f"✓  {info['posted_at'][:10]}  {info.get('question','')[:50]}" if info else '○  chưa post'
        print(f'  {mark[:3]}  {t["name"]:<22} {mark[3:]}')
    print()

def cmd_preview(args):
    slug = args.slug if hasattr(args,'slug') and args.slug else 'chatgpt'
    print(f'\n  === ANSWER PREVIEW: {TOOLS[slug]["name"]} ===\n')
    print(build_answer(slug))
    print(f'\n  Questions:\n')
    for q in QUESTIONS.get(slug, []):
        print(f'  https://www.quora.com/{q}')
    print()

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('config'); sub.add_parser('status')
    sp = sub.add_parser('post');    sp.add_argument('--slug', required=True)
    so = sub.add_parser('open');    so.add_argument('--slug', required=True); so.add_argument('--q', type=int, default=0)
    sv = sub.add_parser('preview'); sv.add_argument('--slug', default='chatgpt')
    sa = sub.add_parser('post-all')
    sa.add_argument('--limit', type=int, default=0)
    sa.add_argument('--delay', type=int, default=0)
    args = p.parse_args()
    cmds = {'config':cmd_config,'status':cmd_status,'post':cmd_post,'open':cmd_open,'post-all':cmd_post_all,'preview':cmd_preview}
    cmds.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
