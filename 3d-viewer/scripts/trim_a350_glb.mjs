// Optimise the fly-mode A350 GLB (3d-viewer/data/models/plane-a350.glb) — HKS-110.
//
// Source: "[FREE] Airbus A350-1000" by hakai315 (CC BY 4.0, Sketchfab) —
// 1.97 M tris / 70 MB scene.bin as published. Way past the fly-mode budget, so
// this script does much more than trim_plane_glb.mjs:
//
//   1. drops interior / wasted-at-distance groups by name (engine fan blades,
//      cargo-bay interiors, cabin floors) AND two stray outlier meshes
//      ("Plane_3" floats ~140 m ahead of the nose — it would wreck the
//      bounding-box fit loadPlaneModel() uses to scale the airframe);
//   2. strips the two bundled textures (engine swirl detail — invisible at
//      fly-mode distances) and flattens those materials to grey;
//   3. paints OUR OWN Cathay-style livery in-file — designed from scratch,
//      expressly NOT derived from any third-party livery texture (in
//      particular not from the NC-fenced outpiston A330 textures — that
//      would drag CC BY-NC-SA into this CC BY asset):
//        - fuselage / nose / doors / tail-fin primitives move to a "CXHull"
//          material that carries a GENERATED livery texture (drawn in-script
//          with sharp, planar side-projection UVs): white upper fuselage,
//          light-grey belly below the waterline, brushwing-jade (#00655B)
//          tail fin with our own white brush-stroke swoosh;
//        - engine nacelle cowls (found by connected component inside the
//          two nacelle boxes) split to a jade "CXEngine" material — fans
//          and exhaust cones stay grey; wings/belly fairing stay grey.
//      No third-party airline branding, no wordmarks.
//   4. flatten + join + weld + meshopt-simplify down to the tri budget, then
//      the shared recipe: dedup / prune / quantize. POSITION stays float32 —
//      three r160's computeBoundingBox reads quantized attributes raw (see
//      trim_plane_glb.mjs / trim_hiker_glb.mjs).
//
// Model axes as authored: fuselage along X (nose −X), span along Z, Y up —
// loadPlaneModel() yaws it −90° (cfg.rotY) so the nose faces −Z.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer sharp
//   node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]
import sharp from 'sharp';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { compactPrimitive, dedup, flatten, join, prune, quantize, simplify, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();

// airframes are static — drop any stray animation data wholesale
for (const anim of root.listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// 1. drop interiors + outliers (names as authored in the Sketchfab export)
const DROP = /^(Blaes in inside|Cargo \.|Cargo _|Plane_3$|Plane\.001|Cube\.005_142)/;
let dropped = 0;
for (const node of root.listNodes()) {
  if (DROP.test(node.getName() || '')) { node.dispose(); dropped++; }
}
console.log('dropped groups:', dropped);

// 2. strip textures, flatten the textured engine materials to grey
for (const tex of root.listTextures()) tex.dispose();
for (const m of root.listMaterials()) {
  if (/^No_human_logo/.test(m.getName() || '')) m.setBaseColorFactor([0.55, 0.56, 0.57, 1]);
}

// 3. route the hull skin to its own "CXHull" material so it survives join()
//    as a separate primitive — the livery texture is painted onto it in
//    stage 5 (after simplification), where the final geometry is known.
const hullMat = doc.createMaterial('CXHull')
  .setBaseColorFactor([1, 1, 1, 1])
  .setRoughnessFactor(0.45)
  .setMetallicFactor(0.15);
// hull / doors / nose / tail-fin groups whose light-grey skin takes the livery
const HULL_GROUPS = /^(body|Nose|Door|Cargo door|Cylinder\.018_4$|Cylinder\.026_80$)/;
let routed = 0;
for (const node of root.listNodes()) {
  if (!HULL_GROUPS.test(node.getName() || '')) continue;
  node.traverse(n => {
    const mesh = n.getMesh();
    if (!mesh) return;
    for (const p of mesh.listPrimitives()) {
      const mat = p.getMaterial();
      if (mat && mat.getName() === 'Material.027') { p.setMaterial(hullMat); routed++; }
    }
  });
}
console.log('hull primitives routed to CXHull:', routed);

// 4. crush to budget: weld + meshopt-simplify, then drop connected components
//    too small to read at fly-mode distances (nuts, brackets, hydraulic lines —
//    each one floors the simplifier at a handful of tris, and there are
//    thousands of them), then simplify again and finish with the shared recipe.
const ratio = Number(ratioArg) || 0.004;
await doc.transform(
  dedup(),
  flatten(),
  join(),
  weld(),
  simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.04 }),
);
// component prune: union-find over welded indices; keep components whose bbox
// diagonal clears minDiag (model units — the airframe is ~120 units long)
const minDiag = Number(process.env.MINDIAG) || 2.6;
for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices(), pos = prim.getAttribute('POSITION');
    if (!idx || !pos) continue;
    const ia = idx.getArray(), nVerts = pos.getCount();
    const parent = new Uint32Array(nVerts).map((_, i) => i);
    const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
    for (let i = 0; i < ia.length; i += 3) {
      const a = find(ia[i]), b = find(ia[i + 1]), c = find(ia[i + 2]);
      parent[b] = a; parent[c] = a;
    }
    const box = new Map();   // component root vert → [minx,miny,minz,maxx,maxy,maxz]
    const el = [];
    for (let v = 0; v < nVerts; v++) {
      const r = find(v); pos.getElement(v, el);
      let b = box.get(r);
      if (!b) box.set(r, [el[0], el[1], el[2], el[0], el[1], el[2]]);
      else for (let k = 0; k < 3; k++) { if (el[k] < b[k]) b[k] = el[k]; if (el[k] > b[k + 3]) b[k + 3] = el[k]; }
    }
    const keep = new Set();
    for (const [r, b] of box)
      if (Math.hypot(b[3] - b[0], b[4] - b[1], b[5] - b[2]) >= minDiag) keep.add(r);
    const out = [];
    for (let i = 0; i < ia.length; i += 3)
      if (keep.has(find(ia[i]))) out.push(ia[i], ia[i + 1], ia[i + 2]);
    if (out.length < ia.length) {
      idx.setArray(new Uint32Array(out));
      compactPrimitive(prim);
    }
  }
}
await doc.transform(
  simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.04 }),
  prune(),
);

