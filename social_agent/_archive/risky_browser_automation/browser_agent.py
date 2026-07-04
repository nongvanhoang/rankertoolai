"""
Social Media Browser Agent dung browser-use + Claude API.
Tu dong tao apps tren Reddit, Twitter, Pinterest va post content.

Usage:
  python browser_agent.py --task setup_reddit
  python browser_agent.py --task setup_twitter
  python browser_agent.py --task setup_pinterest
  python browser_agent.py --task post_twitter
  python browser_agent.py --task setup_all
"""

import os, sys, asyncio, json
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

ENV_FILE   = Path(__file__).parent / ".env"
TOOLS_FILE = Path(__file__).parent / "data" / "tools.json"

ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY")
REDDIT_USER     = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASS     = os.getenv("REDDIT_PASSWORD", "")
TWITTER_USER    = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASS    = os.getenv("TWITTER_PASSWORD", "")
PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL", "")
PINTEREST_PASS  = os.getenv("PINTEREST_PASSWORD", "")

# ─── TASKS ───────────────────────────────────────────────────

def _reddit_task():
    login_hint = ""
    if REDDIT_USER and REDDIT_PASS:
        login_hint = f"\nIf a login page appears, log in with username '{REDDIT_USER}' and password '{REDDIT_PASS}'."
    return f"""
Go to https://www.reddit.com/prefs/apps
{login_hint}
If you see a login page, complete the login first.

Then on the apps page:
1. Find and click "create another app" or "are you a developer? create an app!" button
2. Fill the form:
   - name: rankertoolai
   - Select "script" radio button (NOT web app, NOT installed app)
   - description: AI tool review site
   - about url: https://rankertoolai.com
   - redirect uri: http://localhost:8080
3. Click "create app" button
4. After creation, the page shows the new app. Find:
   - client_id: the short alphanumeric string shown directly under the app name (below the word "personal use script")
   - client_secret: shown next to the label "secret"
5. Output the values in this EXACT format (one per line):
   REDDIT_CLIENT_ID=<value>
   REDDIT_CLIENT_SECRET=<value>
"""

def _twitter_task():
    login_hint = ""
    if TWITTER_USER and TWITTER_PASS:
        login_hint = f"\nIf a login page appears, log in with username '{TWITTER_USER}' and password '{TWITTER_PASS}'."
    return f"""
Go to https://developer.twitter.com/en/portal/projects-and-apps
{login_hint}
If you see a login page or Twitter login redirect, complete the login first.

Then:
1. Click "+ Create Project" or "Create App" or "+ Add App"
2. Project name: RankerToolAI
3. Use case: select "Making a bot" or "Exploring the API"
4. Project description: AI tool review and ranking website
5. App name: rankertoolai (or rankertoolai_bot if taken)
6. After creation you will see API Key and API Key Secret — copy them immediately
7. Then click "Generate" for Access Token and Access Token Secret
8. Output ALL values in this EXACT format (one per line):
   TWITTER_API_KEY=<value>
   TWITTER_API_SECRET=<value>
   TWITTER_ACCESS_TOKEN=<value>
   TWITTER_ACCESS_SECRET=<value>
"""

def _pinterest_task():
    login_hint = ""
    if PINTEREST_EMAIL and PINTEREST_PASS:
        login_hint = f"\nIf a login page appears, log in with email '{PINTEREST_EMAIL}' and password '{PINTEREST_PASS}'."
    return f"""
Go to https://developers.pinterest.com/apps/
{login_hint}
If you see a login page, complete the login first.

4. Website: https://rankertoolai.com
5. Complete app creation
6. In the app settings, go to Authentication or Access token section
7. Generate an access token with scopes: boards:read, boards:write, pins:read, pins:write
8. Output the token in this EXACT format:
   PINTEREST_ACCESS_TOKEN=<value>
"""

POST_TWITTER = """
Go to https://x.com

Make sure you are logged in. Compose and post this tweet:
---
We tested 10 AI tools for 30 days each. Honest scores:

Semrush 9.3/10 — SEO
ElevenLabs 9.2/10 — Voice
Cursor 9.2/10 — Coding
Surfer SEO 9.0/10 — Content SEO

No sponsored content. Full reviews: rankertoolai.com

#AITools #ProductivityTools #TechReview
---

Click the Tweet/Post button to publish it. Confirm when done.
"""

