"""Auto-post AI tool reviews to Discord channel using Claude.

Usage:
  python post_discord.py           -- post for least-posted tool
  python post_discord.py --all     -- post for all tools
  python post_discord.py --tool jasper
"""
import os, sys, json, time, requests
from dotenv import load_dotenv
load_dotenv()

from content_generator import generate_content
from database import log_post, already_posted, get_least_posted_tool

TOKEN       = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_IDS = [c.strip() for c in os.getenv("DISCORD_CHANNEL_IDS", "").split(",") if c.strip()]
BASE        = "https://discord.com/api/v10"
HEADERS     = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
DIR         = os.path.dirname(__file__)
TOOLS_FILE  = os.path.join(DIR, "data", "tools.json")

SCORE_EMOJI = {9.3: "🏆", 9.2: "⭐", 9.0: "⭐", 8.9: "✅", 8.7: "✅", 8.4: "👍"}

def format_discord_message(tool, body):
    emoji = SCORE_EMOJI.get(tool["score"], "📊")
    header = (f"{emoji} **{tool['name']} — {tool['score']}/10**\n"
              f"*{tool['tagline']}*\n\n")
    footer = f"\n\n🔗 Full review: {tool['url']}"
    return header + body.strip() + footer

def post_to_discord(message):
    results = []
    for ch_id in CHANNEL_IDS:
        r = requests.post(
            f"{BASE}/channels/{ch_id}/messages",
            json={"content": message[:2000]},
            headers=HEADERS,
            timeout=15
        )
        if r.status_code == 200:
            msg_id = r.json().get("id")
            url = f"https://discord.com/channels/{os.getenv('DISCORD_GUILD_ID')}/{ch_id}/{msg_id}"
            results.append(url)
            print(f"[Discord] Posted to {ch_id}: {msg_id}")
        else:
            print(f"[Discord] Failed {ch_id}: {r.status_code} {r.text[:80]}")
    return results

def run_tool(tool):
    if already_posted("discord", tool["slug"], days=5):
        print(f"[Discord] {tool['name']}: posted in last 5 days, skipping")
        return False

    print(f"[Discord] Generating for {tool['name']}...")
    try:
        body = generate_content("discord", tool)
        message = format_discord_message(tool, body)
        urls = post_to_discord(message)
        if urls:
            log_post("discord", tool["slug"], urls[0])
            return True
    except Exception as e:
        print(f"[Discord] Error: {e}")
    return False

def main():
    with open(TOOLS_FILE, encoding="utf-8") as f:
        tools = json.load(f)

    if not CHANNEL_IDS:
        print("No DISCORD_CHANNEL_IDS in .env")
        return

    run_all  = "--all" in sys.argv
    force_slug = None
    if "--tool" in sys.argv:
        idx = sys.argv.index("--tool")
        if idx + 1 < len(sys.argv):
            force_slug = sys.argv[idx + 1]

    if force_slug:
        matches = [t for t in tools if t["slug"] == force_slug]
        if matches:
            run_tool(matches[0])
        return

    if run_all:
        for tool in tools:
            run_tool(tool)
            time.sleep(5)
        return

    # Default: post for least-posted tool
    slugs = [t["slug"] for t in tools]
    best = get_least_posted_tool(slugs, "discord")
    matches = [t for t in tools if t["slug"] == best]
    if matches:
        run_tool(matches[0])

if __name__ == "__main__":
    main()
