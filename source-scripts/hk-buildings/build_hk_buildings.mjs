#!/usr/bin/env node
/* build_hk_buildings.mjs — generate 3d-viewer/data/hk-buildings.bin (+ .json, -names.json)  (HKS-114)
 *
 * Every building block in Hong Kong, as compact footprint + absolute height records
 * the viewer extrudes into a 3D city on top of the terrain.
 *
 * Source (fetched live on first run, cached in ./cache/ — not committed, 397 MB):
 *   Lands Department "Building" layer, via the CSDI portal (DATA.GOV.HK Terms of Use)
 *   dataset landsd_rcd_1637211194312_35158 · Building_Outline_Public_v20260819
 *   https://portal.csdi.gov.hk/csdi-webpage/dataset/landsd_rcd_1637211194312_35158
 *   GeoJSON export:
 *   https://portal.csdi.gov.hk/csdi-webpage/file-api?dataset_id=landsd_rcd_1637211194312_35158&format=geojson&layer_name=Building
 *
 *   342,223 polygons. Attributes used: BaseHeight / TopHeight (metres above HK
 *   Principal Datum — the SAME vertical datum as the LandsD 5 m DTM the viewer
 *   renders, so blocks land on the terrain without any height fudge),
 *   BuildingBlockType (Tower / Podium / Open-sided Structure / Temporary Structure),
 *   BuildingNameEN/TC, Storeys, Status. A "building" in this layer is a BLOCK: a
 *   tower, its podium, and the plant room on its roof are separate polygons, each
 *   with its own absolute base + top. ~31% of blocks (nearly all temporary /
 *   open-sided structures — sheds, canopies, huts) carry no heights; they get a
 *   small default and are flagged so the viewer drapes them on the ground.
 *
 * CRS: the CSDI GeoJSON is WGS84 lon/lat. The viewer works in the HK1980 grid
 * (EPSG:2326). We reproject with the official 7-parameter Helmert (the inverse of
 * EPSG:1825 "Hong Kong 1980 to WGS 84 (1)") followed by the HK1980 Transverse
 * Mercator — verified against the CSDI FeatureServer's native outSR=2326
 * coordinates on 360 sampled vertices: 0.000 m residual.
 *
 * Output format (little-endian, then gzipped — the viewer inflates it with
 * DecompressionStream, since hosts don't compress application/octet-stream):
 *   'HKBL' u8 version(1) u8 reserved u16 reserved u32 count
 *   f64 originE f64 originN f32 quant(m)
 *   count × record:
 *     u8 flags   bits0-1 type (0 Tower, 1 Podium, 2 Open-sided, 3 Temporary)
 *                bit2 height estimated (source had none)   bit3 base unknown (drape on ground)
 *     varint nRings; per ring: varint nVerts, then nVerts × (zigzag dE, zigzag dN) in quanta,
 *       delta-coded from the previous vertex; ring 0's first vertex is a delta from the
 *       previous record's first vertex (records are tile-sorted so this stays small);
 *       ring k>0 starts as a delta from ring 0's first vertex
 *     zigzag base (dm)   varint height (dm)
 *   Rings are simplified (Douglas–Peucker, 0.3 m) and the GeoJSON closing vertex dropped.
 *
 * Run:  node source-scripts/hk-buildings/build_hk_buildings.mjs
 * Requires only Node ≥ 18 (fetch, zlib). ~2 GB free RAM.
 */

