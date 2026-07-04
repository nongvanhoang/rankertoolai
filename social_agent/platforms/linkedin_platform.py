import requests
import os
import json
from pathlib import Path
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

TOKEN_FILE = Path(__file__).resolve().parent.parent / "linkedin_tokens.json"


def _load_token():
    """Read token from linkedin_tokens.json, fallback to env var."""
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text())
            token = data.get("access_token", "")
            urn = data.get("person_urn", "")
            if token and urn:
                return token, urn
        except Exception:
            pass
    return os.getenv("LINKEDIN_ACCESS_TOKEN", ""), os.getenv("LINKEDIN_PERSON_URN", "")


def post(tool):
    if already_posted("linkedin", tool["slug"], days=7):
        print(f"[LinkedIn] Already posted {tool['name']} this week, skipping")
        return

    if has_recent_error("linkedin", tool["slug"], hours=24):
        print(f"[LinkedIn] Recent error for {tool['name']}, cooling down 24h")
        return

    token, person_urn = _load_token()

    if not token or not person_urn:
        print("[LinkedIn] No token — run: python social_agent/linkedin_poster.py auth")
        return

    # Strip the full URN prefix if present (API expects just the ID in author field)
    author_urn = person_urn if person_urn.startswith("urn:li:") else f"urn:li:person:{person_urn}"

    try:
        content = generate_content("linkedin", tool)

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        r = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
        )
        r.raise_for_status()
        post_id = r.headers.get("x-restli-id", "")
        url = f"https://www.linkedin.com/feed/update/{post_id}/"

        log_post("linkedin", tool["slug"], "post", post_id, url)
        print(f"[LinkedIn] Posted: {url}")
        return url

    except Exception as e:
        log_post("linkedin", tool["slug"], "post", status="error", error=str(e))
        print(f"[LinkedIn] Error: {e}")
        return None
