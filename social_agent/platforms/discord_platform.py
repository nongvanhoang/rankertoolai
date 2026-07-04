import requests
import os
import json
from content_generator import generate_content
from database import log_post, already_posted

def post(tool):
    if already_posted("discord", tool["slug"], days=5):
        print(f"[Discord] Already posted {tool['name']} recently, skipping")
        return

    try:
        token = os.getenv("DISCORD_BOT_TOKEN")
        channel_ids_raw = os.getenv("DISCORD_CHANNEL_IDS", "")
        channel_ids = [c.strip() for c in channel_ids_raw.split(",") if c.strip()]

        if not channel_ids:
            print("[Discord] No channel IDs configured")
            return

        content = generate_content("discord", tool)
        headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}

        posted_urls = []
        for channel_id in channel_ids:
            r = requests.post(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                json={"content": content},
                headers=headers
            )
            if r.status_code == 200:
                msg_id = r.json().get("id")
                url = f"https://discord.com/channels/{channel_id}/{msg_id}"
                log_post("discord", tool["slug"], "message", msg_id, url)
                print(f"[Discord] Posted to channel {channel_id}: {msg_id}")
                posted_urls.append(url)

        return posted_urls[0] if posted_urls else None

    except Exception as e:
        log_post("discord", tool["slug"], "message", status="error", error=str(e))
        print(f"[Discord] Error: {e}")
        return None
