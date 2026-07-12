// Optimise fly-mode aircraft GLBs (data/models/plane-*.glb).
// Resample/dedup/prune/quantize — no animation keep-list (static airframes).
// POSITION stays float32 (three r160 Box3).
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4
//   node trim_plane_glb.mjs <input.glb> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, resample, quantize, dedup } from '@gltf-transform/functions';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_plane_glb.mjs <input.glb> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
// Drop all animations — flight models are static airframes
for (const anim of doc.getRoot().listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}
await doc.transform(resample(), dedup(), prune(), quantize({ pattern: /^(?!POSITION).*$/ }));
await io.write(output, doc);
console.log('wrote', output);
