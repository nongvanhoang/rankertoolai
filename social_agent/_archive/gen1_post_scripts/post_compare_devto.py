"""Post a Julius AI vs ChatGPT comparison article to Dev.to."""
import os, requests
from dotenv import load_dotenv
load_dotenv()
import anthropic

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

COMPARE_URL = "https://rankertoolai.com/compare/julius-ai-vs-chatgpt/"
JULIUS_URL  = "https://rankertoolai.com/go/julius-ai/"
COUPON      = "25RQK3UL"

prompt = f"""Write a Dev.to article titled: "Julius AI vs ChatGPT for Data Analysis: I Tested Both for a Month (2026)"

This is a comparison article for developers, analysts, and tech-curious readers on Dev.to.

Key facts to include:
- Julius AI: purpose-built for data analysis, $20/mo Pro, Free tier (15 analyses/month), handles CSV/Excel/SQL/Google Sheets natively, auto-generates Python/R code AND charts, maintains session context
- ChatGPT Plus: $20/mo, general-purpose, Code Interpreter for data analysis, good coding but requires more prompting, loses context between sessions
- Julius AI wins for: non-technical data users, chart quality, session context retention, Google Sheets integration
- ChatGPT wins for: general use, coding flexibility, writing tasks
- Coupon code: {COUPON} gives 10% off Julius AI first payment

Structure:
## The Test Setup
## Data Analysis Quality (Winner: Julius AI)
## File Handling & Formats
## Chart & Visualization Quality
## Ease of Use for Non-Coders
## Pricing: Same Cost, Different Value
## When to Use Each Tool
## Final Verdict

End with:
"[Full comparison with feature table: Julius AI vs ChatGPT]({COMPARE_URL})"
"Use code **{COUPON}** for 10% off Julius AI → [Try Julius AI free]({JULIUS_URL})"
"**My verdict: Julius AI for data work, ChatGPT for everything else.**"

Format: Markdown. Dev.to audience = developers + technical users. Conversational but data-driven tone.
600-800 words. Include at least one concrete example query like: 'Which products have declining sales in Q3?'
Return ONLY article body (no frontmatter, no title line). Start with intro paragraph."""

print("Generating article with Claude...")
msg = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}]
)
body = msg.content[0].text.strip()
print(f"Article generated ({len(body)} chars)")
print("---PREVIEW---")
print(body[:300])
print("---END PREVIEW---")

title = "Julius AI vs ChatGPT for Data Analysis: I Tested Both for a Month (2026)"
tags  = ["ai", "datascience", "productivity", "tools"]

payload = {
    "article": {
        "title": title,
        "body_markdown": body,
        "published": True,
        "tags": tags,
        "canonical_url": COMPARE_URL,
    }
}
print(f"\nPosting to Dev.to...")
r = requests.post(
    "https://dev.to/api/articles",
    json=payload,
    headers={"api-key": DEVTO_API_KEY, "Content-Type": "application/json"},
    timeout=30,
)
if r.status_code in (200, 201):
    data = r.json()
    print(f"SUCCESS! Article URL: {data.get('url','')}")
    print(f"Title: {data.get('title','')}")
else:
    print(f"FAILED: {r.status_code} — {r.text[:300]}")
