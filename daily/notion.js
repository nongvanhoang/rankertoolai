// Notion side of the posting board: one row per video in the database
// "Đăng bài Reels (RankerNest & RankerToolAI)". The row has a checkbox per channel and the page
// body holds every channel's caption/comment in code blocks (Notion shows a Copy button on them).
// Needs user env var NOTION_TOKEN (an internal integration added to the database's Connections).
const crypto = require('crypto');
const path = require('path');
const { userEnv } = require('./token');

const DB = '61da72d0d5354100a4e3c3e463c916fc';
const VIEW_PENDING = 'https://www.notion.so/61da72d0d5354100a4e3c3e463c916fc?v=3fca464ec06a81329d56000ce6846af4';
const TOKEN = userEnv('NOTION_TOKEN');
const PROP = { instagram: 'IG', facebook: 'FB', youtube: 'YouTube', tiktok: 'TikTok', pinterest: 'Pinterest', x: 'X', linkedin: 'LinkedIn', reddit: 'Reddit', quora: 'Quora' };
const ORDER = ['instagram', 'facebook', 'youtube', 'tiktok', 'pinterest', 'x', 'linkedin', 'reddit', 'quora'];
const NAME = { instagram: 'Instagram', facebook: 'Facebook', youtube: 'YouTube Shorts', tiktok: 'TikTok', pinterest: 'Pinterest', x: 'X', linkedin: 'LinkedIn', reddit: 'Reddit', quora: 'Quora' };
const SITE = { rn: 'RankerNest', rta: 'RankerToolAI' };
// "📋 Copy" links open a one-button copy page on the posting-board Worker (/c/<id>); the texts are
// uploaded there first (POST /api/snips). Without board_url / RANKER_BOT_API_KEY the links are left out.
const CONFIG = (() => { try { return require(path.join(__dirname, 'config.json')); } catch (_) { return {}; } })();
const BOARD = CONFIG.board_url || '';
const BOARD_KEY = userEnv('RANKER_BOT_API_KEY');
const COPY_PAGES = false;
const snipId = (text) => crypto.createHash('sha256').update(text).digest('hex').slice(0, 16);
async function uploadSnips(snips) {
  if (!snips.length) return;
  const res = await fetch(BOARD + '/api/snips', { method: 'POST', headers: { 'content-type': 'application/json', 'x-api-key': BOARD_KEY }, body: JSON.stringify({ snips }) });
  if (!res.ok) throw new Error('snips upload: HTTP ' + res.status);
}
// Telegram link to the video card, e.g. https://t.me/c/4384456936/345?thread=2 (chat id without -100, message, topic).
// The /<topic>/<msg> form opened the wrong message on the owner's phone (2026-10-29).
const tgLink = (threadId, msgId) => `https://t.me/c/${String(CONFIG.chat_id).replace(/^-100/, '')}/${msgId}${threadId ? '?thread=' + threadId : ''}`;

