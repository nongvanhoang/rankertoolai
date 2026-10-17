// Daily posting pack -> Telegram group "Đăng bài hàng ngày" (one forum topic per brand).
// Runs on the owner's PC from Task Scheduler ("Ranker_DangBaiHangNgay", 06:30, catches up
// at next boot). Videos are read from disk, so nothing has to be uploaded to GitHub.
//
//   node daily/send_daily.js                 # today (Vietnam time), both brands
//   node daily/send_daily.js --dry-run       # print what would be sent, send nothing
//   node daily/send_daily.js --date 2026-10-20 --only rn --force
//
// Each video becomes ONE card: the original MP4 as a file (not re-compressed by Telegram,
// ready for CapCut) whose caption holds the buttons, drawn by the posting-board Worker
// (daily/worker): ☐/✅ per channel, 📋 caption picker, 💬 pinned comments, ⏭ skip.
// The Worker remembers what was posted, so the board, /chuadang and duplicate warnings work
// even when this PC is off. Before today's cards it lists cards still not fully posted, and it
// catches up days the PC missed (up to 3 days back). If the Worker can't be reached it falls
// back to the old one-message-per-channel pack so the day is never lost.
//
// Needs user env vars TELEGRAM_BOT_TOKEN and RANKER_BOT_API_KEY, daily/config.json.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const DIR = __dirname;
const ROOT = path.dirname(DIR);
const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);

const readJson = (f, d) => (fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : d);
const config = readJson(path.join(DIR, 'config.json'), {});
const calendar = readJson(path.join(DIR, 'calendar.json'), []);
const rnQueue = readJson(path.join(DIR, 'rn_queue.json'), { items: [] }).items;
const STATE_FILE = path.join(DIR, 'state.json');
const state = readJson(STATE_FILE, { sent: {}, rn_queue_next: 0 });

const VIDEOS = config.videos_dir || 'C:\\Users\\Admin\\Videos\\RankerToolAI_reels';
const HOLD = config.hold || [];           // reel slugs paused (e.g. out of stock)
const DRY = flag('--dry-run');
const TOKEN = require('./token')();
const API_KEY = require('./token').userEnv('RANKER_BOT_API_KEY');
const BOARD = config.board_url || '';     // posting-board Worker, e.g. https://ranker-posting.<sub>.workers.dev
const vnDate = (ms = Date.now()) => new Date(ms + 7 * 3600e3).toISOString().slice(0, 10);
const TODAY = opt('--date', vnDate());
const ONLY = opt('--only', null);
const CATCH_UP_DAYS = 3;

// Channels per brand (owner 2026-10-14: RankerNest now also has X + LinkedIn).
// Pinterest stays on its own calendar rows (RankerNest reels go through the Pinterest CSV).
const REEL_CHANNELS = {
  rn: ['instagram', 'facebook', 'youtube', 'tiktok', 'x', 'linkedin'],
  rta: ['instagram', 'youtube', 'tiktok', 'x', 'linkedin'],
};
const BRAND = { rn: 'RankerNest', rta: 'RankerToolAI' };
const WD = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const dayLabel = (date) => { const d = new Date(date + 'T00:00:00Z'); return `${WD[d.getUTCDay()]} ${d.getUTCDate()}/${d.getUTCMonth() + 1}`; };

function log(...a) { console.log(new Date().toISOString(), ...a); }

// ---------- Telegram ----------
async function tg(method, body, isForm) {
  if (DRY) return { ok: true, result: { message_id: 0 } };
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(`https://api.telegram.org/bot${TOKEN}/${method}`, isForm
      ? { method: 'POST', body }
      : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await res.json().catch(() => ({}));
    if (j.ok) { await new Promise((r) => setTimeout(r, 400)); return j; }
    if (j.parameters && j.parameters.retry_after) { await new Promise((r) => setTimeout(r, (j.parameters.retry_after + 1) * 1000)); continue; }
    throw new Error(`${method}: ${j.description || res.status}`);
  }
  throw new Error(`${method}: too many retries`);
}
const where = (site) => ({ chat_id: config.chat_id, ...(config.threads && config.threads[site] ? { message_thread_id: config.threads[site] } : {}) });

