// One-time setup: finds the "Đăng bài hàng ngày" group and its two topics, writes daily/config.json.
//   1. Owner creates a Telegram group, turns on Topics, adds @rankernest_reels_bot as admin,
//      creates topics "RankerToolAI" and "RankerNest", and types "rta" in the first, "rn" in the second.
//   2. node daily/setup_telegram.js          (reads the bot's recent updates)
//   3. node daily/setup_telegram.js --test   (sends a short hello into each topic)
const fs = require('fs');
const path = require('path');

const TOKEN = require('./token')();
const CONFIG = path.join(__dirname, 'config.json');
if (!TOKEN) { console.error('Thiếu biến môi trường TELEGRAM_BOT_TOKEN (xem daily/README.md).'); process.exit(1); }
const api = async (m, body) => {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/${m}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  const j = await r.json();
  if (!j.ok) throw new Error(`${m}: ${j.description}`);
  return j.result;
};

(async () => {
  const cfg = fs.existsSync(CONFIG) ? JSON.parse(fs.readFileSync(CONFIG, 'utf8')) : {};
  if (process.argv.includes('--test')) {
    for (const [site, thread] of Object.entries(cfg.threads || {})) {
      await api('sendMessage', { chat_id: cfg.chat_id, message_thread_id: thread, text: `✅ Bot đã kết nối mục ${site === 'rn' ? 'RankerNest' : 'RankerToolAI'}. Từ mai, 6h30 sáng gói bài sẽ tới đây.` });
    }
    console.log('test messages sent');
    return;
  }
  const me = await api('getMe');
  const updates = await api('getUpdates', { allowed_updates: ['message'], limit: 100 });
  const msgs = updates.map((u) => u.message).filter(Boolean);
  const group = msgs.filter((m) => m.chat && m.chat.type === 'supergroup').pop();
  if (!group) {
    console.log(`Bot @${me.username} chưa thấy tin nhắn nào trong nhóm có Topics.`);
    console.log('Kiểm tra: nhóm đã bật Topics, bot là quản trị viên, và đã gõ "rta" / "rn" trong 2 mục.');
    process.exit(2);
  }
  const chatId = group.chat.id;
  const threads = { ...(cfg.threads || {}) };
  for (const m of msgs.filter((x) => x.chat.id === chatId && x.text)) {
    // "rta" / "rn", or "/rta" "/rn@bot": a bot that isn't admin only receives the slash forms
    const t = m.text.trim().toLowerCase().replace(/^\//, '').replace(/@.*$/, '');
    if ((t === 'rta' || t === 'rn') && m.message_thread_id) threads[t] = m.message_thread_id;
  }
  const out = { ...cfg, chat_id: chatId, chat_title: group.chat.title, threads };
  fs.writeFileSync(CONFIG, JSON.stringify(out, null, 1) + '\n');
  console.log(`Nhóm: ${group.chat.title} (${chatId})`);
  console.log(`Mục RankerToolAI: ${threads.rta || 'CHƯA THẤY — gõ "rta" trong mục đó rồi chạy lại'}`);
  console.log(`Mục RankerNest: ${threads.rn || 'CHƯA THẤY — gõ "rn" trong mục đó rồi chạy lại'}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
