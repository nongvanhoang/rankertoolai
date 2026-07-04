#!/usr/bin/env python3
"""
Generate professional social media images for RankerToolAI.
Logo badge su dung brand colors chinh thuc cua tung tool.

Formats:
  pin-{slug}.jpg      1000x1500  Pinterest
  ig-{slug}.jpg       1080x1080  Instagram
  yt-{slug}.jpg       1280x720   YouTube + OG
  tt-{slug}.jpg       1080x1920  TikTok

pip install Pillow
"""

import json, sys, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR   = Path(__file__).parent / "html" / "assets" / "images"
LOGO_DIR  = Path(__file__).parent / "html" / "assets" / "logos"
DATA_FILE = Path(__file__).parent / "social_agent" / "data" / "tools.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOGO_DIR.mkdir(parents=True, exist_ok=True)

_logo_cache = {}

def load_logo(slug):
    """Load logo PNG from local cache. Returns PIL RGBA Image or None."""
    if slug in _logo_cache:
        return _logo_cache[slug]
    path = LOGO_DIR / f"{slug}.png"
    if path.exists():
        try:
            img = Image.open(path).convert("RGBA")
            _logo_cache[slug] = img
            return img
        except:
            pass
    _logo_cache[slug] = None
    return None

# ── Brand colors (label, primary, secondary) ──────────────────────────────────
# Sourced from official brand guidelines / website color schemes
BRAND = {
    "chatgpt":          ("GPT",  (16,  163, 127), (10,   105,  82)),
    "claude":           ("Cl",   (196, 126,  60), (140,   80,  30)),
    "midjourney":       ("MJ",   (110,  55, 210), (75,    25, 160)),
    "cursor":           ("Cur",  (24,   36,  70), (10,    20,  50)),
    "semrush":          ("Sem",  (255, 110,   0), (200,   70,   0)),
    "elevenlabs":       ("11L",  (20,   20,  20), (50,    50,  50)),
    "github-copilot":   ("GH",   (36,   41,  46), (24,    28,  33)),
    "perplexity":       ("Ppx",  (32,  178, 170), (18,   120, 115)),
    "jasper":           ("J",    (255,  90,  31), (200,   55,   0)),
    "windsurf":         ("WS",   (0,   102, 255), (0,     60, 200)),
    "stable-diffusion": ("SD",   (139,  92, 246), (90,    50, 200)),
    "canva-ai":         ("Ca",   (0,   196, 204), (0,    140, 148)),
    "grok":             ("X",    (20,   20,  20), (60,    60,  60)),
    "runway":           ("Rw",   (36,   36,  36), (70,    70,  70)),
    "deepseek":         ("DS",   (37,   99, 235), (20,    60, 180)),
    "gemini":           ("G",    (66,  133, 244), (142,   94, 249)),
    "notion":           ("N",    (37,   37,  37), (60,    60,  60)),
    "otter-ai":         ("Ot",   (79,   70, 229), (50,    40, 180)),
    "hubspot":          ("HS",   (255, 122,  89), (220,   80,  40)),
    "surfer-seo":       ("Srf",  (79,   70, 229), (50,    40, 180)),
    "writesonic":       ("Ws",   (168,  85, 247), (120,   50, 200)),
    "copy-ai":          ("Cp",   (99,  102, 241), (60,    65, 200)),
    "adobe-firefly":    ("Af",   (250,  10,  10), (180,    5,   5)),
}

# ── Category accent colors ────────────────────────────────────────────────────
CAT_COLOR = {
    "AI Chatbot":           (99,  102, 241),
    "AI Coding Tool":       (59,  130, 246),
    "AI Coding IDE":        (59,  130, 246),
    "AI Image Generator":   (168,  85, 247),
    "AI Design Tool":       (139,  92, 246),
    "AI Writing Tool":      (34,  197,  94),
    "AI Voice Generator":   (236,  72, 153),
    "AI SEO Tool":          (249, 115,  22),
    "AI SEO Suite":         (249, 115,  22),
    "AI CRM & Marketing":   (20,  184, 166),
    "AI Productivity Tool": (20,  184, 166),
    "AI Video Generator":   (239,  68,  68),
    "AI Search Tool":       (234, 179,   8),
}

