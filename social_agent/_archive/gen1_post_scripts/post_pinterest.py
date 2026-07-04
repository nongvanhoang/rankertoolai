#!/usr/bin/env python3
"""
Pinterest auto-pinner for RankerToolAI
Tạo boards + pins cho toàn bộ review, blog, compare pages qua Pinterest API v5.

SETUP (làm 1 lần):
  1. Vào developers.pinterest.com → Create app
  2. Trong app settings → Add OAuth redirect URI: https://localhost
  3. Vào "Generate access token" → chọn scopes:
       boards:read, boards:write, pins:read, pins:write, user_accounts:read
  4. Copy token → set env var:
       Windows: $env:PINTEREST_ACCESS_TOKEN = "your_token_here"
       Linux:   export PINTEREST_ACCESS_TOKEN="your_token_here"
  5. Chạy: python post_pinterest.py

LƯU Ý:
  - Token hết hạn sau 30 ngày, cần refresh qua Pinterest OAuth flow
  - Script có cooldown 30 ngày/pin (không re-pin cùng 1 slug)
  - Rate limit: 3 giây giữa mỗi API call
  - Pinterest cần ảnh thực (og:image) trên mỗi trang, hoặc set DEFAULT_IMAGE

pip install requests
"""

import os, json, time, sqlite3, sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
from html.parser import HTMLParser

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
TOOLS_FILE = BASE_DIR / "data" / "tools.json"
DB_FILE    = BASE_DIR / "data" / "pinterest_posts.db"
TOKEN      = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
API        = "https://api.pinterest.com/v5"
SITE       = "https://rankertoolai.com"
COOLDOWN   = 30    # ngày cooldown giữa 2 lần pin cùng slug
RATE_DELAY = 3     # giây giữa API calls

# Ảnh fallback — upload 1 ảnh branded 1000x1500px lên đường dẫn này
DEFAULT_IMAGE = f"{SITE}/assets/images/og-default.jpg"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# ─── Board definitions ────────────────────────────────────────────────────────
BOARDS = {
    "AI Writing Tools Reviews 2026": {
        "desc": "Honest reviews and rankings of the best AI writing tools in 2026. Compare Jasper, Writesonic, Copy.ai and more at RankerToolAI.",
        "categories": ["AI Writing Tool"],
    },
    "AI Coding Tools Reviews 2026": {
        "desc": "In-depth reviews of AI coding assistants — Cursor, GitHub Copilot, Windsurf and more. Find the best AI code editor for developers.",
        "categories": ["AI Coding Tool", "AI Coding IDE"],
    },
    "AI Image Generator Reviews 2026": {
        "desc": "Compare the best AI image generators in 2026: Midjourney, Adobe Firefly, Stable Diffusion, Canva AI and more.",
        "categories": ["AI Image Generator", "AI Design Tool"],
    },
    "AI Chatbot Reviews 2026": {
        "desc": "Honest reviews of the top AI chatbots in 2026: ChatGPT, Claude, Gemini, DeepSeek, Grok and more. Find the best AI assistant.",
        "categories": ["AI Chatbot"],
    },
    "AI Productivity Tools Reviews 2026": {
        "desc": "Top AI tools for productivity and workflow: Notion AI, Otter.ai, ChatGPT and more. Save hours every week with AI.",
        "categories": ["AI Productivity Tool"],
    },
    "AI Voice & TTS Tool Reviews 2026": {
        "desc": "Reviews of the best AI voice and text-to-speech tools: ElevenLabs, Murf, Play.ht and more. Find your perfect AI voice.",
        "categories": ["AI Voice Generator", "AI Voice"],
    },
    "AI SEO & Marketing Tools 2026": {
        "desc": "Best AI tools for SEO and digital marketing: Surfer SEO, Semrush, HubSpot AI and more. Grow your traffic with AI.",
        "categories": ["AI SEO Tool", "AI SEO Suite", "AI CRM & Marketing"],
    },
    "AI Video Tools Reviews 2026": {
        "desc": "Best AI video generation and editing tools: Runway ML and more. Create professional videos with AI in minutes.",
        "categories": ["AI Video Generator"],
    },
    "Best AI Tools 2026 — RankerToolAI": {
        "desc": "Curated list of the best AI tools ranked and reviewed by RankerToolAI. All categories: writing, coding, design, SEO, voice and more.",
        "categories": ["AI Search Tool", "General"],
    },
}

