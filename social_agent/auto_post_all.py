#!/usr/bin/env python3
"""
RankerToolAI — Master Auto-Post Script
Chay: python auto_post_all.py
Hoac lich theo ngay qua Task Scheduler

Pipeline (tat ca mien phi):
  [1] Zernio    -> LinkedIn + Instagram          (free: 2 accounts)
  [2] Buffer    -> Twitter + Facebook + Pinterest (free: 3 channels)
  [3] Bluesky   -> Bluesky                       (free: AT Protocol)
  [4] Blog      -> Dev.to, Hashnode              (free API keys)
  [5] Fallback  -> Discord, Reddit               (legacy direct API)
"""
import os, sys, time, random
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

from database import init_db, get_least_posted_tool
import json
from pathlib import Path

TOOLS_FILE = Path(__file__).parent / "data" / "tools.json"

# NOTE: devto, discord, linkedin are owned by the scheduler.py / *_poster.py
# pipeline (real working credentials there) — deliberately excluded here to
# avoid double-posting the same tool to the same platform twice a day.
# See social_agent/_archive/README.md for the full split.

# Paused 2026-07-03: Meta flagged the connected Facebook/Instagram account for
# "automated activity" after unrelated browser-automation testing. Zernio posts
# to Facebook+Instagram — keep this off until the account is confirmed stable
# again, to avoid adding more automation signals while the flag is active.
ZERNIO_PAUSED = True

# Blog/writing platforms — always run via individual scripts
BLOG_PLATFORMS = [
    ("hashnode", "Hashnode", ["HASHNODE_ACCESS_TOKEN", "HASHNODE_PUBLICATION_ID"]),
    ("medium",   "Medium",   ["MEDIUM_ACCESS_TOKEN"]),
]

# Legacy social fallbacks — only when main services not configured
LEGACY_SOCIAL = [
    ("reddit",   "Reddit",    ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]),
    ("twitter",  "Twitter",   ["TWITTER_REFRESH_TOKEN"]),
    ("pinterest","Pinterest", ["PINTEREST_ACCESS_TOKEN"]),
]


def load_tools():
    with open(TOOLS_FILE, encoding="utf-8") as f:
        return json.load(f)


def pick_tool(tools, platform):
    slugs = [t["slug"] for t in tools]
    best = get_least_posted_tool(slugs, platform)
    matches = [t for t in tools if t["slug"] == best]
    return matches[0] if matches else random.choice(tools)


def check_keys(required):
    return [k for k in required if not os.getenv(k, "").strip()]


def run_legacy(platform, tool, label=""):
    """Run an individual platform poster."""
    if os.getenv(f"{platform.upper()}_ENABLED", "true").lower() == "false":
        print(f"  [{platform}] Disabled, skip")
        return False
    print(f"\n{'─'*48}")
    print(f"  {label or platform.upper()} -> {tool['name']} ({tool['score']}/10)")
    print(f"{'─'*48}")
    try:
        if platform == "devto":
            from platforms.devto_platform import post
        elif platform == "discord":
            from platforms.discord_platform import post
        elif platform == "reddit":
            from platforms.reddit_platform import post
        elif platform == "medium":
            from platforms.medium_platform import post
        elif platform == "linkedin":
            from platforms.linkedin_platform import post
        elif platform == "hashnode":
            from platforms.hashnode_platform import post
        elif platform == "pinterest":
            from platforms.pinterest_platform import post
        elif platform == "twitter":
            from platforms.twitter_platform import post
        else:
            return False
        result = post(tool)
        if result:
            print(f"  [OK] {result}")
            return True
        return False
    except Exception as e:
        print(f"  [ERR] {e}")
        return False


# ── Service runners ──────────────────────────────────────────────────────────────

# Platforms owned by scheduler.py / *_poster.py — never let Zernio/Buffer post
# to these even if the accounts get connected there later (avoid duplicates).
GEN2_OWNED_PLATFORMS = {"linkedin", "discord", "devto"}


def run_zernio(tools):
    """Post via Zernio. Returns (status, platforms_list).
    status: 'ok' | 'skip' | 'err' | 'no_accounts'
    """
    try:
        from post_zernio import get_account_ids, post_tool as zernio_post
    except ImportError as e:
        print(f"  [Zernio] Import error: {e}")
        return 'err', []

    account_map = get_account_ids()
    account_map = {k: v for k, v in account_map.items() if k not in GEN2_OWNED_PLATFORMS}
    if not account_map:
        return 'no_accounts', []

    tool = pick_tool(tools, "zernio")
    pf_list = list(account_map.keys())
    print(f"\n{'='*48}")
    print(f"  ZERNIO -> {tool['name']} ({tool['score']}/10)")
    print(f"  Platforms: {', '.join(pf_list)}")
    print(f"{'='*48}")
    ok = zernio_post(tool, target_platforms=pf_list)
    # ok=False can mean "skipped today" — either way Zernio covers these platforms
    return ('ok' if ok else 'skip'), pf_list


