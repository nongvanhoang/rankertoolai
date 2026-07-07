"""
RankerToolAI Content Creator
Creates images (carousels) and videos for all social platforms.

Usage:
  python content_creator.py --tool elevenlabs --type carousel
  python content_creator.py --tool surfer-seo --type video
  python content_creator.py --all
"""

import os
import sys
import json
import subprocess
import argparse
from PIL import Image, ImageDraw, ImageFont
import textwrap

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")

# Colors
BG_DARK    = (8, 12, 24)
BG_CARD    = (15, 24, 48)
ORANGE     = (249, 115, 22)
ORANGE2    = (251, 191, 36)
GREEN      = (34, 197, 94)
WHITE      = (255, 255, 255)
GRAY       = (160, 170, 190)
GRAY_DIM   = (80, 90, 110)

def load_tools():
    with open(TOOLS_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_font(size, bold=False):
    """Try to load a system font, fall back to default."""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    x0,y0,x1,y1 = xy
    draw.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=fill,
                           outline=outline, width=outline_width)

def gradient_text(img, draw, text, pos, font, color1, color2, direction="h"):
    """Simulate gradient text by drawing colored version."""
    # Simple: use color1 for now (true gradient needs per-pixel)
    draw.text(pos, text, font=font, fill=color1)

# ─────────────────────────────────────────────
# CAROUSEL (Instagram — 10 slides 1080x1080)
# ─────────────────────────────────────────────

def make_carousel(tool):
    slug = tool["slug"]
    out = os.path.join(OUT_DIR, slug, "carousel")
    os.makedirs(out, exist_ok=True)

    slides = [
        {"type": "cover",   "data": tool},
        {"type": "score",   "data": tool},
        {"type": "pros",    "data": tool},
        {"type": "cons",    "data": tool},
        {"type": "pricing", "data": tool},
        {"type": "bestfor", "data": tool},
        {"type": "tip",     "data": tool},
        {"type": "verdict", "data": tool},
    ]

    paths = []
    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide_{i+1:02d}_{slide['type']}.png")
        fn = globals().get(f"slide_{slide['type']}", slide_generic)
        fn(slide["data"], path, i+1, len(slides))
        paths.append(path)
        print(f"  [carousel] {slug} slide {i+1}/{len(slides)}: {slide['type']}")

    return paths

def _base_img():
    img = Image.new("RGB", (1080, 1080), BG_DARK)
    draw = ImageDraw.Draw(img)
    # Dot grid
    for x in range(0, 1080, 54):
        for y in range(0, 1080, 54):
            draw.ellipse([x-1,y-1,x+1,y+1], fill=(249,115,22,15))
    # Orange top bar
    draw.rectangle([0,0,1080,7], fill=ORANGE)
    return img, draw

def _footer(draw, page, total):
    draw.rectangle([0, 980, 1080, 1080], fill=(5,8,18))
    draw.rectangle([0, 980, 1080, 984], fill=ORANGE)
    f = get_font(22)
    draw.text((60, 1020), "rankertoolai.com", font=f, fill=ORANGE)
    draw.text((900, 1020), f"{page} / {total}", font=f, fill=GRAY_DIM)

def slide_cover(tool, path, page, total):
    img, draw = _base_img()
    # Big score badge
    draw.ellipse([760, 200, 1000, 440], fill=(20,30,60))
    draw.ellipse([764, 204, 996, 436], outline=ORANGE, width=4)
    sf = get_font(110, bold=True)
    draw.text((780, 220), str(tool["score"]), font=sf, fill=ORANGE)
    draw.text((800, 360), "/10", font=get_font(36), fill=GRAY)

    # Category
    draw_rounded_rect(draw, [60,100,400,150], 8, (40,20,5))
    draw.text((80, 110), tool["category"].upper(), font=get_font(24, bold=True), fill=ORANGE)

    # Tool name
    nf = get_font(96 if len(tool["name"]) < 10 else 72, bold=True)
    draw.text((60, 180), tool["name"], font=nf, fill=WHITE)

    # Tagline
    tf = get_font(34)
    for i, line in enumerate(textwrap.wrap(tool["tagline"], 28)):
        draw.text((60, 380 + i*50), line, font=tf, fill=GRAY)

    # Swipe hint
    draw.text((60, 880), "Swipe to see full review →", font=get_font(28), fill=GRAY_DIM)
    _footer(draw, page, total)
    img.save(path)

