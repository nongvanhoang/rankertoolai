#!/usr/bin/env python3
"""
RankerToolAI — Batch image & video generator

Images  → kie.ai API  → saved to html/assets/images/
Videos  → fal.ai Kling 1.5 Pro  → URLs saved to social_agent/video_cache.json

Usage examples:
  python social_agent/batch_generate.py pinterest
  python social_agent/batch_generate.py instagram --limit 5
  python social_agent/batch_generate.py all --mode image
  python social_agent/batch_generate.py tiktok --mode video
  python social_agent/batch_generate.py all --mode both --delay 3

Environment vars (optional):
  KIE_AI_KEY      kie.ai API key
  KIE_AI_ENDPOINT kie.ai endpoint  (default: https://api.kie.ai/v1/images/generations)
  FAL_KEY         fal.ai API key
"""

import os, sys, json, time, argparse, urllib.request, urllib.error
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / 'html' / 'assets' / 'images'
CACHE_FILE = Path(__file__).parent / 'video_cache.json'

PLATFORMS = ['pinterest', 'instagram', 'tiktok', 'youtube',
             'twitter', 'threads', 'linkedin', 'facebook', 'reddit', 'quora']

IMG_PREFIX = {
    'pinterest': 'pin',
    'instagram': 'ig',
    'tiktok':    'tt',
    'youtube':   'yt',
}

IMG_SIZES = {
    'pinterest': (1024, 1536),
    'instagram': (1024, 1024),
    'tiktok':    (576,  1024),
    'youtube':   (1280, 720),
    'twitter':   (1200, 630),
    'threads':   (1024, 1024),
    'linkedin':  (1200, 628),
    'facebook':  (1200, 630),
    'reddit':    (1200, 628),
    'quora':     (1200, 630),
}

FAL_ASPECT = {
    'pinterest': '2:3',
    'instagram': '1:1',
    'tiktok':    '9:16',
    'youtube':   '16:9',
    'twitter':   '16:9',
    'threads':   '1:1',
    'linkedin':  '16:9',
    'facebook':  '16:9',
    'reddit':    '16:9',
    'quora':     '16:9',
}

FAL_VID_PROMPT = {
    'tiktok':    'smooth cinematic zoom in, dynamic motion, tech product reveal, vertical video',
    'youtube':   'dramatic cinematic reveal, zoom from center, professional product showcase',
    'instagram': 'smooth parallax zoom, aesthetic product reveal, square format',
    'pinterest': 'gentle ken burns effect, elegant upward motion, portrait format',
    'twitter':   'smooth zoom in, professional product reveal',
    'linkedin':  'corporate professional reveal, smooth zoom, business tech showcase',
    'facebook':  'smooth zoom in, product reveal, social media style',
    'threads':   'smooth parallax zoom, clean minimal aesthetic',
    'reddit':    'smooth zoom in, authentic product reveal',
    'quora':     'clean professional reveal, smooth motion',
}

