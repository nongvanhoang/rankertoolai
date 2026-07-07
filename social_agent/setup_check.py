import requests
import os
import sys
from dotenv import load_dotenv
load_dotenv()

print("=== RankerToolAI Social Agent Setup Check ===\n")

# Test Dev.to
devto_key = os.getenv("DEVTO_API_KEY", "")
if devto_key:
    r = requests.get("https://dev.to/api/users/me", headers={"api-key": devto_key})
    if r.status_code == 200:
        user = r.json()
        print(f"[Dev.to] OK - User: {user.get('username')} | ID: {user.get('id')}")
    else:
        print(f"[Dev.to] ERROR {r.status_code}: {r.text[:100]}")
else:
    print("[Dev.to] No API key set")

# Test Hashnode
hn_token = os.getenv("HASHNODE_ACCESS_TOKEN", "")
if hn_token:
    query = {"query": "{ me { id username publications(first:5) { edges { node { id title } } } } }"}
    # Try v2 API with different auth header
    for endpoint, auth_header in [
        ("https://gql.hashnode.com", {"Authorization": hn_token}),
        ("https://gql.hashnode.com", {"hashnode-token": hn_token}),
        ("https://api.hashnode.com", {"Authorization": hn_token}),
    ]:
        r = requests.post(endpoint, json=query,
                         headers={**auth_header, "Content-Type": "application/json",
                                  "Accept": "application/json", "User-Agent": "python-requests/2.31.0"})
        ct = r.headers.get("Content-Type", "")
        if "json" in ct:
            print(f"[Hashnode] {endpoint} -> {r.status_code}: {r.text[:200]}")
            break
        else:
            print(f"[Hashnode] {endpoint} ({list(auth_header.keys())[0]}) -> HTML response, trying next...")
else:
    print("[Hashnode] No token set")

# Test Anthropic
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
if anthropic_key and not anthropic_key.startswith("YOUR_"):
    print(f"[Anthropic] Key set: {anthropic_key[:15]}...")
else:
    print("[Anthropic] NO KEY - needed for content generation!")

print("\n=== Done ===")
