import urllib.request
import os

out = r"c:\Users\Admin\RankerToolAI\html\assets\images\logos"

logos = {
    "jasper":     "https://www.jasper.ai/apple-touch-icon.png",
    "writesonic": "https://writesonic.com/apple-touch-icon.png",
    "surfer-seo": "https://surferseo.com/apple-touch-icon.png",
    "elevenlabs": "https://elevenlabs.io/apple-touch-icon.png",
    "copy-ai":    "https://www.copy.ai/apple-touch-icon.png",
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for name, url in logos.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        path = os.path.join(out, f"{name}.png")
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK  {name}: {len(data)//1024}KB")
    except Exception as e:
        print(f"ERR {name}: {e}")
