#!/usr/bin/env python3
"""
RankerToolAI — Interactive Platform Setup
Chạy: python social_agent/setup_new_platforms.py

Script này:
  1. Hỏi credentials cho từng platform còn thiếu
  2. Ghi vào .env
  3. Test kết nối ngay lập tức
  4. Tự lấy Hashnode Publication ID qua API

Platforms được setup: Reddit, Hashnode, Medium, Threads
"""
import os, sys, json, getpass, requests
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_FILE   = Path(__file__).parent / ".env"
TOKEN_DIR  = Path(__file__).parent

# ── Colors ─────────────────────────────────────────────────────────────────────
G = '\033[92m'; R = '\033[91m'; Y = '\033[93m'; C = '\033[96m'; B = '\033[1m'; X = '\033[0m'
def ok(s):   print(f"{G}  ✓  {s}{X}")
def err(s):  print(f"{R}  ✗  {s}{X}")
def info(s): print(f"{C}  ℹ  {s}{X}")
def hdr(s):  print(f"\n{B}{C}  {'─'*50}\n  {s}\n  {'─'*50}{X}")
def ask(prompt, secret=False):
    try:
        if secret:
            return getpass.getpass(f"  {prompt}: ")
        return input(f"  {prompt}: ").strip()
    except KeyboardInterrupt:
        print("\n  Đã thoát.")
        sys.exit(0)

def write_env(key, value):
    """Write or update a key in .env file."""
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")
    set_key(str(ENV_FILE), key, value)

def read_env(key):
    load_dotenv(ENV_FILE, override=True)
    return os.getenv(key, "").strip()

# ══════════════════════════════════════════════════════════════════════════════
# REDDIT
# ══════════════════════════════════════════════════════════════════════════════
def setup_reddit():
    hdr("REDDIT — Script App Setup")
    print("""
  Bạn cần tạo Reddit App (30 giây):
  1. Tab đã mở → reddit.com/prefs/apps
  2. Scroll xuống → "create another app"
  3. Name: RankerToolAI
  4. Type: ★ script  (không phải web app)
  5. About URL: https://rankertoolai.com
  6. redirect uri: http://localhost:8080
  7. Save → Copy 2 giá trị bên dưới
""")

    client_id = ask("CLIENT_ID (dãy chữ/số ngắn dưới tên app)")
    if not client_id:
        info("Bỏ qua Reddit."); return False

    client_secret = ask("CLIENT_SECRET (ấn reveal để thấy)", secret=True)
    username = read_env("REDDIT_USERNAME") or ask("Reddit username (e.g. rankertoolai)")
    password = read_env("REDDIT_PASSWORD") or ask("Reddit password", secret=True)

    # Test connection
    info("Đang test kết nối Reddit...")
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent="RankerToolAI/1.0"
        )
        me = reddit.user.me()
        ok(f"Reddit connected! User: u/{me.name}")

        write_env("REDDIT_CLIENT_ID", client_id)
        write_env("REDDIT_CLIENT_SECRET", client_secret)
        write_env("REDDIT_USERNAME", username)
        write_env("REDDIT_PASSWORD", password)
        write_env("REDDIT_USER_AGENT", "RankerToolAI/1.0")
        ok("Reddit credentials saved to .env")
        return True

    except Exception as e:
        err(f"Reddit test failed: {e}")
        info("Kiểm tra lại CLIENT_ID/SECRET và thử lại.")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# HASHNODE
