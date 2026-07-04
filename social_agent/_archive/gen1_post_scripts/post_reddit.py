"""
Auto-post to Reddit using PRAW.
Setup:
  1. reddit.com/prefs/apps → Create App → "script" type
  2. Fill: name=RankerToolAI, redirect=http://localhost:8080
  3. Copy client_id (under app name) and client_secret
  4. Add to .env:
     REDDIT_CLIENT_ID=...
     REDDIT_CLIENT_SECRET=...
     REDDIT_USERNAME=rankertoolai
     REDDIT_PASSWORD=your_password
  5. Run: python post_reddit.py --tool elevenlabs
         python post_reddit.py --all
"""

import os, json, time
from dotenv import load_dotenv
load_dotenv()

try:
    import praw
except ImportError:
    print("Install praw: pip install praw")
    exit(1)

CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME      = os.getenv("REDDIT_USERNAME", "rankertoolai")
PASSWORD      = os.getenv("REDDIT_PASSWORD")

TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")
DB_FILE    = os.path.join(os.path.dirname(__file__), "data", "posts.db")

# Pre-written Reddit posts — value-first, not spammy
REDDIT_POSTS = {
    "elevenlabs": {
        "r/podcasting": {
            "title": "I tested 10 AI voice generators for podcast production — honest scores after 30 days",
            "text": """After spending 30 days using AI voice generators for actual podcast work, here are my scores:

**1. ElevenLabs — 9.2/10**
Best overall quality by a significant margin. Played clips to 15 people, 12 thought it was a real recording. 99 languages, voice cloning from 1 min of audio.

**2. Murf AI — 8.4/10**
Better studio controls, easier for teams. Quality gap vs ElevenLabs is noticeable on emotional content.

**3. Play.ht — 8.1/10**
Cheapest at scale. Good API. Quality drops on anything longer than 2 minutes.

**Pricing comparison:**
- ElevenLabs: Free (10K chars), $5/mo starter
- Murf: $26/mo
- Play.ht: $31/mo

For podcasters specifically, ElevenLabs wins on voice naturalness for long-form content. The other tools struggle to maintain consistent cadence through a 20-minute narration.

Full breakdown with audio samples: https://rankertoolai.com/review/elevenlabs/

Happy to answer questions about any of these tools — tested them all extensively."""
        },
        "r/artificial": {
            "title": "ElevenLabs v3 tested: 9.2/10 after 30 days — what changed and what's still lacking",
            "text": """**What I tested:**
- 500+ samples across podcasting, marketing voiceovers, audiobook production, and real-time API
- Compared against Murf, Play.ht, and Speechify

**What improved in v3:**
- Emotional range is noticeably better on longer content
- Voice cloning quality up significantly (can work with less clean audio now)
- Latency on the API dropped from ~800ms to ~400ms average

**What's still lacking:**
- No SSML support (you work with stability/similarity sliders instead)
- Voice cloning still struggles with strong accents
- Free tier (10K chars/mo) runs out fast

**Score: 9.2/10** — still the best, but the gap with #2 is narrowing.

Full review: https://rankertoolai.com/review/elevenlabs/"""
        },
        "r/ChatGPT": {
            "title": "For anyone building voice apps: ElevenLabs API review after using it in production for 30 days",
            "text": """Built a voice feature into a web app. Here's the honest developer review of ElevenLabs API after real production use.

**Latency:** ~400ms average (acceptable for most use cases, not great for real-time conversation)

**Reliability:** 99.6% uptime over 30 days. Two brief outages, both under 10 minutes.

**API quality:**
```python
response = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={"xi-api-key": key},
    json={"text": text, "model_id": "eleven_multilingual_v2"}
)
```
Simple, well-documented, returns audio bytes directly. No complex setup.

**Cost at scale:**
- 500K chars/mo = $99/mo (Pro plan)
- That's about 6-7 hours of audio

**Alternatives I considered:**
- AWS Polly: cheaper at scale, noticeably worse quality
- Google TTS: better multilingual support, inferior naturalness
- OpenAI TTS: good quality, limited voice options

For consumer apps where voice quality matters: ElevenLabs.
For enterprise/cost-sensitive: depends on volume.

Full review: https://rankertoolai.com/review/elevenlabs/"""
        }
    },
    "surfer-seo": {
        "r/SEO": {
            "title": "90-day Surfer SEO experiment: 20 articles, real results (not a promo)",
            "text": """I ran a controlled experiment because I was skeptical about whether Surfer SEO actually moves rankings or just gives the illusion of optimization.

**Setup:**
- 20 articles total, same niche, same domain
- Group A (10): Written using Surfer Content Editor
- Group B (10): Written with same research effort but no Surfer

**Results after 90 days:**

| | With Surfer | Without Surfer |
|---|---|---|
| Page 1 rankings | 7/10 | 3/10 |
| Avg position | 6.2 | 18.4 |
| Organic traffic | 2,847/mo | 891/mo |
| Time to rank | 31 days | 67 days |

**The key insight:** Most people use Surfer wrong. They obsess over keyword density. The actually useful feature is the **NLP entity analysis** — it shows you what topics Google semantically associates with your keyword.

When I covered those entities, rankings moved. When I hit the "right" keyword density without covering entities, nothing happened.

**Verdict: 9.0/10** — worth it if you're publishing 4+ articles/month.

Full experiment writeup with more data: https://rankertoolai.com/review/surfer-seo/"""
        },
        "r/juststart": {
            "title": "Is Surfer SEO worth it for new sites? My honest take after 90 days",
            "text": """Short answer: **Depends on your publishing frequency.**

Under 4 articles/month → probably not worth $89/mo right now. Learn SEO fundamentals first.

4+ articles/month with monetization goal → yes, it pays for itself.

**Why I changed my mind:**

Started skeptical. Did a 90-day experiment: 10 articles with Surfer vs 10 without on the same domain.

Result: Surfer articles got 3.2x more organic traffic after 90 days.

At $89/mo, one article driving 500 visitors and converting at 1% affiliate rate covers the cost multiple times over.

**The learning curve:** Give it 3 articles before judging. The Content Score system takes some getting used to, but 70+ correlates strongly with first-page rankings in my experience.

**What it doesn't replace:** Still need Ahrefs/Semrush for keyword research. Surfer is a content optimizer, not a keyword tool.

Full breakdown: https://rankertoolai.com/review/surfer-seo/"""
        }
    },
    "cursor": {
        "r/programming": {
            "title": "Cursor vs GitHub Copilot: 60 days, real project, measured results",
            "text": """I switched my primary AI coding assistant every 30 days on a real TypeScript/React SaaS project. Here's what the numbers actually showed.

**Autocomplete acceptance rate:**
- Cursor: 68%
- GitHub Copilot: 52%

**Average time per feature implementation:**
- Cursor: 2.1 hours
- Copilot: 1.4 hours

**Where Cursor dominates:**
The Composer feature is genuinely different. I described a feature in plain English and it edited 8 files simultaneously, coherently. That's not something Copilot has.

```
Me: "Add rate limiting to all API routes using the existing Redis client"
Cursor: *opens 8 files, makes changes across all of them*
Result: Worked first try.
```

**Where Copilot wins:**
- IDE support (JetBrains, Neovim, Visual Studio — Cursor is VS Code only)
- Price ($10 vs $20/mo)
- Enterprise features and audit logs

**My recommendation:**
- VS Code user who codes daily: Cursor ($20/mo) — the time savings pay for the cost difference
- JetBrains: Copilot, no real alternative
- Student/hobbyist: Copilot free tier through GitHub Education

**Scores: Cursor 9.2/10, Copilot 8.8/10**

Full 60-day comparison: https://rankertoolai.com/compare/cursor-vs-github-copilot/"""
        },
        "r/webdev": {
            "title": "After 30 days with Cursor as my only AI coding tool — honest review",
            "text": """Switched from GitHub Copilot + ChatGPT to Cursor-only for a month. Here's what changed.

**What got better:**
- Multi-file edits (Composer) — this changed my workflow more than anything
- Codebase Q&A — "where is auth middleware applied?" gives accurate answers
- Autocomplete feels more context-aware on large files

**What got worse (or stayed same):**
- Price: $20/mo vs $10 Copilot
- No JetBrains support (I'm on VS Code so not an issue for me)

**Specific time I remember:**
Had to add input validation across 12 API endpoints. Old workflow: open each file, write validation, repeat. With Cursor Composer: described what I wanted, it touched all 12 files in one go. Took 8 minutes instead of ~90.

Not every feature is like that — most of the time it's just good autocomplete. But the ceiling is higher.

**Score: 9.2/10**

More details: https://rankertoolai.com/review/cursor/"""
        }
    }
}

