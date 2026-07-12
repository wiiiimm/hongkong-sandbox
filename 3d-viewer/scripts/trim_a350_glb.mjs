// Build the fly-mode A350-1000 GLB (3d-viewer/data/models/plane-a350.glb) — HKS-110.
//
// Source: "A350 V3 with animation" by Newbie99999993 (Sketchfab, CC BY 4.0 —
// commercial OK; provenance ../data/models/README.md). 626 981 tris, 9 objects,
// one 4096² baseColor atlas carrying the AIRBUS house livery (titles + carbon
// tail art), and — the reason this model was picked — REAL landing gear:
// 6-wheel main bogies + twin nose wheels, modelled extended.
//
// This replaces the hakai315 A350 (CC BY, 1.97 M tris): its ~97 % decimation
// read visibly broken at chase distance, and it had no landing gear at all.
//
// What this script does:
//   1. GEAR SPLIT — connected components (union-find over indices) whose world
//      bbox falls entirely inside the main-gear box (x −2.6…3.6, y ≤13.3,
//      |z| ≤7 — wheels/struts/doors; the belly fairing spans x −8.9…11.7 so it
//      can't fit) or the nose-gear box (x 30.8…33.8, |z| ≤1.7) move to a
//      "CXGear" material, plus Object_14/17 wholesale (the outer bogie wheels).
//      loadPlaneModel() tags CXGear meshes and stepFlight hides them airborne.
//      The source's 20 baked animations (a gear-retract style timeline
//      re-targeted per node by Sketchfab) are dropped — the fleet rule is a
//      visibility toggle, and the GLB is reparented at load anyway.
//   2. LIVERY REPAINT — the atlas's AIRBUS branding is replaced with our own
//      Cathay-style treatment (colour/shape studied from Cathay's own A350
//      press photos — painted from scratch, no pixels copied): white hull
//      with procedural window rows, brushwing-jade #00655B tail fin carrying
//      the FULL brushwing mark in white (feathered fan of tapered sub-strokes
//      above a solid notched chevron), the same mark in white on each jade
//      winglet, the mark again in jade on the forward fuselage just aft of the
//      cockpit, jade "CATHAY PACIFIC" titles (stroke-built sans capitals) on
//      the upper forward fuselage, light-grey nacelles + belly fairing. Each
//      region is masked by rasterising that component's actual UV triangles
//      (the atlas islands interleave, so rectangle fills would bleed onto
//      neighbours). Marks/titles are painted in WORLD space so they survive
//      the diagonal UV islands. UV-sharing constraints: the two winglets (and
//      each winglet's two faces) share one UV island, so the winglet mark
//      shows on both faces of both winglets, keyed to the port winglet's
//      world coords; the fuselage sides are SEPARATE islands, so titles are
//      drawn reading nose→tail on each side independently.
//   3. BUDGET — weld + meshopt-simplify to ~60 k tris, with a second, harder
//      pass on the two 102 k-tri engine-fan disks (Material.014/.015); then
//      the shared recipe: dedup/prune/quantize (POSITION float32 — three r160
//      reads quantized attributes raw), metallic clamped (Sketchfab metal=1
//      renders near-black in our lighting), atlas ≤1024 px JPEG.
//
// Axes as authored: fuselage along X, nose +X, up +Y — loadPlaneModel() yaws
// +90° (cfg.rotY: Math.PI/2) to put the nose at −Z.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer sharp
//   node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, simplify, textureCompress, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
for (const anim of root.listAnimations()) {          // baked retract timeline — see header
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// ---- helpers ---------------------------------------------------------------
const xf = (wm, x, y, z) => [
  wm[0] * x + wm[4] * y + wm[8] * z + wm[12],
  wm[1] * x + wm[5] * y + wm[9] * z + wm[13],
  wm[2] * x + wm[6] * y + wm[10] * z + wm[14]];
// per-primitive connected components (union-find over the index array)
function components(prim) {
  const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
  const n = pos.getCount(), ia = idx.getArray();
  const parent = new Uint32Array(n).map((_, i) => i);
  const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
  for (let i = 0; i < ia.length; i += 3) { const a = find(ia[i]); parent[find(ia[i + 1])] = a; parent[find(ia[i + 2])] = a; }
  return { find, ia, n, pos };
}
function componentBoxes(prim, wm) {
  const { find, ia, n, pos } = components(prim);
  const box = new Map(); const el = [];
  for (let v = 0; v < n; v++) {
    pos.getElement(v, el);
    const [wx, wy, wz] = xf(wm, el[0], el[1], el[2]);
    const r = find(v);
    let b = box.get(r);
    if (!b) box.set(r, b = { minX: 1 / 0, maxX: -1 / 0, minY: 1 / 0, maxY: -1 / 0, minZ: 1 / 0, maxZ: -1 / 0 });
    b.minX = Math.min(b.minX, wx); b.maxX = Math.max(b.maxX, wx);
    b.minY = Math.min(b.minY, wy); b.maxY = Math.max(b.maxY, wy);
    b.minZ = Math.min(b.minZ, wz); b.maxZ = Math.max(b.maxZ, wz);
  }
  return { find, ia, box };
}

// ---- 1. gear split (world coords, ground plane y ≈ 9.7) ---------------------
const GEAR_BOXES = [
  { x: [-2.6, 3.6], y: [9.5, 13.3], z: [-7.0, 7.0] },     // main bogies + struts + doors
  { x: [30.8, 33.8], y: [9.5, 13.3], z: [-1.7, 1.7] },    // nose gear
];
const srgb = c => Math.pow((c / 255 + 0.055) / 1.055, 2.4);
const gearMat = doc.createMaterial('CXGear')
  .setBaseColorFactor([srgb(0x55), srgb(0x57), srgb(0x59), 1])
  .setRoughnessFactor(0.7).setMetallicFactor(0.1);
const WHEEL_NODES = new Set(['Object_14', 'Object_17']); // outer bogie wheels — gear wholesale
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const wm = node.getWorldMatrix();
  for (const prim of [...mesh.listPrimitives()]) {
    if (!prim.getIndices() || !prim.getAttribute('POSITION')) continue;
    if (WHEEL_NODES.has(node.getName())) { prim.setMaterial(gearMat); continue; }
    const { find, ia, box } = componentBoxes(prim, wm);
    const isGear = new Set();
    for (const [r, b] of box)
      if (GEAR_BOXES.some(G =>
        b.minX >= G.x[0] && b.maxX <= G.x[1] &&
        b.minY >= G.y[0] && b.maxY <= G.y[1] &&
        b.minZ >= G.z[0] && b.maxZ <= G.z[1])) isGear.add(r);
    if (!isGear.size) continue;
    const gearTris = [], bodyTris = [];
    for (let i = 0; i < ia.length; i += 3)
      (isGear.has(find(ia[i])) ? gearTris : bodyTris).push(ia[i], ia[i + 1], ia[i + 2]);
    const gp = prim.clone();
    gp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(gearTris)));
    gp.setMaterial(gearMat);
    mesh.addPrimitive(gp);
    prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(bodyTris)));
  }
}