POST_REDDIT_ELEVENLABS = """
Go to https://www.reddit.com/r/podcasting/submit

Make sure you are logged in. Create a text post with:
Title: I tested 10 AI voice generators for podcast production - honest scores after 30 days

Body:
After spending 30 days using AI voice generators for actual podcast work, here are my scores:

**1. ElevenLabs - 9.2/10**
Best overall quality by a significant margin. Played clips to 15 people, 12 thought it was a real recording. 99 languages, voice cloning from 1 min of audio.

**2. Murf AI - 8.4/10**
Better studio controls, easier for teams. Quality gap vs ElevenLabs is noticeable on emotional content.

**3. Play.ht - 8.1/10**
Cheapest at scale. Good API. Quality drops on anything longer than 2 minutes.

For podcasters: ElevenLabs wins on voice naturalness for long-form content.
Full breakdown: https://rankertoolai.com/review/elevenlabs/

Submit the post and confirm when done.
"""

def get_task(name):
    if name == "setup_reddit":          return _reddit_task()
    if name == "setup_twitter":         return _twitter_task()
    if name == "setup_pinterest":       return _pinterest_task()
    if name == "post_twitter":          return POST_TWITTER
    if name == "post_reddit_elevenlabs": return POST_REDDIT_ELEVENLABS
    raise ValueError(f"Unknown task: {name}")

async def run_browser_task(task_name, task_prompt, headless=False):
    """Run a browser automation task using browser-use."""
    try:
        from browser_use import Agent
        from langchain_anthropic import ChatAnthropic
        from pydantic import Field
    except ImportError:
        print("Install: pip install browser-use langchain-anthropic")
        return None

    # browser-use 0.13.1 checks llm.provider; ChatAnthropic (Pydantic) rejects unknown attrs
    class ChatAnthropicBU(ChatAnthropic):
        provider: str = Field(default="langchain-anthropic")

    llm = ChatAnthropicBU(
        model="claude-sonnet-4-6",
        anthropic_api_key=ANTHROPIC_KEY,
        temperature=0
    )

    agent = Agent(
        task=task_prompt,
        llm=llm,
        use_vision=True,
        save_conversation_path=f"data/browser_log_{task_name}.json"
    )

    print(f"[Agent] Starting: {task_name}")
    result = await agent.run(max_steps=25)
    return result

def parse_env_values(text):
    """Extract KEY=VALUE pairs from agent output."""
    import re
    values = {}
    pattern = r'(REDDIT_CLIENT_ID|REDDIT_CLIENT_SECRET|TWITTER_API_KEY|TWITTER_API_SECRET|TWITTER_ACCESS_TOKEN|TWITTER_ACCESS_SECRET|PINTEREST_ACCESS_TOKEN|LINKEDIN_ACCESS_TOKEN)=([^\s\n]+)'
    for match in re.finditer(pattern, str(text)):
        values[match.group(1)] = match.group(2)
    return values

def save_to_env(values):
    for key, value in values.items():
        set_key(str(ENV_FILE), key, value)
        print(f"  [.env] Saved: {key}={value[:10]}...")

ALL_TASKS = ["setup_reddit", "setup_twitter", "setup_pinterest", "post_twitter", "post_reddit_elevenlabs"]

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=ALL_TASKS + ["setup_all"])
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    if args.task == "setup_all":
        task_list = ["setup_reddit", "setup_twitter", "setup_pinterest"]
    else:
        task_list = [args.task]

    for task_name in task_list:
        print(f"\n{'='*50}\nTASK: {task_name}\n{'='*50}")
        prompt = get_task(task_name)
        result = await run_browser_task(task_name, prompt, args.headless)

        if result:
            values = parse_env_values(result)
            if values:
                save_to_env(values)
                print(f"Saved {len(values)} credentials")
            else:
                print(f"Result: {str(result)[:300]}")

        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
