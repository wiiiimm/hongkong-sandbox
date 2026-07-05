#!/usr/bin/env node
/* build_hk_sky.mjs — generate 3d-viewer/data/hk-sky.json (HKS-84)
 *
 * A real star catalogue + curated constellation figures for the viewer's
 * night sky, replacing the 78-star hand-curated data/hk-stars.json.
 *
 * Sources (all fetched live, cached in ./cache/ for reproducibility):
 *   • Yale Bright Star Catalogue, 5th rev. ed. (BSC5) — CDS V/50, public
 *     domain. https://cdsarc.cds.unistra.fr/ftp/V/50/catalog.gz
 *     Fixed-width fields per the V/50 ReadMe: HR 1-4, RA J2000 h/m/s 76-83,
 *     Dec J2000 sign/d/m/s 84-90, Vmag 103-107, B-V 110-114.
 *   • Hipparcos main catalogue (ESA 1997) — CDS I/239, hip_main.dat
 *     (pipe-delimited; fields: [1] HIP, [5] Vmag, [8] RAdeg, [9] DEdeg).
 *     Used only to resolve the figures' HIP ids to HR numbers by positional
 *     crossmatch against BSC5 (the IV/27A cross index only covers the 3,690
 *     Bayer/Flamsteed stars — too sparse for full figure coverage). 52 MB,
 *     cached locally but NOT committed (see .gitignore); the script refetches
 *     it on a clean checkout.
 *   • Stellarium western sky-culture constellation figures (figure topology
 *     only) — constellationship.fab @ v0.20.4 (pinned tag), lines keyed by
 *     HIP. https://github.com/Stellarium/stellarium
 *
 * Output: compact array-of-arrays star list [HR, ra_hours, dec_deg, mag, bv]
 * trimmed to Vmag ≤ MAG_LIMIT and Dec ≥ DEC_MIN (nothing below −65° rises
 * usefully at Hong Kong's 22.3° N), plus ~24 curated constellations
 * { iau, en, zh, stars, lines, centroid } recognisable from HK. Figure stars
 * fainter than the magnitude cut are force-included so every line resolves.
 *
 * Run:  node source-scripts/hk-sky/build_hk_sky.mjs
 */

import { execFileSync } from 'node:child_process';
import { mkdirSync, existsSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const CACHE = join(HERE, 'cache');
const OUT = join(HERE, '..', '..', '3d-viewer', 'data', 'hk-sky.json');

const MAG_LIMIT = 5.0;   // Vmag cut for the general field (HK is Bortle 8-9)
const DEC_MIN = -65;     // degrees — keeps Crux/α Cen, drops the far south

const SOURCES = {
  'bsc5-catalog.gz': 'https://cdsarc.cds.unistra.fr/ftp/V/50/catalog.gz',
  'hip_main.dat': 'https://cdsarc.cds.unistra.fr/ftp/I/239/hip_main.dat',
  'constellationship.fab': 'https://raw.githubusercontent.com/Stellarium/stellarium/v0.20.4/skycultures/western/constellationship.fab',
};

// The curated P1 set: constellations visible from HK and actually
// recognisable, with the standard IAU Chinese names used in HK astronomy
// education (HK Space Museum convention). Full 88 is HKS-84 P3.
const CURATED = [
  ['And', 'Andromeda',        '仙女座'],
  ['Aql', 'Aquila',           '天鷹座'],
  ['Aur', 'Auriga',           '御夫座'],
  ['Boo', 'Boötes',           '牧夫座'],
  ['CMa', 'Canis Major',      '大犬座'],
  ['CMi', 'Canis Minor',      '小犬座'],
  ['Cas', 'Cassiopeia',       '仙后座'],
  ['Cen', 'Centaurus',        '半人馬座'],
  ['Cet', 'Cetus',            '鯨魚座'],
  ['CrB', 'Corona Borealis',  '北冕座'],
  ['Cru', 'Crux',             '南十字座'],
  ['Cyg', 'Cygnus',           '天鵝座'],
  ['Del', 'Delphinus',        '海豚座'],
  ['Gem', 'Gemini',           '雙子座'],
  ['Leo', 'Leo',              '獅子座'],
  ['Lyr', 'Lyra',             '天琴座'],
  ['Ori', 'Orion',            '獵戶座'],
  ['Peg', 'Pegasus',          '飛馬座'],
  ['Per', 'Perseus',          '英仙座'],
  ['Sco', 'Scorpius',         '天蠍座'],
  ['Sgr', 'Sagittarius',      '人馬座'],
  ['Tau', 'Taurus',           '金牛座'],
  ['UMa', 'Ursa Major',       '大熊座'],
  ['Vir', 'Virgo',            '室女座'],
];

// ---- fetch with cache -------------------------------------------------------
function fetchCached(name, url) {
  const path = join(CACHE, name);
  if (!existsSync(path)) {
    console.log(`fetching ${url}`);
    mkdirSync(CACHE, { recursive: true });
    execFileSync('curl', ['-sSfL', '--max-time', '120', '-o', path, url], { stdio: 'inherit' });
  }
  return readFileSync(path);
}

// ---- spherical helpers ------------------------------------------------------
const D2R = Math.PI / 180;
const dirOf = s => {
  const ra = s.ra / 24 * Math.PI * 2, dec = s.dec * D2R;
  return [Math.cos(dec) * Math.cos(ra), Math.cos(dec) * Math.sin(ra), Math.sin(dec)];
};
const angle = (a, b) => Math.acos(Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]))) / D2R;