# Map category string → board name
CAT_TO_BOARD = {}
for _bn, _cfg in BOARDS.items():
    for _cat in _cfg["categories"]:
        CAT_TO_BOARD[_cat] = _bn

# ─── Blog posts ───────────────────────────────────────────────────────────────
BLOG_POSTS = [
    {
        "slug": "blog-best-ai-tools-2026",
        "title": "Best AI Tools 2026: Complete Ranked List (Reviewed & Rated)",
        "desc": "Our expert team tested 50+ AI tools and ranked the absolute best. From ChatGPT to Midjourney — find the perfect AI tool for your needs in 2026. Free & paid options included.\n\n#AITools #BestAITools #ArtificialIntelligence #Productivity #Tech",
        "link": f"{SITE}/blog/best-ai-tools-2026/",
        "board": "Best AI Tools 2026 — RankerToolAI",
    },
    {
        "slug": "blog-how-to-use-chatgpt",
        "title": "How to Use ChatGPT: 20 Prompts & Tips That Actually Work (2026)",
        "desc": "Stop using ChatGPT wrong. These 20 proven prompts and power tips will 10x your results — from writing to coding to research. Works on free tier.\n\n#ChatGPT #AIPrompts #OpenAI #AITips #Productivity",
        "link": f"{SITE}/blog/how-to-use-chatgpt/",
        "board": "AI Chatbot Reviews 2026",
    },
    {
        "slug": "blog-best-ai-tools-for-students",
        "title": "10 Best AI Tools for Students in 2026 — Free & Paid Picks",
        "desc": "The top AI tools every student needs: AI writing assistants, research tools, study helpers and more. Most have free plans. Save hours every week on assignments.\n\n#AIForStudents #StudyTips #StudentLife #AITools #Education",
        "link": f"{SITE}/blog/best-ai-tools-for-students/",
        "board": "Best AI Tools 2026 — RankerToolAI",
    },
    {
        "slug": "blog-best-free-ai-image-generators",
        "title": "7 Best Free AI Image Generators in 2026 (No Credit Card Needed)",
        "desc": "Create stunning AI images for free. We tested every free AI image generator so you don't have to. These Midjourney alternatives are 100% free and beginner-friendly.\n\n#AIArt #FreeAI #AIImage #DigitalArt #AITools",
        "link": f"{SITE}/blog/best-free-ai-image-generators/",
        "board": "AI Image Generator Reviews 2026",
    },
    {
        "slug": "blog-ai-tools-for-small-business",
        "title": "12 Best AI Tools for Small Business in 2026 — Save 10+ Hours/Week",
        "desc": "The best AI tools to grow your small business without hiring: AI writing, CRM, SEO, design and automation tools that actually save money and time.\n\n#SmallBusiness #AITools #Entrepreneur #BusinessGrowth #Marketing",
        "link": f"{SITE}/blog/ai-tools-for-small-business/",
        "board": "AI SEO & Marketing Tools 2026",
    },
    {
        "slug": "blog-how-to-use-perplexity-ai",
        "title": "How to Use Perplexity AI: 15 Tips & Use Cases That Will Change How You Search",
        "desc": "Perplexity AI is better than Google for research. Learn 15 power features that will transform how you find information — with real-time cited sources, not just blue links.\n\n#PerplexityAI #AISearch #Research #FutureOfSearch #AITools",
        "link": f"{SITE}/blog/how-to-use-perplexity-ai/",
        "board": "AI Chatbot Reviews 2026",
    },
]

