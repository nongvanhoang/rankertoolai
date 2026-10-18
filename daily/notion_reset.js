// Archive Notion board rows from a date on (e.g. rows pre-filled before their video existed),
// so notion_sync.js can fill them again. Only rows with no channel ticked are archived.
//   node daily/notion_reset.js --from 2026-11-13 [--dry-run]
const { userEnv } = require('./token');
const args = process.argv.slice(2);
const FROM = args[args.indexOf('--from') + 1];
const DRY = args.includes('--dry-run');
const TOKEN = userEnv('NOTION_TOKEN');
const DB = '61da72d0d5354100a4e3c3e463c916fc';
const H = { Authorization: `Bearer ${TOKEN}`, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' };
const TICKS = ['IG', 'FB', 'YouTube', 'TikTok', 'Pinterest', 'X', 'LinkedIn'];

(async () => {
  if (!FROM || !TOKEN) throw new Error('usage: --from YYYY-MM-DD (needs NOTION_TOKEN)');
  let cursor, n = 0;
  do {
    const r = await fetch(`https://api.notion.com/v1/databases/${DB}/query`, { method: 'POST', headers: H,
      body: JSON.stringify({ filter: { property: 'Ngày', date: { on_or_after: FROM } }, page_size: 100, ...(cursor ? { start_cursor: cursor } : {}) }) });
    const j = await r.json();
    for (const p of j.results) {
      if (TICKS.some((t) => p.properties[t] && p.properties[t].checkbox)) continue;   // keep rows with real progress
      const title = (p.properties.Video.title[0] || {}).plain_text;
      if (!DRY) await fetch(`https://api.notion.com/v1/pages/${p.id}`, { method: 'PATCH', headers: H, body: JSON.stringify({ archived: true }) });
      console.log(`${DRY ? 'would archive' : 'archived'}: ${p.properties['Ngày'].date.start} ${title}`);
      n++;
    }
    cursor = j.has_more ? j.next_cursor : null;
  } while (cursor);
  console.log(n, 'rows');
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
