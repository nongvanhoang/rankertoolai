#!/usr/bin/env python3
"""
RankerToolAI — Content Scheduler
Post vào giờ peak engagement thay vì post ngay lập tức.

PEAK TIMES (theo nghiên cứu 2026):
  Pinterest:  Thứ 6-7, 8-11pm EST
  Twitter:    Thứ 2-4, 12-3pm EST
  LinkedIn:   Thứ 2-5, 7-9am & 12pm EST
  Reddit:     Thứ 2-4, 9am & 8pm EST
  Threads:    Thứ 2-5, 9am & 7pm EST
  Medium:     Thứ 2-4, 7-9am EST
  Quora:      Thứ 2-5, 9am-12pm EST

DÙNG:
  python social_agent/scheduler.py status          # xem schedule hôm nay
  python social_agent/scheduler.py next            # lần chạy tiếp theo
  python social_agent/scheduler.py run             # chạy theo schedule (loop)
  python social_agent/scheduler.py install         # cài Windows Task Scheduler
  python social_agent/scheduler.py plan --days 7  # xem plan 7 ngày tới
"""

import os, sys, json, time, argparse, subprocess
from pathlib import Path
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT       = SCRIPT_DIR.parent
SCHED_FILE = SCRIPT_DIR / 'schedule_log.json'

TZ_LOCAL = ZoneInfo('Asia/Ho_Chi_Minh')  # UTC+7

# Peak hours (local Vietnam time, UTC+7)
# Converts US EST peak times: EST+12 = Vietnam time
SCHEDULE = {
    'pinterest': {
        'days':   [4, 5, 6],   # Fri, Sat, Sun (0=Mon)
        'hours':  [8, 20, 22], # 8am, 8pm, 10pm VN time
        'limit':  10,
        'script': 'pinterest_poster.py',
        'cmd':    ['post-all'],
    },
    'twitter': {
        'days':   [0, 1, 2, 3, 4],   # Mon-Fri
        'hours':  [8, 12, 17],
        'limit':  5,
        'script': 'twitter_poster.py',
        'cmd':    ['post-all'],
    },
    'linkedin': {
        'days':   [0, 1, 2, 3, 4],   # Mon-Fri (LinkedIn is B2B)
        'hours':  [8, 12],
        'limit':  3,
        'script': 'linkedin_poster.py',
        'cmd':    ['post-all'],
    },
    'reddit': {
        'days':   [0, 1, 2, 3, 4],
        'hours':  [9, 20],
        'limit':  2,
        'script': 'reddit_poster.py',
        'cmd':    ['post-all'],
    },
    'threads': {
        'days':   [0, 1, 2, 3, 4, 5, 6],
        'hours':  [9, 19],
        'limit':  5,
        'script': 'threads_poster.py',
        'cmd':    ['post-all'],
    },
    'medium': {
        'days':   [0, 1, 2],   # Mon-Wed (less frequent)
        'hours':  [8],
        'limit':  2,
        'script': 'medium_poster.py',
        'cmd':    ['post-all'],
    },
    'quora': {
        'days':   [0, 1, 2, 3, 4],
        'hours':  [9, 14],
        'limit':  2,
        'script': 'quora_poster.py',
        'cmd':    ['post-all'],
    },
    'discord': {
        'days':   [0, 1, 2, 3, 4, 5, 6],   # every day
        'hours':  [9, 18],
        'limit':  1,
        'script': 'post_discord.py',
        'cmd':    [],   # no --all: posts single least-posted tool per run
    },
    'devto': {
        'days':   [0, 2, 4],   # Mon, Wed, Fri
        'hours':  [9],
        'limit':  1,
        'script': 'post_devto_auto.py',
        'cmd':    [],   # no --all: posts single least-posted tool per run
    },
    'instagram': {
        'days':   [1, 4],   # Tue, Fri — only 9/44 tools have carousels ready
        'hours':  [10],
        'limit':  1,
        'script': 'post_instagram.py',
        'cmd':    [],   # no --all: posts single least-posted tool with a ready carousel
    },
}

