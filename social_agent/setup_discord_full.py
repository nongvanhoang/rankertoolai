"""
Full Discord setup:
1. Verify bot token
2. Get guild ID from invite code
3. Invite bot to server
4. Create channels
5. Post welcome message
6. Post first AI tool review
"""
import requests, os, json, time
from dotenv import load_dotenv
load_dotenv()

TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
APP_ID   = "1518651202517209088"
BASE     = "https://discord.com/api/v10"
HEADERS  = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

INVITE_CODE = "5HXuxYfjx"

CHANNELS = [
    {"name": "ai-tool-reviews",          "topic": "Daily AI tool reviews from rankertoolai.com"},
    {"name": "tool-comparisons",         "topic": "Head-to-head AI tool comparisons"},
    {"name": "ask-for-recommendations",  "topic": "Ask which AI tool to use for your use case"},
    {"name": "deals-and-discounts",      "topic": "AI tool deals, free trials, and discount codes"},
    {"name": "showcase-your-work",       "topic": "Share what you built with AI tools"},
]

WELCOME = """👋 **Welcome to RankerTool AI Community!**

We independently test 50+ AI tools so you don't have to.

**Quick links:**
→ Latest reviews: https://rankertoolai.com
→ Ask anything in <#ask-for-recommendations>
→ See deals in <#deals-and-discounts>

**Top-rated tools right now:**
🎙️ **ElevenLabs** — 9.2/10 — Best AI Voice
📊 **Semrush** — 9.3/10 — Best SEO Suite
💻 **Cursor** — 9.2/10 — Best AI Coding Tool
📝 **Surfer SEO** — 9.0/10 — Best Content SEO"""

def verify_bot():
    r = requests.get(f"{BASE}/users/@me", headers=HEADERS)
    if r.status_code == 200:
        me = r.json()
        print(f"Bot verified: {me['username']}#{me.get('discriminator','0')}")
        return True
    else:
        print(f"Bot token invalid: {r.status_code} {r.text[:100]}")
        return False

def get_guild_from_invite(code):
    r = requests.get(f"{BASE}/invites/{code}?with_counts=true")
    if r.status_code == 200:
        data = r.json()
        guild = data.get("guild", {})
        guild_id = guild.get("id")
        guild_name = guild.get("name")
        members = data.get("approximate_member_count", 0)
        print(f"Server: {guild_name} (ID: {guild_id}, Members: {members})")
        return guild_id
    print(f"Could not resolve invite: {r.status_code}")
    return None

def get_invite_url():
    perms = 8  # Administrator
    return (f"https://discord.com/oauth2/authorize"
            f"?client_id={APP_ID}&scope=bot&permissions={perms}&guild_id={guild_id}")

def create_channels(guild_id):
    # Create category
    r = requests.post(f"{BASE}/guilds/{guild_id}/channels",
        json={"name": "AI TOOLS COMMUNITY", "type": 4}, headers=HEADERS)
    cat_id = r.json().get("id") if r.status_code in [200, 201] else None
    if cat_id:
        print(f"Created category (id: {cat_id})")

    channel_ids = []
    for ch in CHANNELS:
        payload = {"name": ch["name"], "type": 0, "topic": ch["topic"]}
        if cat_id:
            payload["parent_id"] = cat_id
        r = requests.post(f"{BASE}/guilds/{guild_id}/channels", json=payload, headers=HEADERS)
        if r.status_code in [200, 201]:
            ch_id = r.json().get("id")
            print(f"  Created #{ch['name']} (id: {ch_id})")
            channel_ids.append((ch["name"], ch_id))
        else:
            print(f"  Failed #{ch['name']}: {r.status_code} {r.text[:80]}")
        time.sleep(0.5)
    return channel_ids

def post_welcome(channel_id):
    r = requests.post(f"{BASE}/channels/{channel_id}/messages",
        json={"content": WELCOME}, headers=HEADERS)
    if r.status_code == 200:
        print(f"Welcome message posted!")
    else:
        print(f"Failed to post welcome: {r.status_code} {r.text[:100]}")

def post_first_review(channel_id):
    msg = """📊 **Tool Review: Semrush — 9.3/10**

We tested Semrush for 30 days against Ahrefs, Moz, and SE Ranking.

**Why it wins:**
→ 50 billion keyword database (largest we've tested)
→ Competitor traffic analysis that's genuinely scary good
→ Content Marketing Toolkit built-in

**The catch:** $129/mo. Worth it for agencies and serious SEOs. Not for beginners.

**Best for:** SEO agencies, content marketers, e-commerce stores

🔗 Full review: https://rankertoolai.com/review/semrush/"""

    r = requests.post(f"{BASE}/channels/{channel_id}/messages",
        json={"content": msg}, headers=HEADERS)
    if r.status_code == 200:
        print(f"First review posted!")
    else:
        print(f"Failed: {r.status_code} {r.text[:100]}")

if __name__ == "__main__":
    print("=== Discord Setup ===\n")

    # Step 1: Verify bot
    if not verify_bot():
        exit(1)

    # Step 2: Get guild ID
    print(f"\nResolving invite: discord.gg/{INVITE_CODE}")
    guild_id = get_guild_from_invite(INVITE_CODE)
    if not guild_id:
        exit(1)

    # Step 3: Generate invite URL for bot
    bot_invite = (f"https://discord.com/oauth2/authorize"
                  f"?client_id={APP_ID}&scope=bot&permissions=8&guild_id={guild_id}")
    print(f"\nBot invite URL:\n{bot_invite}")
    print("\nOpen the URL above to add bot to server, then press Enter...")
    input()

    # Step 4: Create channels
    print("\nCreating channels...")
    channel_ids = create_channels(guild_id)

    # Step 5: Post welcome + first review
    for name, ch_id in channel_ids:
        if "general" in name or "reviews" in name:
            post_welcome(ch_id) if "general" in name else post_first_review(ch_id)
            break

    # Save guild_id and channel IDs to .env
    reviews_ch = next((cid for name, cid in channel_ids if "review" in name), None)
    if reviews_ch:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, encoding="utf-8") as f:
            content = f.read()
        content = content.replace("DISCORD_GUILD_ID=", f"DISCORD_GUILD_ID={guild_id}")
        content = content.replace("DISCORD_CHANNEL_IDS=", f"DISCORD_CHANNEL_IDS={reviews_ch}")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n.env updated: GUILD_ID={guild_id}, CHANNEL_IDS={reviews_ch}")

    print("\n=== Setup complete! ===")
