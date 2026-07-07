"""
Pinterest OAuth 2.0 Token Helper
==================================
Chạy script này để lấy Pinterest access token.

Usage:
  python social_agent/get_pinterest_token.py

Steps:
  1. Tạo Pinterest App tại https://developers.pinterest.com/apps/
  2. Điền App ID và App Secret
  3. Script mở trình duyệt để xác thực
  4. Token được lưu tự động vào .env

Required .env keys:
  PINTEREST_APP_ID=...
  PINTEREST_APP_SECRET=...
  PINTEREST_ACCESS_TOKEN=...  (output của script này)
  PINTEREST_BOARD_ID=...       (optional: default board để pin vào)
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
import urllib.request
import base64

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

REDIRECT_URI = "http://localhost:8788/callback"
SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

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
            <h2 style="color:#e60023">Authorization successful!</h2>
            <p>Pinterest token received. You can close this tab.</p>
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
            <p>Error: {error}: {desc}</p>
            </body></html>
            """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def exchange_code_for_token(app_id, app_secret, code):
    credentials = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(
        "https://api.pinterest.com/v5/oauth/token",
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}",
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_boards(access_token):
    req = urllib.request.Request(
        "https://api.pinterest.com/v5/boards?page_size=10",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except Exception:
        return []


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
    print("  Pinterest OAuth Token Helper — RankerToolAI")
    print("=" * 60)

    app_id = os.getenv("PINTEREST_APP_ID", "").strip()
    app_secret = os.getenv("PINTEREST_APP_SECRET", "").strip()

    if not app_id or not app_secret:
        print("\nStep 1: Create a Pinterest Developer App")
        print("  URL: https://developers.pinterest.com/apps/")
        print("\nIn the app settings:")
        print("  - Add Redirect URI: http://localhost:8788/callback")
        print("  - Request scopes: boards:read, boards:write, pins:read, pins:write")
        print()
        app_id = input("Enter your Pinterest App ID: ").strip()
        app_secret = input("Enter your Pinterest App Secret: ").strip()

        if not app_id or not app_secret:
            print("\nError: App ID and Secret are required.")
            sys.exit(1)

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://www.pinterest.com/oauth/?"
        + urllib.parse.urlencode({
            "client_id": app_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPES,
            "state": state,
        })
    )

    print(f"\nStarting local callback server on port 8788...")
    server = http.server.HTTPServer(("localhost", 8788), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f"Opening Pinterest authorization in browser...")
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
        token_data = exchange_code_for_token(app_id, app_secret, captured_code)
    except Exception as e:
        print(f"\nError: {e}")
        print("Check App ID, Secret, and Redirect URI match your Pinterest app settings.")
        sys.exit(1)

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", 2592000)

    if not access_token:
        print(f"\nError: No access_token in response: {token_data}")
        sys.exit(1)

    print(f"\nSuccess! Token received. Expires in {expires_in // 86400} days.")

    # Fetch boards to help user get board ID
    print("\nFetching your Pinterest boards...")
    boards = get_boards(access_token)
    selected_board_id = ""
    if boards:
        print(f"\nFound {len(boards)} board(s):")
        for i, board in enumerate(boards):
            print(f"  [{i+1}] {board.get('name', 'Unnamed')} — ID: {board['id']}")

        print("\nWhich board should posts go to? (Enter number or press Enter to skip)")
        choice = input("Board number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(boards):
            selected_board_id = boards[int(choice) - 1]["id"]
            print(f"Selected: {boards[int(choice)-1]['name']} ({selected_board_id})")
    else:
        print("Could not fetch boards. You can add PINTEREST_BOARD_ID to .env manually.")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    updates = {
        "PINTEREST_APP_ID": app_id,
        "PINTEREST_APP_SECRET": app_secret,
        "PINTEREST_ACCESS_TOKEN": access_token,
    }
    if refresh_token:
        updates["PINTEREST_REFRESH_TOKEN"] = refresh_token
    if selected_board_id:
        updates["PINTEREST_BOARD_ID"] = selected_board_id

    save_to_env(updates, env_path)
    print(f"\nAll tokens saved to {env_path}")

    print("\n" + "=" * 60)
    print("  .env entries added:")
    print("=" * 60)
    for key, value in updates.items():
        display = value[:20] + "..." if len(value) > 20 else value
        print(f"  {key}={display}")
    print("=" * 60)
    print("\nDone! Pinterest posting is now active.")
    print("Run: python social_agent/run_all.py --status")

    if refresh_token:
        print("\nNote: Pinterest tokens expire. To refresh:")
        print("  python social_agent/get_pinterest_token.py")


if __name__ == "__main__":
    main()
