"""
Auto-post to Twitter/X using OAuth 2.0 (with refresh token support).
"""

import os, json, time, sqlite3, requests
from dotenv import load_dotenv, set_key
load_dotenv()

try:
    import tweepy
except ImportError:
    print("Install tweepy: pip install tweepy")
    exit(1)

CLIENT_ID     = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
ACCESS_TOKEN  = os.getenv("TWITTER_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("TWITTER_REFRESH_TOKEN")

TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")
DB_FILE    = os.path.join(os.path.dirname(__file__), "data", "posts.db")
ENV_FILE   = os.path.join(os.path.dirname(__file__), ".env")

READY_TWEETS = [
    "Just published: ElevenLabs review after 30 days of real testing.\n\nScore: 9.2/10 — still the best AI voice generator by a significant margin.\n\nKey finding: 12/15 people couldn't tell it was AI-generated audio.\n\nhttps://rankertoolai.com/review/elevenlabs/\n\n#AIVoice #ElevenLabs #AITools",

    "Semrush vs every other SEO tool I've tested:\n\nSemrush: 9.3/10\nAhrefs: 8.7/10\nMoz: 7.9/10\nSE Ranking: 7.6/10\n\nThe keyword database size and accuracy gap is real.\n\nFull comparison: https://rankertoolai.com/review/semrush/\n\n#SEO #Semrush #DigitalMarketing",

    "Cursor vs GitHub Copilot — I used both for 60 days.\n\nCursor acceptance rate: 68%\nCopilot acceptance rate: 52%\n\nThe Composer feature edited 8 files simultaneously.\n\nhttps://rankertoolai.com/compare/cursor-vs-github-copilot/\n\n#Cursor #AICode",

    "Surfer SEO experiment results after 90 days:\n\nWith Surfer: 7/10 articles hit page 1\nWithout Surfer: 3/10 articles hit page 1\n\nFull data: https://rankertoolai.com/review/surfer-seo/\n\n#SurferSEO #SEO #ContentMarketing",

    "AI tools I'd pay for again in 2026:\n\n1. ElevenLabs (9.2/10)\n2. Semrush (9.3/10)\n3. Cursor (9.2/10)\n4. Surfer SEO (9.0/10)\n5. Stable Diffusion (8.9/10)\n\nAll reviews: https://rankertoolai.com\n\n#AITools",

    "Hot take: Most AI tool reviews are affiliate content written without using the tool.\n\nWe test everything for 30+ days.\n\nhttps://rankertoolai.com\n\n#AITools #HonestReview",

    "ChatGPT vs Gemini — 50 identical tests:\n\nWriting: ChatGPT\nCoding: Tie\nAnalysis: Gemini\nResearch: Gemini\nCreative: ChatGPT\n\nFull breakdown: https://rankertoolai.com/compare/chatgpt-vs-gemini/\n\n#ChatGPT #Gemini",

    "Stable Diffusion is free. Midjourney is $10/mo.\n\nQuality gap in 2026: smaller than you think.\n\nhttps://rankertoolai.com/review/stable-diffusion/\n\n#StableDiffusion #AIArt",

    "Jasper AI hallucinated on 8% of test prompts.\nWritesonic: 11%\nChatGPT: 6%\nClaude: 4%\n\nAlways fact-check AI-written content.\n\nhttps://rankertoolai.com/review/jasper/\n\n#AIWriting",

    "Runway ML Gen-3 Alpha can generate footage that passes as real on YouTube.\n\nScore: 8.5/10\n\nhttps://rankertoolai.com/review/runway/\n\n#RunwayML #AIVideo",
]

def refresh_access_token():
    """Use refresh token to get new access token."""
    r = requests.post(
        "https://api.twitter.com/2/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
        timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        new_token   = data.get("access_token")
        new_refresh = data.get("refresh_token", REFRESH_TOKEN)
        # Save to .env
        set_key(ENV_FILE, "TWITTER_ACCESS_TOKEN", new_token)
        set_key(ENV_FILE, "TWITTER_REFRESH_TOKEN", new_refresh)
        print(f"  Token refreshed successfully")
        return new_token
    else:
        print(f"  Token refresh failed: {r.status_code} {r.text[:100]}")
        return None

def post_tweet(text, token=None):
    t = token or ACCESS_TOKEN
    r = requests.post(
        "https://api.twitter.com/2/tweets",
        headers={"Authorization": f"Bearer {t}", "Content-Type": "application/json"},
        json={"text": text[:280]},
        timeout=15
    )
    if r.status_code == 201:
        return r.json()["data"]["id"]
    if r.status_code == 401:
        print("  Token expired, refreshing...")
        new_token = refresh_access_token()
        if new_token:
            return post_tweet(text, token=new_token)
    print(f"  Error {r.status_code}: {r.text[:150]}")
    return None

def already_posted(slug):
    try:
        conn = sqlite3.connect(DB_FILE)
        r = conn.execute(
            "SELECT id FROM posts WHERE platform='twitter' AND tool_slug=?", (slug,)
        ).fetchone()
        conn.close()
        return r is not None
    except:
        return False

def log_post(slug, tweet_id=""):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute(
            "INSERT OR IGNORE INTO posts (platform, tool_slug, url, posted_at) VALUES (?,?,?,datetime('now'))",
            ("twitter", slug, f"https://twitter.com/rankertoolai/status/{tweet_id}")
        )
        conn.commit()
        conn.close()
    except:
        pass

def post_ready_tweets(count=1, no_wait=False):
    queued = []
    for i, tweet in enumerate(READY_TWEETS):
        slug = f"ready_{i}"
        if not already_posted(slug):
            queued.append((slug, tweet))

    if not queued:
        print("All ready tweets already posted.")
        return

    for i, (slug, tweet) in enumerate(queued[:count]):
        print(f"\n[{i+1}/{min(count, len(queued))}] Posting...")
        print(f"  Preview: {tweet[:80]}...")
        tid = post_tweet(tweet)
        if tid:
            url = f"https://twitter.com/rankertoolai/status/{tid}"
            print(f"  Posted: {url}")
            log_post(slug, tid)
        if i < count - 1 and not no_wait:
            print("  Waiting 30 min before next tweet...")
            time.sleep(1800)

if __name__ == "__main__":
    import sys
    dry_run  = "--dry-run" in sys.argv
    no_wait  = "--no-wait" in sys.argv
    count    = 1
    for a in sys.argv:
        if a.startswith("--count="):
            count = int(a.split("=")[1])

    if dry_run:
        print("DRY RUN — tweets to post:")
        for i, t in enumerate(READY_TWEETS[:count]):
            print(f"\n--- [{i+1}] ---\n{t}")
        sys.exit(0)

    if not ACCESS_TOKEN and not REFRESH_TOKEN:
        print("No TWITTER_ACCESS_TOKEN or TWITTER_REFRESH_TOKEN in .env")
        sys.exit(1)

    post_ready_tweets(count=count, no_wait=no_wait)
