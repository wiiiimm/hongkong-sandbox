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
const VERSION = 'hks-sandbox-v26';
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
  '/vendor/GLTFLoader.js',
  '/vendor/BufferGeometryUtils.js',
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
// Fetched from the same origin the app uses via main.js `asset()`, so the install
// precache and the app's own fetches share ONE Cache Storage key. On a cold first
// visit the page and the SW may still each touch the network before the SW controls
// the page; the precache omits `cache: 'reload'` so it can be served from the HTTP
// cache the page's own fetch just populated — avoiding a second ~15 MB download in
// the common case. Any remaining gap is topped up by SWR on the next visit.
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
  'data/models/hiker-adventurer.glb',   // walk-mode hiker (CC0 Quaternius Adventurer)
  'data/models/plane-prop.glb',         // fly-mode airframes (HKS-110, CC-BY 3.0 — data/models/README.md)
  'data/models/plane-747.glb',
  'data/models/plane-777.glb',
  'data/models/plane-a350.glb',         // CC-BY 4.0 (hakai315) — data/models/README.md
  'data/models/nc/plane-a330.glb',      // ⚠ CC BY-NC-SA (OUTPISTON) — absent on commercial deploys; precache is per-file best-effort so the 404 just leaves a gap
  'data/models/nc/plane-betsy.glb',     // ⚠ CC BY-NC-SA (OUTPISTON) — same fencing as the a330
].map((f) => `${DATA_BASE}/${f}`);

const isHeavyPath = (p) =>
  p.startsWith('/data/') || p.startsWith('/icons/') ||
  /\.(png|jpe?g|webp|gif|svg|ico|woff2?)$/i.test(p);

const isHeavyReq = (url) =>
  (ASSET_ORIGIN && url.origin === ASSET_ORIGIN) ||
  (url.origin === self.location.origin && isHeavyPath(url.pathname));

// OFFLINE fallback matcher only: when the network is unavailable, serve any cached
// version of a heavy asset regardless of the page's ?v= (dev cache-bust) param.
// The online path matches the EXACT url first so ?v= still busts (see SWR below).
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
    if (await cache.match(u)) return;   // u is the bare URL — exact match
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), PRECACHE_TIMEOUT_MS);
    try {
      const res = await fetch(u, { mode: 'cors', credentials: 'omit', signal: ctrl.signal });
      if (res && res.ok) await cache.put(u, res);
    } catch (_) { /* aborted / offline / error → leave gap; SWR tops up on next online use */ }
    finally { clearTimeout(to); }
  }));
}

self.addEventListener('install', (e) => {
  // Only the shell gates install; skipWaiting so the new worker takes over as soon
  // as it's cached. Terrain is precached in `activate` (after claim) so a slow or
  // hung download can never hold the worker in the `installing` state.
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    const cache = await caches.open(CACHE);
    // Migrate already-cached terrain from any prior cache into the new one BEFORE
    // deleting it, so a VERSION bump never evicts the offline terrain — which would
    // force a ~15 MB re-download, or break offline entirely if the upgrade lands on
    // a dead link. Cache-to-cache copy, no network.
    for (const k of keys) {
      if (k === CACHE) continue;
      const old = await caches.open(k);
      for (const u of DEFAULT_TERRAIN) {
        if (await cache.match(u)) continue;
        const hit = await old.match(u);
        if (hit) await cache.put(u, hit);
      }
    }
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();                 // take control immediately — before the terrain fill
    // Best-effort precache tops up anything the migration didn't cover. Runs after
    // claim so it never delays control (each fetch time-boxed).
    await precacheTerrain(cache);
  })());
});

async function networkFirst(req, e) {
  const url = new URL(req.url);
  try {
    const res = await fetch(req);
    if (res && res.ok) { const copy = res.clone(); e.waitUntil(caches.open(CACHE).then((c) => c.put(req, copy))); }   // clone SYNCHRONOUSLY — a deferred clone runs after `return res` consumes the body
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

async function staleWhileRevalidate(req, e) {
  const url = new URL(req.url);
  const cache = await caches.open(CACHE);
  // Match the EXACT url first so the dev ?v= cache-bust still works: a ?v=123
  // request must not be served the bare cached entry (codex review). The bare
  // precache entry IS the exact match in production (no ?v=), so offline still hits.
  const exact = await cache.match(req);
  const network = fetch(req)
    .then((res) => {
      if (res && res.ok) {
        // Store heavy assets under the bare URL so the install precache and app
        // fetches converge on one key in production.
        const key = isHeavyReq(url) ? url.origin + url.pathname : req;
        e.waitUntil(cache.put(key, res.clone()));   // keep the write alive past respondWith
      }
      return res;
    })
    // offline (network failed): fall back to any cached version, ignoring ?v=
    .catch(() => exact || matchCache(cache, req, url));
  if (exact) e.waitUntil(network.catch(() => {}));   // revalidation continues after we return cached
  return exact || network;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Offloaded terrain data on the R2 assets origin — cache like /data/ so opened
  // sources stay available offline even though they're now cross-origin (HKS-52).
  // These are cors-mode, non-opaque responses (correct R2 CORS from HKS-50), so
  // they're safe to cache and serve.
  if (ASSET_ORIGIN && url.origin === ASSET_ORIGIN) { e.respondWith(staleWhileRevalidate(req, e)); return; }
  if (url.origin !== self.location.origin) return;   // all other cross-origin (HKO / tiles) stay fresh
  if (req.mode === 'navigate') { e.respondWith(networkFirst(req, e)); return; }
  e.respondWith(isHeavyPath(url.pathname) ? staleWhileRevalidate(req, e) : networkFirst(req, e));
});
