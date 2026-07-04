import os, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

TOKEN   = os.environ["CF_API_TOKEN"]
ZONE_ID = "ae5011d58da0b374427226ea91f85ff6"
BASE    = "https://api.cloudflare.com/client/v4"
H       = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}

endpoints = [
    "/zones/" + ZONE_ID + "/ai_scraper_settings",
    "/zones/" + ZONE_ID + "/settings/ai_scraper_policy",
    "/zones/" + ZONE_ID + "/bots/robot_txt",
    "/zones/" + ZONE_ID + "/managed_robots_txt",
    "/zones/" + ZONE_ID + "/workers/routes",
]
for ep in endpoints:
    r = requests.get(BASE + ep, headers=H, timeout=10)
    name = ep.split("/")[-1]
    print(str(r.status_code) + " " + name + ": " + r.text[:150])
    print()