import { createReadStream, createWriteStream, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { gzipSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';

const HERE = dirname(fileURLToPath(import.meta.url));
const CACHE = join(HERE, 'cache');
const OUT_DIR = join(HERE, '..', '..', '3d-viewer', 'data');
const VERSION_TAG = 'v20260819';
const SRC_FILE = join(CACHE, `Building_Outline_Public_${VERSION_TAG}_Building_converted.geojson`);
const SRC_URL = 'https://portal.csdi.gov.hk/csdi-webpage/file-api?dataset_id=landsd_rcd_1637211194312_35158&format=geojson&layer_name=Building';

const QUANT = 0.25;              // metres per coordinate quantum
const SIMPLIFY_TOL = 0.3;        // Douglas–Peucker tolerance, metres (visually lossless at street scale)
const MIN_RING_AREA = 0.5;       // m² — drop slivers
const ORIGIN_E = 800000, ORIGIN_N = 800000;
const DEFAULT_H = { 2: 3.5, 3: 3.0 };   // metres for height-less open-sided / temporary structures
const NAME_MIN_H = 100;          // metres — named towers this tall go to the names sidecar
const TYPE = { 'Tower': 0, 'Podium': 1, 'Open-sided Structure': 2, 'Temporary Structure': 3 };

// ---- HK1980 grid: WGS84 → HK80 (Helmert, inverse EPSG:1825) → Transverse Mercator --------
const D2R = Math.PI / 180, AS2R = D2R / 3600;
const WGS = { a: 6378137, f: 1 / 298.257223563 }; WGS.e2 = WGS.f * (2 - WGS.f);
const INT = { a: 6378388, f: 1 / 297 }; INT.e2 = INT.f * (2 - INT.f);   // International 1924 (Hayford) — HK80's ellipsoid
// EPSG:1825 Hong Kong 1980 → WGS 84 (1), position-vector rotation convention
const HLM = { dx: -162.619, dy: -276.959, dz: -161.764, rx: 0.067753 * AS2R, ry: -2.243649 * AS2R, rz: -1.158827 * AS2R, ds: -1.094246e-6 };
const HK = { a: INT.a, e2: INT.e2, FE: 836694.05, FN: 819069.80, k0: 1.0,
             lat0: (22 + 18 / 60 + 43.68 / 3600) * D2R, lon0: (114 + 10 / 60 + 42.80 / 3600) * D2R };
function geoToEcef(lat, lon, el) {
  const s = Math.sin(lat), c = Math.cos(lat), N = el.a / Math.sqrt(1 - el.e2 * s * s);
  return [N * c * Math.cos(lon), N * c * Math.sin(lon), N * (1 - el.e2) * s];
}
function ecefToGeo(x, y, z, el) {
  const lon = Math.atan2(y, x), p = Math.hypot(x, y);
  let lat = Math.atan2(z, p * (1 - el.e2));
  for (let i = 0; i < 8; i++) { const s = Math.sin(lat), N = el.a / Math.sqrt(1 - el.e2 * s * s); lat = Math.atan2(z + el.e2 * N * s, p); }
  return [lat, lon];
}
function wgsToHk80(lat, lon) {            // radians in, radians out
  const [x, y, z] = geoToEcef(lat, lon, WGS);
  const m = 1 + HLM.ds, X = (x - HLM.dx) / m, Y = (y - HLM.dy) / m, Z = (z - HLM.dz) / m;
  const { rx, ry, rz } = HLM;             // inverse of the small-angle rotation = its transpose
  return ecefToGeo(X + rz * Y - ry * Z, -rz * X + Y + rx * Z, ry * X - rx * Y + Z, INT);
}
function meridianArc(lat) {
  const e2 = HK.e2, e4 = e2 * e2, e6 = e4 * e2;
  return HK.a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * lat - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * Math.sin(2 * lat)
    + (15 * e4 / 256 + 45 * e6 / 1024) * Math.sin(4 * lat) - (35 * e6 / 3072) * Math.sin(6 * lat));
}
const M0 = meridianArc(HK.lat0);
function llToEN(phi, lam) {              // HK80 geodetic (radians) → grid metres; same series as the viewer's llToEN
  const e2 = HK.e2, ep2 = e2 / (1 - e2);
  const s = Math.sin(phi), c = Math.cos(phi), t = Math.tan(phi);
  const N1 = HK.a / Math.sqrt(1 - e2 * s * s), T = t * t, C = ep2 * c * c, A = (lam - HK.lon0) * c;
  const E = HK.FE + HK.k0 * N1 * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5 / 120);
  const N = HK.FN + HK.k0 * (meridianArc(phi) - M0 + N1 * t * (A * A / 2 + (5 - T + 9 * C + 4 * C * C) * A ** 4 / 24 + (61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6 / 720));
  return [E, N];
}
const wgsToEN = (lon, lat) => { const [p, l] = wgsToHk80(lat * D2R, lon * D2R); return llToEN(p, l); };

// ---- geometry helpers --------------------------------------------------------------------
function signedArea(r) { let a = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) a += r[j][0] * r[i][1] - r[i][0] * r[j][1]; return a / 2; }   // shoelace: > 0 for counter-clockwise
function dp(pts, i0, i1, tol2, keep) {   // recursive Douglas–Peucker over pts[i0..i1], marking kept indices
  let maxD = 0, idx = -1;
  const [ax, ay] = pts[i0], [bx, by] = pts[i1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy;
  for (let i = i0 + 1; i < i1; i++) {
    const [px, py] = pts[i];
    let d2;
    if (L2 === 0) d2 = (px - ax) ** 2 + (py - ay) ** 2;
    else { const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); d2 = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2; }
    if (d2 > maxD) { maxD = d2; idx = i; }
  }
  if (maxD > tol2 && idx > 0) { keep[idx] = 1; dp(pts, i0, idx, tol2, keep); dp(pts, idx, i1, tol2, keep); }
}
function simplifyRing(ring, tol) {       // closed ring (no duplicate closer) → simplified closed ring
  const n = ring.length; if (n <= 4) return ring;
  // anchor the split at the vertex farthest from vertex 0 so the closure isn't collapsed
  let far = 1, fd = -1;
  for (let i = 1; i < n; i++) { const d = (ring[i][0] - ring[0][0]) ** 2 + (ring[i][1] - ring[0][1]) ** 2; if (d > fd) { fd = d; far = i; } }
  const keep = new Uint8Array(n); keep[0] = 1; keep[far] = 1;
  const tol2 = tol * tol;
  dp(ring, 0, far, tol2, keep);
  const wrap = ring.slice(far).concat(ring.slice(0, 1));   // far … n-1, 0
  const keep2 = new Uint8Array(wrap.length); dp(wrap, 0, wrap.length - 1, tol2, keep2);
  for (let i = 1; i < wrap.length - 1; i++) if (keep2[i]) keep[far + i] = 1;
  const out = []; for (let i = 0; i < n; i++) if (keep[i]) out.push(ring[i]);
  return out.length >= 3 ? out : ring;
}

