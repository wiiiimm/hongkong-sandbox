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
//   3. paints OUR OWN Cathay-style livery in-file: fuselage, nose, doors and
//      tail-fin primitives move from the author's light-grey Material.027 to a
//      new "CXHull" brushwing-jade (#00655B) material — the same treatment the
//      cx777 GLB gets at load, baked here so no runtime tint is needed. Wings,
//      belly fairing and engines stay grey. No third-party airline branding.
//   4. flatten + join + weld + meshopt-simplify down to the tri budget, then
//      the shared recipe: dedup / prune / quantize. POSITION stays float32 —
//      three r160's computeBoundingBox reads quantized attributes raw (see
//      trim_plane_glb.mjs / trim_hiker_glb.mjs).
//
// Model axes as authored: fuselage along X (nose −X), span along Z, Y up —
// loadPlaneModel() yaws it −90° (cfg.rotY) so the nose faces −Z.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer
//   node trim_a350_glb.mjs <scene.gltf> <output.glb> [ratio]
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

// 3. our Cathay brushwing-jade livery — sRGB #00655B in linear terms
const jade = doc.createMaterial('CXHull')
  .setBaseColorFactor([0.0, 0.130, 0.104, 1.0])
  .setRoughnessFactor(0.45)
  .setMetallicFactor(0.15);
// hull / doors / nose / tail-fin groups whose light-grey skin takes the jade
const JADE_GROUPS = /^(body|Nose|Door|Cargo door|Cylinder\.018_4$|Cylinder\.026_80$)/;
let painted = 0;
for (const node of root.listNodes()) {
  if (!JADE_GROUPS.test(node.getName() || '')) continue;
  node.traverse(n => {
    const mesh = n.getMesh();
    if (!mesh) return;
    for (const p of mesh.listPrimitives()) {
      const mat = p.getMaterial();
      if (mat && mat.getName() === 'Material.027') { p.setMaterial(jade); painted++; }
    }
  });
}
console.log('primitives painted jade:', painted);

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
  quantize({ pattern: /^(?!POSITION).*$/, quantizeNormal: 8 }),
);


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

let tris = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris');