// ---- 5. Cathay-style livery (our own design — see header; HKS-110) ---------
// World-space helpers: node transforms survive the pipeline, so every
// position test goes through the owning node's world matrix.
const worldFns = (node) => {
  const M = node.getWorldMatrix();
  return {
    wx: (x, y, z) => M[0] * x + M[4] * y + M[8] * z + M[12],
    wy: (x, y, z) => M[1] * x + M[5] * y + M[9] * z + M[13],
    wz: (x, y, z) => M[2] * x + M[6] * y + M[10] * z + M[14],
  };
};

// 5a. hull livery texture — planar side projection (u ← world x, v ← world y,
// flipped so image-top = fin-top). Both sides map to the same texels; the
// livery is symmetric so that is exactly what we want. Planar UVs interpolate
// affinely, so even the fin's giant post-simplify triangles sample correctly.
// Geometry landmarks (world units, airframe ~121 long, nose at x≈−57):
//   fuselage crown ≈ y 13.8 · belly ≈ y 4.6 · fin y 14→29, x 48→63.
const HX0 = -58, HX1 = 64, HY0 = 4.0, HY1 = 29.5;      // texture coverage box
const TW = 1024, TH = 512;
const WHITE = [0xf2, 0xf4, 0xf5], BELLY = [0x9d, 0xa2, 0xa6], JADEC = [0x00, 0x65, 0x5b];
const WATERLINE = 8.4;   // below → belly grey
const FIN_Y = 14.0;      // above → jade fin
// brushwing stroke: quadratic bezier up the fin, wide at the root, tapering
const P0 = [52.4, 15.0], P1 = [56.6, 19.2], P2 = [60.4, 26.0];
const strokeW = t => 1.5 - 1.0 * t;
const bez = t => [
  (1 - t) * (1 - t) * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0],
  (1 - t) * (1 - t) * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1],
];
const px = new Uint8Array(TW * TH * 3);
for (let j = 0; j < TH; j++) {
  const y = HY1 - (j + 0.5) / TH * (HY1 - HY0);
  for (let i = 0; i < TW; i++) {
    const x = HX0 + (i + 0.5) / TW * (HX1 - HX0);
    let c = y < WATERLINE ? BELLY : WHITE;
    if (y > FIN_Y) {
      c = JADEC;
      // white brush stroke — min distance to the bezier vs tapered width
      for (let s = 0; s <= 40; s++) {
        const t = s / 40, b = bez(t);
        const dx = x - b[0], dy = y - b[1];
        if (dx * dx + dy * dy < strokeW(t) * strokeW(t)) { c = WHITE; break; }
      }
    }
    const o = (j * TW + i) * 3;
    px[o] = c[0]; px[o + 1] = c[1]; px[o + 2] = c[2];
  }
}
const liveryPng = await sharp(px, { raw: { width: TW, height: TH, channels: 3 } })
  .png({ compressionLevel: 9, palette: true }).toBuffer();
