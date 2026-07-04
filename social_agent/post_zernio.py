#!/usr/bin/env python3
"""
RankerToolAI — Unified social poster via Zernio API

Zernio posts to 14+ platforms (Twitter, Instagram, LinkedIn, Facebook,
TikTok, YouTube, Pinterest, Reddit, Bluesky, Threads, Discord, Telegram,
Snapchat, WhatsApp, Google Business) from a single API call.

Usage:
  python social_agent/post_zernio.py --list-accounts
  python social_agent/post_zernio.py --tool chatgpt
  python social_agent/post_zernio.py --tool semrush --image html/assets/images/og-review-semrush.jpg
  python social_agent/post_zernio.py --tool cursor --platforms twitter linkedin
  python social_agent/post_zernio.py --all --limit 3
  python social_agent/post_zernio.py --content "Custom post text" --platforms twitter

Environment:
  ZERNIO_API_KEY   sk_... key from zernio.com/settings/api
"""

import os, sys, json, time, argparse, urllib.request, urllib.error, sqlite3
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# ── Config ──────────────────────────────────────────────────────────────────────
BASE_URL  = 'https://zernio.com/api/v1'
API_KEY   = os.getenv('ZERNIO_API_KEY', '')
DB_PATH   = Path(__file__).parent / 'data' / 'posts.db'
ROOT      = Path(__file__).resolve().parent.parent
TOOLS_FILE = Path(__file__).parent / 'data' / 'tools.json'

# Zernio platform slugs (must match their API names)
ZERNIO_PLATFORMS = [
    'twitter', 'instagram', 'linkedin', 'facebook',
    'tiktok', 'youtube', 'pinterest', 'reddit',
    'bluesky', 'threads', 'discord', 'telegram',
]


# ── HTTP helpers ────────────────────────────────────────────────────────────────
def _headers():
    return {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }


def _get(path):
    req = urllib.request.Request(f'{BASE_URL}{path}', headers=_headers(), method='GET')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f'{BASE_URL}{path}', data=data, headers=_headers(), method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _put(url, file_bytes, content_type='image/jpeg'):
    req = urllib.request.Request(
        url, data=file_bytes,
        headers={'Content-Type': content_type}, method='PUT'
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status


# ── Accounts ────────────────────────────────────────────────────────────────────
def get_default_profile_id():
    """Return the default profile _id, or None."""
    try:
        data = _get('/profiles')
        profiles = data.get('profiles', [])
        for p in profiles:
            if p.get('isDefault'):
                return p.get('_id')
        if profiles:
            return profiles[0].get('_id')
    except Exception:
        pass
    return None


def list_accounts():
    """Return list of connected accounts as [{platform, _id, ...}]."""
    try:
        data = _get('/accounts')
        accounts = data if isinstance(data, list) else data.get('accounts', data.get('data', []))
        return accounts
    except urllib.error.HTTPError as e:
        print(f'  Error fetching accounts: {e.code} {e.read()[:200]}')
        return []


def get_account_ids(target_platforms=None):
    """Return {platform: account_id} for connected accounts.
    Merges API results with any hardcoded ZERNIO_{PLATFORM}_ID env vars
    (needed because Facebook Pages don't appear in the /accounts endpoint).
    """
    accounts = list_accounts()
    result = {}
    for acc in accounts:
        pf  = acc.get('platform', '')
        aid = acc.get('_id') or acc.get('id') or acc.get('accountId', '')
        if pf and aid:
            if target_platforms is None or pf in target_platforms:
                result[pf] = aid

    # Merge hardcoded overrides from env (ZERNIO_FACEBOOK_ID, ZERNIO_INSTAGRAM_ID, etc.)
    import re
    for key, val in os.environ.items():
        m = re.match(r'^ZERNIO_([A-Z]+)_ID$', key)
        if m and val.strip():
            pf = m.group(1).lower()
            if target_platforms is None or pf in target_platforms:
                result.setdefault(pf, val.strip())   # API result takes priority

    return result


# ── Media upload ────────────────────────────────────────────────────────────────
def upload_image(image_path):
    """Upload local image to Zernio CDN. Returns publicUrl or None."""
    p = Path(image_path)
    if not p.exists():
        print(f'  Image not found: {image_path}')
        return None

    ext = p.suffix.lower().lstrip('.')
    content_type = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                    'png': 'image/png', 'webp': 'image/webp',
                    'gif': 'image/gif'}.get(ext, 'image/jpeg')

    try:
        presign = _post('/media/presign', {'filename': p.name, 'contentType': content_type})
        upload_url  = presign.get('uploadUrl')
        public_url  = presign.get('publicUrl')
        if not upload_url or not public_url:
            print(f'  Presign failed: {presign}')
            return None

        file_bytes = p.read_bytes()
        status = _put(upload_url, file_bytes, content_type)
        if status not in (200, 204):
            print(f'  Upload PUT returned {status}')
            return None

        print(f'  Image uploaded → {public_url[:70]}')
        return public_url

    except Exception as e:
        print(f'  Image upload error: {e}')
        return None


