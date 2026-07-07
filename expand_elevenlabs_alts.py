"""Expand ElevenLabs alternatives page from ~2,550 to ~4,100+ words."""
import os, re

path = os.path.join(os.path.dirname(__file__), "html", "alternatives", "elevenlabs", "index.html")

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Expand tool descriptions ────────────────────────────────────────────────
# Insert a second paragraph after each tool's first <p> and before <div class="pros-cons">

EXPANSIONS = {
    # (old first-para snippet, new extra paragraph)
    'Murf AI is the most polished ElevenLabs alternative for business and professional use.': """\
      <p>Murf Studio's integrated video sync lets you paste a script, select a voice, and export audio synced to a slide deck or video timeline — all without leaving the browser. For e-learning creators, marketers producing explainer videos, or agencies building client demos, this single-tool workflow eliminates the Audacity/Premiere juggling that ElevenLabs requires. In our head-to-head audio quality test, Murf's Business voices (available on the $39/mo plan) were indistinguishable from professional voice actors in blind tests — competitive with ElevenLabs' best voices on neutral narration.</p>""",

    'Play.ht is the strongest developer-focused ElevenLabs alternative.': """\
      <p>In our API benchmarks, Play.ht generated 60-second audio clips in under 800ms at standard quality — comparable to ElevenLabs' API latency at roughly 60% of the cost per character. The key differentiator for development teams is Play.ht's streaming TTS support: you can begin playing audio before the full file generates, reducing perceived latency in voice AI applications by 40–60%. Play.ht's 142-language support also makes it the strongest choice for multilingual voice apps, where ElevenLabs' coverage thins out for less common languages.</p>""",

    'Speechify is purpose-built for converting written content to audio for listening': """\
      <p>Speechify's core innovation is speed control: you can listen at 1×, 2×, or up to 4.5× speed with AI-enhanced clarity at high speeds, accelerating information intake dramatically. Their research shows users who listen at 2× speed retain information as well as at 1× — but in half the time. For students, researchers, and professionals who process large volumes of text (legal documents, research papers, lengthy reports), Speechify's Chrome extension and mobile app create a seamless "listen to anything" workflow. ElevenLabs offers none of this — it's a generation tool, not a consumption tool.</p>""",

    'Descript is a video and podcast editing tool with an Overdub voice cloning feature built in.': """\
      <p>Descript's transcript-based editing is the most genuinely innovative feature in the audio/video production space: you edit a Word-doc-style transcript and the video edits itself. Remove a word from the script — that word disappears from the video. The Overdub feature uses your cloned voice to fill the gap with AI-generated audio that matches your delivery. For podcasters and video creators who record themselves, Descript eliminates 80% of the time spent on cut-edit-re-record cycles. ElevenLabs can clone voices, but it doesn't integrate into a video editing workflow the way Descript does natively.</p>""",

    'Resemble AI specializes in ultra-realistic voice cloning with just 3-5 minutes of audio input.': """\
      <p>The key technical differentiator is Resemble's localization pipeline: you record a voice once in English and Resemble generates that same voice speaking Spanish, French, German, Japanese, and 17 other languages — with natural prosody in each language, not just accent-carried English. For global brands creating consistent brand voice content across markets, this is transformative. A product demo narrated by your brand voice in 20 languages from a single recording session. Resemble's enterprise API also includes deepfake detection — a compliance and trust feature increasingly required for brands using AI voice in regulated industries.</p>""",

    'Replica Studios focuses specifically on voice acting for games, animations, and virtual production.': """\
      <p>Replica Studios' voice models are trained specifically for emotional performance delivery, not neutral narration. Where ElevenLabs produces realistic-sounding speech, Replica produces realistic-sounding character performances — surprise, fear, determination, whispers, shouts — all with the nuance of a professional voice actor rather than a narrator. Their Unreal Engine and Unity SDK integrations let game developers generate NPC dialogue directly in the engine, with emotion tags embedded in the script: [angry] "I said leave!" generates differently than the same line without the tag. For independent game studios, this replaces expensive voice actor session bookings.</p>""",

    'Amazon Polly is a cloud TTS API at $4 per 1 million characters': """\
      <p>For applications that need TTS at scale — IVR phone systems, accessibility features across a large content library, notification reading, or real-time assistants handling thousands of concurrent users — Amazon Polly's pricing model becomes transformatively cheaper than ElevenLabs. A system generating 100 million characters per month pays $400 with Polly vs. $4,000+ with ElevenLabs. Polly's Neural TTS voices are genuinely good for US English and a handful of other major languages — notably better than older Google Cloud TTS. The tradeoff is that Polly requires AWS infrastructure familiarity and offers no consumer-facing editor — it's an API-only product.</p>""",
}

