// Posting board bot (Cloudflare Worker + D1).
// The owner's PC (daily/send_daily.js) sends one card per video into the Telegram group and
// registers it here. This Worker handles the buttons on those cards and the group commands,
// so the board works even when the PC is off:
//   card buttons  ☐/✅ <channel>   mark a channel posted (tap again to undo)
//                 📋 Caption        pick a channel, get its caption (tap-to-copy)
//                 💬 Bình luận      pinned / first comments for this video
//                 ⏭ Bỏ qua          skip the video (↩️ to undo)
//   commands      /homnay  /chuadang  /tuan  /help   (in a brand topic: that brand only)
//   PC API        POST /api/register, GET /api/pending, GET /api/posted   (X-Api-Key)
// Secrets: BOT_TOKEN, API_KEY, WEBHOOK_SECRET.  Vars: THREADS = {"rta":2,"rn":4}, CHAT_ID.

const CH = {
  instagram: "IG", facebook: "FB", youtube: "YT", tiktok: "TT", x: "X",
  linkedin: "LinkedIn", pinterest: "Pin", threads: "Threads", email: "Email",
};
const BRAND = { rn: "RankerNest", rta: "RankerToolAI" };

const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const vnDate = (ms = Date.now()) => new Date(ms + 7 * 3600e3).toISOString().slice(0, 10);
const dm = (d) => `${+d.slice(8, 10)}/${+d.slice(5, 7)}`;
// Secrets were piped in from PowerShell and may carry a trailing CR/LF.
const sec = (v) => String(v || "").trim();
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json" } });

async function tg(env, method, body) {
  const r = await fetch(`https://api.telegram.org/bot${sec(env.BOT_TOKEN)}/${method}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  const j = await r.json().catch(() => ({}));
  if (!j.ok && !/message is not modified/.test(j.description || "")) console.log(method, j.description);
  return j;
}

// ---------- data ----------
async function getItem(env, id) {
  const it = await env.DB.prepare("SELECT * FROM items WHERE id = ?").bind(id).first();
  if (!it) return null;
  it.channels = JSON.parse(it.channels);
  it.kit = JSON.parse(it.kit || "{}");
  const { results } = await env.DB.prepare("SELECT ch, at FROM marks WHERE item_id = ?").bind(id).all();
  it.done = Object.fromEntries(results.map((r) => [r.ch, r.at]));
  return it;
}
// Same video already posted on a channel from another card (e.g. a re-sent or carried-over day).
async function postedElsewhere(env, reel, excludeId) {
  const { results } = await env.DB.prepare(
    "SELECT m.ch, MIN(m.at) AS at FROM marks m JOIN items i ON i.id = m.item_id WHERE i.reel = ? AND i.id != ? GROUP BY m.ch"
  ).bind(reel, excludeId).all();
  return Object.fromEntries(results.map((r) => [r.ch, r.at]));
}

// Slim cards (Notion mode, owner 2026-10-17): one message per video, captions + per-channel ticks
// live in the Notion row; Telegram keeps the file and ONE button "✅ Đã đăng xong".
function slimText(it) {
  const allDone = it.channels.every((c) => it.done[c]);
  return `🎬 <b>${esc(it.title)}</b>\n<i>${esc(BRAND[it.site])} · ${dm(it.date)}</i>\n` +
    `📝 <a href="${it.notion_url}">Caption &amp; đánh dấu từng kênh (Notion)</a>` +
    (it.skipped ? "\n⏭ <b>Đã bỏ qua</b>" : allDone ? "\n✅ <b>Đã đăng xong</b>" : "");
}
function slimKeyboard(it) {
  const allDone = it.channels.every((c) => it.done[c]);
  if (it.skipped || allDone) return { inline_keyboard: [[{ text: "↩️ Hoàn tác", callback_data: `z:${it.id}` }]] };
  return { inline_keyboard: [[{ text: "✅ Đã đăng xong", callback_data: `d:${it.id}` }]] };
}
// Tick (or untick) every channel checkbox on the Notion row.
async function notionTick(env, it, value) {
  if (!env.NOTION_TOKEN || !it.notion_page) return;
  const NP = { instagram: "IG", facebook: "FB", youtube: "YouTube", tiktok: "TikTok", pinterest: "Pinterest", x: "X", linkedin: "LinkedIn" };
  const properties = {};
  for (const c of it.channels) if (NP[c]) properties[NP[c]] = { checkbox: value };
  const r = await fetch(`https://api.notion.com/v1/pages/${it.notion_page}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${sec(env.NOTION_TOKEN)}`, "Notion-Version": "2022-06-28", "Content-Type": "application/json" },
    body: JSON.stringify({ properties }),
  });
  if (!r.ok) console.log("notion tick", r.status, await r.text());
}

