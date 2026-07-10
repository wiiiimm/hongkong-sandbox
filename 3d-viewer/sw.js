/* Service worker — offline app shell for Hong Kong Sandbox (HKS-29).
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
 * The terrain JSON (~21 MB total, same-origin /data/ or the R2 assets origin) is
 * NOT precached; it is cached on first use, so a source you have opened once
 * stays available offline.
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

// Default source (hk-landsd-5m) terrain — precached so the default Hong Kong view
// is fully usable offline right after install (HKS-109). Fetched from the SAME place
// the app requests it (main.js `asset()`): the R2 assets origin on the official
// deploy, else same-origin /data/ (forks/localhost/preview) — so the install and
// the app share one cache entry rather than downloading twice.
const DATA_BASE = ASSET_ORIGIN || self.location.origin;
const TERRAIN = [
  'data/hk-dtm5m.json',          // 5 m DTM mesh (critical)
  'data/hk-georef.json',
  'data/hk-texbb.json',
  'data/hk-b50k-landcover.json', // B50K base-map fills
  'data/hk-b50k-vectors.json',   // 12 MB roads/labels overlay (full-fidelity offline)
  'data/hk-peaks.json',
  'data/hk-landmarks.json',
  'data/hk-sky.json',            // Bright Star Catalogue for Stargaze
].map((f) => `${DATA_BASE}/${f}`);

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(SHELL);            // critical app shell — must all succeed
    self.skipWaiting();              // take control as soon as the shell is cached
    // terrain fills in behind the shell: per-file best-effort so a slow/flaky
    // connection (or going offline mid-install) never rejects the whole install —
    // stale-while-revalidate tops up anything missing on the next online use.
    await Promise.all(TERRAIN.map((u) => c.add(u).catch(() => {})));
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

const isHeavyAsset = (p) =>
  p.startsWith('/data/') || p.startsWith('/icons/') ||
  /\.(png|jpe?g|webp|gif|svg|ico|woff2?)$/i.test(p);

async function networkFirst(req) {
  try {
    const res = await fetch(req);
    if (res && res.ok) (await caches.open(CACHE)).put(req, res.clone());
    return res;
  } catch (err) {
    const cached = await caches.match(req);
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const shell = await caches.match('/index.html');
      if (shell) return shell;
    }
    throw err;
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const network = fetch(req)
    .then((res) => { if (res && res.ok) cache.put(req, res.clone()); return res; })
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
  e.respondWith(isHeavyAsset(url.pathname) ? staleWhileRevalidate(req) : networkFirst(req));
});
