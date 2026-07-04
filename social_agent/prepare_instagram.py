"""
Prepares Instagram content: carousel slides + caption text files.
Run: python prepare_instagram.py
Output: output/instagram/ folder ready to upload
"""

import os, json, shutil
from PIL import Image

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
IG_DIR = os.path.join(OUT_DIR, "instagram")
TOOLS_FILE = os.path.join(os.path.dirname(__file__), "data", "tools.json")

CAPTIONS = {
    "elevenlabs": """We tested 10 AI voice generators. ElevenLabs still wins — by a lot.

Score: 9.2/10 after 30 days of real testing.

What makes it different?
→ Voices that actually fool people (12/15 humans couldn't tell)
→ 99 languages, 1-click voice cloning
→ API that works in production

Free tier: 10,000 characters/month
Paid: from $5/mo

Full review → rankertoolai.com/review/elevenlabs/

#AITools #ElevenLabs #TextToSpeech #AIVoice #ContentCreator #AIProductivity #TechReview #SoftwareReview #AIReview #VoiceAI""",

    "semrush": """The highest-rated AI SEO tool we've tested. 9.3/10.

50 billion keywords. 200+ tools in one platform.
Competitor analysis that's genuinely scary good.

After testing Ahrefs, Moz, and SE Ranking side-by-side for 90 days — Semrush wins on data depth and accuracy.

Is it worth $129/mo? For serious marketers — yes.

Full breakdown → rankertoolai.com/review/semrush/

#SEO #Semrush #DigitalMarketing #AITools #ContentMarketing #SEOTools #Marketing #KeywordResearch #SEOTips #MarketingTools""",

    "cursor": """I switched from VS Code + Copilot to Cursor. Here's what happened.

Score: 9.2/10 — highest we've given any coding tool.

Cursor's Composer wrote 8 files simultaneously for a feature that would've taken me 2 hours. It took 12 minutes.

Autocomplete acceptance rate: 68% (vs 52% with Copilot)

Worth the $20/mo? Absolutely — if you're on VS Code.

Full review → rankertoolai.com/review/cursor/

#Cursor #AICode #Developer #Programming #AITools #CodingTools #WebDev #DevTools #SoftwareDev #AIAssistant""",

    "surfer-seo": """I ran a 90-day SEO experiment. The results:

10 articles WITH Surfer SEO vs 10 WITHOUT it.

With Surfer: 7/10 articles ranked page 1 (avg position 6.2)
Without Surfer: 3/10 articles ranked page 1 (avg position 18.4)

That's 3.2x more organic traffic. Score: 9.0/10.

The secret isn't keyword density — it's the NLP entity analysis.

Full experiment data → rankertoolai.com/review/surfer-seo/

#SurferSEO #SEO #ContentMarketing #Blogging #OrganicTraffic #SEOTips #ContentStrategy #RankOnGoogle #AITools #SEOTools""",

    "jasper": """Best AI writer for marketing teams. Score: 8.9/10.

What Jasper does that others can't:
→ Brand voice training across all content
→ 50+ battle-tested templates
→ Native Surfer SEO integration
→ Team collaboration features

Hallucination rate: ~8% (test everything before publishing)

Full review → rankertoolai.com/review/jasper/

#JasperAI #AIWriting #ContentMarketing #AITools #Marketing #CopywritingTips #ContentCreation #AIWriter #Copywriting #MarketingTools""",

    "stable-diffusion": """The best FREE AI image generator. Score: 8.9/10.

Run it locally: $0/month forever.
Use the API: ~$0.003 per image.

vs Midjourney: Comparable quality, no Discord required, full control.
vs DALL-E 3: Better for photorealistic, cheaper at scale.

The setup takes 2 hours. After that, unlimited images.

Full guide → rankertoolai.com/review/stable-diffusion/

#StableDiffusion #AIArt #AIImage #AITools #DigitalArt #AIArtwork #GenerativeAI #TextToImage #AICreative #OpenSource""",

    "canva-ai": """Canva just became an AI design powerhouse. Score: 8.4/10.

Magic Studio features:
→ Text to Image (surprisingly good)
→ Magic Eraser (background removal in 1 click)
→ Magic Write (AI copywriting built-in)
→ AI Presentations (full decks from a prompt)

If you're not a designer but need design work — this is your tool.

Full review → rankertoolai.com/review/canva-ai/

#Canva #CanvaAI #GraphicDesign #AIDesign #AITools #DesignTools #SocialMedia #ContentCreator #MarketingDesign #VisualContent""",

    "grok": """Grok 3 surprised me. Score: 8.3/10.

What it does better than GPT-4:
→ Real-time data (through X/Twitter — actually useful)
→ No content restrictions on controversial research topics
→ DeepSearch mode rivals Perplexity

Where it still loses:
→ Creative writing (GPT-4 + Claude are better)
→ Long document analysis

Included with X Premium ($8-16/mo). Good value.

Full review → rankertoolai.com/review/grok/

#Grok #GrokAI #AI #ChatGPT #AITools #AIComparison #ArtificialIntelligence #XAI #TechReview #AIAssistant""",

    "runway": """AI video generation in 2026 is actually impressive. Score: 8.5/10.

Runway Gen-3 Alpha generated this 8-second clip:
→ Photorealistic
→ Consistent physics
→ No obvious artifacts

I've seen clips like this end up in actual YouTube channels without disclosure.

Best for: Short clips, B-roll, social media content.
Price: From $12/mo.

Full review → rankertoolai.com/review/runway/

#RunwayML #AIVideo #VideoGeneration #AITools #VideoCreator #ContentCreation #AICreative #GenerativeVideo #TextToVideo #VideoMarketing""",

    "writesonic": """Best value AI writer in 2026. Score: 8.7/10.

$16/mo vs Jasper's $39/mo.
Article quality: ~75% of Jasper at 40% of the price.

Hidden gem: AI Search mode (Chatsonic) is competitive with Perplexity for research.

Best for: Solopreneurs and small teams who need quality AI writing without breaking the budget.

Full review → rankertoolai.com/review/writesonic/

#Writesonic #AIWriting #AITools #ContentMarketing #Copywriting #AIWriter #BloggingTips #ContentCreation #MarketingTools #AIContent"""
}