ORANGE = (249, 115, 22)
BG     = (8,  12, 24)
CARD   = (15, 23, 42)
DARK   = (6,   9, 18)
WHITE  = (255, 255, 255)
LGRAY  = (148, 163, 184)
DGRAY  = (30,  41,  59)
BORDER = (30,  41,  59)

def accent(tool):
    return CAT_COLOR.get(tool.get("category", ""), ORANGE)

# ── Font loader ───────────────────────────────────────────────────────────────
def load_fonts():
    bold = ["C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf","C:/Windows/Fonts/verdanab.ttf"]
    reg  = ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/calibri.ttf","C:/Windows/Fonts/verdana.ttf"]
    def f(paths, size):
        for p in paths:
            try: return ImageFont.truetype(p, size)
            except: pass
        return ImageFont.load_default()
    return {
        "xxl":  f(bold,96), "xl":  f(bold,72), "lg": f(bold,52),
        "md":   f(bold,38), "sm":  f(bold,28), "xs": f(reg, 24),
        "xxs":  f(reg, 20), "tiny":f(reg, 18), "logo_l": f(bold,60),
        "logo_m": f(bold,48), "logo_s": f(bold,36),
    }

FONTS = load_fonts()

# ── Brand logo badge ──────────────────────────────────────────────────────────
def _draw_colored_circle(draw, slug, cx, cy, circle_r, ac):
    """Fallback: brand-colored gradient circle with text label."""
    info = BRAND.get(slug)
    if info:
        label, p_col, s_col = info
    else:
        label = slug[:2].upper()
        p_col = ac
        r, g, b = ac
        s_col = (max(0, r - 60), max(0, g - 60), max(0, b - 60))

    pr, pg, pb = p_col
    sr, sg, sb = s_col

    # Glow halo
    for i in range(4):
        alpha = 0.04 - i * 0.009
        rr_ = circle_r + 14 - i * 4
        glow_col = (
            int(pr * alpha + BG[0] * (1 - alpha)),
            int(pg * alpha + BG[1] * (1 - alpha)),
            int(pb * alpha + BG[2] * (1 - alpha)),
        )
        draw.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], fill=glow_col)

    # Accent ring
    draw.ellipse(
        [cx - circle_r - 3, cy - circle_r - 3,
         cx + circle_r + 3, cy + circle_r + 3],
        fill=p_col
    )

    # Gradient fill via scanlines
    for row in range(circle_r * 2):
        y_abs = cy - circle_r + row
        t  = row / (circle_r * 2)
        cr = int(pr * (1 - t) + sr * t)
        cg = int(pg * (1 - t) + sg * t)
        cb = int(pb * (1 - t) + sb * t)
        dy   = abs(row - circle_r)
        half = int(math.sqrt(max(0, circle_r ** 2 - dy ** 2)))
        if half > 0:
            draw.line([(cx - half, y_abs), (cx + half, y_abs)], fill=(cr, cg, cb))

    # Glossy highlight
    hi_r = int(circle_r * 0.72)
    hi_c = (min(255, pr + 80), min(255, pg + 80), min(255, pb + 80))
    draw.arc(
        [cx - hi_r, cy - hi_r - int(circle_r * 0.25),
         cx + hi_r, cy + hi_r - int(circle_r * 0.25)],
        210, 330, fill=hi_c, width=3
    )

    # Text label
    if len(label) <= 2:
        lfont = FONTS["logo_l"] if circle_r >= 100 else FONTS["logo_m"]
    else:
        lfont = FONTS["logo_m"] if circle_r >= 100 else FONTS["logo_s"]
    draw.text((cx + 2, cy + 2), label, font=lfont, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy), label, font=lfont, fill=WHITE, anchor="mm")


