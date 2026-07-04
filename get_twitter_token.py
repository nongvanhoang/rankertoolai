"""Get Twitter Access Token via PIN-based OAuth flow."""
import os, webbrowser
from dotenv import load_dotenv
load_dotenv("social_agent/.env")

import tweepy

API_KEY    = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")

if not API_KEY or not API_SECRET:
    print("ERROR: TWITTER_API_KEY or TWITTER_API_SECRET missing in .env")
    exit(1)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, callback="oob")
url  = auth.get_authorization_url()

print("\n=== Lấy Twitter Access Token ===\n")
print("1. Mở link này trong trình duyệt:")
print(f"\n   {url}\n")
webbrowser.open(url)
print("2. Đăng nhập Twitter → Authorize App")
print("3. Copy mã PIN hiện ra\n")

pin = input("Paste PIN vào đây: ").strip()

try:
    access_token, access_secret = auth.get_access_token(pin)
    print(f"\nAccess Token:        {access_token}")
    print(f"Access Token Secret: {access_secret}")

    # Ghi vào .env
    env_path = "social_agent/.env"
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(
        f"TWITTER_ACCESS_TOKEN={os.getenv('TWITTER_ACCESS_TOKEN', '')}",
        f"TWITTER_ACCESS_TOKEN={access_token}"
    )
    content = content.replace(
        f"TWITTER_ACCESS_SECRET={os.getenv('TWITTER_ACCESS_SECRET', '')}",
        f"TWITTER_ACCESS_SECRET={access_secret}"
    )
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\n.env updated! Chạy test:")
    print("  python social_agent/post_twitter.py --dry-run")
except Exception as e:
    print(f"\nERROR: {e}")
    print("Kiểm tra lại PIN hoặc Consumer Key/Secret")
