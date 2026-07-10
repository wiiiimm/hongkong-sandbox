// Trim + optimise the walk-mode hiker GLB (data/models/hiker-adventurer.glb).
// Keeps only the clips the viewer drives (Idle/Walk/Run/Wave), then
// resample/dedup/prune/quantize. ~1.94 MB → ~743 KB (≈234 KB gzip).
//
// Source model: “Adventurer” by Quaternius (CC0) — https://poly.pizza/m/5EGWBMpuXq
// (provenance: ../data/models/README.md)
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4
//   node trim_hiker_glb.mjs <input.glb> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, resample, quantize, dedup } from '@gltf-transform/functions';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_hiker_glb.mjs <input.glb> <output.glb>'); process.exit(1); }

const KEEP = new Set(['CharacterArmature|Idle', 'CharacterArmature|Walk',
                      'CharacterArmature|Run', 'CharacterArmature|Wave']);

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
for (const anim of doc.getRoot().listAnimations()) {
  if (KEEP.has(anim.getName())) continue;
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}
// POSITION stays float32: three r160's computeBoundingBox reads quantized
// (normalized-int) attributes raw, which broke the viewer's height normalisation.
await doc.transform(resample(), dedup(), prune(), quantize({ pattern: /^(?!POSITION).*$/ }));
await io.write(output, doc);
console.log('wrote', output);
