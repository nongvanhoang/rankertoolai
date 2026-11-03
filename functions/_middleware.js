// The production *.pages.dev host serves the whole site as a duplicate of
// rankertoolai.com. Send it to the real domain with a 301, keeping path and
// query. Preview deploys (<hash>.rankertoolai.pages.dev) are left alone.
const PAGES_HOST = 'rankertoolai.pages.dev';
const MAIN_HOST = 'rankertoolai.com';

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname === PAGES_HOST) {
    url.hostname = MAIN_HOST;
    url.protocol = 'https:';
    url.port = '';
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
