"""
Master automation runner — chạy tất cả social platforms theo lịch.
Windows Task Scheduler gọi script này mỗi ngày.

Usage:
  python run_all.py            -- chạy theo lịch hôm nay
  python run_all.py --force    -- chạy tất cả bất kể lịch
  python run_all.py --status   -- xem trạng thái
"""

import os, sys, json, datetime, subprocess, sqlite3
from dotenv import load_dotenv
load_dotenv()

DIR      = os.path.dirname(__file__)
DB_FILE  = os.path.join(DIR, "data", "posts.db")
LOG_FILE = os.path.join(DIR, "data", "run_log.txt")

# Lịch chạy theo ngày trong tuần (0=Mon, 6=Sun)
SCHEDULE = {
    "devto":     [0, 2, 4],               # Mon, Wed, Fri
    "quora":     [1, 3, 5],               # Tue, Thu, Sat
    "discord":   [0, 1, 2, 3, 4, 5, 6],  # Mỗi ngày
    "twitter":   [0, 1, 2, 3, 4, 5, 6],  # Mỗi ngày
    "reddit":    [0, 2, 4],               # Mon, Wed, Fri
    "pinterest": [0, 3],                  # Mon, Thu
    "linkedin":  [1, 4],                  # Tue, Fri
    "instagram": [0, 2, 4, 6],            # Mon, Wed, Fri, Sun
    "youtube":   [2],                     # Wed
}

PLATFORMS = {
    "devto":     ("post_devto_auto.py",  ["DEVTO_API_KEY"]),
    "quora":     ("post_quora.py",       ["ANTHROPIC_API_KEY"]),
    "discord":   ("post_discord.py",     ["DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_IDS"]),
    "twitter":   ("post_twitter.py",    ["TWITTER_API_KEY"]),
    "reddit":    ("post_reddit.py",    ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]),
    "pinterest": ("post_pinterest.py", ["PINTEREST_ACCESS_TOKEN"]),
    "linkedin":  ("post_linkedin.py",  ["LINKEDIN_ACCESS_TOKEN"]),
    "instagram": ("post_instagram.py", ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID"]),
    "youtube":   ("post_youtube.py",   ["YOUTUBE_CONFIGURED"]),
}

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def has_credentials(env_keys):
    for k in env_keys:
        if k == "YOUTUBE_CONFIGURED":
            return os.path.exists(os.path.join(DIR, "data", "youtube_token.pkl"))
        if not os.getenv(k):
            return False
    return True

def run_platform(name, script, extra_args=None):
    script_path = os.path.join(DIR, script)
    args = [sys.executable, script_path, "--all"]
    if extra_args:
        args += extra_args
    log(f"Running {name}...")
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode == 0:
        log(f"  {name}: OK")
    else:
        log(f"  {name}: ERROR — {result.stderr[:100]}")
    return result.returncode == 0

def get_stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute(
            "SELECT platform, COUNT(*) as n FROM posts GROUP BY platform ORDER BY n DESC"
        ).fetchall()
        conn.close()
        return rows
    except:
        return []

def main():
    force = "--force" in sys.argv
    status = "--status" in sys.argv

    if status:
        print("\n=== POST STATISTICS ===")
        for platform, count in get_stats():
            print(f"  {platform:<12} {count} posts")
        print()
        print("=== CREDENTIALS STATUS ===")
        for name, (script, keys) in PLATFORMS.items():
            ok = has_credentials(keys)
            print(f"  {name:<12} {'[OK]' if ok else '[MISSING]'}")
        return

    today = datetime.datetime.now().weekday()
    log(f"=== Daily run started (weekday={today}) ===")

    ran = 0
    for name, (script, keys) in PLATFORMS.items():
        if not force and today not in SCHEDULE.get(name, []):
            continue
        if not has_credentials(keys):
            log(f"  {name}: skipped (no credentials)")
            continue
        success = run_platform(name, script)
        if success:
            ran += 1

    log(f"=== Done: {ran} platforms ran ===")

if __name__ == "__main__":
    main()
