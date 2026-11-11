// Motion-graphics reel generator (deal / price / fact reels), both brands, Vietnamese-safe font.
// Usage: node reel_tools/make_deal_reel.js reel_tools/specs/deal_<slug>.json social_videos/<reel_folder>
// Writes <folder>/index.html (HyperFrames composition) and copies photos listed in the spec.
// Push the folder on a video-* branch: GitHub renders it and sends the MP4 to Telegram.
//
// Spec fields (all scenes except hook + cta are optional; durations are automatic):
//   brand: "rta" | "rn"
//   hook:   { kicker, pre?, big, unit?, line (HTML allowed, <span class="hl">) , photo? }
//   price:  { label, old, new, prefix?: "$", per, foot? }      old/new = digits only, e.g. "420" → "210"
//   photos: [{ src (path relative to repo root), text (HTML), small? }]
//   rows:   { kicker, items: [{ n, t (HTML) }] }               up to 3 big-number rows
//   rules:  { items: [{ icon: "ok"|"no"|"warn", text }], ends? }
//   cta:    { text, url (HTML), disclose }
// Every fact must come from the live review/deal page (see VIDEO_REELS.md).
const fs = require("fs");
const path = require("path");

const [specPath, outDir] = process.argv.slice(2);
if (!specPath || !outDir) { console.error("usage: node make_deal_reel.js <spec.json> <out folder>"); process.exit(1); }
const s = JSON.parse(fs.readFileSync(specPath, "utf8"));
const ROOT = path.join(__dirname, "..");
fs.mkdirSync(outDir, { recursive: true });

const THEMES = {
  rta: { bg: "#050a18", panel: "#0d1630", text: "#f8fafc", muted: "#94a3b8", a1: "#f97316", a2: "#fbbf24", ok: "#34d399", g2: "#1d4ed8", g2o: 0.3, head: "Inter", headW: 900 },
  rn: { bg: "#080b0d", panel: "#12181b", text: "#eef1ee", muted: "#9aa3a0", a1: "#ff4d6d", a2: "#ffc93c", ok: "#06d6c4", g2: "#06d6c4", g2o: 0.16, head: "Fraunces", headW: 700 },
};
const T = THEMES[s.brand];
if (!T) throw new Error("brand must be rta or rn");

// ---------- timing ----------
const scenes = [];
let t = 0;
const add = (id, dur) => { scenes.push({ id, start: +t.toFixed(2), dur }); t += dur; return scenes[scenes.length - 1]; };
const sHook = add("hook", s.hook.photo ? 3.4 : 3);
const sPrice = s.price ? add("price", 4.2) : null;
const sPhotos = (s.photos || []).map((p, i) => add("photo" + i, 3.2));
const sRows = s.rows ? add("rows", 1.4 + 0.75 * s.rows.items.length) : null;
const sRules = s.rules ? add("rules", 1.6 + 0.6 * s.rules.items.length + (s.rules.ends ? 0.8 : 0)) : null;
const sCta = add("cta", 2.8);
const D = +t.toFixed(2);

// ---------- photos ----------
const photoName = (src, i) => `p${i}${path.extname(src)}`;
const allPhotos = [s.hook.photo, ...(s.photos || []).map((p) => p.src)].filter(Boolean);
allPhotos.forEach((src, i) => fs.copyFileSync(path.join(ROOT, src), path.join(outDir, photoName(src, i))));
const photoFile = (src) => photoName(src, allPhotos.indexOf(src));

// ---------- odometer: each digit column rolls from old digit down to new digit ----------
function odometer(oldV, newV) {
  const n = Math.max(oldV.length, newV.length);
  const o = oldV.padStart(n, " "), w = newV.padStart(n, " ");
  const cols = [];
  for (let i = 0; i < n; i++) {
    if (o[i] === " " || w[i] === " " || !/\d/.test(o[i]) || !/\d/.test(w[i])) { cols.push({ digits: [w[i] === " " ? "" : w[i]], steps: 0 }); continue; }
    const digits = [o[i]];
    let d = +o[i];
    while (d !== +w[i]) { d = (d + 9) % 10; digits.push(String(d)); }
    cols.push({ digits, steps: digits.length - 1 });
  }
  return cols;
}

const ICON = { ok: ["ok", "✓"], no: ["no", "✕"], warn: ["warn", "!"] };
const clip = (sc, cls, inner) =>
  `<div id="${sc.id}" class="scene clip ${cls || ""}" data-start="${sc.start}" data-duration="${sc.dur}" data-track-index="1">\n${inner}\n      </div>`;

let html = [];
let js = [];
const at = (sc, off) => +(sc.start + off).toFixed(2);

