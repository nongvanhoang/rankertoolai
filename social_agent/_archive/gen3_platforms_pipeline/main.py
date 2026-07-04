"""
RankerToolAI Social Media Auto-Post Agent
Generates platform-specific content using Claude AI and posts to 10+ platforms.

Usage:
  python main.py                    # Run once for today's tool
  python main.py --tool elevenlabs  # Run for specific tool
  python main.py --platform reddit  # Run only one platform
    python main.py --campaign         # Generate a social campaign pack
  python main.py --schedule         # Run on schedule (daily)
  python main.py --stats            # Show posting statistics
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_stats, get_least_posted_tool

TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")

def load_tools():
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_tool(tools, force_slug=None):
    if force_slug:
        matches = [t for t in tools if t["slug"] == force_slug]
        return matches[0] if matches else tools[0]
    slugs = [t["slug"] for t in tools]
    best_slug = get_least_posted_tool(slugs)
    matches = [t for t in tools if t["slug"] == best_slug]
    return matches[0] if matches else random.choice(tools)

def run_platform(platform_name, tool):
    enabled_key = f"{platform_name.upper()}_ENABLED"
    if os.getenv(enabled_key, "true").lower() == "false":
        print(f"[{platform_name}] Disabled in config, skipping")
        return

    print(f"\n{'='*50}")
    print(f"Posting to {platform_name.upper()} — Tool: {tool['name']}")
    print(f"{'='*50}")

    try:
        if platform_name == "reddit":
            from platforms.reddit_platform import post
            required = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]
        elif platform_name == "twitter":
            from platforms.twitter_platform import post
            required = ["TWITTER_API_KEY", "TWITTER_ACCESS_TOKEN"]
        elif platform_name == "devto":
            from platforms.devto_platform import post
            required = ["DEVTO_API_KEY"]
        elif platform_name == "medium":
            from platforms.medium_platform import post
            required = ["MEDIUM_ACCESS_TOKEN"]
        elif platform_name == "linkedin":
            from platforms.linkedin_platform import post
            # LinkedIn reads from linkedin_tokens.json — check that instead of env vars
            _li_file = os.path.join(os.path.dirname(__file__), "linkedin_tokens.json")
            if not os.path.exists(_li_file):
                print(f"[linkedin] No token file — run: python social_agent/linkedin_poster.py auth")
                return
            required = []
        elif platform_name == "threads":
            from platforms.threads_platform import post
            # Threads reads from threads_tokens.json
            _th_file = os.path.join(os.path.dirname(__file__), "threads_tokens.json")
            if not os.path.exists(_th_file):
                print(f"[threads] No token file — run: python social_agent/threads_poster.py auth")
                return
            required = []
        elif platform_name == "pinterest":
            from platforms.pinterest_platform import post
            required = ["PINTEREST_ACCESS_TOKEN", "PINTEREST_BOARD_ID"]
        elif platform_name == "discord":
            from platforms.discord_platform import post
            required = ["DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_IDS"]
        elif platform_name == "hashnode":
            from platforms.hashnode_platform import post
            required = ["HASHNODE_ACCESS_TOKEN", "HASHNODE_PUBLICATION_ID"]
        elif platform_name == "quora":
            from platforms.quora_platform import post
            required = []
        else:
            print(f"Unknown platform: {platform_name}")
            return

        missing = [k for k in required if not os.getenv(k)]
        if missing:
            print(f"[{platform_name}] Missing API keys: {', '.join(missing)} — skipping")
            return

        result = post(tool)
        if result:
            print(f"[{platform_name}] SUCCESS: {result}")
        return result

    except Exception as e:
        print(f"[{platform_name}] FAILED: {e}")
        return None

ALL_PLATFORMS = [
    "devto",       # API key — active
    "hashnode",    # API key
    "medium",      # Access token
    "twitter",     # OAuth — active
    "reddit",      # OAuth
    "linkedin",    # JSON token — active
    "threads",     # JSON token (Meta)
    "pinterest",   # OAuth
    "discord",     # Bot token — active
    "quora",       # Browser automation — active
]

def run_all(tool, only_platform=None):
    platforms = [only_platform] if only_platform else ALL_PLATFORMS
    results = {}

    for i, platform in enumerate(platforms):
        result = run_platform(platform, tool)
        results[platform] = result

        # Delay between platforms to avoid rate limits
        if i < len(platforms) - 1:
            delay = random.randint(30, 90)
            print(f"\nWaiting {delay}s before next platform...")
            time.sleep(delay)

    return results

def show_stats():
    stats = get_stats()
    print("\n[STATS] POSTING STATISTICS")
    print(f"{'Platform':<15} {'Total':<10} {'Success':<10}")
    print("-" * 35)
    for platform, total, success in stats:
        print(f"{platform:<15} {total:<10} {success:<10}")

def run_scheduled():
    import schedule

    def daily_job():
        print(f"\n[START] Daily run started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        tools = load_tools()
        tool = pick_tool(tools)
        print(f"Today's featured tool: {tool['name']} ({tool['score']}/10)")
        run_all(tool)
        print(f"\n[DONE] Daily run complete: {datetime.now().strftime('%H:%M')}")

    schedule.every().day.at("09:00").do(daily_job)
    schedule.every().day.at("15:00").do(daily_job)

    print("🕐 Scheduler started. Runs at 09:00 and 15:00 daily.")
    print("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    parser = argparse.ArgumentParser(description="RankerToolAI Social Media Agent")
    parser.add_argument("--tool", help="Specific tool slug to post about")
    parser.add_argument("--platform", help="Post to only one platform")
    parser.add_argument("--campaign", action="store_true", help="Build a social media campaign pack")
    parser.add_argument("--schedule", action="store_true", help="Run on schedule")
    parser.add_argument("--stats", action="store_true", help="Show posting stats")
    parser.add_argument("--dry-run", action="store_true", help="Generate content but don't post")
    args = parser.parse_args()

    init_db()

    if args.stats:
        show_stats()
        return

    if args.schedule:
        run_scheduled()
        return

    if args.campaign:
        from social_campaign import build_campaign

        tools = load_tools()
        tool = pick_tool(tools, force_slug=args.tool)
        campaign_path = build_campaign(tool)
        print(f"\n[DONE] Campaign pack generated at: {campaign_path}")
        return

    tools = load_tools()
    tool = pick_tool(tools, force_slug=args.tool)

    print(f"\n[AGENT] RankerToolAI Social Agent")
    print(f"Tool: {tool['name']} | Score: {tool['score']}/10 | Category: {tool['category']}")
    print(f"Target: {tool['url']}\n")

    if args.dry_run:
        from content_generator import generate_content
        platform = args.platform or "twitter"
        print(f"--- DRY RUN: {platform.upper()} ---")
        content = generate_content(platform, tool)
        print(content)
        return

    run_all(tool, only_platform=args.platform)
    print("\n[DONE] All platforms processed!")

if __name__ == "__main__":
    main()
