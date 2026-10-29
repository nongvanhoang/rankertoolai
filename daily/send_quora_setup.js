// One-off: Quora profile + Space setup texts -> Telegram group (General topic), tap-to-copy.
// Quora requires real names on personal accounts, so: 1 personal profile + 2 Spaces (one per brand).
const fs = require('fs');
const path = require('path');
const TOKEN = require('./token')();
const config = require('./config.json');
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const msg = (title, how, fields, notes = []) =>
  `<b>${title}</b>\n<i>${esc(how)}</i>\n` + fields.map(([l, t]) => `\n<b>${esc(l)}:</b>\n<pre>${esc(t)}</pre>`).join('') +
  (notes.length ? '\n\n' + notes.map((n) => '• ' + esc(n)).join('\n') : '');

const msgs = [
  `🟥 <b>TẠO QUORA: 1 tài khoản cá nhân + 2 Space</b>\nQuora bắt buộc tên thật, tài khoản tên "RankerToolAI"/"RankerNest" sẽ bị khoá. Bài đăng hằng ngày vào 2 Space (giống fanpage).\n\n` +
  `1. quora.com → Sign up with Google (dùng Gmail bạn hay mở)\n2. Tên: tên thật, viết không dấu\n3. Dán hồ sơ ở tin số 1\n4. Tạo 2 Space theo tin số 2 và 3 (Quora → Spaces → Create a Space)\n5. Làm 3–5 ngày đầu: trả lời vài câu hỏi KHÔNG có link để tài khoản "ấm" rồi mới đăng bài có link`,
  msg('1/3 · HỒ SƠ CÁ NHÂN', 'Ảnh đại diện → Edit profile', [
    ['Profile credential (dòng dưới tên, tối đa 60 ký tự)', 'Founder of RankerToolAI & RankerNest (review sites)'],
    ['Employment credential: Position', 'Founder'],
    ['Employment credential: Company', 'RankerToolAI & RankerNest'],
    ['About / Bio', `I run two independent review sites:

• RankerToolAI (rankertoolai.com): AI tools for work, compared on published pricing, plans and features.
• RankerNest (rankernest.com): practical buyer's guides for home, desk setups, travel and gifts.

When I answer here, I say what I've checked, what I haven't tested myself, and when a link is an affiliate link.

Disclosure: both sites earn a commission from some links, at no extra cost to readers.`],
    ['Topics (chọn trong "Knows about")', 'Artificial Intelligence, AI Tools, Software, Productivity, Small Business, Accounting Software, Video Production, Consumer Electronics, Home Appliances, Gifts, Travel'],
  ], ['Ảnh đại diện: ảnh thật của bạn (Quora ưu tiên người thật, không dùng logo)']),
  msg('2/3 · SPACE RANKERTOOLAI', 'Quora → Spaces → Create a Space', [
    ['Name', 'RankerToolAI'],
    ['Brief description (tagline)', 'AI tools for work, explained in plain English: what they cost, what they do, who they fit.'],
    ['Details / About', `Short breakdowns of AI tools for work: video, writing, accounting, SEO and more.

Every post sticks to what the vendor publishes (prices, plans, limits) and says clearly what we haven't tested hands-on. Prices change, so always confirm on the vendor's site before you buy.

Some links are affiliate links: we may earn a commission at no extra cost to you. Full reviews at rankertoolai.com`],
    ['Rules (Space settings → Rules)', `1. Be useful: real questions and experiences welcome.
2. No spam or link-only posts.
3. Any affiliate link must be disclosed.`],
  ], ['Logo: dùng logo RankerToolAI (Space thì được dùng logo)', 'Ảnh bìa: chụp trang chủ rankertoolai.com hoặc 1 ảnh bìa video']),
  msg('3/3 · SPACE RANKERNEST', 'Quora → Spaces → Create a Space', [
    ['Name', 'RankerNest'],
    ['Brief description (tagline)', 'Smart buys for home, desk and travel: what to check before you buy.'],
    ['Details / About', `Short buyer's guides for everyday purchases: home and cleaning gear, ergonomic desk setups, travel tips and gift ideas.

We focus on the specs and fine print that actually change the decision, and we say when a pick is based on specs rather than hands-on testing. Prices move, so check the live price before you buy.

Some links are affiliate links: we may earn a commission at no extra cost to you. Full guides at rankernest.com`],
    ['Rules (Space settings → Rules)', `1. Be useful: real questions and experiences welcome.
2. No spam or link-only posts.
3. Any affiliate link must be disclosed.`],
  ], ['Logo: dùng logo RankerNest', 'Ảnh bìa: chụp trang chủ rankernest.com hoặc 1 ảnh quà tặng']),
];

(async () => {
  fs.writeFileSync(path.join(__dirname, '..', 'social_posts', '_quora_setup', 'QUORA_SETUP.html'), msgs.join('\n\n<hr>\n\n'));
  for (const text of msgs) {
    const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: config.chat_id, text, parse_mode: 'HTML', disable_web_page_preview: true }) });
    const j = await r.json(); if (!j.ok) throw new Error(j.description);
    console.log('sent', j.result.message_id, text.length);
  }
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
