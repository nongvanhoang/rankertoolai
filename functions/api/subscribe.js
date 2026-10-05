const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Sends each new lead to Brevo (contact list -> welcome automation) and to
// the Notion leads database. Each destination is optional: it only runs when
// its env vars are set, and one failing doesn't block the other.
//   Brevo:  BREVO_API_KEY, BREVO_LIST_ID
//   Notion: NOTION_TOKEN, NOTION_DATABASE_ID
export async function onRequestPost(context) {
  const { request, env } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: 'invalid_body' }, 400);
  }

  // Honeypot field copied from the form's hidden _honey input; bots fill it.
  if (body.honey) {
    return json({ ok: true }, 200);
  }

  const email = String(body.email || '').trim().slice(0, 254);
  const source = String(body.source || 'unknown').trim().slice(0, 64);
  const page = String(body.page || '').trim().slice(0, 300);

  if (!EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'invalid_email' }, 400);
  }

  const tasks = [];
  if (env.BREVO_API_KEY && env.BREVO_LIST_ID) tasks.push(addToBrevo(env, email));
  if (env.NOTION_TOKEN && env.NOTION_DATABASE_ID) tasks.push(addToNotion(env, email, source, page));
  if (!tasks.length) {
    return json({ ok: false, error: 'not_configured' }, 500);
  }

  const results = await Promise.all(tasks);
  const ok = results.some((r) => r.ok);
  return json({ ok, results }, ok ? 200 : 502);
}

async function addToBrevo(env, email) {
  // updateEnabled: an existing contact is just added to the list instead of
  // returning a "duplicate" error.
  const res = await fetch('https://api.brevo.com/v3/contacts', {
    method: 'POST',
    headers: {
      'api-key': env.BREVO_API_KEY,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      email,
      listIds: [Number(env.BREVO_LIST_ID)],
      updateEnabled: true,
    }),
  });
  if (res.ok) return { dest: 'brevo', ok: true };
  const detail = await res.text();
  return { dest: 'brevo', ok: false, status: res.status, detail: detail.slice(0, 200) };
}

async function addToNotion(env, email, source, page) {
  const res = await fetch('https://api.notion.com/v1/pages', {
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
  if (res.ok) return { dest: 'notion', ok: true };
  return { dest: 'notion', ok: false, status: res.status };
}

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
