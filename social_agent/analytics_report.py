#!/usr/bin/env python3
"""
RankerToolAI — Weekly Analytics Report
Tổng hợp hiệu suất nuôi social và traffic từ GSC.

DÙNG:
  python social_agent/analytics_report.py          # terminal report
  python social_agent/analytics_report.py --html   # save HTML report
  python social_agent/analytics_report.py --json   # save JSON data
  python social_agent/analytics_report.py --week 2 # 2 tuần trước
"""

import os, sys, json, argparse
from pathlib import Path
from datetime import datetime, date, timedelta

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT       = SCRIPT_DIR.parent

TOOLS_SLUGS = [
    'chatgpt','claude','midjourney','cursor','semrush','elevenlabs',
    'github-copilot','perplexity','jasper','windsurf','stable-diffusion',
    'canva-ai','grok','runway','deepseek','gemini','notion',
    'otter-ai','hubspot','surfer-seo','writesonic',
]
TOOL_NAMES = {
    'chatgpt':'ChatGPT','claude':'Claude','midjourney':'Midjourney','cursor':'Cursor',
    'semrush':'Semrush','elevenlabs':'ElevenLabs','github-copilot':'GitHub Copilot',
    'perplexity':'Perplexity AI','jasper':'Jasper AI','windsurf':'Windsurf',
    'stable-diffusion':'Stable Diffusion','canva-ai':'Canva AI','grok':'Grok 3',
    'runway':'Runway ML','deepseek':'DeepSeek','gemini':'Gemini','notion':'Notion AI',
    'otter-ai':'Otter.ai','hubspot':'HubSpot AI','surfer-seo':'Surfer SEO',
    'writesonic':'Writesonic',
}

