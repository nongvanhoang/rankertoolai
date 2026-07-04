"""
RankerToolAI — Media Fetcher
Tải ảnh và video miễn phí từ Pexels, Pixabay, Unsplash theo từng AI tool.

Usage:
  python media_fetcher.py --tool elevenlabs              # Tải cho 1 tool
  python media_fetcher.py --tool elevenlabs --type video # Chỉ video
  python media_fetcher.py --tool elevenlabs --type image # Chỉ ảnh
  python media_fetcher.py --all                          # Tải cho tất cả tool
  python media_fetcher.py --query "ai voice technology"  # Tìm theo từ khóa tùy chỉnh
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOOLS_FILE = Path(__file__).parent / "data" / "tools.json"
MEDIA_DIR = Path(__file__).parent / "assets" / "media"

# Số lượng mặc định tải về
DEFAULT_IMAGES = 10
DEFAULT_VIDEOS = 5


# ─── Keyword builder ──────────────────────────────────────────────────────────

def build_keywords(tool: dict) -> list[str]:
    """Keyword riêng cho từng tool — visual, cụ thể, sát nội dung thực tế."""
    slug = tool.get("slug", "")

    # Mỗi tool có keyword riêng, ưu tiên hình ảnh/video có thể dùng làm b-roll YouTube
    keyword_map = {
        # Podcast mic, recording booth, headphones, waveform, audio studio
        "elevenlabs": [
            "podcast microphone closeup studio",
            "sound wave audio visualization",
            "voice recording headphones",
            "audio recording studio professional",
            "radio broadcaster microphone",
        ],

        # Blogger writing, Google search, content planning, keyword chart
        "surfer-seo": [
            "blogger writing laptop coffee",
            "google search results laptop screen",
            "seo keyword research chart",
            "content writer home office desk",
            "website ranking growth graph",
        ],

        # Marketing team, copywriting, brand strategy, email campaign
        "jasper": [
            "marketing team brainstorming office",
            "copywriter laptop coffee shop",
            "brand strategy whiteboard",
            "email marketing campaign laptop",
            "content marketing plan notebook",
        ],

        # Competitor research, enterprise analytics, agency team, data dashboard
        "semrush": [
            "digital marketing agency team",
            "competitor analysis business data",
            "marketing analytics dashboard screen",
            "business growth meeting presentation",
            "market research report laptop",
        ],

        # Freelancer, home office, affordable tools, remote work writing
        "writesonic": [
            "freelancer home office laptop",
            "remote work writing coffee",
            "blog post writing desk",
            "solopreneur workspace morning",
            "content creator typing laptop",
        ],

        # Digital art, GPU render, colorful generative art, illustration
        "stable-diffusion": [
            "digital art illustration colorful",
            "generative art abstract colorful",
            "ai artwork surreal fantasy",
            "graphic design colorful creative",
            "digital painting vibrant colors",
        ],

        # Social media design, colorful templates, brand graphics, non-designer
        "canva-ai": [
            "social media graphic design colorful",
            "brand design laptop colorful",
            "instagram post design creative",
            "graphic designer workspace colorful",
            "marketing materials design template",
        ],

        # Smartphone news feed, X/Twitter, real-time social media, trending
        "grok": [
            "smartphone social media news feed",
            "mobile phone scrolling news",
            "breaking news smartphone screen",
            "social media trending topics phone",
            "real-time data news screen",
        ],

        # Film camera, video production, cinematic, director, clapperboard
        "runway": [
            "film camera cinematic production",
            "video director clapperboard set",
            "cinematography camera lens",
            "film production studio lighting",
            "video shooting professional camera",
        ],

        # Dark code editor, dual monitor, developer night, terminal screen
        "cursor": [
            "programmer dual monitor dark office",
            "code editor dark theme screen",
            "software developer night workspace",
            "developer home office multiple screens",
            "terminal command line dark",
        ],
    }

    keywords = keyword_map.get(slug)
    if keywords:
        return keywords

    # Fallback generic
    name = tool.get("name", "technology")
    return [
        "technology laptop workspace",
        "software productivity tool",
        "digital workspace modern",
        "tech startup office",
        "artificial intelligence screen",
    ]


# ─── Pexels ───────────────────────────────────────────────────────────────────

class PexelsClient:
    BASE = "https://api.pexels.com"

    def __init__(self, api_key: str):
        self.headers = {"Authorization": api_key}

    def search_images(self, query: str, count: int = 10) -> list[dict]:
        url = f"{self.BASE}/v1/search"
        params = {"query": query, "per_page": min(count, 80), "orientation": "landscape"}
        r = requests.get(url, headers=self.headers, params=params, timeout=15)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        return [
            {
                "id": p["id"],
                "url": p["src"]["large2x"],
                "thumb": p["src"]["medium"],
                "credit": f"Photo by {p['photographer']} on Pexels",
                "source": "pexels",
            }
            for p in photos
        ]

    def search_videos(self, query: str, count: int = 5) -> list[dict]:
        url = f"{self.BASE}/videos/search"
        params = {"query": query, "per_page": min(count, 80), "orientation": "landscape"}
        r = requests.get(url, headers=self.headers, params=params, timeout=15)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        results = []
        for v in videos:
            # Lấy file HD nếu có, fallback SD
            files = sorted(v.get("video_files", []), key=lambda f: f.get("width", 0), reverse=True)
            hd = next((f for f in files if f.get("quality") in ("hd", "sd")), None)
            if hd:
                results.append({
                    "id": v["id"],
                    "url": hd["link"],
                    "duration": v.get("duration", 0),
                    "width": hd.get("width"),
                    "height": hd.get("height"),
                    "credit": f"Video by {v['user']['name']} on Pexels",
                    "source": "pexels",
                })
        return results


# ─── Pixabay ──────────────────────────────────────────────────────────────────

class PixabayClient:
    BASE = "https://pixabay.com/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_images(self, query: str, count: int = 10) -> list[dict]:
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": min(count, 200),
            "image_type": "photo",
            "orientation": "horizontal",
            "safesearch": "true",
            "min_width": 1280,
        }
        r = requests.get(f"{self.BASE}/", params=params, timeout=15)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        return [
            {
                "id": h["id"],
                "url": h.get("largeImageURL", h["webformatURL"]),
                "thumb": h["previewURL"],
                "credit": f"Image by {h['user']} on Pixabay",
                "source": "pixabay",
            }
            for h in hits
        ]

    def search_videos(self, query: str, count: int = 5) -> list[dict]:
        params = {
            "key": self.api_key,
            "q": query,
            "per_page": max(3, min(count, 200)),  # Pixabay minimum per_page = 3
            "video_type": "film",
        }
        r = requests.get(f"{self.BASE}/videos/", params=params, timeout=15)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        results = []
        for h in hits:
            videos = h.get("videos", {})
            # Ưu tiên large > medium > small
            for quality in ("large", "medium", "small"):
                v = videos.get(quality)
                if v and v.get("url"):
                    results.append({
                        "id": h["id"],
                        "url": v["url"],
                        "duration": h.get("duration", 0),
                        "width": v.get("width"),
                        "height": v.get("height"),
                        "credit": f"Video by {h['user']} on Pixabay",
                        "source": "pixabay",
                    })
                    break
        return results


# ─── Unsplash ─────────────────────────────────────────────────────────────────

class UnsplashClient:
    BASE = "https://api.unsplash.com"

    def __init__(self, access_key: str):
        self.headers = {"Authorization": f"Client-ID {access_key}"}

    def search_images(self, query: str, count: int = 10) -> list[dict]:
        params = {
            "query": query,
            "per_page": min(count, 30),
            "orientation": "landscape",
        }
        r = requests.get(f"{self.BASE}/search/photos", headers=self.headers, params=params, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
        return [
            {
                "id": p["id"],
                "url": p["urls"]["full"],
                "thumb": p["urls"]["small"],
                "credit": f"Photo by {p['user']['name']} on Unsplash",
                "source": "unsplash",
            }
            for p in results
        ]

    def search_videos(self, query: str, count: int = 5) -> list[dict]:
        # Unsplash không hỗ trợ video
        return []


# ─── Downloader ───────────────────────────────────────────────────────────────

def download_file(url: str, dest: Path, source: str = "") -> bool:
    """Download file với retry 3 lần."""
    for attempt in range(3):
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt == 2:
                print(f"    [FAIL] {dest.name}: {e}")
            time.sleep(1)
    return False


def save_credits(credits: list[str], dest_dir: Path):
    """Lưu credit attribution vào credits.txt."""
    credits_file = dest_dir / "credits.txt"
    with open(credits_file, "w", encoding="utf-8") as f:
        f.write("Media Credits — RankerToolAI\n")
        f.write("=" * 40 + "\n\n")
        for c in credits:
            f.write(f"- {c}\n")


# ─── Main fetch logic ─────────────────────────────────────────────────────────

def get_clients() -> dict:
    """Khởi tạo các API client có API key."""
    clients = {}

    pexels_key = os.getenv("PEXELS_API_KEY")
    if pexels_key:
        clients["pexels"] = PexelsClient(pexels_key)
        print("  [OK] Pexels connected")
    else:
        print("  [--] Pexels: PEXELS_API_KEY not set")

    pixabay_key = os.getenv("PIXABAY_API_KEY")
    if pixabay_key:
        clients["pixabay"] = PixabayClient(pixabay_key)
        print("  [OK] Pixabay connected")
    else:
        print("  [--] Pixabay: PIXABAY_API_KEY not set")

    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if unsplash_key:
        clients["unsplash"] = UnsplashClient(unsplash_key)
        print("  [OK] Unsplash connected")
    else:
        print("  [--] Unsplash: UNSPLASH_ACCESS_KEY not set")

    return clients


def fetch_media_for_tool(tool: dict, clients: dict, media_type: str = "both",
                          n_images: int = DEFAULT_IMAGES, n_videos: int = DEFAULT_VIDEOS,
                          custom_query: str = None, force: bool = False):
    slug = tool["slug"]
    keywords = [custom_query] if custom_query else build_keywords(tool)

    out_img = MEDIA_DIR / slug / "images"
    out_vid = MEDIA_DIR / slug / "videos"
    out_img.mkdir(parents=True, exist_ok=True)
    out_vid.mkdir(parents=True, exist_ok=True)

    all_images, all_videos = [], []
    credits = []

    for keyword in keywords:
        if len(all_images) >= n_images and len(all_videos) >= n_videos:
            break

        print(f"\n  Searching: \"{keyword}\"")

        # ── Images ──
        if media_type in ("image", "both") and len(all_images) < n_images:
            need = n_images - len(all_images)

            for source in ("pexels", "pixabay", "unsplash"):
                if source not in clients or not need:
                    continue
                try:
                    results = clients[source].search_images(keyword, count=need)
                    all_images.extend(results)
                    need -= len(results)
                    print(f"    {source}: {len(results)} images found")
                except Exception as e:
                    print(f"    {source} image error: {e}")

        # ── Videos ──
        if media_type in ("video", "both") and len(all_videos) < n_videos:
            need = n_videos - len(all_videos)

            for source in ("pexels", "pixabay"):
                if source not in clients or not need:
                    continue
                try:
                    results = clients[source].search_videos(keyword, count=need)
                    all_videos.extend(results)
                    need -= len(results)
                    print(f"    {source}: {len(results)} videos found")
                except Exception as e:
                    print(f"    {source} video error: {e}")

    # ── Download images ──
    downloaded_img = 0
    if media_type in ("image", "both"):
        print(f"\n  Downloading {min(len(all_images), n_images)} images...")
        for i, item in enumerate(all_images[:n_images]):
            ext = "jpg"
            fname = f"{slug}_{item['source']}_{item['id']}.{ext}"
            dest = out_img / fname
            if dest.exists() and not force:
                print(f"    [{i+1}] Skip (exists): {fname}")
                downloaded_img += 1
                continue
            ok = download_file(item["url"], dest, item["source"])
            if ok:
                downloaded_img += 1
                credits.append(item["credit"])
                print(f"    [{i+1}] OK: {fname}")

    # ── Download videos ──
    downloaded_vid = 0
    if media_type in ("video", "both"):
        print(f"\n  Downloading {min(len(all_videos), n_videos)} videos...")
        for i, item in enumerate(all_videos[:n_videos]):
            ext = "mp4"
            fname = f"{slug}_{item['source']}_{item['id']}.{ext}"
            dest = out_vid / fname
            if dest.exists() and not force:
                print(f"    [{i+1}] Skip (exists): {fname}")
                downloaded_vid += 1
                continue
            print(f"    [{i+1}] Downloading {fname} ({item.get('width')}x{item.get('height')}, {item.get('duration')}s)...")
            ok = download_file(item["url"], dest)
            if ok:
                downloaded_vid += 1
                credits.append(item["credit"])

    # Lưu credits
    if credits:
        all_dir = MEDIA_DIR / slug
        existing_credits = []
        credits_file = all_dir / "credits.txt"
        if credits_file.exists():
            existing_credits = [l.strip().lstrip("- ") for l in credits_file.read_text(encoding="utf-8").splitlines() if l.startswith("-")]
        save_credits(list(set(existing_credits + credits)), all_dir)

    print(f"\n  [DONE] {slug}: {downloaded_img} images, {downloaded_vid} videos")
    print(f"  Saved to: {MEDIA_DIR / slug}")
    return downloaded_img, downloaded_vid


# ─── CLI ─────────────────────────────────────────────────────────────────────

def load_tools() -> list[dict]:
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="RankerToolAI Media Fetcher")
    parser.add_argument("--tool", help="Tool slug (vd: elevenlabs, cursor)")
    parser.add_argument("--all", action="store_true", help="Tải cho tất cả tool")
    parser.add_argument("--type", choices=["image", "video", "both"], default="both", help="Loại media")
    parser.add_argument("--images", type=int, default=DEFAULT_IMAGES, help=f"Số ảnh (default: {DEFAULT_IMAGES})")
    parser.add_argument("--videos", type=int, default=DEFAULT_VIDEOS, help=f"Số video (default: {DEFAULT_VIDEOS})")
    parser.add_argument("--query", help="Tu khoa tim kiem tuy chinh")
    parser.add_argument("--force", action="store_true", help="Tai lai, ghi de file cu")
    args = parser.parse_args()

    print("\n[MEDIA FETCHER] RankerToolAI")
    print("=" * 45)
    print("Checking API connections...")
    clients = get_clients()

    if not clients:
        print("\n[ERROR] Không có API key nào được cấu hình.")
        print("Thêm vào file .env:")
        print("  PEXELS_API_KEY=your_key_here")
        print("  PIXABAY_API_KEY=your_key_here")
        print("  UNSPLASH_ACCESS_KEY=your_key_here")
        sys.exit(1)

    tools = load_tools()

    if args.all:
        target_tools = tools
    elif args.tool:
        target_tools = [t for t in tools if t["slug"] == args.tool]
        if not target_tools:
            print(f"[ERROR] Không tìm thấy tool: {args.tool}")
            print("Available:", ", ".join(t["slug"] for t in tools))
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)

    total_img = total_vid = 0
    for i, tool in enumerate(target_tools):
        print(f"\n{'='*45}")
        print(f"[{i+1}/{len(target_tools)}] {tool['name']} ({tool['category']})")
        print(f"{'='*45}")
        imgs, vids = fetch_media_for_tool(
            tool, clients,
            media_type=args.type,
            n_images=args.images,
            n_videos=args.videos,
            custom_query=args.query,
            force=args.force,
        )
        total_img += imgs
        total_vid += vids
        if i < len(target_tools) - 1:
            time.sleep(2)  # tránh rate limit

    print(f"\n{'='*45}")
    print(f"[SUMMARY] Total: {total_img} images, {total_vid} videos")
    print(f"Saved to: {MEDIA_DIR}")


if __name__ == "__main__":
    main()
