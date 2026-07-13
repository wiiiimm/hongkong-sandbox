// Build the fly-mode 777-300ER GLB (3d-viewer/data/models/plane-777.glb) — HKS-110.
//
// Source: "boeing 777-300ER Saudi Arabian Airlines (Saudia)" by Omatar
// (Sketchfab, CC BY 4.0 — commercial OK; provenance ../data/models/README.md).
// 507 667 tris, 241 meshes, one 2048² "Stickers" baseColor atlas carrying the
// Saudia branding (two fuselage side strips + the green fin plate); everything
// else is flat-coloured materials. Crucially it ships REAL extended landing
// gear: two 6-wheel main bogies (3 axles × 2 wheel columns per side, plus
// struts and open bay doors) and a twin-wheel nose gear, modelled extended.
//
// This replaces the 777_Boeing hull (CC BY, 120 k tris, textureless — vertex
// colours + tangent decals): user preference for the higher-fidelity airframe.
//
// What this script does (the A350 recipe, ported to this hull):
//   1. GEAR SPLIT — connected components (union-find over indices) whose world
//      bbox falls entirely inside the nose-gear box (x −2.35…−2.19, |z−0.06|
//      small) or either main-gear box (x −0.06…0.35, z −0.47…−0.27 port /
//      0.39…0.60 starboard; the belly fairing spans the full fuselage so it
//      can't fit) move to a "CXGear" material. loadPlaneModel() tags CXGear
//      meshes and stepFlight hides them airborne (HKS-110 fleet rule).
//      Axes as authored: fuselage along X, NOSE at −X, up +Y, fuselage
//      centreline z ≈ +0.055; wheels reach y −0.03, belly starts y 0.19, so
//      the gear-down stance survives the loader's waterline fit.
//   2. LIVERY REPAINT — the Stickers atlas's Saudia cheatlines/titles/fin are
//      replaced with the project-supplied Cathay artwork in scripts/assets/,
//      painted in WORLD space via per-texel world coords recorded while
//      rasterising each region's actual UV triangles (the fuselage side strips
//      and fin are separate islands; rectangle fills would still catch the
//      wrong rows): white hull with the subtle pale-jade lower band, jade
//      #00655B fin with the complete white brushwing SVG, the brushwing again
//      in jade just aft of the cockpit, and the supplied serif CATHAY PACIFIC
//      wordmark on both upper forward fuselage sides (flipped per side so it
//      reads nose-first from either view). Cabin windows and cockpit glass are
//      real dark GEOMETRY on this model, so the wipe never eats them; the
//      777-300ER has raked wingtips (no winglets), so there is no winglet
//      mark. The two thin full-length RED strips (Material.103) that ride the
//      window line are recoloured to hull white — no stray red on a CX hull —
//      and the engines are already light untextured cowls.
//   3. BUDGET — weld + meshopt-simplify ~507 k → ≤60 k tris, with a harder
//      second pass on the CXGear wheel stacks; then the shared recipe:
//      dedup/prune/quantize (POSITION stays float32 — three r160 reads
//      quantized attributes raw), metallic/roughness clamps, atlas ≤1024 px
//      JPEG.
//
// Nose faces −X → loadPlaneModel() yaws −90° (cfg.rotY: -Math.PI/2).
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer sharp
//   node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, simplify, textureCompress, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
const assetPath = name => fileURLToPath(new URL(`./assets/${name}`, import.meta.url));
for (const anim of root.listAnimations()) {               // none authored, but keep the recipe defensive
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// ---- helpers (shared with trim_a350_glb.mjs) --------------------------------
const xf = (wm, x, y, z) => [
  wm[0] * x + wm[4] * y + wm[8] * z + wm[12],
  wm[1] * x + wm[5] * y + wm[9] * z + wm[13],
  wm[2] * x + wm[6] * y + wm[10] * z + wm[14]];
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

// ---- 1. gear split (world coords; wheels reach y −0.03, belly starts 0.19) --
const GEAR_BOXES = [
  { x: [-0.06, 0.35], y: [-0.04, 0.32], z: [-0.50, -0.25] },  // port main bogie + strut + bay doors
  { x: [-0.06, 0.35], y: [-0.04, 0.32], z: [0.36, 0.62] },    // starboard main bogie
  { x: [-2.36, -2.18], y: [-0.04, 0.31], z: [-0.01, 0.13] },  // nose gear + doors
];
const srgb = c => Math.pow((c / 255 + 0.055) / 1.055, 2.4);
const gearMat = doc.createMaterial('CXGear')
  .setBaseColorFactor([srgb(0x55), srgb(0x57), srgb(0x59), 1])
  .setRoughnessFactor(0.7).setMetallicFactor(0.1);
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const wm = node.getWorldMatrix();
  for (const prim of [...mesh.listPrimitives()]) {
    if (!prim.getIndices() || !prim.getAttribute('POSITION')) continue;
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
    if (!bodyTris.length) { prim.setMaterial(gearMat); continue; }   // whole prim is gear
    const gp = prim.clone();
    gp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(gearTris)));
    gp.setMaterial(gearMat);
    mesh.addPrimitive(gp);
    prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(bodyTris)));
  }
}

