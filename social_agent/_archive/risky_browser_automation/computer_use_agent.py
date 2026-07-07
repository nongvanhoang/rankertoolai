"""
Social Media Computer Use Agent
Dùng Claude Computer Use + Playwright để tự động:
  1. Tạo developer apps trên Reddit, Twitter, Pinterest, LinkedIn
  2. Extract API keys và lưu vào .env
  3. Post content lên tất cả platforms

Requirements:
  - Anthropic API với credits ($5+)
  - pip install playwright anthropic pillow
  - playwright install chromium

Usage:
  python computer_use_agent.py --task setup_reddit
  python computer_use_agent.py --task setup_twitter
  python computer_use_agent.py --task setup_all
  python computer_use_agent.py --task post_all
"""

import os, sys, json, time, base64, re, asyncio
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
ENV_FILE = Path(__file__).parent / ".env"
TOOLS_FILE = Path(__file__).parent / "data" / "tools.json"

try:
    import anthropic
    from PIL import ImageGrab, Image
except ImportError:
    print("Run: pip install anthropic pillow")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False

# ─────────────────────────────────────────────
# COMPUTER USE CORE
# ─────────────────────────────────────────────

class ComputerUseAgent:
    def __init__(self, headless=False):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        self.model  = "claude-sonnet-4-6"
        self.headless = headless
        self.browser = None
        self.page = None
        self.extracted = {}

    def screenshot_b64(self):
        """Take screenshot of current browser page."""
        if self.page:
            png = self.page.screenshot()
            return base64.standard_b64encode(png).decode()
        # Fallback: full screen
        img = ImageGrab.grab()
        img = img.resize((1280, 800))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.standard_b64encode(buf.getvalue()).decode()

    def run_task(self, task_description, max_steps=30):
        """Run a Computer Use task with Claude as the agent."""
        print(f"\n[Agent] Task: {task_description}")

        tools = [
            {
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1280,
                "display_height_px": 800
            }
        ]

        messages = [{"role": "user", "content": task_description}]

        for step in range(max_steps):
            # Add current screenshot
            img_b64 = self.screenshot_b64()
            if messages[-1]["role"] == "user" and isinstance(messages[-1]["content"], str):
                messages[-1]["content"] = [
                    {"type": "text", "text": messages[-1]["content"]},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}}
                ]

            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=tools,
                messages=messages,
                betas=["computer-use-2025-01-24"]
            )

            # Process response
            assistant_content = []
            for block in response.content:
                assistant_content.append(block)
                if block.type == "text":
                    print(f"  [Claude] {block.text[:200]}")
                    # Extract any values Claude found
                    self._extract_values(block.text)

            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason == "end_turn":
                print(f"  [Agent] Task complete after {step+1} steps")
                break

            # Execute tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "computer":
                    result = self._execute_action(block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            if tool_results:
                # Add new screenshot after actions
                time.sleep(1)
                new_img = self.screenshot_b64()
                tool_results[-1]["content"] = [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": new_img}}
                ]
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return self.extracted

    def _execute_action(self, action):
        """Execute a computer use action via Playwright."""
        action_type = action.get("action")
        if not self.page:
            return [{"type": "text", "text": "No browser page"}]

        try:
            if action_type == "screenshot":
                pass  # handled in main loop
            elif action_type == "left_click":
                x, y = action["coordinate"]
                self.page.mouse.click(x, y)
            elif action_type == "double_click":
                x, y = action["coordinate"]
                self.page.mouse.dblclick(x, y)
            elif action_type == "type":
                self.page.keyboard.type(action["text"])
            elif action_type == "key":
                self.page.keyboard.press(action["text"])
            elif action_type == "scroll":
                x, y = action["coordinate"]
                direction = action.get("direction", "down")
                amount = action.get("amount", 3)
                self.page.mouse.wheel(0, amount * 100 if direction == "down" else -amount * 100)
            elif action_type == "right_click":
                x, y = action["coordinate"]
                self.page.mouse.click(x, y, button="right")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [Action error] {e}")

        return [{"type": "text", "text": "Action executed"}]

    def _extract_values(self, text):
        """Extract API keys/secrets from Claude's text output."""
        patterns = {
            "REDDIT_CLIENT_ID":     r"client.?id[:\s]+([a-zA-Z0-9_-]{10,30})",
            "REDDIT_CLIENT_SECRET": r"client.?secret[:\s]+([a-zA-Z0-9_-]{20,40})",
            "TWITTER_API_KEY":      r"api.?key[:\s]+([a-zA-Z0-9]{20,50})",
            "TWITTER_API_SECRET":   r"api.?secret[:\s]+([a-zA-Z0-9]{40,60})",
            "TWITTER_ACCESS_TOKEN": r"access.?token[:\s]+([0-9]+-[a-zA-Z0-9]{30,50})",
            "PINTEREST_ACCESS_TOKEN": r"access.?token[:\s]+([a-zA-Z0-9_-]{40,80})",
            "LINKEDIN_ACCESS_TOKEN":  r"access.?token[:\s]+([a-zA-Z0-9_-]{50,200})",
        }
        for key, pattern in patterns.items():
            m = re.search(pattern, text, re.IGNORECASE)
            if m and key not in self.extracted:
                self.extracted[key] = m.group(1)
                print(f"  [Extracted] {key}: {m.group(1)[:10]}...")

    def save_to_env(self):
        """Save all extracted values to .env file."""
        for key, value in self.extracted.items():
            set_key(str(ENV_FILE), key, value)
            print(f"  [.env] Saved: {key}")

    def __enter__(self):
        if PLAYWRIGHT_OK:
            self._pw = sync_playwright().start()
            self.browser = self._pw.chromium.launch(headless=self.headless, slow_mo=500)
            ctx = self.browser.new_context(viewport={"width": 1280, "height": 800})
            self.page = ctx.new_page()
        return self

    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if hasattr(self, "_pw"):
            self._pw.stop()


# ─────────────────────────────────────────────
# TASK DEFINITIONS
# ─────────────────────────────────────────────

TASKS = {
    "setup_reddit": {
        "url": "https://www.reddit.com/prefs/apps",
        "prompt": """You are helping set up a Reddit developer app for RankerToolAI.

Current page: Reddit Apps preferences page.

Steps to complete:
1. Look for "create another app" button or "create app" button and click it
2. Fill in the form:
   - name: rankertoolai
   - Select the "script" radio button
   - description: AI tool review site
   - about url: https://rankertoolai.com
   - redirect uri: http://localhost:8080
3. Click "create app" button
4. After creation, the page will show the app with a client_id (short string under the app name) and client_secret
5. Read and report both values clearly as:
   client_id: [value]
   client_secret: [value]

Complete these steps now."""
    },

    "setup_twitter": {
        "url": "https://developer.twitter.com/en/portal/projects-and-apps",
        "prompt": """You are helping set up a Twitter/X developer app for RankerToolAI.

Steps:
1. Look for "Create Project" or "+ New Project" button and click it
2. Project name: RankerToolAI
3. Use case: select "Making a bot" or closest option
4. Project description: AI tool review and ranking site
5. App name: rankertoolai
6. Complete creation - you'll get API Key and API Secret
7. Also generate Access Token and Access Token Secret
8. Report all 4 values clearly:
   API Key: [value]
   API Key Secret: [value]
   Access Token: [value]
   Access Token Secret: [value]

Complete these steps now."""
    },

    "setup_pinterest": {
        "url": "https://developers.pinterest.com/apps/",
        "prompt": """You are helping set up a Pinterest developer app for RankerToolAI.

Steps:
1. Click "New app" or "Create app" button
2. App name: RankerToolAI
3. Description: AI tool review site that pins tool review infographics
4. Website: https://rankertoolai.com
5. Complete app creation
6. Generate an access token with scopes: boards:read, boards:write, pins:read, pins:write
7. Report the access token clearly:
   access_token: [value]

Complete these steps now."""
    },

    "post_twitter": {
        "url": "https://twitter.com/compose/tweet",
        "prompt": """Post this tweet on Twitter/X:

"We tested 10 AI tools for 30 days each. Here are the honest scores:

🥇 Semrush 9.3/10 — SEO
🥇 ElevenLabs 9.2/10 — Voice
🥇 Cursor 9.2/10 — Coding
🥈 Surfer SEO 9.0/10 — Content

No sponsored content. Full reviews: rankertoolai.com

#AITools #ProductivityTools #Tech"

Steps:
1. Click on the tweet compose area
2. Type or paste the tweet text
3. Click "Post" or "Tweet" button
4. Confirm it was posted successfully"""
    },
}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def check_requirements():
    issues = []
    if not ANTHROPIC_KEY:
        issues.append("ANTHROPIC_API_KEY missing in .env")
    if not PLAYWRIGHT_OK:
        issues.append("playwright not installed: pip install playwright && playwright install chromium")

    # Test API credits
    if ANTHROPIC_KEY:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=5,
                messages=[{"role": "user", "content": "hi"}]
            )
        except anthropic._exceptions.AuthenticationError:
            issues.append("Anthropic API key invalid")
        except Exception as e:
            if "credit" in str(e).lower() or "billing" in str(e).lower():
                issues.append("Anthropic account has $0 credits — add $5 at console.anthropic.com/settings/billing")
            else:
                issues.append(f"Anthropic API error: {e}")

    return issues

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=list(TASKS.keys()) + ["setup_all", "post_all"], required=True)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    print("Checking requirements...")
    issues = check_requirements()
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        if any("credit" in i for i in issues):
            print("\nTo add Anthropic credits:")
            print("  console.anthropic.com/settings/billing → Add $5")
        sys.exit(1)

    print("All requirements OK. Starting agent...")

    if args.task == "setup_all":
        task_list = ["setup_reddit", "setup_twitter", "setup_pinterest"]
    elif args.task == "post_all":
        task_list = ["post_twitter"]
    else:
        task_list = [args.task]

    all_extracted = {}

    for task_name in task_list:
        task = TASKS[task_name]
        print(f"\n{'='*50}")
        print(f"TASK: {task_name}")
        print(f"{'='*50}")

        with ComputerUseAgent(headless=args.headless) as agent:
            if "url" in task:
                agent.page.goto(task["url"])
                time.sleep(2)

            extracted = agent.run_task(task["prompt"])
            all_extracted.update(extracted)

            if extracted:
                agent.save_to_env()
                print(f"\nExtracted {len(extracted)} credentials from {task_name}")
            else:
                print(f"\nNo credentials extracted from {task_name}")

        time.sleep(3)

    print(f"\n{'='*50}")
    print("DONE. Credentials saved to .env")
    print("Run: python run_all.py --status")
