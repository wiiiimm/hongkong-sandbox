#!/usr/bin/env node
/* build_urban_mesh.mjs — a finer terrain mesh for the urban core around Victoria
 * Harbour, cut from the Lands Department 5 m DTM.  (HKS-114 follow-up)
 *
 * The whole-territory mesh (data/hk-dtm5m.json) averages the 5 m LiDAR to 70 m
 * cells so 63 × 48 km fits in ~620k vertices. In the city that smooths away the
 * reclamation edges, the Mid-Levels terraces and every street-scale slope the
 * buildings stand on. This script cuts a 22 × 22 km window — Hong Kong Island,
 * Kowloon, Kwai Tsing / Tsuen Wan, Sha Tin's south and Tseung Kwan O — at 20 m
 * cells (4 × 4 LiDAR cells averaged): 1100 × 1100 = 1.21 M vertices, 3.5× finer
 * than the territory mesh, in the SAME HK1980 grid so every overlay (B50K
 * vectors, land cover, buildings, labels, GPX) drapes unchanged.
 *
 * Source (fetched on first run, cached in ./cache/ — git-ignored, 28.7 MB zip →
 * 302 MB ESRI ASCII grid):
 *   Digital Terrain Model (DTM), 5 m — Lands Department / CSDI via DATA.GOV.HK
 *   https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip
 *   ncols 12751 · nrows 9601 · xllcorner 799997.5 · yllcorner 799997.5 · cellsize 5
 *   · NODATA −9999 · heights in metres above HK Principal Datum · HK1980 grid
 *   (EPSG:2326) · 2020 territory-wide LiDAR, ±5 m. DATA.GOV.HK Terms of Use.
 *
 * Outputs (3d-viewer/data/):
 *   hk-harbour-dtm20m.json  { w, h, cell, zmax, elev[] (integer metres, row-major
 *                             north→south, west→east; sea / NODATA = 0), peaks: [] }
 *   hk-harbour-georef.json  { aE, bE, aN, bN, W, H } — cell-centre grid → HK1980,
 *                             the same flat shape as hk-georef.json
 *
 * Run:  node source-scripts/hk-5m/build_urban_mesh.mjs      (≈ 1–2 min, needs `unzip`)
 */
import { createReadStream, createWriteStream, existsSync, mkdirSync, statSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';

const HERE = dirname(fileURLToPath(import.meta.url));
const CACHE = join(HERE, 'cache');
const OUT = join(HERE, '..', '..', '3d-viewer', 'data');
const ZIP_URL = 'https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip';
const ZIP = join(CACHE, 'Whole_HK_DTM_5m.zip');

// the window, HK1980 metres, and the output cell
const E0 = 826000, E1 = 848000, N0 = 806000, N1 = 828000, FAC = 4;   // 4 × 5 m = 20 m cells

async function ensureAsc() {
  mkdirSync(CACHE, { recursive: true });
  if (!existsSync(ZIP) || statSync(ZIP).size < 1e7) {
    console.log('fetching', ZIP_URL);
    const res = await fetch(ZIP_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status} fetching the DTM zip`);
    await pipeline(Readable.fromWeb(res.body), createWriteStream(ZIP));
  }
  const name = execFileSync('unzip', ['-Z1', ZIP]).toString().split('\n').find(n => /\.asc$/i.test(n));
  const asc = join(CACHE, name);
  if (!existsSync(asc)) { console.log('unzipping', name); execFileSync('unzip', ['-o', '-q', ZIP, name, '-d', CACHE]); }
  return asc;
}

const asc = await ensureAsc();
const t0 = Date.now();
// stream the grid line by line
const rl = (await import('node:readline')).createInterface({ input: createReadStream(asc, { highWaterMark: 1 << 22 }), crlfDelay: Infinity });
const hdr = {};
let ncols, nrows, cs, xll, yll, nodata;
let r0, r1, c0, c1, W, H, out, acc, rowsIn = 0, orow = 0, row = -1, zmax = -1e9;
for await (const line of rl) {
  if (row < 0) {                                  // 6 header lines
    const [k, v] = line.trim().split(/\s+/);
    hdr[k.toLowerCase()] = +v;
    if (Object.keys(hdr).length === 6) {
      ({ ncols, nrows, cellsize: cs, xllcorner: xll, yllcorner: yll, nodata_value: nodata } = hdr);
      // source rows run north → south; row r's cell centre is at N = yll + (nrows − r − 0.5)·cs
      r0 = Math.round(nrows - 0.5 - (N1 - yll) / cs);           // first row inside the window (north edge)
      r1 = Math.round(nrows - 0.5 - (N0 - yll) / cs);           // one past the last
      c0 = Math.round((E0 - xll) / cs - 0.5); c1 = Math.round((E1 - xll) / cs - 0.5);
      W = Math.floor((c1 - c0) / FAC); H = Math.floor((r1 - r0) / FAC);
      out = new Float64Array(W * H); acc = new Float64Array(W);
      console.log(`grid ${ncols}×${nrows} @ ${cs} m · window rows ${r0}–${r1} cols ${c0}–${c1} → ${W}×${H} @ ${cs * FAC} m`);
      row = 0;
    }
    continue;
  }
  if (row >= r0 && row < r1 && orow < H) {
    // parse only the window's columns; each row contributes 1/FAC of an output row
    let i = 0, col = 0, oc = 0, p = 0;
    // fast manual number scan (the line is ~65k chars; split() would allocate 12k strings per row)
    const L = line.length;
    while (p < L && col < c1) {
      while (p < L && line.charCodeAt(p) === 32) p++;
      let q = p; while (q < L && line.charCodeAt(q) !== 32) q++;
      if (col >= c0) {
        let v = +line.slice(p, q);
        if (!(v > -9000)) v = 0; else if (v < 0) v = 0;   // NODATA / below datum → sea level
        acc[(col - c0) >> 2] += v;                         // >> 2 == / FAC for FAC = 4
      }
      col++; p = q;
    }
    rowsIn++;
    if (rowsIn === FAC) {
      const base = orow * W;
      for (let x = 0; x < W; x++) { const e = acc[x] / (FAC * FAC); out[base + x] = e; if (e > zmax) zmax = e; acc[x] = 0; }
      rowsIn = 0; orow++;
      if (orow % 100 === 0) console.log(`  ${orow}/${H} rows · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    }
  }
  row++;
  if (row >= r1) break;
}
const elev = Array.from(out, v => Math.round(v));
const cell = cs * FAC;
const georef = { aE: cell, bE: xll + (c0 + FAC / 2) * cs, aN: -cell, bN: yll + (nrows - r0 - FAC / 2) * cs, W, H };
mkdirSync(OUT, { recursive: true });
writeFileSync(join(OUT, 'hk-harbour-dtm20m.json'), JSON.stringify({ w: W, h: H, cell, zmax: Math.round(zmax * 100) / 100, elev, peaks: [] }));
writeFileSync(join(OUT, 'hk-harbour-georef.json'), JSON.stringify(georef));
console.log('georef', georef, 'zmax', zmax.toFixed(1), `· ${((Date.now() - t0) / 1000).toFixed(0)} s`);
console.log('→ 3d-viewer/data/hk-harbour-dtm20m.json', (statSync(join(OUT, 'hk-harbour-dtm20m.json')).size / 1048576).toFixed(1), 'MB');
