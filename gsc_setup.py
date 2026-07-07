#!/usr/bin/env python3
"""
GSC Setup Helper — kiểm tra trạng thái và hướng dẫn setup.
Chạy: python gsc_setup.py
"""
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent
SECRET_FILE = ROOT / "client_secret.json"
TOKEN_FILE  = ROOT / "gsc_token.json"

print("=" * 60)
print("  GSC Setup Checker — rankertoolai.com")
print("=" * 60)

# Bước 1: Kiểm tra thư viện
print("\n[1] Kiểm tra thư viện Google API...")
try:
    import google.oauth2
    import google_auth_oauthlib
    import googleapiclient
    print("  OK  google-auth, google-api-python-client đã cài")
    libs_ok = True
except ImportError as e:
    print(f"  FAIL  Thiếu thư viện: {e}")
    print("  Chạy: .venv\\Scripts\\pip3.exe install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    libs_ok = False

# Bước 2: Kiểm tra client_secret.json
print("\n[2] Kiểm tra client_secret.json...")
if SECRET_FILE.exists():
    import json
    try:
        data = json.loads(SECRET_FILE.read_text())
        kind = "installed" if "installed" in data else "web"
        client_id = data.get(kind, {}).get("client_id", "?")[:30]
        print(f"  OK  client_secret.json tìm thấy (client_id: {client_id}...)")
        secret_ok = True
    except Exception as e:
        print(f"  FAIL  client_secret.json lỗi: {e}")
        secret_ok = False
else:
    print("  FAIL  client_secret.json chưa có")
    print()
    print("  HƯỚNG DẪN LẤY client_secret.json:")
    print("  ─" * 30)
    print("  1. Mở: https://console.cloud.google.com/")
    print("  2. Tạo project mới (hoặc chọn project có sẵn)")
    print("  3. Menu trái → 'APIs & Services' → 'Library'")
    print("  4. Tìm 'Google Search Console API' → Enable")
    print("  5. Menu trái → 'APIs & Services' → 'Credentials'")
    print("  6. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'")
    print("  7. Application type: 'Desktop app'")
    print("  8. Name: 'RankerToolAI GSC'")
    print("  9. Click 'CREATE' → 'DOWNLOAD JSON'")
    print(" 10. Đổi tên file thành 'client_secret.json'")
    print(f" 11. Chép vào: {ROOT}")
    print()
    print("  Nếu thấy 'OAuth consent screen' cần setup:")
    print("  → User Type: External")
    print("  → App name: RankerToolAI")
    print("  → Add scopes: .../auth/webmasters.readonly")
    print("  → Add test user: nongvanhoang1608@gmail.com")
    secret_ok = False

# Bước 3: Kiểm tra token (đã auth chưa)
print("\n[3] Kiểm tra authentication token...")
if TOKEN_FILE.exists():
    print(f"  OK  gsc_token.json tìm thấy — đã auth rồi")
    token_ok = True
else:
    print("  WAIT  gsc_token.json chưa có — cần chạy auth")
    token_ok = False

# Bước 4: GSC property
print("\n[4] GSC Property cần verify...")
print("  Mở: https://search.google.com/search-console/")
print("  Property phải là: https://rankertoolai.com (URL-prefix type)")
print("  Nếu chưa verify: thêm meta tag hoặc dùng file HTML verify")

# Tóm tắt
print("\n" + "=" * 60)
print("  KẾT QUẢ:")
print("=" * 60)
print(f"  Thư viện Google API : {'OK' if libs_ok else 'CẦN CÀI'}")
print(f"  client_secret.json  : {'OK' if secret_ok else 'CẦN TẠO'}")
print(f"  gsc_token.json      : {'OK (đã auth)' if token_ok else 'CẦN AUTH'}")

if libs_ok and secret_ok and not token_ok:
    print()
    print("  => Chạy lệnh này để authenticate:")
    print("     python gsc_tracker.py --auth")
    print("     (sẽ mở browser, đăng nhập Google, xác nhận quyền)")
    print()
    print("  => Sau khi auth xong, chạy:")
    print("     python gsc_tracker.py")
elif libs_ok and secret_ok and token_ok:
    print()
    print("  => Setup hoàn tất! Chạy:")
    print("     python gsc_tracker.py")
    print("     python gsc_tracker.py --days 28 --top 30")
    print("     python gsc_tracker.py --not-indexed")
elif not secret_ok:
    print()
    print("  => Làm theo hướng dẫn ở bước [2] trước")
    print("     Sau khi có client_secret.json, chạy lại: python gsc_setup.py")

print()
