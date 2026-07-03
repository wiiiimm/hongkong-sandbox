// Vercel Edge (Routing) Middleware — locale routing for /en-hk/ and /zh-hk/.
//
// This is the Vercel port of the Cloudflare Pages Function in
// `functions/_middleware.js` (HKS-47). Same behaviour, three cases:
//
//  • asset requests (anything with a file extension) pass straight through
//    (also excluded by `config.matcher`, so middleware never even runs on them)
//  • a locale-prefixed page request (/en-hk/…, /zh-hk/…) serves the SPA
//    (index.html) and stamps the LOCALE cookie so the next visit is remembered
//  • any other page request (/, /whatever) is negotiated — LOCALE cookie, then
//    Accept-Language, then the default — and 302-redirected to /<locale>/…
//
// The one Cloudflare-only piece was `HTMLRewriter`, which does not exist on the
// Vercel Edge runtime. Vercel middleware can instead fetch the static index.html
// and return a transformed body, so the per-locale SEO/OG rewrite is done with
// targeted string replacements keyed on the `id="…"` hooks already in the HTML.
//
// `<base href="/">` in index.html root-anchors every relative asset/data fetch,
// so the SPA served under /en-hk/ still loads /data/… from the origin root.
//
// The client (main.js) also reads its locale from the first path segment and
// falls back to ?locale= / localStorage / navigator.languages, so the app still
// works if this middleware isn't running (e.g. a plain static dev server).

const LOCALES = ['en-hk', 'zh-hk'];
const DEFAULT = 'en-hk';

// Localized SEO / social-share metadata, rewritten into the served HTML per locale so
// crawlers (which don't run main.js) get the right title/description/OG for /zh-hk/ vs
// /en-hk/. Keep the strings in sync with functions/_middleware.js and main.js (HKS-28).
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

const esc = v => String(v)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Replace the content="" of a <meta> identified by its id="" hook.
function setMetaById(html, id, val) {
  return html.replace(
    new RegExp(`(<meta[^>]*\\bid="${id}"[^>]*\\bcontent=")[^"]*(")`),
    `$1${esc(val)}$2`,
  );
}

function localizeSEO(html, seg, origin) {
  const s = SEO[seg];
  if (!s) return html;
  const canonical = `${origin}/${seg}/`;
  let h = html;
  h = h.replace(/(<html[^>]*\blang=")[^"]*(")/, `$1${esc(s.lang)}$2`);
  h = h.replace(/(<title>)[^<]*(<\/title>)/, `$1${esc(s.title)}$2`);
  h = h.replace(/(<meta[^>]*\bname="description"[^>]*\bcontent=")[^"]*(")/, `$1${esc(s.desc)}$2`);
  h = h.replace(/(<link[^>]*\bid="canonical"[^>]*\bhref=")[^"]*(")/, `$1${canonical}$2`);
  h = setMetaById(h, 'og-title', s.title);
  h = setMetaById(h, 'og-desc', s.desc);
  h = setMetaById(h, 'og-url', canonical);
  h = setMetaById(h, 'og-locale', s.ogLocale);
  h = setMetaById(h, 'og-locale-alt', s.ogAlt);
  h = setMetaById(h, 'tw-title', s.title);
  h = setMetaById(h, 'tw-desc', s.desc);
  return h;
}

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

export default async function middleware(request) {
  const url = new URL(request.url);
  if (/\.[a-z0-9]+$/i.test(url.pathname)) return undefined;       // static asset → serve as-is

  const seg = url.pathname.split('/')[1];
  if (LOCALES.includes(seg)) {                                    // /<locale>/… → serve the SPA
    // fetch the static index.html directly (cleanUrls is off, so no 308 → '/' loop)
    const res = await fetch(new URL('/index.html', url));
    const html = localizeSEO(await res.text(), seg, url.origin);  // OG/canonical/title for crawlers (HKS-28)
    const headers = new Headers({
      'Content-Type': 'text/html; charset=utf-8',
      'Set-Cookie': cookie(seg),
      'x-locale': seg,
      'Vary': 'Accept-Language, Cookie',
    });
    return new Response(html, { status: 200, headers });
  }

  const loc = negotiate(request);                                 // unprefixed → negotiate + redirect
  const rest = url.pathname === '/' ? '' : url.pathname.replace(/^\/+/, '');
  return new Response(null, {
    status: 302,
    headers: { Location: `/${loc}/${rest}${url.search}`, 'Set-Cookie': cookie(loc), 'Vary': 'Accept-Language, Cookie' },
  });
}

// Run on page requests only — skip anything with a file extension (assets), so
// /data/*.json, /main.js, /vendor/*, icons, etc. are served straight from the CDN
// and never re-enter middleware (which also prevents the /index.html fetch looping).
export const config = {
  matcher: ['/((?!.*\\.[a-zA-Z0-9]+$).*)'],
};
