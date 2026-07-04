"""Fix Cloudflare robots.txt via Worker to allow AI crawlers."""
import os, requests, json, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

CF_TOKEN = os.environ["CF_API_TOKEN"]
DOMAIN   = "rankertoolai.com"
BASE     = "https://api.cloudflare.com/client/v4"
H        = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}

ROBOTS_CONTENT = """User-agent: *
Allow: /
Disallow: /go/
Disallow: /pages/
Disallow: /link-building-guide.html
Disallow: /deploy-checklist.html
Disallow: /500.html

User-agent: Amazonbot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

Sitemap: https://rankertoolai.com/sitemap.xml
IndexNow-Key: bcbb9e83c3f84cd098e9a71dcf38b086
IndexNow-Key-Location: https://rankertoolai.com/bcbb9e83c3f84cd098e9a71dcf38b086.txt"""

# Service Worker syntax (no metadata needed)
WORKER_SCRIPT = """addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  if (url.pathname === '/robots.txt') {
    return new Response(ROBOTS, {
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    })
  }
  return fetch(request)
}

const ROBOTS = `""" + ROBOTS_CONTENT + "`\n"

ZONE_ID_HARDCODED    = "ae5011d58da0b374427226ea91f85ff6"
ACCOUNT_ID_HARDCODED = "e8be9a830f6ad3f3741ea90966f972de"

def verify_token():
    r = requests.get(f"{BASE}/user/tokens/verify", headers=H)
    if r.status_code == 200:
        print(f"Token OK: {r.json()['result']['status']}")
        return True
    print(f"Token ERROR: {r.status_code} {r.text[:100]}")
    return False

def get_zone_id():
    print(f"Zone ID: {ZONE_ID_HARDCODED}")
    return ZONE_ID_HARDCODED

def get_account_id():
    print(f"Account ID: {ACCOUNT_ID_HARDCODED}")
    return ACCOUNT_ID_HARDCODED

def create_worker(account_id, zone_id):
    worker_name = "rankertoolai-robots"

    # Upload Worker script (Service Worker format — no metadata part needed)
    r = requests.put(
        f"{BASE}/accounts/{account_id}/workers/scripts/{worker_name}",
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/javascript"},
        data=WORKER_SCRIPT.encode("utf-8")
    )
    if r.status_code in [200, 201]:
        print(f"Worker uploaded: {worker_name}")
    else:
        print(f"Worker upload failed: {r.status_code} {r.text[:300]}")
        return False

    # Add route: rankertoolai.com/robots.txt
    r2 = requests.post(
        f"{BASE}/zones/{zone_id}/workers/routes",
        headers=H,
        json={"pattern": f"{DOMAIN}/robots.txt", "script": worker_name}
    )
    if r2.status_code in [200, 201]:
        route_id = r2.json().get("result", {}).get("id")
        print(f"Route added: {DOMAIN}/robots.txt -> {worker_name} (id: {route_id})")
        return True
    else:
        if "already exists" in r2.text or r2.status_code == 409:
            print("Route already exists, updating...")
            r3 = requests.get(f"{BASE}/zones/{zone_id}/workers/routes", headers=H)
            routes = r3.json().get("result", [])
            for route in routes:
                if "robots.txt" in route.get("pattern", ""):
                    rid = route["id"]
                    r4 = requests.put(
                        f"{BASE}/zones/{zone_id}/workers/routes/{rid}",
                        headers=H,
                        json={"pattern": f"{DOMAIN}/robots.txt", "script": worker_name}
                    )
                    print(f"Route updated: {r4.status_code}")
                    return r4.status_code in [200, 201]
        print(f"Route failed: {r2.status_code} {r2.text[:300]}")
        return False

def verify_fix():
    import time
    time.sleep(5)
    r = requests.get(f"https://{DOMAIN}/robots.txt", timeout=10)
    content = r.text
    blocked = [b for b in ["GPTBot", "ClaudeBot", "Google-Extended"] if f"{b}\nDisallow: /" in content]
    print(f"\n=== VERIFICATION ===")
    print(f"Still blocked: {blocked if blocked else 'NONE - all AI crawlers allowed!'}")
    print(f"\nrobots.txt content:\n{content[:400]}")

def main():
    print("=== Cloudflare robots.txt Fix ===\n")

    if not verify_token():
        sys.exit(1)

    zone_id    = get_zone_id()
    account_id = get_account_id()

    print("\nDeploying Worker...")
    success = create_worker(account_id, zone_id)

    if success:
        print("\nVerifying fix...")
        verify_fix()
        print("\nDone! AI crawlers can now access rankertoolai.com")
    else:
        print("\nWorker deploy failed — check errors above")

if __name__ == "__main__":
    main()