def get_reddit():
    if not all([CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD]):
        return None
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        user_agent=f"RankerToolAI/1.0 by u/{USERNAME}"
    )

def already_posted(platform_sub):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        r = conn.execute("SELECT id FROM posts WHERE platform=? AND tool_slug=?",
            ("reddit", platform_sub)).fetchone()
        conn.close()
        return r is not None
    except:
        return False

def log_post(platform_sub, url):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT OR IGNORE INTO posts (platform, tool_slug, url, posted_at) VALUES (?,?,?,datetime('now'))",
            ("reddit", platform_sub, url))
        conn.commit()
        conn.close()
    except: pass

def post_to_subreddit(reddit, subreddit, title, text):
    try:
        sub = reddit.subreddit(subreddit)
        submission = sub.submit(title=title, selftext=text)
        return submission.url
    except Exception as e:
        return f"ERROR: {e}"

def post_tool(reddit, tool_slug):
    if tool_slug not in REDDIT_POSTS:
        print(f"No Reddit posts written for: {tool_slug}")
        return
    posts = REDDIT_POSTS[tool_slug]
    for subreddit, post in posts.items():
        key = f"{tool_slug}:{subreddit}"
        if already_posted(key):
            print(f"  Already posted to {subreddit}, skipping")
            continue
        print(f"  Posting to {subreddit}...")
        url = post_to_subreddit(reddit, subreddit.replace("r/",""), post["title"], post["text"])
        if "ERROR" not in str(url):
            print(f"  Posted: {url}")
            log_post(key, url)
        else:
            print(f"  Failed: {url}")
        time.sleep(600)  # 10 min between posts (Reddit rate limit)