async function sendText(site, html) {
  for (const chunk of splitHtml(html)) {
    if (DRY) { console.log(`  [msg ${chunk.length} chars] ${chunk.split('\n')[0].replace(/<[^>]+>/g, '').slice(0, 90)}`); continue; }
    await tg('sendMessage', { ...where(site), text: chunk, parse_mode: 'HTML', disable_web_page_preview: true });
  }
}
// Telegram caps a message at 4096 chars; split on blank lines outside <pre> if ever needed.
function splitHtml(html) {
  if (html.length <= 4000) return [html];
  const parts = []; let cur = '';
  for (const block of html.split(/\n\n(?![^<]*<\/pre>)/)) {
    if ((cur + '\n\n' + block).length > 4000 && cur) { parts.push(cur); cur = block; } else cur = cur ? cur + '\n\n' + block : block;
  }
  if (cur) parts.push(cur);
  return parts;
}
// Small JPEG preview for the file card (Telegram: <=320px, <=200KB). Cover image if we have one.
function thumbFor(reel, file) {
  const out = path.join(os.tmpdir(), `thumb_${reel}.jpg`);
  const cover = path.join(VIDEOS, 'covers', `${reel}_cover.jpg`);
  try {
    const src = fs.existsSync(cover) ? ['-i', cover] : ['-ss', '2.2', '-i', file];
    execFileSync('ffmpeg', ['-v', 'error', '-threads', '1', '-y', ...src, '-frames:v', '1', '-vf', 'scale=180:320:force_original_aspect_ratio=decrease', '-q:v', '5', out], { stdio: 'ignore' });
    return fs.existsSync(out) ? out : null;
  } catch (_) { return null; }
}
// The video as a FILE (original quality). Returns the message id; caption = temporary card text.
async function sendVideoFile(site, file, reel, captionHtml) {
  const mb = (fs.statSync(file).size / 1048576).toFixed(1);
  if (DRY) { console.log(`  [file ${mb}MB] ${path.basename(file)}`); return 0; }
  if (fs.statSync(file).size > 49 * 1048576) throw new Error(`${path.basename(file)} is ${mb}MB, over the 50MB bot limit`);
  const fd = new FormData();
  for (const [k, v] of Object.entries(where(site))) fd.append(k, String(v));
  fd.append('caption', captionHtml);
  fd.append('parse_mode', 'HTML');
  fd.append('disable_content_type_detection', 'true');
  fd.append('document', new Blob([fs.readFileSync(file)], { type: 'video/mp4' }), path.basename(file));
  const th = thumbFor(reel, file);
  if (th) fd.append('thumbnail', new Blob([fs.readFileSync(th)], { type: 'image/jpeg' }), 'thumb.jpg');
  const j = await tg('sendDocument', fd, true);
  return j.result.message_id;
}

// ---------- posting board (Worker) ----------
async function board(pathname, body) {
  if (!BOARD || !API_KEY) throw new Error('chưa cấu hình board_url / RANKER_BOT_API_KEY');
  const res = await fetch(BOARD + pathname, body
    ? { method: 'POST', headers: { 'content-type': 'application/json', 'x-api-key': API_KEY }, body: JSON.stringify(body) }
    : { headers: { 'x-api-key': API_KEY } });
  if (!res.ok) throw new Error(`board ${pathname}: HTTP ${res.status}`);
  return res.json();
}
let boardOk = !!(BOARD && API_KEY);

// ---------- content ----------
const kitDir = (reel) => path.join(ROOT, 'social_posts', reel, 'tg');
const kitFiles = (reel) => (fs.existsSync(kitDir(reel)) ? fs.readdirSync(kitDir(reel)).sort() : []);
const kitText = (reel, f) => fs.readFileSync(path.join(kitDir(reel), f), 'utf8').trim();
function expiry(reel) {
  for (const f of kitFiles(reel)) {
    const m = kitText(reel, f).match(/Không đăng sau (\d{4}-\d{2}-\d{2})/);
    if (m) return m[1];
  }
  return null;
}
const baseSlug = (reel) => reel.replace(/^rankernest_|_reel/g, '').replace(/_v\d+.*$/, '');
function reelProblem(reel, date) {
  if (HOLD.includes(baseSlug(reel))) return 'tạm hoãn (trong danh sách hold của config.json)';
  const exp = expiry(reel);
  if (exp && date > exp) return `hết hạn đăng từ ${exp}`;
  if (!fs.existsSync(path.join(VIDEOS, reel + '.mp4'))) return `thiếu file video ${reel}.mp4`;
  if (!kitFiles(reel).length) return 'thiếu bộ caption social_posts/' + reel;
  return null;
}