// ---- 2. livery repaint on the shared atlas ----------------------------------
const tex = root.listTextures()[0];                       // single 4096² baseColor atlas
const srcPng = sharp(Buffer.from(tex.getImage()));
const meta = await srcPng.metadata();
const TW = meta.width, TH = meta.height;
const raw = await srcPng.raw().toBuffer({ resolveWithObject: true });
const CH = raw.info.channels;
const rgb = new Uint8ClampedArray(raw.data);
// region predicates on world-space component bboxes (measured on the source)
const REGIONS = {
  fin:      b => b.minX < -23 && b.minY > 16.5 && b.minZ > -2 && b.maxZ < 2,   // vertical fin + rudder (z-narrow; hstab spans ±16)
  winglet:  b => b.minY > 16 && b.maxY < 20.5 && Math.min(Math.abs(b.minZ), Math.abs(b.maxZ)) > 27,
  fuselage: b => (b.maxX - b.minX) > 60 && b.maxY < 20,
  nacelle:  b => b.minX > 7 && b.maxX < 12 && b.minY > 10.5 && Math.min(Math.abs(b.minZ), Math.abs(b.maxZ)) > 8,
  belly:    b => b.minX > -9.5 && b.maxX < 12 && b.minY > 11.9 && b.maxY < 13 && b.minZ > -3 && b.maxZ < 3,
};
const masks = {}; for (const k of Object.keys(REGIONS)) masks[k] = new Uint8Array(TW * TH);
// the atlas islands sit diagonally/interleaved, so the brushwing AND the hull
// windows are painted in WORLD space: while rasterising the fin/fuselage/belly
// masks, record each texel's world x/y
const finWX = new Float32Array(TW * TH), finWY = new Float32Array(TW * TH);
const finWZ = new Float32Array(TW * TH);                 // side sign for per-side title flip
const WORLD_REGIONS = new Set(['fin', 'fuselage', 'belly', 'winglet']);
function rasterUV(mask, uv, ia, keep, find, world) {
  for (let i = 0; i < ia.length; i += 3) {
    if (!keep(find(ia[i]))) continue;
    const P = [];
    for (let j = 0; j < 3; j++) { const e = []; uv.getElement(ia[i + j], e); P.push([e[0] * TW, e[1] * TH]); }
    const minx = Math.max(0, Math.floor(Math.min(P[0][0], P[1][0], P[2][0]) - 1)), maxx = Math.min(TW - 1, Math.ceil(Math.max(P[0][0], P[1][0], P[2][0]) + 1));
    const miny = Math.max(0, Math.floor(Math.min(P[0][1], P[1][1], P[2][1]) - 1)), maxy = Math.min(TH - 1, Math.ceil(Math.max(P[0][1], P[1][1], P[2][1]) + 1));
    const [A, B, C] = P, den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1]);
    if (!den) continue;
    const wpos = world && world(i);                       // [[x,y]×3] world coords of the tri's corners
    for (let y = miny; y <= maxy; y++) for (let x = minx; x <= maxx; x++) {
      const w1 = ((B[1] - C[1]) * (x - C[0]) + (C[0] - B[0]) * (y - C[1])) / den,
            w2 = ((C[1] - A[1]) * (x - C[0]) + (A[0] - C[0]) * (y - C[1])) / den, w3 = 1 - w1 - w2;
      if (w1 < -0.05 || w2 < -0.05 || w3 < -0.05) continue;   // slight dilation so filtering doesn't fetch old paint
      const p = y * TW + x;
      mask[p] = 1;
      if (wpos) {
        finWX[p] = w1 * wpos[0][0] + w2 * wpos[1][0] + w3 * wpos[2][0];
        finWY[p] = w1 * wpos[0][1] + w2 * wpos[1][1] + w3 * wpos[2][1];
        finWZ[p] = w1 * wpos[0][2] + w2 * wpos[1][2] + w3 * wpos[2][2];
      }
    }
  }
}
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const wm = node.getWorldMatrix();
  for (const prim of mesh.listPrimitives()) {
    const uv = prim.getAttribute('TEXCOORD_0');
    if (!uv || !prim.getIndices() || prim.getMaterial() === gearMat) continue;
    const { find, ia, box } = componentBoxes(prim, wm);
    const pos = prim.getAttribute('POSITION');
    const worldOf = i => [0, 1, 2].map(j => {
      const e = []; pos.getElement(ia[i + j], e);
      return xf(wm, e[0], e[1], e[2]);
    });
    for (const [k, test] of Object.entries(REGIONS)) {
      const roots = new Set();
      for (const [r, b] of box) if (test(b)) roots.add(r);
      if (!roots.size) continue;
      if (k === 'winglet') {
        // both winglets share one UV island but sit at slightly different world
        // heights — record paint coords from the PORT (z<0) winglet only so the
        // mark isn't smeared by disagreeing coordinates.
        const port = new Set(), stbd = new Set();
        for (const [r, b] of box) if (roots.has(r)) (b.minZ < 0 ? port : stbd).add(r);
        if (port.size) rasterUV(masks[k], uv, ia, r => port.has(r), find, worldOf);
        if (stbd.size) rasterUV(masks[k], uv, ia, r => stbd.has(r), find, null);
      } else {
        rasterUV(masks[k], uv, ia, r => roots.has(r), find, WORLD_REGIONS.has(k) ? worldOf : null);
      }
    }
  }
}
const JADE = [0x00, 0x65, 0x5b], WHITE = [0xf4, 0xf6, 0xf7], GREY = [0xdd, 0xe0, 0xe3];
const put = (i, c) => { rgb[i] = c[0]; rgb[i + 1] = c[1]; rgb[i + 2] = c[2]; };