TOOLS = [
    {'name':'ChatGPT',       'slug':'chatgpt',        'score':8.8,'cat':'AI Chatbot',          'tagline':'Most versatile AI assistant — GPT-4o, images, voice & 1,000+ plugins','price':'Free / $20/mo Plus'},
    {'name':'Claude',        'slug':'claude',          'score':9.2,'cat':'AI Chatbot',          'tagline':'Best AI for writing & reasoning — 200K context, safest frontier model','price':'Free / $20/mo Pro'},
    {'name':'Midjourney',    'slug':'midjourney',      'score':9.1,'cat':'AI Image Generator',  'tagline':'Best AI image generator — stunning quality preferred by designers','price':'From $10/mo'},
    {'name':'Cursor',        'slug':'cursor',          'score':9.2,'cat':'AI Coding Tool',      'tagline':'Best AI code editor that writes code faster than you','price':'Free / $20/mo Pro'},
    {'name':'Semrush',       'slug':'semrush',         'score':9.1,'cat':'AI SEO Suite',        'tagline':'Most complete SEO and marketing platform powered by AI','price':'Free / $139/mo Pro'},
    {'name':'ElevenLabs',    'slug':'elevenlabs',      'score':9.2,'cat':'AI Voice Generator',  'tagline':'Most realistic AI voice generator in 2026','price':'Free / $5/mo Starter'},
    {'name':'GitHub Copilot','slug':'github-copilot',  'score':9.1,'cat':'AI Coding Tool',      'tagline':'Most-used AI coding assistant — real-time suggestions in every IDE','price':'Free / $10/mo Pro'},
    {'name':'Perplexity AI', 'slug':'perplexity',      'score':8.8,'cat':'AI Search Tool',      'tagline':'Best AI for research — real-time answers with cited sources','price':'Free / $20/mo Pro'},
    {'name':'Jasper AI',     'slug':'jasper',          'score':8.9,'cat':'AI Writing Tool',     'tagline':'Best AI writing assistant for marketing teams','price':'$39/mo Creator'},
    {'name':'Windsurf',      'slug':'windsurf',        'score':8.9,'cat':'AI Coding IDE',       'tagline':'Best value AI coding IDE — Cascade agent at $15/mo','price':'Free / $15/mo Pro'},
    {'name':'Stable Diffusion','slug':'stable-diffusion','score':8.9,'cat':'AI Image Generator','tagline':'Best free open-source AI image generator in 2026','price':'Free / $10/mo'},
    {'name':'Canva AI',      'slug':'canva-ai',        'score':8.7,'cat':'AI Design Tool',      'tagline':'Best AI design tool for non-designers in 2026','price':'Free / $15/mo Pro'},
    {'name':'Grok 3',        'slug':'grok',            'score':8.4,'cat':'AI Chatbot',          'tagline':"Elon Musk's AI chatbot with real-time X data access",'price':'X Premium $8/mo'},
    {'name':'Runway ML',     'slug':'runway',          'score':9.0,'cat':'AI Video Generator',  'tagline':'Best AI video generation platform for creators','price':'Free / $15/mo Standard'},
    {'name':'DeepSeek',      'slug':'deepseek',        'score':9.0,'cat':'AI Chatbot',          'tagline':'Open-source AI that shocked Silicon Valley — free & GPT-4 quality','price':'Free / API $0.14/M'},
    {'name':'Gemini',        'slug':'gemini',          'score':8.7,'cat':'AI Chatbot',          'tagline':"Google's AI — best for G-Suite users and real-time search",'price':'Free / $20/mo Advanced'},
    {'name':'Notion AI',     'slug':'notion',          'score':8.9,'cat':'AI Productivity Tool','tagline':'AI writing & summarization built into the best productivity workspace','price':'+$10/mo add-on'},
    {'name':'Otter.ai',      'slug':'otter-ai',        'score':8.7,'cat':'AI Productivity Tool','tagline':'Best AI meeting assistant — real-time transcription & action items','price':'Free / $16.99/mo Pro'},
    {'name':'HubSpot AI',    'slug':'hubspot',         'score':8.2,'cat':'AI CRM & Marketing',  'tagline':'CRM-native AI — Breeze AI for sales & marketing teams','price':'Free CRM / $20/mo Starter'},
    {'name':'Surfer SEO',    'slug':'surfer-seo',      'score':9.0,'cat':'AI SEO Tool',         'tagline':'Best AI content optimizer that ranks pages faster','price':'$89/mo Essential'},
    {'name':'Writesonic',    'slug':'writesonic',      'score':8.7,'cat':'AI Writing Tool',     'tagline':'Best budget AI writer with GPT-4 quality output','price':'Free / $16/mo Chatsonic'},
]


# ── Prompt builder ─────────────────────────────────────────────────────────────
def build_prompt(tool, platform):
    base = ('dark navy background #080c18, orange accent color #f97316, '
            'professional tech aesthetic, high quality digital art, clean minimalist design')
    n, tag, s = tool['name'], tool['tagline'], tool['score']
    p = {
        'pinterest': f'Tall portrait review card for "{n}" AI tool. "{tag}". Score badge {s}/10. {base}. 1000x1500 portrait social media pin.',
        'instagram': f'Square social media review post for "{n}" AI tool. Score {s}/10. "{tag}". {base}. 1080x1080 square Instagram post.',
        'tiktok':    f'Vertical TikTok thumbnail for "{n}" AI review. Bold text "{s}/10". Eye-catching gradient. {base}. 1080x1920 vertical.',
        'youtube':   f'YouTube thumbnail for "{n} Review 2026". Text "IS IT WORTH IT? {s}/10". High contrast, readable small. {base}. 1280x720 landscape.',
        'twitter':   f'Wide social card for "{n}" AI tool. Score {s}/10. "{tag}". {base}. 1200x628 Twitter card.',
        'threads':   f'Square post for "{n}" AI review. {s}/10. "{tag}". {base}.',
        'linkedin':  f'Professional LinkedIn post image for "{n}". "{tag}". Score {s}/10. Corporate tech style. {base}. 1200x628.',
        'facebook':  f'Facebook post image for "{n}" AI tool review. {s}/10. "{tag}". {base}. 1200x630.',
        'reddit':    f'Wide banner for "{n}" honest review. {s}/10. "{tag}". {base}.',
        'quora':     f'Featured image for "{n}" AI tool answer. {s}/10. {base}.',
    }
    return p.get(platform, f'Social media image for {n} AI tool review. {s}/10. {base}.')


def img_filename(tool, platform):
    prefix = IMG_PREFIX.get(platform, 'og-review')
    if platform in IMG_PREFIX:
        return f'{prefix}-{tool["slug"]}.jpg'
    return f'og-review-{tool["slug"]}.jpg'