async function api(method, path, body) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const res = await fetch('https://api.notion.com/v1' + path, {
      method, headers: { Authorization: `Bearer ${TOKEN}`, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (res.status === 429 || res.status >= 500) { await new Promise((r) => setTimeout(r, 1500 * (attempt + 1))); continue; }
    const j = await res.json();
    if (!res.ok) throw new Error(`Notion ${path}: ${j.message || res.status}`);
    return j;
  }
  throw new Error(`Notion ${path}: too many retries`);
}

const unesc = (s) => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&amp;/g, '&');
const link = (text, url) => ({ type: 'text', text: { content: text, link: { url } }, annotations: { bold: true } });
const rt = (text, bold) => {
  const out = [];
  for (let i = 0; i < text.length; i += 1900) out.push({ type: 'text', text: { content: text.slice(i, i + 1900) }, ...(bold ? { annotations: { bold: true } } : {}) });
  return out.length ? out : [{ type: 'text', text: { content: '' } }];
};
// Telegram-HTML kit message -> Notion blocks: "<b>Label:</b>\n<pre>text</pre>" => bold label + code block.
function kitBlocks(html, snips, where) {
  const blocks = [];
  for (const b of html.split(/\n+(?=<b>)/)) {
    const label = unesc((b.match(/^<b>([^<]*)<\/b>/) || [])[1] || '').replace(/:$/, '');
    const pre = b.match(/<pre>([\s\S]*?)<\/pre>/);
    const rest = unesc(b.replace(/^<b>[^<]*<\/b>/, '').replace(/<pre>[\s\S]*?<\/pre>/, '').replace(/<\/?[a-z]+[^>]*>/g, '')).trim();
    if (pre) {
      const text = unesc(pre[1]);
      // Off 2026-10-29: owner found the extra page annoying; Notion's own Copy on the code block is used instead.
      const copy = COPY_PAGES && snips && BOARD && BOARD_KEY;
      const sid = snipId(`${where}
${label}
${text}`);     // same text under two labels (Reddit title = Quora question) gets two pages
      if (copy) snips.push({ id: sid, label: `${where} · ${label}`, text });
      blocks.push({ type: 'paragraph', paragraph: { rich_text: [...rt(label, true), ...(copy ? [{ type: 'text', text: { content: '   ' } }, link('📋 Copy', `${BOARD}/c/${sid}`)] : [])] } });
      blocks.push({ type: 'code', code: { language: 'plain text', rich_text: rt(text) } });
      if (rest) blocks.push({ type: 'paragraph', paragraph: { rich_text: rt(rest) } });
    } else if (/^Cài đặt/i.test(label)) {
      for (const line of rest.split('\n').map((l) => l.replace(/^•\s*/, '').trim()).filter(Boolean))
        blocks.push({ type: 'bulleted_list_item', bulleted_list_item: { rich_text: rt(line) } });
    } else if (label) {
      blocks.push({ type: 'paragraph', paragraph: { rich_text: [...rt(label + '  ', true), ...rt(rest)] } });
    }
  }
  return blocks;
}
// Page body: one toggle heading per channel (tap to open, caption inside).
function videoCallout(fileName, tgUrl) {
  return { icon: { type: 'emoji', emoji: '🎬' }, rich_text: tgUrl
    ? [...rt('Video: '), link(`${fileName} ↗ (mở Telegram để tải)`, tgUrl), ...rt('. Tải về → thêm nhạc trong CapCut. Mở từng kênh bên dưới → bấm Copy trên khung chữ xám → đăng → tích ô kênh ở đầu trang.')]
    : rt(`Video: ${fileName} (file gốc ở Telegram, link hiện ở đây khi gói bài được gửi). Mở từng kênh bên dưới → bấm Copy trên khung chữ xám → đăng → tích ô kênh ở đầu trang.`) };
}
function pageChildren(post, snips) {
  const kids = [{ type: 'callout', callout: videoCallout(post.fileName, post.tgUrl) }];
  for (const ch of ORDER.filter((c) => post.channels.includes(c))) {
    const k = post.kit[ch];
    const inner = k ? [...kitBlocks(k.caption, snips, NAME[ch]), ...(k.comment ? kitBlocks(k.comment, snips, NAME[ch]) : [])] : [{ type: 'paragraph', paragraph: { rich_text: rt('(Chưa có caption cho kênh này)') } }];
    kids.push({ type: 'heading_2', heading_2: { rich_text: rt(NAME[ch]), is_toggleable: true, children: inner.slice(0, 100) } });
  }
  return kids;
}

