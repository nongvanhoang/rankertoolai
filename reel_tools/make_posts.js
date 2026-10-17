// Builds the multi-platform posting kit for one reel from a post spec.
// Usage: node reel_tools/make_posts.js reel_tools/posts/<slug>.json
// Writes social_posts/<reel>/:
//   DANG_DA_KENH.txt   full kit (Vietnamese instructions + English copy), same format as
//                      the Synthesia v3 file the owner approved
//   tg/NN_<channel>.html  one Telegram message per channel (HTML; copy text in <pre> blocks,
//                      which Telegram shows with a tap-to-copy button)
// Every channel gets its own utm_source; utm_content=reel-<slug> matches RankerNest's
// social/winners_report.py. Fails loudly when a platform length limit is exceeded.
const fs = require("fs");
const path = require("path");

const specPath = process.argv[2];
const s = JSON.parse(fs.readFileSync(specPath, "utf8"));
const ROOT = path.join(__dirname, "..");

const SITES = {
  rn: { domain: "rankernest.com", brand: "RankerNest", tag: "RankerNest", email: "bản tin RankerNest (Brevo, list #3)" },
  rta: { domain: "rankertoolai.com", brand: "RankerToolAI", tag: "RankerToolAI", email: "bản tin RankerToolAI (Brevo, list #5)" },
};
const site = SITES[s.site];
const link = (source, medium, content = s.slug) =>
  `https://${site.domain}/${s.kw}/?utm_source=${source}&utm_medium=${medium}&utm_campaign=reel_video&utm_content=reel-${content}`;
const short = `${site.domain}/${s.kw}`;
const what = s.disclose === "code" ? "affiliate code" : "affiliate link";
const disclosure = `#ad — ${what}. We may earn a commission at no extra cost to you.`;
const tags = (list) => list.map((t) => "#" + t).join(" ");
const allTags = [...s.hashtags, site.tag];

// ---- copy per channel (English, for US audience) ----
const bullets = s.points.map((p) => "• " + p).join("\n");
const pinDesc = [s.summary, s.points.join(". ") + ".", s.offer, s.caveat, `#ad ${what[0].toUpperCase() + what.slice(1)}.`]
  .filter(Boolean).join(" ");

const ytDesc = [
  s.summary,
  bullets,
  s.offer, s.caveat,
  `Full review + current price:\n${link("youtube", "shorts")}`,
  disclosure,
  tags(allTags.slice(0, 5)),
].filter(Boolean).join("\n\n");

const fbCaption = [
  `#ad ${s.hook}`,
  s.summary,
  s.points.map((p) => "✅ " + p).join("\n"),
  s.offer ? "🏷️ " + s.offer : "",
  s.caveat ? "ℹ️ " + s.caveat : "",
  "👇 Full review + link in the first comment",
  tags(allTags.slice(0, 5)),
].filter(Boolean).join("\n");
const fbComment = `Full review: ${link("facebook", "reel")}\n(${what}: we may earn a commission at no extra cost to you)`;

const threads = [s.hook, s.summary, s.offer, `Full review: ${link("threads", "social")}`, `#ad (${what})`]
  .filter(Boolean).join("\n\n");

const xText = `${s.x}\n\n${link("x", "social")}\n\n#ad ${tags(s.xTags || [])}`.trim();
const xLen = xText.replace(/https?:\/\/\S+/g, "x".repeat(23)).length; // X counts any URL as 23

// First comments: links in IG/TikTok/Shorts captions aren't clickable, so the comment points to the bio page.
const igComment = () => `Full review + current price 👉 link in bio, tap ${s.kw.toUpperCase()}\n(${short} · #ad ${what})`;
const ttComment = () => `Link in bio → ${s.kw.toUpperCase()} 👆 (${short}) · #ad ${what}`;
const xReply = () => `Full review: ${link("x", "social")}\n(${what}: we may earn a commission)`;

