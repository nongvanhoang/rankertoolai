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

## RankerNest photo reels (generator)

RankerNest reels live here too, in folders named `social_videos/rankernest_<slug>_vN/`.
Only use products whose status is `ok` in RankerNest's `social/asset_permissions.json`
(merchant photos). Amazon product images are not allowed.

1. Copy 4 cleared photos into the new folder as `.jpg` + `logo.svg` (RankerNest white mark).
   Skip merchant photos that make health, before/after or "vs other brands" claims.
2. Write a spec like `reel_tools/specs/switchbot.json` (hook, 3 photo scenes, optional
   fact cards, offer/price, url, disclose). Every number must be on the review page.
3. `node reel_tools/make_rn_reel.js reel_tools/specs/<name>.json social_videos/rankernest_<slug>_v1`
4. Add `caption.txt` (ends with `#ad — affiliate link…`), commit, push. Telegram gets it ~4 min later.

## Music: NOT baked in (owner adds trending music in CapCut)

Owner decision 2026-10-13: reels go out with their ORIGINAL sound only (silent photo
reels stay silent, Synthesia keeps the avatar voice). The owner adds trending music
in CapCut before posting. Do NOT run add_music.js unless the owner asks for it.

Optional tool, kept for later: `node reel_tools/add_music.js social_videos/<folder> <mood>`
bakes a beat-synced Mixkit free-license track into a reel (moods in
reel_tools/music/tracks.json). The *_v5 / *_v3 / ek01-plus_v4 folders from 2026-10-13 are
the music versions; the previous version numbers are the original-sound ones to post.

## Multi-platform posting kit (every reel gets one)

Since 2026-10-13 every reel also gets a posting kit for Pinterest, YouTube Shorts,
(LinkedIn), Facebook Reels, Threads, X, TikTok and the email newsletter, in the format
of the Synthesia v3 kit the owner approved. Instagram keeps using caption.txt.

1. Write `reel_tools/posts/<slug>.json` (copy a similar one). `site` is `rn` or `rta`,
   `reel` is the social_videos folder to post, `kw` is the keyword landing page the video
   shows (rankernest.com/<kw>, rankertoolai.com/<kw>). Facts ONLY from the review page /
   caption.txt. Add `linkedin` only for work/B2B products. Add `expires` for sale-dated videos.
2. `node reel_tools/make_posts.js reel_tools/posts/<slug>.json` → `social_posts/<reel>/`
   (DANG_DA_KENH.txt + tg/*.html). It fails if any platform length limit is exceeded.
3. Commit and push together with (or after) the reel. `.github/workflows/send-posts-tg.yml`
   waits for the render to finish, then sends one Telegram message per channel (copy text in
   tap-to-copy blocks) + the .txt file. Resend one: Actions → "Send posting kit" → Run workflow.

Links: every channel has its own utm_source; utm_campaign=reel_video, utm_content=reel-<slug>
(RankerNest's social/winners_report.py reads utm_content).
