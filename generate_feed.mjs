#!/usr/bin/env node
// Generate feed.xml (RSS 2.0) for FeedSpot / feed readers.
//
// Reads each page's <title>, meta description, canonical URL and the
// "datePublished" from its JSON-LD, so the feed always matches what's live.
// Only pages listed in sitemap.xml are included (skips noindex/quarantined).
//
// Usage: node generate_feed.mjs
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const BASE_URL = "https://rankertoolai.com";
const SECTIONS = ["review", "blog", "compare", "best", "alternatives"];
const MAX_ITEMS = 60;

const sitemap = new Set(
  [...readFileSync("sitemap.xml", "utf8").matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim())
);

const decode = (s) =>
  s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const posts = [];
for (const section of SECTIONS) {
  if (!existsSync(section)) continue;
  for (const slug of readdirSync(section)) {
    const file = join(section, slug, "index.html");
    if (!existsSync(file)) continue;
    const html = readFileSync(file, "utf8");
    const url = (html.match(/<link rel="canonical" href="([^"]+)"/) || [])[1] || `${BASE_URL}/${section}/${slug}/`;
    if (!sitemap.has(url)) continue;
    const date = (html.match(/"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})/) || [])[1];
    if (!date) continue;
    const title = decode(((html.match(/<title>([^<]*)/) || [])[1] || "").replace(/\s*\|\s*RankerToolAI\s*$/i, "").trim());
    const description = decode((html.match(/<meta name="description" content="([^"]*)"/) || [])[1] || "");
    if (!title) continue;
    posts.push({ title, description, url, date });
  }
}

posts.sort((a, b) => b.date.localeCompare(a.date) || a.url.localeCompare(b.url));
const items = posts.slice(0, MAX_ITEMS);
const rfc822 = (d) => new Date(`${d}T00:00:00Z`).toUTCString().replace("GMT", "+0000");

const xml = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
  "  <channel>",
  "    <title>RankerToolAI</title>",
  `    <link>${BASE_URL}/</link>`,
  "    <description>Hands-on reviews, comparisons and best-of guides for AI tools.</description>",
  "    <language>en-us</language>",
  `    <lastBuildDate>${rfc822(items[0].date)}</lastBuildDate>`,
  `    <atom:link href="${BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>`,
  ...items.flatMap((p) => [
    "    <item>",
    `      <title>${esc(p.title)}</title>`,
    `      <link>${p.url}</link>`,
    `      <guid isPermaLink="true">${p.url}</guid>`,
    `      <pubDate>${rfc822(p.date)}</pubDate>`,
    `      <description>${esc(p.description)}</description>`,
    "    </item>",
  ]),
  "  </channel>",
  "</rss>",
  "",
].join("\n");

writeFileSync("feed.xml", xml, "utf8");
console.log(`feed.xml: ${items.length} items (of ${posts.length} eligible), newest ${items[0].date}`);
