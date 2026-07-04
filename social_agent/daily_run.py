#!/usr/bin/env python3
"""
RankerToolAI — Daily Social Media Orchestrator
Chạy toàn bộ pipeline nuôi social bằng 1 lệnh.

DÙNG HÀNG NGÀY:
  python social_agent/daily_run.py              # menu tương tác
  python social_agent/daily_run.py --auto       # chạy tất cả tự động
  python social_agent/daily_run.py --pinterest  # chỉ Pinterest
  python social_agent/daily_run.py --twitter    # chỉ Twitter
  python social_agent/daily_run.py --reddit     # chỉ Reddit
  python social_agent/daily_run.py --linkedin   # chỉ LinkedIn
  python social_agent/daily_run.py --status     # xem tiến độ tổng
  python social_agent/daily_run.py --report     # weekly analytics report

THIẾT LẬP CHẠY TỰ ĐỘNG (Windows Task Scheduler):
  Mở Task Scheduler → Create Basic Task → Daily → 9:00 AM
  Action: python C:\\Users\\Admin\\RankerToolAI\\social_agent\\daily_run.py --auto
"""

import os, sys, json, time, argparse, subprocess
from pathlib import Path
from datetime import datetime, date

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE   = SCRIPT_DIR / 'daily_run.log'

TOOLS_SLUGS = [
    'chatgpt','claude','midjourney','cursor','semrush','elevenlabs',
    'github-copilot','perplexity','jasper','windsurf','stable-diffusion',
    'canva-ai','grok','runway','deepseek','gemini','notion',
    'otter-ai','hubspot','surfer-seo','writesonic',
]

# ── Colors ─────────────────────────────────────────────────────────────────────
R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; B='\033[1m'; X='\033[0m'
def ok(s):   print(f'{G}  ✓  {s}{X}')
def err(s):  print(f'{R}  ✗  {s}{X}')
def info(s): print(f'{C}  ℹ  {s}{X}')
def hdr(s):  print(f'\n{B}{C}  {'─'*50}\n  {s}\n  {'─'*50}{X}')
def warn(s): print(f'{Y}  ⚠  {s}{X}')

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{ts}] {msg}\n')

def run_script(script, *args, capture=False):
    cmd = [sys.executable, str(SCRIPT_DIR / script)] + list(args)
    if capture:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    else:
        r = subprocess.run(cmd)
        return r.returncode, ''

# ── Status readers ─────────────────────────────────────────────────────────────
def read_pinterest_status():
    f = SCRIPT_DIR / 'pinterest_posted.json'
    if not f.exists(): return {}
    return json.loads(f.read_text())

def read_twitter_status():
    f = SCRIPT_DIR / 'twitter_posted.json'
    if not f.exists(): return {}
    return json.loads(f.read_text())

def read_reddit_status():
    f = SCRIPT_DIR / 'reddit_posted.json'
    if not f.exists(): return {}
    return json.loads(f.read_text())

def read_linkedin_status():
    f = SCRIPT_DIR / 'linkedin_posted.json'
    if not f.exists(): return {}
    return json.loads(f.read_text())

def read_images_status():
    assets = SCRIPT_DIR.parent / 'html' / 'assets' / 'images'
    if not assets.exists(): return {}
    return {f.stem: True for f in assets.glob('pin-*.jpg')}

def today_count(state_dict):
    today = date.today().isoformat()
    return sum(
        1 for v in state_dict.values()
        if isinstance(v, dict) and v.get('posted_at','').startswith(today)
    )

# ── Full status report ─────────────────────────────────────────────────────────
def show_status():
    hdr('RankerToolAI — Social Status')

    pin   = read_pinterest_status()
    tw    = read_twitter_status()
    rd    = read_reddit_status()
    li    = read_linkedin_status()
    imgs  = read_images_status()
    total = len(TOOLS_SLUGS)

    pin_done = len(pin)
    tw_done  = len(tw)
    rd_done  = len([s for s,v in rd.items() if v])
    li_done  = len(li)
    img_done = len(imgs)

    print(f'\n  {"Platform":<15} {"Done":>6} {"Total":>6} {"Today":>6} {"Progress"}')
    print(f'  {"─"*58}')

    def bar(n, t, w=20):
        filled = int(w * n / t) if t else 0
        pct = round(n/t*100) if t else 0
        return f'{"█"*filled}{"░"*(w-filled)} {pct}%'

    print(f'  {"📌 Pinterest":<15} {pin_done:>6} {total:>6} {today_count(pin):>6}  {bar(pin_done,total)}')
    print(f'  {"🐦 Twitter":<15} {tw_done:>6} {total:>6} {today_count(tw):>6}  {bar(tw_done,total)}')
    print(f'  {"💬 Reddit":<15} {rd_done:>6} {total:>6} {"?":>6}  {bar(rd_done,total)}')
    print(f'  {"💼 LinkedIn":<15} {li_done:>6} {total:>6} {today_count(li):>6}  {bar(li_done,total)}')
    print(f'  {"🎨 Images":<15} {img_done:>6} {total:>6} {"─":>6}  {bar(img_done,total)}')

    total_actions = total * 4  # pin + tw + rd + li
    done_actions  = pin_done + tw_done + rd_done + li_done
    print(f'\n  Overall: {done_actions}/{total_actions} actions ({round(done_actions/total_actions*100) if total_actions else 0}%)')

    # Unposted per platform
    unposted_pin = [s for s in TOOLS_SLUGS if s not in pin]
    unposted_tw  = [s for s in TOOLS_SLUGS if s not in tw]
    unposted_rd  = [s for s in TOOLS_SLUGS if not rd.get(s)]
    unposted_li  = [s for s in TOOLS_SLUGS if s not in li]

    print(f'\n  Chưa post:')
    if unposted_pin: print(f'  📌 Pinterest ({len(unposted_pin)}): {", ".join(unposted_pin[:5])}{"…" if len(unposted_pin)>5 else ""}')
    if unposted_tw:  print(f'  🐦 Twitter  ({len(unposted_tw)}): {", ".join(unposted_tw[:5])}{"…" if len(unposted_tw)>5 else ""}')
    if unposted_rd:  print(f'  💬 Reddit   ({len(unposted_rd)}): {", ".join(unposted_rd[:5])}{"…" if len(unposted_rd)>5 else ""}')
    if unposted_li:  print(f'  💼 LinkedIn ({len(unposted_li)}): {", ".join(unposted_li[:5])}{"…" if len(unposted_li)>5 else ""}')
    print()

