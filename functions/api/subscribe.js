const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function onRequestPost(context) {
  const { request, env } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: 'invalid_body' }, 400);
  }

  const email = String(body.email || '').trim().slice(0, 254);
  const source = String(body.source || 'unknown').trim().slice(0, 64);
  const page = String(body.page || '').trim().slice(0, 300);

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'invalid_email' }, 400);
  }
  if (!env.NOTION_TOKEN || !env.NOTION_DATABASE_ID) {
    return json({ ok: false, error: 'not_configured' }, 500);
  }

  const notionRes = await fetch('https://api.notion.com/v1/pages', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.NOTION_TOKEN}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
    // Property names must match the target Notion database exactly:
    // "Email" (title), "Nguồn" (rich_text), "Trang" (rich_text).
    body: JSON.stringify({
      parent: { database_id: env.NOTION_DATABASE_ID },
      properties: {
        Email: { title: [{ text: { content: email } }] },
        'Nguồn': { rich_text: [{ text: { content: source } }] },
        'Trang': { rich_text: [{ text: { content: page } }] },
      },
    }),
  });

  if (!notionRes.ok) {
    return json({ ok: false, error: 'notion_error' }, 502);
  }

  return json({ ok: true }, 200);
}

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
