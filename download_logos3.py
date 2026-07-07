import urllib.request, os, re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

out = r"c:\Users\Admin\RankerToolAI\html\assets\images\logos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

class IconFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icons = []
    def handle_starttag(self, tag, attrs):
        if tag == "link":
            d = dict(attrs)
            rel = d.get("rel", "")
            href = d.get("href", "")
            if href and any(k in rel for k in ["icon", "apple-touch"]):
                self.icons.append((rel, href))

def fetch_best_icon(site, name):
    try:
        req = urllib.request.Request(site, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  fetch {site}: {e}"); return False

    parser = IconFinder()
    parser.feed(html)
    print(f"  Found icons for {name}: {parser.icons}")

    # prefer apple-touch or large icons
    best = None
    for rel, href in parser.icons:
        url = urljoin(site, href)
        if "apple-touch" in rel or "192" in href or "180" in href:
            best = url; break
    if not best and parser.icons:
        best = urljoin(site, parser.icons[0][1])

    if not best:
        # fallback to /favicon.ico
        best = urljoin(site, "/favicon.ico")

    print(f"  Downloading: {best}")
    try:
        req = urllib.request.Request(best, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        if len(data) < 100:
            print(f"  Too small"); return False
        ext = ".png" if "png" in best else ".ico"
        path = os.path.join(out, name + ".png")
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK  {name} ({len(data)//1024}KB)")
        return True
    except Exception as e:
        print(f"  download error: {e}"); return False

fetch_best_icon("https://www.jasper.ai", "jasper")
fetch_best_icon("https://writesonic.com", "writesonic")
fetch_best_icon("https://surferseo.com", "surfer-seo")
fetch_best_icon("https://www.copy.ai", "copy-ai")
