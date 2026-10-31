// Weekly scheduling pack (owner 2026-10-29, "phương án 1"): instead of posting 7 channels by hand every
// day, the owner sits down once a week and schedules each channel's videos in that platform's OWN
// scheduler (Meta Business Suite, YouTube Studio, TikTok Studio, Pinterest, LinkedIn, X). Official tools
// only: no browser bots. Quora and Reddit stay daily and manual.
//
// Writes one row per site × channel × week into the Notion DB "Hẹn giờ tuần" with every day's video
// file, suggested time and copy. send_daily.js then auto-ticks channels whose week row is checked.
//   node daily/weekly_schedule.js                       # next Monday..Sunday
//   node daily/weekly_schedule.js --from 2026-11-02 [--dry-run] [--refresh]
const fs = require('fs');
const path = require('path');
const Module = require('module');

const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const DRY = args.includes('--dry-run');
const REFRESH = args.includes('--refresh');
process.argv.push('--dry-run');                 // load send_daily.js without sending anything
const file = path.join(__dirname, 'send_daily.js');
const src = fs.readFileSync(file, 'utf8').replace(/main\(\)\.catch[\s\S]*$/, 'module.exports = { buildDay, state, VIDEOS };');
const mod = new Module(file); mod.filename = file; mod.paths = Module._nodeModulePaths(__dirname); mod._compile(src, file);
const { buildDay, state, VIDEOS } = mod.exports;
const notion = require('./notion');
const { api, rt, unesc } = notion;

const WEEK_DB = notion.WEEK_DB;
const SITE = { rn: 'RankerNest', rta: 'RankerToolAI' };
// Channels scheduled weekly. Quora/Reddit have no safe scheduler, they stay in the daily pack.
const CH = notion.WEEKLY_CHANNELS;
const TOOL = {
  instagram: { time: '07:00', tool: 'Meta Business Suite (business.facebook.com) → Tạo Reel → chọn Instagram → Lên lịch' },
  facebook: { time: '07:00', tool: 'Meta Business Suite → Tạo Reel → chọn Facebook → Lên lịch (hẹn cùng lúc với Instagram được, nhưng dán caption riêng của Facebook)' },
  youtube: { time: '07:00', tool: 'YouTube Studio → Tạo → Tải video lên → bước Chế độ hiển thị → Lên lịch' },
  tiktok: { time: '07:30', tool: 'tiktok.com/tiktokstudio/upload (trên máy tính) → Lên lịch (tối đa 10 ngày trước)' },
  pinterest: { time: '08:00', tool: 'Pinterest → Tạo Pin → "Xuất bản vào thời điểm sau"' },
  x: { time: '20:30', tool: 'x.com → soạn bài → biểu tượng lịch (Schedule). Không có nút này thì đăng tay hằng ngày' },
  linkedin: { time: '21:00', tool: 'LinkedIn (trang công ty) → Bắt đầu bài đăng → biểu tượng đồng hồ' },
};
const WD = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
const ymd = (t) => new Date(t).toISOString().slice(0, 10);
const vnToday = ymd(Date.now() + 7 * 3600e3);
const nextMonday = () => { const t = Date.parse(vnToday + 'T00:00:00Z'); const d = new Date(t).getUTCDay(); return ymd(t + ((8 - d) % 7 || 7) * 864e5); };
const FROM = opt('--from', nextMonday());
const DAYS = Array.from({ length: 7 }, (_, i) => ymd(Date.parse(FROM + 'T00:00:00Z') + i * 864e5));
const TO = DAYS[6];
const dm = (d) => `${+d.slice(8)}/${+d.slice(5, 7)}`;
const label = (d) => `${WD[new Date(d + 'T00:00:00Z').getUTCDay()]} ${dm(d)}`;

// "<b>Label:</b>\n<pre>text</pre>" pairs and the "Cài đặt" bullets out of a Telegram-HTML kit message.
function fields(html) {
  const out = [];
  for (const b of html.split(/\n+(?=<b>)/)) {
    const l = unesc((b.match(/^<b>([^<]*)<\/b>/) || [])[1] || '').replace(/:$/, '');
    const pre = b.match(/<pre>([\s\S]*?)<\/pre>/);
    if (pre) out.push([l, unesc(pre[1])]);
  }
  return out;
}
function settings(html) {
  const m = html.match(/<b>Cài đặt:<\/b>\n([\s\S]*)$/);
  return m ? unesc(m[1].replace(/<[^>]+>/g, '')).split('\n').map((x) => x.replace(/^•\s*/, '').trim()).filter(Boolean) : [];
}
const para = (rich) => ({ type: 'paragraph', paragraph: { rich_text: rich } });
const code = (text) => ({ type: 'code', code: { language: 'plain text', rich_text: rt(text) } });

