// AI voiceover for existing silent reels (owner 2026-10-31: "lồng tiếng như dự án Joiin, áp dụng cho
// tất cả video"). Same engine and voice as the Joiin voice reels: Kokoro TTS run locally (Apache 2.0
// weights, commercial use OK), voice af_heart.
//
//   node reel_tools/add_voice.js                 # every slug in voice_scripts.json
//   node reel_tools/add_voice.js gifts-wfh dropmagic [--dry-run]
//
// For each slug: base reel + its _hb/_hc variants. The silent original is kept once in
// Videos/RankerToolAI_reels/_goc_khong_tieng/ and every run starts from that copy, so re-running is safe.
// Lines are spread over the clip (hook first), sped up to 1.2x at most, and the last frame is held if the
// voice still runs long. The video stream is copied unless it has to be extended (weak PC: no re-encode).
// Rules from the Joiin reels: loudnorm I=-14, voice ends >= 0.5s before the clip does.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const VIDEOS = 'C:\\Users\\Admin\\Videos\\RankerToolAI_reels';
const ORIG = path.join(VIDEOS, '_goc_khong_tieng');
const PY = 'C:\\Users\\Admin\\tools\\kokoro\\.venv\\Scripts\\python.exe';
const TTS = 'C:\\Users\\Admin\\RankerToolAI\\social_agent\\video\\tts_kokoro.py';
const VOICE = 'af_heart';
const START = 0.25, MIN_GAP = 0.2, MAX_GAP = 1.0, TAIL = 0.5, MAX_TEMPO = 1.2;

const args = process.argv.slice(2);
const DRY = args.includes('--dry-run');
const scripts = JSON.parse(fs.readFileSync(path.join(__dirname, 'voice_scripts.json'), 'utf8'));
const slugs = args.filter((a) => !a.startsWith('--'));
const todo = slugs.length ? slugs : Object.keys(scripts).filter((k) => !k.startsWith('_'));

const probe = (f) => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

for (const slug of todo) {
  const sc = scripts[slug];
  if (!sc) { console.error(`${slug}: không có lời đọc trong voice_scripts.json`); continue; }
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts', slug + '.json'), 'utf8'));
  const variants = [['a', spec.reel], ...Object.keys(spec.variants || {}).map((k) => [k, `${spec.reel}_h${k}`])];

  // One TTS run per slug: the 3 hooks + the shared body.
  const tmp = path.join(os.tmpdir(), 'voice_' + slug);
  const lines = [...variants.filter(([k]) => sc[k]).map(([k]) => `H${k}|${sc[k]}`), ...sc.body.map((t, i) => `B${i + 1}|${t}`)];
  if (DRY) { console.log(`${slug}: ${variants.map((v) => v[1]).join(', ')}\n  ${lines.join('\n  ')}`); continue; }
  fs.mkdirSync(tmp, { recursive: true });
  fs.writeFileSync(path.join(tmp, 'script.txt'), lines.join('\n'), 'utf8');
  execFileSync(PY, [TTS, path.join(tmp, 'script.txt'), tmp, VOICE, '1.0'], { stdio: 'inherit' });
  const dur = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(tmp, 'lines.json'), 'utf8')).lines.map((l) => [l.id, l.dur]));

  fs.mkdirSync(ORIG, { recursive: true });
  for (const [k, reel] of variants) {
    const out = path.join(VIDEOS, reel + '.mp4');
    const src = path.join(ORIG, reel + '.mp4');
    if (!fs.existsSync(src)) {
      if (!fs.existsSync(out)) { console.log(`  ${reel}: thiếu video, bỏ qua`); continue; }
      fs.copyFileSync(out, src);                  // keep the silent original once
    }
    const ids = [`H${sc[k] ? k : 'a'}`, ...sc.body.map((_, i) => `B${i + 1}`)];
    const D = probe(src);
    const speech = ids.reduce((a, id) => a + dur[id], 0);
    let room = D - START - TAIL - MIN_GAP * (ids.length - 1);
    const tempo = Math.min(MAX_TEMPO, Math.max(1, speech / room));
    const spoken = speech / tempo;
    const hold = Math.max(0, spoken - room);       // still too long at max tempo: freeze the last frame
    const gap = Math.min(MAX_GAP, MIN_GAP + Math.max(0, room - spoken) / Math.max(1, ids.length - 1));
    let t = START; const starts = [];
    for (const id of ids) { starts.push(t); t += dur[id] / tempo + gap; }
    const total = D + hold;

    const inputs = ['-i', src, ...ids.flatMap((id) => ['-i', path.join(tmp, id + '.wav')])];
    const chains = ids.map((id, i) => `[${i + 1}:a]${tempo > 1.001 ? `atempo=${tempo.toFixed(3)},` : ''}adelay=${Math.round(starts[i] * 1000)}:all=1[v${i}]`);
    const mix = `${ids.map((_, i) => `[v${i}]`).join('')}amix=inputs=${ids.length}:normalize=0,apad,atrim=0:${total.toFixed(3)},loudnorm=I=-14:TP=-1.5:LRA=11[a]`;
    const vf = hold > 0 ? ['-filter_complex', `[0:v]tpad=stop_mode=clone:stop_duration=${hold.toFixed(3)}[vv];${chains.join(';')};${mix}`, '-map', '[vv]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-threads', '2', '-x264-params', 'rc-lookahead=10']
      : ['-filter_complex', `${chains.join(';')};${mix}`, '-map', '0:v', '-c:v', 'copy'];
    const tmpOut = path.join(tmp, reel + '.mp4');
    execFileSync('ffmpeg', ['-v', 'error', '-y', ...inputs, ...vf, '-map', '[a]', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-t', total.toFixed(3), '-movflags', '+faststart', tmpOut], { stdio: 'inherit' });
    fs.copyFileSync(tmpOut, out);
    console.log(`  ${reel}: ${D.toFixed(1)}s video, giọng ${speech.toFixed(1)}s, tốc độ x${tempo.toFixed(2)}${hold ? `, giữ khung cuối +${hold.toFixed(1)}s` : ''}`);
  }
}