// Split one channel message into the caption part and the comment part
// (blocks "<b>Bình luận …:</b>\n<pre>…</pre>" go to the 💬 button).
function splitKit(html) {
  const blocks = html.split(/\n+(?=<b>)/);       // fields: "<b>Label:</b>\n<pre>…</pre>"
  const isComment = (b) => /^<b>[^<]*(Bình luận|Tin nhắn)/i.test(b);
  return {
    caption: blocks.filter((b) => !isComment(b)).join('\n\n').replace(/^<b>\d+\/\d+ · /, '<b>'),
    comment: blocks.filter(isComment).join('\n\n'),
  };
}
const FIELD_CH = [[/^INSTAGRAM/i, 'instagram'], [/^YOUTUBE/i, 'youtube'], [/^TIKTOK/i, 'tiktok']];
// Per-channel {caption, comment} for a reel's kit.
function reelKit(reel) {
  const kit = {};
  const files = kitFiles(reel);
  const hook = files.find((f) => /hooktest/.test(f));
  if (hook) {                                     // A/B/C variant: one message with IG/YT/TikTok fields
    const html = kitText(reel, hook);
    for (const block of html.split(/\n+(?=<b>)/)) {
      const label = (block.match(/^<b>([^<:]*)/) || [])[1] || '';
      const hit = FIELD_CH.find(([re]) => re.test(label));
      if (!hit) continue;
      const ch = hit[1];
      kit[ch] = kit[ch] || { caption: `<b>${ch === 'instagram' ? 'INSTAGRAM' : ch === 'youtube' ? 'YOUTUBE SHORTS' : 'TIKTOK'}</b>`, comment: '' };
      kit[ch].caption += '\n\n' + block;
    }
    return kit;
  }
  for (const f of files) {
    const m = f.match(/^\d+_([a-z]+)\.html$/);
    if (!m || m[1] === 'head') continue;
    kit[m[1]] = splitKit(kitText(reel, f));
  }
  if (!kit.instagram) {                           // older kits: Instagram caption lives in caption.txt
    const cap = path.join(ROOT, 'social_videos', reel, 'caption.txt');
    if (fs.existsSync(cap)) kit.instagram = { caption: `<b>INSTAGRAM REELS</b>\n<pre>${esc(fs.readFileSync(cap, 'utf8').trim())}</pre>`, comment: '' };
  }
  if (kit.facebook && kit.instagram) kit.facebook.caption = '↪️ <i>Nếu đã bật “Chia sẻ lên Facebook” khi đăng Instagram: chỉ cần dán bình luận đầu tiên (nút 💬).</i>\n' + kit.facebook.caption;
  return kit;
}
function queueKit(item) {
  const kit = {};
  for (const ch of ['instagram', 'youtube', 'tiktok', 'facebook']) if (item.messages[ch]) kit[ch] = splitKit(item.messages[ch]);
  if (item.messages.dm && kit.instagram) kit.instagram.comment = [kit.instagram.comment, item.messages.dm].filter(Boolean).join('\n\n');
  return kit;
}

function queuePost(date) {
  let i = state.rn_queue_next || 0;
  const skipped = [];
  while (i < rnQueue.length) {
    const it = rnQueue[i];
    const why = it.skip ? 'ảnh chưa được phép dùng' : it.expires && it.expires < date ? `hết mùa ${it.expires}` : !fs.existsSync(it.video) ? 'thiếu file video' : null;
    if (!why) return { item: it, index: i, skipped };
    skipped.push(`${it.topic} (${why})`);
    i++;
  }
  return { item: null, index: i, skipped };
}

