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
//   2. LIVERY REPAINT — the atlas's AIRBUS branding is replaced with the
//      project-supplied Cathay artwork in scripts/assets/: white hull with a
//      subtle pale-jade lower band and procedural window rows; jade #005D63
//      fin with the complete brushwing SVG in white; the white mark on each
//      winglet's inward face; the mark again in jade just aft of the cockpit;
//      and the supplied serif CATHAY PACIFIC wordmark on the upper forward
//      fuselage. Each
//      region is masked by rasterising that component's actual UV triangles
//      (the atlas islands interleave, so rectangle fills would bleed onto
//      neighbours). Marks/titles are painted in WORLD space so they survive
//      the diagonal UV islands. Because the winglet faces share a UV island,
//      inward-facing triangles are split to a marked copy of the atlas while
//      outward faces remain plain jade. The fuselage sides are separate UV
//      islands, so the wordmark reads correctly from either side.
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
import { fileURLToPath } from 'node:url';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
const assetPath = name => fileURLToPath(new URL(`./assets/${name}`, import.meta.url));
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

// Source-backed Cathay artwork supplied for HKS-110. The SVG is the complete
// brushwing mark. The JPEG contains the mark plus the official wordmark; crop
// coordinates below deliberately retain only the lettering (the mark is
// sourced from the clean SVG instead). Both are sampled as masks and coloured
// here, so JPEG white/background pixels never enter the aircraft atlas.
const MARK_W = 512;
const markRaw = await sharp(assetPath('cathay-brushwing.svg'))
  .resize({ width: MARK_W }).ensureAlpha().raw()
  .toBuffer({ resolveWithObject: true });
const wordRaw = await sharp(assetPath('cathay-wordmark.jpg'))
  .extract({ left: 107, top: 80, width: 289, height: 27 })
  .raw().toBuffer({ resolveWithObject: true });
const clamp01 = n => Math.max(0, Math.min(1, n));
const sampleMark = (u, v) => {
  if (u < 0 || u > 1 || v < 0 || v > 1) return 0;
  const x = Math.min(markRaw.info.width - 1, Math.round(u * (markRaw.info.width - 1)));
  const y = Math.min(markRaw.info.height - 1, Math.round((1 - v) * (markRaw.info.height - 1)));
  return markRaw.data[(y * markRaw.info.width + x) * markRaw.info.channels + 3] / 255;
};
const sampleWordmark = (u, v) => {
  if (u < 0 || u > 1 || v < 0 || v > 1) return 0;
  const x = Math.min(wordRaw.info.width - 1, Math.round(u * (wordRaw.info.width - 1)));
  const y = Math.min(wordRaw.info.height - 1, Math.round((1 - v) * (wordRaw.info.height - 1)));
  const i = (y * wordRaw.info.width + x) * wordRaw.info.channels;
  const r = wordRaw.data[i], g = wordRaw.data[i + 1], b = wordRaw.data[i + 2];
  // Teal chroma is a cleaner antialiased mask than a raw luminance threshold:
  // it rejects the white JPEG field and its compression noise.
  return clamp01((Math.min(g, b) - r - 3) / 48);
};
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
const insideWingletSplits = [];                          // marked inward faces vs plain-jade outward faces
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

        // This model reuses the same UV island on every winglet face. Split
        // inward-facing triangles into a second primitive/material so only the
        // inside curve receives the white mark. A face points inward when its
        // world normal points back towards z=0 (the fuselage centreline).
        const inside = [], rest = [];
        for (let i = 0; i < ia.length; i += 3) {
          let isInside = false;
          if (roots.has(find(ia[i]))) {
            const [a, b, c] = worldOf(i);
            const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
            const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
            const nx = ab[1] * ac[2] - ab[2] * ac[1];
            const ny = ab[2] * ac[0] - ab[0] * ac[2];
            const nz = ab[0] * ac[1] - ab[1] * ac[0];
            const nl = Math.hypot(nx, ny, nz) || 1;
            const cz = (a[2] + b[2] + c[2]) / 3;
            isInside = Math.abs(nz) / nl > 0.35 && cz * nz < 0;
          }
          (isInside ? inside : rest).push(ia[i], ia[i + 1], ia[i + 2]);
        }
        if (inside.length) insideWingletSplits.push({ mesh, prim, inside, rest });
      } else {
        rasterUV(masks[k], uv, ia, r => roots.has(r), find, WORLD_REGIONS.has(k) ? worldOf : null);
      }
    }
  }
}
const JADE = [0x00, 0x5d, 0x63], WHITE = [0xf4, 0xf6, 0xf7],
      GREY = [0xdd, 0xe0, 0xe3], PALE_JADE = [0xb8, 0xd4, 0xd2];
const put = (buf, i, c) => { buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]; };
const blend = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * clamp01(t)));