def _paste_real_logo(base_img, logo_img, cx, cy, circle_r):
    """Paste real logo PNG into a white circle on base_img."""
    size = circle_r * 2

    # --- White circle background ---
    circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circle_draw = ImageDraw.Draw(circle)
    circle_draw.ellipse([0, 0, size, size], fill=(255, 255, 255, 255))

    # --- Subtle shadow ring outside circle ---
    shadow_r = circle_r + 6
    shadow = Image.new("RGBA", (shadow_r * 2, shadow_r * 2), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([0, 0, shadow_r * 2, shadow_r * 2], fill=(0, 0, 0, 60))
    # Paste shadow first (centered on cx, cy)
    sx = cx - shadow_r
    sy = cy - shadow_r
    base_rgba = base_img.convert("RGBA")
    base_rgba.paste(shadow, (sx, sy), shadow)
    base_img.paste(base_rgba.convert("RGB"), (0, 0))

    # --- Fit logo inside circle with padding ---
    pad    = max(16, int(circle_r * 0.22))
    inner  = size - pad * 2

    logo_copy = logo_img.copy()
    logo_copy.thumbnail((inner, inner), Image.LANCZOS)
    lw, lh = logo_copy.size

    # Clip logo to a circle so it fits neatly inside the white ring
    logo_circle = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    logo_mask = Image.new("L", (lw, lh), 0)
    ImageDraw.Draw(logo_mask).ellipse([0, 0, lw, lh], fill=255)
    logo_rgb = logo_copy.convert("RGBA")
    logo_circle.paste(logo_rgb, (0, 0), logo_mask)

    # Compose circular-clipped logo onto white circle
    ox = (size - lw) // 2
    oy = (size - lh) // 2
    circle.paste(logo_circle, (ox, oy), logo_circle)

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)

    # Paste onto base image
    px = cx - circle_r
    py = cy - circle_r
    base_img.paste(circle.convert("RGB"), (px, py), mask)

    # Thin border ring
    overlay = ImageDraw.Draw(base_img)
    overlay.ellipse(
        [cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r],
        outline=(220, 220, 220), width=2
    )


def draw_logo_circle(base_img, slug, cx, cy, circle_r, ac, draw):
    """
    Draw logo badge: real PNG logo if available, otherwise brand-colored badge.
    """
    logo = load_logo(slug)
    if logo:
        _paste_real_logo(base_img, logo, cx, cy, circle_r)
    else:
        _draw_colored_circle(draw, slug, cx, cy, circle_r, ac)