function cardText(it, before) {
  const total = it.channels.length;
  const n = it.channels.filter((c) => it.done[c] || before[c]).length;
  const status = it.skipped ? "⏭ <b>Đã bỏ qua</b>" : n === total ? "🎉 <b>Xong tất cả kênh</b>" : `Đã đăng ${n}/${total} kênh`;
  const dup = Object.keys(before).filter((c) => it.channels.includes(c) && !it.done[c]);
  return `🎬 <b>${esc(it.title)}</b>\n<i>${esc(BRAND[it.site])} · ${dm(it.date)}</i>\n${status}` +
    (dup.length ? `\n🔁 Video này đã đăng trước đó trên: ${dup.map((c) => CH[c] || c).join(", ")} (không đăng lại)` : "") +
    (it.skipped ? "" : "\n\nĐăng xong kênh nào bấm kênh đó. 📋 lấy caption, 💬 lấy bình luận ghim.");
}
function cardKeyboard(it, before) {
  if (it.skipped) return { inline_keyboard: [[{ text: "↩️ Hoàn tác bỏ qua", callback_data: `u:${it.id}` }]] };
  const btn = (c) => ({
    text: `${it.done[c] || before[c] ? "✅" : "☐"} ${CH[c] || c}`,
    callback_data: `t:${it.id}:${c}`,
  });
  const rows = [];
  for (let i = 0; i < it.channels.length; i += 3) rows.push(it.channels.slice(i, i + 3).map(btn));
  rows.push([
    { text: "📋 Caption", callback_data: `c:${it.id}` },
    { text: "💬 Bình luận", callback_data: `m:${it.id}` },
    { text: "⏭ Bỏ qua", callback_data: `s:${it.id}` },
  ]);
  return { inline_keyboard: rows };
}
async function refreshCard(env, it) {
  if (it.notion_url) {
    return tg(env, "editMessageCaption", { chat_id: it.chat_id, message_id: it.card_msg, parse_mode: "HTML", caption: slimText(it), reply_markup: slimKeyboard(it) });
  }
  const before = await postedElsewhere(env, it.reel, it.id);
  const body = { chat_id: it.chat_id, message_id: it.card_msg, parse_mode: "HTML", reply_markup: cardKeyboard(it, before) };
  // The card is the video document's caption when the PC sent the video as a file.
  if (it.card_is_caption) await tg(env, "editMessageCaption", { ...body, caption: cardText(it, before) });
  else await tg(env, "editMessageText", { ...body, text: cardText(it, before), disable_web_page_preview: true });
}
const place = (it) => ({ chat_id: it.chat_id, ...(it.thread_id ? { message_thread_id: it.thread_id } : {}) });
const link = (it) => `https://t.me/c/${String(it.chat_id).replace(/^-100/, "")}/${it.card_msg}${it.thread_id ? `?thread=${it.thread_id}` : ""}`;