// ---- parse BSC5 (fixed-width, 1-indexed byte ranges per the V/50 ReadMe) ----
const fw = (line, a, b) => line.slice(a - 1, b).trim();   // 1-indexed inclusive
function parseBSC(text) {
  const stars = new Map();   // HR -> { hr, ra, dec, mag, bv }
  for (const line of text.split('\n')) {
    if (line.length < 107) continue;
    const hr = parseInt(fw(line, 1, 4), 10);
    const rah = fw(line, 76, 77), ram = fw(line, 78, 79), ras = fw(line, 80, 83);
    const mags = fw(line, 103, 107);
    if (!hr || rah === '' || mags === '') continue;   // novae / non-stellar entries have blank positions
    const ra = (+rah) + (+ram) / 60 + (+ras) / 3600;               // hours
    const sgn = fw(line, 84, 84) === '-' ? -1 : 1;
    const dec = sgn * ((+fw(line, 85, 86)) + (+fw(line, 87, 88)) / 60 + (+fw(line, 89, 90)) / 3600);
    const bvs = fw(line, 110, 114);
    stars.set(hr, { hr, ra, dec, mag: +mags, bv: bvs === '' ? 0 : +bvs });
  }
  return stars;
}

// ---- HIP → HR by positional crossmatch (Hipparcos I/239 vs BSC5) ------------
// hip_main.dat is pipe-delimited: [1] HIP, [5] Vmag, [8] RAdeg, [9] DEdeg.
// Only the HIPs the figures actually use are looked up; each is matched to the
// nearest BSC5 star and accepted within 0.03° (HIP/BSC positions agree to
// arcseconds — 0.03° is generous for double-star component offsets).
function crossmatchHip(text, wanted, bscList) {
  const map = new Map();
  for (const line of text.split('\n')) {
    const f = line.split('|');
    if (f.length < 10) continue;
    const hip = parseInt(f[1], 10);
    if (!wanted.has(hip)) continue;
    const raDeg = +f[8], deDeg = +f[9];
    if (!Number.isFinite(raDeg) || !Number.isFinite(deDeg)) continue;
    const hd = { ra: raDeg / 15, dec: deDeg };
    let best = null, bestA = 0.03;                 // degrees
    for (const s of bscList) {
      if (Math.abs(s.dec - deDeg) > 0.05) continue;   // cheap prefilter
      const a = angle(dirOf(hd), dirOf(s));
      if (a < bestA) { bestA = a; best = s; }
    }
    if (best) map.set(hip, best.hr);
  }
  return map;
}

