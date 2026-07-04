"""
Auto-post carousels to Instagram via Meta Graph API.
Requirements:
  - Instagram Business/Creator account
  - Facebook Page connected to Instagram account
  - Meta Developer App with instagram_basic + instagram_content_publish permissions

Setup:
  1. Create Facebook Page: facebook.com/pages/create
  2. Connect to Instagram: Instagram app → Settings → Account → Linked Accounts → Facebook
  3. Go to: developers.facebook.com → Create App → Business type
  4. Add Instagram Graph API product
  5. Generate long-lived access token (60 days)
  6. Add to .env:
     INSTAGRAM_ACCESS_TOKEN=...
     INSTAGRAM_BUSINESS_ID=...  (numeric ID from Graph API Explorer)
"""

import os, sys, json, time, requests
from dotenv import load_dotenv
load_dotenv()

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TOKEN   = os.getenv("INSTAGRAM_ACCESS_TOKEN")
BIZA_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
BASE    = "https://graph.facebook.com/v19.0"

OUT_DIR    = os.path.join(os.path.dirname(__file__), "output")
TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")
DB_FILE    = os.path.join(os.path.dirname(__file__), "data", "posts.db")

# Captions for each tool
CAPTIONS = {
    "elevenlabs": "We tested 10 AI voice generators. ElevenLabs wins — by a lot.\n\nScore: 9.2/10 after 30 days of real testing.\n\n→ Voices that fool people (12/15 humans couldn't tell)\n→ 99 languages, 1-click voice cloning\n→ API that works in production\n\nFull review → rankertoolai.com/review/elevenlabs/\n\n#AITools #ElevenLabs #TextToSpeech #AIVoice #ContentCreator #AIProductivity",
    "semrush": "The highest-rated AI SEO tool we've tested. 9.3/10.\n\n50 billion keywords. 200+ tools in one platform.\nCompetitor analysis that's genuinely scary good.\n\nFull breakdown → rankertoolai.com/review/semrush/\n\n#SEO #Semrush #DigitalMarketing #AITools #ContentMarketing",
    "cursor": "I switched from VS Code + Copilot to Cursor. Score: 9.2/10.\n\nComposer wrote 8 files simultaneously for a feature that would've taken 2 hours. It took 12 minutes.\n\nFull review → rankertoolai.com/review/cursor/\n\n#Cursor #AICode #Developer #Programming #AITools",
    "surfer-seo": "90-day SEO experiment results:\n\nWith Surfer: 7/10 articles hit page 1\nWithout Surfer: 3/10 hit page 1\n\nThat's 3.2x more organic traffic. Score: 9.0/10.\n\nFull data → rankertoolai.com/review/surfer-seo/\n\n#SurferSEO #SEO #ContentMarketing #Blogging",
    "jasper": "Best AI writer for marketing teams. Score: 8.9/10.\n\n→ Brand voice training\n→ 50+ templates\n→ Native Surfer SEO integration\n\nFull review → rankertoolai.com/review/jasper/\n\n#JasperAI #AIWriting #ContentMarketing #AITools",
    "stable-diffusion": "The best FREE AI image generator. Score: 8.9/10.\n\nRun locally: $0/month forever.\nQuality rivals Midjourney at a fraction of the cost.\n\nFull guide → rankertoolai.com/review/stable-diffusion/\n\n#StableDiffusion #AIArt #AIImage #GenerativeAI",
    "canva-ai": "Canva just became an AI design powerhouse. Score: 8.4/10.\n\n→ Text to Image\n→ Magic Eraser\n→ AI Presentations\n\nFull review → rankertoolai.com/review/canva-ai/\n\n#Canva #CanvaAI #GraphicDesign #AIDesign #AITools",
    "grok": "Grok 3 surprised me. Score: 8.3/10.\n\nReal-time data via X, strong reasoning, no content restrictions on research.\n\nIncluded with X Premium ($8-16/mo).\n\nFull review → rankertoolai.com/review/grok/\n\n#Grok #GrokAI #AI #AITools #XAI",
    "runway": "AI video generation in 2026 is actually impressive. Score: 8.5/10.\n\nGen-3 Alpha produces footage I've seen on real YouTube channels without disclosure.\n\nFull review → rankertoolai.com/review/runway/\n\n#RunwayML #AIVideo #VideoGeneration #AITools",
    "writesonic": "Best value AI writer. Score: 8.7/10.\n\n$16/mo vs Jasper's $39/mo. Quality: ~75% of Jasper at 40% of the price.\n\nFull review → rankertoolai.com/review/writesonic/\n\n#Writesonic #AIWriting #AITools #ContentMarketing",
}

def already_posted(slug):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        r = conn.execute("SELECT id FROM posts WHERE platform='instagram' AND tool_slug=?", (slug,)).fetchone()
        conn.close()
        return r is not None
    except:
        return False

