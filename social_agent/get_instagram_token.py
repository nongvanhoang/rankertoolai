"""
Instagram (Meta Graph API) OAuth 2.0 Token Helper
====================================================
Chạy script này để lấy Instagram long-lived access token + Business Account ID.

Việc BẠN phải làm thủ công trước (cần tài khoản Facebook/Instagram thật của bạn,
script này không thể tự làm thay):
  1. Tạo Facebook Page (nếu chưa có): https://facebook.com/pages/create
  2. Liên kết Instagram Business/Creator account với Page đó:
     Instagram app → Settings → Account → Linked Accounts → Facebook
  3. Tạo Meta App: https://developers.facebook.com/apps/ → Create App → loại "Business"
  4. Trong app, thêm sản phẩm "Facebook Login" (hoặc "Facebook Login for Business")
  5. Trong Facebook Login settings, thêm Valid OAuth Redirect URI:
       http://localhost:8790/callback
  6. Lấy App ID + App Secret ở trang Settings → Basic của app
  7. (Nếu app đang ở chế độ Development) thêm tài khoản Facebook của bạn vào
     Roles → Administrators/Testers để có thể đăng nhập được

Sau khi có App ID + App Secret, chạy:
  python social_agent/get_instagram_token.py

Script sẽ:
  - Mở trình duyệt để bạn đăng nhập Facebook và cho phép quyền
  - Đổi code -> short-lived token -> long-lived token (60 ngày)
  - Liệt kê các Facebook Page bạn quản lý, tìm Instagram Business Account gắn với Page
  - Lưu INSTAGRAM_ACCESS_TOKEN + INSTAGRAM_BUSINESS_ID vào .env

Required .env keys (output):
  FB_APP_ID=...
  FB_APP_SECRET=...
  INSTAGRAM_ACCESS_TOKEN=...   (long-lived Page access token, ~60 ngày)
  INSTAGRAM_BUSINESS_ID=...    (Instagram Business Account numeric ID)

Lưu ý: quyền instagram_content_publish thường cần Meta App Review nếu app chưa
ở chế độ Live. Ở chế độ Development, chỉ tài khoản admin/tester của app mới
đăng được. Token hết hạn sau ~60 ngày — chạy lại script này để làm mới.
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

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

API_VERSION = "v19.0"
GRAPH_BASE = f"https://graph.facebook.com/{API_VERSION}"
REDIRECT_URI = "http://localhost:8790/callback"
SCOPES = "pages_show_list,pages_read_engagement,instagram_basic,instagram_content_publish,business_management"

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
            <h2 style="color:#E1306C">Authorization successful!</h2>
            <p>Instagram/Facebook token received. You can close this tab.</p>
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


def graph_get(path, params):
    url = f"{GRAPH_BASE}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def exchange_code_for_short_token(app_id, app_secret, code):
    return graph_get("oauth/access_token", {
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })


def exchange_for_long_lived_token(app_id, app_secret, short_token):
    return graph_get("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    })


def get_pages(user_access_token):
    data = graph_get("me/accounts", {"access_token": user_access_token})
    return data.get("data", [])


def get_ig_business_id(page_id, page_access_token):
    data = graph_get(page_id, {
        "fields": "instagram_business_account",
        "access_token": page_access_token,
    })
    ig = data.get("instagram_business_account")
    return ig.get("id") if ig else None


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
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("  Instagram (Meta Graph API) OAuth Token Helper — RankerToolAI")
    print("=" * 60)

    app_id = os.getenv("FB_APP_ID", "").strip()
    app_secret = os.getenv("FB_APP_SECRET", "").strip()

    if not app_id or not app_secret:
        print("\nStep 1: Tạo Meta App (loại Business)")
        print("  URL: https://developers.facebook.com/apps/")
        print("\nTrong app settings:")
        print("  - Thêm sản phẩm Facebook Login")
        print(f"  - Valid OAuth Redirect URI: {REDIRECT_URI}")
        print("  - Thêm tài khoản của bạn vào Roles nếu app đang Development mode")
        print()
        app_id = input("Nhập Meta App ID: ").strip()
        app_secret = input("Nhập Meta App Secret: ").strip()

        if not app_id or not app_secret:
            print("\nLỗi: cần cả App ID và App Secret.")
            sys.exit(1)

    state = secrets.token_urlsafe(16)
    auth_url = (
        f"https://www.facebook.com/{API_VERSION}/dialog/oauth?"
        + urllib.parse.urlencode({
            "client_id": app_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPES,
            "state": state,
        })
    )

    print(f"\nĐang mở local callback server ở port 8790...")
    server = http.server.HTTPServer(("localhost", 8790), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f"Mở trình duyệt để đăng nhập Facebook và cấp quyền...")
    print(f"\nNếu trình duyệt không tự mở, vào link sau:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    print("Đang chờ xác thực (timeout 90 giây)...")
    timeout = 90
    while captured_code is None and timeout > 0:
        time.sleep(1)
        timeout -= 1

    server.shutdown()

    if captured_code is None:
        print("\nTimeout: không nhận được xác thực.")
        sys.exit(1)

    if captured_state != state:
        print("\nLỗi bảo mật: state không khớp.")
        sys.exit(1)

    print("\nĐổi code lấy short-lived token...")
    try:
        short_data = exchange_code_for_short_token(app_id, app_secret, captured_code)
        short_token = short_data["access_token"]
    except Exception as e:
        print(f"\nLỗi: {e}")
        print("Kiểm tra lại App ID, App Secret, và Redirect URI có khớp cấu hình app không.")
        sys.exit(1)

    print("Đổi sang long-lived token (60 ngày)...")
    try:
        long_data = exchange_for_long_lived_token(app_id, app_secret, short_token)
        user_token = long_data["access_token"]
    except Exception as e:
        print(f"\nLỗi khi lấy long-lived token: {e}")
        sys.exit(1)

    print("\nĐang lấy danh sách Facebook Page bạn quản lý...")
    pages = get_pages(user_token)
    if not pages:
        print("\nKhông tìm thấy Page nào. Kiểm tra:")
        print("  - Bạn có phải admin của ít nhất 1 Facebook Page không")
        print("  - Đã cấp đủ quyền pages_show_list khi đăng nhập chưa")
        sys.exit(1)

    print(f"\nTìm thấy {len(pages)} Page:")
    for i, page in enumerate(pages):
        print(f"  [{i+1}] {page.get('name', 'Unnamed')} — ID: {page['id']}")

    if len(pages) == 1:
        selected = pages[0]
    else:
        choice = input("\nChọn Page đã liên kết với Instagram Business account (số): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(pages)):
            print("Lựa chọn không hợp lệ.")
            sys.exit(1)
        selected = pages[int(choice) - 1]

    page_id = selected["id"]
    page_token = selected["access_token"]  # long-lived vì user_token đã long-lived

    print(f"\nĐang tìm Instagram Business Account gắn với Page '{selected.get('name')}'...")
    ig_business_id = get_ig_business_id(page_id, page_token)

    if not ig_business_id:
        print("\nKhông tìm thấy Instagram Business Account gắn với Page này.")
        print("Kiểm tra lại: Instagram app → Settings → Account → Linked Accounts → Facebook")
        print(f"đã trỏ đúng vào Page '{selected.get('name')}' chưa.")
        sys.exit(1)

    print(f"Tìm thấy Instagram Business Account ID: {ig_business_id}")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    updates = {
        "FB_APP_ID": app_id,
        "FB_APP_SECRET": app_secret,
        "FB_PAGE_ID": page_id,
        "INSTAGRAM_ACCESS_TOKEN": page_token,
        "INSTAGRAM_BUSINESS_ID": ig_business_id,
    }
    save_to_env(updates, env_path)
    print(f"\nĐã lưu vào {env_path}")

    print("\n" + "=" * 60)
    print("  .env entries đã thêm:")
    print("=" * 60)
    for key, value in updates.items():
        display = value[:20] + "..." if len(value) > 20 else value
        print(f"  {key}={display}")
    print("=" * 60)
    print("\nXong! Chạy thử: python social_agent/post_instagram.py --tool elevenlabs")
    print("\nLưu ý: token hết hạn sau ~60 ngày. Chạy lại script này để làm mới.")


if __name__ == "__main__":
    main()
