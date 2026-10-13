// Adds a royalty-free background music bed to a reel folder (HyperFrames composition).
// Usage: node reel_tools/add_music.js social_videos/<reel_folder> <mood>
// Moods are in reel_tools/music/tracks.json (tech, home, fashion, gadget, warm).
//
// The track is time-stretched to exactly 120 BPM (one beat = 0.5s) and starts on a beat
// at its drop, so every scene cut (all on 0.5s steps) lands on a beat. Clips with their
// own sound (data-has-audio="true", e.g. the Synthesia avatar) get the music ducked
// under them. Writes music.m4a into the folder and an <audio id="music"> into index.html.
// Needs ffmpeg on PATH. Source mp3s are cached in reel_tools/music/cache/ (not committed).
const fs = require("fs");
const path = require("path");
const https = require("https");
const { execFileSync } = require("child_process");

const [dir, mood] = process.argv.slice(2);
const lib = JSON.parse(fs.readFileSync(path.join(__dirname, "music/tracks.json"), "utf8")).tracks;
const track = lib[mood];
if (!dir || !track) {
  console.error("Usage: node add_music.js <reel_folder> <" + Object.keys(lib).join("|") + ">");
  process.exit(1);
}

const TARGET_BPM = 120;
const DUCK_GAIN = 0.18; // music level under a voice clip (~ -15 dB)
const RAMP = 0.25;      // seconds to duck in/out

const htmlPath = path.join(dir, "index.html");
let html = fs.readFileSync(htmlPath, "utf8");
const total = parseFloat(html.match(/id="root"[^>]*data-duration="([\d.]+)"/)[1]);

// Voice windows: media clips that keep their own sound
const ducks = [];
for (const m of html.matchAll(/<video[^>]*data-has-audio="true"[^>]*>/g)) {
  const a = parseFloat(m[0].match(/data-start="([\d.]+)"/)[1]);
  const d = parseFloat(m[0].match(/data-duration="([\d.]+)"/)[1]);
  ducks.push([a, a + d]);
}

function download(url, file) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) return reject(new Error(url + " -> HTTP " + res.statusCode));
      const out = fs.createWriteStream(file);
      res.pipe(out);
      out.on("finish", () => out.close(resolve));
    }).on("error", reject);
  });
}

(async () => {
  const cache = path.join(__dirname, "music/cache");
  fs.mkdirSync(cache, { recursive: true });
  const src = path.join(cache, track.id + ".mp3");
  if (!fs.existsSync(src)) await download(`https://assets.mixkit.co/music/${track.id}/${track.id}.mp3`, src);

  const tempo = TARGET_BPM / track.bpm;
  // 1 at full level, DUCK_GAIN inside each voice window, linear ramps around it
  const vol = ducks.length
    ? ducks.map(([a, b]) =>
        `(1-${1 - DUCK_GAIN}*clip((t-${a - RAMP})/${RAMP},0,1)*clip((${b + RAMP}-t)/${RAMP},0,1))`).join("*")
    : "1";
  const filter = [
    `atempo=${tempo.toFixed(5)}`,
    `atrim=0:${total}`,
    "asetpts=N/SR/TB",
    "loudnorm=I=-14:TP=-1.5:LRA=11",
    "aresample=48000",
    `volume='${vol}':eval=frame`,
    "afade=t=in:d=0.03",
    `afade=t=out:st=${Math.max(0, total - 1.5)}:d=1.5`,
  ].join(",");
  const out = path.join(dir, "music.m4a");
  execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(track.start), "-t", String(total / tempo + 1),
    "-i", src, "-af", filter, "-ac", "2", "-c:a", "aac", "-b:a", "160k", out], { stdio: "inherit" });

  const tag = `<audio id="music" class="clip" data-start="0" data-duration="${total}" data-track-index="2" data-volume="1" src="music.m4a"></audio>`;
  if (/<audio id="music"[^>]*><\/audio>/.test(html)) html = html.replace(/<audio id="music"[^>]*><\/audio>/, tag);
  else html = html.replace(/(<div id="root"[^>]*>)/, `$1\n      <!-- Music: "${track.title}" (Mixkit, free license), stretched to ${TARGET_BPM} BPM so cuts land on beats -->\n      ${tag}`);
  fs.writeFileSync(htmlPath, html);
  console.log(`${dir}: ${mood} = "${track.title}", ${total}s, tempo x${tempo.toFixed(3)}, ducked ${JSON.stringify(ducks)}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