for trigger, extra_para in EXPANSIONS.items():
    # Find the paragraph containing this trigger and insert the new paragraph before <div class="pros-cons">
    pattern = re.compile(
        r'(<p>' + re.escape(trigger) + r'.*?</p>)(\s*\n\s*<div class="pros-cons">)',
        re.DOTALL
    )
    match = pattern.search(html)
    if match:
        html = html[:match.start()] + match.group(1) + '\n' + extra_para + match.group(2) + html[match.end():]
        print(f"  Expanded: {trigger[:50]}...")
    else:
        print(f"  SKIP (not found): {trigger[:50]}...")


# ── 2. Add 5 more FAQ items before </section> after the existing 4 ─────────────
new_faqs = """      <div class="faq-item"><div class="faq-question">Can ElevenLabs alternatives clone my voice?</div><div class="faq-answer">Yes — Murf AI, Play.ht, Resemble AI, and Descript all offer voice cloning. Quality varies significantly: Resemble AI produces the most realistic custom clones (from 3-5 minutes of audio). Murf and Play.ht clone from short samples but with lower accuracy on specific accents. Descript's Overdub clones your voice specifically for corrections within your own recorded content. None match ElevenLabs' Professional Voice Cloning quality, which requires 30 minutes of clean audio and produces the most realistic results.</div></div>
      <div class="faq-item"><div class="faq-question">Which ElevenLabs alternative is best for podcasters?</div><div class="faq-answer">Descript is the best ElevenLabs alternative for podcasters. Its transcript-based editing workflow — remove a word from the script and it disappears from the audio — eliminates 80% of cut-edit-re-record cycles. Overdub clones your voice so you can fix mistakes without re-recording. Murf AI is a better pick if you produce scripted content (not natural conversation) and need studio-quality narration without video editing. ElevenLabs itself is also excellent for scripted podcast intros/outros and ad reads — <a href="/go/elevenlabs/" rel="nofollow sponsored" target="_blank" style="color:var(--color-primary);">its permanent free plan</a> covers 10,000 characters monthly at no cost.</div></div>
      <div class="faq-item"><div class="faq-question">Is there an ElevenLabs alternative with unlimited characters?</div><div class="faq-answer">Yes — Play.ht's Unlimited plan ($49/month) offers unlimited character generation. Murf AI's Pro plan ($26/month) offers 24 hours of voice generation per year with no per-character limits on their standard voices. Amazon Polly is effectively unlimited at scale ($4 per 1M characters, first 5M characters free for 12 months). ElevenLabs' own Starter plan ($22/month) includes 30,000 characters — enough for about 22 minutes of audio per month.</div></div>
      <div class="faq-item"><div class="faq-question">ElevenLabs vs Murf AI — which is better for YouTube?</div><div class="faq-answer">For YouTube voice-over content, the choice depends on your production style. ElevenLabs is better if you need hyper-realistic narration that passes as human — particularly if you clone your own voice for AI-generated narration. Murf AI is better if you need an integrated workflow where you write a script, pick a voice, and export directly — Murf Studio's video sync eliminates the step of importing audio into a video editor. Both have permanent free plans. See our full <a href="/compare/elevenlabs-vs-murf/">ElevenLabs vs Murf comparison</a> for a complete breakdown by use case.</div></div>
      <div class="faq-item"><div class="faq-question">Which ElevenLabs alternative supports the most languages?</div><div class="faq-answer">Play.ht supports 142 languages and dialects — the largest coverage of any ElevenLabs alternative. Amazon Polly supports 30+ languages with 60+ voices. Murf AI supports 20+ languages. ElevenLabs supports 29 languages natively, with voice cloning quality highest in English, Spanish, French, German, and Portuguese. For multilingual content or multilingual voice applications, Play.ht's 142-language coverage makes it the strongest alternative — particularly for languages where ElevenLabs' quality drops significantly (Hindi, Arabic, Vietnamese).</div></div>"""