DAY_NAMES = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ Nhật']
PLATFORM_ICONS = {
    'pinterest':'📌','twitter':'🐦','linkedin':'💼','reddit':'💬',
    'threads':'🧵','medium':'📝','quora':'💡','discord':'🎮','devto':'👨‍💻',
    'instagram':'📷',
}

# ── State ──────────────────────────────────────────────────────────────────────
def load_log():
    if SCHED_FILE.exists(): return json.loads(SCHED_FILE.read_text())
    return {}
def save_log(l): SCHED_FILE.write_text(json.dumps(l, indent=2))

def last_run_key(platform, h):
    return f'{platform}_{date.today().isoformat()}_{h:02d}'

def already_ran(platform, h):
    log = load_log()
    return last_run_key(platform, h) in log

def mark_ran(platform, h, result):
    log = load_log()
    log[last_run_key(platform, h)] = {'time': datetime.now().isoformat(), 'result': result}
    save_log(log)

# ── Schedule logic ─────────────────────────────────────────────────────────────
def should_run_now(platform, cfg, now=None):
    now     = now or datetime.now(TZ_LOCAL)
    weekday = now.weekday()
    hour    = now.hour
    if weekday not in cfg['days']: return False
    if hour not in cfg['hours']:   return False
    if already_ran(platform, hour): return False
    return True

def next_slot(platform, cfg, from_dt=None):
    from_dt  = from_dt or datetime.now(TZ_LOCAL)
    for delta_days in range(8):
        check = from_dt + timedelta(days=delta_days)
        wd    = check.weekday()
        if wd not in cfg['days']: continue
        for h in sorted(cfg['hours']):
            slot = check.replace(hour=h, minute=0, second=0, microsecond=0)
            if slot > from_dt:
                return slot
    return None

# ── Runner ─────────────────────────────────────────────────────────────────────
def run_platform(platform, cfg):
    cmd = [sys.executable, str(SCRIPT_DIR / cfg['script'])] + cfg['cmd'] + ['--limit', str(cfg['limit'])]
    print(f'  Running: {" ".join(cmd[1:])}')
    r = subprocess.run(cmd, capture_output=False)
    return r.returncode == 0

# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_status(args):
    now = datetime.now(TZ_LOCAL)
    print(f'\n  ⏰ Schedule Status  |  {now.strftime("%Y-%m-%d %H:%M")} ({DAY_NAMES[now.weekday()]})\n')
    print(f'  {"Platform":<12} {"Hôm nay":^8} {"Giờ đăng":<20} {"Tiếp theo"}')
    print(f'  {"─"*65}')

    for platform, cfg in SCHEDULE.items():
        icon    = PLATFORM_ICONS[platform]
        active  = now.weekday() in cfg['days']
        hours   = ', '.join(f'{h:02d}:00' for h in cfg['hours'])
        ran_today = sum(1 for h in cfg['hours'] if already_ran(platform, h))
        nxt   = next_slot(platform, cfg, now)
        nxt_s = nxt.strftime('%m/%d %H:%M') if nxt else '─'
        act_s = f'active ({ran_today}/{len(cfg["hours"])} done)' if active else 'rest day'
        print(f'  {icon} {platform:<10} {act_s:<18} {hours:<20} {nxt_s}')

    print()

def cmd_next(args):
    now = datetime.now(TZ_LOCAL)
    slots = []
    for platform, cfg in SCHEDULE.items():
        nxt = next_slot(platform, cfg, now)
        if nxt: slots.append((nxt, platform))
    slots.sort()
    print(f'\n  ⏰ Lần chạy tiếp theo:\n')
    for dt, platform in slots[:5]:
        icon = PLATFORM_ICONS[platform]
        diff = dt - now
        mins = int(diff.total_seconds() / 60)
        print(f'  {icon} {platform:<12} {dt.strftime("%m/%d %H:%M")}  (sau {mins} phút)')
    print()