// ---------- callbacks ----------
async function onCallback(env, q) {
  const [op, id, ch] = (q.data || "").split(":");
  const it = await getItem(env, id);
  if (!it) return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: "Không tìm thấy bài này (đã quá cũ?)" });
  let toast = "";
  if (op === "d" || op === "z") {                 // slim card: all channels done / undo
    const value = op === "d";
    if (value) {
      const at = new Date().toISOString();
      for (const c of it.channels) {
        await env.DB.prepare("INSERT OR IGNORE INTO marks (item_id, ch, at) VALUES (?, ?, ?)").bind(id, c, at).run();
        it.done[c] = it.done[c] || at;
      }
    } else {
      await env.DB.prepare("DELETE FROM marks WHERE item_id = ?").bind(id).run();
      await env.DB.prepare("UPDATE items SET skipped = 0 WHERE id = ?").bind(id).run();
      it.done = {}; it.skipped = 0;
    }
    await notionTick(env, it, value);
    await refreshCard(env, it);
    return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: value ? "✅ Đã ghi: đăng xong (Notion cũng đã tích)" : "Đã hoàn tác" });
  }
  if (op === "t") {
    if (it.done[ch]) { await env.DB.prepare("DELETE FROM marks WHERE item_id = ? AND ch = ?").bind(id, ch).run(); delete it.done[ch]; toast = `Bỏ đánh dấu ${CH[ch] || ch}`; }
    else {
      const before = await postedElsewhere(env, it.reel, it.id);
      if (before[ch]) toast = `${CH[ch] || ch}: video này đã đăng ngày ${dm(vnDate(Date.parse(before[ch])))} rồi, đừng đăng lại`;
      else {
        const at = new Date().toISOString();
        await env.DB.prepare("INSERT OR REPLACE INTO marks (item_id, ch, at) VALUES (?, ?, ?)").bind(id, ch, at).run();
        it.done[ch] = at; toast = `✅ Đã ghi: ${CH[ch] || ch}`;
      }
    }
    await refreshCard(env, it);
  } else if (op === "s" || op === "u") {
    it.skipped = op === "s" ? 1 : 0;
    await env.DB.prepare("UPDATE items SET skipped = ? WHERE id = ?").bind(it.skipped, id).run();
    toast = op === "s" ? "Đã bỏ qua video này" : "Đã hoàn tác";
    await refreshCard(env, it);
  } else if (op === "c") {
    const chans = it.channels.filter((c) => it.kit[c] && it.kit[c].caption);
    if (!chans.length) toast = "Video này chưa có caption trong bộ đăng";
    else {
      const rows = [];
      for (let i = 0; i < chans.length; i += 4) rows.push(chans.slice(i, i + 4).map((c) => ({ text: CH[c] || c, callback_data: `p:${id}:${c}` })));
      await tg(env, "sendMessage", { ...place(it), reply_to_message_id: it.card_msg, text: `📋 Caption cho <b>${esc(it.title)}</b>: chọn kênh`, parse_mode: "HTML", reply_markup: { inline_keyboard: rows } });
    }
  } else if (op === "p") {
    const k = it.kit[ch];
    if (!k || !k.caption) toast = "Không có caption cho kênh này";
    else await tg(env, "sendMessage", { ...place(it), text: k.caption, parse_mode: "HTML", disable_web_page_preview: true });
  } else if (op === "m") {
    const parts = it.channels.filter((c) => it.kit[c] && it.kit[c].comment).map((c) => `<b>${CH[c] || c}</b>\n${it.kit[c].comment}`);
    if (!parts.length) toast = "Video này không có bình luận ghim";
    else await tg(env, "sendMessage", { ...place(it), reply_to_message_id: it.card_msg, text: `💬 <b>Bình luận ghim / bình luận đầu tiên</b>\n\n${parts.join("\n\n")}`.slice(0, 4090), parse_mode: "HTML", disable_web_page_preview: true });
  }
  return tg(env, "answerCallbackQuery", { callback_query_id: q.id, text: toast });
}

// ---------- commands ----------
async function listItems(env, where, args) {
  const { results } = await env.DB.prepare(`SELECT id FROM items WHERE ${where} ORDER BY date, id`).bind(...args).all();
  const out = [];
  for (const r of results) out.push(await getItem(env, r.id));
  return out;
}
const pendingCh = (it) => it.channels.filter((c) => !it.done[c]);

