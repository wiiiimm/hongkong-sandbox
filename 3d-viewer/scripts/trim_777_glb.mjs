// Build the fly-mode 777-300ER GLB (3d-viewer/data/models/plane-777.glb) — HKS-110.
//
// Source: "Boeing 777-300er." by 777_Boeing / The F-35's Modeling Hub
// (Sketchfab, CC BY 4.0 — commercial OK; provenance ../data/models/README.md).
// 120 k tris, two primitives, ONE flat grey material, no UVs, no textures —
// so our Cathay livery is painted as VERTEX COLOURS by position (local axes:
// x = span, y = fore-aft with the tail at +y, z = up; the Sketchfab root node
// yaws/scales it into world):
//
//   - fuselage barrel + nose + tail fin → brushwing jade #00655B
//   - wings / engines / stabilisers / belly hardware → light airframe greys
//
// Landing gear is split out by connected component (union-find over welded
// indices): components living entirely below the engine line get a separate
// "CXGear" material so loadPlaneModel() can tag them (userData.gear) and
// stepFlight can hide them once airborne.
//
// Then weld + meshopt-simplify to budget and the shared recipe (dedup/prune/
// quantize, POSITION float32 — three r160 reads quantized attributes raw).
// Nose faces world +Z → loadPlaneModel() yaws 180° (cfg.rotY).
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer
//   node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]
import { Document, NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, simplify, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
for (const anim of root.listAnimations()) {
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// crush first so the vertex paint applies to the final vertices
const ratio = Number(ratioArg) || 0.4;
await doc.transform(weld(), simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.002 }));

// ---- paint + gear split (local model coords, see header) --------------------
const srgb = (c) => Math.pow((c / 255 + 0.055) / 1.055, 2.4);
const JADE = [srgb(0x00), srgb(0x65), srgb(0x5b)];
const WING = [srgb(0xc7), srgb(0xca), srgb(0xcc)];
const BELLY = [srgb(0x9d), srgb(0xa2), srgb(0xa6)];
const gearMat = doc.createMaterial('CXGear')
  .setBaseColorFactor([srgb(0x55), srgb(0x57), srgb(0x59), 1])
  .setRoughnessFactor(0.7).setMetallicFactor(0.1);
const GEAR_TOP = -0.15;   // components entirely below this (engines bottom ≈ -0.124) are gear
for (const mesh of root.listMeshes()) {
  for (const prim of [...mesh.listPrimitives()]) {
    const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
    if (!pos || !idx) continue;
    const n = pos.getCount(), ia = idx.getArray(), el = [];
    // union-find → per-component z-max, to split the gear off
    const parent = new Uint32Array(n).map((_, i) => i);
    const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
    for (let i = 0; i < ia.length; i += 3) { const a = find(ia[i]); parent[find(ia[i + 1])] = a; parent[find(ia[i + 2])] = a; }
    const zmax = new Map();
    for (let v = 0; v < n; v++) { pos.getElement(v, el); const r = find(v); zmax.set(r, Math.max(zmax.get(r) ?? -1e9, el[2])); }
    const gearTris = [], bodyTris = [];
    for (let i = 0; i < ia.length; i += 3)
      (zmax.get(find(ia[i])) < GEAR_TOP ? gearTris : bodyTris).push(ia[i], ia[i + 1], ia[i + 2]);
    if (gearTris.length) {
      const gp = prim.clone();
      gp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(gearTris)));
      gp.setMaterial(gearMat);
      mesh.addPrimitive(gp);
      prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(bodyTris)));
    }
    // vertex-colour livery on the body primitive
    const col = new Float32Array(n * 3);
    for (let v = 0; v < n; v++) {
      pos.getElement(v, el);
      const [x, y, z] = el;
      let c = WING;
      if (y > 0.52 && z > 0.08) c = JADE;                       // tail fin
      else if (Math.abs(x) < 0.078 && z > -0.115 && z < 0.12) c = JADE;   // fuselage barrel + nose
      else if (Math.abs(x) < 0.09 && z <= -0.115 && z > -0.15) c = BELLY; // belly / fairing
      col[v * 3] = c[0]; col[v * 3 + 1] = c[1]; col[v * 3 + 2] = c[2];
    }
    prim.setAttribute('COLOR_0', doc.createAccessor().setType('VEC3').setArray(col));
    const m = prim.getMaterial();
    m.setBaseColorFactor([1, 1, 1, 1]).setRoughnessFactor(0.45).setMetallicFactor(0.15);
  }
}

await doc.transform(dedup(), prune(), quantize({ pattern: /^(?!POSITION).*$/, quantizeNormal: 8 }));
let tris = 0, gear = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const t = (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3;
    tris += t;
    if (p.getMaterial()?.getName() === 'CXGear') gear += t;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris (', Math.round(gear), 'gear )');