def cmd_plan(args):
    days  = getattr(args, 'days', 7)
    now   = datetime.now(TZ_LOCAL)
    print(f'\n  📅 Kế hoạch {days} ngày tới:\n')
    current = now
    for _ in range(days):
        day = current.replace(hour=0, minute=0, second=0, microsecond=0)
        today_slots = []
        for platform, cfg in SCHEDULE.items():
            if day.weekday() in cfg['days']:
                for h in cfg['hours']:
                    slot = day.replace(hour=h)
                    if slot > now:
                        today_slots.append((h, platform, cfg['limit']))
        if today_slots:
            today_slots.sort()
            print(f'  {DAY_NAMES[day.weekday()]} {day.strftime("%m/%d")}:')
            for h, platform, limit in today_slots:
                icon = PLATFORM_ICONS[platform]
                print(f'    {h:02d}:00  {icon} {platform} (max {limit} posts)')
            print()
        current += timedelta(days=1)

def cmd_run(args):
    """Loop liên tục, chạy platforms khi đến giờ."""
    print(f'\n  🔄 Scheduler running — Ctrl+C để dừng\n')
    while True:
        now = datetime.now(TZ_LOCAL)
        ran_any = False
        for platform, cfg in SCHEDULE.items():
            if should_run_now(platform, cfg, now):
                icon = PLATFORM_ICONS[platform]
                print(f'\n  {icon} [{now.strftime("%H:%M")}] Running {platform}…')
                ok = run_platform(platform, cfg)
                mark_ran(platform, now.hour, 'ok' if ok else 'err')
                ran_any = True

        if not ran_any:
            # Sleep until next minute
            sleep_secs = 60 - datetime.now(TZ_LOCAL).second
            print(f'  ⏳ {now.strftime("%H:%M")} — chờ {sleep_secs}s…', end='\r')
            time.sleep(sleep_secs)

def cmd_install(args):
    """Cài Windows Task Scheduler để tự động chạy scheduler.py mỗi giờ."""
    script_path = SCRIPT_DIR / 'scheduler.py'
    python_path = sys.executable

    # Create task: runs every hour from 7am to 11pm
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2026-01-01T07:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" run-once</Arguments>
      <WorkingDirectory>{ROOT}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
</Task>"""

    xml_path = SCRIPT_DIR / 'scheduler_task.xml'
    xml_path.write_text(task_xml, encoding='utf-16')

    print('\n  Cài Windows Task Scheduler:')
    print(f'  Task XML: {xml_path}')

    try:
        result = subprocess.run(
            ['schtasks', '/Create', '/TN', 'RankerToolAI_Scheduler',
             '/XML', str(xml_path), '/F'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print('  ✓ Task đã được cài đặt: RankerToolAI_Scheduler')
            print('  ✓ Chạy mỗi giờ từ 7am → 11pm, tự động post khi đến giờ peak')
        else:
            print(f'  ✗ Lỗi: {result.stderr}')
            print(f'\n  Thử thủ công:')
            print(f'  schtasks /Create /TN RankerToolAI_Scheduler /XML "{xml_path}" /F')
    except FileNotFoundError:
        print('  ✗ schtasks không tìm thấy — chạy thủ công:')
        print(f'  {python_path} "{script_path}" run-once')
    print()

def cmd_run_once(args):
    """Kiểm tra và chạy platforms cần chạy ngay lúc này (gọi bởi Task Scheduler)."""
    now = datetime.now(TZ_LOCAL)
    ran = []
    for platform, cfg in SCHEDULE.items():
        if should_run_now(platform, cfg, now):
            ok = run_platform(platform, cfg)
            mark_ran(platform, now.hour, 'ok' if ok else 'err')
            ran.append(f'{platform}:{"ok" if ok else "err"}')
    if ran:
        print(f'[{now.strftime("%Y-%m-%d %H:%M")}] Ran: {", ".join(ran)}')

def main():
    p = argparse.ArgumentParser(description='RankerToolAI Content Scheduler')
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('status')
    sub.add_parser('next')
    sub.add_parser('run')
    sub.add_parser('install')
    sub.add_parser('run-once')
    pp = sub.add_parser('plan')
    pp.add_argument('--days', type=int, default=7)
    args = p.parse_args()
    cmds = {
        'status':   cmd_status,
        'next':     cmd_next,
        'run':      cmd_run,
        'install':  cmd_install,
        'run-once': cmd_run_once,
        'plan':     cmd_plan,
    }
    cmds.get(args.cmd, lambda _: p.print_help())(args)

if __name__ == '__main__': main()
