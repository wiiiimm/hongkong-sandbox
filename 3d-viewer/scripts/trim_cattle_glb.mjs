// Optimise the fly-mode cattle — the UFO's quarry (HKS-113).
//   3d-viewer/data/models/cow.glb  · 3d-viewer/data/models/bull.glb
//
// Source: "Cow" and "Bull" by Quaternius (via Poly Pizza) — **CC0 / public
// domain**, the same author and the same licence as the walk-mode hiker. No
// attribution conditions at all; see ../data/models/README.md for provenance.
//
// These are the opposite problem from the aircraft. The meshes are already tiny
// (~2.4 k tris, no textures — Quaternius colours by material), but each ships
// **25 skeletal animations** and a skin, which is what makes the download 1 MB.
// The herd is scattered static across the map and every animal is a speck seen
// from a hovering saucer, so:
//
//   - strip all 25 animations and the skin/skeleton, leaving the bind pose (a
//     standing animal). This is the entire saving: ~1 MB → tens of KB.
//   - drop JOINTS/WEIGHTS with the skin, so the herd renders as plain static
//     meshes and dozens of them cost nothing.
//   - no decimation and no texture work — there is nothing to decimate or resize.
//
// Axes as authored: stands on +Y. Yaw is randomised per animal at scatter time,
// so the facing direction in the file does not matter.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4
//   node trim_cattle_glb.mjs <input.glb> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize } from '@gltf-transform/functions';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_cattle_glb.mjs <input.glb> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();

const anims = root.listAnimations().length;
for (const anim of root.listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// Drop the rig: with the animations gone the skin only costs us JOINTS/WEIGHTS
// attributes and a bone hierarchy the viewer would have to skin every frame, for
// a herd that never moves. The bind pose IS the standing animal we want.
const skins = root.listSkins().length;
for (const node of root.listNodes()) if (node.getSkin()) node.setSkin(null);
for (const skin of root.listSkins()) skin.dispose();
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives())
    for (const name of ['JOINTS_0', 'WEIGHTS_0', 'JOINTS_1', 'WEIGHTS_1'])
      if (p.getAttribute(name)) p.setAttribute(name, null);

await doc.transform(
  dedup(),
  prune(),
  quantize({ pattern: /^(?!POSITION).*$/ }),   // POSITION stays float32 — r160 reads quantized attrs raw (see trim_plane_glb.mjs)
);

let tris = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris; stripped', anims, 'animations and', skins, 'skin(s)');