def slide_score(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "OVERALL SCORE", font=get_font(32, bold=True), fill=ORANGE)

    # Big score
    draw.ellipse([340, 180, 740, 580], fill=(15,24,48))
    draw.ellipse([344, 184, 736, 576], outline=ORANGE, width=6)
    draw.text((390, 230), str(tool["score"]), font=get_font(160, bold=True), fill=ORANGE)
    draw.text((430, 430), "OUT OF 10", font=get_font(32), fill=GRAY)

    # Stars
    stars = round(tool["score"] / 2)
    sx = 290
    for i in range(5):
        clr = ORANGE if i < stars else GRAY_DIM
        draw.text((sx + i*100, 610), "★", font=get_font(80, bold=True), fill=clr)

    draw.text((60, 730), f"Tested by RankerToolAI team", font=get_font(28), fill=GRAY)
    draw.text((60, 775), f"30+ days real-world testing", font=get_font(28), fill=GRAY)
    draw.text((60, 840), f"Category: {tool['category']}", font=get_font(26), fill=GRAY_DIM)
    _footer(draw, page, total)
    img.save(path)

def slide_pros(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "WHAT WE LOVED", font=get_font(42, bold=True), fill=GREEN)

    y = 180
    for i, pro in enumerate(tool["pros"]):
        draw_rounded_rect(draw, [60, y, 1020, y+90], 12, (10,35,20))
        draw.ellipse([80,y+22,126,y+68], fill=GREEN)
        draw.text((92, y+28), "✓", font=get_font(30, bold=True), fill=(5,8,18))
        for j, line in enumerate(textwrap.wrap(pro, 38)):
            draw.text((150, y+20+j*32), line, font=get_font(30), fill=WHITE)
        y += 110

    _footer(draw, page, total)
    img.save(path)

def slide_cons(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "WHAT COULD BE BETTER", font=get_font(38, bold=True), fill=(251,191,36))

    y = 180
    for con in tool["cons"]:
        draw_rounded_rect(draw, [60, y, 1020, y+90], 12, (35,25,5))
        draw.ellipse([80,y+22,126,y+68], fill=(251,191,36))
        draw.text((88, y+26), "!", font=get_font(32, bold=True), fill=(5,8,18))
        for j, line in enumerate(textwrap.wrap(con, 38)):
            draw.text((150, y+20+j*32), line, font=get_font(30), fill=WHITE)
        y += 110

    _footer(draw, page, total)
    img.save(path)

def slide_pricing(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "PRICING", font=get_font(56, bold=True), fill=ORANGE)

    draw_rounded_rect(draw, [60,180,1020,380], 16, (15,24,48), ORANGE, 2)
    draw.text((80, 210), tool["price"], font=get_font(40, bold=True), fill=WHITE)
    draw.text((80, 280), "→ Free trial available in most plans", font=get_font(28), fill=GRAY)
    draw.text((80, 325), "→ Cancel anytime", font=get_font(28), fill=GRAY)

    draw.text((60, 430), "IS IT WORTH IT?", font=get_font(36, bold=True), fill=GREEN)
    draw_rounded_rect(draw, [60,490,1020,720], 16, (10,30,15))
    worth = f"At {tool['score']}/10, {tool['name']} offers strong value for {tool['best_for'].split(',')[0].lower()}."
    for i, line in enumerate(textwrap.wrap(worth, 36)):
        draw.text((80, 510+i*50), line, font=get_font(34), fill=WHITE)

    _footer(draw, page, total)
    img.save(path)

def slide_bestfor(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "BEST FOR", font=get_font(56, bold=True), fill=ORANGE)

    draw_rounded_rect(draw, [60,170,1020,500], 16, (15,24,48), ORANGE, 2)
    for i, line in enumerate(textwrap.wrap(tool["best_for"], 32)):
        draw.text((80, 190+i*60), line, font=get_font(42, bold=True), fill=WHITE)

    draw.text((60, 560), "NOT IDEAL FOR:", font=get_font(32, bold=True), fill=GRAY)
    draw_rounded_rect(draw, [60,610,1020,760], 16, (20,15,25))
    draw.text((80, 630), "→ Casual / hobby use", font=get_font(30), fill=GRAY)
    draw.text((80, 680), "→ Very tight budgets", font=get_font(30), fill=GRAY)

    _footer(draw, page, total)
    img.save(path)