// ---- source-art placements (world metres) ----------------------------------
// Fin spans x −35.8…−23.9, y 17.6…27.2. Let the swept fin silhouette crop
// the rectangular mark mapping naturally: the point faces +X (the nose),
// while the fine strokes rise aft towards the top of the tail.
const finMark = (x, y) => {
  return sampleMark((x + 35.3) / 9.2, (y - 18.9) / 7.2);
};
// Winglet: same SVG mark, rotated along the sharklet. Only inward-facing
// triangles receive the marked atlas; outward faces remain solid jade.
const WGA = [0.545, 0.838], WGB = [-0.838, 0.545];         // unit vectors in world x/y
const wingletMark = (x, y) => {
  const dx = x - (-11.6), dy = y - 17.6;                   // port winglet centre-ish
  const mx = (dx * WGA[0] + dy * WGA[1]) / 1.55 + 0.5;
  const my = (dx * WGB[0] + dy * WGB[1]) / 1.35 + 0.38;
  return sampleMark(mx, my);
};
// Nose: green mark immediately aft of the black cockpit mask. Source axes use
// +X as forward, so the SVG's pointed end naturally faces the nose.
const noseMark = (x, y) => sampleMark((x - 28.25) / 3.5, (y - 13.75) / 2.75);
// Official wordmark: the two fuselage sides use separate UV islands. Flip the
// world-X sampling by side so the lettering reads correctly from either view.
const TITLE_XA = 14.2, TITLE_XB = 28.7, TITLE_Y0 = 16.05, TITLE_Y1 = 17.40;
const titleAt = (x, y, z) =>
  sampleWordmark(
    z < 0 ? (TITLE_XB - x) / (TITLE_XB - TITLE_XA) : (x - TITLE_XA) / (TITLE_XB - TITLE_XA),
    (y - TITLE_Y0) / (TITLE_Y1 - TITLE_Y0));

for (let p = 0; p < TW * TH; p++) {
  const i = p * CH, r = rgb[i], g = rgb[i + 1], b = rgb[i + 2];
  const lum = (r + g + b) / 765;
  if (masks.fin[p]) put(rgb, i, blend(JADE, WHITE, finMark(finWX[p], finWY[p])));
  else if (masks.winglet[p]) put(rgb, i, JADE);            // marked copy is built below for inward faces only
  else if (masks.nacelle[p]) put(rgb, i, lum < 0.25 ? [0x3a, 0x3f, 0x44] : GREY);  // light-grey cowls, keep dark intake lips
}
// hull de-branding: the source atlas carries AIRBUS house-livery titles,
// giant "1000"s and pale watermark art scattered through the fuselage/belly
// islands (its windows are grey like the titles — no colour signal to key
// on), so the hull is repainted and the cabin window rows are redrawn
// procedurally in world space. The lower third fades into Cathay's subtle
// pale-jade belly band instead of becoming a flat white/grey cylinder.
{
  const WIN = [0x3c, 0x42, 0x4a];
  for (let p = 0; p < TW * TH; p++) {
    if (!masks.fuselage[p] && !masks.belly[p]) continue;
    const i = p * CH;
    if (masks.fuselage[p]) {
      const x = finWX[p], y = finWY[p], z = finWZ[p];
      const mark = Math.max(noseMark(x, y), titleAt(x, y, z));
      if (mark > 0) { put(rgb, i, blend(WHITE, JADE, mark)); continue; }
      const inRow = x > -26 && x < 27 && Math.abs(y - 15.55) < 0.17 && (((x % 0.8) + 0.8) % 0.8) < 0.42;
      const lower = clamp01((15.0 - y) / 2.4);
      put(rgb, i, inRow ? WIN : blend(WHITE, PALE_JADE, 0.72 * lower));
    } else put(rgb, i, blend(WHITE, PALE_JADE, 0.58));
  }
}

// A second atlas differs only on the winglet island. It is assigned solely to
// the inward-facing split above; outward faces use the solid-jade base atlas.
const wingRgb = new Uint8ClampedArray(rgb);
for (let p = 0; p < TW * TH; p++) {
  if (!masks.winglet[p]) continue;
  const i = p * CH;
  put(wingRgb, i, blend(JADE, WHITE, wingletMark(finWX[p], finWY[p])));
}
const basePng = await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toBuffer();
const wingPng = await sharp(Buffer.from(wingRgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toBuffer();
tex.setImage(basePng)
   .setMimeType('image/png');
const wingTex = doc.createTexture('CX A350 inward-winglet atlas').setImage(wingPng).setMimeType('image/png');
const wingMats = new Map();
for (const { mesh, prim, inside, rest } of insideWingletSplits) {
  const sourceMat = prim.getMaterial();
  let markedMat = wingMats.get(sourceMat);
  if (!markedMat) {
    markedMat = sourceMat.clone().setName(`${sourceMat.getName() || 'A350'} CX inward winglet`);
    markedMat.setBaseColorTexture(wingTex);
    wingMats.set(sourceMat, markedMat);
  }
  const marked = prim.clone();
  marked.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(inside)));
  marked.setMaterial(markedMat);
  mesh.addPrimitive(marked);
  prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(rest)));
}
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
