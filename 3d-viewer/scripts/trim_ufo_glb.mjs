// Optimise the fly-mode UFO GLB (3d-viewer/data/models/plane-ufo.glb).
//
// Source: "UFO" by Islide (Sketchfab, CC BY 4.0 — attribution required,
// commercial use allowed; see ../data/models/README.md for provenance).
// Freely licensed, so this one lives in data/models/ proper — NOT behind the
// nc/ fence — and IS precached by the service worker.
//
// Unlike the airliners, this model's problem is NOT geometry: it ships a single
// 7 264-tri mesh (already lighter than every jet in the fleet) wrapped in ~29 MB
// of 4K textures — a 15.9 MB normal PNG and an 11.4 MB metallicRoughness PNG.
// So: no decimation at all, and the whole recipe is texture reduction (30 MB →
// ~0.7 MB, comfortably under every jet in the fleet).
//
//   - the metallicRoughness SLOT is unwired in favour of scalar factors — but
//     note Sketchfab points occlusionTexture at the SAME image, so that image
//     survives as the AO map rather than being pruned. That's deliberate: once
//     resized it costs ~85 KB and buys free ambient occlusion on the hull.
//   - baseColor / normal / occlusion / emissive are resized to 1024 px and
//     re-encoded as JPEG.
//   - the emissive map is the UFO's underside light — the abduction beam is
//     anchored to it, so it is kept and never dropped.
//
// Axes as authored: saucer lies in the XZ plane, dome +Y. Rotationally
// symmetric, so loadPlaneModel() needs no rotY; the beam hangs off -Y.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 sharp
//   node trim_ufo_glb.mjs <scene.gltf> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_ufo_glb.mjs <scene.gltf> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
for (const anim of doc.getRoot().listAnimations()) {
  for (const ch of anim.listChannels()) ch.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

for (const m of doc.getRoot().listMaterials()) {
  // Drop the 11.4 MB metallicRoughness map: at fly-mode scale it buys nothing a
  // scalar pair can't. Sketchfab also leaves metallicFactor at 1.0, which with
  // no environment map in the viewer renders the hull near-black — so clamp to a
  // brushed-metal finish (a touch shinier than the painted airliners' 0.15/0.5).
  const mr = m.getMetallicRoughnessTexture();
  if (mr) m.setMetallicRoughnessTexture(null);
  m.setMetallicFactor(0.35);
  m.setRoughnessFactor(0.42);
  // The emissive map IS the underside light — force it fully lit so the ring and
  // the belly lamp read at altitude, and so the beam has something to grow from.
  if (m.getEmissiveTexture()) m.setEmissiveFactor([1, 1, 1]);
}

await doc.transform(
  dedup(),
  prune(),                                      // sweeps the now-orphaned metallicRoughness image
  quantize({ pattern: /^(?!POSITION).*$/ }),    // POSITION stays float32 — three r160's computeBoundingBox reads quantized attrs raw (see trim_plane_glb.mjs)
  textureCompress({ encoder: sharp, resize: [1024, 1024], targetFormat: 'jpeg', quality: 80 }),
);

let tris = 0;
for (const mesh of doc.getRoot().listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
const tex = doc.getRoot().listTextures().map(t => `${t.getName() || '?'}:${(t.getImage()?.byteLength / 1024).toFixed(0)}KB`);
console.log('wrote', output, '—', Math.round(tris), 'tris,', doc.getRoot().listTextures().length, 'textures [' + tex.join(' ') + ']');