# ── Drawing helpers ───────────────────────────────────────────────────────────
def rr(draw, xy, r=16, fill=None, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def gradient_bg(img, top, bot):
    w, h = img.size
    px   = img.load()
    for y in range(h):
        t = y / h
        px_r = int(top[0] * (1 - t) + bot[0] * t)
        px_g = int(top[1] * (1 - t) + bot[1] * t)
        px_b = int(top[2] * (1 - t) + bot[2] * t)
        for x in range(w):
            px[x, y] = (px_r, px_g, px_b)

def add_dot_grid(draw, w, h, color, spacing=40, radius=1, opacity=0.18):
    """Subtle dot grid texture overlay."""
    r = int(color[0] * opacity + BG[0] * (1 - opacity))
    g = int(color[1] * opacity + BG[1] * (1 - opacity))
    b = int(color[2] * opacity + BG[2] * (1 - opacity))
    for gy in range(spacing // 2, h, spacing):
        for gx in range(spacing // 2, w, spacing):
            draw.ellipse([gx - radius, gy - radius, gx + radius, gy + radius], fill=(r, g, b))

def add_corner_glow(draw, w, h, color, corner="tr"):
    """Large radial glow in corner for depth."""
    r, g, b = color
    if corner == "tr":
        cx, cy = w, 0
    elif corner == "bl":
        cx, cy = 0, h
    else:
        cx, cy = w // 2, h // 2
    for rad in [300, 220, 150, 90]:
        a = 0.025 - rad * 0.00005
        a = max(0.005, a)
        fc = (int(r * a + BG[0] * (1 - a)), int(g * a + BG[1] * (1 - a)), int(b * a + BG[2] * (1 - a)))
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=fc)

def alpha_rect(draw, xy, color, a=0.12):
    r = int(color[0] * a + BG[0] * (1 - a))
    g = int(color[1] * a + BG[1] * (1 - a))
    b = int(color[2] * a + BG[2] * (1 - a))
    draw.rectangle(xy, fill=(r, g, b))

def score_arc(draw, cx, cy, radius, score, ac, thick=16):
    bb  = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.arc(bb, 0, 360, fill=DGRAY, width=thick)
    deg = int(score / 10 * 360)
    draw.arc(bb, -90, -90 + deg, fill=ac, width=thick)

def pill(draw, cx, y, text, font, fg=WHITE, bg=None, px=20, py=9):
    bb     = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0, y0 = cx - tw // 2 - px, y
    x1, y1 = cx + tw // 2 + px, y + th + py * 2
    if bg:
        rr(draw, [x0, y0, x1, y1], r=min(tw, th) // 2 + py, fill=bg)
    draw.text((cx, y + py), text, font=font, fill=fg, anchor="mt")

def txt_c(draw, cx, y, text, font, fill=WHITE):
    draw.text((cx, y), text, font=font, fill=fill, anchor="mt")

def wrap(text, font, draw, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


# ── FORMAT 1 — Pinterest 1000x1500 ───────────────────────────────────────────
def make_pinterest(tool, ac):
    W, H = 1000, 1500
    img  = Image.new("RGB", (W, H), BG)
    gradient_bg(img, DARK, (12, 18, 36))
    draw = ImageDraw.Draw(img)

    r, g, b = ac
    cx = W // 2

    # Dot grid texture across full bg
    add_dot_grid(draw, W, H, ac, spacing=44, radius=1, opacity=0.10)
    # Corner glow top-right
    add_corner_glow(draw, W, H, ac, corner="tr")

    # Top accent bar
    draw.rectangle([0, 0, W, 10], fill=ac)

    # Header label
    rr(draw, [cx - 90, 28, cx + 90, 68], r=20, fill=(r // 5, g // 5, b // 5))
    draw.text((cx, 48), "REVIEW 2026", font=FONTS["xxs"], fill=ac, anchor="mm")
    draw.text((26, 48), "RankerToolAI", font=FONTS["tiny"], fill=DGRAY, anchor="lm")

    # Category
    draw.text((cx, 92), tool.get("category", "AI Tool").upper(),
              font=FONTS["tiny"], fill=LGRAY, anchor="mm")

    # ── Logo badge ────────────────────────────────────────────────────────────
    draw_logo_circle(img, tool["slug"], cx, 270, 110, ac, draw)
    draw = ImageDraw.Draw(img)   # refresh after scanline drawing

    # Tool name
    name  = tool["name"]
    nfont = FONTS["xl"] if len(name) <= 10 else FONTS["lg"]
    draw.text((cx, 410), name, font=nfont, fill=WHITE, anchor="mm")

    # Underline
    nl = int(draw.textlength(name, font=nfont))
    draw.rectangle([cx - nl // 2, 448, cx + nl // 2, 453], fill=ac)

    # Score ring
    score = tool["score"]
    score_arc(draw, cx, 565, 78, score, ac, thick=15)
    draw.text((cx, 543), str(score), font=FONTS["lg"], fill=WHITE, anchor="mm")
    draw.text((cx, 586), "/ 10", font=FONTS["xs"], fill=LGRAY, anchor="mm")

    if score >= 9.0:
        pill(draw, cx, 648, "EDITOR'S CHOICE", FONTS["tiny"],
             fg=ac, bg=(r // 5, g // 5, b // 5), px=16, py=8)
        div_y = 706
    else:
        div_y = 660

    draw.rectangle([60, div_y, W - 60, div_y + 2], fill=BORDER)
    draw.rectangle([cx - 70, div_y, cx + 70, div_y + 2], fill=ac)

    # Tagline
    tlines = wrap(tool.get("tagline", ""), FONTS["xs"], draw, W - 120)
    ty = div_y + 20
    for tl in tlines[:2]:
        draw.text((cx, ty), tl, font=FONTS["xs"], fill=LGRAY, anchor="mt")
        ty += 32

    # Pros
    py_pros = ty + 28
    for pro in tool.get("pros", [])[:3]:
        rr(draw, [62, py_pros, 94, py_pros + 30], r=8, fill=(34, 197, 94))
        draw.text((78, py_pros + 15), "+", font=FONTS["xs"], fill=DARK, anchor="mm")
        plines = wrap(pro, FONTS["xs"], draw, W - 130)
        draw.text((106, py_pros), plines[0], font=FONTS["xs"], fill=WHITE, anchor="lt")
        if len(plines) > 1:
            draw.text((106, py_pros + 27), plines[1], font=FONTS["xxs"], fill=LGRAY, anchor="lt")
            py_pros += 28
        py_pros += 46

    # Con
    if tool.get("cons"):
        rr(draw, [62, py_pros, 94, py_pros + 30], r=8, fill=(239, 68, 68))
        draw.text((78, py_pros + 15), "-", font=FONTS["xs"], fill=WHITE, anchor="mm")
        draw.text((106, py_pros), tool["cons"][0][:55], font=FONTS["xs"], fill=LGRAY, anchor="lt")
        py_pros += 52

    draw.rectangle([60, py_pros, W - 60, py_pros + 2], fill=BORDER)

    # Price box
    px2 = py_pros + 18
    alpha_rect(draw, [60, px2, W - 60, px2 + 95], ac, 0.10)
    rr(draw, [60, px2, W - 60, px2 + 95], r=12, outline=BORDER, width=1)
    draw.text((cx, px2 + 16), "PRICING", font=FONTS["tiny"], fill=LGRAY, anchor="mt")
    draw.text((cx, px2 + 44), tool.get("price", "See review"), font=FONTS["sm"], fill=WHITE, anchor="mt")

    # Best for
    bf   = tool.get("best_for", "")
    bls  = wrap(bf, FONTS["xxs"], draw, W - 120)
    bfy  = px2 + 130
    draw.text((cx, bfy), "BEST FOR", font=FONTS["tiny"], fill=LGRAY, anchor="mt")
    bfy += 24
    for bl in bls[:2]:
        draw.text((cx, bfy), bl, font=FONTS["xxs"], fill=LGRAY, anchor="mt")
        bfy += 26

    # Footer
    draw.rectangle([0, H - 82, W, H - 80], fill=ac)
    draw.rectangle([0, H - 80, W, H], fill=DARK)
    slug = tool["slug"]
    draw.text((cx, H - 40), f"rankertoolai.com/review/{slug}/",
              font=FONTS["xxs"], fill=WHITE, anchor="mm")

    out = OUT_DIR / f"pin-{slug}.jpg"
    img.save(out, "JPEG", quality=94, optimize=True)
    return out


# ── FORMAT 2 — YouTube thumbnail 1280x720 ─────────────────────────────────────
def make_youtube(tool, ac):
    W, H = 1280, 720
    img  = Image.new("RGB", (W, H), BG)
    gradient_bg(img, DARK, (10, 14, 28))
    draw = ImageDraw.Draw(img)

    r, g, b = ac
    cx_r = W - 220

    # Dot grid texture
    add_dot_grid(draw, W, H, ac, spacing=50, radius=1, opacity=0.08)
    # Right glow
    for rad in [340, 270, 200]:
        alpha_rect(draw, [cx_r - rad, H // 2 - rad,
                          cx_r + rad, H // 2 + rad], ac, 0.04)

    draw.rectangle([0, 0, 8, H], fill=ac)

    # ── Logo badge — left ─────────────────────────────────────────────────────
    draw_logo_circle(img, tool["slug"], 160, H // 2 - 60, 100, ac, draw)
    draw = ImageDraw.Draw(img)

    # Category badge
    lx = 290
    rr(draw, [lx, 60, lx + 200, 98], r=18, fill=(r // 5, g // 5, b // 5))
    draw.text((lx + 100, 79), tool.get("category", "AI Tool").upper(),
              font=FONTS["tiny"], fill=ac, anchor="mm")

    name  = tool["name"]
    nfont = (FONTS["xxl"] if len(name) <= 8
             else FONTS["xl"] if len(name) <= 13
             else FONTS["lg"])
    draw.text((lx, 120), name, font=nfont, fill=WHITE, anchor="lt")
    nl = int(draw.textlength(name, font=nfont))
    draw.rectangle([lx, 125 + nfont.size, lx + nl, 130 + nfont.size], fill=ac)

    draw.text((lx, 235), "HONEST REVIEW 2026", font=FONTS["sm"], fill=LGRAY, anchor="lt")
    draw.text((lx, 288), tool.get("tagline", "")[:68], font=FONTS["xs"], fill=LGRAY, anchor="lt")

    py = 340
    for pro in tool.get("pros", [])[:3]:
        draw.text((lx, py), f"+ {pro[:55]}", font=FONTS["xxs"], fill=LGRAY, anchor="lt")
        py += 30

    rr(draw, [lx, py + 10, lx + 300, py + 52], r=10, fill=DGRAY)
    draw.text((lx + 14, py + 31), f"From: {tool.get('price', '')[:30]}",
              font=FONTS["xxs"], fill=WHITE, anchor="lm")

    draw.text((lx, H - 44), "rankertoolai.com", font=FONTS["xs"], fill=ac, anchor="lt")

    # Score ring — right
    score = tool["score"]
    score_arc(draw, cx_r, H // 2, 125, score, ac, thick=22)
    draw.text((cx_r, H // 2 - 22), str(score), font=FONTS["xxl"], fill=WHITE, anchor="mm")
    draw.text((cx_r, H // 2 + 48), "/ 10",     font=FONTS["md"],  fill=LGRAY, anchor="mm")
    draw.text((cx_r, H // 2 + 106), "SCORE",   font=FONTS["tiny"], fill=LGRAY, anchor="mm")

    stars = round(score / 2)
    draw.text((cx_r, H // 2 + 150), "★" * stars + "☆" * (5 - stars),
              font=FONTS["sm"], fill=ac, anchor="mm")

    slug = tool["slug"]
    out  = OUT_DIR / f"yt-{slug}.jpg"
    img.save(out, "JPEG", quality=94, optimize=True)
    og = img.resize((1200, 630), Image.LANCZOS)
    og.save(OUT_DIR / f"og-review-{slug}.jpg", "JPEG", quality=92)
    return out


# ── FORMAT 3 — Instagram 1080x1080 ───────────────────────────────────────────
def make_instagram(tool, ac):
    W, H = 1080, 1080
    img  = Image.new("RGB", (W, H), BG)
    gradient_bg(img, (8, 12, 24), (12, 18, 36))
    draw = ImageDraw.Draw(img)

    r, g, b = ac
    cx = W // 2

    # Dot grid texture
    add_dot_grid(draw, W, H, ac, spacing=48, radius=1, opacity=0.09)
    add_corner_glow(draw, W, H, ac, corner="bl")

    draw.rectangle([0, 0, 8, H], fill=ac)

    # Category pill
    rr(draw, [cx - 130, 38, cx + 130, 80], r=20, fill=(r // 5, g // 5, b // 5))
    draw.text((cx, 59), tool.get("category", "AI Tool").upper(),
              font=FONTS["xxs"], fill=ac, anchor="mm")

    # ── Logo badge ────────────────────────────────────────────────────────────
    draw_logo_circle(img, tool["slug"], cx, 240, 110, ac, draw)
    draw = ImageDraw.Draw(img)

    name  = tool["name"]
    nfont = FONTS["xl"] if len(name) <= 10 else FONTS["lg"]
    draw.text((cx, 382), name, font=nfont, fill=WHITE, anchor="mm")

    score = tool["score"]
    score_arc(draw, cx, 530, 88, score, ac, thick=18)
    draw.text((cx, 507), str(score), font=FONTS["lg"], fill=WHITE, anchor="mm")
    draw.text((cx, 554), "/ 10",     font=FONTS["xs"], fill=LGRAY, anchor="mm")

    if score >= 9.0:
        pill(draw, cx, 632, "EDITOR'S CHOICE", FONTS["xxs"],
             fg=ac, bg=(r // 5, g // 5, b // 5), px=20, py=10)
        py = 690
    else:
        py = 650

    draw.rectangle([100, py, W - 100, py + 1], fill=BORDER)
    draw.rectangle([cx - 80, py, cx + 80, py + 1], fill=ac)
    py += 22

    for pro in tool.get("pros", [])[:2]:
        rr(draw, [102, py, 138, py + 30], r=8, fill=(34, 197, 94))
        draw.text((120, py + 15), "+", font=FONTS["xs"], fill=DARK, anchor="mm")
        draw.text((152, py + 4), pro[:44], font=FONTS["xxs"], fill=LGRAY, anchor="lt")
        py += 46

    rr(draw, [102, py + 10, W - 102, py + 52], r=10, fill=DGRAY)
    draw.text((cx, py + 31), tool.get("price", "See review"),
              font=FONTS["xs"], fill=WHITE, anchor="mm")

    draw.rectangle([0, H - 68, W, H - 66], fill=ac)
    draw.rectangle([0, H - 66, W, H], fill=DARK)
    draw.text((cx, H - 33), f"rankertoolai.com/review/{tool['slug']}/",
              font=FONTS["xxs"], fill=WHITE, anchor="mm")

    out = OUT_DIR / f"ig-{tool['slug']}.jpg"
    img.save(out, "JPEG", quality=94, optimize=True)
    return out


# ── FORMAT 4 — TikTok 1080x1920 ──────────────────────────────────────────────
def make_tiktok(tool, ac):
    W, H = 1080, 1920
    img  = Image.new("RGB", (W, H), BG)
    gradient_bg(img, DARK, (8, 12, 28))
    draw = ImageDraw.Draw(img)

    r, g, b = ac
    cx = W // 2

    # Dot grid texture
    add_dot_grid(draw, W, H, ac, spacing=52, radius=1, opacity=0.09)

    for rad in [500, 420, 340, 260]:
        alpha_rect(draw, [cx - rad, H // 2 - rad,
                          cx + rad, H // 2 + rad], ac, 0.03)

    draw.rectangle([0, 0, W, 10], fill=ac)
    draw.text((cx, 58),  "WATCH TO LEARN", font=FONTS["xxs"], fill=LGRAY, anchor="mm")
    draw.text((cx, 100), tool.get("category", "AI Tool").upper(),
              font=FONTS["sm"], fill=ac, anchor="mm")

    # ── Logo badge ────────────────────────────────────────────────────────────
    draw_logo_circle(img, tool["slug"], cx, 420, 155, ac, draw)
    draw = ImageDraw.Draw(img)

    name  = tool["name"]
    nfont = FONTS["xxl"] if len(name) <= 8 else FONTS["xl"]
    draw.text((cx, 640), name, font=nfont, fill=WHITE, anchor="mm")
    nl = int(draw.textlength(name, font=nfont))
    draw.rectangle([cx - nl // 2, 694, cx + nl // 2, 701], fill=ac)

    score = tool["score"]
    score_arc(draw, cx, 890, 120, score, ac, thick=22)
    draw.text((cx, 860), str(score), font=FONTS["xxl"], fill=WHITE, anchor="mm")
    draw.text((cx, 944), "/ 10",    font=FONTS["lg"],  fill=LGRAY, anchor="mm")

    draw.text((cx, 1060), "HONEST REVIEW", font=FONTS["lg"], fill=WHITE, anchor="mm")
    draw.rectangle([100, 1118, W - 100, 1120], fill=BORDER)
    draw.rectangle([cx - 100, 1118, cx + 100, 1120], fill=ac)

    py = 1145
    for pro in tool.get("pros", [])[:3]:
        rr(draw, [cx - 440, py, cx - 402, py + 36], r=8, fill=(34, 197, 94))
        draw.text((cx - 421, py + 18), "+", font=FONTS["xs"], fill=DARK, anchor="mm")
        draw.text((cx - 390, py + 4), pro[:40], font=FONTS["xs"], fill=LGRAY, anchor="lt")
        py += 56

    rr(draw, [100, 1460, W - 100, 1540], r=20, fill=(r // 4, g // 4, b // 4))
    draw.text((cx, 1500), "LINK IN BIO -> FULL REVIEW",
              font=FONTS["sm"], fill=ac, anchor="mm")

    rr(draw, [200, 1560, W - 200, 1615], r=14, fill=DGRAY)
    draw.text((cx, 1587), f"Price: {tool.get('price', '')}",
              font=FONTS["xs"], fill=WHITE, anchor="mm")

    draw.text((cx, H - 150), "Follow for more AI reviews",
              font=FONTS["xs"], fill=LGRAY, anchor="mm")
    draw.text((cx, H - 108), "@rankertoolai",
              font=FONTS["md"], fill=ac, anchor="mm")

    draw.rectangle([0, H - 66, W, H - 64], fill=ac)
    draw.rectangle([0, H - 64, W, H], fill=DARK)
    draw.text((cx, H - 32), "rankertoolai.com",
              font=FONTS["xs"], fill=WHITE, anchor="mm")

    out = OUT_DIR / f"tt-{tool['slug']}.jpg"
    img.save(out, "JPEG", quality=94, optimize=True)
    return out


# ── Default OG image ──────────────────────────────────────────────────────────
def make_default():
    W, H = 1200, 630
    img  = Image.new("RGB", (W, H), BG)
    gradient_bg(img, DARK, (10, 14, 28))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=ORANGE)
    draw.rectangle([0, H - 8, W, H], fill=ORANGE)
    cx = W // 2

    for rad in [280, 220, 160]:
        alpha_rect(draw, [cx - rad, H // 2 - rad,
                          cx + rad, H // 2 + rad], ORANGE, 0.04)

    rr(draw, [80, 50, W - 80, H - 50], r=20, fill=CARD)

    rr(draw, [cx - 64, 80, cx + 64, 120], r=20,
       fill=(ORANGE[0] // 5, ORANGE[1] // 5, ORANGE[2] // 5))
    draw.text((cx, 100), "AI TOOLS", font=FONTS["xxs"], fill=ORANGE, anchor="mm")

    draw.text((cx, 188), "RankerToolAI", font=FONTS["xl"], fill=WHITE, anchor="mm")
    draw.text((cx, 274), "AI Tools, Ranked & Reviewed", font=FONTS["sm"], fill=LGRAY, anchor="mm")

    draw.rectangle([cx - 180, 318, cx + 180, 320], fill=BORDER)
    draw.rectangle([cx - 60,  318, cx + 60,  320], fill=ORANGE)

    for i, (num, lab) in enumerate([("50+", "Tools Tested"), ("9.2", "Top Score"), ("0", "Paid Placements")]):
        sx = 240 + i * 360
        draw.text((sx, 368), num, font=FONTS["lg"], fill=ORANGE, anchor="mm")
        draw.text((sx, 422), lab, font=FONTS["xxs"], fill=LGRAY, anchor="mm")

    draw.rectangle([80, H - 98, W - 80, H - 96], fill=BORDER)
    draw.text((cx, H - 58), "rankertoolai.com", font=FONTS["sm"], fill=ORANGE, anchor="mm")

    out = OUT_DIR / "og-default.jpg"
    img.save(out, "JPEG", quality=94, optimize=True)
    print("  done  og-default.jpg")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating branded social media images...\n")
    with open(DATA_FILE, encoding="utf-8") as f:
        tools = json.load(f)

    make_default()

    counts = {"pin": 0, "ig": 0, "yt": 0, "tt": 0}
    for t in tools:
        ac   = accent(t)
        slug = t["slug"]
        make_pinterest(t, ac); counts["pin"] += 1
        make_instagram(t, ac); counts["ig"]  += 1
        make_youtube(t, ac);   counts["yt"]  += 1
        make_tiktok(t, ac);    counts["tt"]  += 1
        print(f"  done  {slug}")

    total = 1 + sum(counts.values())
    print(f"\nDone! {total} images -> {OUT_DIR}")

if __name__ == "__main__":
    main()