async function findPage(id) {
  const q = await api('POST', `/databases/${DB}/query`, { filter: { property: 'Mã', rich_text: { equals: id } }, page_size: 1 });
  return q.results[0] || null;
}
const fileProp = (fileName, tgUrl) => ({ rich_text: tgUrl ? [{ type: 'text', text: { content: fileName, link: { url: tgUrl } } }] : rt(fileName) });
// Create the row for a card if it doesn't exist yet. Returns { id, url }.
// refresh: rebuild an existing row's body in place (same page link; ticks and Telegram link kept).
async function ensurePage(post, { refresh } = {}) {
  const found = await findPage(post.id);
  if (found && !refresh) return { id: found.id, url: found.url };
  if (found) {
    const f = found.properties['File video'].rich_text[0];
    post = { ...post, tgUrl: post.tgUrl || (f && f.href) || null };
    const snips = []; const kids = pageChildren(post, snips);
    await uploadSnips(snips);
    let cursor;
    const old = [];
    do { const j = await api('GET', `/blocks/${found.id}/children?page_size=100${cursor ? '&start_cursor=' + cursor : ''}`); old.push(...j.results); cursor = j.has_more ? j.next_cursor : null; } while (cursor);
    for (const b of old) await api('DELETE', `/blocks/${b.id}`);
    await api('PATCH', `/blocks/${found.id}/children`, { children: kids.slice(0, 90) });
    await api('PATCH', `/pages/${found.id}`, { properties: { 'Số kênh': { number: post.channels.filter((c) => PROP[c]).length }, 'File video': fileProp(post.fileName, post.tgUrl) } });
    return { id: found.id, url: found.url };
  }
  const props = {
    Video: { title: rt(post.title) },
    'Ngày': { date: { start: post.date } },
    Site: { select: { name: SITE[post.site] } },
    'Số kênh': { number: post.channels.filter((c) => PROP[c]).length },
    'File video': fileProp(post.fileName, post.tgUrl),
    'Mã': { rich_text: rt(post.id) },
  };
  const snips = []; const kids = pageChildren(post, snips);
  await uploadSnips(snips);
  const page = await api('POST', '/pages', { parent: { database_id: DB }, properties: props, children: kids.slice(0, 90) });
  return { id: page.id, url: page.url };
}
// Rows not finished, dated before `before` (for the morning "Còn nợ" list).
async function pending(site, before) {
  const q = await api('POST', `/databases/${DB}/query`, {
    filter: { and: [
      { property: 'Site', select: { equals: SITE[site] } },
      { property: 'Ngày', date: { before } },
      { property: 'Trạng thái', formula: { string: { does_not_equal: '✅ Xong' } } },
      { property: 'Trạng thái', formula: { string: { does_not_equal: '⏭ Bỏ qua' } } },
    ] },
    sorts: [{ property: 'Ngày', direction: 'ascending' }], page_size: 30,
  });
  return q.results.map((p) => ({
    title: (p.properties.Video.title[0] || {}).plain_text || '',
    date: p.properties['Ngày'].date && p.properties['Ngày'].date.start,
    url: p.url,
    left: (p.properties["Còn"] && p.properties["Còn"].formula && p.properties["Còn"].formula.number) || 0,
  }));
}

// After the morning card is sent: point the row's video name (property + top callout) at the Telegram message.
async function setVideoLink(pageId, fileName, threadId, msgId) {
  const url = tgLink(threadId, msgId);
  await api('PATCH', `/pages/${pageId}`, { properties: { 'File video': fileProp(fileName, url) } });
  const j = await api('GET', `/blocks/${pageId}/children?page_size=5`);
  const c = j.results.find((b) => b.type === 'callout');
  if (c) await api('PATCH', `/blocks/${c.id}`, { callout: videoCallout(fileName, url) });
  return url;
}

// Weekly scheduling (weekly_schedule.js): rows in "Hẹn giờ tuần" the owner ticked "Đã hẹn giờ".
// Returns the channel keys already scheduled for this site on this date.
const WEEK_DB = '2516b65bc95c48b09fed61bfd2a9933e';
const WEEKLY_CHANNELS = { instagram: 'Instagram', facebook: 'Facebook', youtube: 'YouTube', tiktok: 'TikTok', pinterest: 'Pinterest', x: 'X', linkedin: 'LinkedIn' };
async function scheduledChannels(site, date) {
  const q = await api('POST', `/databases/${WEEK_DB}/query`, { filter: { and: [
    { property: 'Site', select: { equals: SITE[site] } },
    { property: 'Đã hẹn giờ', checkbox: { equals: true } },
    { property: 'Tuần', date: { on_or_before: date } },
  ] }, page_size: 50 });
  const byName = Object.fromEntries(Object.entries(WEEKLY_CHANNELS).map(([k, v]) => [v, k]));
  return q.results.filter((p) => { const w = p.properties['Tuần'].date; return w && (w.end || w.start) >= date; })
    .map((p) => byName[(p.properties['Kênh'].select || {}).name]).filter(Boolean);
}
async function tick(pageId, channels) {
  const properties = {};
  for (const c of channels) if (PROP[c]) properties[PROP[c]] = { checkbox: true };
  if (Object.keys(properties).length) await api('PATCH', `/pages/${pageId}`, { properties });
}

module.exports = { enabled: () => !!TOKEN, ensurePage, pending, setVideoLink, scheduledChannels, tick, PROP, VIEW_PENDING, WEEK_DB, WEEKLY_CHANNELS, api, rt, unesc };