// hook
{
  const h = s.hook;
  html.push(clip(sHook, "", [
    `<div class="kicker">${h.kicker}</div>`,
    h.pre ? `<div class="pre">${h.pre}</div>` : "",
    `<div class="stamp">${h.big}${h.unit ? `<small>${h.unit}</small>` : ""}</div>`,
    `<div class="bar"></div>`,
    `<div class="mid">${h.line}</div>`,
    h.photo ? `<div class="photo short"><img src="${photoFile(h.photo)}" alt="" /></div>` : "",
  ].filter(Boolean).join("\n")));
  js.push(`tl.fromTo("#hook .kicker", inUp, shown, ${at(sHook, 0.05)});`);
  if (h.pre) js.push(`tl.fromTo("#hook .pre", inUp, shown, ${at(sHook, 0.2)});`);
  js.push(`tl.fromTo("#hook .stamp", { opacity: 0, scale: 2.2, rotation: -8 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.55, ease: "back.out(1.7)", transformOrigin: "left center" }, ${at(sHook, 0.3)});`);
  js.push(`tl.fromTo("#hook .bar", { scaleX: 0 }, { scaleX: 1, duration: 0.4, ease: "power2.out" }, ${at(sHook, 0.85)});`);
  js.push(`tl.fromTo("#hook .mid", inUp, shown, ${at(sHook, 1.05)});`);
  if (h.photo) js.push(`photoIn("#hook .photo", ${at(sHook, 1.4)}, ${sHook.dur - 1.4});`);
  js.push(`tl.to("#hook .stamp", { scale: 1.04, duration: 0.25, yoyo: true, repeat: 1, ease: "power1.inOut", transformOrigin: "left center" }, ${at(sHook, sHook.dur - 0.8)});`);
}

// price
if (sPrice) {
  const p = s.price, pre = p.prefix ?? "$";
  const cols = odometer(p.old, p.new);
  html.push(clip(sPrice, "", [
    `<div class="card">`,
    `  <div class="label">${p.label}</div>`,
    `  <div class="old">${pre}${p.old}<div class="strike"></div></div>`,
    `  <div class="new"><div class="dollar">${pre}</div><div class="odo">${cols.map((c, i) => `<div class="col" id="c${i}">${c.digits.map((d) => `<span>${d}</span>`).join("")}</div>`).join("")}</div></div>`,
    `  <div class="per">${p.per}</div>`,
    `</div>`,
    p.foot ? `<div class="foot">${p.foot}</div>` : "",
  ].filter(Boolean).join("\n")));
  js.push(`tl.fromTo("#price .card", { opacity: 0, y: 90, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out" }, ${at(sPrice, 0.05)});`);
  js.push(`tl.fromTo("#price .strike", { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "power2.inOut" }, ${at(sPrice, 0.75)});`);
  js.push(`tl.to("#price .old", { opacity: 0.5, duration: 0.3 }, ${at(sPrice, 1.1)});`);
  js.push(`tl.fromTo("#price .new", { opacity: 0 }, { opacity: 1, duration: 0.3 }, ${at(sPrice, 1.2)});`);
  cols.forEach((c, i) => { if (c.steps) js.push(`tl.fromTo("#c${i}", { y: 0 }, { y: ${-200 * c.steps}, duration: ${(0.6 + 0.1 * c.steps).toFixed(2)}, ease: "power3.inOut" }, ${at(sPrice, 1.3 + 0.12 * i)});`); });
  js.push(`tl.fromTo("#price .per", inUp, shown, ${at(sPrice, 2.2)});`);
  if (p.foot) js.push(`tl.fromTo("#price .foot", { opacity: 0 }, { opacity: 1, duration: 0.4 }, ${at(sPrice, 2.5)});`);
}

// photos
(s.photos || []).forEach((p, i) => {
  const sc = sPhotos[i], id = "#" + sc.id;
  html.push(clip(sc, "top", [
    `<div class="photo tall"><img src="${photoFile(p.src)}" alt="" /></div>`,
    `<div class="mid">${p.text}</div>`,
    p.small ? `<div class="small">${p.small}</div>` : "",
  ].filter(Boolean).join("\n")));
  js.push(`photoIn("${id} .photo", ${at(sc, 0.05)}, ${sc.dur});`);
  js.push(`tl.fromTo("${id} .mid", inUp, shown, ${at(sc, 0.5)});`);
  if (p.small) js.push(`tl.fromTo("${id} .small", inUp, shown, ${at(sc, 0.95)});`);
});

// rows
if (sRows) {
  html.push(clip(sRows, "", [
    `<div class="kicker">${s.rows.kicker}</div>`,
    `<div class="rows">${s.rows.items.map((r) => `<div class="row"><div class="n">${r.n}</div><div class="t">${r.t}</div></div>`).join("")}</div>`,
  ].join("\n")));
  js.push(`tl.fromTo("#rows .kicker", inUp, shown, ${at(sRows, 0.05)});`);
  js.push(`gsap.utils.toArray("#rows .row").forEach((el, i) => tl.fromTo(el, { opacity: 0, x: -160 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, ${at(sRows, 0.4)} + i * 0.4));`);
}

