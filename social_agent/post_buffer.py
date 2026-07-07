#!/usr/bin/env python3
"""
RankerToolAI — Buffer GraphQL poster (free tier: 3 channels)

Buffer free plan = 3 social channels. Recommended assignment:
  - Twitter/X
  - Facebook Page
  - Pinterest

Usage:
  python social_agent/post_buffer.py --list-channels
  python social_agent/post_buffer.py --tool semrush
  python social_agent/post_buffer.py --tool cursor --channels twitter facebook
  python social_agent/post_buffer.py --all --limit 5
  python social_agent/post_buffer.py --content "Custom text" --dry-run

Setup:
  1. Go to https://publish.buffer.com → Settings → API
  2. Generate API key → add to social_agent/.env as BUFFER_API_KEY=...
  3. Connect your 3 channels in Buffer dashboard
  4. Run: python social_agent/post_buffer.py --list-channels
"""

import os, sys, json, time, argparse, urllib.request, urllib.error, sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

ENDPOINT = 'https://api.buffer.com'
API_KEY  = os.getenv('BUFFER_API_KEY', '')
DB_PATH  = Path(__file__).parent / 'data' / 'posts.db'
ROOT     = Path(__file__).resolve().parent.parent
TOOLS_FILE = Path(__file__).parent / 'data' / 'tools.json'

# Buffer platform slugs
BUFFER_PLATFORMS = ['twitter', 'facebook', 'pinterest', 'instagram',
                    'linkedin', 'tiktok', 'youtube', 'mastodon', 'bluesky']


# ── GraphQL helper ───────────────────────────────────────────────────────────────
def gql(query, variables=None):
    body = {'query': query}
    if variables:
        body['variables'] = variables
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        }, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    if 'errors' in resp:
        raise Exception(f"GraphQL error: {resp['errors']}")
    return resp.get('data', {})


# ── Channel discovery ────────────────────────────────────────────────────────────
def get_org_id():
    """Get organization ID via account query."""
    data = gql('{ account { organizations { id name } } }')
    orgs = (data.get('account') or {}).get('organizations', [])
    return orgs[0]['id'] if orgs else None


def list_channels():
    """Return list of connected Buffer channels."""
    try:
        org_id = get_org_id()
        if not org_id:
            return []
        data = gql(
            '''query Channels($orgId: OrganizationId!) {
                channels(input: { organizationId: $orgId }) {
                    id
                    name
                    displayName
                    service
                    isDisconnected
                }
            }''',
            {'orgId': org_id}
        )
        return data.get('channels', [])
    except Exception as e:
        print(f'  [Buffer] Error listing channels: {e}')
        return []


def get_channel_map(target_services=None):
    """Return {service: channel_id} for active connected channels."""
    channels = list_channels()
    result = {}
    for ch in channels:
        svc = (ch.get('service') or '').lower()
        cid = ch.get('id', '')
        if not svc or not cid:
            continue
        if ch.get('isDisconnected'):
            continue
        if target_services is None or svc in target_services:
            result[svc] = cid
    return result


# ── Post creation ────────────────────────────────────────────────────────────────
REQUIRES_IMAGE = {'pinterest', 'instagram', 'tiktok'}
REQUIRES_VIDEO = {'youtube'}

def create_post(text, channel_id, service, image_url=None, title=None):
    """Schedule a post to a single Buffer channel."""
    # Skip platforms that need content we don't have
    if service in REQUIRES_VIDEO:
        raise Exception(f'{service} requires a video — skip')
    if service in REQUIRES_IMAGE and not image_url:
        raise Exception(f'{service} requires an image — no image available for this tool')

    assets = []
    if image_url:
        assets.append({'image': {'url': image_url}})

    mutation = '''
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on PostActionSuccess { post { id text } }
            ... on MutationError { message }
        }
    }'''

    inp = {
        'channelId': channel_id,
        'text': text,
        'schedulingType': 'automatic',
        'mode': 'addToQueue',
        'assets': assets,
    }
    if title:
        inp['metadata'] = {'title': title}

    data = gql(mutation, {'input': inp})
    result = data.get('createPost', {})
    if 'post' in result:
        return result['post'].get('id')
    if 'message' in result:
        raise Exception(result['message'])
    return None


# ── Content builder ──────────────────────────────────────────────────────────────
def build_content(tool, platform=''):
    n    = tool['name']
    s    = tool['score']
    tag  = tool['tagline']
    slug = tool['slug']
    url  = f'https://rankertoolai.com/review/{slug}/'

    templates = {
        'twitter': [
            f'{n} review after 30 days: {s}/10\n\n{tag}\n\nFull breakdown: {url}',
            f'Tested {n} vs its competitors. Here\'s the verdict: {s}/10\n\n{tag}\n\n{url}',
            f'Is {n} worth it in 2026? Score: {s}/10\n\n{tag}\n\n{url}',
        ],
        'facebook': [
            f'We just published our in-depth {n} review after 30+ days of testing.\n\nScore: {s}/10\n\n{tag}\n\nRead the full review: {url}',
            f'{n} is one of the top AI tools we\'ve tested this year.\n\nOur verdict: {s}/10\n\n{tag}\n\nSee the full breakdown: {url}',
        ],
        'pinterest': [
            f'{n} — {tag}\n\nScore: {s}/10\n\nFull review: {url}',
            f'Best {tool.get("cat", "AI Tool")} of 2026: {n} ({s}/10)\n\n{tag}\n\n{url}',
        ],
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE platform LIKE 'buffer_%' AND tool_slug=?",
            (slug,)
        ).fetchone()[0]
        conn.close()
    except:
        count = 0

    pool = templates.get(platform, [
        f'{n} scores {s}/10 in our test. {tag}\n{url}',
        f'Tested {n} for 30 days. Score: {s}/10. {tag}\n{url}',
    ])
    return pool[count % len(pool)]