const liveryTex = doc.createTexture('CXLivery').setImage(liveryPng).setMimeType('image/png');
hullMat.setBaseColorTexture(liveryTex);
let uvVerts = 0;
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const { wx, wy } = worldFns(node);
  for (const prim of mesh.listPrimitives()) {
    if (prim.getMaterial() !== hullMat) continue;
    const pos = prim.getAttribute('POSITION');
    const uv = new Float32Array(pos.getCount() * 2), el = [];
    for (let v = 0; v < pos.getCount(); v++) {
      pos.getElement(v, el);
      uv[v * 2] = (wx(el[0], el[1], el[2]) - HX0) / (HX1 - HX0);
      uv[v * 2 + 1] = (HY1 - wy(el[0], el[1], el[2])) / (HY1 - HY0);
    }
    prim.setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(uv));
    uvVerts += pos.getCount();
  }
}
console.log('hull UV-mapped verts:', uvVerts, '— livery png', liveryPng.length, 'bytes');

// 5b. engine nacelle cowls → jade "CXEngine". Connected components (union-find
// over indices) whose world bbox sits entirely inside a nacelle box are cowl
// surfaces — the wings never satisfy that (they run on past the box). Fans
// (Material.038) and exhaust cones (Material.033) are excluded by name.
const engineMat = doc.createMaterial('CXEngine')
  .setBaseColorFactor([0.0, 0.130, 0.104, 1.0])   // sRGB #00655B in linear terms
  .setRoughnessFactor(0.45).setMetallicFactor(0.15);
const NAC = { x0: -16, x1: -1.5, y0: 1.0, y1: 8.0, z0: 14.0, z1: 23.0 };
const inNac = (x, y, z) =>
  x > NAC.x0 && x < NAC.x1 && y > NAC.y0 && y < NAC.y1 && Math.abs(z) > NAC.z0 && Math.abs(z) < NAC.z1;
