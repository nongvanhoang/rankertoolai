import requests
import os
from datetime import datetime
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

API_URL = "https://dev.to/api/articles"

# Dev.to rejects articles whose tags contain spaces or uppercase — keep lowercase, no spaces
TAGS = ["ai", "productivity", "tools", "webdev"]

def post(tool):
    if already_posted("devto", tool["slug"], days=30):
        print(f"[Dev.to] Already posted {tool['name']} this month, skipping")
        return

    # Don't retry if it errored in the last 48 hours — prevents 422 spam loops
    if has_recent_error("devto", tool["slug"], hours=48):
        print(f"[Dev.to] Recent error for {tool['name']}, cooling down 48h")
        return

    try:
        content = generate_content("devto", tool)
        lines = content.strip().split("\n")
        title = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()

        # Append month/year to title to prevent duplicate-title 422 rejections
        month_year = datetime.now().strftime("%b %Y")
        if month_year not in title:
            title = f"{title} ({month_year})"

        payload = {
            "article": {
                "title": title,
                "body_markdown": body,
                "published": True,
                "tags": TAGS,
                # canonical_url removed — Dev.to rejects duplicate canonical URLs
                # causing 422 loops when the same tool is retried
            }
        }

        headers = {
            "api-key": os.getenv("DEVTO_API_KEY"),
            "Content-Type": "application/json"
        }

        r = requests.post(API_URL, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

        url = data.get("url", "")
        post_id = str(data.get("id", ""))
        log_post("devto", tool["slug"], "article", post_id, url)
        print(f"[Dev.to] Published: {url}")
        return url

    except Exception as e:
        log_post("devto", tool["slug"], "article", status="error", error=str(e))
        print(f"[Dev.to] Error: {e}")
        return None