# ── DB logging ───────────────────────────────────────────────────────────────────
def log_post(tool_slug, service, post_id=''):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR IGNORE INTO posts (platform, tool_slug, post_id, created_at) "
            "VALUES (?,?,?,datetime('now'))",
            (f'buffer_{service}', tool_slug, str(post_id))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'  DB log error: {e}')


def already_posted_today(tool_slug):
    try:
        conn = sqlite3.connect(DB_PATH)
        r = conn.execute(
            "SELECT id FROM posts WHERE platform LIKE 'buffer_%' AND tool_slug=? "
            "AND date(created_at)=date('now')",
            (tool_slug,)
        ).fetchone()
        conn.close()
        return r is not None
    except:
        return False


# ── Find image ────────────────────────────────────────────────────────────────────
def find_image_url(tool, platform=''):
    """Return a live URL for the tool's image (already deployed to Cloudflare)."""
    slug = tool['slug']
    prefix_map = {'pinterest': 'pin', 'instagram': 'ig', 'twitter': 'og-review',
                  'facebook': 'og-review', 'linkedin': 'og-review'}
    prefix = prefix_map.get(platform, 'og-review')
    fname = f'{prefix}-{slug}.jpg'
    local = ROOT / 'html' / 'assets' / 'images' / fname
    if local.exists():
        return f'https://rankertoolai.com/assets/images/{fname}'
    fallback = ROOT / 'html' / 'assets' / 'images' / f'og-review-{slug}.jpg'
    if fallback.exists():
        return f'https://rankertoolai.com/assets/images/og-review-{slug}.jpg'
    return None


# ── Load tools ────────────────────────────────────────────────────────────────────
def load_tools():
    if TOOLS_FILE.exists():
        return json.loads(TOOLS_FILE.read_text(encoding='utf-8'))
    return []


# ── Main post flow ────────────────────────────────────────────────────────────────
def post_tool(tool, target_services=None, dry_run=False):
    """Post for one tool to all (or specified) connected Buffer channels."""
    slug = tool['slug']

    if already_posted_today(slug):
        print(f'  >> {tool["name"]} already posted today via Buffer, skipping')
        return False

    channel_map = get_channel_map(target_services) if not dry_run else {}

    if dry_run:
        print(f'\n  [DRY] Tool: {tool["name"]}')
        print(f'  Channels: {target_services or "all connected"}')
        sample = build_content(tool, 'twitter')
        print(f'  Content preview:\n{sample}')
        return True

    if not channel_map:
        print('  No connected Buffer channels. Run --list-channels to check.')
        return False

    ok_count = 0
    for service, channel_id in channel_map.items():
        text      = build_content(tool, service)
        image_url = find_image_url(tool, service)
        try:
            post_id = create_post(text, channel_id, service, image_url=image_url)
            if post_id:
                log_post(slug, service, post_id)
                print(f'  [OK] {service:12s} queued  id:{post_id[:10]}')
                ok_count += 1
            else:
                print(f'  [??] {service:12s} no post id returned')
        except Exception as e:
            print(f'  [SKIP] {service:12s} {e}')

    return ok_count > 0


# ── CLI ───────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Post via Buffer GraphQL API (free 3 channels)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list-channels', action='store_true')
    group.add_argument('--tool',    metavar='SLUG')
    group.add_argument('--all',     action='store_true')
    group.add_argument('--content', metavar='TEXT')

    parser.add_argument('--channels', nargs='+', metavar='SERVICE',
                        help='e.g. twitter facebook pinterest')
    parser.add_argument('--limit',   type=int, default=0)
    parser.add_argument('--delay',   type=float, default=10)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not API_KEY:
        print('BUFFER_API_KEY not set.')
        print('Go to https://publish.buffer.com -> Settings -> API -> Generate key')
        print('Then add to social_agent/.env: BUFFER_API_KEY=...')
        sys.exit(1)

    target = args.channels or None

    if args.list_channels:
        channels = list_channels()
        if not channels:
            print('No connected channels. Connect them at https://publish.buffer.com')
            return
        print(f'\n  Buffer channels ({len(channels)}):')
        for ch in channels:
            print(f'    {ch.get("service","?"):12s}  {ch.get("id","?")}  {ch.get("name","")}')
        return

    if args.content:
        channel_map = get_channel_map(target) if not args.dry_run else {}
        if args.dry_run:
            print(f'[DRY] Would post: {args.content[:120]}')
            return
        for svc, cid in channel_map.items():
            try:
                pid = create_post(args.content, cid)
                print(f'[OK] {svc}: {pid}')
            except Exception as e:
                print(f'[ERR] {svc}: {e}')
        return

    tools = load_tools()

    if args.tool:
        matches = [t for t in tools if t['slug'] == args.tool]
        if not matches:
            print(f'Tool "{args.tool}" not found')
            sys.exit(1)
        post_tool(matches[0], target_services=target, dry_run=args.dry_run)
        return

    if args.all:
        subset = tools[:args.limit] if args.limit else tools
        ok = err = skip = 0
        for i, tool in enumerate(subset):
            print(f'\n[{i+1}/{len(subset)}] {tool["name"]}')
            result = post_tool(tool, target_services=target, dry_run=args.dry_run)
            if result:
                ok += 1
            else:
                if already_posted_today(tool['slug']):
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
