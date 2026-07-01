// Cloudflare Pages middleware — locale routing for /en-hk/ and /zh-hk/.
//
//  • asset requests (anything with a file extension) pass straight through
//  • a locale-prefixed page request (/en-hk/…, /zh-hk/…) serves the SPA
//    (index.html) and stamps the LOCALE cookie so the next visit is remembered
//  • any other page request (/, /whatever) is negotiated — LOCALE cookie, then
//    Accept-Language, then the default — and 302-redirected to /<locale>/…
//
// The client (main.js) reads its locale from the first path segment; if this
// Function isn't running (e.g. the plain static dev server) it falls back to
// ?locale= / localStorage / navigator.languages, so the app still works.
const LOCALES = ['en-hk', 'zh-hk'];
const DEFAULT = 'en-hk';

function negotiate(request) {
  const m = (request.headers.get('Cookie') || '').match(/(?:^|;\s*)LOCALE=([^;]+)/);
  if (m && LOCALES.includes(m[1])) return m[1];
  const prefs = (request.headers.get('Accept-Language') || '')
    .split(',')
    .map(p => { const [tag, q] = p.trim().split(';q='); return { tag: tag.toLowerCase(), q: q ? parseFloat(q) : 1 }; })
    .sort((a, b) => b.q - a.q).map(x => x.tag);
  for (const p of prefs) if (LOCALES.includes(p)) return p;                          // exact (zh-hk)
  for (const p of prefs) { const hit = LOCALES.find(l => l.split('-')[0] === p.split('-')[0]); if (hit) return hit; }  // zh-* → zh-hk
  return DEFAULT;
}
const cookie = loc => `LOCALE=${loc}; Path=/; Max-Age=31536000; SameSite=Lax`;

export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  if (/\.[a-z0-9]+$/i.test(url.pathname)) return next();          // static asset → serve as-is

  const seg = url.pathname.split('/')[1];
  if (LOCALES.includes(seg)) {                                    // /<locale>/… → serve the SPA
    const res = await env.ASSETS.fetch(new Request(new URL('/index.html', url), request));
    const out = new Response(res.body, res);
    out.headers.set('Content-Type', 'text/html; charset=utf-8');
    out.headers.append('Set-Cookie', cookie(seg));
    out.headers.set('x-locale', seg);
    return out;
  }

  const loc = negotiate(request);                                 // unprefixed → negotiate + redirect
  const rest = url.pathname === '/' ? '' : url.pathname.replace(/^\/+/, '');
  return new Response(null, {
    status: 302,
    headers: { Location: `/${loc}/${rest}${url.search}`, 'Set-Cookie': cookie(loc), Vary: 'Accept-Language, Cookie' },
  });
}
