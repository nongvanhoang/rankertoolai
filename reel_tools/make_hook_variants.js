// Makes hook-test copies of a reel: same video, only the opening line (first 3–3.5s) changes.
// Usage: node reel_tools/make_hook_variants.js reel_tools/posts/<slug>.json
// For each spec.variants.<k> writes social_videos/<reel>_h<k>/ (index.html with the new
// hook, caption.txt whose first line is the new hook, same photos/clips).
// The original reel counts as hook A. Then run make_posts.js for the posting texts.
const fs = require("fs");
const path = require("path");
const s = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const root = path.join(__dirname, "..", "social_videos");
const src = path.join(root, s.reel);
for (const [k, v] of Object.entries(s.variants || {})) {
  const dst = path.join(root, `${s.reel}_h${k}`);
  fs.rmSync(dst, { recursive: true, force: true });
  fs.cpSync(src, dst, { recursive: true });
  const f = path.join(dst, "index.html");
  const html = fs.readFileSync(f, "utf8");
  // the hook is the first .big inside the scene that starts at 0 on track 1
  const re = /(<div id="\w+" class="scene clip[^"]*" data-start="0" [^>]*data-track-index="1">[\s\S]*?<div class="big">)([\s\S]*?)(<\/div>)/;
  if (!re.test(html)) { console.error(`${s.reel}: hook not found`); process.exit(1); }
  fs.writeFileSync(f, html.replace(re, (m, a, _old, c) => a + v.html + c)); // function form: "$1" in prices must stay literal
  const cap = path.join(dst, "caption.txt");
  const lines = fs.readFileSync(cap, "utf8").split("\n");
  lines[0] = v.hook;
  fs.writeFileSync(cap, lines.join("\n"));
  console.log(`${s.reel}_h${k}: ${v.hook}`);
}