// ---- parse Stellarium constellationship.fab (per-constellation HIP pairs) ---
function parseFab(text) {
  const figures = new Map();   // iau -> [[hipA, hipB], ...]
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const tok = line.split(/\s+/);
    const iau = tok[0], n = parseInt(tok[1], 10);
    if (!n || tok.length < 2 + n * 2) continue;
    const pairs = [];
    for (let i = 0; i < n; i++) pairs.push([+tok[2 + i * 2], +tok[3 + i * 2]]);
    figures.set(iau, pairs);
  }
  return figures;
}

// ---- main -------------------------------------------------------------------
const bsc = parseBSC(gunzipSync(fetchCached('bsc5-catalog.gz', SOURCES['bsc5-catalog.gz'])).toString('latin1'));
const fab = parseFab(fetchCached('constellationship.fab', SOURCES['constellationship.fab']).toString('latin1'));
const wantedHips = new Set();
for (const [iau] of CURATED) for (const pr of (fab.get(iau) || [])) { wantedHips.add(pr[0]); wantedHips.add(pr[1]); }
const hip2hr = crossmatchHip(fetchCached('hip_main.dat', SOURCES['hip_main.dat']).toString('latin1'),
                             wantedHips, [...bsc.values()]);

console.log(`BSC5 parsed: ${bsc.size} stars · fab figures: ${fab.size} · figure HIPs: ${wantedHips.size} → HR resolved: ${hip2hr.size}`);

// sanity anchors — if the fixed-width columns were misread, these fail loudly
const anchors = [
  [32349, 2491, 'Sirius'], [91262, 7001, 'Vega'], [27989, 2061, 'Betelgeuse'], [24436, 1713, 'Rigel']];
for (const [hip, hr, name] of anchors) {
  if (hip2hr.get(hip) !== hr) throw new Error(`cross-index anchor failed: ${name} HIP ${hip} → ${hip2hr.get(hip)}, expected HR ${hr}`);
}
if (Math.abs(bsc.get(2491).mag - -1.46) > 0.05 || Math.abs(bsc.get(2491).dec - -16.716) > 0.05)
  throw new Error('BSC anchor failed: Sirius HR 2491 mag/dec off');

// 1) the general field: mag ≤ limit, dec ≥ min
const keep = new Set();
for (const s of bsc.values()) if (s.mag <= MAG_LIMIT && s.dec >= DEC_MIN) keep.add(s.hr);
console.log(`field cut (mag ≤ ${MAG_LIMIT}, dec ≥ ${DEC_MIN}°): ${keep.size} stars`);

// 2) curated constellations: map HIP→HR, force-include figure stars
const constellations = [];
for (const [iau, en, zh] of CURATED) {
  const pairs = fab.get(iau);
  if (!pairs) throw new Error(`no fab figure for ${iau}`);
  const lines = [], members = new Set();
  for (const [ha, hb] of pairs) {
    const a = hip2hr.get(ha), b = hip2hr.get(hb);
    if (!a || !b || !bsc.has(a) || !bsc.has(b)) {   // figure star below BSC limit — drop the segment
      console.warn(`  ${iau}: dropping segment HIP ${ha}-${hb} (no HR)`);
      continue;
    }
    lines.push([a, b]); members.add(a); members.add(b);
  }
  if (!lines.length) throw new Error(`${iau}: figure collapsed to 0 segments`);   // CMi is legitimately 1 segment
  for (const hr of members) keep.add(hr);          // force-include even if fainter than the cut
  // centroid: normalized mean of member unit vectors → ra/dec
  let cx = 0, cy = 0, cz = 0;
  for (const hr of members) { const d = dirOf(bsc.get(hr)); cx += d[0]; cy += d[1]; cz += d[2]; }
  const cl = Math.hypot(cx, cy, cz); cx /= cl; cy /= cl; cz /= cl;
  const cra = ((Math.atan2(cy, cx) / (Math.PI * 2)) * 24 + 24) % 24;
  const cdec = Math.asin(Math.max(-1, Math.min(1, cz))) / D2R;
  constellations.push({ iau, en, zh, stars: [...members].sort((x, y) => x - y),
                        lines, centroid: [+cra.toFixed(3), +cdec.toFixed(2)] });
}

