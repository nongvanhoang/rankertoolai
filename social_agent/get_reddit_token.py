"""
Reddit OAuth2 Token Helper
============================
Chạy script này để lấy Reddit refresh token cho auto-posting.

Usage:
  python social_agent/get_reddit_token.py

Steps:
  1. Tạo Reddit App tại https://www.reddit.com/prefs/apps
  2. Chọn "script" app type
  3. Set redirect URI: http://localhost:8789/callback
  4. Script mở trình duyệt để xác thực
  5. Token lưu tự động vào .env

Required .env keys (output):
  REDDIT_CLIENT_ID=...
  REDDIT_CLIENT_SECRET=...
  REDDIT_USERNAME=...
  REDDIT_PASSWORD=...
  REDDIT_USER_AGENT=RankerToolAI/1.0 by u/YourUsername
"""

import os
import sys
import json
import webbrowser
import urllib.parse
import urllib.request
import http.server
import threading
import time
import secrets
import base64

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

REDIRECT_URI = "http://localhost:8789/callback"
SCOPES = "submit identity read"

captured_code = None
captured_state = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code, captured_state
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            captured_code = params["code"][0]
            captured_state = params.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html><body style="font-family:sans-serif;max-width:600px;margin:2rem auto;text-align:center">
            <h2 style="color:#ff4500">Reddit authorization successful!</h2>
            <p>You can close this tab and return to the terminal.</p>
            </body></html>
            """)
        elif "error" in params:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <html><body style="font-family:sans-serif;max-width:600px;margin:2rem auto;text-align:center">
            <h2 style="color:red">Authorization failed: {error}</h2>
            </body></html>
            """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def get_token(client_id, client_secret, code):
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "User-Agent": "RankerToolAI/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def verify_token(access_token, user_agent):
    req = urllib.request.Request(
        "https://oauth.reddit.com/api/v1/me",
        headers={
            "Authorization": f"bearer {access_token}",
            "User-Agent": user_agent,
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("name", "")
    except Exception:
        return ""


def save_to_env(updates, env_path):
    lines = []
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            lines = f.readlines()

    for key, value in updates.items():
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"{key}={value}\n")
        lines = new_lines

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    print("=" * 60)
    print("  Reddit OAuth Token Helper — RankerToolAI")
    print("=" * 60)

    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("\nStep 1: Create a Reddit App")
        print("  URL: https://www.reddit.com/prefs/apps")
        print("\nSettings:")
        print("  - App type: 'script'")
        print("  - Name: RankerToolAI")
        print("  - Redirect URI: http://localhost:8789/callback")
        print("  - Permissions: submit, identity, read")
        print()
        client_id = input("Enter your Reddit App Client ID: ").strip()
        client_secret = input("Enter your Reddit App Client Secret: ").strip()

        if not client_id or not client_secret:
            print("\nError: Client ID and Secret are required.")
            sys.exit(1)

    username = os.getenv("REDDIT_USERNAME", "").strip()
    if not username:
        username = input("\nEnter your Reddit username (without u/): ").strip()

    user_agent = f"RankerToolAI/1.0 by u/{username}"

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://www.reddit.com/api/v1/authorize?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": REDIRECT_URI,
            "duration": "permanent",
            "scope": SCOPES,
        })
    )

    print(f"\nStarting local callback server on port 8789...")
    server = http.server.HTTPServer(("localhost", 8789), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f"Opening Reddit authorization in browser...")
    print(f"\nIf browser doesn't open, go to:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for authorization (60 seconds timeout)...")
    timeout = 60
    while captured_code is None and timeout > 0:
        time.sleep(1)
        timeout -= 1

    server.shutdown()

    if captured_code is None:
        print("\nTimeout: No authorization received.")
        sys.exit(1)

    if captured_state != state:
        print("\nSecurity error: State mismatch.")
        sys.exit(1)

    print("\nExchanging code for access token...")
    try:
        token_data = get_token(client_id, client_secret, captured_code)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token", "")
    scope = token_data.get("scope", "")

    if not access_token:
        print(f"\nError: No access_token in response: {token_data}")
        sys.exit(1)

    print(f"\nToken received! Scope: {scope}")

    # Verify identity
    reddit_name = verify_token(access_token, user_agent)
    if reddit_name:
        print(f"Verified as: u/{reddit_name}")
    else:
        print("Warning: Could not verify identity (token may still be valid)")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    updates = {
        "REDDIT_CLIENT_ID": client_id,
        "REDDIT_CLIENT_SECRET": client_secret,
        "REDDIT_USERNAME": username,
        "REDDIT_USER_AGENT": user_agent,
    }
    if refresh_token:
        updates["REDDIT_REFRESH_TOKEN"] = refresh_token

    save_to_env(updates, env_path)
    print(f"\nCredentials saved to {env_path}")

    print("\n" + "=" * 60)
    print("  .env entries saved:")
    print("=" * 60)
    for key, value in updates.items():
        display = value[:30] + "..." if len(value) > 30 else value
        print(f"  {key}={display}")
    print("=" * 60)

    print("\nIMPORTANT: Reddit also needs your password for PRAW.")
    print("Add this to .env manually:")
    print("  REDDIT_PASSWORD=your_reddit_password")
    print("\nPRAW uses username+password for 'script' app type.")

    print("\nDone! Reddit posting is now active.")
    print("Run: python social_agent/run_all.py --status")

    if refresh_token:
        print("\nRefresh token saved — Reddit sessions won't expire.")


if __name__ == "__main__":
    main()