// ---- 2. livery repaint on the Stickers atlas ---------------------------------
const tex = root.listTextures().find(t => /sticker/i.test(t.getName() || '') || /sticker/i.test(t.getURI() || '')) || root.listTextures()[0];
const srcPng = sharp(Buffer.from(tex.getImage()));
const meta = await srcPng.metadata();
const TW = meta.width, TH = meta.height;
const raw = await srcPng.raw().toBuffer({ resolveWithObject: true });
const CH = raw.info.channels;
const rgb = new Uint8ClampedArray(raw.data);

// Source-backed Cathay artwork supplied for HKS-110 (see assets/README.md).
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
  return clamp01((Math.min(g, b) - r - 3) / 48);        // teal chroma beats a luminance threshold
};
// region predicates on world-space component bboxes (measured on the source):
// the fin is the flat plate rising to y 1.42 behind x 1.9; EVERY other
// Stickers component (hull strips, doors, exit markings, the 75-years logo
// pieces) gets the white-hull treatment — a narrower span test left Saudia
// door/exit dashes behind.
const REGIONS = {
  fin:      b => b.minX > 1.9 && b.maxY > 0.75,
  fuselage: b => !(b.minX > 1.9 && b.maxY > 0.75),
};
const masks = {}; for (const k of Object.keys(REGIONS)) masks[k] = new Uint8Array(TW * TH);
const finWX = new Float32Array(TW * TH), finWY = new Float32Array(TW * TH);
const finWZ = new Float32Array(TW * TH);                 // side sign for the per-side title flip
function rasterUV(mask, uv, ia, keep, find, world) {
  for (let i = 0; i < ia.length; i += 3) {
    if (!keep(find(ia[i]))) continue;
    const P = [];
    for (let j = 0; j < 3; j++) { const e = []; uv.getElement(ia[i + j], e); P.push([e[0] * TW, e[1] * TH]); }
    const minx = Math.max(0, Math.floor(Math.min(P[0][0], P[1][0], P[2][0]) - 1)), maxx = Math.min(TW - 1, Math.ceil(Math.max(P[0][0], P[1][0], P[2][0]) + 1));
    const miny = Math.max(0, Math.floor(Math.min(P[0][1], P[1][1], P[2][1]) - 1)), maxy = Math.min(TH - 1, Math.ceil(Math.max(P[0][1], P[1][1], P[2][1]) + 1));
    const [A, B, C] = P, den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1]);
    if (!den) continue;
    const wpos = world && world(i);
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
    const mat = prim.getMaterial();
    if (!uv || !prim.getIndices() || mat === gearMat) continue;
    if (mat?.getBaseColorTexture() !== tex) continue;    // only Stickers-atlas prims
    const { find, ia, box } = componentBoxes(prim, wm);
    const pos = prim.getAttribute('POSITION');
    const worldOf = i => [0, 1, 2].map(j => {
      const e = []; pos.getElement(ia[i + j], e);
      return xf(wm, e[0], e[1], e[2]);
    });
    for (const [k, test] of Object.entries(REGIONS)) {
      const roots = new Set();
      for (const [r, b] of box) if (test(b)) roots.add(r);
      if (roots.size) rasterUV(masks[k], uv, ia, r => roots.has(r), find, worldOf);
    }
  }
}
const JADE = [0x00, 0x65, 0x5b], WHITE = [0xf4, 0xf6, 0xf7], PALE_JADE = [0xb8, 0xd4, 0xd2];
const put = (buf, i, c) => { buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]; };
const blend = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * clamp01(t)));