def log_post(slug, url=""):
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO posts (platform, tool_slug, content_type, url, status) VALUES (?,?,?,?,?)",
            ("instagram", slug, "carousel", url, "success"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [DB] log_post error: {e}")

def upload_image_to_imgbb(image_path):
    """Upload local image to imgbb for use with Graph API."""
    IMGBB_KEY = os.getenv("IMGBB_API_KEY")
    if not IMGBB_KEY:
        return None
    import base64
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = requests.post("https://api.imgbb.com/1/upload",
        data={"key": IMGBB_KEY, "image": b64})
    if r.status_code == 200:
        return r.json()["data"]["url"]
    return None

def create_carousel_post(tool_slug, image_urls, caption):
    """Create an Instagram carousel post."""
    # Step 1: Create media containers for each image
    children = []
    for url in image_urls:
        r = requests.post(f"{BASE}/{BIZA_ID}/media",
            params={"image_url": url, "is_carousel_item": "true", "access_token": TOKEN})
        if r.status_code == 200:
            children.append(r.json()["id"])
            print(f"    Image container: {r.json()['id']}")
        else:
            print(f"    Image error: {r.text[:100]}")
        time.sleep(1)

    if not children:
        return None

    # Step 2: Create carousel container
    r = requests.post(f"{BASE}/{BIZA_ID}/media",
        params={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": TOKEN
        })
    if r.status_code != 200:
        print(f"  Carousel container error: {r.text[:200]}")
        return None
    carousel_id = r.json()["id"]
    print(f"  Carousel container: {carousel_id}")

    # Step 3: Wait for processing
    time.sleep(5)

    # Step 4: Publish
    r = requests.post(f"{BASE}/{BIZA_ID}/media_publish",
        params={"creation_id": carousel_id, "access_token": TOKEN})
    if r.status_code == 200:
        return r.json()["id"]
    print(f"  Publish error: {r.text[:200]}")
    return None

def post_tool(tool):
    slug = tool["slug"]
    if already_posted(slug):
        print(f"  Already posted: {slug}")
        return

    # Get carousel slide paths
    carousel_dir = os.path.join(OUT_DIR, slug, "carousel")
    if not os.path.exists(carousel_dir):
        print(f"  No carousel for {slug}, run content_creator.py first")
        return

    slides = sorted([f for f in os.listdir(carousel_dir) if f.endswith(".png")])[:10]
    if not slides:
        print(f"  No slides found for {slug}")
        return

    print(f"  Uploading {len(slides)} images to imgbb...")
    image_urls = []
    for slide in slides:
        path = os.path.join(carousel_dir, slide)
        url = upload_image_to_imgbb(path)
        if url:
            image_urls.append(url)
            print(f"    Uploaded: {slide}")
        time.sleep(1)

    if not image_urls:
        print(f"  No images uploaded (check IMGBB_API_KEY in .env)")
        return

    caption = CAPTIONS.get(slug, f"Review: {tool['name']} — {tool['score']}/10\n\n{tool['url']}")
    print(f"  Creating carousel post...")
    post_id = create_carousel_post(slug, image_urls, caption)
    if post_id:
        url = f"https://www.instagram.com/p/{post_id}/"
        print(f"  Posted: {url}")
        log_post(slug, url)
    else:
        print(f"  Failed to post {slug}")

def pick_next_tool(tools):
    """Highest-score tool that has a ready carousel and hasn't been posted yet."""
    for tool in sorted(tools, key=lambda x: -x["score"]):
        slug = tool["slug"]
        carousel_dir = os.path.join(OUT_DIR, slug, "carousel")
        if os.path.exists(carousel_dir) and not already_posted(slug):
            return tool
    return None

if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", help="Tool slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=1, help="Unused when not --all; kept for scheduler compatibility")
    args = parser.parse_args()

    if not TOKEN or not BIZA_ID:
        print("""
Missing credentials. Run the OAuth helper first:
  python social_agent/get_instagram_token.py

(It walks you through creating the Facebook Page + Meta App and saves
INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ID to .env automatically.)
""")
        sys.exit(0)

    tools = json.load(open(TOOLS_FILE, encoding="utf-8"))
    if args.all:
        for tool in sorted(tools, key=lambda x: -x["score"]):
            print(f"\n=== {tool['name']} ===")
            post_tool(tool)
            time.sleep(60)  # 1 min between posts
    elif args.tool:
        tool = next((t for t in tools if t["slug"] == args.tool), None)
        if tool:
            post_tool(tool)
        else:
            print(f"Tool not found: {args.tool}")
    else:
        tool = pick_next_tool(tools)
        if tool:
            print(f"\n=== {tool['name']} ===")
            post_tool(tool)
        else:
            print("  No tool ready to post (need a carousel in output/<slug>/carousel/ and not yet posted)")