const tiktok = `#ad ${s.hook} ${s.tiktokLine || ""} Link in bio → ${s.kw.toUpperCase()}\n${tags(s.tiktokTags || allTags)}`.replace(/  +/g, " ");

const email = {
  title: s.emailTitle,
  body: [s.summary, s.points.slice(0, 3).join(". ") + ".", s.offer, s.caveat].filter(Boolean).join(" "),
  link: link("brevo", "email"),
  small: `${what[0].toUpperCase() + what.slice(1)}: we may earn a commission at no extra cost to you.`,
};

// ---- limits ----
const problems = [];
if (s.pinterest.title.length > 100) problems.push(`Pinterest title ${s.pinterest.title.length}/100`);
if (pinDesc.length > 500) problems.push(`Pinterest description ${pinDesc.length}/500`);
if (s.youtubeTitle.length > 100) problems.push(`YouTube title ${s.youtubeTitle.length}/100`);
if (ytDesc.length > 5000) problems.push(`YouTube description too long`);
if (xLen > 280) problems.push(`X post ${xLen}/280`);
if (threads.length > 500) problems.push(`Threads ${threads.length}/500`);
if (tiktok.length > 2200) problems.push(`TikTok caption too long`);
if (problems.length) { console.error(specPath + ": " + problems.join("; ")); process.exit(1); }

