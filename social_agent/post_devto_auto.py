"""Auto-generate and post Dev.to articles using Claude API.

Usage:
  python post_devto_auto.py           -- post one article (least posted tool)
  python post_devto_auto.py --all     -- post for all tools not yet posted
  python post_devto_auto.py --tool jasper  -- post for specific tool
"""
import os, sys, json, requests, time
from dotenv import load_dotenv
load_dotenv()

import anthropic
from database import log_post, already_posted, get_least_posted_tool

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")
DIR = os.path.dirname(__file__)
TOOLS_FILE = os.path.join(DIR, "data", "tools.json")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ALREADY_POSTED_SLUGS = {"elevenlabs", "surfer-seo", "cursor"}

TAG_MAP = {
    "AI Writing Tool":     ["ai", "productivity", "tools", "writing"],
    "AI SEO Tool":         ["seo", "ai", "webdev", "productivity"],
    "AI SEO Suite":        ["seo", "ai", "webdev", "tools"],
    "AI Voice Generator":  ["ai", "productivity", "javascript", "tools"],
    "AI Image Generator":  ["ai", "programming", "productivity", "tools"],
    "AI Design Tool":      ["ai", "design", "productivity", "tools"],
    "AI Chatbot":          ["ai", "productivity", "chatgpt", "tools"],
    "AI Video Generator":  ["ai", "productivity", "video", "tools"],
    "AI Coding Tool":      ["programming", "ai", "tools", "productivity"],
}


def generate_article(tool):
    pros = ", ".join(tool["pros"][:3])
    cons = ", ".join(tool["cons"][:2])
    prompt = f"""Write a Dev.to article about {tool['name']} ({tool['score']}/10).

Title: Practical, specific — e.g. "I Tested {tool['name']} for 30 Days: {tool['score']}/10 — Here's My Honest Review"
Category: {tool['category']}
Tagline: {tool['tagline']}
Price: {tool['price']}
Best for: {tool['best_for']}
Pros: {pros}
Cons: {cons}

Format: Markdown with ## headers
Include: one code snippet or workflow example if relevant to the tool
Word count: 600-800 words
End with: "Full review with pricing details: [{tool['name']} Review]({tool['url']})"
Score line at end: "**Score: {tool['score']}/10**"

Return ONLY the article body in Markdown (no title line, no frontmatter). Start with the intro paragraph."""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def build_title(tool):
    return f"I Tested {tool['name']} for 30 Days: Honest Review ({tool['score']}/10)"


def post_to_devto(title, body, tags, canonical_url):
    payload = {
        "article": {
            "title": title,
            "body_markdown": body,
            "published": True,
            "tags": tags,
            "canonical_url": canonical_url,
        }
    }
    r = requests.post(
        "https://dev.to/api/articles",
        json=payload,
        headers={"api-key": DEVTO_API_KEY, "Content-Type": "application/json"},
        timeout=30,
    )
    return r


def run_tool(tool):
    slug = tool["slug"]
    if slug in ALREADY_POSTED_SLUGS:
        print(f"[Dev.to] {tool['name']}: already posted, skipping")
        return False
    if already_posted("devto", slug, days=60):
        print(f"[Dev.to] {tool['name']}: posted in last 60 days, skipping")
        return False

    print(f"[Dev.to] Generating article for {tool['name']}...")
    try:
        body = generate_article(tool)
    except Exception as e:
        print(f"[Dev.to] Generation failed: {e}")
        return False

    title = build_title(tool)
    tags = TAG_MAP.get(tool["category"], ["ai", "tools", "productivity", "webdev"])
    canonical = tool["url"]

    print(f"[Dev.to] Posting: {title}")
    for attempt in range(3):
        r = post_to_devto(title, body, tags, canonical)
        if r.status_code in [200, 201]:
            data = r.json()
            url = data.get("url", "")
            print(f"[Dev.to] SUCCESS: {url}")
            log_post("devto", slug, url)
            return True
        elif r.status_code == 429:
            wait = 310
            print(f"[Dev.to] Rate limited. Waiting {wait}s before retry {attempt+1}/3...")
            time.sleep(wait)
        else:
            print(f"[Dev.to] ERROR {r.status_code}: {r.text[:300]}")
            return False
    print(f"[Dev.to] Failed after 3 attempts")
    return False


def main():
    with open(TOOLS_FILE, encoding="utf-8") as f:
        tools = json.load(f)

    run_all = "--all" in sys.argv
    force_slug = None
    for arg in sys.argv[1:]:
        if arg.startswith("--tool"):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                force_slug = sys.argv[idx + 1]

    if force_slug:
        matches = [t for t in tools if t["slug"] == force_slug]
        if not matches:
            print(f"Tool '{force_slug}' not found")
            return
        run_tool(matches[0])
        return

    if run_all:
        posted = 0
        for tool in tools:
            if tool["slug"] not in ALREADY_POSTED_SLUGS:
                success = run_tool(tool)
                if success:
                    posted += 1
                    if posted < len(tools):
                        print(f"[Dev.to] Waiting 60s before next article...")
                        time.sleep(60)
        print(f"\nDone: {posted} articles posted")
        return

    slugs = [t["slug"] for t in tools]
    best_slug = get_least_posted_tool(slugs, "devto")
    matches = [t for t in tools if t["slug"] == best_slug]
    if matches:
        run_tool(matches[0])


if __name__ == "__main__":
    main()
