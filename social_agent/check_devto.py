import requests, os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("DEVTO_API_KEY")
r = requests.get("https://dev.to/api/articles/me/published", headers={"api-key": api_key})
articles = r.json()
if isinstance(articles, list):
    print(f"Total published: {len(articles)}")
    for a in articles:
        print(f"\n- [{a['id']}] {a['title']}")
        print(f"  URL: {a['url']}")
        print(f"  Views: {a.get('page_views_count',0)} | Reactions: {a.get('public_reactions_count',0)}")
else:
    print(articles)