// ---- channel blocks: {key, title, how, fields:[[label, text]], settings:[...]} ----
const ai = s.aiAvatar;
const channels = [];
const igCaption = fs.readFileSync(path.join(ROOT, "social_videos", s.reel, "caption.txt"), "utf8").trim();
channels.push({
  key: "instagram", title: "INSTAGRAM REELS", how: `Tài khoản @${s.site === "rn" ? "ranker.nest" : "ranker.toolai"} → + → Reel`,
  fields: [["Caption", igCaption], ["Bình luận đầu tiên (đăng xong thì ghim)", igComment()]],
  settings: [
    `Ảnh bìa: covers/${s.reel}_cover.jpg (trong thư mục Videos\\RankerToolAI_reels)`,
    `Nhạc trend: chọn trong thư viện của Instagram, giữ âm thanh gốc${ai ? " (nhạc nhỏ dưới giọng avatar)" : ""}`,
    ai ? `Bật nhãn "AI info" (video có người dẫn AI)` : `Không cần nhãn AI`,
    `Dòng #ad trong caption là đủ công khai; chỉ dùng nhãn "Paid partnership" khi ${s.brandName} đồng ý`,
    `Link bio: https://${site.domain}/links (người xem chọn từ khoá ${s.kw.toUpperCase()})`,
  ],
});
channels.push({
  key: "pinterest", title: "PINTEREST", how: "Tạo Pin → tải video lên → điền các ô dưới",
  note: s.pinterestCsv ? "Video này ĐÃ có trong file CSV Pinterest (lên lịch sẵn). Nếu đã tải CSV lên thì BỎ QUA mục này." : "",
  fields: [["Tiêu đề", s.pinterest.title], ["Mô tả", pinDesc], ["Link (ô Destination link)", link("pinterest", "video_pin")],
    ["Alt text", s.pinterest.alt]],
  settings: [`Board: ${s.pinterest.board}`, `Từ khoá gợi ý: ${s.pinterest.keywords}`],
});
channels.push({
  key: "youtube", title: "YOUTUBE SHORTS", how: "YouTube Studio → Tạo → Tải video lên",
  fields: [["Tiêu đề (tối đa 100 ký tự)", s.youtubeTitle + " #shorts"], ["Mô tả", ytDesc],
    ["Bình luận ghim", `Full review + current price 👉 ${short} (link on our channel page)`]],
  settings: [
    `Made for kids: chọn "No, it's not made for kids"`,
    `Paid promotion: TÍCH "My video contains paid promotion"`,
    ai ? `Altered or synthetic content: TÍCH Yes (video có người dẫn AI)` : `Altered or synthetic content: No (ảnh sản phẩm thật)`,
    `Danh mục: ${s.category}`,
    `Đăng xong: dán "Bình luận ghim" rồi GHIM lên đầu (link trong Shorts không bấm được, nên ghi tên trang ngắn)`,
    `Trang kênh → Tuỳ chỉnh → Links: thêm https://${site.domain}/links`,
  ],
});
if (s.linkedin) channels.push({
  key: "linkedin", title: "LINKEDIN",
  how: `Đăng từ trang ${site.brand} (Company Page); tải video trực tiếp, KHÔNG dán link YouTube`,
  fields: [["Nội dung bài", s.linkedin + `\n\n#ad ${tags(s.linkedinTags || [])}`],
    ["Bình luận đầu tiên (đăng ngay sau bài)", `Full review and pricing: ${link("linkedin", "social")}\n(${what}, we may earn a commission)`]],
  settings: ["Giờ đẹp: thứ 3–thứ 5, 20h–22h giờ VN (sáng giờ Mỹ)"],
});
channels.push({
  key: "facebook", title: "FACEBOOK REELS", how: "Fanpage → Reel → tải video",
  fields: [["Caption", fbCaption], ["Bình luận đầu tiên", fbComment]],
  settings: [`Dòng #ad ở đầu caption là đủ công khai; chỉ bật "Branded content" nếu có tag được trang của ${s.brandName}`],
});
channels.push({ key: "threads", title: "THREADS", how: "Bài mới → đính kèm video", fields: [["Nội dung", threads]], settings: [] });
channels.push({ key: "x", title: "X / TWITTER", how: `Bài mới → đính kèm video (${xLen}/280 ký tự)`, fields: [["Nội dung", xText], ["Trả lời ngay dưới bài (link)", xReply()]], settings: ["Nếu bài có link bị ít người xem: xoá link khỏi bài, chỉ để link trong phần trả lời"] });
channels.push({
  key: "tiktok", title: "TIKTOK", how: "+ → Tải lên → chọn video → dán caption",
  fields: [["Caption", tiktok], ["Bình luận ghim (đăng xong thì ghim)", ttComment()], ["Link bio (nếu tài khoản cho thêm link)", link("tiktok", "bio")]],
  settings: [`Bật "Content disclosure" → "Branded content"`, ai ? `Bật nhãn "AI-generated content"` : `Không cần nhãn AI (ảnh sản phẩm thật)`,
    `Nhạc trend: chọn trong thư viện "Commercial" của TikTok/CapCut (tài khoản Business)`],
});
channels.push({
  key: "email", title: "EMAIL", how: `Thêm 1 mục vào ${site.email}, không gửi email riêng chỉ để quảng cáo`,
  fields: [["Tiêu đề mục", email.title], ["Nội dung", email.body], ["Link (gắn vào ảnh bìa + nút)", email.link], ["Chữ nhỏ cuối mục", email.small]],
  settings: [`Ảnh: chụp 1 khung đẹp trong video (hoặc ảnh still bot đã tạo)`],
});

// ---- outputs ----
const outDir = path.join(ROOT, "social_posts", s.reel);
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(path.join(outDir, "tg"), { recursive: true });