def slide_tip(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "PRO TIP", font=get_font(56, bold=True), fill=GREEN)
    draw.text((60, 155), f"Get the most out of {tool['name']}", font=get_font(30), fill=GRAY)

    tip = f"Start with the free tier to test quality, then upgrade once you've validated your workflow. Most power users save 2-4 hours/week after integrating {tool['name']} into their process."
    draw_rounded_rect(draw, [60,220,1020,620], 16, (10,30,15))
    for i, line in enumerate(textwrap.wrap(tip, 35)):
        draw.text((80, 245+i*58), line, font=get_font(36), fill=WHITE)

    draw.text((60, 680), "USED BY:", font=get_font(32, bold=True), fill=GRAY_DIM)
    roles = ["Content Creators", "Marketing Teams", "Developers", "Agencies"]
    for i, role in enumerate(roles):
        col = i % 2
        row = i // 2
        draw_rounded_rect(draw, [60+col*490, 730+row*90, 540+col*490, 810+row*90], 10, (20,30,50))
        draw.text((80+col*490, 748+row*90), f"→ {role}", font=get_font(28), fill=WHITE)

    _footer(draw, page, total)
    img.save(path)

def slide_verdict(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 80), "FINAL VERDICT", font=get_font(48, bold=True), fill=ORANGE)

    draw.ellipse([340, 170, 740, 570], fill=(15,24,48))
    draw.ellipse([344, 174, 736, 566], outline=ORANGE, width=5)
    draw.text((376, 210), str(tool["score"]), font=get_font(165, bold=True), fill=ORANGE)
    draw.text((415, 445), "/10", font=get_font(40), fill=GRAY)

    rec = "RECOMMENDED" if tool["score"] >= 8.5 else "WORTH TRYING"
    rclr = GREEN if tool["score"] >= 8.5 else ORANGE
    draw_rounded_rect(draw, [200, 610, 880, 690], 30, (10,35,20) if tool["score"] >= 8.5 else (35,20,5))
    draw.text((260, 622), f"✓ {rec}", font=get_font(40, bold=True), fill=rclr)

    draw.text((60, 740), "Full review + affiliate link:", font=get_font(26), fill=GRAY)
    draw.text((60, 780), tool["url"], font=get_font(28, bold=True), fill=ORANGE)

    draw.text((60, 870), "Follow @rankertoolai for more reviews", font=get_font(26), fill=GRAY_DIM)
    _footer(draw, page, total)
    img.save(path)

def slide_generic(tool, path, page, total):
    img, draw = _base_img()
    draw.text((60, 200), tool["name"], font=get_font(72, bold=True), fill=WHITE)
    _footer(draw, page, total)
    img.save(path)

# ─────────────────────────────────────────────
# VIDEO (MP4 slideshow with ffmpeg)
# ─────────────────────────────────────────────