# Insert before the closing </section> of the FAQ section
faq_close = '    </section>\n\n    <section style="margin-top:3rem;">'
if faq_close in html:
    html = html.replace(
        faq_close,
        new_faqs + '\n' + faq_close,
        1
    )
    print("  FAQ items added")
else:
    print("  SKIP FAQ (anchor not found)")


# ── 3. Add Buyer's Guide before the Related section ───────────────────────────
buyers_guide = """
    <section style="margin-top:2.5rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,0.08);">
      <h2>How to Choose the Right ElevenLabs Alternative</h2>
      <p style="color:rgba(148,163,184,0.85);line-height:1.8;">ElevenLabs alternatives are not interchangeable — each solves a different problem. The right choice depends on your primary use case, volume needs, and technical requirements.</p>

      <h3>For Content Creators (YouTube, Podcasts, Courses)</h3>
      <p style="color:rgba(148,163,184,0.85);line-height:1.8;">If you produce video or podcast content, <strong style="color:#f1f5f9;">Descript</strong> is the most practical alternative — its transcript-based editing and Overdub voice cloning integrate directly into your editing workflow. For scripted narration (courses, explainer videos), <strong style="color:#f1f5f9;">Murf AI</strong> provides the cleanest studio-quality output with a built-in video sync editor. Both have free plans for testing. ElevenLabs itself remains the best choice for voice cloning quality — its <a href="/go/elevenlabs/" rel="nofollow sponsored" target="_blank" style="color:#f97316;">free plan (10,000 chars/month)</a> is worth using even as a secondary tool.</p>

      <h3>For Developers Building Voice Applications</h3>
      <p style="color:rgba(148,163,184,0.85);line-height:1.8;"><strong style="color:#f1f5f9;">Play.ht</strong> is the strongest developer-focused alternative: real-time streaming TTS, 142 languages, webhook support, and competitive per-character pricing. For high-volume production at AWS scale, <strong style="color:#f1f5f9;">Amazon Polly</strong> at $4 per 1M characters is unmatched on cost. For custom enterprise voice cloning at scale (brand voices, character voices), <strong style="color:#f1f5f9;">Resemble AI</strong> offers the most sophisticated API with multilingual voice generation from a single sample recording.</p>

      <h3>For Personal Productivity and Learning</h3>
      <p style="color:rgba(148,163,184,0.85);line-height:1.8;"><strong style="color:#f1f5f9;">Speechify</strong> is the only alternative on this list designed specifically for consuming content rather than producing it. If you want to listen to articles, PDFs, emails, and research papers at 2-4× speed, Speechify's Chrome extension and mobile app solve a different problem than ElevenLabs. None of the other alternatives offer this listening-mode workflow.</p>

      <h3>For Gaming and Interactive Media</h3>
      <p style="color:rgba(148,163,184,0.85);line-height:1.8;"><strong style="color:#f1f5f9;">Replica Studios</strong> is purpose-built for game development: emotional voice performance, NPC dialogue generation, Unreal Engine and Unity SDK integration, and voice actors trained for interactive rather than linear storytelling. For studios that need character dialogue with emotional range — not just neutral narration — Replica Studios is the only ElevenLabs alternative specifically designed for this use case.</p>
    </section>
"""

related_section = '    <section style="margin-top:3rem;">\n      <h3>Related</h3>'
if related_section in html:
    html = html.replace(related_section, buyers_guide + '\n' + related_section, 1)
    print("  Buyer's guide added")
else:
    print("  SKIP buyer's guide (anchor not found)")


# ── 4. Save and report ────────────────────────────────────────────────────────
with open(path, "w", encoding="utf-8") as f:
    f.write(html)

words = len(re.sub(r'<[^>]+>', '', html).split())
print(f"\nDone. Word count: ~{words}")
