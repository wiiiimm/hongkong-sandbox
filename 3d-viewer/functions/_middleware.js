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

// Localized SEO / social-share metadata, rewritten into the served HTML per locale so
// crawlers (which don't run main.js) get the right title/description/OG for /zh-hk/ vs
// /en-hk/. Keep the strings in sync with main.js's doc.title / meta.desc (HKS-28).
const SEO = {
  'en-hk': { lang: 'en',
    title: 'Hong Kong Sandbox — 3D terrain, live weather & typhoon sim',
    desc: 'An interactive 3D Hong Kong — real LiDAR terrain, live Hong Kong Observatory weather, tides and typhoon signals (No.1–10). Fly it yourself. Bilingual (EN / 繁中).',
    ogLocale: 'en_HK', ogAlt: 'zh_HK' },
  'zh-hk': { lang: 'zh-HK',
    title: '香港沙盒 — 3D 地形、實時天氣與颱風模擬',
    desc: '互動 3D 香港 — 真實 LiDAR 地形、香港天文台實時天氣、潮汐及颱風信號（一號至十號）。親自駕駛飛越香港。中英雙語。',
    ogLocale: 'zh_HK', ogAlt: 'en_HK' },
};
function localizeSEO(response, seg, origin) {
  const s = SEO[seg];
  if (!s) return response;
  const canonical = `${origin}/${seg}/`;
  const content = v => ({ element(el) { el.setAttribute('content', v); } });
  return new HTMLRewriter()
    .on('html',                                 { element(el) { el.setAttribute('lang', s.lang); } })
    .on('title',                                { element(el) { el.setInnerContent(s.title); } })
    .on('meta[name="description"]',             content(s.desc))
    .on('link[rel="canonical"]',                { element(el) { el.setAttribute('href', canonical); } })
    .on('meta[property="og:title"]',            content(s.title))
    .on('meta[property="og:description"]',      content(s.desc))
    .on('meta[property="og:url"]',              content(canonical))
    .on('meta[property="og:locale"]',           content(s.ogLocale))
    .on('meta[property="og:locale:alternate"]', content(s.ogAlt))
    .on('meta[name="twitter:title"]',           content(s.title))
    .on('meta[name="twitter:description"]',     content(s.desc))
    .transform(response);
}

export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  if (/\.[a-z0-9]+$/i.test(url.pathname)) return next();          // static asset → serve as-is

  const seg = url.pathname.split('/')[1];
  if (LOCALES.includes(seg)) {                                    // /<locale>/… → serve the SPA
    // fetch '/' (not '/index.html' — Pages 308-redirects that to '/', which would loop)
    const res = await env.ASSETS.fetch(new URL('/', url));
    const out = new Response(res.body, res);
    out.headers.set('Content-Type', 'text/html; charset=utf-8');
    out.headers.append('Set-Cookie', cookie(seg));
    out.headers.set('x-locale', seg);
    return localizeSEO(out, seg, url.origin);   // rewrite OG/canonical/title for crawlers (HKS-28)
  }

  const loc = negotiate(request);                                 // unprefixed → negotiate + redirect
  const rest = url.pathname === '/' ? '' : url.pathname.replace(/^\/+/, '');
  return new Response(null, {
    status: 302,
    headers: { Location: `/${loc}/${rest}${url.search}`, 'Set-Cookie': cookie(loc), Vary: 'Accept-Language, Cookie' },
  });
}
