// Optimise a fly-mode aircraft GLB (3d-viewer/data/models/plane-*.glb) — HKS-110.
// Static airframes (no animations): dedup/prune/quantize with glTF-Transform.
//
// POSITION stays float32: three r160's computeBoundingBox reads quantized
// (normalized-int) attributes raw, which broke the hiker's height normalisation
// (see trim_hiker_glb.mjs) — the plane loader fits models by bounding box too.
//
// Sources (provenance: ../data/models/README.md):
//   plane-prop.glb — "Small Airplane" by Vojtěch Balák (CC-BY 3.0, Poly Pizza)
//   plane-747.glb  — "Boeing 747" by Miha Lunar (CC-BY 3.0, Poly Pizza)
//   plane-777.glb  — "Airplane" by Poly by Google (CC-BY 3.0, Poly Pizza)
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4
//   node trim_plane_glb.mjs <input.glb> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, quantize, dedup } from '@gltf-transform/functions';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_plane_glb.mjs <input.glb> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
// airframes are static — drop any stray animation data wholesale
for (const anim of doc.getRoot().listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}
await doc.transform(dedup(), prune(), quantize({ pattern: /^(?!POSITION).*$/ }));
await io.write(output, doc);
console.log('wrote', output);