const bar = "=".repeat(69);
let txt = `VIDEO: ${s.reel}.mp4  |  SẢN PHẨM: ${s.brandName}  |  TRANG ĐÍCH: ${short}\n`;
txt += `Mỗi kênh 1 link riêng (utm_source khác nhau) để sau 1 tuần biết kênh nào ra khách.\n`;
txt += `Trước khi đăng: thêm nhạc trend trong CapCut (giữ âm thanh gốc${ai ? ", nhạc nhỏ 15–25% dưới giọng avatar" : ""}), xuất 1080p 30fps, tắt đoạn đuôi CapCut.\n`;
if (s.expires) txt += `⚠️ HẠN: KHÔNG đăng sau ${s.expires} (${s.expiresNote}).\n`;
channels.forEach((c, i) => {
  txt += `\n${bar}\n${i + 1}) ${c.title}  (${c.how})\n${bar}\n`;
  if (c.note) txt += c.note + "\n\n";
  for (const [label, text] of c.fields) txt += `${label}:\n${text}\n\n`;
  if (c.settings.length) txt += "Cài đặt:\n" + c.settings.map((x) => "- " + x).join("\n") + "\n";
});
txt += `\n${bar}\nLỊCH ĐĂNG GỢI Ý (không đăng tất cả 1 lúc)\n${bar}\n`;
txt += `Ngày 1: Pinterest + YouTube Shorts\nNgày 2: ${s.linkedin ? "LinkedIn (20h–22h) + " : ""}Threads + X\nNgày 3: Facebook Reels (+ TikTok nếu có)\nBản tin email tiếp theo: thêm mục "${email.title}"\nSau ~7 ngày: nhờ Claude xem GA4 theo utm_source / utm_content=reel-${s.slug}.\n`;
txt += `\nKHÔNG: đăng vào nhiều nhóm lạ, dùng tên/logo ${s.brandName} làm tên/ảnh tài khoản, chạy quảng cáo bằng từ khoá thương hiệu "${s.brandName}".\n`;
fs.writeFileSync(path.join(outDir, "DANG_DA_KENH.txt"), txt);

const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const head = `<b>📋 ${esc(s.reel)}</b> · ${channels.length} kênh, mỗi kênh 1 tin bên dưới. Chạm vào khung chữ để copy.\n` +
  `🎵 Thêm nhạc trend trong CapCut trước khi đăng (giữ âm thanh gốc).` +
  (s.expires ? `\n⚠️ <b>Không đăng sau ${esc(s.expires)}</b> (${esc(s.expiresNote)}).` : "");
fs.writeFileSync(path.join(outDir, "tg", "00_head.html"), head);
channels.forEach((c, i) => {
  let m = `<b>${i + 1}/${channels.length} · ${c.title}</b>  <i>${esc(c.how)}</i>\n`;
  if (c.note) m += `⚠️ ${esc(c.note)}\n`;
  for (const [label, text] of c.fields) m += `\n<b>${esc(label)}:</b>\n<pre>${esc(text)}</pre>`;
  if (c.settings.length) m += `\n\n<b>Cài đặt:</b>\n` + c.settings.map((x) => "• " + esc(x)).join("\n");
  if (m.length > 4000) { console.error(`${s.reel}: Telegram message ${c.key} too long (${m.length})`); process.exit(1); }
  fs.writeFileSync(path.join(outDir, "tg", `${String(i + 1).padStart(2, "0")}_${c.key}.html`), m);
});
console.log(`${s.reel}: ${channels.length} channels, X ${xLen}/280, Pinterest desc ${pinDesc.length}/500 → social_posts/${s.reel}/`);

