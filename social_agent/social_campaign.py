"""RankerToolAI social campaign automation.

Builds a campaign pack for a selected tool and writes platform-specific
drafts, a schedule, and a machine-readable JSON summary to output/campaigns/.

Usage:
  python social_campaign.py
  python social_campaign.py --tool semrush
  python social_campaign.py --week-start 2026-06-22
  python social_campaign.py --no-llm
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

from database import init_db

BASE_DIR = Path(__file__).resolve().parent
TOOLS_FILE = BASE_DIR / "data" / "tools.json"
PROFILE_FILE = BASE_DIR / "data" / "social_profiles.md"
CONTENT_READY_FILE = BASE_DIR / "data" / "content_ready.md"
OUTPUT_ROOT = BASE_DIR / "output" / "campaigns"

WEEKLY_PLAN = [
    (0, "linkedin"),
    (1, "twitter"),
    (2, "reddit"),
    (3, "pinterest"),
    (4, "medium"),
    (5, "devto"),
    (6, "quora"),
]


def load_tools() -> List[Dict]:
    with open(TOOLS_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def select_tool(tools: List[Dict], slug: str | None = None) -> Dict:
    if slug:
        for tool in tools:
            if tool["slug"] == slug:
                return tool
    return max(tools, key=lambda item: item.get("score", 0))


def format_hashtags(tool: Dict, limit: int = 5) -> str:
    hashtags = tool.get("hashtags", [])[:limit]
    return " ".join(hashtags)


def render_twitter(tool: Dict) -> str:
    hashtags = format_hashtags(tool)
    return (
        f"{tool['name']} scored {tool['score']}/10 after real testing.\n"
        f"What stood out most: {tool['pros'][0]}.\n"
        f"Biggest tradeoff: {tool['cons'][0]}.\n\n"
        f"For creators and teams who need {tool['best_for'].lower()}, this is worth a closer look.\n"
        f"Full review: {tool['url']}\n\n"
        f"{hashtags}\n---\n"
        f"If you care about {tool['category'].lower()}, {tool['name']} is one of the strongest options we tested.\n"
        f"Its edge comes from {tool['pros'][1].lower() if len(tool['pros']) > 1 else tool['pros'][0].lower()}.\n"
        f"Would I recommend it? Yes for the right use case.\n---\n"
        f"Final score: {tool['score']}/10.\n"
        f"Read the full breakdown: {tool['url']}"
    )


def render_linkedin(tool: Dict) -> str:
    return (
        f"We tested {tool['name']} across real workflows, not just specs.\n\n"
        f"The short version: it earned a {tool['score']}/10 because it solves {tool['best_for'].lower()} better than most alternatives.\n\n"
        f"What stood out:\n"
        f"- {tool['pros'][0]}\n"
        f"- {tool['pros'][1] if len(tool['pros']) > 1 else tool['pros'][0]}\n"
        f"- Clear value for teams that care about speed and quality\n\n"
        f"What to watch out for:\n"
        f"- {tool['cons'][0]}\n"
        f"- {tool['cons'][1] if len(tool['cons']) > 1 else tool['cons'][0]}\n\n"
        f"If you are evaluating {tool['category'].lower()} tools this quarter, this deserves a spot on the shortlist.\n"
        f"Full review: {tool['url']}\n\n"
        f"#RankerToolAI #AITools #Productivity #{tool['slug'].replace('-', '').title()}"
    )


def render_reddit(tool: Dict) -> str:
    title = f"I tested {tool['name']} for real-world use - here is the honest takeaway"
    body = (
        f"After testing {tool['name']} for a real workflow, I ended up at {tool['score']}/10.\n\n"
        f"The strongest part was {tool['pros'][0]}. The main downside was {tool['cons'][0]}.\n\n"
        f"If you need {tool['best_for'].lower()}, it is a solid option. If you are on a tight budget or want something simpler, that is where the tradeoffs show up.\n\n"
        f"Full review for the details: {tool['url']}"
    )
    return f"{title}\n\n{body}"


def render_pinterest(tool: Dict) -> str:
    title = f"{tool['name']} Review | {tool['score']}/10"
    description = (
        f"{tool['name']} helps {tool['best_for'].lower()}. "
        f"See the pros, cons, pricing, and why it scored {tool['score']}/10. "
        f"Save for later and click to learn more: {tool['url']}"
    )
    return f"{title}\n{description}"


def render_medium(tool: Dict) -> str:
    return (
        f"# I tested {tool['name']} - here is what actually matters\n\n"
        f"{tool['name']} is a strong fit for {tool['best_for'].lower()}. After real testing, it landed at {tool['score']}/10.\n\n"
        f"## What it does well\n"
        f"- {tool['pros'][0]}\n"
        f"- {tool['pros'][1] if len(tool['pros']) > 1 else tool['pros'][0]}\n\n"
        f"## Where it falls short\n"
        f"- {tool['cons'][0]}\n"
        f"- {tool['cons'][1] if len(tool['cons']) > 1 else tool['cons'][0]}\n\n"
        f"## Verdict\n"
        f"If you need {tool['best_for'].lower()}, this is worth testing. Full review: {tool['url']}"
    )


def render_devto(tool: Dict) -> str:
    return (
        f"# {tool['name']} review: is it worth it in 2026?\n\n"
        f"I tested {tool['name']} for real workflows and scored it {tool['score']}/10.\n\n"
        f"## Key strengths\n"
        f"- {tool['pros'][0]}\n"
        f"- {tool['pros'][1] if len(tool['pros']) > 1 else tool['pros'][0]}\n\n"
        f"## Tradeoffs\n"
        f"- {tool['cons'][0]}\n"
        f"- {tool['cons'][1] if len(tool['cons']) > 1 else tool['cons'][0]}\n\n"
        f"## Who should use it\n"
        f"{tool['best_for']}\n\n"
        f"Full review: {tool['url']}"
    )


def render_hashnode(tool: Dict) -> str:
    return (
        f"# {tool['name']} review: practical takeaways for creators and teams\n\n"
        f"{tool['name']} scored {tool['score']}/10 in our testing.\n\n"
        f"## Why it stands out\n"
        f"- {tool['pros'][0]}\n"
        f"- {tool['pros'][1] if len(tool['pros']) > 1 else tool['pros'][0]}\n\n"
        f"## Things to know\n"
        f"- {tool['cons'][0]}\n"
        f"- {tool['cons'][1] if len(tool['cons']) > 1 else tool['cons'][0]}\n\n"
        f"Full review: {tool['url']}"
    )


def render_quora(tool: Dict) -> str:
    return (
        f"Yes, {tool['name']} is worth considering if you need {tool['best_for'].lower()}.\n\n"
        f"In our testing, the biggest advantages were {tool['pros'][0]} and {tool['pros'][1] if len(tool['pros']) > 1 else tool['pros'][0]}.\n\n"
        f"The main limitation is {tool['cons'][0]}.\n\n"
        f"If you want the full breakdown, I published it here: {tool['url']}"
    )


def render_discord(tool: Dict) -> str:
    return (
        f"Quick note: we tested {tool['name']} and it scored {tool['score']}/10.\n\n"
        f"Best part: {tool['pros'][0]}.\n"
        f"Watch out for: {tool['cons'][0]}.\n\n"
        f"If anyone here is using {tool['category'].lower()} tools for {tool['best_for'].lower()}, the full review is here: {tool['url']}"
    )


def render_platform(tool: Dict, platform: str, use_llm: bool = True) -> str:
    if use_llm:
        try:
            from content_generator import generate_content

            return generate_content(platform, tool)
        except Exception:
            pass

    renderers = {
        "twitter": render_twitter,
        "linkedin": render_linkedin,
        "reddit": render_reddit,
        "pinterest": render_pinterest,
        "medium": render_medium,
        "devto": render_devto,
        "hashnode": render_hashnode,
        "quora": render_quora,
        "discord": render_discord,
    }
    renderer = renderers.get(platform, render_medium)
    return renderer(tool)


def build_schedule(start_date: date, tool: Dict, platforms: List[str]) -> List[Dict]:
    schedule = []
    for offset, platform in WEEKLY_PLAN:
        if platform not in platforms:
            continue
        scheduled_date = start_date + timedelta(days=offset)
        schedule.append(
            {
                "date": scheduled_date.isoformat(),
                "day": scheduled_date.strftime("%A"),
                "platform": platform,
                "title": tool["name"],
            }
        )
    return schedule


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_campaign(
    tool: Dict,
    week_start: date | None = None,
    platforms: List[str] | None = None,
    use_llm: bool = True,
) -> str:
    week_start = week_start or date.today()
    platforms = platforms or [platform for _, platform in WEEKLY_PLAN]

    init_db()

    campaign_dir = OUTPUT_ROOT / week_start.isoformat() / tool["slug"]
    campaign_dir.mkdir(parents=True, exist_ok=True)

    profile_text = load_text(PROFILE_FILE)
    ready_text = load_text(CONTENT_READY_FILE)
    schedule = build_schedule(week_start, tool, platforms)

    campaign = {
        "brand": {
            "name": "RankerTool AI",
            "website": "https://rankertoolai.com",
            "handle": "@rankertoolai",
        },
        "tool": tool,
        "week_start": week_start.isoformat(),
        "schedule": schedule,
        "platforms": platforms,
    }

    details_md = [
        f"# Social Campaign: {tool['name']}",
        "",
        f"Website: https://rankertoolai.com",
        f"Handle: @rankertoolai",
        f"Score: {tool['score']}/10",
        f"Category: {tool['category']}",
        f"Target URL: {tool['url']}",
        "",
        "## Weekly schedule",
        "",
        "| Date | Day | Platform | Draft |",
        "| --- | --- | --- | --- |",
    ]

    for item in schedule:
        platform_path = campaign_dir / f"{item['platform']}.md"
        draft = render_platform(tool, item["platform"], use_llm=use_llm)
        write_text(platform_path, draft)
        item["file"] = str(platform_path.relative_to(BASE_DIR)).replace("\\", "/")
        details_md.append(
            f"| {item['date']} | {item['day']} | {item['platform']} | [{item['platform']}]({item['file']}) |"
        )

    details_md.extend(
        [
            "",
            "## Brand notes",
            "",
            "Use the same username and voice across platforms.",
            "",
            "## Profile reference",
            "",
            profile_text[:3000],
            "",
            "## Ready content reference",
            "",
            ready_text[:3000],
        ]
    )

    write_text(campaign_dir / "campaign.md", "\n".join(details_md).strip() + "\n")
    write_text(campaign_dir / "campaign.json", json.dumps(campaign, indent=2, ensure_ascii=False))

    return str(campaign_dir)


def parse_week_start(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a RankerToolAI social media campaign pack")
    parser.add_argument("--tool", help="Specific tool slug to feature")
    parser.add_argument("--week-start", help="Week start date in YYYY-MM-DD format")
    parser.add_argument("--platforms", help="Comma-separated list of platforms to include")
    parser.add_argument("--no-llm", action="store_true", help="Use deterministic drafts instead of AI generation")
    args = parser.parse_args()

    tools = load_tools()
    tool = select_tool(tools, args.tool)
    week_start = parse_week_start(args.week_start)
    platforms = [item.strip() for item in args.platforms.split(",")] if args.platforms else None

    campaign_dir = build_campaign(
        tool=tool,
        week_start=week_start,
        platforms=platforms,
        use_llm=not args.no_llm,
    )
    print(campaign_dir)


if __name__ == "__main__":
    main()