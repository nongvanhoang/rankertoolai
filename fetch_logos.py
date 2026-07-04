#!/usr/bin/env python3
"""
Patch Python socket DNS -> nslookup via 8.8.8.8, then download all brand logos.
Run once: python fetch_logos.py
"""

import sys, socket, subprocess, re, time
from pathlib import Path
from io import BytesIO

sys.stdout.reconfigure(encoding="utf-8")

# ── DNS patch via nslookup 8.8.8.8 ───────────────────────────────────────────
_original_getaddrinfo = socket.getaddrinfo
_dns_cache = {}

def _resolve_via_google(host):
    if host in _dns_cache:
        return _dns_cache[host]
    try:
        result = subprocess.run(
            ["nslookup", host, "8.8.8.8"],
            capture_output=True, text=True, timeout=8
        )
        # Parse IPs from output, skip 8.8.8.8 itself
        ips = re.findall(r"Addresses?:\s+([\d.]+)", result.stdout)
        if not ips:
            ips = re.findall(r"Address:\s+([\d.]+)", result.stdout)
        ips = [ip for ip in ips if ip != "8.8.8.8"]
        if ips:
            _dns_cache[host] = ips[0]
            return ips[0]
    except Exception as e:
        print(f"  nslookup failed for {host}: {e}")
    return None

def _patched_getaddrinfo(host, port, *args, **kwargs):
    try:
        return _original_getaddrinfo(host, port, *args, **kwargs)
    except socket.gaierror:
        ip = _resolve_via_google(host)
        if ip:
            return _original_getaddrinfo(ip, port, *args, **kwargs)
        raise

socket.getaddrinfo = _patched_getaddrinfo
print("DNS patch applied (using 8.8.8.8 as fallback)")

# ── Now import requests (after patch) ────────────────────────────────────────
import requests
from PIL import Image

LOGO_DIR = Path(__file__).parent / "html" / "assets" / "logos"
LOGO_DIR.mkdir(parents=True, exist_ok=True)

TOOLS = [
    ("chatgpt",          "openai.com"),
    ("claude",           "anthropic.com"),
    ("gemini",           "google.com"),
    ("grok",             "x.ai"),
    ("deepseek",         "deepseek.com"),
    ("perplexity",       "perplexity.ai"),
    ("midjourney",       "midjourney.com"),
    ("stable-diffusion", "stability.ai"),
    ("runway",           "runwayml.com"),
    ("canva-ai",         "canva.com"),
    ("cursor",           "cursor.com"),
    ("windsurf",         "windsurf.com"),
    ("github-copilot",   "github.com"),
    ("elevenlabs",       "elevenlabs.io"),
    ("jasper",           "jasper.ai"),
    ("writesonic",       "writesonic.com"),
    ("notion",           "notion.so"),
    ("otter-ai",         "otter.ai"),
    ("semrush",          "semrush.com"),
    ("hubspot",          "hubspot.com"),
    ("surfer-seo",       "surferseo.com"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/png,image/*,*/*",
}

def try_fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if r.status_code == 200 and len(r.content) > 300:
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img
    except Exception as e:
        pass
    return None

def download_logo(slug, domain):
    out = LOGO_DIR / f"{slug}.png"
    if out.exists():
        print(f"  skip  {slug} (cached)")
        return True

    sources = [
        f"https://logo.clearbit.com/{domain}?size=256",
        f"https://logo.clearbit.com/{domain}?size=128",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
        f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=256",
    ]

    for url in sources:
        img = try_fetch(url)
        if img:
            img.save(out, "PNG")
            w, h = img.size
            print(f"  OK    {slug} ({domain}) [{w}x{h}]")
            return True
        time.sleep(0.3)

    print(f"  FAIL  {slug} ({domain})")
    return False

# ── Disable SSL warnings ──────────────────────────────────────────────────────
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(f"\nDownloading {len(TOOLS)} logos to: {LOGO_DIR}\n")
ok = 0
for slug, domain in TOOLS:
    if download_logo(slug, domain):
        ok += 1
    time.sleep(0.5)

print(f"\nDone: {ok}/{len(TOOLS)} logos saved")
if ok > 0:
    print("Now run: python generate_og_images.py")
