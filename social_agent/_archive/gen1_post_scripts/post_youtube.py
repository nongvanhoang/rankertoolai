"""
Auto-upload videos to YouTube via YouTube Data API v3.
Setup:
  1. console.cloud.google.com → New Project → Enable YouTube Data API v3
  2. Credentials → OAuth 2.0 Client ID → Desktop app → Download client_secret.json
  3. Place client_secret.json in social_agent/data/
  4. Run once: python post_youtube.py --auth  (opens browser to authorize)
  5. After auth: python post_youtube.py --all
"""

import os, json, time, pickle
from dotenv import load_dotenv
load_dotenv()

OUT_DIR    = os.path.join(os.path.dirname(__file__), "output")
TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")
DB_FILE    = os.path.join(os.path.dirname(__file__), "data", "posts.db")
SECRET_FILE = os.path.join(os.path.dirname(__file__), "data", "client_secret.json")
TOKEN_FILE  = os.path.join(os.path.dirname(__file__), "data", "youtube_token.pkl")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

VIDEO_DESCRIPTIONS = {
    "elevenlabs": {
        "title": "I Tested ElevenLabs for 30 Days — Honest AI Voice Review (9.2/10)",
        "description": "After 30 days of testing ElevenLabs alongside Murf, Play.ht, and Speechify — here's my honest score and breakdown.\n\n📊 Score: 9.2/10\n✅ Pros: Best voice quality, 99 languages, fast API\n❌ Cons: Limited free tier, no SSML support\n\n🔗 Full review: https://rankertoolai.com/review/elevenlabs/\n🌐 All AI tool reviews: https://rankertoolai.com\n\n⏱️ Timestamps:\n0:00 Introduction\n0:15 Score overview\n0:30 What we loved\n0:45 What could be better\n1:00 Pricing\n1:15 Who should use it\n1:30 Final verdict\n\n#ElevenLabs #AIVoice #TextToSpeech #AITools #AIReview",
        "tags": ["ElevenLabs", "AI voice", "text to speech", "AI tools", "AI review", "voice generator"],
        "category": "28"  # Science & Technology
    },
    "semrush": {
        "title": "Semrush Review 2026 — Is It Worth $129/Month? (9.3/10)",
        "description": "After 90 days of using Semrush as our primary SEO tool, here's the honest verdict.\n\n📊 Score: 9.3/10 — highest rated tool we've tested\n✅ 50 billion keywords, 200+ SEO tools\n✅ Best competitor analysis available\n❌ Expensive for solopreneurs\n\n🔗 Full review: https://rankertoolai.com/review/semrush/\n🌐 rankertoolai.com\n\n#Semrush #SEO #DigitalMarketing #SEOTools #AITools",
        "tags": ["Semrush", "SEO tools", "digital marketing", "keyword research", "AI SEO"],
        "category": "28"
    },
    "cursor": {
        "title": "Cursor vs GitHub Copilot — 60 Days Testing (Cursor 9.2 vs Copilot 8.8)",
        "description": "I used both Cursor and GitHub Copilot as my ONLY coding assistant for 30 days each on a real TypeScript project.\n\n📊 Cursor: 9.2/10 | Copilot: 8.8/10\n\nKey finding: Cursor's Composer edited 8 files simultaneously — took 12 minutes vs 2 hours manually.\n\n🔗 Full comparison: https://rankertoolai.com/compare/cursor-vs-github-copilot/\n\n#Cursor #GitHubCopilot #AICode #Programming #DeveloperTools",
        "tags": ["Cursor", "GitHub Copilot", "AI coding", "developer tools", "programming", "AI code"],
        "category": "28"
    },
    "surfer-seo": {
        "title": "Surfer SEO Review — My 90-Day Experiment With Real Results (9.0/10)",
        "description": "I ran a controlled experiment: 10 articles WITH Surfer SEO vs 10 WITHOUT. Here are the actual ranking results after 90 days.\n\n📊 Score: 9.0/10\nWith Surfer: 7/10 articles hit page 1\nWithout Surfer: 3/10 hit page 1\n\n🔗 Full experiment: https://rankertoolai.com/review/surfer-seo/\n\n#SurferSEO #SEO #ContentMarketing #RankGoogle #SEOTools",
        "tags": ["Surfer SEO", "SEO", "content optimization", "rank on Google", "content marketing"],
        "category": "28"
    },
}