# ANSI colors
R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'; B='\033[1m'; X='\033[0m'

# ── State readers ──────────────────────────────────────────────────────────────
def _read_json(path):
    p = SCRIPT_DIR / path
    if not p.exists(): return {}
    try: return json.loads(p.read_text())
    except: return {}

def read_platform(filename):
    return _read_json(filename)

def read_images():
    assets = ROOT / 'html' / 'assets' / 'images'
    if not assets.exists(): return set()
    return {f.stem.replace('pin-','') for f in assets.glob('pin-*.jpg')}

def read_gsc():
    """Try to read latest GSC data from gsc_tracker results."""
    gsc_file = ROOT / 'gsc_data.json'
    if not gsc_file.exists(): return {}
    try: return json.loads(gsc_file.read_text())
    except: return {}

# ── Date helpers ───────────────────────────────────────────────────────────────
def week_range(weeks_ago=0):
    today  = date.today()
    end    = today - timedelta(days=today.weekday()) - timedelta(weeks=weeks_ago)
    start  = end - timedelta(days=6)
    return start, end

def posts_in_range(state_dict, start, end):
    result = {}
    for slug, info in state_dict.items():
        if not isinstance(info, dict): continue
        posted = info.get('posted_at', '')
        if not posted: continue
        try:
            d = date.fromisoformat(posted[:10])
            if start <= d <= end: result[slug] = info
        except: pass
    return result

# ── GSC per-page traffic ───────────────────────────────────────────────────────
def gsc_for_slug(gsc_data, slug):
    site = 'https://rankertoolai.com'
    url  = f'{site}/review/{slug}/'
    rows = gsc_data.get('rows', [])
    for row in rows:
        keys = row.get('keys', [])
        if url in keys or f'{site}/review/{slug}' in keys:
            return {'clicks': row.get('clicks',0), 'impressions': row.get('impressions',0),
                    'ctr': round(row.get('ctr',0)*100,1), 'position': round(row.get('position',0),1)}
    return None

# ── Terminal report ────────────────────────────────────────────────────────────
def bar(n, max_n, w=15):
    if max_n == 0: return '░'*w
    filled = min(int(w * n / max_n), w)
    return f'{G}{"█"*filled}{X}{"░"*(w-filled)}'

def run_report(args):
    weeks_ago      = getattr(args, 'week', 0)
    show_html      = getattr(args, 'html', False)
    show_json_flag = getattr(args, 'json', False)

    start, end = week_range(weeks_ago)
    now        = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Load all state
    pin_all = read_platform('pinterest_posted.json')
    tw_all  = read_platform('twitter_posted.json')
    rd_all  = read_platform('reddit_posted.json')
    li_all  = read_platform('linkedin_posted.json')
    imgs    = read_images()
    gsc     = read_gsc()

    total = len(TOOLS_SLUGS)

    # Cumulative totals
    pin_total = len(pin_all)
    tw_total  = len(tw_all)
    rd_total  = len([s for s,v in rd_all.items() if v])
    li_total  = len(li_all)
    img_total = len(imgs)

    # This period (week)
    pin_week = posts_in_range(pin_all, start, end)
    tw_week  = posts_in_range(tw_all, start, end)
    rd_week  = posts_in_range(rd_all, start, end)
    li_week  = posts_in_range(li_all, start, end)

    # ── Print header ──────────────────────────────────────────────────────────
    wlabel = 'Tuần này' if weeks_ago == 0 else f'{weeks_ago} tuần trước'
    print(f'\n{B}{C}  ╔═══════════════════════════════════════════════════╗')
    print(f'  ║  RankerToolAI — Weekly Social Report              ║')
    print(f'  ║  {start} → {end}   ({wlabel})        ║')
    print(f'  ╚═══════════════════════════════════════════════════╝{X}')
    print(f'  Generated: {now}\n')

    # ── Platform summary ──────────────────────────────────────────────────────
    print(f'{B}  PLATFORM OVERVIEW{X}')
    print(f'  {"─"*70}')
    print(f'  {"Platform":<14} {"Tuần này":>9} {"Tổng cộng":>10} {"Còn lại":>8} {"Phủ sóng":>9}')
    print(f'  {"─"*70}')

    platforms = [
        ('📌 Pinterest', pin_week, pin_total),
        ('🐦 Twitter',   tw_week,  tw_total),
        ('💬 Reddit',    rd_week,  rd_total),
        ('💼 LinkedIn',  li_week,  li_total),
    ]
    for name, week_data, cum in platforms:
        remaining = total - cum
        pct       = round(cum/total*100)
        print(f'  {name:<14} {len(week_data):>9} {cum:>10} {remaining:>8} {pct:>8}%  {bar(cum,total,12)}')

    print(f'  {"─"*70}')
    print(f'  {"🎨 Images":<14} {"─":>9} {img_total:>10} {total-img_total:>8} {round(img_total/total*100):>8}%  {bar(img_total,total,12)}')

    total_actions  = total * 4
    done_actions   = pin_total + tw_total + rd_total + li_total
    overall_pct    = round(done_actions / total_actions * 100) if total_actions else 0
    print(f'\n  Overall completion: {done_actions}/{total_actions} ({overall_pct}%)')

    # ── This week activity ────────────────────────────────────────────────────
    week_total = len(pin_week) + len(tw_week) + len(rd_week) + len(li_week)
    print(f'\n{B}  TUẦN NÀY: {week_total} posts{X}  ({start} → {end})')
    print(f'  {"─"*50}')
    if week_total == 0:
        print(f'  {Y}  Chưa có post nào tuần này{X}')
    else:
        all_week_slugs = set(list(pin_week)+list(tw_week)+list(rd_week)+list(li_week))
        for slug in sorted(all_week_slugs):
            name = TOOL_NAMES.get(slug, slug)
            marks = []
            if slug in pin_week: marks.append('📌')
            if slug in tw_week:  marks.append('🐦')
            if slug in rd_week:  marks.append('💬')
            if slug in li_week:  marks.append('💼')
            print(f'  {name:<22} {"".join(marks)}')

    # ── Per-tool breakdown ────────────────────────────────────────────────────
    print(f'\n{B}  CHI TIẾT TỪNG TOOL{X}')
    print(f'  {"─"*70}')
    print(f'  {"Tool":<22} {"📌":^4} {"🐦":^4} {"💬":^4} {"💼":^4} {"🎨":^4} {"GSC Clicks":>10} {"Pos":>6}')
    print(f'  {"─"*70}')

    tool_data = []
    for slug in TOOLS_SLUGS:
        name    = TOOL_NAMES.get(slug, slug)
        has_pin = '✓' if slug in pin_all else '·'
        has_tw  = '✓' if slug in tw_all  else '·'
        has_rd  = '✓' if slug in rd_all  else '·'
        has_li  = '✓' if slug in li_all  else '·'
        has_img = '✓' if slug in imgs    else '·'
        gsc_row = gsc_for_slug(gsc, slug)
        clicks  = gsc_row['clicks']   if gsc_row else None
        pos     = gsc_row['position'] if gsc_row else None
        tool_data.append({'slug':slug,'name':name,'clicks':clicks or 0,'pos':pos,'pin':has_pin,'tw':has_tw,'rd':has_rd,'li':has_li,'img':has_img})

    # Sort by clicks desc
    tool_data.sort(key=lambda x: x['clicks'], reverse=True)
    max_clicks = max(d['clicks'] for d in tool_data) if tool_data else 1

    for d in tool_data:
        pos_str = f'{d["pos"]:.1f}' if d['pos'] else ' ─ '
        clk_str = str(d['clicks']) if d['clicks'] else ' ─ '
        # Highlight top performers
        if d['clicks'] >= max_clicks * 0.5 and d['clicks'] > 0:
            name_fmt = f'{G}{d["name"]:<22}{X}'
        else:
            name_fmt = f'{d["name"]:<22}'
        print(f'  {name_fmt} {d["pin"]:^4} {d["tw"]:^4} {d["rd"]:^4} {d["li"]:^4} {d["img"]:^4} {clk_str:>10} {pos_str:>6}')

    # ── Top performers ────────────────────────────────────────────────────────
    top_by_clicks = [d for d in tool_data if d['clicks'] > 0][:5]
    if top_by_clicks:
        print(f'\n{B}  TOP TOOLS BY GSC CLICKS{X}')
        print(f'  {"─"*40}')
        for i, d in enumerate(top_by_clicks):
            print(f'  {i+1}. {d["name"]:<22} {d["clicks"]:>6} clicks  pos {d["pos"]:.1f}')

    # ── Coverage gaps (tools missing multiple platforms) ───────────────────────
    gaps = [d for d in tool_data if sum(1 for x in [d['pin'],d['tw'],d['rd'],d['li']] if x=='·') >= 3]
    if gaps:
        print(f'\n{B}  CẦN POST THÊM (chưa có 3+ platforms){X}')
        print(f'  {"─"*40}')
        for d in gaps[:8]:
            missing = []
            if d['pin']=='·': missing.append('Pinterest')
            if d['tw'] =='·': missing.append('Twitter')
            if d['rd'] =='·': missing.append('Reddit')
            if d['li'] =='·': missing.append('LinkedIn')
            print(f'  {d["name"]:<22} thiếu: {", ".join(missing)}')

    # ── Recommendations ───────────────────────────────────────────────────────
    print(f'\n{B}  KHUYẾN NGHỊ TUẦN TỚI{X}')
    print(f'  {"─"*50}')

    recs = []
    if pin_total < total:
        left = total - pin_total
        recs.append(f'📌 Đăng {min(left,10)} pin Pinterest (còn {left} tools)')
    if tw_total < total:
        left = total - tw_total
        recs.append(f'🐦 Tweet {min(left,5)} reviews (còn {left} tools)')
    if li_total < total:
        left = total - li_total
        recs.append(f'💼 Post {min(left,3)} LinkedIn articles (còn {left} tools)')
    if rd_total < total:
        left = total - rd_total
        recs.append(f'💬 Post {min(left,2)} Reddit reviews (còn {left} tools)')
    if img_total < total:
        left = total - img_total
        recs.append(f'🎨 Generate {min(left,5)} images với kie.ai (còn {left})')

    gsc_ok = any(d['clicks'] > 0 for d in tool_data)
    if not gsc_ok:
        recs.append(f'📊 Kết nối Google Search Console để xem traffic')

    # Check tools with GSC clicks but missing social posts
    hot_unposted = [d for d in top_by_clicks if d['clicks']>0 and any(x=='·' for x in [d['pin'],d['tw'],d['rd'],d['li']])]
    if hot_unposted:
        recs.append(f'🔥 Ưu tiên post {hot_unposted[0]["name"]} — đang có GSC traffic nhưng chưa phủ social đầy đủ')

    for r in recs:
        print(f'  → {r}')

    if not recs:
        print(f'  {G}✓ Tất cả platforms đã được phủ sóng hoàn toàn!{X}')

    print(f'\n  {"─"*50}')
    print(f'  Chạy: python social_agent/daily_run.py --auto  để tiếp tục\n')

    # ── Save HTML ────────────────────────────────────────────────────────────
    if show_html:
        save_html(start, end, tool_data, pin_total, tw_total, rd_total, li_total, img_total, total, week_total)

    if show_json_flag:
        out = {
            'generated': now, 'period': {'start': str(start), 'end': str(end)},
            'totals': {'pinterest':pin_total,'twitter':tw_total,'reddit':rd_total,'linkedin':li_total,'images':img_total,'tools':total},
            'this_week': {'pinterest':len(pin_week),'twitter':len(tw_week),'reddit':len(rd_week),'linkedin':len(li_week)},
            'tools': tool_data,
        }
        json_path = SCRIPT_DIR / f'report_{start}.json'
        json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
        print(f'  ✓ JSON saved: {json_path}')

# ── HTML report ────────────────────────────────────────────────────────────────
def save_html(start, end, tool_data, pin_t, tw_t, rd_t, li_t, img_t, total, week_posts):
    html_path = SCRIPT_DIR / f'report_{start}.html'
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    rows = ''
    for d in tool_data:
        def cell(v): return f'<td class="{"yes" if v=="✓" else "no"}">{v}</td>'
        gsc_td = f'<td class="num">{d["clicks"]}</td><td class="num">{d["pos"]:.1f if d["pos"] else "─"}</td>'
        rows += f'<tr><td><a href="https://rankertoolai.com/review/{d["slug"]}/" target="_blank">{d["name"]}</a></td>{cell(d["pin"])}{cell(d["tw"])}{cell(d["rd"])}{cell(d["li"])}{cell(d["img"])}{gsc_td}</tr>\n'

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>RankerToolAI Analytics {start}</title>
<style>
  body{{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#1a1a2e;background:#f0f4f8}}
  h1{{color:#6c63ff;margin-bottom:.25rem}}
  .subtitle{{color:#666;margin-bottom:2rem;font-size:.9rem}}
  .cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin-bottom:2rem}}
  .card{{background:#fff;border-radius:12px;padding:1.2rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  .card .icon{{font-size:1.5rem}}
  .card .num{{font-size:1.8rem;font-weight:700;color:#6c63ff}}
  .card .sub{{font-size:.8rem;color:#888;margin-top:.25rem}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  th{{background:#6c63ff;color:#fff;padding:.75rem;text-align:left;font-weight:600}}
  td{{padding:.6rem .75rem;border-bottom:1px solid #f0f0f0}}
  tr:last-child td{{border-bottom:none}}
  tr:hover{{background:#f7f5ff}}
  td.yes{{color:#22c55e;font-weight:700;text-align:center}}
  td.no{{color:#ccc;text-align:center}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums}}
  a{{color:#6c63ff;text-decoration:none}}
  a:hover{{text-decoration:underline}}
  .footer{{text-align:center;color:#999;font-size:.8rem;margin-top:2rem}}
</style>
</head>
<body>
<h1>📊 RankerToolAI — Analytics Report</h1>
<p class="subtitle">Kỳ: {start} → {end} &nbsp;|&nbsp; Generated: {now}</p>

<div class="cards">
  <div class="card"><div class="icon">📌</div><div class="num">{pin_t}</div><div class="sub">Pinterest pins</div></div>
  <div class="card"><div class="icon">🐦</div><div class="num">{tw_t}</div><div class="sub">Tweets</div></div>
  <div class="card"><div class="icon">💬</div><div class="num">{rd_t}</div><div class="sub">Reddit posts</div></div>
  <div class="card"><div class="icon">💼</div><div class="num">{li_t}</div><div class="sub">LinkedIn posts</div></div>
  <div class="card"><div class="icon">🎨</div><div class="num">{img_t}</div><div class="sub">Images generated</div></div>
</div>
<p style="color:#666;margin-bottom:1rem">Tuần này: <strong>{week_posts} posts</strong> &nbsp;|&nbsp; Tổng coverage: {round((pin_t+tw_t+rd_t+li_t)/(total*4)*100)}% of {total*4} possible actions</p>

<table>
<thead>
<tr><th>Tool</th><th>📌 Pin</th><th>🐦 Twitter</th><th>💬 Reddit</th><th>💼 LinkedIn</th><th>🎨 Image</th><th>Clicks</th><th>Pos</th></tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
<p class="footer">RankerToolAI Social Analytics · rankertoolai.com</p>
</body></html>"""
    html_path.write_text(html, encoding='utf-8')
    print(f'  ✓ HTML saved: {html_path}')
    # Try to open in browser
    try:
        import webbrowser; webbrowser.open(html_path.as_uri())
    except: pass

# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description='RankerToolAI Weekly Analytics Report')
    p.add_argument('--html', action='store_true', help='Lưu HTML report và mở browser')
    p.add_argument('--json', action='store_true', help='Lưu JSON data')
    p.add_argument('--week', type=int, default=0, help='Báo cáo N tuần trước (0=tuần này)')
    args = p.parse_args()
    run_report(args)

if __name__ == '__main__': main()
