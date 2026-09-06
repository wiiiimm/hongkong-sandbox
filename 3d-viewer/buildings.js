// buildings.js — the 3D city (HKS-114): every building block in Hong Kong, extruded
// from the Lands Department "Building" layer onto the terrain.
//
// Data: data/hk-buildings.bin — 342k footprint polygons with ABSOLUTE base + top
// heights in metres above HK Principal Datum (the DTM's datum too), produced by
// source-scripts/hk-buildings/build_hk_buildings.mjs (format documented there).
// A "building" is a block: tower, podium and rooftop plant room are separate
// polygons stacked by their own base/top, so we never drape a block onto the
// ground individually — we place it at its true height and only sink a skirt
// down to the DEM where the block actually stands on the ground.
//
// Rendering: blocks are merged into chunked meshes in two disjoint tiers —
//   • big  (≥ BIG_H m tall or ≥ BIG_A m² footprint): 4 km chunks, built
//     progressively right after load and kept for the whole session — the city
//     massing you see from orbit;
//   • small (everything else — village houses, sheds, plant rooms): 1 km chunks
//     streamed in around the camera and evicted as you move away.
// Geometry is one indexed BufferGeometry per chunk with two groups (walls, roofs);
// walls carry metre-scaled UVs for a procedural window texture whose lit-window
// emissive map is driven by the sky simulation's luminance (the city lights up at
// dusk). Flat shading comes from screen-space derivatives, so no normals are stored.
//
// Night: every window bay has a stable random bedtime; the share still lit follows the
// sky simulation's Hong Kong clock PER LAND-USE CLASS (homes, offices, retail, industry,
// institutions, villages — classified from the Planning Department's land-utilisation
// grid in the build script), with shopfronts on the two lowest floors on retail hours.
//
// Movement: roofAt(x, z) answers "what is the highest block top here?" via a 100 m
// spatial hash + point-in-polygon, so Walk treats blocks as solid (and stands on
// roofs you drop onto) and Fly can set down on — or crash into — a rooftop.
import * as THREE from './vendor/three.module.js';

