// Daily posting pack -> Telegram group "Đăng bài hàng ngày" (one forum topic per brand).
// Runs on the owner's PC from Task Scheduler ("Ranker_DangBaiHangNgay", 06:30, catches up
// at next boot). Videos are read from disk, so nothing has to be uploaded to GitHub.
//
//   node daily/send_daily.js                 # today (Vietnam time), both brands
//   node daily/send_daily.js --dry-run       # print what would be sent, send nothing
//   node daily/send_daily.js --date 2026-10-20 --only rn --force
//
// Needs: user env var TELEGRAM_BOT_TOKEN, daily/config.json (made by setup_telegram.js).
// Per day and brand it sends: header, then for each post the video + one message per
// channel (caption in <pre>, tap to copy), then a checklist. RankerNest days without a
// calendar reel take the next item from rn_queue.json (RankerNest/social/launch queue).
const fs = require('fs');
const path = require('path');

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
const vnDate = () => new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10);
const DATE = opt('--date', vnDate());
const ONLY = opt('--only', null);

// Channels per brand for a calendar reel (owner decisions 2026-10-13).
const REEL_CHANNELS = {
  rn: ['instagram', 'youtube', 'tiktok', 'facebook'],   // Pinterest reels are scheduled by CSV
  rta: ['instagram', 'youtube', 'tiktok'],
};
const BRAND = { rn: 'RankerNest', rta: 'RankerToolAI' };
const WD = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

function log(...a) { console.log(new Date().toISOString(), ...a); }