# ── API helpers ────────────────────────────────────────────────────────────────
def extract_url(data):
    if isinstance(data, list) and data:
        data = {'data': data}
    checks = [
        lambda d: (d.get('data') or [{}])[0].get('url'),
        lambda d: (d.get('images') or [{}])[0].get('url'),
        lambda d: (d.get('result') or {}).get('url'),
        lambda d: d.get('image_url'),
        lambda d: d.get('url'),
        lambda d: d.get('output_url'),
    ]
    for fn in checks:
        try:
            v = fn(data)
            if v and isinstance(v, str) and v.startswith('http'):
                return v
        except Exception:
            pass
    return None


def api_post(url, body, headers):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={**headers, 'Content-Type': 'application/json'}, method='POST'
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def api_get(url, headers):
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def download(url, path):
    with urllib.request.urlopen(url, timeout=60) as r:
        Path(path).write_bytes(r.read())


# ── Image generation ───────────────────────────────────────────────────────────
def generate_image(tool, platform, api_key, endpoint, status_ep=''):
    w, h = IMG_SIZES.get(platform, (1024, 1024))
    body = {'prompt': build_prompt(tool, platform), 'width': w, 'height': h, 'n': 1}
    data = api_post(endpoint, body, {'Authorization': f'Bearer {api_key}'})

    url = extract_url(data)
    if url:
        return url

    task_id = data.get('task_id') or data.get('id') or data.get('request_id')
    if task_id and status_ep:
        poll_url = status_ep.replace('{task_id}', str(task_id))
        for _ in range(72):
            time.sleep(5)
            sd = api_get(poll_url, {'Authorization': f'Bearer {api_key}'})
            url = extract_url(sd)
            if url:
                return url
        raise Exception('Timeout after 6 min waiting for kie.ai')

    raise Exception(f'No image URL in response. Raw: {json.dumps(data)[:200]}')


# ── Video generation (fal.ai Kling) ───────────────────────────────────────────
def queue_video(image_url, platform, fal_key):
    body = {
        'image_url': image_url,
        'prompt':    FAL_VID_PROMPT.get(platform, 'smooth zoom in, professional product showcase'),
        'duration':  '5',
        'aspect_ratio': FAL_ASPECT.get(platform, '16:9'),
    }
    data = api_post(
        'https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video',
        body, {'Authorization': f'Key {fal_key}'}
    )
    return data.get('request_id')


def poll_video(request_id, fal_key, timeout_s=600):
    base = 'https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video'
    status_url = f'{base}/requests/{request_id}/status'
    result_url = f'{base}/requests/{request_id}'
    hdrs = {'Authorization': f'Key {fal_key}'}
    deadline = time.time() + timeout_s

    while time.time() < deadline:
        time.sleep(8)
        sd = api_get(status_url, hdrs)
        status = sd.get('status', '')
        if status == 'COMPLETED':
            rd = api_get(result_url, hdrs)
            return rd.get('video', {}).get('url') or rd.get('url')
        if status == 'FAILED':
            raise Exception(f'fal.ai video generation FAILED for request {request_id}')
    raise Exception(f'Video timeout after {timeout_s}s')


def load_video_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    return {}


def save_video_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding='utf-8')


# ── Progress display ───────────────────────────────────────────────────────────
def bar(done, total, width=30):
    filled = int(width * done / total) if total else 0
    return f"[{'█'*filled}{'░'*(width-filled)}] {done}/{total}"