# ── Pipeline steps ─────────────────────────────────────────────────────────────
def step_generate_images(limit=5):
    hdr('Step 1 — Generate Images (kie.ai)')
    kieai_key = os.environ.get('KIE_AI_KEY', '')
    if not kieai_key:
        warn('KIE_AI_KEY not set — skipping image generation')
        warn('Set: $env:KIE_AI_KEY = "your-key"')
        return False
    info(f'Generating Pinterest images (limit {limit})…')
    code, out = run_script('batch_generate.py', 'pinterest', '--limit', str(limit), '--delay', '3')
    if code == 0: ok('Images generated')
    else: err('Image generation failed'); print(out[:500])
    log(f'generate_images limit={limit} exit={code}')
    return code == 0

def step_pinterest(limit=10):
    hdr('Step 2 — Post to Pinterest')
    pf = SCRIPT_DIR / 'pinterest_config.json'
    if not pf.exists():
        warn('Pinterest not configured. Run: python social_agent/pinterest_poster.py config')
        return False
    cfg = json.loads(pf.read_text())
    if not cfg.get('default_board_id') and not cfg.get('board_map'):
        warn('Pinterest board IDs not set. Run: python social_agent/pinterest_poster.py config')
        return False
    info(f'Posting {limit} pins to Pinterest…')
    code, _ = run_script('pinterest_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Pinterest done')
    else: err('Pinterest failed')
    log(f'pinterest limit={limit} exit={code}')
    return code == 0

def step_twitter(limit=5):
    hdr('Step 3 — Post to Twitter/X')
    tf = SCRIPT_DIR / 'twitter_config.json'
    if not tf.exists():
        warn('Twitter not configured. Run: python social_agent/twitter_poster.py config')
        return False
    cfg = json.loads(tf.read_text())
    if not cfg.get('api_key'):
        warn('Twitter API key not set')
        return False
    info(f'Tweeting {limit} reviews…')
    code, _ = run_script('twitter_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Twitter done')
    else: err('Twitter failed')
    log(f'twitter limit={limit} exit={code}')
    return code == 0

def step_reddit(limit=2):
    hdr('Step 4 — Post to Reddit')
    rf = SCRIPT_DIR / 'reddit_config.json'
    if not rf.exists():
        warn('Reddit not configured. Run: python social_agent/reddit_poster.py config')
        return False
    cfg = json.loads(rf.read_text())
    if not cfg.get('client_id'):
        warn('Reddit client_id not set')
        return False
    info(f'Posting {limit} Reddit reviews…')
    code, _ = run_script('reddit_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Reddit done')
    else: err('Reddit failed')
    log(f'reddit limit={limit} exit={code}')
    return code == 0

