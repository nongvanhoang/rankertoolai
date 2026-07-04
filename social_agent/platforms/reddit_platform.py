import praw
import os
import random
from content_generator import generate_reddit_post
from database import log_post, already_posted, has_recent_error

def get_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "RankerToolAI/1.0")
    )

def post(tool):
    if already_posted("reddit", tool["slug"], days=7):
        print(f"[Reddit] Already posted {tool['name']} this week, skipping")
        return

    if has_recent_error("reddit", tool["slug"], hours=24):
        print(f"[Reddit] Recent error for {tool['name']}, cooling down 24h")
        return

    subreddit_name = random.choice(tool["reddit_subs"]).lstrip("r/")

    try:
        reddit = get_client()
        title, body = generate_reddit_post(tool, subreddit_name)

        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title=title, selftext=body)

        url = f"https://reddit.com{submission.permalink}"
        log_post("reddit", tool["slug"], "text_post", str(submission.id), url)
        print(f"[Reddit] Posted to r/{subreddit_name}: {url}")
        return url

    except Exception as e:
        log_post("reddit", tool["slug"], "text_post", status="error", error=str(e))
        print(f"[Reddit] Error: {e}")
        return None
