import requests, os, time, json
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD = os.getenv("DISCORD_GUILD_ID")
BASE  = "https://discord.com/api/v10"
H     = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

CHANNELS = [
    {"name": "ai-tool-reviews",         "topic": "Daily AI tool reviews from rankertoolai.com"},
    {"name": "tool-comparisons",        "topic": "Head-to-head AI tool comparisons"},
    {"name": "ask-for-recommendations", "topic": "Ask which AI tool to use for your use case"},
    {"name": "deals-and-discounts",     "topic": "AI tool deals, free trials, and discount codes"},
    {"name": "showcase-your-work",      "topic": "Share what you built with AI tools"},
]

WELCOME = """👋 **Welcome to RankerTool AI Community!**

We independently test 50+ AI tools so you don't have to.

**Quick links:**
→ Latest reviews: https://rankertoolai.com
→ Ask for recommendations below
→ See deals in #deals-and-discounts

**Top-rated tools right now:**
🎙️ **ElevenLabs** — 9.2/10 — Best AI Voice
📊 **Semrush** — 9.3/10 — Best SEO Suite
💻 **Cursor** — 9.2/10 — Best AI Coding Tool
🎨 **Midjourney** — 9.1/10 — Best AI Image"""

FIRST_REVIEW = """📊 **Tool Review: Semrush — 9.3/10** ⭐

After 30 days of testing against Ahrefs, Moz, and SE Ranking — here's our verdict.

**Why it wins:**
→ 50 billion keyword database (largest we've tested)
→ Competitor traffic analysis — see exactly where rivals get their traffic
→ Content Marketing Toolkit + SEO Writing Assistant built-in
→ Backlink audit that actually finds toxic links

**The honest downside:** $129/mo is steep. Not for beginners.

**Best for:** SEO agencies, content marketers, e-commerce stores doing serious volume.

**vs Ahrefs:** Semrush wins on competitor research. Ahrefs wins on backlink data depth.

🔗 Full review + pricing breakdown: https://rankertoolai.com/review/semrush/"""

def main():
    # Step 1: Create category
    r = requests.post(f"{BASE}/guilds/{GUILD}/channels",
        json={"name": "AI TOOLS COMMUNITY", "type": 4}, headers=H)
    cat_id = r.json().get("id") if r.status_code in [200, 201] else None
    print(f"Category: {r.status_code} id={cat_id}")

    # Step 2: Create channels
    channel_ids = {}
    for ch in CHANNELS:
        payload = {"name": ch["name"], "type": 0, "topic": ch["topic"]}
        if cat_id:
            payload["parent_id"] = cat_id
        r = requests.post(f"{BASE}/guilds/{GUILD}/channels", json=payload, headers=H)
        if r.status_code in [200, 201]:
            cid = r.json().get("id")
            channel_ids[ch["name"]] = cid
            print(f"  #{ch['name']} -> {cid}")
        else:
            print(f"  #{ch['name']} FAIL {r.status_code}: {r.text[:80]}")
        time.sleep(0.5)

    # Step 3: Post welcome in ask-for-recommendations
    ask_ch = channel_ids.get("ask-for-recommendations")
    if ask_ch:
        r = requests.post(f"{BASE}/channels/{ask_ch}/messages",
            json={"content": WELCOME}, headers=H)
        print(f"\nWelcome message: {r.status_code}")

    # Step 4: Post first review in ai-tool-reviews
    reviews_ch = channel_ids.get("ai-tool-reviews")
    if reviews_ch:
        r = requests.post(f"{BASE}/channels/{reviews_ch}/messages",
            json={"content": FIRST_REVIEW}, headers=H)
        print(f"First review: {r.status_code}")

    # Step 5: Save channel IDs to .env
    all_ids = ",".join(channel_ids.values())
    reviews_id = channel_ids.get("ai-tool-reviews", "")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, encoding="utf-8") as f:
        content = f.read()
    if "DISCORD_CHANNEL_IDS=" in content:
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("DISCORD_CHANNEL_IDS="):
                new_lines.append(f"DISCORD_CHANNEL_IDS={reviews_id}")
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n.env updated: DISCORD_CHANNEL_IDS={reviews_id}")
    print(f"\nAll channel IDs: {json.dumps(channel_ids, indent=2)}")
    print("\nDiscord setup COMPLETE!")

if __name__ == "__main__":
    main()
