"""
Setup Discord server for RankerToolAI via API.
Run AFTER creating a Discord bot at discord.com/developers/applications
and adding DISCORD_BOT_TOKEN to .env
"""
import requests
import os
import time
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BASE = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

CHANNELS = [
    {"name": "announcements", "type": 0, "topic": "Latest reviews and updates from RankerToolAI"},
    {"name": "general", "type": 0, "topic": "General chat about AI tools"},
    {"name": "ai-tool-reviews", "type": 0, "topic": "Share and discuss AI tool reviews"},
    {"name": "tool-comparisons", "type": 0, "topic": "Head-to-head AI tool comparisons"},
    {"name": "ask-for-recommendations", "type": 0, "topic": "Ask the community which AI tool to use"},
    {"name": "deals-and-discounts", "type": 0, "topic": "AI tool deals, trials, and discount codes"},
    {"name": "showcase-your-work", "type": 0, "topic": "Share what you built with AI tools"},
]

WELCOME_MSG = """Welcome to **RankerTool AI Community**!

We test 50+ AI tools so you don't have to.

**Get started:**
→ Ask for tool recommendations in #ask-for-recommendations
→ See our latest reviews at https://rankertoolai.com
→ Share what you're building in #showcase-your-work

**Top-rated tools right now:**
- ElevenLabs 9.2/10 — AI Voice
- Semrush 9.3/10 — AI SEO
- Cursor 9.2/10 — AI Coding
- Surfer SEO 9.0/10 — Content SEO"""

def setup_server(guild_id):
    if not TOKEN:
        print("No DISCORD_BOT_TOKEN set in .env")
        return

    print(f"Setting up Discord server {guild_id}...")

    # Create categories and channels
    # Text category
    r = requests.post(f"{BASE}/guilds/{guild_id}/channels",
        json={"name": "COMMUNITY", "type": 4}, headers=HEADERS)
    cat_id = r.json().get("id") if r.status_code in [200,201] else None

    for ch in CHANNELS:
        payload = {**ch, "parent_id": cat_id} if cat_id else ch
        r = requests.post(f"{BASE}/guilds/{guild_id}/channels", json=payload, headers=HEADERS)
        if r.status_code in [200, 201]:
            ch_data = r.json()
            print(f"  Created #{ch['name']} (id: {ch_data.get('id')})")
            # Post welcome in general
            if ch["name"] == "general":
                time.sleep(1)
                requests.post(f"{BASE}/channels/{ch_data['id']}/messages",
                    json={"content": WELCOME_MSG}, headers=HEADERS)
        time.sleep(0.5)

    print("Discord server setup complete!")

if __name__ == "__main__":
    import sys
    guild_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter Discord Server ID: ")
    setup_server(guild_id)