// ---- the full Cathay-style brushwing mark, drawn from scratch ---------------
// Defined in a unit box: +mx = forward (reading direction), +my = up. Two
// elements, per the tail reference photo: a SOLID CHEVRON (bold swept
// triangle, sharp tip forward, a notch cut into its lower trailing edge) and,
// above it, a FEATHERED fan of thin tapered sub-strokes sweeping up and aft
// from just above the tip.
const qbez = (P0, P1, P2, t) => [
  (1 - t) * (1 - t) * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0],
  (1 - t) * (1 - t) * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1]];
const CHEV = [];                                           // polygon, sampled bezier edges
{
  const edge = (P0, P1, P2, n = 16) => { for (let i = 0; i < n; i++) CHEV.push(qbez(P0, P1, P2, i / n)); };
  edge([0.97, 0.44], [0.55, 0.56], [0.20, 0.60]);          // upper edge, tip → aft, slightly concave
  edge([0.20, 0.60], [0.13, 0.42], [0.10, 0.16]);          // aft edge down
  edge([0.10, 0.16], [0.26, 0.22], [0.36, 0.30]);          // lower-aft up into the notch
  edge([0.36, 0.30], [0.44, 0.20], [0.55, 0.12]);          // notch back down
  edge([0.55, 0.12], [0.78, 0.26], [0.97, 0.44]);          // lower edge out to the tip
}
const inChevron = (x, y) => {
  let inside = false;
  for (let i = 0, j = CHEV.length - 1; i < CHEV.length; j = i++) {
    const [xi, yi] = CHEV[i], [xj, yj] = CHEV[j];
    if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};
const FEATHERS = [];                                       // sampled [x, y, halfWidth]
{
  const N = 9;
  for (let k = 0; k < N; k++) {
    const f = k / (N - 1);
    const O = [0.90 - 0.06 * f, 0.48 + 0.02 * f];          // origins near/above the tip
    const E = [0.12 + 0.30 * f, 0.66 + 0.34 * f];          // fan of endpoints, aft-low → aft-high
    const M = [(O[0] + E[0]) / 2, (O[1] + E[1]) / 2 + 0.05 + 0.04 * f];  // gentle upward bow
    for (let t = 0.04; t <= 1; t += 0.02) {
      const [x, y] = qbez(O, M, E, t);
      FEATHERS.push([x, y, 0.013 * (1 - t) + 0.002, k]);   // taper root → tip; k = feather id
    }
  }
}
const onMark = (mx, my, fw = 1) => {                       // fw: feather-width boost for coarse UV islands
  if (mx < -0.02 || mx > 1.02 || my < 0.06 || my > 1.05) return false;
  if (my < 0.62 && inChevron(mx, my)) return true;
  if (my > 0.4) for (const [fx, fy, w, k] of FEATHERS) {
    if (fw > 1 && k % 2 === 0) continue;                   // coarse mode: every other feather, so they stay distinct
    const dx = mx - fx, dy = my - fy, r = fw > 1 ? Math.max(w * fw, 0.045) : w;
    if (dx * dx + dy * dy < r * r) return true;
  }
  return false;
};

// ---- "CATHAY PACIFIC" — stroke-built sans capitals ---------------------------
// Segment skeletons in a unit glyph cell (x 0…1 = width, y 0…1 = cap height),
// rendered by distance-to-segment. Kept to simple strokes so the letters stay
// legible at the final 1024-px atlas (~11 px cap height at chase distance).
const GLYPHS = (() => {
  const arc = (cx, cy, rx, ry, a0, a1, n = 10) => {
    const s = [];
    for (let i = 0; i < n; i++) {
      const t0 = a0 + (a1 - a0) * i / n, t1 = a0 + (a1 - a0) * (i + 1) / n;
      s.push([cx + rx * Math.cos(t0), cy + ry * Math.sin(t0), cx + rx * Math.cos(t1), cy + ry * Math.sin(t1)]);
    }
    return s;
  };
  const D = Math.PI / 180;
  return {
    C: arc(0.52, 0.5, 0.48, 0.5, 50 * D, 310 * D),
    A: [[0.02, 0, 0.5, 1], [0.5, 1, 0.98, 0], [0.22, 0.33, 0.78, 0.33]],
    T: [[0, 1, 1, 1], [0.5, 1, 0.5, 0]],
    H: [[0.04, 0, 0.04, 1], [0.96, 0, 0.96, 1], [0.04, 0.5, 0.96, 0.5]],
    Y: [[0.02, 1, 0.5, 0.48], [0.98, 1, 0.5, 0.48], [0.5, 0.48, 0.5, 0]],
    P: [[0.06, 0, 0.06, 1], [0.06, 1, 0.58, 1], ...arc(0.58, 0.76, 0.36, 0.24, -90 * D, 90 * D), [0.58, 0.52, 0.06, 0.52]],
    I: [[0.5, 0, 0.5, 1]],
    F: [[0.06, 0, 0.06, 1], [0.06, 1, 0.98, 1], [0.06, 0.5, 0.8, 0.5]],
  };
})();
const TITLE = 'CATHAY PACIFIC';
const CAP = 0.85, ADV = 0.74, GLYPH_W = 0.6 * CAP, STROKE = 0.115;  // metres / cell units
const TITLE_LEN = (TITLE.length - 1) * ADV + GLYPH_W;
const onTitle = (sx, sy) => {                              // sx along reading dir from block start, sy up from baseline (metres)
  if (sy < -0.15 || sy > CAP + 0.15 || sx < -0.1 || sx > TITLE_LEN + 0.1) return false;
  const k = Math.floor(sx / ADV);
  for (const ki of [k - 1, k]) {                           // glyph cells can spill past ADV slightly
    if (ki < 0 || ki >= TITLE.length) continue;
    const segs = GLYPHS[TITLE[ki]];
    if (!segs) continue;
    const gx = (sx - ki * ADV) / GLYPH_W, gy = sy / CAP;
    for (const [x1, y1, x2, y2] of segs) {
      const dx = x2 - x1, dy = y2 - y1, L2 = dx * dx + dy * dy || 1;
      let t = ((gx - x1) * dx + (gy - y1) * dy) / L2;
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      const ex = gx - (x1 + t * dx), ey = gy - (y1 + t * dy);
      if (ex * ex + ey * ey < STROKE * STROKE) return true;
    }
  }
  return false;
};

// ---- placements (world metres; fin spans x −35.8…−23.9, y 17.6…27.2) --------
// Fin: mark box ~middle 55 % of fin height, sheared aft with the sweep
// (leading edge slope ≈ −0.7 dx/dy, measured on the source).
const finMark = (x, y) => {
  const my = (y - 20.1) / 5.1;
  const mx = ((x + 35.2) + 0.7 * (y - 20.1)) / 6.8;
  return onMark(mx, my);
};
// Winglet: same mark, rotated to run up the sharklet with the sweep. Local
// axis A points forward-up along the blade, B is the in-plane "up" of the
// mark. Keyed to the PORT winglet's coords (shared UV island — see header).
const WGA = [0.545, 0.838], WGB = [-0.838, 0.545];         // unit vectors in world x/y
const wingletMark = (x, y) => {
  const dx = x - (-11.6), dy = y - 17.6;                   // port winglet centre-ish
  const mx = (dx * WGA[0] + dy * WGA[1]) / 1.55 + 0.5;
  const my = (dx * WGB[0] + dy * WGB[1]) / 1.35 + 0.38;
  return onMark(mx, my, 6);                                // fat feathers: island is only ~55×110 texels at 1024
};
// Nose: jade mark just aft of the cockpit, ahead of the first door. Keyed to
// world x on both sides, so the tip points forward on each (livery-mirrored).
const noseMark = (x, y) => onMark((x - 28.6) / 3.0, (y - 13.9) / 2.6);
// Titles: upper forward fuselage, above the window line. The two fuselage
// sides are separate UV islands, so each is drawn reading nose→tail: the
// glyph x-axis flips with the recorded world-z sign.
const TITLE_XA = 15.6, TITLE_XB = TITLE_XA + TITLE_LEN, TITLE_Y0 = 16.35;
const titleAt = (x, y, z) =>
  onTitle(z < 0 ? TITLE_XB - x : x - TITLE_XA, y - TITLE_Y0);

for (let p = 0; p < TW * TH; p++) {
  const i = p * CH, r = rgb[i], g = rgb[i + 1], b = rgb[i + 2];
  const lum = (r + g + b) / 765;
  if (masks.fin[p]) put(i, finMark(finWX[p], finWY[p]) ? WHITE : JADE);
  else if (masks.winglet[p]) put(i, wingletMark(finWX[p], finWY[p]) ? WHITE : JADE);
  else if (masks.nacelle[p]) put(i, lum < 0.25 ? [0x3a, 0x3f, 0x44] : GREY);  // light-grey cowls, keep dark intake lips
}
// hull de-branding: the source atlas carries AIRBUS house-livery titles,
// giant "1000"s and pale watermark art scattered through the fuselage/belly
// islands (its windows are grey like the titles — no colour signal to key
// on), so the hull is painted CLEAN WHITE and the cabin window rows are
// redrawn procedurally in world space: one dark rounded dot every 0.8 m at
// the real window line (y ≈ 15.55, the cabin mid-line), stopping short of
// the nose (the cockpit glass is separate geometry) and the tail taper.
{
  const WIN = [0x3c, 0x42, 0x4a];
  for (let p = 0; p < TW * TH; p++) {
    if (!masks.fuselage[p] && !masks.belly[p]) continue;
    const i = p * CH;
    if (masks.fuselage[p]) {
      const x = finWX[p], y = finWY[p], z = finWZ[p];
      if (noseMark(x, y) || titleAt(x, y, z)) { put(i, JADE); continue; }
      const inRow = x > -26 && x < 27 && Math.abs(y - 15.55) < 0.17 && (((x % 0.8) + 0.8) % 0.8) < 0.42;
      put(i, inRow ? WIN : WHITE);
    } else put(i, WHITE);
  }
}
tex.setImage(await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toBuffer())
   .setMimeType('image/png');
if (process.env.A350_DEBUG_ATLAS)                         // full painted atlas, for livery inspection
  await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toFile(process.env.A350_DEBUG_ATLAS);

// ---- 3. budget --------------------------------------------------------------
const ratio = Number(ratioArg) || 0.18;
await doc.transform(weld(), simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.003 }));
// second, harder pass on the dense round bits the global error bound protects:
// the two 102 k-tri engine-fan disks (sub-metre blade detail invisible behind
// the intake) and the 180 k+ tris of bogie wheels now under CXGear
await MeshoptSimplifier.ready;
const CRUSH = { 'Material.014': 0.1, 'Material.015': 0.1, CXGear: 0.22 };
for (const mesh of root.listMeshes())
  for (const prim of mesh.listPrimitives()) {
    const target = CRUSH[prim.getMaterial()?.getName()];
    if (!target) continue;
    const idx = prim.getIndices(), pos = prim.getAttribute('POSITION');
    if (!idx || !pos) continue;
    const ia = idx.getArray() instanceof Uint32Array ? idx.getArray() : new Uint32Array(idx.getArray());
    const [out] = MeshoptSimplifier.simplify(
      ia, pos.getArray(), 3, Math.floor(ia.length * target / 3) * 3, 0.01, ['LockBorder']);
    idx.setArray(out.slice());
  }
// material sanity: Sketchfab roughness-0 glass-smooth everything reads wrong
for (const m of root.listMaterials()) {
  if (m.getMetallicFactor() > 0.2) m.setMetallicFactor(0.15);
  if (m.getRoughnessFactor() < 0.4) m.setRoughnessFactor(0.5);
}
await doc.transform(
  dedup(), prune(),
  quantize({ pattern: /^(?!POSITION).*$/, quantizeNormal: 8 }),
  textureCompress({ encoder: sharp, resize: [1024, 1024], targetFormat: 'jpeg', quality: 80 }),
);

let tris = 0, gear = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const t = (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3;
    tris += t;
    if (p.getMaterial()?.getName() === 'CXGear') gear += t;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris (', Math.round(gear), 'gear )');