// ---- source-art placements (world units; 1 unit ≈ 12.7 m, nose at −X) -------
// Fin plate spans x 2.01…3.03, y 0.59…1.42. u is flipped (forward = −X) so the
// SVG's pointed end faces the nose; the swept silhouette crops the mapping.
const finMark = (x, y) => sampleMark((3.02 - x) / 0.98, (y - 0.70) / 0.60);
// Jade mark immediately aft of the cockpit glass (which ends near x −2.49).
const noseMark = (x, y) => sampleMark((-2.20 - x) / 0.27, (y - 0.40) / 0.21);
// Official serif wordmark on the upper forward fuselage, above the window row
// (windows are geometry at y 0.46…0.49). The two sides are separate UV
// islands; flip world-X sampling per side (z vs the 0.055 centreline) so the
// lettering reads nose-first from either view.
const TITLE_XF = -2.12, TITLE_XA = -0.98, TITLE_Y0 = 0.512, TITLE_Y1 = 0.617;
const titleAt = (x, y, z) =>
  sampleWordmark(
    z > 0.055 ? (x - TITLE_XF) / (TITLE_XA - TITLE_XF) : (TITLE_XA - x) / (TITLE_XA - TITLE_XF),
    (y - TITLE_Y0) / (TITLE_Y1 - TITLE_Y0));

for (let p = 0; p < TW * TH; p++) {
  const i = p * CH;
  if (masks.fin[p]) put(rgb, i, blend(JADE, WHITE, finMark(finWX[p], finWY[p])));
  else if (masks.fuselage[p]) {
    const x = finWX[p], y = finWY[p], z = finWZ[p];
    const mark = Math.max(noseMark(x, y), titleAt(x, y, z));
    if (mark > 0) { put(rgb, i, blend(WHITE, JADE, mark)); continue; }
    const lower = clamp01((0.33 - y) / 0.14);            // subtle pale-jade belly band
    put(rgb, i, blend(WHITE, PALE_JADE, 0.72 * lower));
  }
}
// Uncovered texels (the atlas's own window ticks show through the hull mesh's
// window HOLES — no triangle maps them, but mip filtering would average their
// old green into the white hull): dilate the painted colours outward, then
// flood whatever remains (full-width cheatline overshoot etc.) with hull white.
{
  const covered = new Uint8Array(TW * TH);
  for (let p = 0; p < TW * TH; p++) covered[p] = masks.fin[p] | masks.fuselage[p];
  let frontier = [];
  for (let p = 0; p < TW * TH; p++) if (covered[p]) frontier.push(p);
  for (let it = 0; it < 16 && frontier.length; it++) {
    const next = [];
    for (const p of frontier) {
      const x = p % TW, y = (p / TW) | 0;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= TW || ny >= TH) continue;
        const q = ny * TW + nx;
        if (covered[q]) continue;
        covered[q] = 1;
        put(rgb, q * CH, [rgb[p * CH], rgb[p * CH + 1], rgb[p * CH + 2]]);
        next.push(q);
      }
    }
    frontier = next;
  }
  for (let p = 0; p < TW * TH; p++) if (!covered[p]) put(rgb, p * CH, WHITE);
}
tex.setImage(await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toBuffer())
   .setMimeType('image/png');
if (process.env.CX777_DEBUG_ATLAS)
  await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toFile(process.env.CX777_DEBUG_ATLAS);

// The Saudia scheme also rides two thin full-length RED geometry strips along
// the window line (Material.103) — recolour to hull white. Other reds (beacon
// lenses, engine markings) are small and stay.
for (const m of root.listMaterials()) {
  if (m.getName() === 'Material.103')
    m.setBaseColorFactor([srgb(0xf4), srgb(0xf6), srgb(0xf7), 1]);
}

// ---- 3. budget ----------------------------------------------------------------
const ratio = Number(ratioArg) || 0.082;
await doc.transform(weld(), simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.005 }));
// harder pass on the gear wheel stacks the global error bound protects
await MeshoptSimplifier.ready;
for (const mesh of root.listMeshes())
  for (const prim of mesh.listPrimitives()) {
    if (prim.getMaterial()?.getName() !== 'CXGear') continue;
    const idx = prim.getIndices(), pos = prim.getAttribute('POSITION');
    if (!idx || !pos) continue;
    const ia = idx.getArray() instanceof Uint32Array ? idx.getArray() : new Uint32Array(idx.getArray());
    if (ia.length < 300) continue;               // leave tiny brackets alone
    const [out] = MeshoptSimplifier.simplify(
      ia, pos.getArray(), 3, Math.floor(ia.length * 0.07 / 3) * 3, 0.1, ["LockBorder"]);
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
