// Weekly price check: are the prices in our videos/kits still the live prices?
// Usage: node reel_tools/price_check.js [--push]
// Writes social_posts/_gia_<date>/tg/01_prices.html (+ GIA.txt); --push commits it on this branch
// so the "Send posting kit to Telegram" workflow delivers it.
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "price_watch.json"), "utf8"));
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36";
const money = (n) => "$" + n.toFixed(2).replace(/\.00$/, "");
const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

(async () => {
  const bad = [], ok = [];
  for (const it of cfg.items) {
    try {
      const r = await fetch(it.url, { headers: { "User-Agent": UA }, redirect: "follow" });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const j = await r.json();
      const prices = j.variants.filter((v) => v.available !== false).map((v) => v.price / 100);
      const all = j.variants.map((v) => v.price / 100);
      const live = [...new Set(prices.length ? prices : all)].sort((a, b) => a - b);
      const problems = [];
      for (const p of it.expect || []) if (!all.includes(p)) problems.push(`video ghi ${money(p)}, web giờ ${live.slice(0, 4).map(money).join(" / ")}`);
      if (it.min != null && Math.min(...all) !== it.min) problems.push(`video ghi từ ${money(it.min)}, web giờ từ ${money(Math.min(...all))}`);
      if (it.compareAt != null) {
        const ca = [...new Set(j.variants.map((v) => (v.compare_at_price || 0) / 100))];
        if (!ca.includes(it.compareAt)) problems.push(`giá gốc ghi ${money(it.compareAt)}, web giờ ${ca.filter(Boolean).map(money).join(" / ") || "không còn giá gốc"}`);
      }
      if (!prices.length) problems.push("HẾT HÀNG trên web");
      (problems.length ? bad : ok).push({ it, problems });
    } catch (e) {
      bad.push({ it, problems: ["không đọc được giá (" + e.message + "), kiểm tay"] });
    }
  }
  const day = new Date().toISOString().slice(0, 10);
  let m = `<b>🏷️ Kiểm giá ${day}</b> · ${ok.length}/${cfg.items.length} giá còn đúng`;
  if (bad.length) {
    m += `\n\n<b>⚠️ Giá đã đổi, ĐỪNG đăng lại các video này cho tới khi sửa (nhắn Claude):</b>`;
    for (const { it, problems } of bad) m += `\n• <b>${esc(it.name)}</b>: ${esc(problems.join("; "))}\n  <i>video: ${esc(it.videos)}</i>`;
  } else m += "\n\n✅ Mọi giá trong video vẫn đúng. Đăng lại thoải mái.";
  m += `\n\n<i>Kiểm tay: ${esc(cfg.manual.join(" · "))}</i>`;
  const out = path.join(ROOT, "social_posts", `_gia_${day}`);
  fs.mkdirSync(path.join(out, "tg"), { recursive: true });
  fs.writeFileSync(path.join(out, "tg", "01_prices.html"), m);
  fs.writeFileSync(path.join(out, "GIA.txt"), m.replace(/<\/?[bi]>/g, ""));
  console.log(m.replace(/<\/?[bi]>/g, ""));
  if (process.argv.includes("--push")) {
    const git = (...a) => execFileSync("git", ["-C", ROOT, ...a], { stdio: "inherit" });
    try { git("pull", "-q", "--rebase", "origin", "video-test-synthesia"); } catch {}
    git("add", path.relative(ROOT, out).split(path.sep).join("/"));
    try { git("commit", "-q", "-m", `Weekly price check ${day}`); } catch {}
    git("push", "-q", "origin", "video-test-synthesia");
  }
})();
