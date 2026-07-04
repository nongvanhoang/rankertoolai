"""Setup BIMI: update DMARC p=quarantine + add BIMI DNS record."""
import os, requests, sys, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env.cloudflare")

CF_TOKEN = os.environ["CF_API_TOKEN"]
ZONE_ID  = "ae5011d58da0b374427226ea91f85ff6"
DOMAIN   = "rankertoolai.com"
BASE     = "https://api.cloudflare.com/client/v4"
H        = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}

BIMI_NAME  = "default._bimi"
BIMI_VALUE = "v=BIMI1; l=https://rankertoolai.com/assets/images/bimi-logo.svg;"


def log(msg): print(f"  {msg}")


def list_dns_records():
    r = requests.get(f"{BASE}/zones/{ZONE_ID}/dns_records?per_page=100", headers=H)
    r.raise_for_status()
    return r.json()["result"]


def update_dmarc(records):
    dmarc = next((r for r in records if r["type"] == "TXT" and r["name"].startswith("_dmarc")), None)
    if not dmarc:
        log("ERROR: DMARC record not found")
        return False

    current = dmarc["content"]
    log(f"DMARC hiện tại: {current}")

    if "p=quarantine" in current or "p=reject" in current:
        log("DMARC đã đủ điều kiện (quarantine/reject). Bỏ qua.")
        return True

    # Replace p=none with p=quarantine
    new_content = current.replace("p=none", "p=quarantine")
    log(f"DMARC mới: {new_content}")

    r = requests.put(
        f"{BASE}/zones/{ZONE_ID}/dns_records/{dmarc['id']}",
        headers=H,
        json={
            "type": "TXT",
            "name": dmarc["name"],
            "content": new_content,
            "ttl": dmarc.get("ttl", 3600),
        }
    )
    if r.status_code in [200, 201]:
        log("DMARC updated: p=none → p=quarantine ✓")
        return True
    else:
        log(f"DMARC update failed: {r.status_code} {r.text[:200]}")
        return False


def add_bimi_record(records):
    existing = next((r for r in records if r["type"] == "TXT" and BIMI_NAME in r["name"]), None)

    if existing:
        log(f"BIMI record đã tồn tại: {existing['content']}")
        if existing["content"] == BIMI_VALUE:
            log("BIMI record đúng rồi. Bỏ qua.")
            return True
        # Update nếu sai
        r = requests.put(
            f"{BASE}/zones/{ZONE_ID}/dns_records/{existing['id']}",
            headers=H,
            json={"type": "TXT", "name": BIMI_NAME, "content": BIMI_VALUE, "ttl": 3600}
        )
        if r.status_code in [200, 201]:
            log("BIMI record updated ✓")
            return True
        else:
            log(f"BIMI update failed: {r.status_code} {r.text[:200]}")
            return False
    else:
        r = requests.post(
            f"{BASE}/zones/{ZONE_ID}/dns_records",
            headers=H,
            json={"type": "TXT", "name": BIMI_NAME, "content": BIMI_VALUE, "ttl": 3600}
        )
        if r.status_code in [200, 201]:
            log(f"BIMI record added: {BIMI_NAME} ✓")
            return True
        else:
            log(f"BIMI add failed: {r.status_code} {r.text[:200]}")
            return False


def verify_svg():
    url = f"https://{DOMAIN}/assets/images/bimi-logo.svg"
    log(f"Checking SVG at {url}...")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and "svg" in r.text.lower():
            log(f"SVG accessible ✓ ({len(r.text)} bytes)")
            return True
        else:
            log(f"SVG not accessible yet: HTTP {r.status_code}")
            return False
    except Exception as e:
        log(f"SVG check error: {e}")
        return False


def main():
    print("\n=== BIMI Setup ===\n")

    print("[1/3] Fetching DNS records...")
    records = list_dns_records()
    log(f"Found {len(records)} records")

    print("\n[2/3] Updating DMARC...")
    dmarc_ok = update_dmarc(records)

    print("\n[3/3] Adding BIMI DNS record...")
    bimi_ok = add_bimi_record(records)

    print("\n=== Checking SVG URL ===")
    svg_ok = verify_svg()

    print("\n=== Summary ===")
    print(f"  DMARC p=quarantine : {'✓' if dmarc_ok else '✗ FAILED'}")
    print(f"  BIMI DNS record    : {'✓' if bimi_ok else '✗ FAILED'}")
    print(f"  SVG accessible     : {'✓' if svg_ok else '✗ Not yet (deploy trước)'}")

    if dmarc_ok and bimi_ok:
        print("\n  DNS propagation mất 5-30 phút.")
        print("  Sau đó check tại: https://bimigroup.org/bimi-generator/")
    else:
        print("\n  Có lỗi, xem chi tiết ở trên.")


if __name__ == "__main__":
    main()