let engTris = 0;
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const { wx, wy, wz } = worldFns(node);
  for (const prim of [...mesh.listPrimitives()]) {
    const mn = prim.getMaterial()?.getName() || '';
    if (mn === 'CXHull' || mn === 'Material.038' || mn === 'Material.033') continue;
    const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
    if (!pos || !idx) continue;
    const n = pos.getCount(), ia = idx.getArray(), el = [];
    const parent = new Uint32Array(n).map((_, i) => i);
    const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
    for (let i = 0; i < ia.length; i += 3) { const a = find(ia[i]); parent[find(ia[i + 1])] = a; parent[find(ia[i + 2])] = a; }
    const inside = new Map();   // component root → still fully inside a nacelle box?
    const used = new Set(ia);
    for (const v of used) {
      pos.getElement(v, el);
      const ok = inNac(wx(el[0], el[1], el[2]), wy(el[0], el[1], el[2]), wz(el[0], el[1], el[2]));
      const r = find(v);
      inside.set(r, (inside.get(r) ?? true) && ok);
    }
    const eng = [], rest = [];
    for (let i = 0; i < ia.length; i += 3)
      (inside.get(find(ia[i])) ? eng : rest).push(ia[i], ia[i + 1], ia[i + 2]);
    if (!eng.length) continue;
    engTris += eng.length / 3;
    const ep = prim.clone();
    ep.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(eng)));
    ep.setMaterial(engineMat);
    mesh.addPrimitive(ep);
    prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(rest)));
  }
}
console.log('engine nacelle tris painted jade:', engTris);

// ---- HKS-110 fleet rule: split the landing gear into "CXGear" primitives ----
// Union-find over the welded indices; any connected component living entirely
// below GEAR_TOP (WORLD Y-up units — vertices are tested through each node's
// world matrix, since node transforms survive the transform pipeline) is
// gear/wheels — moved to a cloned primitive whose material is renamed CXGear-*
// so loadPlaneModel() tags it (userData.gear) and stepFlight retracts it.
const GEAR_SPAN = 8;   // gear lives near the centreline; engines/wing bits sit further out
const GEAR_TOP = 5.0;
let gearTris = 0;
const seenMesh = new Set();
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh || seenMesh.has(mesh)) continue;
  seenMesh.add(mesh);
  const M = node.getWorldMatrix();
  const wy = (x, y, z) => M[1] * x + M[5] * y + M[9] * z + M[13];
  const ws = (x, y, z) => M[2] * x + M[6] * y + M[10] * z + M[14];   // world span coordinate
  for (const prim of [...mesh.listPrimitives()]) {
    const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
    if (!pos || !idx) continue;
    const n = pos.getCount(), ia = idx.getArray(), el = [];
    const parent = new Uint32Array(n).map((_, i) => i);
    const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
    for (let i = 0; i < ia.length; i += 3) { const a = find(ia[i]); parent[find(ia[i + 1])] = a; parent[find(ia[i + 2])] = a; }
    const ymax = new Map(), smax = new Map();
    for (let v = 0; v < n; v++) { pos.getElement(v, el); const r = find(v); const y = wy(el[0], el[1], el[2]); ymax.set(r, Math.max(ymax.get(r) ?? -1e9, y)); smax.set(r, Math.max(smax.get(r) ?? 0, Math.abs(ws(el[0], el[1], el[2])))); }
    const g = [], b = [];
    for (let i = 0; i < ia.length; i += 3)
      ((ymax.get(find(ia[i])) < GEAR_TOP && smax.get(find(ia[i])) < GEAR_SPAN) ? g : b).push(ia[i], ia[i + 1], ia[i + 2]);
    if (!g.length) continue;
    gearTris += g.length / 3;
    const gp = prim.clone();
    gp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(g)));
    const gm = (prim.getMaterial() || doc.createMaterial()).clone().setName('CXGear-' + (prim.getMaterial()?.getName() || 'mat'));
    gp.setMaterial(gm);
    mesh.addPrimitive(gp);
    prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(b)));
  }
}
console.log('gear tris split out:', gearTris);

// final shared recipe step — POSITION stays float32 (see header)
await doc.transform(quantize({ pattern: /^(?!POSITION).*$/, quantizeNormal: 8 }));

let tris = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris');