// Posts (cards) + notes for one brand on one date.
function buildDay(site, date) {
  const day = calendar.find((d) => d.date === date) || { entries: [] };
  const entries = day.entries.filter((x) => x.site === site || x.site === 'both');
  const posts = []; const notes = []; let queueUsed = null;
  const reelsToday = new Set(entries.filter((e) => e.type === 'reel').map((e) => e.reel));
  for (const e of entries) {
    if (e.type === 'note') { notes.push(e.text); continue; }
    const problem = reelProblem(e.reel, date);
    if (problem) { notes.push(`⏸ Bỏ qua ${e.title}: ${problem}`); continue; }
    if (e.type === 'reel') {
      posts.push({ title: e.title, reel: e.reel, file: path.join(VIDEOS, e.reel + '.mp4'), channels: REEL_CHANNELS[site], kit: reelKit(e.reel) });
    } else {
      // Extra rows: drop channels the main card already covers (cards now include X/LinkedIn).
      const chans = (e.channels || []).filter((c) => !REEL_CHANNELS[site].includes(c));
      if (!chans.length) continue;
      const main = posts.find((p) => p.reel === e.reel);
      if (main && reelsToday.has(e.reel)) { main.channels = [...main.channels, ...chans]; continue; }
      posts.push({ title: e.title, reel: e.reel, file: path.join(VIDEOS, e.reel + '.mp4'), channels: chans, kit: reelKit(e.reel) });
    }
  }
  if (site === 'rn' && !entries.some((e) => e.type === 'reel' && !reelProblem(e.reel, date))) {
    const q = queuePost(date);
    if (q.skipped.length) notes.push('Hàng đợi bỏ qua: ' + q.skipped.join(', '));
    if (q.item) {
      const kit = queueKit(q.item);
      posts.push({ title: `${q.item.title} (hàng đợi ${q.index + 1}/${rnQueue.length})`, reel: q.item.topic, file: q.item.video, channels: Object.keys(kit), kit });
      if (q.item.promo) notes.push('Bài giới thiệu sản phẩm: bật Branded content trên TikTok');
      queueUsed = q.index + 1;
    } else notes.push('Hàng đợi RankerNest đã hết: nhắn Claude thêm bài mới');
  }
  return { posts, notes, queueUsed };
}

// Fallback (Worker unreachable): the old pack, one message per channel.
async function sendOldStyle(site, p) {
  for (const ch of p.channels) {
    const k = p.kit[ch];
    if (k) await sendText(site, [k.caption, k.comment].filter(Boolean).join('\n\n'));
  }
}

async function sendCard(site, date, n, p) {
  const id = `${date.replace(/-/g, '')}${site}${n}`;
  const already = boardOk && !DRY ? await board(`/api/posted?reel=${encodeURIComponent(p.reel)}`).catch(() => ({})) : {};
  if (p.channels.length && p.channels.every((c) => already[c])) return `↩︎ ${p.title}: đã đăng đủ kênh từ trước, không gửi lại`;
  const temp = `🎬 <b>${esc(p.title)}</b>\n<i>${BRAND[site]} · ${date.slice(8)}/${date.slice(5, 7)}</i>` + (boardOk ? '\n(đang tải nút bấm…)' : '');
  const msgId = await sendVideoFile(site, p.file, p.reel, temp);
  if (DRY) { console.log(`  [card ${id}] ${p.title} · ${p.channels.join(', ')} · caption cho: ${Object.keys(p.kit).join(', ')}`); return null; }
  if (boardOk) {
    try {
      await board('/api/register', { id, site, date, title: p.title, reel: p.reel, channels: p.channels,
        chat_id: config.chat_id, thread_id: config.threads[site], card_msg: msgId, card_is_caption: true, kit: p.kit });
      return null;
    } catch (e) { boardOk = false; log('board register failed, falling back:', e.message); }
  }
  await sendOldStyle(site, p);
  return null;
}