(async () => {
  if (!notion.enabled()) throw new Error('Thiếu biến môi trường NOTION_TOKEN');
  const plan = { rn: {}, rta: {} };              // site -> date -> [posts]
  for (const date of DAYS) for (const site of ['rta', 'rn']) {
    const { posts, queueUsed } = buildDay(site, date);
    if (queueUsed) state.rn_queue_next = queueUsed;   // in memory only
    plan[site][date] = posts;
  }
  let made = 0;
  for (const site of ['rta', 'rn']) for (const [ch, name] of Object.entries(CH)) {
    const meta = TOOL[ch];
    const days = DAYS.map((d) => ({ d, posts: plan[site][d].filter((p) => p.channels.includes(ch) && p.kit[ch]) })).filter((x) => x.posts.length);
    if (!days.length) continue;
    const n = days.reduce((a, x) => a + x.posts.length, 0);
    const id = `wk${FROM.replace(/-/g, '')}${site}-${ch}`;
    const title = `${SITE[site]} · ${name} · ${dm(FROM)}–${dm(TO)}`;
    const kids = [
      { type: 'callout', callout: { icon: { type: 'emoji', emoji: '🗓' }, rich_text: rt(
        `Hẹn giờ ${n} video trong: ${meta.tool}. Giờ gợi ý ${meta.time} (giờ Việt Nam). File video ở thư mục ${VIDEOS}, ảnh bìa trong thư mục covers. ` +
        `Nhạc: đã lồng sẵn (nhạc Mixkit dưới giọng đọc), dùng đúng file "_nhac.mp4" ghi ở từng ngày, không cần CapCut, không thêm nhạc trong app nữa. ` +
        `Hẹn xong cả tuần → tích ô "Đã hẹn giờ" ở đầu trang.`) } },
      ...settings(days[0].posts[0].kit[ch].caption).map((x) => ({ type: 'bulleted_list_item', bulleted_list_item: { rich_text: rt(x) } })),
    ];
    for (const { d, posts } of days) for (const p of posts) {
      const k = p.kit[ch];
      kids.push({ type: 'heading_3', heading_3: { rich_text: rt(`${label(d)} · ${meta.time} · ${p.title}`) } });
      kids.push(para(rt(`File: ${path.basename(p.file)}  ·  Ảnh bìa: covers\\${p.reel}_cover.jpg`)));
      for (const [l, t] of [...fields(k.caption), ...(k.comment ? fields(k.comment) : [])]) { kids.push(para(rt(l, true))); kids.push(code(t)); }
    }
    if (DRY) { console.log(`${id}  ${title}  (${n} video, ${kids.length} khối)`); continue; }
    const q = await api('POST', `/databases/${WEEK_DB}/query`, { filter: { property: 'Mã', rich_text: { equals: id } }, page_size: 1 });
    let page = q.results[0];
    if (page && !REFRESH) { console.log(`${id}  (đã có)`); continue; }
    if (page) {                                   // rebuild body in place, keep the tick
      let cursor; const old = [];
      do { const j = await api('GET', `/blocks/${page.id}/children?page_size=100${cursor ? '&start_cursor=' + cursor : ''}`); old.push(...j.results); cursor = j.has_more ? j.next_cursor : null; } while (cursor);
      for (const b of old) await api('DELETE', `/blocks/${b.id}`);
      await api('PATCH', `/pages/${page.id}`, { properties: { 'Số video': { number: n } } });
    } else {
      page = await api('POST', '/pages', { parent: { database_id: WEEK_DB }, properties: {
        'Việc': { title: rt(title) }, Site: { select: { name: SITE[site] } }, 'Kênh': { select: { name } },
        'Tuần': { date: { start: FROM, end: TO } }, 'Số video': { number: n }, 'Mã': { rich_text: rt(id) } } });
    }
    for (let i = 0; i < kids.length; i += 90) await api('PATCH', `/blocks/${page.id}/children`, { children: kids.slice(i, i + 90) });
    console.log(`${id}  ${title}  ${page.url}`);
    made++;
  }
  console.log(`${made} dòng cho tuần ${FROM} → ${TO}`);
  if (made && !DRY) {                              // heads-up in the Telegram group (General topic)
    const config = require('./config.json');
    const token = require('./token')();
    const text = `🗓 <b>Hẹn giờ tuần ${dm(FROM)}–${dm(TO)} đã sẵn sàng</b>\n${made} trang (mỗi kênh 1 trang). Ngồi 1 buổi trên máy tính, hẹn giờ cả tuần, tích "Đã hẹn giờ".\n` +
      `<a href="https://www.notion.so/${WEEK_DB}">Mở bảng Hẹn giờ tuần</a>\nQuora + Reddit vẫn đăng tay hằng ngày theo tin buổi sáng.`;
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: config.chat_id, text, parse_mode: 'HTML', disable_web_page_preview: true }) }).catch(() => {});
  }
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
