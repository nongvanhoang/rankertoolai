import requests
import os
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

def post(tool):
    if already_posted("pinterest", tool["slug"], days=14):
        print(f"[Pinterest] Already posted {tool['name']} recently, skipping")
        return

    if has_recent_error("pinterest", tool["slug"], hours=24):
        print(f"[Pinterest] Recent error for {tool['name']}, cooling down 24h")
        return

    try:
        token = os.getenv("PINTEREST_ACCESS_TOKEN")
        board_id = os.getenv("PINTEREST_BOARD_ID")

        raw = generate_content("pinterest", tool)
        lines = raw.strip().split("\n")
        title = lines[0].strip().lstrip("#").strip()[:100]
        description = " ".join(lines[1:]).strip()[:500]

        # Use OG image from site
        og_image = f"https://rankertoolai.com/assets/images/og-image.png"

        payload = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "link": tool["url"],
            "media_source": {
                "source_type": "image_url",
                "url": og_image
            }
        }

        r = requests.post(
            "https://api.pinterest.com/v5/pins",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        r.raise_for_status()
        data = r.json()
        pin_id = data.get("id", "")
        url = f"https://pinterest.com/pin/{pin_id}/"

        log_post("pinterest", tool["slug"], "pin", pin_id, url)
        print(f"[Pinterest] Pinned: {url}")
        return url

    except Exception as e:
        log_post("pinterest", tool["slug"], "pin", status="error", error=str(e))
        print(f"[Pinterest] Error: {e}")
        return None
