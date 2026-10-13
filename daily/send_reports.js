// Sends new weekly report folders (social_posts/_gia_<date>, social_posts/_bao_cao_<date>)
// into the General topic of the daily-posting group. Called at the end of
// reel_tools/run_weekly_report.ps1; remembers what it sent in daily/state.json.
//   node daily/send_reports.js [--dry-run]
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const POSTS = path.join(path.dirname(DIR), 'social_posts');
const DRY = process.argv.includes('--dry-run');
const TOKEN = require('./token')();
const config = JSON.parse(fs.readFileSync(path.join(DIR, 'config.json'), 'utf8'));
const STATE = path.join(DIR, 'state.json');
const state = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : { sent: {}, rn_queue_next: 0 };
state.reports_sent = state.reports_sent || [];

(async () => {
  if (!DRY && (!TOKEN || !config.chat_id)) throw new Error('Thiếu TELEGRAM_BOT_TOKEN hoặc config.json (chạy setup_telegram.js)');
  const folders = fs.readdirSync(POSTS).filter((n) => /^_(gia|bao_cao)_/.test(n) && !state.reports_sent.includes(n)).sort();
  for (const name of folders) {
    const tg = path.join(POSTS, name, 'tg');
    if (!fs.existsSync(tg)) continue;
    for (const f of fs.readdirSync(tg).sort()) {
      const text = fs.readFileSync(path.join(tg, f), 'utf8').trim();
      if (DRY) { console.log(`[${name}/${f}] ${text.length} chars`); continue; }
      const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: config.chat_id, text: text.slice(0, 4096), parse_mode: 'HTML', disable_web_page_preview: true }),
      });
      const j = await r.json();
      if (!j.ok) throw new Error(`${name}/${f}: ${j.description}`);
    }
    if (!DRY) state.reports_sent.push(name);
    console.log('sent', name);
  }
  if (!DRY) fs.writeFileSync(STATE, JSON.stringify(state, null, 1) + '\n');
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