async function main() {
  if (!DRY && !TOKEN) throw new Error('Thiếu biến môi trường TELEGRAM_BOT_TOKEN (xem daily/README.md)');
  if (!DRY && !config.chat_id) throw new Error('Chưa có config.json: chạy node daily/setup_telegram.js trước');
  log(`pack for ${TODAY}${DRY ? ' (dry run)' : ''}${boardOk ? '' : ' (no board: old-style messages)'}`);

  for (const site of ['rta', 'rn']) {
    if (ONLY && ONLY !== site) continue;
    // Today plus any of the last CATCH_UP_DAYS days the PC missed (was off at 06:30).
    const dates = [];
    for (let k = CATCH_UP_DAYS; k >= 1; k--) {
      const d = new Date(Date.parse(TODAY + 'T00:00:00Z') - k * 864e5).toISOString().slice(0, 10);
      if (!(state.sent[d] && state.sent[d][site]) && !flag('--date')) dates.push(d);
    }
    if (!(state.sent[TODAY] && state.sent[TODAY][site]) || flag('--force')) dates.push(TODAY);
    if (!dates.length) { log(`${site}: already sent today, skip (use --force)`); continue; }

    // Carried-over cards (sent earlier, not fully posted): one message with links.
    let carry = [];
    if (boardOk && !DRY) {
      try { carry = await board(`/api/pending?site=${site}&before=${dates[0]}`); }
      catch (e) { boardOk = false; log('board pending failed:', e.message); }
    }

    for (const date of dates) {
      const { posts, notes, queueUsed } = buildDay(site, date);
      const late = date !== TODAY;
      if (!posts.length && !notes.length && !(date === TODAY && carry.length)) { log(`${site} ${date}: nothing`); continue; }
      const head = `📅 <b>${dayLabel(date)} · ${BRAND[site]}</b>${late ? ' <i>(gửi bù, máy tắt hôm đó)</i>' : ''}\n` + (posts.length
        ? `${posts.length} video. Lưu file video → (tuỳ chọn) thêm nhạc trong CapCut → đăng.` +
          (boardOk ? ' Đăng xong kênh nào bấm tên kênh đó để ✅.' : ' Caption từng kênh ở các tin ngay dưới video.')
        : 'Không có video mới.');
      log(`${site} ${date}: ${posts.length} cards, ${notes.length} notes, ${date === TODAY ? carry.length : 0} carried`);
      await sendText(site, head);
      if (date === TODAY && carry.length) {
        await sendText(site, `📌 <b>Còn nợ từ hôm trước</b> (bấm tên để tới thẻ)\n` +
          carry.map((c) => `• <a href="${c.link}">${esc(c.title)}</a> (${+c.date.slice(8)}/${+c.date.slice(5, 7)}): còn ${c.pending.length} kênh`).join('\n'));
      }
      const extra = [];
      for (let n = 0; n < posts.length; n++) { const r = await sendCard(site, date, n + 1, posts[n]); if (r) extra.push(r); }
      const always = posts.length ? ['Đăng IG · TikTok · YouTube khoảng 6h30–8h sáng (buổi tối ở Mỹ)', 'Chỉ dán link rankernest.com / rankertoolai.com, không dán link affiliate trực tiếp', 'Gõ /chuadang để xem mọi bài còn nợ'] : [];
      const lines = [...notes, ...extra, ...always];
      if (lines.length) await sendText(site, '✅ <b>Ghi chú</b>\n' + lines.map((t) => '• ' + esc(t)).join('\n'));

      if (!DRY) {
        state.sent[date] = state.sent[date] || {};
        state.sent[date][site] = new Date().toISOString();
        if (queueUsed) state.rn_queue_next = queueUsed;
        fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 1) + '\n');
      }
    }
  }
}

main().catch(async (e) => {
  log('ERROR', e.message);
  // Tell the owner instead of failing silently in a hidden scheduled task.
  if (!DRY && TOKEN && config.chat_id) {
    try { await tg('sendMessage', { chat_id: config.chat_id, text: `⚠️ Gói bài ${TODAY} bị lỗi: ${e.message}\nNhắn Claude: "gói bài hàng ngày bị lỗi".` }); } catch (_) {}
  }
  process.exitCode = 1;
});