def step_linkedin(limit=3):
    hdr('Step 5 — Post to LinkedIn')
    lf = SCRIPT_DIR / 'linkedin_tokens.json'
    if not lf.exists():
        warn('LinkedIn not authenticated. Run: python social_agent/linkedin_poster.py auth')
        return False
    info(f'Posting {limit} LinkedIn articles…')
    code, _ = run_script('linkedin_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('LinkedIn done')
    else: err('LinkedIn failed')
    log(f'linkedin limit={limit} exit={code}')
    return code == 0

def step_threads(limit=5):
    hdr('Step 6 — Post to Threads')
    tf = SCRIPT_DIR / 'threads_tokens.json'
    if not tf.exists():
        warn('Threads not authenticated. Run: python social_agent/threads_poster.py auth')
        return False
    info(f'Posting {limit} Threads posts…')
    code, _ = run_script('threads_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Threads done')
    else: err('Threads failed')
    log(f'threads limit={limit} exit={code}')
    return code == 0

def step_medium(limit=2):
    hdr('Step 7 — Publish to Medium')
    mf = SCRIPT_DIR / 'medium_config.json'
    if not mf.exists():
        warn('Medium not configured. Run: python social_agent/medium_poster.py config')
        return False
    cfg = json.loads(mf.read_text())
    if not cfg.get('token'):
        warn('Medium token not set')
        return False
    info(f'Publishing {limit} Medium articles…')
    code, _ = run_script('medium_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Medium done')
    else: err('Medium failed')
    log(f'medium limit={limit} exit={code}')
    return code == 0

def step_quora(limit=2):
    hdr('Step 8 — Post to Quora')
    qf = SCRIPT_DIR / 'quora_config.json'
    if not qf.exists():
        warn('Quora not configured. Run: python social_agent/quora_poster.py config')
        return False
    info(f'Posting {limit} Quora answers…')
    code, _ = run_script('quora_poster.py', 'post-all', '--limit', str(limit))
    if code == 0: ok('Quora done')
    else: err('Quora failed')
    log(f'quora limit={limit} exit={code}')
    return code == 0

# ── Interactive menu ───────────────────────────────────────────────────────────
def interactive_menu():
    while True:
        show_status()
        print(f'{B}  Menu:{X}')
        print('  [1] Generate images (kie.ai batch)')
        print('  [2] Post to Pinterest')
        print('  [3] Post to Twitter/X')
        print('  [4] Post to Reddit')
        print('  [5] Post to LinkedIn')
        print('  [6] Run ALL (1→2→3→4→5)')
        print('  [7] Weekly Analytics Report')
        print('  [r] Refresh status')
        print('  [q] Quit')
        print()
        choice = input('  Chọn: ').strip().lower()

        if choice == '1':
            n = input('  Số images (default 5): ').strip() or '5'
            step_generate_images(int(n))
        elif choice == '2':
            n = input('  Số pins hôm nay (default 10): ').strip() or '10'
            step_pinterest(int(n))
        elif choice == '3':
            n = input('  Số tweets hôm nay (default 5): ').strip() or '5'
            step_twitter(int(n))
        elif choice == '4':
            n = input('  Số posts Reddit hôm nay (default 2): ').strip() or '2'
            step_reddit(int(n))
        elif choice == '5':
            n = input('  Số posts LinkedIn hôm nay (default 3): ').strip() or '3'
            step_linkedin(int(n))
        elif choice == '6':
            run_auto()
        elif choice == '7':
            run_script('analytics_report.py')
        elif choice == 'r':
            continue
        elif choice == 'q':
            break
        else:
            warn('Chọn 1-7, r hoặc q')

        input('\n  Enter để tiếp tục…')

# ── Auto run ───────────────────────────────────────────────────────────────────
def run_auto(args=None):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    hdr(f'RankerToolAI — Auto Run  [{ts}]')
    log(f'=== AUTO RUN START ===')

    results = {}

    # Generate missing images first
    results['images']    = step_generate_images(limit=5)
    results['pinterest'] = step_pinterest(limit=10)
    results['twitter']   = step_twitter(limit=5)
    results['reddit']    = step_reddit(limit=2)
    results['linkedin']  = step_linkedin(limit=3)
    results['threads']   = step_threads(limit=5)
    results['medium']    = step_medium(limit=2)
    results['quora']     = step_quora(limit=2)

    hdr('Summary')
    for k, v in results.items():
        if v:  ok(f'{k.capitalize()} OK')
        else: warn(f'{k.capitalize()} skipped / failed')

    log(f'=== AUTO RUN END === results={results}')
    print()

# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description='RankerToolAI Daily Social Orchestrator')
    p.add_argument('--auto',      action='store_true', help='Chạy tất cả tự động (không cần menu)')
    p.add_argument('--status',    action='store_true', help='Chỉ hiện status và thoát')
    p.add_argument('--report',    action='store_true', help='Chạy weekly analytics report')
    p.add_argument('--pinterest', action='store_true', help='Chỉ chạy Pinterest')
    p.add_argument('--twitter',   action='store_true', help='Chỉ chạy Twitter')
    p.add_argument('--reddit',    action='store_true', help='Chỉ chạy Reddit')
    p.add_argument('--linkedin',  action='store_true', help='Chỉ chạy LinkedIn')
    p.add_argument('--images',    action='store_true', help='Chỉ generate images')
    p.add_argument('--limit',     type=int, default=0, help='Giới hạn số posts mỗi platform')
    args = p.parse_args()

    if args.status:
        show_status(); return

    if args.report:
        run_script('analytics_report.py'); return

    if args.images:
        step_generate_images(args.limit or 5); return

    if args.pinterest:
        step_pinterest(args.limit or 10); return

    if args.twitter:
        step_twitter(args.limit or 5); return

    if args.reddit:
        step_reddit(args.limit or 2); return

    if args.linkedin:
        step_linkedin(args.limit or 3); return

    if args.auto:
        run_auto(args); return

    # Default: interactive menu
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print('\n\n  Bye!\n')

if __name__ == '__main__':
    main()
