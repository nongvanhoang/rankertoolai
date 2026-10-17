// Weekly newsletter drafts for both lists, built from the videos scheduled in the past 7 days.
//   node daily/newsletter.js                 # week ending today (Vietnam time)
//   node daily/newsletter.js --date 2026-10-23 --dry-run
// For each brand: one email (header, one block per product: image, 3 facts, price/offer, button
// to the keyword landing page with utm_source=brevo&utm_medium=email), {{ unsubscribe }} footer.
// Output: daily/newsletters/<date>_<site>.html (paste-ready body for a Brevo HTML block).
// If RN_BREVO_API_KEY / RTA_BREVO_API_KEY are set (user env), it also creates a DRAFT campaign in
// that Brevo account (list RN #3 / RTA #5) — the owner reviews and presses Send. Never sends itself.
// Then it posts the files to the Telegram group's General topic with a short note.
const fs = require('fs');
const path = require('path');
const { userEnv } = require('./token');

const DIR = __dirname;
const ROOT = path.dirname(DIR);
const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const DRY = args.includes('--dry-run');
const DATE = opt('--date', new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10));
const FROM = new Date(Date.parse(DATE + 'T00:00:00Z') - 6 * 864e5).toISOString().slice(0, 10);
const config = JSON.parse(fs.readFileSync(path.join(DIR, 'config.json'), 'utf8'));
const calendar = JSON.parse(fs.readFileSync(path.join(DIR, 'calendar.json'), 'utf8'));