# ─── Compare pages ────────────────────────────────────────────────────────────
COMPARE_PAGES = [
    {
        "slug": "compare-claude-vs-gpt4o",
        "title": "Claude vs GPT-4o: Which AI Is Better in 2026? [Full Comparison]",
        "desc": "Claude 3.5 Sonnet vs GPT-4o compared head-to-head on writing, coding, pricing and context length. We tested both for 30 days — here's the honest verdict.\n\n#Claude #ChatGPT #GPT4 #AIComparison #AITools",
        "link": f"{SITE}/compare/claude-vs-gpt4o/",
        "board": "AI Chatbot Reviews 2026",
    },
    {
        "slug": "compare-midjourney-vs-firefly",
        "title": "Midjourney vs Adobe Firefly: Which AI Image Generator Wins? (2026)",
        "desc": "Midjourney vs Adobe Firefly compared on image quality, pricing, and commercial licensing. One wins on quality — the other wins for safe commercial use.\n\n#Midjourney #AdobeFirefly #AIArt #AIImage #DigitalArt",
        "link": f"{SITE}/compare/midjourney-vs-firefly/",
        "board": "AI Image Generator Reviews 2026",
    },
    {
        "slug": "compare-perplexity-vs-google",
        "title": "Perplexity AI vs Google Search: Is AI Search Actually Better? (2026 Test)",
        "desc": "We ran 50 real searches on Perplexity AI vs Google. The results surprised us. See which wins for research, local search, shopping and everyday questions.\n\n#PerplexityAI #Google #AISearch #FutureOfSearch #Tech",
        "link": f"{SITE}/compare/perplexity-vs-google/",
        "board": "Best AI Tools 2026 — RankerToolAI",
    },
    {
        "slug": "compare-notion-vs-chatgpt",
        "title": "Notion AI vs ChatGPT: Which Should You Use for Writing? (2026)",
        "desc": "Notion AI vs ChatGPT compared for writing, productivity, and daily tasks. One wins inside your workspace — the other wins for standalone tasks and coding.\n\n#NotionAI #ChatGPT #Productivity #AIWriting #PKM",
        "link": f"{SITE}/compare/notion-vs-chatgpt/",
        "board": "AI Productivity Tools Reviews 2026",
    },
]


