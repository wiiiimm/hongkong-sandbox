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
let tris = 0;
for (const mesh of doc.getRoot().listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris');