// ---- hook-test variants (built by make_hook_variants.js): short kit for IG, YouTube Shorts, TikTok ----
// Hooks are tested where the algorithm shows videos to strangers; the other channels keep hook A.
for (const [k, v] of Object.entries(s.variants || {})) {
  const reel = `${s.reel}_h${k}`, content = `${s.slug}-h${k}`;
  const ig = fs.readFileSync(path.join(ROOT, "social_videos", reel, "caption.txt"), "utf8").trim();
  const yt = [v.hook, s.summary, bullets, s.offer, s.caveat,
    `Full review + current price:\n${link("youtube", "shorts", content)}`, disclosure, tags(allTags.slice(0, 5))]
    .filter(Boolean).join("\n\n");
  const tt = `#ad ${v.hook} ${s.tiktokLine || ""} Link in bio → ${s.kw.toUpperCase()}\n${tags(s.tiktokTags || allTags)}`.replace(/  +/g, " ");
  const ytTitle = v.hook.replace(/[\s\p{Extended_Pictographic}‍️]+$/u, "") + ` | ${s.brandName} #shorts`;
  if (ytTitle.length > 100) { console.error(`${reel}: YouTube title ${ytTitle.length}/100`); process.exit(1); }
  const fields = [["INSTAGRAM caption", ig], ["YOUTUBE tiêu đề", ytTitle], ["YOUTUBE mô tả", yt], ["TIKTOK caption", tt]];
  // Same per-channel layout as hook A (caption + first comment + settings), with this hook's own utm_content
  const byKey = Object.fromEntries(channels.map((c) => [c.key, c]));
  const fbV = [`#ad ${v.hook}`, s.summary, s.points.map((p) => "✅ " + p).join("\n"), s.offer ? "🏷️ " + s.offer : "",
    s.caveat ? "ℹ️ " + s.caveat : "", "👇 Full review + link in the first comment", tags(allTags.slice(0, 5))].filter(Boolean).join("\n");
  const vChannels = [
    { ...byKey.instagram, fields: [["Caption", ig], ["Bình luận đầu tiên (đăng xong thì ghim)", igComment()]] },
    { ...byKey.youtube, fields: [["Tiêu đề (tối đa 100 ký tự)", ytTitle], ["Mô tả", yt], ["Bình luận ghim", `Full review + current price 👉 ${short} (link on our channel page)`]] },
    { ...byKey.tiktok, fields: [["Caption", tt], ["Bình luận ghim (đăng xong thì ghim)", ttComment()]] },
    { ...byKey.facebook, fields: [["Caption", fbV], ["Bình luận đầu tiên", `Full review: ${link("facebook", "reel", content)}\n(${what}: we may earn a commission at no extra cost to you)`]] },
  ];

  const vDir = path.join(ROOT, "social_posts", reel);
  fs.rmSync(vDir, { recursive: true, force: true });
  fs.mkdirSync(path.join(vDir, "tg"), { recursive: true });
  let t = `VIDEO: ${reel}.mp4  |  THỬ KIỂU MỞ ĐẦU ${k.toUpperCase()} cho ${s.brandName} (bản gốc ${s.reel} = kiểu A)\n`;
  t += `Chỉ đăng lên Instagram, YouTube Shorts, TikTok (nơi người lạ thấy video). Các kênh khác dùng bản A.\n`;
  t += `Cài đặt YouTube/TikTok giống bản A. Link riêng utm_content=reel-${content} để so kiểu nào thắng.\n`;
  if (s.expires) t += `⚠️ KHÔNG đăng sau ${s.expires} (${s.expiresNote}).\n`;
  for (const [l, x] of fields) t += `\n${l}:\n${x}\n`;
  fs.writeFileSync(path.join(vDir, "DANG_DA_KENH.txt"), t);

  fs.writeFileSync(path.join(vDir, "tg", "00_head.html"), `<b>🧪 ${esc(reel)}</b> · kiểu mở đầu ${k.toUpperCase()} (cùng video, chỉ khác câu đầu)` +
    (s.expires ? `\n⚠️ <b>Không đăng sau ${esc(s.expires)}</b> (${esc(s.expiresNote)}).` : ""));
  vChannels.forEach((c, i) => {
    let m = `<b>${c.title}</b>  <i>${esc(c.how)}</i>\n`;
    for (const [label, text] of c.fields) m += `\n<b>${esc(label)}:</b>\n<pre>${esc(text)}</pre>`;
    if (c.settings.length) m += `\n\n<b>Cài đặt:</b>\n` + c.settings.map((x) => "• " + esc(x)).join("\n");
    if (m.length > 4000) { console.error(`${reel}: Telegram message ${c.key} too long (${m.length})`); process.exit(1); }
    fs.writeFileSync(path.join(vDir, "tg", `${String(i + 1).padStart(2, "0")}_${c.key}.html`), m);
  });
  console.log(`  + ${reel} (hook ${k.toUpperCase()})`);
}

