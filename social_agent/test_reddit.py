import praw, os
from dotenv import load_dotenv
load_dotenv()

client_id     = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
username      = os.getenv("REDDIT_USERNAME")
password      = os.getenv("REDDIT_PASSWORD")

print(f"CLIENT_ID:     {'[SET]' if client_id else '[MISSING]'}")
print(f"CLIENT_SECRET: {'[SET]' if client_secret else '[MISSING]'}")
print(f"USERNAME:      {username}")
print(f"PASSWORD:      {'[SET]' if password else '[MISSING]'}")

if not client_id or not client_secret:
    print("\nKhong the ket noi: thieu CLIENT_ID hoac CLIENT_SECRET")
else:
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent="RankerToolAI/1.0"
        )
        me = reddit.user.me()
        print(f"\nKet noi thanh cong! Logged in as: u/{me.name}")
    except Exception as e:
        print(f"\nLoi: {e}")
