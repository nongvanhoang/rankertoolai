// Builds a RankerNest photo reel (HyperFrames composition) from a small JSON spec.
// Usage: node make_rn_reel.js spec.json outDir
// Spec: { duration?, hook: {html, photo, photoClass?}, photos: [{photo, html, note?}],
//         cards?: {kicker, items:[{v,l}], note?}, offer: {kicker, badge?, rows:[html], note?},
//         url, disclose }
const fs = require("fs");
const [specPath, outDir] = process.argv.slice(2);
const s = JSON.parse(fs.readFileSync(specPath, "utf8"));

const HOOK = 3.5, PHOTO = 3.5, CARDS = 4, OFFER = 4, CTA = 2.5;
let t = 0;
const scenes = [];
const anim = [];
const at = (x) => +x.toFixed(2);

// 1. Hook
scenes.push(`
      <div id="s0" class="scene clip" data-start="0" data-duration="${HOOK}" data-track-index="1">
        <div class="big">${s.hook.html}</div>
        <div class="photo ${s.hook.photoClass || "mediumh"}"><img src="${s.hook.photo}" alt="" /></div>
      </div>`);
anim.push(`tl.fromTo("#s0 .big", inUp, shown, 0.1);`, `photoIn("#s0 .photo", 0.6, ${HOOK - 0.6});`);
t = HOOK;

// 2. Photo scenes
s.photos.forEach((p, i) => {
  const id = `p${i}`;
  scenes.push(`
      <div id="${id}" class="scene clip" data-start="${at(t)}" data-duration="${PHOTO}" data-track-index="1">
        <div class="photo ${p.photoClass || "tall"}"><img src="${p.photo}" alt="" /></div>
        <div class="mid">${p.html}</div>${p.note ? `\n        <div class="small">${p.note}</div>` : ""}
      </div>`);
  anim.push(`photoIn("#${id} .photo", ${at(t + 0.05)}, ${PHOTO - 0.05});`, `tl.fromTo("#${id} .mid", inUp, shown, ${at(t + 0.5)});`);
  if (p.note) anim.push(`tl.fromTo("#${id} .small", inUp, shown, ${at(t + 1.0)});`);
  t += PHOTO;
});

// 3. Fact cards (optional)
if (s.cards) {
  scenes.push(`
      <div id="cards" class="scene clip center" data-start="${at(t)}" data-duration="${CARDS}" data-track-index="1">
        <div class="kicker">${s.cards.kicker}</div>
${s.cards.items.map((c) => `        <div class="stat"><span class="v">${c.v}</span><span class="l">${c.l}</span></div>`).join("\n")}${s.cards.note ? `\n        <div class="small">${s.cards.note}</div>` : ""}
      </div>`);
  anim.push(`tl.fromTo("#cards .kicker", inUp, shown, ${at(t + 0.05)});`,
    `tl.fromTo("#cards .stat", { opacity: 0, x: -100 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out", stagger: 0.4 }, ${at(t + 0.3)});`);
  if (s.cards.note) anim.push(`tl.fromTo("#cards .small", inUp, shown, ${at(t + 1.6)});`);
  t += CARDS;
}

// 4. Offer / price
scenes.push(`
      <div id="offer" class="scene clip center" data-start="${at(t)}" data-duration="${OFFER}" data-track-index="1">
        <div class="kicker">${s.offer.kicker}</div>${s.offer.badge ? `\n        <div class="ends">${s.offer.badge}</div>` : ""}
        <div class="deal">
${s.offer.rows.map((r) => `          <div class="row">${r}</div>`).join("\n")}
        </div>${s.offer.note ? `\n        <div class="small">${s.offer.note}</div>` : ""}
      </div>`);
anim.push(`tl.fromTo("#offer .kicker", inUp, shown, ${at(t + 0.05)});`);
if (s.offer.badge) anim.push(`tl.fromTo("#offer .ends", { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }, ${at(t + 0.3)});`);
anim.push(`tl.fromTo("#offer .deal", { opacity: 0, scale: 0.88 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.6)" }, ${at(t + 0.7)});`);
if (s.offer.note) anim.push(`tl.fromTo("#offer .small", inUp, shown, ${at(t + 1.5)});`);
t += OFFER;

// 5. CTA
scenes.push(`
      <div id="cta" class="scene clip center" data-start="${at(t)}" data-duration="${CTA}" data-track-index="1">
        <div class="brand"><img src="logo.svg" alt="" /><span>RankerNest</span></div>
        <div class="cta">Full review → link in bio</div>
        <div class="url">${s.url}</div>
        <div class="disclose">${s.disclose}</div>
      </div>`);
anim.push(`tl.fromTo("#cta .brand", inUp, shown, ${at(t + 0.05)});`,
  `tl.fromTo("#cta .cta", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)" }, ${at(t + 0.3)});`,
  `tl.fromTo("#cta .url", inUp, shown, ${at(t + 0.6)});`,
  `tl.fromTo("#cta .disclose", { opacity: 0 }, { opacity: 1, duration: 0.3 }, ${at(t + 0.9)});`);
t += CTA;
const TOTAL = at(t);

const tpl = fs.readFileSync(__dirname + "/rn_reel_template.html", "utf8");
const html = tpl
  .replace(/__TOTAL__/g, TOTAL)
  .replace("<!--SCENES-->", scenes.join("\n"))
  .replace("//ANIM", anim.join("\n      "));
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outDir + "/index.html", html);
console.log(outDir, "total", TOTAL);