def make_video(tool, carousel_paths=None):
    slug = tool["slug"]
    out_dir = os.path.join(OUT_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    if not carousel_paths:
        carousel_paths = make_carousel(tool)

    # Create 16:9 versions for YouTube/TikTok
    video_frames_dir = os.path.join(out_dir, "video_frames")
    os.makedirs(video_frames_dir, exist_ok=True)

    frame_paths = []
    for i, src in enumerate(carousel_paths):
        img = Image.open(src)
        # Convert 1:1 to 9:16 (1080x1920) for TikTok/Reels
        canvas = Image.new("RGB", (1080, 1920), BG_DARK)
        # Center the 1080x1080 square
        canvas.paste(img, (0, 420))
        # Add top/bottom branding
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([0,0,1080,420], fill=(5,8,18))
        draw.rectangle([0,0,1080,7], fill=ORANGE)
        draw.text((60, 170), "RankerTool AI", font=get_font(64, bold=True), fill=ORANGE)
        draw.text((60, 250), "Independent AI Tool Reviews", font=get_font(32), fill=GRAY)
        draw.rectangle([0,1500,1080,1920], fill=(5,8,18))
        draw.rectangle([0,1500,1080,1506], fill=ORANGE)
        draw.text((60, 1560), "Follow for more AI tool reviews", font=get_font(36), fill=WHITE)
        draw.text((60, 1620), "@rankertoolai", font=get_font(44, bold=True), fill=ORANGE)
        draw.text((60, 1700), "rankertoolai.com", font=get_font(36), fill=GRAY)

        frame_path = os.path.join(video_frames_dir, f"frame_{i:02d}.png")
        canvas.save(frame_path)
        frame_paths.append(frame_path)

    # Build video with ffmpeg (3 seconds per slide)
    ffmpeg_path = _find_ffmpeg()
    if not ffmpeg_path:
        print("[Video] ffmpeg not found in PATH, restart terminal and try again")
        return None

    list_file = os.path.join(video_frames_dir, "frames.txt")
    with open(list_file, "w") as f:
        for fp in frame_paths:
            f.write(f"file '{fp}'\n")
            f.write("duration 3\n")
        # repeat last frame
        f.write(f"file '{frame_paths[-1]}'\n")

    output_video = os.path.join(out_dir, f"{slug}_tiktok.mp4")
    cmd = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-vf", "scale=1080:1920:flags=lanczos,fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", output_video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[Video] TikTok/Reels video: {output_video}")
    else:
        print(f"[Video] ffmpeg error: {result.stderr[-200:]}")
        return None

    # Also make 16:9 YouTube version
    yt_dir = os.path.join(out_dir, "yt_frames")
    os.makedirs(yt_dir, exist_ok=True)
    yt_frames = []
    for i, src in enumerate(carousel_paths):
        img = Image.open(src).resize((1080, 1080))
        canvas = Image.new("RGB", (1920, 1080), BG_DARK)
        canvas.paste(img, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([1080,0,1920,1080], fill=(5,8,18))
        draw.rectangle([1080,0,1086,1080], fill=ORANGE)
        draw.text((1110, 200), "RankerTool AI", font=get_font(48, bold=True), fill=ORANGE)
        draw.text((1110, 270), tool["name"], font=get_font(52, bold=True), fill=WHITE)
        draw.text((1110, 350), f"Score: {tool['score']}/10", font=get_font(40, bold=True), fill=ORANGE)
        draw.text((1110, 650), "rankertoolai.com", font=get_font(30), fill=GRAY)
        fp = os.path.join(yt_dir, f"frame_{i:02d}.png")
        canvas.save(fp)
        yt_frames.append(fp)

    yt_list = os.path.join(yt_dir, "frames.txt")
    with open(yt_list, "w") as f:
        for fp in yt_frames:
            f.write(f"file '{fp}'\n")
            f.write("duration 4\n")
        f.write(f"file '{yt_frames[-1]}'\n")

    yt_video = os.path.join(out_dir, f"{slug}_youtube.mp4")
    cmd2 = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
        "-i", yt_list,
        "-vf", "scale=1920:1080:flags=lanczos,fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", yt_video
    ]
    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    if result2.returncode == 0:
        print(f"[Video] YouTube video: {yt_video}")

    return output_video

def _find_ffmpeg():
    import shutil, glob as _glob
    p = shutil.which("ffmpeg")
    if p:
        return p
    common = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    ]
    for c in common:
        if os.path.exists(c):
            return c
    winget_base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    matches = _glob.glob(os.path.join(winget_base, "Gyan.FFmpeg*", "**", "ffmpeg.exe"), recursive=True)
    if matches:
        return matches[0]
    return None

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", help="Tool slug")
    parser.add_argument("--type", choices=["carousel","video","all"], default="all")
    parser.add_argument("--all", action="store_true", help="Create for all tools")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    tools = load_tools()

    targets = tools if args.all else [t for t in tools if t["slug"] == args.tool]
    if not targets:
        print(f"Tool not found: {args.tool}")
        return

    for tool in targets:
        print(f"\nCreating content for: {tool['name']}")
        slides = None
        if args.type in ["carousel", "all"]:
            slides = make_carousel(tool)
            print(f"  Carousel: {len(slides)} slides -> output/{tool['slug']}/carousel/")
        if args.type in ["video", "all"]:
            make_video(tool, slides)

    print(f"\nAll content saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