// ---- varint writer -----------------------------------------------------------------------
class Buf {
  constructor(n) { this.b = new Uint8Array(n); this.p = 0; }
  grow(need) { if (this.p + need <= this.b.length) return; const nb = new Uint8Array(Math.max(this.b.length * 2, this.p + need)); nb.set(this.b); this.b = nb; }
  u8(v) { this.grow(1); this.b[this.p++] = v & 255; }
  u16(v) { this.grow(2); this.b[this.p++] = v & 255; this.b[this.p++] = (v >>> 8) & 255; }
  u32(v) { this.grow(4); for (let i = 0; i < 4; i++) this.b[this.p++] = (v >>> (8 * i)) & 255; }
  f32(v) { this.grow(4); new DataView(this.b.buffer).setFloat32(this.p, v, true); this.p += 4; }
  f64(v) { this.grow(8); new DataView(this.b.buffer).setFloat64(this.p, v, true); this.p += 8; }
  varint(v) { this.grow(10); v = v >>> 0; while (v >= 0x80) { this.b[this.p++] = (v & 0x7f) | 0x80; v >>>= 7; } this.b[this.p++] = v; }
  zig(v) { this.varint(v >= 0 ? v * 2 : -v * 2 - 1); }
  bytes() { return this.b.subarray(0, this.p); }
}

// ---- streaming GeoJSON feature reader (the export is pretty-printed; parse by brace depth) --
async function* features(file) {
  let buf = '', depth = 0, start = -1, inStr = false, esc = false, seenArr = false, pos = 0;
  for await (const chunk of createReadStream(file, { encoding: 'utf8', highWaterMark: 1 << 20 })) {
    buf += chunk;
    for (let i = pos; i < buf.length; i++) {
      const c = buf[i];
      if (inStr) { if (esc) esc = false; else if (c === '\\') esc = true; else if (c === '"') inStr = false; continue; }
      if (c === '"') { inStr = true; continue; }
      if (c === '[' && depth === 1) seenArr = true;
      if (c === '{') { if (depth === 1 && seenArr && start < 0) start = i; depth++; }
      else if (c === '}') { depth--; if (depth === 1 && start >= 0) { yield JSON.parse(buf.slice(start, i + 1)); start = -1; } }
    }
    if (start >= 0) { buf = buf.slice(start); start = 0; pos = buf.length; } else { buf = ''; pos = 0; }
  }
}