// ---------- Telegram ----------
async function tg(method, body, isForm) {
  if (DRY) return { ok: true };
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
async function sendVideo(site, file, caption) {
  const mb = (fs.statSync(file).size / 1048576).toFixed(1);
  if (DRY) { console.log(`  [video ${mb}MB] ${path.basename(file)}`); return; }
  if (fs.statSync(file).size > 49 * 1048576) throw new Error(`${path.basename(file)} is ${mb}MB, over the 50MB bot limit`);
  const fd = new FormData();
  for (const [k, v] of Object.entries(where(site))) fd.append(k, String(v));
  fd.append('caption', caption);
  fd.append('parse_mode', 'HTML');
  fd.append('supports_streaming', 'true');
  fd.append('video', new Blob([fs.readFileSync(file)], { type: 'video/mp4' }), path.basename(file));
  await tg('sendVideo', fd, true);
}

// ---------- content ----------
const kitDir = (reel) => path.join(ROOT, 'social_posts', reel, 'tg');
const kitFiles = (reel) => (fs.existsSync(kitDir(reel)) ? fs.readdirSync(kitDir(reel)).sort() : []);
const kitText = (reel, f) => fs.readFileSync(path.join(kitDir(reel), f), 'utf8').trim();
// Kits carry "Không đăng sau YYYY-MM-DD" when the video mentions a dated sale.
function expiry(reel) {
  for (const f of kitFiles(reel)) {
    const m = kitText(reel, f).match(/Không đăng sau (\d{4}-\d{2}-\d{2})/);
    if (m) return m[1];
  }
  return null;
}
const baseSlug = (reel) => reel.replace(/^rankernest_|_reel/g, '').replace(/_v\d+.*$/, '');
function reelProblem(reel) {
  if (HOLD.includes(baseSlug(reel))) return 'tạm hoãn (trong danh sách hold của config.json)';
  const exp = expiry(reel);
  if (exp && DATE > exp) return `hết hạn đăng từ ${exp}`;
  if (!fs.existsSync(path.join(VIDEOS, reel + '.mp4'))) return `thiếu file video ${reel}.mp4`;
  if (!kitFiles(reel).length) return 'thiếu bộ caption social_posts/' + reel;
  return null;
}

// Messages for one reel: the kit's own per-channel messages, filtered to the brand's channels.
function reelMessages(site, reel, channels) {
  const files = kitFiles(reel);
  const msgs = [];
  if (files.some((f) => /hooktest/.test(f))) {                // A/B/C hook variant: one combined kit
    for (const f of files) msgs.push(kitText(reel, f));
    return msgs;
  }
  const igKit = files.some((f) => /^\d+_instagram\.html$/.test(f));   // newer kits carry their own IG message
  if (channels.includes('instagram') && !igKit) {
    const cap = path.join(ROOT, 'social_videos', reel, 'caption.txt');
    if (fs.existsSync(cap)) {
      const how = site === 'rn' ? 'Bật “Chia sẻ lên Facebook” → chọn Trang RankerNest' : 'Tải video lên → dán caption';
      msgs.push(`<b>INSTAGRAM REELS</b>  <i>${how}</i>\n<pre>${esc(fs.readFileSync(cap, 'utf8').trim())}</pre>`);
    }
  }
  for (const ch of channels.filter((c) => c !== 'instagram' || igKit)) {
    const f = files.find((x) => new RegExp(`^\\d+_${ch}\\.html$`).test(x));
    if (!f) continue;
    let t = kitText(reel, f).replace(/^<b>\d+\/\d+ · /, '<b>')    // drop the kit's "3/7" numbering
      .replace('<i>Chỉ đăng nếu đã có tài khoản</i>', '<i>Tải video lên → dán caption</i>'); // both brands have TikTok now
    if (site === 'rn' && ch === 'facebook') t = '↪️ <i>Nếu đã bật “Chia sẻ lên Facebook” khi đăng Instagram: chỉ cần dán “Bình luận đầu tiên” dưới Reel trên Trang.</i>\n' + t;
    msgs.push(t);
  }
  return msgs;
}

function queuePost() {
  let i = state.rn_queue_next || 0;
  const skipped = [];
  while (i < rnQueue.length) {
    const it = rnQueue[i];
    const why = it.skip ? 'ảnh chưa được phép dùng' : it.expires && it.expires < DATE ? `hết mùa ${it.expires}` : !fs.existsSync(it.video) ? 'thiếu file video' : null;
    if (!why) return { item: it, index: i, skipped };
    skipped.push(`${it.topic} (${why})`);
    i++;
  }
  return { item: null, index: i, skipped };
}

// ---------- main ----------
async function main() {
  if (!DRY && !TOKEN) throw new Error('Thiếu biến môi trường TELEGRAM_BOT_TOKEN (xem daily/README.md)');
  if (!DRY && !config.chat_id) throw new Error('Chưa có config.json: chạy node daily/setup_telegram.js trước');
  const day = calendar.find((d) => d.date === DATE) || { entries: [] };
  const d = new Date(DATE + 'T00:00:00Z');
  const label = `${WD[d.getUTCDay()]} ${d.getUTCDate()}/${d.getUTCMonth() + 1}`;
  log(`pack for ${DATE}${DRY ? ' (dry run)' : ''}`);

  for (const site of ['rta', 'rn']) {
    if (ONLY && ONLY !== site) continue;
    state.sent[DATE] = state.sent[DATE] || {};
    if (state.sent[DATE][site] && !flag('--force')) { log(`${site}: already sent today, skip (use --force)`); continue; }

    const posts = []; const checklist = []; let queueUsed = null;
    for (const e of day.entries.filter((x) => x.site === site || x.site === 'both')) {
      if (e.type === 'note') { checklist.push(e.text); continue; }
      const problem = reelProblem(e.reel);
      if (problem) { checklist.push(`⏸ Bỏ qua ${e.title}: ${problem}`); continue; }
      posts.push(e.type === 'reel'
        ? { title: e.title, file: path.join(VIDEOS, e.reel + '.mp4'), msgs: reelMessages(site, e.reel, REEL_CHANNELS[site]) }
        : { title: e.title, file: path.join(VIDEOS, e.reel + '.mp4'), msgs: reelMessages(site, e.reel, e.channels) });
    }
    if (site === 'rn' && !day.entries.some((e) => e.site === 'rn' && e.type === 'reel' && !reelProblem(e.reel))) {
      const q = queuePost();
      if (q.skipped.length) checklist.push('Hàng đợi bỏ qua: ' + q.skipped.join(', '));
      if (q.item) {
        const m = q.item.messages;
        posts.push({ title: `${q.item.title} (bài ${q.index + 1}/${rnQueue.length} hàng đợi)`, file: q.item.video,
          msgs: ['instagram', 'youtube', 'tiktok', 'facebook', 'dm'].filter((k) => m[k]).map((k) => m[k]) });
        if (q.item.promo) checklist.push('Bài giới thiệu sản phẩm: bật Branded content trên TikTok');
        queueUsed = q.index + 1;
      } else checklist.push('Hàng đợi RankerNest đã hết: nhắn Claude thêm bài mới');
    }

    if (!posts.length && !checklist.length) { log(`${site}: nothing today`); continue; }
    const head = `📅 <b>${label} · ${BRAND[site]}</b>\n` + (posts.length
      ? `${posts.length} video hôm nay. Lưu video → (tuỳ chọn) thêm nhạc trong CapCut → đăng từng kênh theo thứ tự bên dưới. Đăng xong kênh nào thì trả lời “xong” dưới tin của kênh đó.`
      : 'Hôm nay không có video để đăng.');
    log(`${site}: ${posts.length} posts, ${checklist.length} notes`);
    await sendText(site, head);
    for (const p of posts) {
      await sendVideo(site, p.file, `🎬 <b>${esc(p.title)}</b>`);
      for (const m of p.msgs) await sendText(site, m);
    }
    const always = posts.length ? ['Đăng IG · TikTok · YouTube khoảng 6h30–8h sáng (buổi tối ở Mỹ)', 'Chỉ dán link rankernest.com / rankertoolai.com, không dán link affiliate trực tiếp'] : [];
    await sendText(site, '✅ <b>Việc hôm nay</b>\n' + [...checklist, ...always].map((t) => '• ' + esc(t)).join('\n'));

    if (!DRY) {
      state.sent[DATE][site] = new Date().toISOString();
      if (queueUsed) state.rn_queue_next = queueUsed;
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 1) + '\n');
    }
  }
}

main().catch(async (e) => {
  log('ERROR', e.message);
  // Tell the owner instead of failing silently in a hidden scheduled task.
  if (!DRY && TOKEN && config.chat_id) {
    try { await tg('sendMessage', { chat_id: config.chat_id, text: `⚠️ Gói bài ${DATE} bị lỗi: ${e.message}\nNhắn Claude: "gói bài hàng ngày bị lỗi".` }); } catch (_) {}
  }
  process.exitCode = 1;
});
