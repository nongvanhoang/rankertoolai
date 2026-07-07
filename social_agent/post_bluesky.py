#!/usr/bin/env python3
"""
RankerToolAI — Bluesky poster via AT Protocol (free, no OAuth)

Bluesky uses the AT Protocol (atproto) — no paid plan needed.
Authentication is just username + app password.

Setup:
  1. Go to https://bsky.app -> Settings -> Privacy and Security -> App Passwords
  2. Create an app password -> copy it
  3. Add to social_agent/.env:
       BLUESKY_HANDLE=yourhandle.bsky.social
       BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

Usage:
  python social_agent/post_bluesky.py --tool semrush
  python social_agent/post_bluesky.py --all --limit 3
  python social_agent/post_bluesky.py --content "Custom post" --dry-run
"""

import os, sys, json, time, argparse, urllib.request, urllib.error, sqlite3
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

ATP_BASE   = 'https://bsky.social/xrpc'
HANDLE     = os.getenv('BLUESKY_HANDLE', '')
APP_PASS   = os.getenv('BLUESKY_APP_PASSWORD', '')
DB_PATH    = Path(__file__).parent / 'data' / 'posts.db'
ROOT       = Path(__file__).resolve().parent.parent
TOOLS_FILE = Path(__file__).parent / 'data' / 'tools.json'

_session = {}   # cached {accessJwt, did}


# ── AT Protocol helpers ──────────────────────────────────────────────────────────
def _post(path, body, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(
        f'{ATP_BASE}/{path}',
        data=json.dumps(body).encode(),
        headers=headers, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _get(path, params=None, token=None):
    url = f'{ATP_BASE}/{path}'
    if params:
        qs = '&'.join(f'{k}={v}' for k, v in params.items())
        url = f'{url}?{qs}'
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_session():
    """Create or return cached session."""
    if _session.get('accessJwt'):
        return _session
    data = _post('com.atproto.server.createSession', {
        'identifier': HANDLE,
        'password': APP_PASS,
    })
    _session.update(data)
    return _session


# ── Upload image to Bluesky CDN ──────────────────────────────────────────────────
def upload_image(image_path, token):
    """Upload image blob to Bluesky. Returns blob ref dict or None."""
    p = Path(image_path)
    if not p.exists():
        return None
    ext = p.suffix.lower()
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'webp': 'image/webp'}.get(ext.lstrip('.'), 'image/jpeg')
    file_bytes = p.read_bytes()
    req = urllib.request.Request(
        f'{ATP_BASE}/com.atproto.repo.uploadBlob',
        data=file_bytes,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': mime},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read()).get('blob')


# ── Create post (skeet) ──────────────────────────────────────────────────────────
def create_post(text, did, token, image_path=None, alt_text=''):
    """Create a Bluesky post. Returns post URI or None."""
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    record = {
        '$type': 'app.bsky.feed.post',
        'text': text[:300],
        'createdAt': now,
        'langs': ['en'],
    }

    # Attach image if provided
    if image_path:
        blob = upload_image(image_path, token)
        if blob:
            record['embed'] = {
                '$type': 'app.bsky.embed.images',
                'images': [{'image': blob, 'alt': alt_text or text[:100]}],
            }

    # Extract URL for facets (clickable links)
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    if urls:
        facets = []
        for url in urls:
            start = text.encode('utf-8').find(url.encode('utf-8'))
            if start >= 0:
                facets.append({
                    'index': {'byteStart': start, 'byteEnd': start + len(url.encode('utf-8'))},
                    'features': [{'$type': 'app.bsky.richtext.facet#link', 'uri': url}],
                })
        if facets:
            record['facets'] = facets

    data = _post('com.atproto.repo.createRecord', {
        'repo': did,
        'collection': 'app.bsky.feed.post',
        'record': record,
    }, token=token)
    return data.get('uri')


# ── Content ──────────────────────────────────────────────────────────────────────
def build_content(tool):
    n, s, tag, slug = tool['name'], tool['score'], tool['tagline'], tool['slug']
    url = f'https://rankertoolai.com/review/{slug}/'

    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE platform='bluesky' AND tool_slug=?", (slug,)
        ).fetchone()[0]
        conn.close()
    except:
        count = 0

    variations = [
        f'{n} review: {s}/10\n\n{tag}\n\n{url}',
        f'Tested {n} for 30 days. Verdict: {s}/10\n\n{tag}\n\n{url}',
        f'Is {n} worth it in 2026?\n\nScore: {s}/10\n{tag}\n\n{url}',
        f'Honest {n} review — no affiliate bias.\n\n{s}/10 | {tag}\n\n{url}',
    ]
    return variations[count % len(variations)]


# ── DB ────────────────────────────────────────────────────────────────────────────
def log_post(tool_slug, uri=''):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR IGNORE INTO posts (platform, tool_slug, url, created_at) "
            "VALUES ('bluesky',?,?,datetime('now'))",
            (tool_slug, uri or '')
        )
        conn.commit()
        conn.close()
    except:
        pass