# ── Post creation ────────────────────────────────────────────────────────────────
def _post_single(content, platform, account_id, media_url=None,
                 title=None, schedule_minutes=0, profile_id=None):
    """Post to ONE platform/account using the simple Zernio API format."""
    body = {
        'content': content,
        'platform': platform,
        'account_id': account_id,
        'publish_now': schedule_minutes == 0,
    }
    if profile_id:
        body['profile_id'] = profile_id
    if media_url:
        body['media_urls'] = media_url          # comma-separated string per docs
    if title:
        body['title'] = title
    if schedule_minutes > 0:
        body['schedule_minutes'] = schedule_minutes
    return _post('/posts', body)


def create_post(content, account_map, media_url=None, title=None, schedule_minutes=0):
    """
    Post to each platform in account_map (one API call per platform).
    account_map: {platform_slug: account_id}
    Returns dict of {platform: result_or_None}.
    """
    profile_id = get_default_profile_id()
    results = {}
    for pf, aid in account_map.items():
        try:
            r = _post_single(content, pf, aid, media_url=media_url,
                             title=title, schedule_minutes=schedule_minutes,
                             profile_id=profile_id)
            results[pf] = r
        except urllib.error.HTTPError as e:
            err_body = e.read()[:300]
            print(f'  Post [{pf}] failed: {e.code} {err_body}')
            results[pf] = None
    return results


# ── DB logging ──────────────────────────────────────────────────────────────────
def log_post(tool_slug, platform, post_id='', url=''):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR IGNORE INTO posts (platform, tool_slug, post_id, url, created_at) "
            "VALUES (?,?,?,?,datetime('now'))",
            (f'zernio_{platform}', tool_slug, str(post_id), url)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'  DB log error: {e}')


def already_posted_today(tool_slug):
    try:
        conn = sqlite3.connect(DB_PATH)
        r = conn.execute(
            "SELECT id FROM posts WHERE platform LIKE 'zernio_%' AND tool_slug=? "
            "AND date(created_at)=date('now')",
            (tool_slug,)
        ).fetchone()
        conn.close()
        return r is not None
    except:
        return False


# ── Content builder ──────────────────────────────────────────────────────────────
def build_content(tool):
    """Generate a clean multi-platform post for the tool."""
    n   = tool['name']
    s   = tool['score']
    tag = tool['tagline']
    slug = tool['slug']
    cat  = tool.get('cat', 'AI Tool')
    url  = f'https://rankertoolai.com/review/{slug}/'

    # Rotate variation based on post count to avoid repetition
    variations = [
        f"{n} scores {s}/10 in our independent test.\n\n{tag}\n\nFull review → {url}",
        f"Tested {n} for 30 days. Here's the honest verdict:\n\n✅ {tag}\n📊 Score: {s}/10\n\n{url}",
        f"Is {n} worth it in 2026?\n\n{tag}\n\nWe ran 50+ real tests. Score: {s}/10\n→ {url}",
        f"Best {cat} picks for 2026:\n\n{n} made the list at {s}/10\n\n\"{tag}\"\n\n{url}",
        f"Honest {n} review after 30+ days:\n\nPros, cons, pricing, alternatives.\nScore: {s}/10\n\n{url}",
    ]

    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE platform LIKE 'zernio_%' AND tool_slug=?",
            (slug,)
        ).fetchone()[0]
        conn.close()
    except:
        count = 0

    return variations[count % len(variations)]


# ── Load tools ───────────────────────────────────────────────────────────────────
def load_tools():
    if TOOLS_FILE.exists():
        return json.loads(TOOLS_FILE.read_text(encoding='utf-8'))
    # Fallback: top tools hardcoded
    return [
        {'name': 'Semrush',    'slug': 'semrush',    'score': 9.1, 'cat': 'AI SEO Suite',   'tagline': 'Most complete SEO and marketing platform powered by AI', 'price': 'Free / $139/mo'},
        {'name': 'ChatGPT',    'slug': 'chatgpt',    'score': 8.8, 'cat': 'AI Chatbot',      'tagline': 'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins', 'price': 'Free / $20/mo'},
        {'name': 'Cursor',     'slug': 'cursor',     'score': 9.2, 'cat': 'AI Coding Tool',  'tagline': 'Best AI code editor that writes code faster than you', 'price': 'Free / $20/mo'},
        {'name': 'ElevenLabs', 'slug': 'elevenlabs', 'score': 9.2, 'cat': 'AI Voice',        'tagline': 'Most realistic AI voice generator in 2026', 'price': 'Free / $5/mo'},
        {'name': 'Surfer SEO', 'slug': 'surfer-seo', 'score': 9.0, 'cat': 'AI SEO Tool',    'tagline': 'Best AI content optimizer that ranks pages faster', 'price': '$89/mo'},
    ]


