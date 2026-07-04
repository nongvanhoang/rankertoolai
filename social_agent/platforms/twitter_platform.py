import requests
import os
import time
import json
from pathlib import Path
from content_generator import generate_content
from database import log_post, already_posted

TOKEN_CACHE = Path(__file__).parent.parent / "data" / "twitter_token.json"

def _refresh_access_token():
    """Get fresh access token using refresh token (OAuth 2.0 PKCE)."""
    client_id     = os.getenv("TWITTER_CLIENT_ID")
    client_secret = os.getenv("TWITTER_CLIENT_SECRET")
    refresh_token = os.getenv("TWITTER_REFRESH_TOKEN", "").strip("'\"")

    if not refresh_token:
        return None

    r = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        data={
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if r.status_code != 200:
        print(f"[Twitter] Token refresh failed {r.status_code}: {r.text[:200]}")
        return None

    data = r.json()
    access_token  = data.get("access_token")
    new_refresh   = data.get("refresh_token")

    # Cache tokens to disk so next run re-uses them
    TOKEN_CACHE.write_text(json.dumps({"access_token": access_token, "refresh_token": new_refresh}))

    # Patch env for this process
    if new_refresh:
        os.environ["TWITTER_REFRESH_TOKEN"] = new_refresh

    return access_token


def _get_access_token():
    """Return a valid access token (cache → refresh)."""
    if TOKEN_CACHE.exists():
        try:
            cached = json.loads(TOKEN_CACHE.read_text())
            return cached.get("access_token")
        except Exception:
            pass
    return _refresh_access_token()


def _post_tweet(access_token, text):
    r = requests.post(
        "https://api.twitter.com/2/tweets",
        json={"text": text[:280]},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        },
    )
    return r


def post(tool):
    if already_posted("twitter", tool["slug"], days=3):
        print(f"[Twitter] Already posted {tool['name']} in last 3 days, skipping")
        return

    try:
        access_token = _get_access_token()
        if not access_token:
            # Fallback: try refresh
            access_token = _refresh_access_token()
        if not access_token:
            print("[Twitter] No access token available — need TWITTER_REFRESH_TOKEN in .env")
            return

        raw = generate_content("twitter", tool)
        tweets = [t.strip() for t in raw.split("---") if t.strip()]
        tweet_ids = []
        reply_to  = None

        for tweet_text in tweets[:3]:
            payload = {"text": tweet_text[:280]}
            if reply_to:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to}

            r = _post_tweet(access_token, tweet_text[:280])

            # If 401 → token expired, refresh and retry once
            if r.status_code == 401:
                print("[Twitter] Token expired, refreshing...")
                TOKEN_CACHE.unlink(missing_ok=True)
                access_token = _refresh_access_token()
                if not access_token:
                    print("[Twitter] Refresh failed — cannot post")
                    return
                r = _post_tweet(access_token, tweet_text[:280])

            if r.status_code in (200, 201):
                tweet_id = r.json()["data"]["id"]
                tweet_ids.append(tweet_id)
                reply_to = tweet_id
                print(f"[Twitter] Tweet posted: {tweet_id}")
                time.sleep(3)
            else:
                print(f"[Twitter] Failed tweet: {r.status_code} — {r.text[:200]}")
                break

        if tweet_ids:
            url = f"https://twitter.com/rankertoolai/status/{tweet_ids[0]}"
            log_post("twitter", tool["slug"], "thread", str(tweet_ids[0]), url)
            print(f"[Twitter] Thread: {url}")
            return url

    except Exception as e:
        log_post("twitter", tool["slug"], "thread", status="error", error=str(e))
        print(f"[Twitter] Error: {e}")
        return None