async function onCommand(env, msg) {
  const cmd = (msg.text || "").split(/[\s@]/)[0].toLowerCase();
  const threads = JSON.parse(env.THREADS || "{}");
  const site = Object.keys(threads).find((k) => threads[k] === msg.message_thread_id) || null;
  const siteSql = site ? " AND site = ?" : "";
  const siteArgs = site ? [site] : [];
  const reply = (text) => tg(env, "sendMessage", {
    chat_id: msg.chat.id, ...(msg.message_thread_id ? { message_thread_id: msg.message_thread_id } : {}),
    text, parse_mode: "HTML", disable_web_page_preview: true,
  });
  const today = vnDate();
  const line = (it) => {
    const p = pendingCh(it);
    const state = it.skipped ? "⏭ bỏ qua" : p.length ? `còn ${p.map((c) => CH[c] || c).join(", ")}` : "✅ xong";
    return `• <a href="${link(it)}">${esc(it.title)}</a> (${dm(it.date)}): ${state}`;
  };
  if (cmd === "/homnay") {
    const items = await listItems(env, `date = ?${siteSql}`, [today, ...siteArgs]);
    return reply(items.length ? `📅 <b>Hôm nay ${dm(today)}</b>\n` + items.map(line).join("\n") : "Hôm nay chưa có video nào được gửi.");
  }
  if (cmd === "/chuadang") {
    const from = vnDate(Date.now() - 14 * 864e5);
    const items = (await listItems(env, `date >= ? AND skipped = 0${siteSql}`, [from, ...siteArgs])).filter((it) => pendingCh(it).length);
    if (!items.length) return reply("🎉 Không còn bài nào chưa đăng (14 ngày qua).");
    const byCh = {};
    for (const it of items) for (const c of pendingCh(it)) byCh[c] = (byCh[c] || 0) + 1;
    return reply(`📌 <b>Còn ${items.length} video chưa đăng xong</b> (bấm tên để tới thẻ)\n` + items.map(line).join("\n") +
      `\n\n<b>Theo kênh:</b> ` + Object.entries(byCh).map(([c, n]) => `${CH[c] || c} ${n}`).join(" · "));
  }
  if (cmd === "/tuan") {
    const from = vnDate(Date.now() - 6 * 864e5);
    const { results } = await env.DB.prepare(
      `SELECT m.ch, COUNT(*) AS n FROM marks m JOIN items i ON i.id = m.item_id WHERE substr(m.at,1,10) >= ?${site ? " AND i.site = ?" : ""} GROUP BY m.ch ORDER BY n DESC`
    ).bind(from, ...siteArgs).all();
    return reply(results.length ? `📊 <b>7 ngày qua đã đăng</b>\n` + results.map((r) => `• ${CH[r.ch] || r.ch}: ${r.n} bài`).join("\n") : "7 ngày qua chưa đánh dấu bài nào.");
  }
  if (cmd === "/help" || cmd === "/start") {
    return reply("<b>Bảng đăng bài</b>\nMỗi video là 1 thẻ. Đăng xong kênh nào bấm kênh đó (✅). 📋 Caption: chọn kênh để lấy caption. 💬: bình luận ghim. ⏭: bỏ qua.\n\n/homnay — việc hôm nay\n/chuadang — bài còn nợ (14 ngày)\n/tuan — số bài đã đăng 7 ngày qua\nGõ trong chủ đề RankerNest/RankerToolAI để chỉ xem thương hiệu đó.");
  }
}

// ---------- PC API ----------
async function onApi(env, req, url) {
  if (req.headers.get("x-api-key") !== sec(env.API_KEY)) return json({ error: "unauthorized" }, 401);
  if (url.pathname === "/api/register" && req.method === "POST") {
    const it = await req.json();
    await env.DB.prepare(
      `INSERT OR REPLACE INTO items (id, site, date, title, reel, channels, chat_id, thread_id, card_msg, card_is_caption, kit, notion_page, notion_url, skipped, created)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT skipped FROM items WHERE id = ?), 0), ?)`
    ).bind(it.id, it.site, it.date, it.title, it.reel, JSON.stringify(it.channels), it.chat_id, it.thread_id || null,
      it.card_msg, it.card_is_caption ? 1 : 0, JSON.stringify(it.kit || {}), it.notion_page || null, it.notion_url || null, it.id, new Date().toISOString()).run();
    const full = await getItem(env, it.id);
    await refreshCard(env, full);            // draw the real buttons (and any "already posted" ticks)
    return json({ ok: true });
  }
  if (url.pathname === "/api/remind" && req.method === "POST") { await remind(env); return json({ ok: true }); }   // manual test of the 21h reminder
  if (url.pathname === "/api/posted") {      // channels a reel was already posted on (any card)
    const reel = url.searchParams.get("reel");
    return json(await postedElsewhere(env, reel, ""));
  }
  if (url.pathname === "/api/pending") {     // carried-over work for the morning pack
    const site = url.searchParams.get("site");
    const before = url.searchParams.get("before") || vnDate();
    const from = vnDate(Date.now() - 14 * 864e5);
    const items = (await listItems(env, "date >= ? AND date < ? AND skipped = 0 AND site = ?", [from, before, site]))
      .filter((it) => pendingCh(it).length)
      .map((it) => ({ id: it.id, title: it.title, date: it.date, reel: it.reel, link: link(it), pending: pendingCh(it) }));
    return json(items);
  }
  return json({ error: "not found" }, 404);
}