// rules
if (sRules) {
  html.push(clip(sRules, "", [
    ...s.rules.items.map((r) => { const [c, g] = ICON[r.icon || "ok"]; return `<div class="rule"><div class="tick ${c}">${g}</div><div>${r.text}</div></div>`; }),
    s.rules.ends ? `<div class="ends">${s.rules.ends}</div>` : "",
  ].filter(Boolean).join("\n")));
  js.push(`gsap.utils.toArray("#rules .rule").forEach((el, i) => { tl.fromTo(el, inUp, shown, ${at(sRules, 0.1)} + i * 0.55); tl.fromTo(el.querySelector(".tick"), { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(2.2)" }, ${at(sRules, 0.25)} + i * 0.55); });`);
  if (s.rules.ends) js.push(`tl.fromTo("#rules .ends", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)", transformOrigin: "left center" }, ${at(sRules, 0.3 + 0.55 * s.rules.items.length)});`);
}

// cta
html.push(clip(sCta, "", [
  s.cta.logo ? `<div class="brand"><img src="logo.svg" alt="" /><span>${s.cta.logo}</span></div>` : "",
  `<div class="cta">${s.cta.text}</div>`,
  `<div class="url">${s.cta.url}</div>`,
  `<div class="disclose">${s.cta.disclose}</div>`,
].filter(Boolean).join("\n")));
if (s.cta.logo) {
  fs.copyFileSync(path.join(ROOT, s.cta.logoSrc), path.join(outDir, "logo.svg"));
  js.push(`tl.fromTo("#cta .brand", inUp, shown, ${at(sCta, 0.05)});`);
}
js.push(`tl.fromTo("#cta .cta", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)" }, ${at(sCta, 0.3)});`);
js.push(`tl.fromTo("#cta .url", inUp, shown, ${at(sCta, 0.6)});`);
js.push(`tl.fromTo("#cta .disclose", { opacity: 0 }, { opacity: 1, duration: 0.3 }, ${at(sCta, 0.9)});`);

const fonts = T.head === "Fraunces"
  ? "family=Fraunces:wght@600;700&family=Inter:wght@500;700;800;900"
  : "family=Inter:wght@500;700;800;900";
const head = `'${T.head}', Inter, ui-sans-serif, system-ui, sans-serif`;

