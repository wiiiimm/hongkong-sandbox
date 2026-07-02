/* Service worker — offline app shell for Hong Kong Sandbox (HKS-29).
 *
 * Same-origin only. Two strategies:
 *   • code / navigations (html, main.js, audio.js, vendor, manifest)
 *       → network-first: always the latest when online, cache as offline fallback.
 *   • heavy static assets (terrain data under /data/, icons, images, fonts)
 *       → stale-while-revalidate: instant from cache, refreshed in the background.
 *
 * Cross-origin requests are never intercepted, so live data (HKO / data.gov.hk)
 * and map tiles (OSM / Esri) always hit the network — no stale weather or tides.
 *
 * The terrain JSON in /data/ (~21 MB total) is NOT precached; it is cached on
 * first use, so a source you have opened once stays available offline.
 *
 * Bump VERSION when the app shell changes to evict old caches on activate.
 */
const VERSION = 'hks-sandbox-v1';
const CACHE = VERSION;

// Small, critical boot files — enough to open the app offline.
const SHELL = [
  '/index.html',
  '/main.js',
  '/audio.js',
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

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()),
  );
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
  if (url.origin !== self.location.origin) return;   // live feeds & map tiles stay fresh
  if (req.mode === 'navigate') { e.respondWith(networkFirst(req)); return; }
  e.respondWith(isHeavyAsset(url.pathname) ? staleWhileRevalidate(req) : networkFirst(req));
});