def cprint(msg, color=''):
    codes = {'green':'\033[92m','red':'\033[91m','yellow':'\033[93m','cyan':'\033[96m','reset':'\033[0m','bold':'\033[1m'}
    if color:
        print(f"{codes.get(color,'')}{msg}{codes['reset']}")
    else:
        print(msg)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='Batch generate social media images and videos for RankerToolAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.strip()
    )
    parser.add_argument('platform', help='Platform name or "all"', choices=PLATFORMS+['all'])
    parser.add_argument('--mode',   default='image', choices=['image','video','both'], help='What to generate (default: image)')
    parser.add_argument('--limit',  type=int, default=0, help='Max tools to process per platform (0 = all)')
    parser.add_argument('--delay',  type=float, default=2.5, help='Seconds between image requests (default: 2.5)')
    parser.add_argument('--skip-existing', action='store_true', default=True, help='Skip already-generated files (default: true)')
    parser.add_argument('--force',  action='store_true', help='Re-generate even if file exists')
    parser.add_argument('--kieai-key',      default=os.environ.get('KIE_AI_KEY', ''))
    parser.add_argument('--kieai-endpoint', default=os.environ.get('KIE_AI_ENDPOINT', 'https://api.kie.ai/v1/images/generations'))
    parser.add_argument('--kieai-status',   default=os.environ.get('KIE_AI_STATUS', ''), help='Status polling endpoint with {task_id} placeholder')
    parser.add_argument('--fal-key',        default=os.environ.get('FAL_KEY', ''))
    args = parser.parse_args()

    platforms = PLATFORMS if args.platform == 'all' else [args.platform]
    tools     = TOOLS[:args.limit] if args.limit else TOOLS
    skip      = args.skip_existing and not args.force
    need_kie  = args.mode in ('image', 'both')
    need_fal  = args.mode in ('video', 'both')

    # Collect API keys
    kie_key = args.kieai_key
    fal_key = args.fal_key

    if need_kie and not kie_key:
        kie_key = input('kie.ai API key: ').strip()
    if need_fal and not fal_key:
        fal_key = input('fal.ai API key: ').strip()

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    vid_cache = load_video_cache()

    total = len(tools) * len(platforms)
    done = errors = skipped = 0

    cprint(f'\n  RankerToolAI Batch Generator', 'bold')
    cprint(f'  Mode: {args.mode.upper()}  |  Tools: {len(tools)}  |  Platforms: {len(platforms)}  |  Total: {total}\n', 'cyan')

    for pf in platforms:
        cprint(f'  ── {pf.upper()} ──', 'cyan')

        for tool in tools:
            label = f'{tool["name"]:20s}'

            # ── Image ──
            if need_kie:
                fname  = img_filename(tool, pf)
                fpath  = ASSETS_DIR / fname
                ckey   = f'{tool["slug"]}_{pf}'

                if skip and fpath.exists():
                    cprint(f'  ✓ skip  {label} {fname}', 'green')
                    skipped += 1
                else:
                    print(f'  🎨 gen   {label}', end='', flush=True)
                    try:
                        img_url = generate_image(
                            tool, pf, kie_key,
                            args.kieai_endpoint, args.kieai_status
                        )
                        download(img_url, fpath)
                        cprint(f' ✓  → {fname}', 'green')

                        # If also doing video, stash the URL for video step
                        if need_fal:
                            vid_cache[f'img_url_{ckey}'] = img_url

                    except Exception as e:
                        cprint(f' ✗  {e}', 'red')
                        errors += 1
                    time.sleep(args.delay)

            # ── Video ──
            if need_fal:
                ckey     = f'{tool["slug"]}_{pf}'
                vid_ckey = f'vid_{ckey}'

                if skip and vid_cache.get(vid_ckey):
                    cprint(f'  ✓ skip  {label} (video cached)', 'green')
                    skipped += 1
                else:
                    # Source image: prefer freshly generated URL, else live site
                    img_src = (vid_cache.get(f'img_url_{ckey}') or
                               f'https://rankertoolai.com/assets/images/{img_filename(tool, pf)}')

                    print(f'  🎬 queue {label}', end='', flush=True)
                    try:
                        req_id = queue_video(img_src, pf, fal_key)
                        cprint(f' ⏳ queued ({req_id[:8]}…)', 'yellow')
                        cprint(f'  ⏳ poll  {label}', 'yellow')
                        vid_url = poll_video(req_id, fal_key)
                        vid_cache[vid_ckey] = vid_url
                        save_video_cache(vid_cache)
                        cprint(f'  ✓ video  {label} → {vid_url[:60]}…', 'green')
                    except Exception as e:
                        cprint(f' ✗  {e}', 'red')
                        errors += 1

            done += 1
            print(f'  {bar(done, total)}', end='\r')

        save_video_cache(vid_cache)

    # Final summary
    print(' ' * 60, end='\r')
    cprint(f'\n  Done!', 'bold')
    cprint(f'  ✓ Processed : {done - errors - skipped}', 'green')
    cprint(f'  ↷ Skipped   : {skipped}', 'cyan')
    cprint(f'  ✗ Errors    : {errors}', 'red' if errors else 'green')
    cprint(f'  Images saved → {ASSETS_DIR}', 'cyan')
    if need_fal:
        cprint(f'  Video URLs  → {CACHE_FILE}', 'cyan')

    if need_fal and vid_cache:
        cprint('\n  Import video URLs to dashboard — paste in browser console:', 'yellow')
        lines = []
        for k, v in vid_cache.items():
            if k.startswith('vid_'):
                parts = k[4:].rsplit('_', 1)
                if len(parts) == 2:
                    slug_part, pf_part = parts
                    lines.append(f"localStorage.setItem('rta_vid_{slug_part}_{pf_part}','{v}');")
        if lines:
            console_path = Path(__file__).parent / 'import_videos.js'
            console_path.write_text('\n'.join(lines), encoding='utf-8')
            cprint(f'  JS file: {console_path}', 'cyan')
            cprint('  Open dashboard → F12 → Console → paste contents of import_videos.js', 'yellow')


if __name__ == '__main__':
    main()