def run_buffer(tools):
    """Post via Buffer. Returns (status, services_list)."""
    try:
        from post_buffer import get_channel_map, post_tool as buffer_post
    except ImportError as e:
        print(f"  [Buffer] Import error: {e}")
        return 'err', []

    channel_map = get_channel_map()
    channel_map = {k: v for k, v in channel_map.items() if k not in GEN2_OWNED_PLATFORMS}
    if not channel_map:
        return 'no_accounts', []

    tool = pick_tool(tools, "buffer")
    svc_list = list(channel_map.keys())
    print(f"\n{'='*48}")
    print(f"  BUFFER -> {tool['name']} ({tool['score']}/10)")
    print(f"  Channels: {', '.join(svc_list)}")
    print(f"{'='*48}")
    ok = buffer_post(tool)
    return ('ok' if ok else 'skip'), svc_list


def run_bluesky(tools):
    """Post via Bluesky. Returns status string."""
    try:
        from post_bluesky import post_tool as bsky_post
    except ImportError as e:
        print(f"  [Bluesky] Import error: {e}")
        return 'err'

    tool = pick_tool(tools, "bluesky")
    print(f"\n{'='*48}")
    print(f"  BLUESKY -> {tool['name']} ({tool['score']}/10)")
    print(f"{'='*48}")
    ok = bsky_post(tool)
    return 'ok' if ok else 'skip'


# ── Main ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    tools = load_tools()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*48}")
    print(f"  RankerToolAI Auto-Post — {now}")
    print(f"{'='*48}")

    results = {}
    used_platforms = set()

    STATUS_ICON = {'ok': '[OK]', 'skip': '[--]', 'err': '[ERR]', 'no_accounts': '[??]'}

    # ── [1] Zernio: Facebook + Instagram ────────────────────────────────────────
    if ZERNIO_PAUSED:
        print("\n  [Zernio] Paused (Meta automation flag on FB/IG account) — skip")
    elif os.getenv("ZERNIO_API_KEY", "").strip():
        status, covered = run_zernio(tools)
        if status == 'no_accounts':
            print("\n  [Zernio] No accounts connected yet")
        else:
            preview = ', '.join(covered[:3]) + ('...' if len(covered) > 3 else '')
            results["Zernio"] = f"{STATUS_ICON[status]} {preview}"
            used_platforms.update(covered)   # mark as covered even if skipped today
        if covered:
            time.sleep(random.randint(15, 30))
    else:
        print("\n  [Zernio] ZERNIO_API_KEY not set — skip")

    # ── [2] Buffer: Twitter + Facebook + Pinterest ───────────────────────────────
    if os.getenv("BUFFER_API_KEY", "").strip():
        status, covered = run_buffer(tools)
        if status == 'no_accounts':
            print("\n  [Buffer] No channels connected yet")
        else:
            preview = ', '.join(covered[:3]) + ('...' if len(covered) > 3 else '')
            results["Buffer"] = f"{STATUS_ICON[status]} {preview}"
            used_platforms.update(covered)
        if covered:
            time.sleep(random.randint(15, 30))
    else:
        print("\n  [Buffer] BUFFER_API_KEY not set — skip")

    # ── [3] Bluesky: AT Protocol (free) ─────────────────────────────────────────
    if os.getenv("BLUESKY_HANDLE", "").strip() and os.getenv("BLUESKY_APP_PASSWORD", "").strip():
        status = run_bluesky(tools)
        results["Bluesky"] = STATUS_ICON[status]
        used_platforms.add("bluesky")
        if status == 'ok':
            time.sleep(random.randint(10, 20))
    else:
        print("\n  [Bluesky] BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set — skip")

    # ── [4] Blog platforms: Dev.to, Hashnode, Medium ────────────────────────────
    for pid, label, keys in BLOG_PLATFORMS:
        missing = check_keys(keys)
        if missing:
            print(f"\n  [{label}] Skip — need: {', '.join(missing)}")
            continue
        tool = pick_tool(tools, pid)
        ok = run_legacy(pid, tool, label)
        results[label] = "[OK]" if ok else "[ERR]"
        if ok:
            time.sleep(random.randint(15, 30))

    # ── [5] Legacy fallback — only if main services didn't cover these ───────────
    fallback_needed = [
        (pid, label, keys) for pid, label, keys in LEGACY_SOCIAL
        if pid not in used_platforms
    ]
    if fallback_needed:
        print(f"\n  [Fallback] Running legacy scripts for: "
              f"{', '.join(pid for pid, _, _ in fallback_needed)}")
        for pid, label, keys in fallback_needed:
            missing = check_keys(keys)
            if missing:
                print(f"\n  [{label}] Skip — need: {', '.join(missing)}")
                continue
            tool = pick_tool(tools, pid)
            ok = run_legacy(pid, tool, label)
            results[label] = "[OK]" if ok else "[ERR]"
            if ok:
                time.sleep(random.randint(15, 30))

    # ── Summary ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*48}")
    print(f"  KET QUA:")
    for label, status in results.items():
        print(f"    {status:<30}  {label}")
    print(f"  Platforms used: {', '.join(sorted(used_platforms)) or 'none'}")
    print(f"{'='*48}\n")
