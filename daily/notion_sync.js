// Fill the Notion board ahead of time with every scheduled video (one row each), so the
// "🗓 Lịch" view shows the whole plan. Safe to re-run: rows are matched by "Mã" and skipped.
//   node daily/notion_sync.js                    # from today to the end of the calendar
//   node daily/notion_sync.js --from 2026-10-18 --to 2026-11-12
// Uses the same day-building logic as send_daily.js (queue order included).
const fs = require('fs');
const path = require('path');
const Module = require('module');

const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
process.argv.push('--dry-run');                  // load send_daily.js without sending anything
const file = path.join(__dirname, 'send_daily.js');
const src = fs.readFileSync(file, 'utf8').replace(/main\(\)\.catch[\s\S]*$/, 'module.exports = { buildDay, state, calendar };');
const mod = new Module(file); mod.filename = file; mod.paths = Module._nodeModulePaths(__dirname); mod._compile(src, file);
const { buildDay, state, calendar } = mod.exports;
const notion = require('./notion');

const vnToday = new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10);
const FROM = opt('--from', vnToday);
const TO = opt('--to', '9999-12-31');

(async () => {
  if (!notion.enabled()) throw new Error('Thiếu biến môi trường NOTION_TOKEN');
  let made = 0;
  // Every day in the range (queue days have no calendar entry but still get a RankerNest video).
  const last = TO !== '9999-12-31' ? TO : calendar.map((d) => d.date).sort().pop();
  const days = [];
  for (let t = Date.parse(FROM + 'T00:00:00Z'); t <= Date.parse(last + 'T00:00:00Z'); t += 864e5) days.push(new Date(t).toISOString().slice(0, 10));
  for (const date of days) {
    for (const site of ['rta', 'rn']) {
      const { posts, queueUsed } = buildDay(site, date);
      if (queueUsed) state.rn_queue_next = queueUsed;      // in memory only: send_daily owns state.json
      for (let n = 0; n < posts.length; n++) {
        const p = posts[n];
        const id = `${date.replace(/-/g, '')}${site}${n + 1}`;
        const page = await notion.ensurePage({ id, site, date, title: p.title, channels: p.channels, kit: p.kit, fileName: path.basename(p.file) });
        console.log(`${id}  ${p.title}  ${page.url}`);
        made++;
      }
    }
  }
  console.log(`${made} dòng (đã có thì bỏ qua)`);
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