const SITES = {
  rn: { name: 'RankerNest', domain: 'https://rankernest.com', list: 3, key: 'RN_BREVO_API_KEY', sender: 'hello@rankernest.com',
    color: '#06D6C4', accent: '#FF4D6D', dark: '#090c0f', tagline: 'Smart buys, explained',
    img: (slug) => /^gifts-/.test(slug) ? `https://rankernest.com/assets/videos/${slug}-poster.jpg`
      : `https://rankernest.com/assets/email/${slug === 'switchbot-s20' ? 'switchbot-s20-vacuum' : slug}.jpg` },
  rta: { name: 'RankerToolAI', domain: 'https://rankertoolai.com', list: 5, key: 'RTA_BREVO_API_KEY', sender: 'hello@rankertoolai.com',
    color: '#f97316', accent: '#fbbf24', dark: '#0f1e38', tagline: 'AI tools, tried on the free plan first',
    img: (slug) => `https://rankertoolai.com/assets/images/logos/${slug.replace(/-lang$/, '')}.png` },
};
const FONT = "font-family:'Segoe UI',Helvetica,Arial,sans-serif;";
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Post specs (reel_tools/posts/*.json) keyed by reel folder; hook variants map to their base spec.
const specs = {};
for (const f of fs.readdirSync(path.join(ROOT, 'reel_tools', 'posts')).filter((x) => x.endsWith('.json'))) {
  const s = JSON.parse(fs.readFileSync(path.join(ROOT, 'reel_tools', 'posts', f), 'utf8'));
  specs[s.reel] = s;
}
const specFor = (reel) => specs[reel] || specs[reel.replace(/_h[a-z]$/, '')];

function itemsFor(site) {
  const seen = new Set(); const out = [];
  for (const d of calendar.filter((x) => x.date >= FROM && x.date <= DATE)) {
    for (const e of d.entries.filter((x) => x.type === 'reel' && x.site === site)) {
      const s = specFor(e.reel);
      if (!s) continue;
      const key = site === 'rta' ? s.brandName : s.slug;     // RTA: one block per tool (Synthesia has 2 reels)
      if (seen.has(key) || (config.hold || []).some((h) => s.slug.startsWith(h))) continue;
      if (s.expires && DATE > s.expires) continue;
      seen.add(key); out.push(s);
    }
  }
  return out;
}

function block(site, s, campaign) {
  const S = SITES[site];
  const url = `${S.domain}/${s.kw}/?utm_source=brevo&amp;utm_medium=email&amp;utm_campaign=${campaign}&amp;utm_content=${s.slug}`;
  const facts = s.points.slice(0, 3).map((p) => `<li style="margin:0 0 6px;">${esc(p)}</li>`).join('');
  return `
<tr><td style="padding:22px 28px 6px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb;border-radius:14px;">
    <tr><td style="padding:18px;text-align:center;background:#ffffff;border-radius:14px 14px 0 0;">
      <a href="${url}"><img src="${S.img(s.slug)}" width="260" alt="${esc(s.emailTitle)}" style="display:inline-block;max-width:260px;height:auto;border:0;"></a>
    </td></tr>
    <tr><td style="padding:4px 20px 20px;${FONT}">
      <h2 style="margin:0 0 8px;font-size:20px;line-height:1.3;color:#111827;">${esc(s.emailTitle)}</h2>
      <p style="margin:0 0 10px;font-size:15px;line-height:1.55;color:#374151;">${esc(s.summary)}</p>
      <ul style="margin:0 0 10px;padding-left:20px;font-size:14px;line-height:1.5;color:#374151;">${facts}</ul>
      ${s.offer ? `<p style="margin:0 0 10px;font-size:14px;color:#111827;"><strong>${esc(s.offer)}</strong></p>` : ''}
      ${s.caveat ? `<p style="margin:0 0 14px;font-size:13px;color:#6b7280;">${esc(s.caveat)}</p>` : ''}
      <a href="${url}" style="display:inline-block;background:${S.color};color:#ffffff;text-decoration:none;font-weight:700;font-size:15px;padding:11px 20px;border-radius:10px;">See the full breakdown →</a>
    </td></tr>
  </table>
</td></tr>`;
}

function email(site, items) {
  const S = SITES[site];
  const campaign = `newsletter_${DATE.replace(/-/g, '')}`;
  const subject = items.length === 1 ? items[0].emailTitle : `${items[0].emailTitle} + ${items.length - 1} more pick${items.length > 2 ? 's' : ''}`;
  const html = `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f7;">
<tr><td align="center" style="padding:20px 10px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;">
<tr><td style="background:${S.dark};padding:22px 28px;${FONT}">
  <span style="font-size:22px;font-weight:800;color:#ffffff;">${S.name}</span>
  <span style="font-size:13px;color:#9aa3a8;"> · ${S.tagline}</span>
</td></tr>
<tr><td style="height:4px;line-height:4px;font-size:0;background:${S.accent};">&nbsp;</td></tr>
<tr><td style="padding:24px 28px 0;${FONT}">
  <p style="margin:0;font-size:16px;line-height:1.6;color:#1f2937;">This week's picks from our short videos, with the facts that matter and the catch. Prices are at time of writing.</p>
</td></tr>
${items.map((s) => block(site, s, campaign)).join('\n')}
<tr><td style="padding:22px 28px 28px;${FONT}font-size:12px;line-height:1.6;color:#6b7280;">
  Some links are affiliate links: we may earn a commission at no extra cost to you. It never decides what we pick.<br>
  You're getting this because you signed up at ${S.domain.replace('https://', '')}. <a href="{{ unsubscribe }}" style="color:#6b7280;">Unsubscribe</a>
</td></tr>
</table></td></tr></table>`;
  return { subject, html, campaign };
}

async function brevoDraft(site, e) {
  const key = userEnv(SITES[site].key);
  if (!key) return null;
  const res = await fetch('https://api.brevo.com/v3/emailCampaigns', {
    method: 'POST', headers: { 'api-key': key, 'content-type': 'application/json', accept: 'application/json' },
    body: JSON.stringify({ name: `${SITES[site].name} weekly ${DATE}`, subject: e.subject,
      sender: { name: SITES[site].name, email: SITES[site].sender }, htmlContent: e.html, recipients: { listIds: [SITES[site].list] } }),
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Brevo ${site}: ${j.message || res.status}`);
  return j.id;
}

async function telegramFile(file, caption) {
  const token = require('./token')();
  if (!token || DRY) return;
  const fd = new FormData();
  fd.append('chat_id', String(config.chat_id));
  fd.append('caption', caption);
  fd.append('parse_mode', 'HTML');
  fd.append('document', new Blob([fs.readFileSync(file)], { type: 'text/html' }), path.basename(file));
  const r = await fetch(`https://api.telegram.org/bot${token}/sendDocument`, { method: 'POST', body: fd });
  if (!(await r.json()).ok) throw new Error('telegram sendDocument failed');
}

(async () => {
  const outDir = path.join(DIR, 'newsletters');
  fs.mkdirSync(outDir, { recursive: true });
  for (const site of ['rn', 'rta']) {
    const items = itemsFor(site);
    if (!items.length) { console.log(`${site}: no videos ${FROM}..${DATE}, no newsletter`); continue; }
    const e = email(site, items);
    const file = path.join(outDir, `${DATE}_${site}.html`);
    fs.writeFileSync(file, e.html);
    let draft = null, note = '';
    if (!DRY) { try { draft = await brevoDraft(site, e); } catch (err) { note = err.message; } }
    const how = draft ? `Đã tạo <b>bản nháp</b> trong Brevo (chiến dịch #${draft}): mở Brevo → Campaigns → xem lại → Send.`
      : `Chưa có khoá Brevo trên máy: mở file → copy hết → Brevo → Campaigns → Create → kéo khối HTML → dán. Danh sách #${SITES[site].list}.${note ? ' (' + esc(note) + ')' : ''}`;
    console.log(`${site}: ${items.length} items, subject "${e.subject}" → ${file}${draft ? ` (Brevo draft ${draft})` : ''}`);
    await telegramFile(file, `📧 <b>Bản tin ${SITES[site].name} tuần này</b>\nTiêu đề: <code>${esc(e.subject)}</code>\n${how}`);
  }
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