def prepare():
    os.makedirs(IG_DIR, exist_ok=True)
    tools = json.load(open(TOOLS_FILE, encoding="utf-8"))

    print(f"Preparing Instagram content for {len(tools)} tools...")
    for tool in tools:
        slug = tool["slug"]
        tool_ig_dir = os.path.join(IG_DIR, slug)
        os.makedirs(tool_ig_dir, exist_ok=True)

        # Copy carousel slides
        carousel_dir = os.path.join(OUT_DIR, slug, "carousel")
        if os.path.exists(carousel_dir):
            slides = sorted([f for f in os.listdir(carousel_dir) if f.endswith(".png")])
            for i, slide in enumerate(slides):
                src = os.path.join(carousel_dir, slide)
                dst = os.path.join(tool_ig_dir, f"{i+1:02d}_{slide}")
                shutil.copy2(src, dst)
            print(f"  {tool['name']}: {len(slides)} slides copied")
        else:
            print(f"  {tool['name']}: no carousel found, run content_creator.py first")

        # Write caption
        caption = CAPTIONS.get(slug, f"Review: {tool['name']} — Score {tool['score']}/10\n\nFull review: {tool['url']}")
        caption_path = os.path.join(tool_ig_dir, "caption.txt")
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption)
        print(f"  {tool['name']}: caption saved")

    # Create posting schedule
    schedule_path = os.path.join(IG_DIR, "POSTING_SCHEDULE.txt")
    with open(schedule_path, "w", encoding="utf-8") as f:
        f.write("INSTAGRAM POSTING SCHEDULE\n")
        f.write("=" * 50 + "\n\n")
        f.write("Best times to post: 9am, 12pm, 6pm (your local time)\n")
        f.write("Post 1 carousel every 1-2 days for maximum growth\n\n")
        for i, tool in enumerate(sorted(tools, key=lambda x: -x["score"])):
            f.write(f"Day {i*2+1}: {tool['name']} ({tool['score']}/10)\n")
            f.write(f"  Folder: instagram/{tool['slug']}/\n")
            f.write(f"  Slides: 8 images\n")
            f.write(f"  Caption: instagram/{tool['slug']}/caption.txt\n\n")

    print(f"\nAll Instagram content ready in: output/instagram/")
    print(f"Posting schedule: output/instagram/POSTING_SCHEDULE.txt")
    print(f"\nUpload order (by score):")
    for t in sorted(tools, key=lambda x: -x["score"]):
        print(f"  {t['name']}: {t['score']}/10")

if __name__ == "__main__":
    prepare()