// 3) emit the compact star table
const round = (v, d) => +v.toFixed(d);
const starRows = [...keep].sort((a, b) => a - b)
  .map(hr => { const s = bsc.get(hr); return [hr, round(s.ra, 4), round(s.dec, 3), round(s.mag, 2), round(s.bv, 2)]; });

// ---- validation --------------------------------------------------------------
const hrSet = new Set(starRows.map(r => r[0]));
let maxSeg = 0;
for (const c of constellations) {
  const cDir = dirOf({ ra: c.centroid[0], dec: c.centroid[1] });
  for (const hr of c.stars) {
    if (!hrSet.has(hr)) throw new Error(`${c.iau}: member HR ${hr} missing from star table`);
    const a = angle(dirOf(bsc.get(hr)), cDir);
    if (a > 35) throw new Error(`${c.iau}: HR ${hr} is ${a.toFixed(1)}° from centroid — bad mapping?`);
  }
  for (const [a, b] of c.lines) {
    if (!hrSet.has(a) || !hrSet.has(b)) throw new Error(`${c.iau}: line ${a}-${b} unresolved`);
    const seg = angle(dirOf(bsc.get(a)), dirOf(bsc.get(b)));
    if (seg > 30) throw new Error(`${c.iau}: segment ${a}-${b} spans ${seg.toFixed(1)}° — bad mapping?`);
    maxSeg = Math.max(maxSeg, seg);
  }
}
for (const r of starRows) if (r.some(v => !Number.isFinite(v))) throw new Error(`NaN in star row ${r}`);
if (starRows.length < 1200 || starRows.length > 2000) throw new Error(`unexpected star count ${starRows.length}`);
console.log(`validated: ${starRows.length} stars, ${constellations.length} constellations, longest segment ${maxSeg.toFixed(1)}°`);

// ---- write -------------------------------------------------------------------
const note = 'HK night-sky catalogue (HKS-84). Stars: Yale Bright Star Catalogue 5th rev. ed. (BSC5, public domain, Yale/CDS V/50), trimmed to Vmag <= ' + MAG_LIMIT + ' and Dec >= ' + DEC_MIN + ' deg for Hong Kong (22.3 N); figure stars fainter than the cut are force-included. Fields per star: [HR, ra_hours_J2000, dec_deg_J2000, Vmag, B-V]. Constellations: modern IAU figures adapted from the Stellarium western sky culture (constellationship.fab, figure topology), HIP ids resolved to HR by positional crossmatch against the Hipparcos main catalogue (ESA 1997, CDS I/239); Chinese names are the standard IAU names used in HK astronomy education. Generated by source-scripts/hk-sky/build_hk_sky.mjs.';
// one star per line keeps the diff sane without ballooning the file
const json = '{\n' +
  `"note": ${JSON.stringify(note)},\n` +
  `"fields": ${JSON.stringify(['HR', 'ra_hours', 'dec_deg', 'mag', 'bv'])},\n` +
  `"magLimit": ${MAG_LIMIT}, "decMin": ${DEC_MIN},\n` +
  '"stars": [\n' + starRows.map(r => JSON.stringify(r)).join(',\n') + '\n],\n' +
  '"constellations": [\n' + constellations.map(c => JSON.stringify(c)).join(',\n') + '\n]\n}\n';
JSON.parse(json);   // self-check
writeFileSync(OUT, json);
console.log(`wrote ${OUT} (${(json.length / 1024).toFixed(1)} KB)`);