# ── Main post flow ───────────────────────────────────────────────────────────────
def post_tool(tool, target_platforms=None, image_path=None, dry_run=False):
    """Post for one tool across all (or specified) connected platforms."""
    slug = tool['slug']

    if already_posted_today(slug):
        print(f'  ↷ {tool["name"]} already posted today via Zernio, skipping')
        return False

    content   = build_content(tool)
    media_url = None

    if image_path:
        if not dry_run:
            media_url = upload_image(image_path)
    else:
        # Look for a Pinterest/OG image in assets
        candidates = [
            ROOT / 'html' / 'assets' / 'images' / f'pin-{slug}.jpg',
            ROOT / 'html' / 'assets' / 'images' / f'og-review-{slug}.jpg',
        ]
        for c in candidates:
            if c.exists():
                if not dry_run:
                    media_url = upload_image(str(c))
                else:
                    print(f'  [DRY] Would upload {c.name}')
                break

    account_map = get_account_ids(target_platforms) if not dry_run else {}

    if dry_run:
        print(f'\n  [DRY RUN] Tool: {tool["name"]}')
        print(f'  Platforms: {target_platforms or "all connected"}')
        print(f'  Content preview:\n{content[:200]}...' if len(content) > 200 else f'  Content:\n{content}')
        return True

    if not account_map:
        print(f'  No connected accounts found. Run --list-accounts to check.')
        return False

    print(f'  Posting to: {", ".join(account_map.keys())}')
    results = create_post(content, account_map, media_url=media_url)

    ok_count = 0
    for pf, r in results.items():
        if r:
            post_id  = r.get('_id') or r.get('id') or r.get('post', {}).get('_id') or ''
            post_url = r.get('url') or ''
            log_post(slug, pf, str(post_id), post_url)
            print(f'  [OK] {pf:12s} id:{str(post_id)[:12]}')
            ok_count += 1
        else:
            print(f'  [ERR] {pf:12s} failed')
    return ok_count > 0


# ── CLI ──────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Post to social media via Zernio API')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list-accounts', action='store_true', help='List connected Zernio accounts')
    group.add_argument('--tool',    metavar='SLUG', help='Post for a specific tool slug')
    group.add_argument('--all',     action='store_true', help='Post for all tools (one each)')
    group.add_argument('--content', metavar='TEXT', help='Post a custom text')

    parser.add_argument('--platforms', nargs='+', metavar='PLATFORM',
                        help='Target specific platforms (twitter linkedin etc.)')
    parser.add_argument('--image',  metavar='PATH', help='Image file to attach')
    parser.add_argument('--limit',  type=int, default=0, help='Max tools to post (--all mode)')
    parser.add_argument('--delay',  type=float, default=30, help='Seconds between posts (--all mode)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without posting')
    args = parser.parse_args()

    if not API_KEY:
        print('ZERNIO_API_KEY not set. Add it to social_agent/.env')
        sys.exit(1)

    target = args.platforms or None

    # ── List accounts ──
    if args.list_accounts:
        profile_id = get_default_profile_id()
        print(f'  Zernio profile: {profile_id or "none"}')
        accounts = list_accounts()
        if not accounts:
            print('\n  No social accounts connected yet.')
            print('  >> Go to https://zernio.com/accounts and connect:')
            print('     Twitter/X, LinkedIn, Pinterest, Instagram, Facebook, TikTok, Reddit, etc.')
            print('  Then re-run this script to start posting.')
            return
        print(f'\n  Connected accounts ({len(accounts)}):')
        for acc in accounts:
            pf  = acc.get('platform', '?')
            aid = acc.get('_id') or acc.get('id', '?')
            name = acc.get('name') or acc.get('username') or ''
            print(f'    {pf:15s}  {aid}  {name}')
        return

    # ── Custom content ──
    if args.content:
        account_map = get_account_ids(target) if not args.dry_run else {}
        media_url = upload_image(args.image) if args.image and not args.dry_run else None
        if args.dry_run:
            print(f'[DRY] Would post: {args.content[:120]}')
            print(f'[DRY] Platforms: {target or "all"}')
            return
        result = create_post(args.content, account_map, media_url=media_url)
        if result:
            print(f'✓ Posted  id: {result.get("_id", "")}')
        return

    tools = load_tools()

    # ── Single tool ──
    if args.tool:
        matches = [t for t in tools if t['slug'] == args.tool]
        if not matches:
            print(f'Tool "{args.tool}" not found in tools.json')
            sys.exit(1)
        post_tool(matches[0], target_platforms=target,
                  image_path=args.image, dry_run=args.dry_run)
        return

    # ── All tools ──
    if args.all:
        subset = tools[:args.limit] if args.limit else tools
        ok = err = skip = 0
        for i, tool in enumerate(subset):
            print(f'\n[{i+1}/{len(subset)}] {tool["name"]}')
            result = post_tool(tool, target_platforms=target,
                               image_path=args.image, dry_run=args.dry_run)
            if result is True:
                ok += 1
            elif result is False:
                # check if it was a skip
                if already_posted_today(tool['slug']):
                    skip += 1
                else:
                    err += 1
            if i < len(subset) - 1 and not args.dry_run:
                print(f'  Waiting {args.delay}s...')
                time.sleep(args.delay)
        print(f'\n  Done — ✓{ok}  ↷{skip}  ✗{err}')
        return

    parser.print_help()


if __name__ == '__main__':
    main()
