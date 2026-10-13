// Turns calendar_source.json (the 14/10-12/11 reels calendar, same data as the
// "Lịch đăng Reels" artifact) into calendar.json for send_daily.js.
//   node daily/build_calendar.js
// Rules applied (owner decisions 2026-10-13):
//   - RankerNest has no Threads / X / LinkedIn: its "kênh phụ" and LinkedIn rows are dropped
//     (Facebook gets the Reel through Instagram's "Share to Facebook").
//   - RankerToolAI "kênh phụ" = X only (no verified Facebook Page / Threads for RTA).
//   - Rows marked "⏸" (EC200 out of stock) become hold notes; "(bản thắng)" reposts wait for the
//     4/11 hook-test decision, so they are notes too.
const fs = require('fs');
const path = require('path');
const src = JSON.parse(fs.readFileSync(path.join(__dirname, 'calendar_source.json'), 'utf8'));

const out = [];
for (const day of src) {
  const entries = [];
  for (const it of day.items) {
    const held = /⏸/.test(it.note || '');
    const winner = /bản thắng/.test(it.file || '');
    if (it.kind === 'video' && it.file && !held && !winner && !/LinkedIn/.test(it.ch)) {
      entries.push({ type: 'reel', site: it.site, reel: it.file, title: it.title });
    } else if (it.kind === 'post' && it.site === 'rta' && !held) {
      const channels = /Pinterest/.test(it.ch) ? ['pinterest'] : /LinkedIn/.test(it.ch) ? ['linkedin'] : ['x'];
      entries.push({ type: 'extra', site: 'rta', reel: it.file, title: it.title, channels });
    } else if (it.kind === 'post' && it.site === 'rn') {
      continue; // RN: no Threads/X/LinkedIn; Facebook comes from the Instagram share
    } else {
      const note = [it.title, it.ch, it.note].filter(Boolean).join(' · ');
      entries.push({ type: 'note', site: it.site, text: (held ? '⏸ ' : '') + note.replace(/^⏸\s*/, '') });
    }
  }
  if (entries.length) out.push({ date: day.date, entries });
}
fs.writeFileSync(path.join(__dirname, 'calendar.json'), JSON.stringify(out, null, 1) + '\n');
const count = (t) => out.reduce((n, d) => n + d.entries.filter((e) => e.type === t).length, 0);
console.log(`${out.length} days: ${count('reel')} reels, ${count('extra')} extras, ${count('note')} notes`);