// ---------- 21:00 Vietnam reminder (cron "0 14 * * *" UTC) ----------
// Lists today's and earlier (14 days) videos not fully posted, per brand topic. Source of truth:
// the Notion board when NOTION_TOKEN is set, otherwise the button marks in D1.
async function pendingFromNotion(env, site) {
  const body = { filter: { and: [
    { property: "Site", select: { equals: BRAND[site] } },
    { property: "Ngày", date: { on_or_before: vnDate() } },
    { property: "Ngày", date: { on_or_after: vnDate(Date.now() - 14 * 864e5) } },
    { property: "Trạng thái", formula: { string: { does_not_equal: "✅ Xong" } } },
    { property: "Trạng thái", formula: { string: { does_not_equal: "⏭ Bỏ qua" } } },
  ] }, sorts: [{ property: "Ngày", direction: "ascending" }], page_size: 20 };
  const r = await fetch("https://api.notion.com/v1/databases/61da72d0d5354100a4e3c3e463c916fc/query", {
    method: "POST",
    headers: { Authorization: `Bearer ${sec(env.NOTION_TOKEN)}`, "Notion-Version": "2022-06-28", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error("notion " + r.status);
  const j = await r.json();
  return j.results.map((p) => ({
    title: (p.properties.Video.title[0] || {}).plain_text || "",
    date: p.properties["Ngày"].date.start, url: p.url,
    left: (p.properties["Còn"] && p.properties["Còn"].formula && p.properties["Còn"].formula.number) || 0,
  }));
}
async function remind(env) {
  const threads = JSON.parse(env.THREADS || "{}");
  for (const site of Object.keys(threads)) {
    let rows = [];
    try {
      if (env.NOTION_TOKEN) rows = await pendingFromNotion(env, site);
      else {
        const from = vnDate(Date.now() - 14 * 864e5);
        rows = (await listItems(env, "date >= ? AND date <= ? AND skipped = 0 AND site = ?", [from, vnDate(), site]))
          .filter((it) => pendingCh(it).length)
          .map((it) => ({ title: it.title, date: it.date, url: link(it), left: pendingCh(it).length }));
      }
    } catch (e) { console.log("remind", site, e.message); continue; }
    if (!rows.length) continue;                    // nothing owed: stay quiet
    const today = vnDate();
    const text = `🌙 <b>Nhắc việc 21h · ${BRAND[site]}</b>\nCòn ${rows.length} video chưa đăng xong:\n` +
      rows.map((r) => `• <a href="${r.url}">${esc(r.title)}</a>${r.date === today ? " (hôm nay)" : ` (${dm(r.date)})`}${r.left ? `: còn ${r.left} kênh` : ""}`).join("\n") +
      "\n\nĐăng xong thì bấm ✅ (hoặc tích trong Notion). Không đăng nữa: bấm ⏭ trên thẻ hoặc tích “Bỏ qua” trong Notion.";
    await tg(env, "sendMessage", { chat_id: env.CHAT_ID, message_thread_id: threads[site], text, parse_mode: "HTML", disable_web_page_preview: true });
  }
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(remind(env));
  },
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname.startsWith("/api/")) return onApi(env, req, url);
    if (url.pathname === "/tg" && req.method === "POST") {
      if (req.headers.get("x-telegram-bot-api-secret-token") !== sec(env.WEBHOOK_SECRET)) return new Response("forbidden", { status: 403 });
      const u = await req.json();
      try {
        if (u.callback_query) await onCallback(env, u.callback_query);
        else if (u.message && /^\//.test(u.message.text || "") && String(u.message.chat.id) === String(env.CHAT_ID)) await onCommand(env, u.message);
      } catch (e) { console.log("update error", e.stack || e.message); }
      return new Response("ok");
    }
    return new Response("Ranker posting bot");
  },
};
