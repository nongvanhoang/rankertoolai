import requests, os, json
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("HASHNODE_ACCESS_TOKEN")
query = """{ me { publications(first: 5) { edges { node { id title url } } } } }"""

headers = {
    "Authorization": token,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; RankerToolAI/1.0)",
}

# Try new possible endpoints
endpoints = [
    "https://hashnode.com/graphql",
    "https://api.hashnode.com/graphql",
    "https://gql.hashnode.com/graphql",
]

for url in endpoints:
    try:
        r = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        is_json = r.headers.get("Content-Type", "").startswith("application/json")
        print(f"\n[{url}]")
        print(f"  Status: {r.status_code} | JSON: {is_json}")
        if is_json:
            print(json.dumps(r.json(), indent=2)[:500])
        else:
            print(f"  Body: {r.text[:150]}")
    except Exception as e:
        print(f"\n[{url}] ERROR: {e}")
