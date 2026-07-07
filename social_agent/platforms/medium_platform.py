import requests
import os
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

def post(tool):
    if already_posted("medium", tool["slug"], days=30):
        print(f"[Medium] Already posted {tool['name']} this month, skipping")
        return

    if has_recent_error("medium", tool["slug"], hours=24):
        print(f"[Medium] Recent error for {tool['name']}, cooling down 24h")
        return

    try:
        token = os.getenv("MEDIUM_ACCESS_TOKEN")
        author_id = os.getenv("MEDIUM_AUTHOR_ID")

        if not author_id:
            r = requests.get("https://api.medium.com/v1/me",
                           headers={"Authorization": f"Bearer {token}"})
            author_id = r.json()["data"]["id"]

        content = generate_content("medium", tool)
        lines = content.strip().split("\n")
        title = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()

        payload = {
            "title": title,
            "contentFormat": "markdown",
            "content": f"# {title}\n\n{body}",
            "canonicalUrl": tool["url"],
            "publishStatus": "public",
            "tags": ["ai", "technology", "productivity", "tools"]
        }

        r = requests.post(
            f"https://api.medium.com/v1/users/{author_id}/posts",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        r.raise_for_status()
        data = r.json()["data"]

        url = data.get("url", "")
        log_post("medium", tool["slug"], "article", data.get("id"), url)
        print(f"[Medium] Published: {url}")
        return url

    except Exception as e:
        log_post("medium", tool["slug"], "article", status="error", error=str(e))
        print(f"[Medium] Error: {e}")
        return None