def already_posted_today(slug):
    try:
        conn = sqlite3.connect(DB_PATH)
        r = conn.execute(
            "SELECT id FROM posts WHERE platform='bluesky' AND tool_slug=? "
            "AND date(created_at)=date('now')", (slug,)
        ).fetchone()
        conn.close()
        return r is not None
    except:
        return False


def load_tools():
    if TOOLS_FILE.exists():
        return json.loads(TOOLS_FILE.read_text(encoding='utf-8'))
    return []


# ── Main flow ─────────────────────────────────────────────────────────────────────
def post_tool(tool, dry_run=False):
    slug = tool['slug']
    if already_posted_today(slug):
        print(f'  >> {tool["name"]} already posted today on Bluesky, skipping')
        return False

    text = build_content(tool)

    # Find image
    candidates = [
        ROOT / 'html' / 'assets' / 'images' / f'og-review-{slug}.jpg',
        ROOT / 'html' / 'assets' / 'images' / f'pin-{slug}.jpg',
    ]
    image_path = next((str(p) for p in candidates if p.exists()), None)

    if dry_run:
        print(f'  [DRY] {tool["name"]} | Bluesky')
        print(f'  Content:\n{text}')
        if image_path:
            print(f'  Image: {Path(image_path).name}')
        return True

    try:
        sess = get_session()
        uri = create_post(text, sess['did'], sess['accessJwt'],
                          image_path=image_path, alt_text=f'{tool["name"]} review')
        if uri:
            log_post(slug, uri)
            print(f'  [OK] Bluesky post: {uri}')
            return True
        print('  [ERR] No URI returned from Bluesky')
        return False
    except Exception as e:
        print(f'  [ERR] Bluesky: {e}')
        return False


def main():
    parser = argparse.ArgumentParser(description='Post to Bluesky via AT Protocol')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tool',    metavar='SLUG')
    group.add_argument('--all',     action='store_true')
    group.add_argument('--content', metavar='TEXT')
    parser.add_argument('--limit',   type=int, default=0)
    parser.add_argument('--delay',   type=float, default=10)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not HANDLE or not APP_PASS:
        print('BLUESKY_HANDLE and BLUESKY_APP_PASSWORD not set.')
        print('Go to https://bsky.app -> Settings -> App Passwords -> Add')
        print('Then add to social_agent/.env:')
        print('  BLUESKY_HANDLE=yourhandle.bsky.social')
        print('  BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx')
        sys.exit(1)

    if args.content:
        if args.dry_run:
            print(f'[DRY] Would post: {args.content[:120]}')
            return
        sess = get_session()
        uri = create_post(args.content, sess['did'], sess['accessJwt'])
        print(f'[OK] {uri}' if uri else '[ERR] No URI returned')
        return

    tools = load_tools()

    if args.tool:
        matches = [t for t in tools if t['slug'] == args.tool]
        if not matches:
            print(f'Tool "{args.tool}" not found')
            sys.exit(1)
        post_tool(matches[0], dry_run=args.dry_run)
        return

    if args.all:
        subset = tools[:args.limit] if args.limit else tools
        ok = err = skip = 0
        for i, t in enumerate(subset):
            print(f'\n[{i+1}/{len(subset)}] {t["name"]}')
            r = post_tool(t, dry_run=args.dry_run)
            (ok if r else (skip if already_posted_today(t['slug']) else err)).__class__  # noqa
            if r:
                ok += 1
            elif already_posted_today(t['slug']):
                skip += 1
            else:
                err += 1
            if i < len(subset) - 1 and not args.dry_run:
                time.sleep(args.delay)
        print(f'\n  Done: OK={ok}  Skip={skip}  Err={err}')
        return

    parser.print_help()


if __name__ == '__main__':
    main()
