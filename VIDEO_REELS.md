# Social reels (Instagram / TikTok / Shorts)

Vertical 1080x1920 promo reels for RankerToolAI review pages, written as
[HyperFrames](https://github.com/heygen-com/hyperframes) HTML compositions and
rendered in the cloud. The owner's PC is too weak to render locally, and the
owner usually works from a phone.

## How a reel gets made

1. Work on branch `video-test-synthesia` (or a new `video-*` branch made FROM it,
   because main does not have the workflow). Never commit reels to `main`:
   pushing main deploys the live site.
2. Add a folder `social_videos/<slug>_reel_vN/` with `index.html` (the
   composition), `caption.txt`, and any footage clips it references.
   Copy `synthesia_reel_v3/` as the template.
3. Push. `.github/workflows/render-reel-tg.yml` renders only the folders changed
   in that push, uploads an artifact named `reels` (MP4 + 4 stills + caption),
   and sends the MP4 plus the caption as a separate message to the owner's
   Telegram (bot @rankernest_reels_bot, secrets TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).
4. Check: `gh run list -b video-test-synthesia`, then `gh run download <id> -n reels`.

## Content rules

- Facts come ONLY from that tool's page `review/<slug>/index.html`. Never invent
  numbers or test results.
- Real footage only: the owner's own screen recordings or the tool's own output
  from the owner's account. No AI-faked UI, no fake avatars, no AI voiceover of our own.
- Caption must carry `#ad — contains affiliate links`. Platforms' "AI-generated"
  label goes on when the clip shows AI avatars.
- Check the affiliate program's rules first (some ban paid ads or brand use).
- 1–2 reels a day per account, not mass posting.

## Gotchas

- HyperFrames aborts if a video clip has fewer than 95% of its expected frames.
  Re-encode every footage clip with `-vf "...,fps=30,tpad=stop_mode=clone:stop_duration=2"`
  and make it ~0.1s longer than its `data-duration`.
- Text stays inside the safe zone: 260px from the top, 420px from the bottom.
- Changing anything under `.github/workflows/` needs the owner to commit it via
  the GitHub web page (the local gh token has no `workflow` scope).
