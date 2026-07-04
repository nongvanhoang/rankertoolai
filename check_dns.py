import os, requests
CF_TOKEN = os.environ["CF_API_TOKEN"]
ZONE_ID  = "ae5011d58da0b374427226ea91f85ff6"
H = {"Authorization": f"Bearer {CF_TOKEN}"}
r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?per_page=100", headers=H)
for rec in r.json()["result"]:
    if "_dmarc" in rec["name"] or "_bimi" in rec["name"]:
        print(rec["name"], "=>", rec["content"])
