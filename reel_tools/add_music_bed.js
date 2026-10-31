// Music bed under the AI voice (owner 2026-10-31): the weekly scheduling tools (Meta Business Suite,
// YouTube Studio, TikTok Studio, Pinterest, LinkedIn) can't add app music, so the music has to be in the
// file. Royalty-free Mixkit beds only (reel_tools/music/tracks.json "beds"), never trend/app music.
//
//   node reel_tools/add_music_bed.js                       # every slug in voice_scripts.json
//   node reel_tools/add_music_bed.js friendshiplamps [--track 158] [--out <dir>] [--suffix _x] [--dry-run]
//
// Reads Videos/RankerToolAI_reels/<reel>.mp4 (already voiced) and writes <reel>_nhac.mp4 next to it.
// The bed is levelled by its measured loudness, faded in/out and ducked under the voice (sidechain), then
// the mix is loudnormed to -14 LUFS like the voice reels. Video stream copied (weak PC: no re-encode).
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const VIDEOS = 'C:\\Users\\Admin\\Videos\\RankerToolAI_reels';
const CACHE = path.join(__dirname, 'music', 'cache');
const BED_LVL = -23;            // where every bed's loud part sits before ducking (dBFS)

const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const DRY = args.includes('--dry-run');
const TRACK = opt('--track');
const OUT = opt('--out', VIDEOS);
const SUFFIX = opt('--suffix', '_nhac');
const flagVals = new Set(['--track', '--out', '--suffix'].map((n) => opt(n)).filter(Boolean));
const lib = JSON.parse(fs.readFileSync(path.join(__dirname, 'music', 'tracks.json'), 'utf8'));
const voiced = JSON.parse(fs.readFileSync(path.join(__dirname, 'voice_scripts.json'), 'utf8'));
const slugs = args.filter((a) => !a.startsWith('--') && !flagVals.has(a));
const todo = slugs.length ? slugs : Object.keys(voiced).filter((k) => !k.startsWith('_'));

const probe = (f) => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const hash = (s) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
const allBeds = Object.values(lib.beds).flat();

function pick(slug, reel) {
  if (TRACK) return allBeds.find((b) => String(b.id) === String(TRACK)) || { id: +TRACK, title: '?', start: 0, lvl: -12 };
  const list = lib.beds[lib.slug_mood[slug] || 'warm'];
  return list[hash(reel) % list.length];
}

for (const slug of todo) {
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts', slug + '.json'), 'utf8'));
  const reels = [spec.reel, ...Object.keys(spec.variants || {}).map((k) => `${spec.reel}_h${k}`)];
  for (const reel of reels) {
    const src = path.join(VIDEOS, reel + '.mp4');
    if (!fs.existsSync(src)) { console.log(`  ${reel}: thiếu video, bỏ qua`); continue; }
    const bed = pick(slug, reel);
    const mp3 = path.join(CACHE, bed.id + '.mp3');
    if (DRY) { console.log(`  ${reel} ← ${bed.id} ${bed.title}`); continue; }
    if (!fs.existsSync(mp3)) execFileSync('curl', ['-sfL', '-A', 'Mozilla/5.0', '-o', mp3, `https://assets.mixkit.co/music/${bed.id}/${bed.id}.mp3`]);
    const D = probe(src);
    const gain = Math.pow(10, (BED_LVL - bed.lvl) / 20).toFixed(3);
    const fc = `[0:a]asplit=2[v][sc];[1:a]volume=${gain},afade=t=in:d=0.4,afade=t=out:st=${(D - 1.2).toFixed(2)}:d=1.2[m];` +
      `[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];` +
      `[v][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]`;
    const out = path.join(OUT, reel + SUFFIX + '.mp4');
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', src, '-ss', String(bed.start), '-i', mp3, '-filter_complex', fc,
      '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', D.toFixed(3), '-movflags', '+faststart', out], { stdio: 'inherit' });
    console.log(`  ${path.basename(out)} ← ${bed.id} ${bed.title}`);
  }
}
