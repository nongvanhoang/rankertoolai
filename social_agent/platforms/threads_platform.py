"""
Threads (Meta) platform poster.
Uses the Threads API v1.0 with a long-lived token stored in threads_tokens.json.

Setup (one-time):
  1. Create a Meta app at developers.facebook.com → Add Threads API product
  2. Add THREADS_APP_ID and THREADS_APP_SECRET to .env
  3. Run: python social_agent/threads_poster.py auth
  4. threads_tokens.json will be created with the access token

The token file is auto-refreshed if expired (Threads tokens last 60 days).
"""
import requests
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

TOKEN_FILE = Path(__file__).resolve().parent.parent / "threads_tokens.json"
API_BASE = "https://graph.threads.net/v1.0"


def _load_token():
    if not TOKEN_FILE.exists():
        return None, None
    data = json.loads(TOKEN_FILE.read_text())
    return data.get("access_token"), data.get("user_id")


def _refresh_long_lived_token(short_token, app_id, app_secret):
    """Exchange short-lived token for a 60-day long-lived token."""
    r = requests.get(
        "https://graph.threads.net/access_token",
        params={
            "grant_type": "th_exchange_token",
            "client_secret": app_secret,
            "access_token": short_token,
        }
    )
    if r.status_code == 200:
        return r.json().get("access_token")
    return None


def _create_text_container(user_id, token, text):
    """Step 1: Create a media container (text-only post)."""
    r = requests.post(
        f"{API_BASE}/{user_id}/threads",
        params={
            "media_type": "TEXT",
            "text": text[:500],  # Threads text limit is 500 chars
            "access_token": token,
        }
    )
    r.raise_for_status()
    return r.json().get("id")


def _publish_container(user_id, token, container_id):
    """Step 2: Publish the created container."""
    r = requests.post(
        f"{API_BASE}/{user_id}/threads_publish",
        params={
            "creation_id": container_id,
            "access_token": token,
        }
    )
    r.raise_for_status()
    return r.json().get("id")


def post(tool):
    if already_posted("threads", tool["slug"], days=3):
        print(f"[Threads] Already posted {tool['name']} in last 3 days, skipping")
        return

    if has_recent_error("threads", tool["slug"], hours=24):
        print(f"[Threads] Recent error for {tool['name']}, cooling down 24h")
        return

    token, user_id = _load_token()
    if not token or not user_id:
        print("[Threads] No token found — run: python social_agent/threads_poster.py auth")
        return

    try:
        content = generate_content("threads", tool)
        # Threads: 500 char limit — use the first paragraph only
        text = content.strip().split("\n\n")[0][:500]

        container_id = _create_text_container(user_id, token, text)

        # Threads recommends a small delay between create and publish
        import time; time.sleep(3)

        post_id = _publish_container(user_id, token, container_id)
        url = f"https://www.threads.net/@rankertoolai/post/{post_id}"

        log_post("threads", tool["slug"], "post", post_id, url)
        print(f"[Threads] Published: {url}")
        return url

    except requests.exceptions.HTTPError as e:
        # Token might be expired — note it clearly
        if e.response is not None and e.response.status_code in (400, 401):
            print(f"[Threads] Auth error ({e.response.status_code}) — re-run: python social_agent/threads_poster.py auth")
        log_post("threads", tool["slug"], "post", status="error", error=str(e))
        print(f"[Threads] Error: {e}")
        return None
    except Exception as e:
        log_post("threads", tool["slug"], "post", status="error", error=str(e))
        print(f"[Threads] Error: {e}")
        return None
