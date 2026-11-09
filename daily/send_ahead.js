// Send upcoming videos to Telegram AHEAD of their day, only the video file, so the Notion row's
// "File video" link works right away (owner taps the name in Notion → Telegram video, for weekly
// scheduling). No caption messages, no board buttons: the full card still comes on the day.
// Rows that already have a Telegram link are skipped.
//   node daily/send_ahead.js --only rn [--from 2026-11-10] [--to 2026-12-09] [--dry-run]
const fs = require('fs');
const path = require('path');
const Module = require('module');

const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const DRY = args.includes('--dry-run');
const ONLY = opt('--only', null);
const file = path.join(__dirname, 'send_daily.js');
const src = fs.readFileSync(file, 'utf8').replace(/main\(\)\.catch[\s\S]*$/, 'module.exports = { buildDay, sendVideoFile, config, BRAND, esc };');
const mod = new Module(file); mod.filename = file; mod.paths = Module._nodeModulePaths(__dirname); mod._compile(src, file);
const { buildDay, sendVideoFile, config, BRAND, esc } = mod.exports;
const notion = require('./notion');

const DB = '61da72d0d5354100a4e3c3e463c916fc';
const vnToday = new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10);
const addDay = (d, k) => new Date(Date.parse(d + 'T00:00:00Z') + k * 864e5).toISOString().slice(0, 10);
const FROM = opt('--from', addDay(vnToday, 1));
const TO = opt('--to', addDay(FROM, 30));

(async () => {
  if (!notion.enabled()) throw new Error('Thiếu NOTION_TOKEN');
  for (const site of ['rta', 'rn']) {
    if (ONLY && ONLY !== site) continue;
    for (let date = FROM; date <= TO; date = addDay(date, 1)) {
      let posts;
      try { posts = buildDay(site, date).posts; } catch (e) { console.log(date, site, 'bỏ qua:', e.message); continue; }
      for (let n = 0; n < posts.length; n++) {
        const p = posts[n];
        const id = `${date.replace(/-/g, '')}${site}${n + 1}`;
        const q = await notion.api('POST', `/databases/${DB}/query`, { filter: { property: 'Mã', rich_text: { equals: id } }, page_size: 1 });
        const page = q.results[0];
        if (!page) { console.log(date, id, 'chưa có dòng Notion (chạy notion_sync.js trước)'); continue; }
        const f = page.properties['File video'].rich_text[0];
        if (f && f.href) { console.log(date, id, 'đã có link'); continue; }
        if (!fs.existsSync(p.file)) { console.log(date, id, 'thiếu file video', p.file); continue; }
        const dd = `${date.slice(8)}/${date.slice(5, 7)}`;
        const cap = `🎬 <b>${esc(p.title)}</b>\n<i>${BRAND[site]} · ${dd} · gửi trước để hẹn giờ</i>\n📝 <a href="${page.url}">Caption từng kênh (Notion)</a>`;
        if (DRY) { console.log(date, id, 'sẽ gửi', path.basename(p.file)); continue; }
        const msgId = await sendVideoFile(site, p.file, p.reel, cap);
        const url = await notion.setVideoLink(page.id, path.basename(p.file), config.threads && config.threads[site], msgId);
        console.log(date, id, 'đã gửi →', url);
      }
    }
  }
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