def get_default_description(tool):
    return {
        "title": f"{tool['name']} Review — Is It Worth It? ({tool['score']}/10) | RankerTool AI",
        "description": f"Full review of {tool['name']} after 30+ days of real-world testing.\n\nScore: {tool['score']}/10\nBest for: {tool['best_for']}\nPrice: {tool['price']}\n\nFull review: {tool['url']}\nAll AI reviews: https://rankertoolai.com\n\n{' '.join(tool['hashtags'])}",
        "tags": [tool['name'], "AI tools", "AI review", tool['category']],
        "category": "28"
    }

def get_credentials():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("Install: pip install google-auth google-auth-oauthlib google-api-python-client")
        return None

    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(SECRET_FILE):
                print(f"Missing: {SECRET_FILE}")
                print("Download from: console.cloud.google.com → APIs & Services → Credentials")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds

def upload_video(youtube, video_path, title, description, tags, category="28"):
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("Install: pip install google-api-python-client")
        return None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True,
                            mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    Upload {int(status.progress() * 100)}%")

    return response.get("id")

def already_posted(slug):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        r = conn.execute("SELECT id FROM posts WHERE platform='youtube' AND tool_slug=?", (slug,)).fetchone()
        conn.close()
        return r is not None
    except:
        return False

def log_post(slug, video_id):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT OR IGNORE INTO posts (platform, tool_slug, url, posted_at) VALUES (?,?,?,datetime('now'))",
            ("youtube", slug, f"https://youtube.com/watch?v={video_id}"))
        conn.commit()
        conn.close()
    except: pass

if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", action="store_true", help="Authorize YouTube access")
    parser.add_argument("--all", action="store_true", help="Upload all tool videos")
    parser.add_argument("--tool", help="Upload specific tool slug")
    args = parser.parse_args()

    if not os.path.exists(SECRET_FILE):
        print("""
Missing client_secret.json

Setup:
  1. console.cloud.google.com → Select/Create project
  2. APIs & Services → Library → Search "YouTube Data API v3" → Enable
  3. APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
  4. Application type: Desktop app → Create → Download JSON
  5. Rename file to client_secret.json
  6. Place in: social_agent/data/client_secret.json
  7. Run: python post_youtube.py --auth
""")
        sys.exit(0)

    creds = get_credentials()
    if not creds:
        sys.exit(1)

    try:
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", credentials=creds)
    except ImportError:
        print("Install: pip install google-api-python-client")
        sys.exit(1)

    if args.auth:
        print("YouTube authorized successfully!")
        info = youtube.channels().list(part="snippet", mine=True).execute()
        print(f"Channel: {info['items'][0]['snippet']['title']}")
        sys.exit(0)

    tools = json.load(open(TOOLS_FILE, encoding="utf-8"))
    targets = tools if args.all else [t for t in tools if t["slug"] == args.tool]

    for tool in sorted(targets, key=lambda x: -x["score"]):
        slug = tool["slug"]
        if already_posted(slug):
            print(f"Already uploaded: {slug}")
            continue

        video_path = os.path.join(OUT_DIR, slug, f"{slug}_youtube.mp4")
        if not os.path.exists(video_path):
            print(f"No video for {slug}, run: python content_creator.py --tool {slug} --type video")
            continue

        meta = VIDEO_DESCRIPTIONS.get(slug, get_default_description(tool))
        print(f"\nUploading: {tool['name']} ({meta['title'][:50]}...)")

        vid_id = upload_video(youtube, video_path,
            meta["title"], meta["description"], meta["tags"], meta["category"])

        if vid_id:
            print(f"  Uploaded: https://youtube.com/watch?v={vid_id}")
            log_post(slug, vid_id)
        else:
            print(f"  Failed: {slug}")

        if args.all:
            print("  Waiting 30s before next upload...")
            time.sleep(30)
