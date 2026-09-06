#!/usr/bin/env node
/* report_coverage.mjs — where the 3D city stands, district by district.
 *
 * Decodes 3d-viewer/data/hk-buildings.bin (HKBL v1) and buckets every block into one of
 * Hong Kong's 18 districts (Islands split into Lantau and the other islands), so the
 * question "have we got the buildings for <area>?" has a number behind it. Per district:
 * blocks by type, share with a surveyed height, share standing on the fine 20 m harbour
 * mesh (elsewhere the 70 m territory DEM can bury lower floors on steep slopes), blocks by
 * land-use class, named towers ≥ 100 m and the tallest block.
 *
 * District polygons: OpenStreetMap administrative boundaries via Nominatim (ODbL —
 * report use only, nothing is shipped), fetched once into ./cache/districts.geojson
 * (git-ignored) and projected to HK1980 with the same Helmert + TM series as the build.
 *
 * Run:  node source-scripts/hk-buildings/report_coverage.mjs [--md docs/out.md]
 *   → prints a Markdown table; --json path writes the per-district numbers.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DATA = join(HERE, '..', '..', '3d-viewer', 'data');
const CACHE = join(HERE, 'cache');
const args = process.argv.slice(2);
const opt = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };

// ---- HK1980 projection (copy of the build script's series) --------------------------------
const D2R = Math.PI / 180, AS2R = D2R / 3600;
const WGS = { a: 6378137, f: 1 / 298.257223563 }; WGS.e2 = WGS.f * (2 - WGS.f);
const INT = { a: 6378388, f: 1 / 297 }; INT.e2 = INT.f * (2 - INT.f);
const HLM = { dx: -162.619, dy: -276.959, dz: -161.764, rx: 0.067753 * AS2R, ry: -2.243649 * AS2R, rz: -1.158827 * AS2R, ds: -1.094246e-6 };
const HK = { a: INT.a, e2: INT.e2, FE: 836694.05, FN: 819069.80, k0: 1.0, lat0: (22 + 18 / 60 + 43.68 / 3600) * D2R, lon0: (114 + 10 / 60 + 42.80 / 3600) * D2R };
const geoToEcef = (lat, lon, el) => { const s = Math.sin(lat), c = Math.cos(lat), N = el.a / Math.sqrt(1 - el.e2 * s * s); return [N * c * Math.cos(lon), N * c * Math.sin(lon), N * (1 - el.e2) * s]; };
function ecefToGeo(x, y, z, el) { const lon = Math.atan2(y, x), p = Math.hypot(x, y); let lat = Math.atan2(z, p * (1 - el.e2)); for (let i = 0; i < 8; i++) { const s = Math.sin(lat), N = el.a / Math.sqrt(1 - el.e2 * s * s); lat = Math.atan2(z + el.e2 * N * s, p); } return [lat, lon]; }
function wgsToHk80(lat, lon) { const [x, y, z] = geoToEcef(lat, lon, WGS); const m = 1 + HLM.ds, X = (x - HLM.dx) / m, Y = (y - HLM.dy) / m, Z = (z - HLM.dz) / m; const { rx, ry, rz } = HLM; return ecefToGeo(X + rz * Y - ry * Z, -rz * X + Y + rx * Z, ry * X - rx * Y + Z, INT); }
function meridianArc(lat) { const e2 = HK.e2, e4 = e2 * e2, e6 = e4 * e2; return HK.a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * lat - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * Math.sin(2 * lat) + (15 * e4 / 256 + 45 * e6 / 1024) * Math.sin(4 * lat) - (35 * e6 / 3072) * Math.sin(6 * lat)); }
const M0 = meridianArc(HK.lat0);
function llToEN(phi, lam) { const e2 = HK.e2, ep2 = e2 / (1 - e2); const s = Math.sin(phi), c = Math.cos(phi), t = Math.tan(phi); const N1 = HK.a / Math.sqrt(1 - e2 * s * s), T = t * t, C = ep2 * c * c, A = (lam - HK.lon0) * c; return [HK.FE + HK.k0 * N1 * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5 / 120), HK.FN + HK.k0 * (meridianArc(phi) - M0 + N1 * t * (A * A / 2 + (5 - T + 9 * C + 4 * C * C) * A ** 4 / 24 + (61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6 / 720))]; }
const wgsToEN = (lon, lat) => { const [p, l] = wgsToHk80(lat * D2R, lon * D2R); return llToEN(p, l); };

// ---- districts ---------------------------------------------------------------------------
const DISTRICTS = ['Central and Western', 'Wan Chai', 'Eastern', 'Southern', 'Yau Tsim Mong', 'Sham Shui Po', 'Kowloon City', 'Wong Tai Sin', 'Kwun Tong',
  'Kwai Tsing', 'Tsuen Wan', 'Tuen Mun', 'Yuen Long', 'North', 'Tai Po', 'Sha Tin', 'Sai Kung', 'Islands'];
const REGION = { 'Central and Western': 'Hong Kong Island', 'Wan Chai': 'Hong Kong Island', 'Eastern': 'Hong Kong Island', 'Southern': 'Hong Kong Island',
  'Yau Tsim Mong': 'Kowloon', 'Sham Shui Po': 'Kowloon', 'Kowloon City': 'Kowloon', 'Wong Tai Sin': 'Kowloon', 'Kwun Tong': 'Kowloon',
  'Kwai Tsing': 'New Territories West', 'Tsuen Wan': 'New Territories West', 'Tuen Mun': 'New Territories West', 'Yuen Long': 'New Territories West',
  'North': 'New Territories North', 'Tai Po': 'New Territories East', 'Sha Tin': 'New Territories East', 'Sai Kung': 'New Territories East',
  'Islands · Lantau': 'Lantau & airport', 'Islands · other islands': 'Outlying islands' };
async function nominatim(q) {
  const u = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=geojson&polygon_geojson=1&limit=5`;
  const r = await fetch(u, { headers: { 'User-Agent': 'hongkong-sandbox coverage report (github.com/wiiiimm/hongkong-sandbox)' } });
  if (!r.ok) throw new Error(`Nominatim ${r.status} for ${q}`);
  return (await r.json()).features;
}
async function ensureDistricts() {
  const p = join(CACHE, 'districts.geojson');
  if (existsSync(p)) return JSON.parse(readFileSync(p, 'utf8'));
  mkdirSync(CACHE, { recursive: true });
  const out = { type: 'FeatureCollection', licence: 'Data © OpenStreetMap contributors, ODbL 1.0 — report use only', features: [] };
  for (const name of [...DISTRICTS, 'Lantau Island']) {
    const isDistrict = name !== 'Lantau Island';
    const fs = await nominatim(isDistrict ? `${name} District, Hong Kong` : 'Lantau Island, Hong Kong');
    const f = fs.find(f => (isDistrict ? f.properties.category === 'boundary' : /island|place|natural/.test(f.properties.category)) && /Polygon/.test(f.geometry.type)) || fs.find(f => /Polygon/.test(f.geometry.type));
    if (!f) throw new Error(`no polygon for ${name}: ${fs.map(f => f.properties.display_name).join(' | ')}`);
    f.properties.hks = name;
    out.features.push(f);
    console.error(`  ${name} ← ${f.properties.display_name}`);
    await new Promise(r => setTimeout(r, 1100));   // Nominatim: 1 req/s
  }
  writeFileSync(p, JSON.stringify(out));
  return out;
}
// polygon → { rings: [[[E,N],…]…], bbox } in HK1980; MultiPolygon → many
function toGrid(geom) {
  const polys = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates;
  return polys.map(rings => {
    const R = rings.map(r => r.map(([lon, lat]) => wgsToEN(lon, lat)));
    let e0 = 1e12, e1 = -1e12, n0 = 1e12, n1 = -1e12;
    for (const [e, n] of R[0]) { if (e < e0) e0 = e; if (e > e1) e1 = e; if (n < n0) n0 = n; if (n > n1) n1 = n; }
    return { rings: R, bbox: [e0, n0, e1, n1] };
  });
}
function inRing(r, x, y) { let inside = false; for (let i = 0, j = r.length - 1; i < r.length; j = i++) { const [xi, yi] = r[i], [xj, yj] = r[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside; } return inside; }
function inPolys(polys, x, y) {
  for (const p of polys) {
    if (x < p.bbox[0] || x > p.bbox[2] || y < p.bbox[1] || y > p.bbox[3]) continue;
    if (!inRing(p.rings[0], x, y)) continue;
    let hole = false; for (let k = 1; k < p.rings.length; k++) if (inRing(p.rings[k], x, y)) { hole = true; break; }
    if (!hole) return true;
  }
  return false;
}

// ---- HKBL decode (mirror of buildings.js parse, centroids only) -----------------------------
function decode(u8) {
  if (String.fromCharCode(...u8.subarray(0, 4)) !== 'HKBL') throw new Error('not an HKBL file');
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  const count = dv.getUint32(8, true), oE = dv.getFloat64(12, true), oN = dv.getFloat64(20, true), q = dv.getFloat32(28, true);   // vertices are quanta from the origin
  let pos = 32;
  const rv = () => { let r = 0, s = 0, b; do { b = u8[pos++]; r += (b & 0x7f) * 2 ** s; s += 7; } while (b & 0x80); return r; };
  const rz = () => { const v = rv(); return (v % 2) ? -(v + 1) / 2 : v / 2; };
  const flags = new Uint8Array(count), base = new Float32Array(count), hgt = new Float32Array(count), cE = new Float64Array(count), cN = new Float64Array(count);
  let pE = 0, pN = 0;
  for (let i = 0; i < count; i++) {
    flags[i] = u8[pos++];
    const nr = rv(); let e0 = 0, n0 = 0;
    for (let k = 0; k < nr; k++) {
      const n = rv(); let ce = k === 0 ? pE : e0, cn = k === 0 ? pN : n0, sx = 0, sy = 0;
      for (let j = 0; j < n; j++) { ce += rz(); cn += rz(); if (k === 0) { sx += ce; sy += cn; if (j === 0) { e0 = ce; n0 = cn; } } }
      if (k === 0) { cE[i] = oE + sx / n * q; cN[i] = oN + sy / n * q; }
    }
    pE = e0; pN = n0;
    base[i] = rz() / 10; hgt[i] = Math.max(0.5, rv() / 10);
  }
  return { count, flags, base, hgt, cE, cN };
}

// ---- report ----------------------------------------------------------------------------
const gj = await ensureDistricts();
const polys = Object.fromEntries(gj.features.map(f => [f.properties.hks, toGrid(f.geometry)]));
const lantau = polys['Lantau Island'];
const D = decode(gunzipSync(readFileSync(join(DATA, 'hk-buildings.bin'))));
const names = JSON.parse(readFileSync(join(DATA, 'hk-buildings-names.json'), 'utf8')).towers;
const HARBOUR = [826000, 806000, 848000, 828000];           // the 20 m mesh window (E0, N0, E1, N1)
const USE = ['residential', 'office', 'retail', 'industrial', 'institution', 'village', 'other'];
const TYPE = ['tower', 'podium', 'open', 'temp'];
const rows = {};
const row = k => rows[k] ??= { district: k, region: REGION[k] || '—', blocks: 0, type: [0, 0, 0, 0], surveyed: 0, fine: 0, use: [0, 0, 0, 0, 0, 0, 0], named: 0, tallest: 0, tallestName: '' };
function districtOf(e, n) {
  for (const d of DISTRICTS) if (inPolys(polys[d], e, n)) return d === 'Islands' ? (inPolys(lantau, e, n) ? 'Islands · Lantau' : 'Islands · other islands') : d;
  return 'unassigned';
}
const t0 = Date.now();
for (let i = 0; i < D.count; i++) {
  const e = D.cE[i], n = D.cN[i], r = row(districtOf(e, n)), f = D.flags[i];
  r.blocks++; r.type[f & 3]++; if (!(f & 4)) r.surveyed++; r.use[(f >> 4) & 7]++;
  if (e >= HARBOUR[0] && e <= HARBOUR[2] && n >= HARBOUR[1] && n <= HARBOUR[3]) r.fine++;
  if (D.hgt[i] > r.tallest && !(f & 4)) { r.tallest = D.hgt[i]; r._tE = e; r._tN = n; }   // tallest by height above its base (hilltop huts would win on mPD)
}
for (const t of names) row(districtOf(t.E, t.N)).named++;
for (const r of Object.values(rows)) {
  if (r._tE != null) { let best = null, bd = 1e9; for (const t of names) { const d = Math.hypot(t.E - r._tE, t.N - r._tN); if (d < bd) { bd = d; best = t; } } r.tallestName = best && bd < 60 ? best.en : ''; }
  delete r._tE; delete r._tN;
}
console.error(`classified ${D.count} blocks in ${((Date.now() - t0) / 1000).toFixed(1)} s`);

const order = [...DISTRICTS.filter(d => d !== 'Islands'), 'Islands · Lantau', 'Islands · other islands', 'unassigned'].filter(k => rows[k]);
const pct = (a, b) => b ? Math.round(100 * a / b) + ' %' : '—';
const fmt = n => n.toLocaleString('en-GB');
let md = '| District | Region | Blocks | Towers | Podia | Sheds / canopies | Surveyed height | On 20 m mesh | Homes | Offices | Shops | Industry | Villages | Named ≥ 100 m | Tallest |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n';
let tot = { blocks: 0, type: [0, 0, 0, 0], surveyed: 0, fine: 0, use: [0, 0, 0, 0, 0, 0, 0], named: 0 };
for (const k of order) {
  const r = rows[k];
  md += `| ${k} | ${r.region} | ${fmt(r.blocks)} | ${fmt(r.type[0])} | ${fmt(r.type[1])} | ${fmt(r.type[2] + r.type[3])} | ${pct(r.surveyed, r.blocks)} | ${pct(r.fine, r.blocks)} | ${fmt(r.use[0])} | ${fmt(r.use[1])} | ${fmt(r.use[2])} | ${fmt(r.use[3])} | ${fmt(r.use[5])} | ${r.named} | ${r.tallestName ? r.tallestName + ' ' : ''}${Math.round(r.tallest)} m |\n`;
  tot.blocks += r.blocks; tot.surveyed += r.surveyed; tot.fine += r.fine; tot.named += r.named; r.type.forEach((v, i) => tot.type[i] += v); r.use.forEach((v, i) => tot.use[i] += v);
}
md += `| **All Hong Kong** | | **${fmt(tot.blocks)}** | ${fmt(tot.type[0])} | ${fmt(tot.type[1])} | ${fmt(tot.type[2] + tot.type[3])} | ${pct(tot.surveyed, tot.blocks)} | ${pct(tot.fine, tot.blocks)} | ${fmt(tot.use[0])} | ${fmt(tot.use[1])} | ${fmt(tot.use[2])} | ${fmt(tot.use[3])} | ${fmt(tot.use[5])} | ${tot.named} | |\n`;
console.log(md);
if (opt('--json')) writeFileSync(opt('--json'), JSON.stringify({ generated: new Date().toISOString().slice(0, 10), source: 'hk-buildings.bin (LandsD Building layer v20260819)', districts: 'OSM administrative boundaries via Nominatim (ODbL), report use only', rows: order.map(k => rows[k]) }, null, 1));
if (opt('--md')) writeFileSync(opt('--md'), md);