const out = `<!doctype html>
<html lang="${s.lang || "en"}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <!-- Generated by reel_tools/make_deal_reel.js from ${path.basename(specPath)}. Edit the spec, not this file. -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?${fonts}&display=block" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      :root { --bg: ${T.bg}; --panel: ${T.panel}; --text: ${T.text}; --muted: ${T.muted}; --a1: ${T.a1}; --a2: ${T.a2}; --ok: ${T.ok}; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--bg); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
      #bg { position: absolute; inset: 0; }
      .glow { position: absolute; width: 900px; height: 900px; border-radius: 50%; filter: blur(120px); opacity: 0.32; }
      #glow1 { background: var(--a1); left: -300px; top: 200px; }
      #glow2 { background: ${T.g2}; right: -350px; bottom: 300px; opacity: ${T.g2o}; }
      #grid { position: absolute; inset: 0; opacity: 0.07; background-image: linear-gradient(var(--muted) 1px, transparent 1px), linear-gradient(90deg, var(--muted) 1px, transparent 1px); background-size: 90px 90px; }
      /* Safe zone: 260px top, 420px bottom */
      .scene { position: absolute; left: 80px; right: 80px; top: 260px; bottom: 420px; display: flex; flex-direction: column; justify-content: center; gap: 40px; }
      .scene.top { justify-content: flex-start; }
      .kicker { font-size: 40px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--a1); }
      .pre { font-size: 56px; font-weight: 800; color: var(--muted); margin-bottom: -30px; }
      .mid { font-family: ${head}; font-size: 64px; font-weight: ${T.head === "Inter" ? 800 : 700}; line-height: 1.14; letter-spacing: -0.02em; }
      .small { font-size: 40px; font-weight: 500; line-height: 1.35; color: var(--muted); }
      .hl { color: var(--a2); }
      .bar { width: 160px; height: 12px; border-radius: 6px; background: linear-gradient(90deg, var(--a1), var(--a2)); transform-origin: left center; }
      .stamp { align-self: flex-start; display: flex; align-items: baseline; gap: 12px; font-family: Inter, sans-serif; font-size: 280px; font-weight: 900; letter-spacing: -0.06em; line-height: 0.9;
        background: linear-gradient(180deg, var(--a2), var(--a1)); -webkit-background-clip: text; background-clip: text; color: transparent; padding-right: 20px; }
      .stamp small { font-size: 110px; letter-spacing: -0.03em; margin-left: 22px; }
      .photo { width: 100%; border-radius: 36px; overflow: hidden; background: #fff; box-shadow: 0 30px 90px rgba(0, 0, 0, 0.55); }
      .photo img { width: 100%; height: 100%; display: block; object-fit: cover; object-position: center 35%; }
      .photo.tall { height: 860px; }
      .photo.short { height: 420px; }
      .card { background: var(--panel); border: 2px solid color-mix(in srgb, var(--a1) 35%, transparent); border-radius: 36px; padding: 48px 52px; display: flex; flex-direction: column; gap: 18px; }
      .card .label { font-size: 38px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
      .old { position: relative; align-self: flex-start; font-size: 110px; font-weight: 800; color: var(--muted); letter-spacing: -0.03em; line-height: 1; }
      .strike { position: absolute; left: -10px; right: -10px; top: 52%; height: 12px; border-radius: 6px; background: var(--a1); transform-origin: left center; }
      .new { display: flex; align-items: baseline; gap: 14px; }
      .dollar { font-size: 200px; font-weight: 900; color: var(--a2); line-height: 1; letter-spacing: -0.05em; }
      .odo { display: flex; height: 200px; overflow: hidden; }
      .col { display: flex; flex-direction: column; }
      .col span { display: block; height: 200px; min-width: 60px; font-size: 200px; font-weight: 900; line-height: 200px; color: var(--a2); letter-spacing: -0.05em; text-align: center; padding: 0 4px; }
      .per { font-size: 48px; font-weight: 700; color: var(--muted); }
      .foot { font-size: 32px; font-weight: 500; color: var(--muted); line-height: 1.35; }
      .rows { display: flex; flex-direction: column; gap: 26px; }
      .row { display: flex; align-items: center; gap: 30px; background: var(--panel); border-radius: 28px; padding: 30px 38px; border-left: 10px solid var(--a1); }
      .row .n { font-size: 84px; font-weight: 900; color: var(--a2); letter-spacing: -0.03em; min-width: 250px; }
      .row .t { font-size: 44px; font-weight: 700; line-height: 1.2; }
      .rule { display: flex; align-items: flex-start; gap: 26px; font-size: 52px; font-weight: 800; line-height: 1.18; }
      .tick { flex: none; width: 74px; height: 74px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 44px; font-weight: 900; }
      .tick.ok { background: var(--ok); color: #04170f; }
      .tick.no { background: var(--a1); color: #1a0d02; }
      .tick.warn { background: var(--a2); color: #1a0d02; }
      .ends { align-self: flex-start; font-size: 52px; font-weight: 900; color: #1a0d02; background: linear-gradient(90deg, var(--a1), var(--a2)); border-radius: 999px; padding: 20px 42px; }
      .brand { display: flex; align-items: center; gap: 24px; }
      .brand img { width: 120px; height: 120px; }
      .brand span { font-family: ${head}; font-size: 72px; font-weight: 700; }
      .cta { font-size: 58px; font-weight: 800; line-height: 1.2; background: linear-gradient(90deg, var(--a1), var(--a2)); color: #1a0d02; border-radius: 32px; padding: 40px 48px; }
      .url { font-size: 50px; font-weight: 800; color: var(--text); word-break: break-word; }
      .disclose { font-size: 34px; font-weight: 500; color: var(--muted); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${D}" data-width="1080" data-height="1920">
      <div id="bg" class="clip" data-start="0" data-duration="${D}" data-track-index="0">
        <div id="grid"></div>
        <div id="glow1" class="glow"></div>
        <div id="glow2" class="glow"></div>
      </div>

      ${html.join("\n\n      ")}
    </div>

    <script>
      const D = ${D};
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#glow1", { x: 0, y: 0 }, { x: 240, y: 520, duration: D, ease: "none" }, 0);
      tl.fromTo("#glow2", { x: 0, y: 0 }, { x: -200, y: -480, duration: D, ease: "none" }, 0);
      tl.fromTo("#grid", { y: 0 }, { y: 90, duration: D, ease: "none" }, 0);
      const inUp = { opacity: 0, y: 70 };
      const shown = { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" };
      const photoIn = (sel, t, dur) => {
        tl.fromTo(sel, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.5, ease: "power3.out" }, t);
        tl.fromTo(sel + " img", { scale: 1 }, { scale: 1.06, duration: dur, ease: "none" }, t);
      };
      ${js.join("\n      ")}
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
`;
fs.writeFileSync(path.join(outDir, "index.html"), out);
console.log(`${outDir}/index.html  ${D}s, ${scenes.length} scenes`);
