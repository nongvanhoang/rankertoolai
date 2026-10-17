// Notion side of the posting board: one row per video in the database
// "Đăng bài Reels (RankerNest & RankerToolAI)". The row has a checkbox per channel and the page
// body holds every channel's caption/comment in code blocks (Notion shows a Copy button on them).
// Needs user env var NOTION_TOKEN (an internal integration added to the database's Connections).
const { userEnv } = require('./token');

const DB = '61da72d0d5354100a4e3c3e463c916fc';
const VIEW_PENDING = 'https://www.notion.so/61da72d0d5354100a4e3c3e463c916fc?v=3fca464ec06a81329d56000ce6846af4';
const TOKEN = userEnv('NOTION_TOKEN');
const PROP = { instagram: 'IG', facebook: 'FB', youtube: 'YouTube', tiktok: 'TikTok', pinterest: 'Pinterest', x: 'X', linkedin: 'LinkedIn' };
const ORDER = ['instagram', 'facebook', 'youtube', 'tiktok', 'pinterest', 'x', 'linkedin'];
const NAME = { instagram: 'Instagram', facebook: 'Facebook', youtube: 'YouTube Shorts', tiktok: 'TikTok', pinterest: 'Pinterest', x: 'X', linkedin: 'LinkedIn' };
const SITE = { rn: 'RankerNest', rta: 'RankerToolAI' };

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
const rt = (text, bold) => {
  const out = [];
  for (let i = 0; i < text.length; i += 1900) out.push({ type: 'text', text: { content: text.slice(i, i + 1900) }, ...(bold ? { annotations: { bold: true } } : {}) });
  return out.length ? out : [{ type: 'text', text: { content: '' } }];
};
// Telegram-HTML kit message -> Notion blocks: "<b>Label:</b>\n<pre>text</pre>" => bold label + code block.
function kitBlocks(html) {
  const blocks = [];
  for (const b of html.split(/\n+(?=<b>)/)) {
    const label = unesc((b.match(/^<b>([^<]*)<\/b>/) || [])[1] || '').replace(/:$/, '');
    const pre = b.match(/<pre>([\s\S]*?)<\/pre>/);
    const rest = unesc(b.replace(/^<b>[^<]*<\/b>/, '').replace(/<pre>[\s\S]*?<\/pre>/, '').replace(/<\/?[a-z]+[^>]*>/g, '')).trim();
    if (pre) {
      blocks.push({ type: 'paragraph', paragraph: { rich_text: rt(label, true) } });
      blocks.push({ type: 'code', code: { language: 'plain text', rich_text: rt(unesc(pre[1])) } });
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
function pageChildren(post) {
  const kids = [{ type: 'callout', callout: { icon: { type: 'emoji', emoji: '🎬' }, rich_text: rt(`Video: ${post.fileName} (file gốc ở Telegram). Mở từng kênh bên dưới → bấm Copy trên khung chữ → đăng → tích ô kênh ở đầu trang.`) } }];
  for (const ch of ORDER.filter((c) => post.channels.includes(c))) {
    const k = post.kit[ch];
    const inner = k ? [...kitBlocks(k.caption), ...(k.comment ? kitBlocks(k.comment) : [])] : [{ type: 'paragraph', paragraph: { rich_text: rt('(Chưa có caption cho kênh này)') } }];
    kids.push({ type: 'heading_2', heading_2: { rich_text: rt(NAME[ch]), is_toggleable: true, children: inner.slice(0, 100) } });
  }
  return kids;
}

async function findPage(id) {
  const q = await api('POST', `/databases/${DB}/query`, { filter: { property: 'Mã', rich_text: { equals: id } }, page_size: 1 });
  return q.results[0] || null;
}
// Create the row for a card if it doesn't exist yet. Returns { id, url }.
async function ensurePage(post) {
  const found = await findPage(post.id);
  if (found) return { id: found.id, url: found.url };
  const props = {
    Video: { title: rt(post.title) },
    'Ngày': { date: { start: post.date } },
    Site: { select: { name: SITE[post.site] } },
    'Số kênh': { number: post.channels.filter((c) => PROP[c]).length },
    'File video': { rich_text: rt(post.fileName) },
    'Mã': { rich_text: rt(post.id) },
  };
  const kids = pageChildren(post);
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

module.exports = { enabled: () => !!TOKEN, ensurePage, pending, PROP, VIEW_PENDING };