# ══════════════════════════════════════════════════════════════════════════════
def setup_hashnode():
    hdr("HASHNODE — Personal Access Token")
    print("""
  Bạn cần tạo PAT token:
  1. Tab đã mở → hashnode.com/settings/developer
  2. "Generate New Token" → đặt tên: RankerToolAI → Generate
  3. Copy token (chỉ hiện 1 lần!)
""")

    token = ask("Hashnode PAT Token", secret=True)
    if not token:
        info("Bỏ qua Hashnode."); return False

    # Test + auto-fetch publication ID
    info("Đang test token và lấy Publication ID...")
    try:
        query = "{ me { id username publications(first:5) { edges { node { id title } } } } }"
        r = requests.post(
            "https://gql.hashnode.com",
            json={"query": query},
            headers={"Authorization": token, "Content-Type": "application/json", "Accept": "application/json"},
            timeout=10
        )
        ct = r.headers.get("Content-Type", "")
        if "text/html" in ct:
            err("Token không hợp lệ — Hashnode trả về HTML (Cloudflare block)")
            return False

        data = r.json()
        if data.get("errors"):
            err(f"GraphQL error: {data['errors'][0]['message']}")
            return False

        me = data["data"]["me"]
        pubs = me["publications"]["edges"]
        ok(f"Hashnode connected! User: @{me['username']}")

        if not pubs:
            err("Không tìm thấy publication. Vào hashnode.com → tạo blog trước.")
            return False

        print(f"\n  Publications tìm thấy:")
        for i, p in enumerate(pubs):
            print(f"    [{i}] {p['node']['title']} (ID: {p['node']['id']})")

        pub_id = pubs[0]["node"]["id"]
        if len(pubs) > 1:
            choice = ask(f"Chọn publication (0-{len(pubs)-1}, mặc định 0)")
            if choice.isdigit() and int(choice) < len(pubs):
                pub_id = pubs[int(choice)]["node"]["id"]

        write_env("HASHNODE_ACCESS_TOKEN", token)
        write_env("HASHNODE_PUBLICATION_ID", pub_id)
        ok(f"Hashnode saved. Publication ID: {pub_id}")
        return True

    except Exception as e:
        err(f"Hashnode test failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# MEDIUM
# ══════════════════════════════════════════════════════════════════════════════
def setup_medium():
    hdr("MEDIUM — Integration Token")
    print("""
  Lấy Medium token (1 phút):
  1. Vào: https://medium.com/me/settings/security
  2. "Integration tokens" → mô tả: RankerToolAI → Get token
  3. Copy token
""")
    import webbrowser
    webbrowser.open("https://medium.com/me/settings/security")

    token = ask("Medium Integration Token", secret=True)
    if not token:
        info("Bỏ qua Medium."); return False

    info("Đang test Medium token...")
    try:
        r = requests.get(
            "https://api.medium.com/v1/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            user = r.json()["data"]
            ok(f"Medium connected! User: {user.get('name')} (@{user.get('username')})")
            write_env("MEDIUM_ACCESS_TOKEN", token)
            write_env("MEDIUM_AUTHOR_ID", user["id"])
            ok("Medium credentials saved to .env")
            return True
        else:
            err(f"Medium test failed: {r.status_code} — {r.text[:100]}")
            return False
    except Exception as e:
        err(f"Medium test failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# THREADS (META)
# ══════════════════════════════════════════════════════════════════════════════
def setup_threads():
    hdr("THREADS — Meta Developer App")
    print("""
  Threads setup phức tạp hơn (5-10 phút):
  1. Vào: https://developers.facebook.com
  2. My Apps → Create App → Consumer
  3. Add Product: Threads API
  4. Settings → Basic → copy App ID + App Secret
  5. Chạy sau: python social_agent/threads_poster.py auth
     (Script sẽ mở browser để authorize Threads account)
""")
    import webbrowser
    webbrowser.open("https://developers.facebook.com/apps")

    app_id = ask("Threads App ID (tìm trong Settings > Basic)")
    if not app_id:
        info("Bỏ qua Threads. Chạy lại script sau khi đã tạo app."); return False

    app_secret = ask("Threads App Secret", secret=True)

    write_env("THREADS_APP_ID", app_id)
    write_env("THREADS_APP_SECRET", app_secret)
    ok("Threads App ID/Secret saved to .env")
    info("Bước tiếp: python social_agent/threads_poster.py auth")
    return True

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print(f"\n{B}{C}  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  RankerToolAI — Platform Credential Setup      ║")
    print(f"  ╚══════════════════════════════════════════════════╝{X}\n")

    load_dotenv(ENV_FILE)

    # LinkedIn is already done — confirm
    hdr("LinkedIn — Checking existing token")
    token_file = TOKEN_DIR / "linkedin_tokens.json"
    if token_file.exists():
        import json, time
        d = json.loads(token_file.read_text())
        exp = d.get("expires_at", 0)
        days = (exp - time.time()) / 86400
        if days > 0:
            ok(f"LinkedIn token valid — {days:.0f} days remaining. Nothing to do!")
        else:
            err("LinkedIn token expired. Run: python social_agent/linkedin_poster.py auth")
    else:
        err("LinkedIn not configured. Run: python social_agent/linkedin_poster.py auth")

    results = {}

    # Reddit
    r_done = bool(read_env("REDDIT_CLIENT_ID") and read_env("REDDIT_CLIENT_SECRET"))
    if r_done:
        ok("Reddit already configured — skip")
        results["Reddit"] = True
    else:
        results["Reddit"] = setup_reddit()

    # Hashnode
    hn_done = bool(read_env("HASHNODE_ACCESS_TOKEN") and read_env("HASHNODE_PUBLICATION_ID"))
    # Also verify token isn't broken (returns HTML)
    if hn_done:
        info("Hashnode has token — verifying it's not expired...")
        try:
            q = "{ me { id } }"
            r = requests.post("https://gql.hashnode.com",
                json={"query": q},
                headers={"Authorization": read_env("HASHNODE_ACCESS_TOKEN"),
                         "Content-Type":"application/json","Accept":"application/json"})
            if "text/html" in r.headers.get("Content-Type",""):
                err("Hashnode token expired — need new token")
                results["Hashnode"] = setup_hashnode()
            else:
                ok("Hashnode token valid"); results["Hashnode"] = True
        except:
            results["Hashnode"] = setup_hashnode()
    else:
        results["Hashnode"] = setup_hashnode()

    # Medium
    med_done = bool(read_env("MEDIUM_ACCESS_TOKEN"))
    if med_done:
        ok("Medium already configured — skip")
        results["Medium"] = True
    else:
        results["Medium"] = setup_medium()

    # Threads
    th_done = bool(read_env("THREADS_APP_ID") and read_env("THREADS_APP_SECRET"))
    if th_done:
        ok("Threads App credentials set. Run threads_poster.py auth if not done yet.")
        results["Threads"] = True
    else:
        results["Threads"] = setup_threads()

    # Summary
    hdr("SETUP COMPLETE — Summary")
    for platform, success in results.items():
        if success:
            ok(f"{platform}")
        else:
            err(f"{platform} — skipped or failed")

    active = sum(1 for v in results.values() if v)
    total = len(results) + 1  # +1 for LinkedIn which is always counted
    print(f"\n  Platforms ready: LinkedIn + {active}/{len(results)} others")
    print(f"\n  Test all platforms:")
    print(f"  python social_agent/auto_post_all.py\n")

if __name__ == "__main__":
    main()
