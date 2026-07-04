"""
LinkedIn OAuth 2.0 Token Helper
================================
Chạy script này để lấy LinkedIn access token.

Usage:
  python social_agent/get_linkedin_token.py

Steps:
  1. Tạo LinkedIn Developer App tại https://www.linkedin.com/developers/apps
  2. Điền Client ID và Client Secret vào đây hoặc .env
  3. Script mở trình duyệt để xác thực
  4. Copy token vào .env

Required .env keys:
  LINKEDIN_CLIENT_ID=...
  LINKEDIN_CLIENT_SECRET=...
  LINKEDIN_ACCESS_TOKEN=...  (output của script này)
"""

import os
import sys
import json
import webbrowser
import urllib.parse
import http.server
import threading
import time
import secrets
import base64
import hashlib
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

REDIRECT_URI = "http://localhost:8787/callback"
SCOPES = "openid profile email w_member_social"

# Token captured from callback
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
            <h2 style="color:#0a66c2">Authorization successful!</h2>
            <p>You can close this tab and return to the terminal.</p>
            </body></html>
            """)
        elif "error" in params:
            error = params.get("error", ["unknown"])[0]
            desc = params.get("error_description", [""])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <html><body style="font-family:sans-serif;max-width:600px;margin:2rem auto;text-align:center">
            <h2 style="color:red">Authorization failed</h2>
            <p>Error: {error}</p>
            <p>{desc}</p>
            </body></html>
            """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silence access logs


def exchange_code_for_token(client_id, client_secret, code):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = urllib.request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def save_token_to_env(token, env_path):
    lines = []
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
            new_lines.append(f"LINKEDIN_ACCESS_TOKEN={token}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"\nLINKEDIN_ACCESS_TOKEN={token}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def main():
    print("=" * 60)
    print("  LinkedIn OAuth Token Helper — RankerToolAI")
    print("=" * 60)

    client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("\nStep 1: Create a LinkedIn Developer App")
        print("  URL: https://www.linkedin.com/developers/apps/new")
        print("\nIn the app settings:")
        print("  - Products: Add 'Share on LinkedIn' and 'Sign In with LinkedIn using OpenID Connect'")
        print("  - Auth tab → Redirect URLs: Add http://localhost:8787/callback")
        print()
        client_id = input("Enter your LinkedIn Client ID: ").strip()
        client_secret = input("Enter your LinkedIn Client Secret: ").strip()

        if not client_id or not client_secret:
            print("\nError: Client ID and Secret are required.")
            sys.exit(1)

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
        })
    )

    print(f"\nStarting local callback server on port 8787...")
    server = http.server.HTTPServer(("localhost", 8787), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f"Opening LinkedIn authorization in browser...")
    print(f"\nIf browser doesn't open, go to:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for authorization (60 seconds timeout)...")
    timeout = 60
    while captured_code is None and timeout > 0:
        time.sleep(1)
        timeout -= 1

    server.shutdown()

    if captured_code is None:
        print("\nTimeout: No authorization received in 60 seconds.")
        print("Please run the script again and complete authorization faster.")
        sys.exit(1)

    if captured_state != state:
        print("\nSecurity error: State mismatch. Possible CSRF attack.")
        sys.exit(1)

    print("\nAuthorization code received. Exchanging for access token...")

    try:
        token_data = exchange_code_for_token(client_id, client_secret, captured_code)
    except Exception as e:
        print(f"\nError exchanging code for token: {e}")
        print("Check that your Client ID, Secret, and Redirect URI are correct.")
        sys.exit(1)

    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 5184000)

    if not access_token:
        print(f"\nError: No access_token in response: {token_data}")
        sys.exit(1)

    print(f"\nSuccess! Access token received.")
    print(f"Expires in: {expires_in // 86400} days")
    print(f"\nToken (first 20 chars): {access_token[:20]}...")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    save_token_to_env(access_token, env_path)
    print(f"\nSaved LINKEDIN_ACCESS_TOKEN to {env_path}")

    print("\n" + "=" * 60)
    print("  Add these to your .env file if not already there:")
    print("=" * 60)
    print(f"  LINKEDIN_CLIENT_ID={client_id}")
    print(f"  LINKEDIN_CLIENT_SECRET={client_secret}")
    print(f"  LINKEDIN_ACCESS_TOKEN={access_token}")
    print("=" * 60)
    print("\nDone! LinkedIn posting is now active.")
    print("Run: python social_agent/run_all.py --status")


if __name__ == "__main__":
    main()
