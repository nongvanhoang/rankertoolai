import anthropic
import os
import json
from database import get_next_variation, mark_variation_used

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Content variation angles — rotated per tool per platform to avoid repetition
VARIATIONS = ["tip", "comparison", "use_case", "question", "stat", "verdict"]

VARIATION_PREFIXES = {
    "tip":        "Share a specific power tip or workflow hack for using {tool_name}. Lead with the tip, explain why it works.",
    "comparison": "Compare {tool_name} with its closest competitor. Mention one area where {tool_name} wins and one where it loses. Be honest.",
    "use_case":   "Describe one specific real-world use case where {tool_name} shines. Make it concrete — who, what task, what result.",
    "question":   "Ask the community a genuine question about {tool_name}. Share your own experience briefly, then ask for theirs.",
    "stat":       "Lead with a surprising fact, number, or data point about {tool_name} or its category. Make it the hook.",
    "verdict":    "Give your honest bottom-line verdict on {tool_name} in one paragraph. Score: {score}/10. Who should and shouldn't use it.",
}

PLATFORM_PROMPTS = {
    "reddit": """Write a Reddit post for r/{subreddit} about {tool_name}.
Style: Helpful, conversational, NO salesy tone. Share genuine insights.
Format: Title on first line, then body. Mention the tool naturally.
Include: 1 specific tip or comparison, honest pros/cons.
End with: a subtle mention of the full review at {url} (don't make it the focus).
Max 300 words. Sound like a real user sharing experience.""",

    "twitter": """Write 3 tweets about {tool_name} ({score}/10 score).
Each tweet max 270 chars. Include relevant hashtags: {hashtags}.
Tweet 1: Share a surprising fact or tip
Tweet 2: Quick comparison or use case
Tweet 3: Score reveal with CTA to review
Separate tweets with ---
Sound natural, not promotional.""",

    "devto": """Write a Dev.to article about {tool_name}.
Title: Practical, specific (e.g. "I tested {tool_name} for 30 days — here's what happened")
Tags: ai, productivity, tools, webdev
Format: Markdown with ## headers
Include: code snippet or workflow example if relevant
Word count: 600-800 words
End with link to full review: {url}
Score: {score}/10""",

    "medium": """Write a Medium article about {tool_name}.
Title: Story-driven, curiosity-inducing
Subtitle: Clear value proposition
Format: Engaging narrative + practical tips
Opening: Hook with a relatable problem or surprising stat
Include: personal experience angle, specific examples
Word count: 700-900 words
CTA at end: link to {url} for full breakdown
Score: {score}/10""",

    "linkedin": """Write a LinkedIn post about {tool_name}.
Audience: Business professionals, marketers, entrepreneurs
Style: Professional but conversational, thought leadership tone
Format: Short paragraphs, each 1-2 sentences. Use line breaks.
Hook: Start with a bold statement or question (no "I" as first word)
Include: Business ROI angle, time/money saved
Length: 200-250 words
End with CTA and link: {url}
Hashtags: {hashtags} (3-4 only)""",

    "pinterest": """Write a Pinterest pin description for {tool_name}.
Style: Inspiring, actionable, keyword-rich for SEO
Include: What it does, who it's for, key benefit
Keywords: naturally include {category} related terms
Length: 150-200 characters for description
Title: 50-60 chars, keyword-first
CTA: Include "Save for later" or "Click to learn more"
Link: {url}""",

    "discord": """Write a Discord message to share in an AI tools community about {tool_name}.
Style: Casual, helpful, like a community member sharing a find
NOT promotional — share a genuine insight or tip
Include: one specific use case or workflow tip
Length: 2-3 short paragraphs max
Mention the review link {url} casually at the end""",

    "hashnode": """Write a Hashnode blog post about {tool_name}.
Title: SEO-optimized, specific
Subtitle: Benefit-focused
Format: Well-structured Markdown with headers, bullet points
Include: Detailed feature breakdown, pricing table, who should use it
Word count: 800-1000 words
Score: {score}/10
CTA: Link to {url} for more details""",

    "quora": """Write a Quora answer about {tool_name} for the question: "{quora_question}"
Style: Expert, helpful, detailed — like someone who has used the tool extensively
Format: Start with direct answer, then elaborate with specifics
Include: pros, cons, pricing, alternatives comparison
Length: 300-400 words
At the end naturally mention: "I wrote a full review at {url} if you want more details"
NO promotional tone — be genuinely helpful""",

    "threads": """Write a Threads post about {tool_name}.
Style: Casual, punchy — like a knowledgeable friend sharing a quick take
Format: 2-3 short paragraphs. No bullet lists. Conversational tone.
Hook: Open with a bold one-liner (not "I" as first word)
Include: One specific tip or surprising fact, honest score {score}/10
CTA: End with the review link {url} naturally worked in
Max 480 characters total (Threads limit). Tight, no fluff.
Hashtags: add 3 hashtags at the very end: {hashtags}"""
}

def generate_content(platform, tool, variation=None, **kwargs):
    tool_info = {
        "tool_name": tool["name"],
        "score": tool["score"],
        "category": tool["category"],
        "url": tool["url"],
        "hashtags": " ".join(tool["hashtags"][:5]),
        "price": tool["price"],
        "best_for": tool["best_for"],
        "pros": ", ".join(tool["pros"]),
        "cons": ", ".join(tool["cons"]),
        **kwargs
    }

    # Pick content variation (auto-rotate if not specified)
    if variation is None:
        variation = get_next_variation(platform, tool["slug"], VARIATIONS)
    mark_variation_used(platform, tool["slug"], variation)

    variation_prefix = VARIATION_PREFIXES.get(variation, "").format(**tool_info)

    prompt_template = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS["medium"])
    base_prompt = prompt_template.format(**{k: v for k, v in tool_info.items() if "{"+k+"}" in prompt_template})

    # Prepend the variation angle to guide the content direction
    prompt = f"ANGLE FOR THIS POST: {variation_prefix}\n\n{base_prompt}"

    system = f"""You are a content creator who genuinely uses and tests AI tools.
You write honest, helpful content that provides real value.
Tool being featured: {tool['name']} — Score: {tool['score']}/10
Key strengths: {', '.join(tool['pros'][:2])}
Best for: {tool['best_for']}
Content angle this time: {variation}
Never sound like an ad. Sound like a real person sharing a useful discovery."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def generate_quora_answer(tool, question):
    return generate_content("quora", tool, quora_question=question)


def generate_reddit_post(tool, subreddit):
    content = generate_content("reddit", tool, subreddit=subreddit)
    lines = content.strip().split("\n")
    title = lines[0].strip().lstrip("#").strip()
    body = "\n".join(lines[1:]).strip()
    return title, body
