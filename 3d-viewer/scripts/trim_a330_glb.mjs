// Optimise the fly-mode A330-300 GLB (3d-viewer/data/models/nc/plane-a330.glb).
//
// Source: "Cathay Pacific Airbus A330-300" by OUTPISTON (Sketchfab,
// ⚠ CC BY-NC-SA 4.0 — NonCommercial, ShareAlike; see
// ../data/models/LICENSE-ASSETS.md for the fencing rules and
// ../data/models/README.md for provenance). The output stays BY-NC-SA and
// must live under data/models/nc/ so commercial deployments can delete it.
//
// The model ships with real Cathay Pacific livery textures — kept as-is (the
// whole point of this asset), just resized to ≤1024 px / re-encoded JPEG.
// Geometry is already light (42 770 tris) so this is the standard static
// recipe: dedup / prune / quantize, POSITION float32 (three r160's
// computeBoundingBox reads quantized attributes raw — see trim_plane_glb.mjs).
//
// Axes as authored: fuselage along Z, nose +Z — loadPlaneModel() yaws it 180°.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 sharp
//   node trim_a330_glb.mjs <scene.gltf> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_a330_glb.mjs <scene.gltf> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
for (const anim of doc.getRoot().listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}
// Sketchfab's export leaves metallicFactor at 1.0 — with no environment map in
// the viewer that renders the livery near-black. Clamp to a painted-hull finish
// (same ballpark as the procedural builders' 0.15 metal / 0.4 rough).
for (const m of doc.getRoot().listMaterials()) {
  if (m.getMetallicFactor() > 0.2) m.setMetallicFactor(0.15);
  if (m.getRoughnessFactor() < 0.4) m.setRoughnessFactor(0.5);
}
await doc.transform(
  dedup(),
  prune(),
  quantize({ pattern: /^(?!POSITION).*$/ }),
  // livery textures down to fly-mode resolution (PNGs with alpha are skipped
  // by the encoder and stay as authored — only the big JPEGs shrink)
  textureCompress({ encoder: sharp, resize: [1024, 1024], targetFormat: 'jpeg', quality: 78 }),
);

// ---- HKS-110 fleet rule: split the landing gear into "CXGear" primitives ----
// Union-find over the welded indices; any connected component living entirely
// below GEAR_TOP (WORLD Y-up units — vertices are tested through each node's
// world matrix, since node transforms survive the transform pipeline) is
// gear/wheels — moved to a cloned primitive whose material is renamed CXGear-*
// so loadPlaneModel() tags it (userData.gear) and stepFlight retracts it.
const GEAR_SPAN = 6;   // gear lives near the centreline; engines/wing bits sit further out
const GEAR_TOP = -2.7;
const root = doc.getRoot();
let gearTris = 0;
const seenMesh = new Set();
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh || seenMesh.has(mesh)) continue;
  seenMesh.add(mesh);
  const M = node.getWorldMatrix();
  const wy = (x, y, z) => M[1] * x + M[5] * y + M[9] * z + M[13];
  const ws = (x, y, z) => M[0] * x + M[4] * y + M[8] * z + M[12];   // world span coordinate
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
for (const mesh of doc.getRoot().listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris');