export function createBuildings(env) {
  // env: { world, renderer, asset, attachTerrainFX, grid(): {W,H,cell,g,meshStep}, sampleEtri, coarse }
  const { world, renderer, asset, attachTerrainFX, sampleEtri } = env;
  const coarse = !!env.coarse;
  const BIG_H = coarse ? 16 : 10, BIG_A = coarse ? 600 : 300;   // metres / m² — the "big" tier threshold
  const FAR_CHUNK = 4000, NEAR_CHUNK = 1000;                     // metres
  const NEAR_R = coarse ? 2200 : 4500, EVICT_R = NEAR_R * 1.8, MAX_NEAR = coarse ? 36 : 110;
  const HASH_CELL = 100;                                          // metres — collision spatial hash

  // ---- data ------------------------------------------------------------------
  let D = null;            // parsed dataset (see parse)
  let ready = false, loading = false, failed = false;
  let towers = [];         // named tall towers for labels (from data/hk-buildings-names.json)
  const group = new THREE.Group(); group.name = 'buildings'; world.add(group);

  // ---- materials --------------------------------------------------------------
  const WIN_M = 3.6;       // one texture tile = one 3.6 m window bay × one 3.6 m storey
  function windowTex() {
    const S = 64, c = document.createElement('canvas'); c.width = c.height = S;
    const x = c.getContext('2d');
    x.fillStyle = '#ffffff'; x.fillRect(0, 0, S, S);                      // facade (tinted by the vertex colour)
    x.fillStyle = 'rgba(0,0,0,0.10)'; x.fillRect(0, S - 5, S, 5);          // floor slab shadow line
    x.fillStyle = '#8b98a6'; x.fillRect(15, 14, 34, 30);                   // the window
    x.fillStyle = 'rgba(255,255,255,0.28)'; x.fillRect(15, 14, 34, 9);     // sky reflection on the upper pane
    x.fillStyle = 'rgba(0,0,0,0.18)'; x.fillRect(15, 41, 34, 3);           // sill
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / WIN_M, 1 / WIN_M);
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return t;
  }
  function litTex() {      // the glass-only mask of the same 3.6 m bay: white where a lit window would glow
    const S = 64, c = document.createElement('canvas'); c.width = c.height = S;
    const x = c.getContext('2d');
    x.fillStyle = '#000'; x.fillRect(0, 0, S, S);
    x.fillStyle = '#fff'; x.fillRect(16, 15, 32, 27);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / WIN_M, 1 / WIN_M);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  const matWall = new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, map: windowTex(),
    emissiveMap: litTex(), emissive: new THREE.Color(0xffd9a3), emissiveIntensity: 0, roughness: 0.82, metalness: 0 });
  const matRoof = new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, color: 0x8e8e8a, roughness: 1, metalness: 0 });
  attachTerrainFX(matWall, false);     // cloud shadows + height fog, like the terrain fill
  attachTerrainFX(matRoof, false);
  // The city's night life: every window bay gets a stable random "bedtime" (a hash of
  // its bay index + a coarse world cell, so the pattern never repeats across the
  // skyline), and uAwake — the share of households still up, driven from the sky
  // simulation's Hong Kong clock (setNight) — decides which are lit. Evening: most;
  // small hours: a scattered few (never none); dawn: the early risers come on.
  // Who is awake depends on what the block IS. Each block carries a land-use class
  // (flags bits 4–6, from the Planning Department's land-utilisation grid — see the
  // build script): offices start emptying at 18:00, some work on to 20:00, and by
  // midnight they are mostly dark bar a few all-nighters and cleaners; shops are the
  // first to switch on at dusk, start shutting around 21:00, are mostly closed by 23:00
  // and a few trade past midnight; homes fill up as people get back — the big wave
  // around 21:00, peak at 22:00 — and turn in from 23:00, so by 04:00 the city is
  // mostly (never entirely) asleep; industrial and institutional blocks keep a skeleton
  // of lights; villages turn in early. The two lowest floors of any urban block are
  // shopfronts, so they follow retail hours whatever the block above them does.
  // uDusk (0 day → 1 deep night) staggers the switch-on: shopfronts and offices glow
  // as soon as the light fades, homes only once it is properly dark.
  const USE = { RES: 0, OFFICE: 1, RETAIL: 2, INDUSTRIAL: 3, INSTITUTION: 4, VILLAGE: 5, OTHER: 6 };
  const awakeA = { value: new THREE.Vector4(0.6, 0.6, 0.6, 0.6) };   // RES, OFFICE, RETAIL, INDUSTRIAL
  const awakeB = { value: new THREE.Vector4(0.6, 0.6, 0.6, 0.0) };   // INSTITUTION, VILLAGE, OTHER, –
  const dusk = { value: 0 };
  const fxHook = matWall.onBeforeCompile;
  matWall.onBeforeCompile = (sh) => {
    fxHook(sh);
    sh.uniforms.uAwakeA = awakeA; sh.uniforms.uAwakeB = awakeB; sh.uniforms.uDusk = dusk;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nattribute float aUse;\nvarying float vUse;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvUse = aUse;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
        uniform vec4 uAwakeA; uniform vec4 uAwakeB; uniform float uDusk; varying float vUse;
        float hkbHash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }`)
      .replace('#include <emissivemap_fragment>', `
        #ifdef USE_EMISSIVEMAP
        { vec4 glass = texture2D(emissiveMap, vEmissiveMapUv);
          vec2 bay = floor(vMapUv) + 17.0 * floor(vWpos.xz / 37.0);   // one bay = one window (3.6 m grid), unique-ish across the city
          float u = vUse;
          float awake = u < 0.5 ? uAwakeA.x : u < 1.5 ? uAwakeA.y : u < 2.5 ? uAwakeA.z : u < 3.5 ? uAwakeA.w
                      : u < 4.5 ? uAwakeB.x : u < 5.5 ? uAwakeB.y : uAwakeB.z;
          if (floor(vMapUv.y) < 2.0 && u < 4.5) { awake = uAwakeA.z; u = 2.0; }   // shopfronts: ground + first floor keep retail hours
          float bed = hkbHash(bay);                                    // this household's bedtime rank
          float on = step(bed, awake) * (0.55 + 0.45 * hkbHash(bay + 9.1));
          // dusk stagger: shops light up as soon as the light fades, offices soon after, homes once it is dark
          float ramp = (u > 1.5 && u < 2.5) ? smoothstep(0.0, 0.42, uDusk) : (u > 0.5 && u < 1.5) ? smoothstep(0.08, 0.60, uDusk) : smoothstep(0.22, 0.85, uDusk);
          vec3 tone = mix(vec3(1.0, 0.90, 0.70), vec3(0.84, 0.91, 1.0), step(u < 1.5 && u > 0.5 ? 0.35 : 0.82, hkbHash(bay + 3.7)));   // warm bulbs at home, cool fluorescents in the offices
          totalEmissiveRadiance *= glass.rgb * tone * on * ramp; }
        #endif`);
  };
  // share of windows lit by Hong Kong clock hour, per use class (piecewise-linear keyframes)
  //   homes:   people drift back from 18:00, the big wave ~21:00, peak 22:00, turning in from 23:00; ~11% still up at 04:00
  //   offices: full to 17:00, emptying from 18:00, a share works to 20:00, mostly dark by 24:00 — a few all-nighters / cleaners
  //   shops:   bright 10:00–21:00, start shutting ~21:00, mostly closed by 23:00, a few trade past midnight
  const AWAKE = {
    [USE.RES]:         [[0, .52], [1, .34], [2, .22], [3, .15], [4, .11], [5, .14], [6, .30], [7, .42], [9, .28], [16, .32], [17, .42], [18, .55], [19, .66], [20, .76], [21, .86], [22, .93], [23, .80], [24, .52]],
    [USE.OFFICE]:      [[0, .07], [1, .05], [5, .04], [6, .06], [7, .15], [8, .55], [9, .85], [17, .85], [18, .78], [19, .58], [20, .38], [21, .24], [22, .16], [23, .11], [24, .07]],
    [USE.RETAIL]:      [[0, .18], [1, .11], [2, .08], [3, .07], [4, .06], [6, .06], [7, .15], [8, .30], [9, .55], [10, .88], [20, .92], [21, .88], [22, .68], [23, .38], [24, .18]],
    [USE.INDUSTRIAL]:  [[0, .08], [4, .06], [6, .08], [8, .55], [18, .55], [20, .30], [22, .14], [24, .08]],
    [USE.INSTITUTION]: [[0, .07], [6, .07], [8, .60], [17, .60], [18, .35], [20, .18], [22, .10], [24, .07]],
    [USE.VILLAGE]:     [[0, .25], [1, .15], [2, .10], [3, .08], [4, .07], [5, .15], [6, .30], [7, .35], [9, .25], [17, .40], [18, .65], [19, .75], [20, .72], [21, .62], [22, .45], [23, .35], [24, .25]],
    [USE.OTHER]:       [[0, .22], [4, .14], [6, .30], [8, .50], [18, .55], [20, .45], [22, .32], [24, .22]],
  };
  function awakeAt(h, use = USE.RES) {
    h = ((h % 24) + 24) % 24;
    const K = AWAKE[use] || AWAKE[USE.RES];
    for (let i = 1; i < K.length; i++) if (h <= K[i][0]) { const [h0, a0] = K[i - 1], [h1, a1] = K[i]; return a0 + (a1 - a0) * (h - h0) / (h1 - h0); }
    return K[K.length - 1][1];
  }
  const matMx = new THREE.MeshBasicMaterial({ color: 0x2fe463, wireframe: true, transparent: true, opacity: 0.3 });   // Matrix look
  let matrixLook = false;
  const materials = () => matrixLook ? [matMx, matMx] : [matWall, matRoof];

  // palette (sRGB → linear, since vertex colours are read as linear) — HK's facade
  // vocabulary: glass towers, pale concrete high-rises, warm tong-lau mid-rises,
  // village-house creams, grey-brown podia, sheet-metal sheds
  const lin = hex => { const c = new THREE.Color(hex).convertSRGBToLinear(); return [c.r, c.g, c.b]; };
  const PAL = {
    glass:   [lin(0xb9cbdb), lin(0xc9d5df), lin(0xaec3d3), lin(0xd2d9de)],   // curtain-wall office towers
    high:    [lin(0xe6e3dc), lin(0xdfe3e7), lin(0xe4d9c8), lin(0xebe8e2)],   // pale concrete / tile high-rises
    mid:     [lin(0xeae5da), lin(0xeddfc4), lin(0xe3d6cf), lin(0xdde3d6), lin(0xf0ece4)],   // tong lau warmth
    low:     [lin(0xe8e2d4), lin(0xe1dbcc), lin(0xece8de)],
    podium:  [lin(0xb9b4aa), lin(0xc2bbaf)],
    open:    [lin(0xc0c4bc), lin(0xc9c8c0)],
    temp:    [lin(0xbdb5a5), lin(0xb1aca4), lin(0xc5bbab)],
  };
  function tint(b, out) {
    const f = D.flags[b], type = f & 3, h = D.hgt[b];
    const hash = ((b * 2654435761) >>> 0) / 4294967296, h2 = (hash * 7919) % 1;
    // no use-class in the data: the very tall are offices (glass); 100–160 m towers are
    // mostly residential in Hong Kong, so only a minority of those go glass
    let set = type === 1 ? PAL.podium : type === 2 ? PAL.open : type === 3 ? PAL.temp
            : (h >= 160 || (h >= 100 && h2 < 0.3)) ? PAL.glass : h >= 40 ? PAL.high : h >= 12 ? PAL.mid : PAL.low;
    const c = set[Math.floor(hash * set.length) % set.length];
    const v = 0.92 + ((hash * 104729) % 1) * 0.16;             // ±8 % value variation per block
    out[0] = Math.min(255, c[0] * v * 255); out[1] = Math.min(255, c[1] * v * 255); out[2] = Math.min(255, c[2] * v * 255);
  }

  // ---- parse HKBL v1 -----------------------------------------------------------
  function parse(u8) {
    if (u8[0] !== 0x48 || u8[1] !== 0x4b || u8[2] !== 0x42 || u8[3] !== 0x4c) throw new Error('not an HKBL file');
    const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
    const count = dv.getUint32(8, true);
    const oE = dv.getFloat64(12, true), oN = dv.getFloat64(20, true), q = dv.getFloat32(28, true);
    let pos = 32;
    const rv = () => { let r = 0, s = 0, b; do { b = u8[pos++]; r += (b & 0x7f) * 2 ** s; s += 7; } while (b & 0x80); return r; };
    const rz = () => { const v = rv(); return (v % 2) ? -(v + 1) / 2 : v / 2; };
    // pass 1: sizes
    const p0 = pos; let rings = 0, verts = 0;
    for (let i = 0; i < count; i++) {
      pos++; const nr = rv();
      for (let k = 0; k < nr; k++) { const n = rv(); rings++; verts += n; for (let j = 0; j < 2 * n; j++) rv(); }
      rv(); rv();
    }
    pos = p0;
    const flags = new Uint8Array(count), base = new Float32Array(count), hgt = new Float32Array(count);
    const bRing = new Uint32Array(count + 1), ringOff = new Uint32Array(rings + 1);
    const vE = new Float32Array(verts), vN = new Float32Array(verts);
    const minE = new Float32Array(count), maxE = new Float32Array(count), minN = new Float32Array(count), maxN = new Float32Array(count);
    const area = new Float32Array(count), cE = new Float32Array(count), cN = new Float32Array(count);
    let ri = 0, vi = 0, pE = 0, pN = 0;
    for (let i = 0; i < count; i++) {
      flags[i] = u8[pos++];
      const nr = rv(); bRing[i] = ri;
      let e0 = 0, n0 = 0, mnE = 1e9, mxE = -1e9, mnN = 1e9, mxN = -1e9, a = 0, sx = 0, sy = 0;
      for (let k = 0; k < nr; k++) {
        const n = rv(); ringOff[ri++] = vi;
        let ce = k === 0 ? pE : e0, cn = k === 0 ? pN : n0;
        const start = vi;
        for (let j = 0; j < n; j++) {
          ce += rz(); cn += rz();
          const e = ce * q, nn = cn * q;
          vE[vi] = e; vN[vi] = nn; vi++;
          if (k === 0) { if (e < mnE) mnE = e; if (e > mxE) mxE = e; if (nn < mnN) mnN = nn; if (nn > mxN) mxN = nn; sx += e; sy += nn; }
        }
        if (k === 0) {
          e0 = ce - 0; n0 = cn - 0;   // placeholder, fixed below
          // first vertex of ring 0 (quanta) — hole rings delta from it
          e0 = Math.round(vE[start] / q); n0 = Math.round(vN[start] / q);
          for (let j = start, jn = vi - 1; j < vi; jn = j++) a += vE[jn] * vN[j] - vE[j] * vN[jn];   // shoelace (> 0: CCW)
          area[i] = Math.abs(a) / 2; cE[i] = sx / n; cN[i] = sy / n;
        }
      }
      pE = e0; pN = n0;
      base[i] = rz() / 10; hgt[i] = Math.max(0.5, rv() / 10);
      minE[i] = mnE; maxE[i] = mxE; minN[i] = mnN; maxN[i] = mxN;
    }
    bRing[count] = ri; ringOff[ri] = vi;
    return { count, oE, oN, flags, base, hgt, bRing, ringOff, vE, vN, minE, maxE, minN, maxN, area, cE, cN };
  }

  // ---- indices: collision hash, chunk lists, stacking, tiers ---------------------
  function index() {
    const { count, minE, maxE, minN, maxN } = D;
    let gE0 = 1e9, gE1 = -1e9, gN0 = 1e9, gN1 = -1e9;
    for (let i = 0; i < count; i++) { if (minE[i] < gE0) gE0 = minE[i]; if (maxE[i] > gE1) gE1 = maxE[i]; if (minN[i] < gN0) gN0 = minN[i]; if (maxN[i] > gN1) gN1 = maxN[i]; }
    D.ext = { E0: gE0, E1: gE1, N0: gN0, N1: gN1 };
    // CSR spatial hash over 100 m cells (a block is listed in every cell its bbox touches)
    const hw = Math.ceil((gE1 - gE0) / HASH_CELL) + 1, hh = Math.ceil((gN1 - gN0) / HASH_CELL) + 1;
    const cnt = new Uint32Array(hw * hh + 1);
    const cellsOf = (i, fn) => {
      const x0 = Math.floor((minE[i] - gE0) / HASH_CELL), x1 = Math.floor((maxE[i] - gE0) / HASH_CELL);
      const y0 = Math.floor((minN[i] - gN0) / HASH_CELL), y1 = Math.floor((maxN[i] - gN0) / HASH_CELL);
      for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) fn(y * hw + x);
    };
    for (let i = 0; i < count; i++) cellsOf(i, c => cnt[c + 1]++);
    for (let c = 0; c < hw * hh; c++) cnt[c + 1] += cnt[c];
    const fill = new Uint32Array(hw * hh), items = new Uint32Array(cnt[hw * hh]);
    for (let i = 0; i < count; i++) cellsOf(i, c => { items[cnt[c] + fill[c]++] = i; });
    D.hash = { hw, hh, off: cnt, items };
    // stacking: a block whose base sits on another block's top (within 1.5 m) is stacked —
    // it gets no skirt (its support is the other block). Cheap: one hash query per block.
    const stacked = new Uint8Array(count);
    for (let i = 0; i < count; i++) {
      if (D.flags[i] & 8) continue;
      const bi = D.base[i], x = D.cE[i], y = D.cN[i];
      for (const j of candidates(x, y)) {
        if (j === i || Math.abs(D.base[j] + D.hgt[j] - bi) > 1.5) continue;
        if (contains(j, x, y)) { stacked[i] = 1; break; }
      }
    }
    D.stacked = stacked;
    // tiers + chunk membership
    const tier = new Uint8Array(count);
    const far = new Map(), near = new Map();
    for (let i = 0; i < count; i++) {
      const big = !(D.flags[i] & 4) && (D.hgt[i] >= BIG_H || D.area[i] >= BIG_A);
      tier[i] = big ? 1 : 0;
      const sz = big ? FAR_CHUNK : NEAR_CHUNK, m = big ? far : near;
      const key = Math.floor((D.cN[i] - gN0) / sz) * 4096 + Math.floor((D.cE[i] - gE0) / sz);
      let l = m.get(key); if (!l) m.set(key, l = []); l.push(i);
    }
    D.tier = tier;
    D.far = [...far].map(([key, list]) => ({ key, list: Uint32Array.from(list), sz: FAR_CHUNK }));
    D.near = [...near].map(([key, list]) => ({ key, list: Uint32Array.from(list), sz: NEAR_CHUNK }));
    for (const c of [...D.far, ...D.near]) {   // chunk centre in E/N
      const cx = (c.key % 4096), cy = Math.floor(c.key / 4096);
      c.E = gE0 + (cx + 0.5) * c.sz; c.N = gN0 + (cy + 0.5) * c.sz; c.mesh = null; c.last = 0;
    }
  }
  function* candidates(E, N) {              // blocks whose bbox may contain (E, N)
    const h = D.hash, x = Math.floor((E - D.ext.E0) / HASH_CELL), y = Math.floor((N - D.ext.N0) / HASH_CELL);
    if (x < 0 || y < 0 || x >= h.hw || y >= h.hh) return;
    const c = y * h.hw + x;
    for (let k = h.off[c]; k < h.off[c + 1]; k++) {
      const i = h.items[k];
      if (E >= D.minE[i] && E <= D.maxE[i] && N >= D.minN[i] && N <= D.maxN[i]) yield i;
    }
  }
  function inRing(r, E, N) {                // even-odd point-in-ring
    const s = D.ringOff[r], e = D.ringOff[r + 1];
    let inside = false;
    for (let i = s, j = e - 1; i < e; j = i++) {
      const xi = D.vE[i], yi = D.vN[i], xj = D.vE[j], yj = D.vN[j];
      if ((yi > N) !== (yj > N) && E < (xj - xi) * (N - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }
  function contains(b, E, N) {              // footprint (outer ring minus holes) contains the point?
    const r0 = D.bRing[b], r1 = D.bRing[b + 1];
    if (!inRing(r0, E, N)) return false;
    for (let r = r0 + 1; r < r1; r++) if (inRing(r, E, N)) return false;
    return true;
  }

  // ---- per-source placement -------------------------------------------------------
  // The terrain grid changes with the source (and its triangulation with the density
  // slider), so everything that touches the DEM is recomputed from here.
  let G = null;            // { W, H, cell, g } of the current source
  let botCache, topCache;  // per block, real metres (NaN = not yet computed for this grid)
  const toX = (E) => ((E + D.oE - G.g.bE) / G.g.aE - G.W / 2) * G.cell;
  const toZ = (N) => ((N + D.oN - G.g.bN) / G.g.aN - G.H / 2) * G.cell;
  const toE = (x) => G.g.aE * (x / G.cell + G.W / 2) + G.g.bE - D.oE;
  const toN = (z) => G.g.aN * (z / G.cell + G.H / 2) + G.g.bN - D.oN;
  const terrainAt = (E, N) => {
    const col = (E + D.oE - G.g.bE) / G.g.aE, row = (N + D.oN - G.g.bN) / G.g.aN;
    return sampleEtri(col, row);
  };
  const onGrid = (E, N) => {
    const col = (E + D.oE - G.g.bE) / G.g.aE, row = (N + D.oN - G.g.bN) / G.g.aN;
    return col >= 0 && col <= G.W - 1 && row >= 0 && row <= G.H - 1;
  };
  // bottom/top of a block on the CURRENT terrain (real metres, absolute)
  function place(b) {
    if (!isNaN(botCache[b])) return;
    const r0 = D.bRing[b], s = D.ringOff[r0], e = D.ringOff[r0 + 1];
    let minT = 1e9;
    for (let i = s; i < e; i++) { const t = terrainAt(D.vE[i], D.vN[i]); if (t < minT) minT = t; }
    const tc = terrainAt(D.cE[b], D.cN[b]), h = D.hgt[b];
    let bot, top;
    if (D.flags[b] & 8) { bot = Math.min(minT, tc) - 0.5; top = tc + h; }               // no height data: sit it on the ground
    else if (D.stacked[b]) { bot = D.base[b]; top = bot + h; }                            // rests on another block
    else { bot = Math.min(D.base[b], minT - 1); top = D.base[b] + h; }                    // ground block: skirt into the DEM
    botCache[b] = bot; topCache[b] = top;
  }

  // ---- chunk geometry -------------------------------------------------------------------
  const _v2 = [];   // reused Vector2 pool for the roof triangulation
  function v2(n) { while (_v2.length < n) _v2.push(new THREE.Vector2()); return _v2; }
  function buildChunk(c) {
    const list = c.list;
    // size pass (upper bounds; walls exact, roofs ≤ 3·(verts + 2·holes))
    let nv = 0, nw = 0, nrf = 0, any = false;
    const use = new Uint8Array(list.length);
    for (let k = 0; k < list.length; k++) {
      const b = list[k];
      if (!onGrid(D.cE[b], D.cN[b])) continue;
      place(b);
      // fully buried under the coarse DEM (top under the lowest ground point) → nothing to see
      let minT = 1e9; const r0 = D.bRing[b], s0 = D.ringOff[r0], e0 = D.ringOff[r0 + 1];
      if (!(D.flags[b] & 8)) { for (let i = s0; i < e0; i++) { const t = terrainAt(D.vE[i], D.vN[i]); if (t < minT) minT = t; } if (topCache[b] <= minT + 0.2) continue; }
      use[k] = 1; any = true;
      for (let r = D.bRing[b]; r < D.bRing[b + 1]; r++) { const n = D.ringOff[r + 1] - D.ringOff[r]; nv += 2 * (n + 1); nw += 6 * n; nrf += 3 * n; }
      nrf += 6 * (D.bRing[b + 1] - D.bRing[b] - 1);
    }
    if (!any) return null;
    const pos = new Float32Array(nv * 3), uv = new Float32Array(nv * 2), col = new Uint8Array(nv * 3), useA = new Uint8Array(nv);
    const wall = nv > 65535 ? new Uint32Array(nw) : new Uint16Array(nw);
    const roof = nv > 65535 ? new Uint32Array(nrf) : new Uint16Array(nrf);
    let vi = 0, wi = 0, ri = 0;
    const rgb = [0, 0, 0];
    for (let k = 0; k < list.length; k++) {
      if (!use[k]) continue;
      const b = list[k], bot = botCache[b], top = topCache[b], hh = top - bot;
      tint(b, rgb);
      const bUse = (D.flags[b] >> 4) & 7;   // land-use class → the aUse vertex attribute (night-lights curve)
      useA.fill(bUse, vi, vi + 2 * (D.ringOff[D.bRing[b + 1]] - D.ringOff[D.bRing[b]] + (D.bRing[b + 1] - D.bRing[b])));
      const rings = [];   // { start (vertex index of the bottom of vertex 0), n }
      for (let r = D.bRing[b]; r < D.bRing[b + 1]; r++) {
        const s = D.ringOff[r], n = D.ringOff[r + 1] - s, start = vi;
        let u = 0, px = 0, pz = 0;
        for (let i = 0; i <= n; i++) {
          const j = s + (i % n), x = toX(D.vE[j]), z = toZ(D.vN[j]);
          if (i > 0) u += Math.hypot(x - px, z - pz);
          px = x; pz = z;
          pos[vi * 3] = x; pos[vi * 3 + 1] = bot; pos[vi * 3 + 2] = z; uv[vi * 2] = u; uv[vi * 2 + 1] = 0;
          col[vi * 3] = rgb[0]; col[vi * 3 + 1] = rgb[1]; col[vi * 3 + 2] = rgb[2]; vi++;
          pos[vi * 3] = x; pos[vi * 3 + 1] = top; pos[vi * 3 + 2] = z; uv[vi * 2] = u; uv[vi * 2 + 1] = hh;
          col[vi * 3] = rgb[0]; col[vi * 3 + 1] = rgb[1]; col[vi * 3 + 2] = rgb[2]; vi++;
        }
        // walls: ring vertices run counter-clockwise in E/N (holes clockwise) — with z = −N
        // that makes (b_i, b_i+1, t_i+1) face outward (see the derivation in HKS-114)
        for (let i = 0; i < n; i++) {
          const a = start + 2 * i, bb = a + 2;
          wall[wi++] = a; wall[wi++] = bb; wall[wi++] = bb + 1;
          wall[wi++] = a; wall[wi++] = bb + 1; wall[wi++] = a + 1;
        }
        rings.push({ start, n });
      }
      // roof: earcut over the top ring(s); orientation checked on the first triangle
      const outer = rings[0], pts = v2(outer.n), contour = [];
      for (let i = 0; i < outer.n; i++) { const p = pts[i]; p.set(pos[(outer.start + 2 * i) * 3], pos[(outer.start + 2 * i) * 3 + 2]); contour.push(p); }
      const holes = [], map = [];
      for (let i = 0; i < outer.n; i++) map.push(outer.start + 2 * i + 1);
      for (let h = 1; h < rings.length; h++) {
        const hr = rings[h], hp = [];
        for (let i = 0; i < hr.n; i++) { hp.push(new THREE.Vector2(pos[(hr.start + 2 * i) * 3], pos[(hr.start + 2 * i) * 3 + 2])); map.push(hr.start + 2 * i + 1); }
        holes.push(hp);
      }
      let tris;
      try { tris = THREE.ShapeUtils.triangulateShape(contour, holes); } catch (e) { tris = []; }
      if (tris.length) {
        const [a, bq, cq] = tris[0];
        const ax = contour[a] ? contour[a].x : pos[map[a] * 3], az = contour[a] ? contour[a].y : pos[map[a] * 3 + 2];
        const bx = pos[map[bq] * 3], bz = pos[map[bq] * 3 + 2], cx = pos[map[cq] * 3], cz = pos[map[cq] * 3 + 2];
        const ny = (bz - az) * (cx - ax) - (bx - ax) * (cz - az);   // y of (B−A)×(C−A) on the roof plane
        const flip = ny < 0;
        for (const t of tris) {
          if (ri + 3 > roof.length) break;
          roof[ri++] = map[t[0]]; roof[ri++] = map[flip ? t[2] : t[1]]; roof[ri++] = map[flip ? t[1] : t[2]];
        }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos.subarray(0, vi * 3), 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(uv.subarray(0, vi * 2), 2));
    geo.setAttribute('color', new THREE.BufferAttribute(col.subarray(0, vi * 3), 3, true));
    geo.setAttribute('aUse', new THREE.BufferAttribute(useA.subarray(0, vi), 1));
    const idx = wall.constructor === Uint32Array ? new Uint32Array(wi + ri) : new Uint16Array(wi + ri);
    idx.set(wall.subarray(0, wi), 0); idx.set(roof.subarray(0, ri), wi);
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.addGroup(0, wi, 0); geo.addGroup(wi, ri, 1);
    geo.computeBoundingSphere();
    const mesh = new THREE.Mesh(geo, materials());
    mesh.frustumCulled = true;
    return mesh;
  }
  function disposeChunk(c) { if (c.mesh) { group.remove(c.mesh); c.mesh.geometry.dispose(); c.mesh = null; } c.built = false; }

  // ---- lifecycle -------------------------------------------------------------------------
  let farQueue = [];
  function onSource() {   // new grid / triangulation: drop everything and rebuild lazily
    const gr = env.grid(); if (!gr || !gr.g) return;
    G = gr;
    if (!D) return;
    for (const c of D.far) disposeChunk(c);
    for (const c of D.near) disposeChunk(c);
    botCache = new Float32Array(D.count).fill(NaN); topCache = new Float32Array(D.count).fill(NaN);
    for (const c of [...D.far, ...D.near]) { c.x = toX(c.E); c.z = toZ(c.N); c.on = onGrid(c.E, c.N) || onGrid(c.E - c.sz / 2, c.N - c.sz / 2) || onGrid(c.E + c.sz / 2, c.N + c.sz / 2); }
    // the big tier streams in from the map centre outward
    farQueue = D.far.filter(c => c.on).sort((a, b) => (b.x * b.x + b.z * b.z) - (a.x * a.x + a.z * a.z));
  }
  async function load() {
    if (loading || ready || failed) return;
    loading = true;
    try {
      if (typeof DecompressionStream === 'undefined') throw new Error('DecompressionStream unsupported — buildings need a 2023+ browser');
      const [res, names] = await Promise.all([
        fetch(asset('data/hk-buildings.bin'), { cache: 'no-cache' }),
        fetch(asset('data/hk-buildings-names.json'), { cache: 'no-cache' }).then(r => r.ok ? r.json() : { towers: [] }).catch(() => ({ towers: [] })),
      ]);
      if (!res.ok) throw new Error(`HTTP ${res.status} data/hk-buildings.bin`);
      const buf = await new Response(res.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
      const t0 = performance.now();
      D = parse(new Uint8Array(buf));
      index();
      towers = pickTowers(names.towers || []);
      ready = true;
      console.info(`buildings: ${D.count} blocks, ${D.vE.length} verts, ${D.far.length} big + ${D.near.length} small chunks · parsed in ${Math.round(performance.now() - t0)} ms`);
      onSource();
      env.onReady && env.onReady();
    } catch (e) {
      failed = true; console.warn('buildings layer unavailable:', e);
    } finally { loading = false; }
  }
  // the label subset: tallest ~60 distinct names (one per estate — "Tower 3", "Block B", 第N座 collapse)
  function pickTowers(list) {
    const seen = new Set(), out = [];
    const stem = s => s.replace(/\s*\(.*?\)\s*/g, ' ').replace(/\s+(tower|block|phase|house|court)\s*[\w\d]+$/i, '').replace(/第?\s*[０-９0-9一二三四五六七八九十]+\s*座$/, '').trim().toLowerCase();
    for (const t of [...list].sort((a, b) => b.h - a.h)) {
      const k = stem(t.en); if (!t.en || seen.has(k)) continue;
      seen.add(k); out.push(t);
      if (out.length >= 60) break;
    }
    return out;
  }

  // ---- per-frame --------------------------------------------------------------------------
  const _sph = new THREE.Vector3();
  function update(fx, fz, now) {   // focus point in world-local metres (the walker / plane / orbit target)
    if (!ready || !G || !group.visible) return;
    const t0 = performance.now();
    // big tier: keep building until the frame budget is spent
    while (farQueue.length && performance.now() - t0 < 7) {
      const c = farQueue.pop();
      c.mesh = buildChunk(c); c.built = true;
      if (c.mesh) group.add(c.mesh);
    }
    // small tier: nearest wanted chunk first, one per frame; evict the far-away ones
    let best = null, bd = Infinity, live = 0;
    for (const c of D.near) {
      if (!c.on) continue;
      const dx = c.x - fx, dz = c.z - fz, d = Math.hypot(dx, dz) - c.sz * 0.71;
      if (c.built) {
        live++;
        if (d < NEAR_R) c.last = now;
        else if (d > EVICT_R) disposeChunk(c);
        continue;
      }
      if (d < NEAR_R && d < bd) { bd = d; best = c; }
    }
    if (best && performance.now() - t0 < 12) {
      if (live >= MAX_NEAR) {   // over budget: recycle the stalest chunk first
        let old = null; for (const c of D.near) if (c.built && (!old || c.last < old.last)) old = c;
        if (old) disposeChunk(old);
      }
      best.mesh = buildChunk(best); best.built = true; best.last = now;
      if (best.mesh) group.add(best.mesh);
    }
  }

  // ---- queries ----------------------------------------------------------------------------
  // highest block top at a world-local point (real metres, absolute), or -Infinity
  function roofAt(x, z) {
    if (!ready || !G || !group.visible) return -Infinity;
    const E = toE(x), N = toN(z);
    let top = -Infinity;
    for (const b of candidates(E, N)) {
      if (!contains(b, E, N)) continue;
      place(b);
      if (topCache[b] > top) top = topCache[b];
    }
    return top;
  }
  // like roofAt, but only counts blocks whose top is at or below `yMax` — what a walker can
  // STAND on. A tower beside you (top far overhead) is not a floor; the roof you dropped onto is.
  function standAt(x, z, yMax) {
    if (!ready || !G || !group.visible) return -Infinity;
    const E = toE(x), N = toN(z);
    let top = -Infinity;
    for (const b of candidates(E, N)) {
      if (!contains(b, E, N)) continue;
      place(b);
      if (topCache[b] <= yMax && topCache[b] > top) top = topCache[b];
    }
    return top;
  }
  // is a block solid at body height here? — an obstacle to walk around: its top is above
  // the step-up allowance and its bottom is below head height, OR starts within 8 m
  // overhead (a tower whose surveyed base is its podium roof still can't be walked
  // under where the podium polygon happens not to cover). Anything starting more than
  // 8 m up is a real overhang you can pass beneath.
  function solidAt(x, z, feet) {
    if (!ready || !G || !group.visible) return false;
    const E = toE(x), N = toN(z);
    for (const b of candidates(E, N)) {
      if (!contains(b, E, N)) continue;
      place(b);
      if (topCache[b] > feet + 0.6 && botCache[b] < feet + 8) return true;
    }
    return false;
  }
  // debug / inspection: every block under a world-local point, with its placement
  function blocksAt(x, z) {
    if (!ready || !G) return [];
    const E = toE(x), N = toN(z), out = [];
    for (const b of candidates(E, N)) {
      if (!contains(b, E, N)) continue;
      place(b);
      out.push({ i: b, type: D.flags[b] & 3, use: (D.flags[b] >> 4) & 7, est: !!(D.flags[b] & 4), stacked: !!D.stacked[b], base: D.base[b], h: D.hgt[b], bot: botCache[b], top: topCache[b] });
    }
    return out;
  }

  return {
    group, load, onSource, update, roofAt, standAt, solidAt, blocksAt,
    get ready() { return ready; }, get failed() { return failed; }, get count() { return D ? D.count : 0; },
    towers: () => towers,
    fxMats: () => [matWall, matRoof],
    setVisible(on) { group.visible = !!on; },
    setVE(ve) { group.scale.y = ve; },
    // night: dark 0 (day) → 1 (deep night) scales the window glow; hkHour (0–24, Hong Kong
    // clock of the sky sim) decides how much of the city is still up — the bedtime curve
    setNight(dark, hkHour) {
      const d = Math.max(0, Math.min(1, dark));
      dusk.value = d;                                        // the shader ramps each use class in at its own dusk point
      matWall.emissiveIntensity = d > 0.001 ? 1.45 : 0;
      if (hkHour != null && isFinite(hkHour)) {
        awakeA.value.set(awakeAt(hkHour, USE.RES), awakeAt(hkHour, USE.OFFICE), awakeAt(hkHour, USE.RETAIL), awakeAt(hkHour, USE.INDUSTRIAL));
        awakeB.value.set(awakeAt(hkHour, USE.INSTITUTION), awakeAt(hkHour, USE.VILLAGE), awakeAt(hkHour, USE.OTHER), 0);
      }
    },
    awakeAt, USE,
    setLook(matrix) {
      matrixLook = !!matrix;
      const m = materials();
      for (const c of [...(D?.far || []), ...(D?.near || [])]) if (c.mesh) c.mesh.material = m;
    },
  };
}
