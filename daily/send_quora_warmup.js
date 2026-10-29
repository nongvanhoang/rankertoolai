// One-off: Quora warm-up pack -> Telegram General topic. Link-free answers to real questions
// (new posters who open with links get filtered), plus the step-by-step for posting from the phone.
const fs = require('fs');
const path = require('path');
const TOKEN = require('./token')();
const config = require('./config.json');
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const qa = (n, site, url, answer) =>
  `<b>${n} · ${site}</b>\nMở câu hỏi: ${url}\n\n<b>Câu trả lời (copy):</b>\n<pre>${esc(answer)}</pre>`;

const msgs = [
  `🟥 <b>BẮT ĐẦU ĐĂNG QUORA (trên điện thoại)</b>

<b>Giai đoạn 1 · từ nay đến ~2/11: trả lời KHÔNG link</b>
1. Bấm link câu hỏi ở tin 1–4 bên dưới → mở bằng app Quora
2. Bấm <b>Answer</b> (Trả lời)
3. Chạm khung chữ để copy → dán → bấm <b>Post</b>
4. Mỗi ngày 1–2 câu, đừng đăng cả 4 câu trong 1 lúc
5. Có thể sửa vài chữ cho giống giọng mình

<b>Giai đoạn 2 · từ ~2/11: đăng vào Space theo video hằng ngày</b>
1. Lưu video từ Telegram về máy
2. Quora → biểu tượng Spaces → chọn Space RankerToolAI hoặc RankerNest
3. Bấm <b>Post</b> (Đăng bài, KHÔNG phải Add question)
4. Mở tin <b>QUORA</b> dưới video hôm đó trong Telegram → copy ô "Bài đăng / câu trả lời" → dán
5. Bấm biểu tượng ảnh/video → đính kèm video → <b>Post</b>
6. Mở Notion → tích ô <b>Quora</b>

⚠️ Không dán cùng 1 bài vào nhiều câu hỏi. Mỗi bài tối đa 1 link, luôn giữ dòng Disclosure.`,
  qa('1/4', 'RankerToolAI', 'https://www.quora.com/What-is-the-best-AI-video-generation-tool-which-is-more-human-like',
`It depends on what "human-like" means for your video.

If you need a presenter talking to camera (training, explainers, product walkthroughs), look at avatar tools: you type a script and a digital presenter reads it. Before you pay, check three things:

1. Lip sync on your own script, not the demo. Run a free trial with a real paragraph you'd use, including names and numbers.
2. Voice quality in your language. Many tools sound fine in English and noticeably worse in other languages.
3. What the free plan leaves out. Free tiers usually add a watermark and cap video length, so a test can look better or worse than the paid result.

If you need realistic scenes or b-roll rather than a talking presenter, that's a different category (text-to-video generators), and they're still better at short clips than long, consistent footage.

Full disclosure: I run a site that reviews AI tools, so I compare these for a living. My advice is the same either way: test with your own script before choosing.`),
  qa('2/4', 'RankerToolAI', 'https://www.quora.com/What-is-the-best-AI-video-generator-out-now',
`There isn't one "best" because the tools solve different jobs:

• Talking-presenter videos (training, onboarding, explainers): avatar tools, where you write a script and an AI presenter reads it. Good when you'd otherwise need to film yourself again and again, or translate the same video into several languages.
• Turning a blog post or script into a stock-footage video: script-to-video tools. Fast for social clips, less control over every shot.
• Cinematic or creative clips from a text prompt: text-to-video generators. Impressive for a few seconds, harder to keep consistent over a long video.

What I'd check before paying for any of them: the watermark and length limits on the free plan, whether you get commercial rights on the plan you're buying, and how many minutes of video per month the price actually covers. Those three details change the real cost more than the headline price.

(Disclosure: I run an AI-tool review site.)`),
  qa('3/4', 'RankerNest', 'https://www.quora.com/What-are-the-advantages-and-disadvantages-of-an-ergonomic-keyboard-and-a-split-mechanical-keyboard',
`Advantages of a split (or curved split) layout:
• Your hands sit roughly shoulder-width apart, so your wrists don't have to bend outward to reach the keys.
• Many split boards can also be tented (raised in the middle), which reduces how much you twist your forearms flat.
• You can put a mouse or trackpad between the halves, closer to your body.

Disadvantages:
• There's an adjustment period. Expect slower, sloppier typing for a week or two, longer if you never learned to touch type, because a split board punishes reaching across the middle with the "wrong" hand.
• Fully separate halves take more desk space and setup.
• Some compact split models drop the number pad or move keys like Delete and the arrows, which matters if you work in spreadsheets.

A practical middle ground: a one-piece curved "split" keyboard. It keeps the angled key layout but stays a single unit, so it's easier to get used to and to move around.

One honest note: a keyboard helps with wrist angle, not with everything. Chair height, desk height and where your screen sits matter just as much. If you already have pain, see a professional too.

(Disclosure: I write buyer's guides, including on ergonomic desk gear.)`),
  qa('4/4', 'RankerNest', 'https://www.quora.com/Are-the-ergonomic-keyboards-actually-useful',
`They can be, but mostly for a specific problem: wrists bent outward or forearms twisted flat for hours a day.

A standard keyboard makes you bring both hands toward the middle, which angles your wrists. Split and curved keyboards spread the keys so your hands stay closer to shoulder-width. If that's where your discomfort comes from, many people notice a difference.

Where they're less useful:
• If your problem is mostly posture (screen too low, chair too high or low), a new keyboard alone won't fix it.
• If you're a two-finger typist, the split layout can feel awkward for a long time.
• "Ergonomic" is a marketing word too: some keyboards labelled that way are just a regular layout with a wrist rest.

What I'd look for: a real split or curved key layout, adjustable tilt (ideally negative tilt or tenting, not just raised back feet), and a layout that keeps the keys you use most, like the number pad if you do spreadsheets.

(Disclosure: I write buyer's guides, including on ergonomic desk gear.)`),
];

(async () => {
  fs.writeFileSync(path.join(__dirname, '..', 'social_posts', '_quora_setup', 'QUORA_WARMUP.html'), msgs.join('\n\n<hr>\n\n'));
  for (const text of msgs) {
    if (text.length > 4000) throw new Error('message too long ' + text.length);
    const r = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: config.chat_id, text, parse_mode: 'HTML', disable_web_page_preview: true }) });
    const j = await r.json(); if (!j.ok) throw new Error(j.description);
    console.log('sent', j.result.message_id, text.length);
  }
})().catch((e) => { console.error(e.message); process.exitCode = 1; });
