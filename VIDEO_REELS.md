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

## Background music (every reel gets it)

Since 2026-10-13 every reel ships with a music bed baked in. Owner's choice: music
pre-mixed into the MP4, NOT trending hit songs. Hit songs are copyrighted (muted or
removed on IG/TikTok, and IG Business accounts may only use Meta's commercial library),
so only free-license tracks go into the file.

1. Build the reel folder as usual (index.html etc.).
2. `node reel_tools/add_music.js social_videos/<folder> <mood>`
   - moods (reel_tools/music/tracks.json): `tech` (AI tools / Synthesia), `home`
     (vacuums, appliances, chairs), `fashion` (silk, beauty), `gadget` (keyboards,
     desk gear), `warm` (gifts, lamps).
   - Needs ffmpeg + internet the first time (downloads the Mixkit mp3 into
     `reel_tools/music/cache/`, which is gitignored).
3. Commit `music.m4a` together with the folder and push.

What the script does: stretches the track to exactly 120 BPM and starts it on a beat
at the track's drop, so every scene cut (all on 0.5s steps) lands on a beat. Keep scene
starts/durations on 0.5s steps or the sync is lost. Loudness -14 LUFS; under any clip
with `data-has-audio="true"` (the Synthesia avatar) the music drops ~15 dB.

Adding a track: Mixkit only (license: social media + online ads OK, no attribution;
not for TV/radio/games). Measure bpm and an on-beat `start` at the drop before adding
it to tracks.json; a wrong bpm drifts off the cuts.