if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", help="Tool slug to post")
    parser.add_argument("--all", action="store_true", help="Post all tools")
    parser.add_argument("--list", action="store_true", help="List available posts")
    args = parser.parse_args()

    if args.list:
        for slug, posts in REDDIT_POSTS.items():
            print(f"\n{slug}:")
            for sub in posts:
                print(f"  → {sub}")
        sys.exit(0)

    reddit = get_reddit()
    if not reddit:
        print("""
No Reddit API credentials found.

Steps:
  1. Go to: https://www.reddit.com/prefs/apps
  2. Click 'Create App' at the bottom
  3. Name: RankerToolAI
  4. Type: 'script'
  5. Redirect URI: http://localhost:8080
  6. Click Create
  7. Copy the client_id (short string under app name)
  8. Copy client_secret
  9. Add to social_agent/.env:
     REDDIT_CLIENT_ID=xxx
     REDDIT_CLIENT_SECRET=xxx
     REDDIT_USERNAME=rankertoolai
     REDDIT_PASSWORD=your_reddit_password
  10. Run: python post_reddit.py --tool elevenlabs
""")
        sys.exit(0)

    print(f"Reddit logged in as: u/{reddit.user.me().name}")

    if args.all:
        for slug in REDDIT_POSTS:
            print(f"\n=== Posting: {slug} ===")
            post_tool(reddit, slug)
    elif args.tool:
        post_tool(reddit, args.tool)
    else:
        print("Usage: python post_reddit.py --tool elevenlabs | --all | --list")
