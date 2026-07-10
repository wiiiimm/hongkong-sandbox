/* Service worker — offline app shell for Hong Kong Sandbox (HKS-29 / HKS-109).
 *
 * Same-origin only. Two strategies:
 *   • code / navigations (html, main.js, audio.js, vendor, manifest)
 *       → network-first: always the latest when online, cache as offline fallback.
 *   • heavy static assets (terrain data under /data/, icons, images, fonts)
 *       → stale-while-revalidate: instant from cache, refreshed in the background.
 *
 * Cross-origin requests are never intercepted — EXCEPT the R2 assets origin that
 * serves the offloaded terrain JSON on the official deploy (HKS-50/52), which is
 * cached like /data/ so opened sources stay available offline. Everything else
 * cross-origin — live data (HKO / data.gov.hk) and map tiles (OSM / Esri) —
 * always hits the network, so weather and tides are never stale.
 *
 * HKS-109: the default Hong Kong source (hk-landsd-5m) terrain is best-effort
 * precached at install (from R2 on the live deploy, else same-origin /data/) so a
 * cold offline launch after one online visit can render the full default view.
 * Other sources stay cache-on-first-use.
 *
 * Cache matches for heavy assets ignore the query string so install-time URLs
 * and app fetches with ?v= (dev cache-bust) share one entry.
 *
 * Bump VERSION when the app shell changes to evict old caches on activate.
 */
const VERSION = 'hks-sandbox-v21';
const CACHE = VERSION;

// The heavy terrain JSON is served from the R2 assets origin on the official
// deploy (HKS-50). Mirror index.html's hostname gate so the SW caches those
// (now cross-origin) requests too; any other host — forks, previews, localhost —
// keeps ASSET_ORIGIN null and stays strictly same-origin (fork-safe).
const ASSET_ORIGIN = self.location.hostname === 'hongkong-sandbox.wiiiimm.codes'
  ? 'https://assets.hongkong-sandbox.wiiiimm.codes'
  : null;

// Small, critical boot files — enough to open the app offline.
const SHELL = [
  '/index.html',
  '/main.js',
  '/audio.js',
  '/analytics.js',
  '/vendor/three.module.js',
  '/vendor/OrbitControls.js',
  '/vendor/glass-gl.js',
  '/vendor/astro.js',
  '/manifest.webmanifest',
  '/favicon.ico',
  '/favicon-32.png',
  '/favicon-16.png',
  '/apple-touch-icon.png',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// Default source (hk-landsd-5m) — full-fidelity offline (~15 MB raw / ~4–5 MB gzip).
// Same origin the app uses via main.js `asset()` so install + first online load
// share one Cache Storage entry (no double-download once either wins).
const DATA_BASE = ASSET_ORIGIN || self.location.origin;
const DEFAULT_TERRAIN = [
  'data/hk-dtm5m.json',
  'data/hk-georef.json',
  'data/hk-texbb.json',
  'data/hk-b50k-landcover.json',
  'data/hk-b50k-vectors.json',
  'data/hk-peaks.json',
  'data/hk-landmarks.json',
  'data/hk-sky.json',
].map((f) => `${DATA_BASE}/${f}`);

const isHeavyPath = (p) =>
  p.startsWith('/data/') || p.startsWith('/icons/') ||
  /\.(png|jpe?g|webp|gif|svg|ico|woff2?)$/i.test(p);

const isHeavyReq = (url) =>
  (ASSET_ORIGIN && url.origin === ASSET_ORIGIN) ||
  (url.origin === self.location.origin && isHeavyPath(url.pathname));

// Match cache entries even when the page appends ?v= (dev) or other search params.
async function matchCache(cache, req, url) {
  const opts = isHeavyReq(url) ? { ignoreSearch: true } : undefined;
  return cache.match(req, opts);
}

// Cap each precache download. Without this a hung R2 fetch (stalled, never
// erroring) keeps the worker `installing` forever via waitUntil, blocking
// activation and the offline boot fallback (HKS-109 review). A genuinely
// slow-but-progressing link may abort here and get topped up by SWR on the
// next online use — the intended best-effort behaviour.
const PRECACHE_TIMEOUT_MS = 60000;

async function precacheTerrain(cache) {
  // Per-file best-effort: a flaky link must never fail the whole install, and each
  // fetch is time-boxed so a hung download can't stall the worker's activation.
  await Promise.all(DEFAULT_TERRAIN.map(async (u) => {
    if (await cache.match(u, { ignoreSearch: true })) return;
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), PRECACHE_TIMEOUT_MS);
    try {
      const res = await fetch(u, { mode: 'cors', credentials: 'omit', cache: 'reload', signal: ctrl.signal });
      if (res && res.ok) await cache.put(u, res);
    } catch (_) { /* aborted / offline / error → leave gap; SWR tops up on next online use */ }
    finally { clearTimeout(to); }
  }));
}

self.addEventListener('install', (e) => {
  // Shell is required and gates activation. Terrain is a separate, best-effort
  // waitUntil that keeps the worker alive to finish downloading — but each fetch is
  // time-boxed (PRECACHE_TIMEOUT_MS), so a hung R2 request can no longer keep the
  // worker `installing`: install always settles and activation proceeds.
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(SHELL);
    await self.skipWaiting();
  })());
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await precacheTerrain(c);
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

async function networkFirst(req) {
  const url = new URL(req.url);
  try {
    const res = await fetch(req);
    if (res && res.ok) (await caches.open(CACHE)).put(req, res.clone());
    return res;
  } catch (err) {
    const cached = await matchCache(await caches.open(CACHE), req, url);
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const shell = await caches.match('/index.html');
      if (shell) return shell;
    }
    throw err;
  }
}

async function staleWhileRevalidate(req) {
  const url = new URL(req.url);
  const cache = await caches.open(CACHE);
  const cached = await matchCache(cache, req, url);
  const network = fetch(req)
    .then((res) => {
      if (res && res.ok) {
        // Store under the bare URL for heavy assets so install precache + app
        // fetch (with or without ?v=) hit the same key.
        const key = isHeavyReq(url) ? url.origin + url.pathname : req;
        cache.put(key, res.clone());
      }
      return res;
    })
    .catch(() => cached);
  return cached || network;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Offloaded terrain data on the R2 assets origin — cache like /data/ so opened
  // sources stay available offline even though they're now cross-origin (HKS-52).
  // These are cors-mode, non-opaque responses (correct R2 CORS from HKS-50), so
  // they're safe to cache and serve.
  if (ASSET_ORIGIN && url.origin === ASSET_ORIGIN) { e.respondWith(staleWhileRevalidate(req)); return; }
  if (url.origin !== self.location.origin) return;   // all other cross-origin (HKO / tiles) stay fresh
  if (req.mode === 'navigate') { e.respondWith(networkFirst(req)); return; }
  e.respondWith(isHeavyPath(url.pathname) ? staleWhileRevalidate(req) : networkFirst(req));
});
