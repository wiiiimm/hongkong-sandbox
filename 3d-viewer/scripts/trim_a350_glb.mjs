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
//      press photo — painted from scratch, no pixels copied): white hull
//      (titles/marks wiped, window rows kept), brushwing-jade #00655B tail fin
//      with a white tapered-bezier brush stroke, jade winglets, light-grey
//      nacelles + belly fairing. Each region is masked by rasterising that
//      component's actual UV triangles (the atlas islands interleave, so
//      rectangle fills would bleed onto neighbours). No wordmarks — skipped
//      rather than garbled.
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
const WORLD_REGIONS = new Set(['fin', 'fuselage', 'belly']);
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
      const [wx, wy] = xf(wm, e[0], e[1], e[2]);
      return [wx, wy];
    });
    for (const [k, test] of Object.entries(REGIONS)) {
      const roots = new Set();
      for (const [r, b] of box) if (test(b)) roots.add(r);
      if (roots.size) rasterUV(masks[k], uv, ia, r => roots.has(r), find, WORLD_REGIONS.has(k) ? worldOf : null);
    }
  }
}
const JADE = [0x00, 0x65, 0x5b], WHITE = [0xf4, 0xf6, 0xf7], GREY = [0xdd, 0xe0, 0xe3];
const put = (i, c) => { rgb[i] = c[0]; rgb[i + 1] = c[1]; rgb[i + 2] = c[2]; };
// white brushwing on the jade fin, defined in fin world coords (fin spans
// x −35.8…−23.9 aft, y 17.6…27.2 up): a tapered quadratic bezier sweeping
// from the root leading edge up and aft toward the tip, like the real scheme.
const BRUSH = [];                                          // sampled [x, y, halfWidth]
{
  const P0 = [-27.5, 17.9], P1 = [-30.5, 22.5], P2 = [-34.0, 26.3];
  for (let t = 0; t <= 1; t += 0.005) {
    const x = (1 - t) * (1 - t) * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0];
    const y = (1 - t) * (1 - t) * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1];
    BRUSH.push([x, y, 0.85 * (1 - t) + 0.16 * t]);        // metres, tapering root → tip
  }
}
const onBrush = (x, y) => {
  for (const [bx, by, w] of BRUSH) {
    const dx = x - bx, dy = y - by;
    if (dx * dx + dy * dy < w * w) return true;
  }
  return false;
};
for (let p = 0; p < TW * TH; p++) {
  const i = p * CH, r = rgb[i], g = rgb[i + 1], b = rgb[i + 2];
  const lum = (r + g + b) / 765;
  if (masks.fin[p]) put(i, onBrush(finWX[p], finWY[p]) ? WHITE : JADE);
  else if (masks.winglet[p]) put(i, JADE);
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
      const x = finWX[p], y = finWY[p];
      const inRow = x > -26 && x < 27 && Math.abs(y - 15.55) < 0.17 && (((x % 0.8) + 0.8) % 0.8) < 0.42;
      put(i, inRow ? WIN : WHITE);
    } else put(i, WHITE);
  }
}
tex.setImage(await sharp(Buffer.from(rgb.buffer), { raw: { width: TW, height: TH, channels: CH } }).png().toBuffer())
   .setMimeType('image/png');

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