async function ensureSource() {
  if (existsSync(SRC_FILE) && statSync(SRC_FILE).size > 1e8) return;
  mkdirSync(CACHE, { recursive: true });
  console.log('fetching', SRC_URL, '(≈397 MB — a few minutes)');
  const res = await fetch(SRC_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching the CSDI GeoJSON`);
  await pipeline(Readable.fromWeb(res.body), createWriteStream(SRC_FILE));
  console.log('cached →', SRC_FILE);
}

// ---- main ----------------------------------------------------------------------------------
await ensureSource();
const t0 = Date.now();
const recs = [];                          // { E0, N0, tile, flags, rings:[[ [qE,qN],… ]], baseDm, hDm, name }
const stats = { read: 0, kept: 0, droppedGeom: 0, vertsIn: 0, vertsOut: 0, holes: 0, estimatedH: 0, byType: {} };
const names = new Map();                  // en → { en, tc, E, N, top, h }
for await (const f of features(SRC_FILE)) {
  stats.read++;
  const p = f.properties, g = f.geometry;
  if (p.Status && p.Status !== 'Active') continue;
  const type = TYPE[p.BuildingBlockType] ?? 0;
  const polys = g.type === 'MultiPolygon' ? g.coordinates : g.type === 'Polygon' ? [g.coordinates] : [];
  for (const poly of polys) {
    const rings = [];
    for (let k = 0; k < poly.length; k++) {
      let r = poly[k].map(([lon, lat]) => wgsToEN(lon, lat));
      stats.vertsIn += r.length;
      if (r.length > 1 && Math.abs(r[0][0] - r[r.length - 1][0]) < 1e-6 && Math.abs(r[0][1] - r[r.length - 1][1]) < 1e-6) r.pop();
      // dedupe consecutive near-identical vertices
      r = r.filter((v, i) => i === 0 || Math.abs(v[0] - r[i - 1][0]) > 1e-4 || Math.abs(v[1] - r[i - 1][1]) > 1e-4);
      if (r.length < 3) { if (k === 0) rings.length = 0; if (k === 0) break; else continue; }
      r = simplifyRing(r, SIMPLIFY_TOL);
      const a = signedArea(r);
      if (Math.abs(a) < MIN_RING_AREA) { if (k === 0) { rings.length = 0; break; } continue; }
      // orientation: outer ring counter-clockwise in (E,N), holes clockwise — the viewer relies on it
      if ((k === 0 && a < 0) || (k > 0 && a > 0)) r.reverse();
      // quantise
      const q = r.map(([E, N]) => [Math.round((E - ORIGIN_E) / QUANT), Math.round((N - ORIGIN_N) / QUANT)]);
      const qd = q.filter((v, i) => i === 0 || v[0] !== q[i - 1][0] || v[1] !== q[i - 1][1]);
      if (qd.length >= 3) rings.push(qd);
      else if (k === 0) { rings.length = 0; break; }
    }
    if (!rings.length) { stats.droppedGeom++; continue; }
    let flags = type, base = p.BaseHeight, top = p.TopHeight, h;
    if (base == null || top == null || top - base <= 0) {
      h = DEFAULT_H[type] ?? 3.5; flags |= 4 | 8; base = 0; stats.estimatedH++;   // estimated height, unknown base → drape
    } else h = top - base;
    const rec = { E0: rings[0][0][0], N0: rings[0][0][1], flags, rings, baseDm: Math.round(base * 10), hDm: Math.round(h * 10) };
    // 2 km tile key for the sort (row-major, north→south then west→east) keeps first-vertex deltas small
    const tE = Math.floor(rec.E0 * QUANT / 2000), tN = Math.floor(rec.N0 * QUANT / 2000);
    rec.tile = (40 - tN) * 64 + tE;
    recs.push(rec);
    stats.kept++; stats.holes += rings.length - 1;
    for (const r of rings) stats.vertsOut += r.length;
    stats.byType[p.BuildingBlockType] = (stats.byType[p.BuildingBlockType] || 0) + 1;
    if (p.BuildingNameEN && !(flags & 4) && h >= NAME_MIN_H) {
      const en = p.BuildingNameEN.trim(), prev = names.get(en);
      if (!prev || h > prev.h) {
        // label at the footprint centroid (quanta → metres)
        let cx = 0, cy = 0; for (const v of rings[0]) { cx += v[0]; cy += v[1]; }
        names.set(en, { en, tc: (p.BuildingNameTC || '').trim(), E: Math.round(ORIGIN_E + cx / rings[0].length * QUANT), N: Math.round(ORIGIN_N + cy / rings[0].length * QUANT), top: Math.round(top * 10) / 10, h: Math.round(h * 10) / 10 });
      }
    }
  }
  if (stats.read % 50000 === 0) console.log(`  ${stats.read} features…`);
}
console.log(`parsed ${stats.read} features in ${((Date.now() - t0) / 1000).toFixed(1)} s`);

recs.sort((a, b) => a.tile - b.tile || a.E0 - b.E0);
const out = new Buf(16 << 20);
out.u8(0x48); out.u8(0x4b); out.u8(0x42); out.u8(0x4c);   // 'HKBL'
out.u8(1); out.u8(0); out.u16(0);
out.u32(recs.length);
out.f64(ORIGIN_E); out.f64(ORIGIN_N); out.f32(QUANT);
let pE = 0, pN = 0;
for (const r of recs) {
  out.u8(r.flags);
  out.varint(r.rings.length);
  for (let k = 0; k < r.rings.length; k++) {
    const ring = r.rings[k];
    out.varint(ring.length);
    let cE = k === 0 ? pE : r.rings[0][0][0], cN = k === 0 ? pN : r.rings[0][0][1];
    for (const [e, n] of ring) { out.zig(e - cE); out.zig(n - cN); cE = e; cN = n; }
  }
  pE = r.rings[0][0][0]; pN = r.rings[0][0][1];
  out.zig(r.baseDm); out.varint(r.hDm);
}
const raw = out.bytes();
const gz = gzipSync(raw, { level: 9 });
mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(join(OUT_DIR, 'hk-buildings.bin'), gz);

const nameList = [...names.values()].sort((a, b) => b.top - a.top);
writeFileSync(join(OUT_DIR, 'hk-buildings-names.json'), JSON.stringify({
  note: `Named building blocks ≥ ${NAME_MIN_H} m tall (one entry per name — the tallest block), HK1980 grid centroid, top in mPD. Source: LandsD Building layer via CSDI (${VERSION_TAG}), DATA.GOV.HK Terms of Use.`,
  count: nameList.length, towers: nameList,
}));

const meta = {
  note: 'Hong Kong building blocks for the 3D viewer — see source-scripts/hk-buildings/build_hk_buildings.mjs for the format and provenance.',
  source: 'Lands Department "Building" layer (Building_Outline_Public), via the CSDI portal — https://portal.csdi.gov.hk/csdi-webpage/dataset/landsd_rcd_1637211194312_35158',
  sourceVersion: VERSION_TAG, licence: 'DATA.GOV.HK Terms of Use (attribution: Lands Department, HKSAR Government)',
  crs: 'HK1980 grid (EPSG:2326); heights in metres above HK Principal Datum',
  generated: new Date().toISOString().slice(0, 10), format: 'HKBL v1, gzip', quant: QUANT, origin: [ORIGIN_E, ORIGIN_N],
  count: recs.length, verts: stats.vertsOut, holes: stats.holes, estimatedHeights: stats.estimatedH, byType: stats.byType,
  bytes: { raw: raw.length, gzip: gz.length }, names: nameList.length,
};
writeFileSync(join(OUT_DIR, 'hk-buildings.json'), JSON.stringify(meta, null, 1));
console.log(meta);
console.log(`vertices ${stats.vertsIn} → ${stats.vertsOut} after simplify · dropped geom ${stats.droppedGeom} · ${((Date.now() - t0) / 1000).toFixed(1)} s`);
console.log(`hk-buildings.bin: ${(raw.length / 1048576).toFixed(2)} MB raw → ${(gz.length / 1048576).toFixed(2)} MB gzip · names ${nameList.length}`);