# ─── DB helpers ───────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pinned (
            slug      TEXT PRIMARY KEY,
            pinned_at TEXT,
            pin_id    TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS boards_cache (
            name     TEXT PRIMARY KEY,
            board_id TEXT
        )
    """)
    conn.commit()
    return conn


def already_pinned(conn, slug):
    row = conn.execute("SELECT pinned_at FROM pinned WHERE slug=?", (slug,)).fetchone()
    if not row:
        return False
    return datetime.utcnow() - datetime.fromisoformat(row[0]) < timedelta(days=COOLDOWN)


def mark_pinned(conn, slug, pin_id):
    conn.execute(
        "INSERT OR REPLACE INTO pinned (slug, pinned_at, pin_id) VALUES (?,?,?)",
        (slug, datetime.utcnow().isoformat(), pin_id or ""),
    )
    conn.commit()


def get_cached_board(conn, name):
    row = conn.execute("SELECT board_id FROM boards_cache WHERE name=?", (name,)).fetchone()
    return row[0] if row else None


def cache_board(conn, name, board_id):
    conn.execute("INSERT OR REPLACE INTO boards_cache (name, board_id) VALUES (?,?)", (name, board_id))
    conn.commit()


# ─── OG image extractor ───────────────────────────────────────────────────────
class _OGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.og_image = None

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            d = dict(attrs)
            if d.get("property") == "og:image" and "content" in d:
                self.og_image = d["content"]


def get_og_image(url):
    try:
        r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0 (Pinterest)"})
        p = _OGParser()
        p.feed(r.text)
        return p.og_image or DEFAULT_IMAGE
    except Exception:
        return DEFAULT_IMAGE


# ─── Pinterest API ────────────────────────────────────────────────────────────
def _get(path, params=None):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path, body):
    r = requests.post(f"{API}{path}", headers=HEADERS, json=body, timeout=10)
    if not r.ok:
        raise Exception(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


def get_or_create_board(conn, name):
    board_id = get_cached_board(conn, name)
    if board_id:
        return board_id

    # Tìm board đang có trên Pinterest
    try:
        bookmark = None
        while True:
            params = {"page_size": 25}
            if bookmark:
                params["bookmark"] = bookmark
            data = _get("/boards", params)
            time.sleep(1)
            for b in data.get("items", []):
                if b["name"] == name:
                    cache_board(conn, name, b["id"])
                    print(f"  ♟  Board found: {name}")
                    return b["id"]
            bookmark = data.get("bookmark")
            if not bookmark:
                break
    except Exception as e:
        print(f"  ⚠  List boards failed: {e}")

    # Tạo board mới
    cfg = BOARDS.get(name, {"desc": f"AI tools reviews — {name}"})
    try:
        result = _post("/boards", {
            "name": name,
            "description": cfg["desc"],
            "privacy": "PUBLIC",
        })
        bid = result["id"]
        cache_board(conn, name, bid)
        print(f"  ✅ Board created: {name}")
        time.sleep(RATE_DELAY)
        return bid
    except Exception as e:
        print(f"  ❌ Board create failed '{name}': {e}")
        return None


def create_pin(board_id, title, description, link, image_url):
    body = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "media_source": {"source_type": "image_url", "url": image_url},
        "alt_text": title[:500],
    }
    return _post("/pins", body).get("id")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not TOKEN:
        print("❌  PINTEREST_ACCESS_TOKEN chưa set.")
        print("   Windows: $env:PINTEREST_ACCESS_TOKEN = 'your_token'")
        print("   Xem hướng dẫn setup ở đầu file.")
        sys.exit(1)

    conn  = init_db()
    done  = 0
    skip  = 0

    # ── Tool Reviews ──────────────────────────────────────────────────────────
    print("\n📌  Tool reviews...")
    with open(TOOLS_FILE, encoding="utf-8") as f:
        tools = json.load(f)

    for tool in tools:
        slug = f"review-{tool['slug']}"
        if already_pinned(conn, slug):
            print(f"  ⏭  {tool['name']} (cooldown)")
            skip += 1
            continue

        board_name = CAT_TO_BOARD.get(tool["category"], "Best AI Tools 2026 — RankerToolAI")
        board_id   = get_or_create_board(conn, board_name)
        if not board_id:
            continue

        title = f"{tool['name']} Review 2026: {tool['score']}/10 — {tool['tagline']}"[:100]
        pros  = " | ".join(f"✅ {p}" for p in tool["pros"][:3])
        desc  = (
            f"{tool['tagline']}\n\n"
            f"{pros}\n\n"
            f"Price: {tool['price']}\n"
            f"Best for: {tool['best_for']}\n\n"
            f"Full review → {tool['url']}\n\n"
            + " ".join(tool.get("hashtags", [])[:5])
        )

        image_url = get_og_image(tool["url"])
        try:
            pin_id = create_pin(board_id, title, desc, tool["url"], image_url)
            mark_pinned(conn, slug, pin_id)
            print(f"  📌  {tool['name']} → {board_name}")
            done += 1
            time.sleep(RATE_DELAY)
        except Exception as e:
            print(f"  ❌  {tool['name']}: {e}")

    # ── Blog Posts ────────────────────────────────────────────────────────────
    print("\n📰  Blog posts...")
    for post in BLOG_POSTS:
        if already_pinned(conn, post["slug"]):
            print(f"  ⏭  {post['slug']} (cooldown)")
            skip += 1
            continue

        board_id = get_or_create_board(conn, post["board"])
        if not board_id:
            continue

        image_url = get_og_image(post["link"])
        try:
            pin_id = create_pin(board_id, post["title"], post["desc"], post["link"], image_url)
            mark_pinned(conn, post["slug"], pin_id)
            print(f"  📰  {post['title'][:65]}…")
            done += 1
            time.sleep(RATE_DELAY)
        except Exception as e:
            print(f"  ❌  {post['slug']}: {e}")

    # ── Compare Pages ─────────────────────────────────────────────────────────
    print("\n⚖   Compare pages...")
    for page in COMPARE_PAGES:
        if already_pinned(conn, page["slug"]):
            print(f"  ⏭  {page['slug']} (cooldown)")
            skip += 1
            continue

        board_id = get_or_create_board(conn, page["board"])
        if not board_id:
            continue

        image_url = get_og_image(page["link"])
        try:
            pin_id = create_pin(board_id, page["title"], page["desc"], page["link"], image_url)
            mark_pinned(conn, page["slug"], pin_id)
            print(f"  ⚖   {page['title'][:65]}…")
            done += 1
            time.sleep(RATE_DELAY)
        except Exception as e:
            print(f"  ❌  {page['slug']}: {e}")

    conn.close()
    print(f"\n✅  Xong! Đã pin: {done} | Bỏ qua: {skip}")
    print(f"   DB lưu tại: {DB_FILE}")


if __name__ == "__main__":
    main()
