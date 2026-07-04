import urllib.request, os, re

out = r"c:\Users\Admin\RankerToolAI\html\assets\images\logos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"}

def try_urls(name, urls):
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            if len(data) < 200:
                continue
            path = os.path.join(out, f"{name}.png")
            with open(path, "wb") as f:
                f.write(data)
            print(f"OK  {name} <- {url}  ({len(data)//1024}KB)")
            return True
        except Exception as e:
            print(f"    {url} -> {e}")
    print(f"FAIL {name}")
    return False

try_urls("jasper", [
    "https://www.jasper.ai/favicon-192x192.png",
    "https://www.jasper.ai/favicon-96x96.png",
    "https://www.jasper.ai/favicon-32x32.png",
    "https://assets.jasper.ai/public/favicon.png",
    "https://cdn.jasper.ai/images/favicon.png",
])

try_urls("writesonic", [
    "https://writesonic.com/favicon-192x192.png",
    "https://writesonic.com/favicon-96x96.png",
    "https://writesonic.com/favicon-32x32.png",
    "https://writesonic.com/static/favicon.png",
])

try_urls("surfer-seo", [
    "https://surferseo.com/favicon-192x192.png",
    "https://surferseo.com/favicon-96x96.png",
    "https://surferseo.com/favicon-32x32.png",
    "https://surferseo.com/wp-content/uploads/surfer-icon.png",
])

try_urls("copy-ai", [
    "https://www.copy.ai/favicon-192x192.png",
    "https://www.copy.ai/favicon-96x96.png",
    "https://www.copy.ai/favicon-32x32.png",
    "https://www.copy.ai/images/favicon.png",
])
