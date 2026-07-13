// Build the fly-mode Betsy DC-3 GLB (3d-viewer/data/models/nc/plane-betsy.glb).
//
// Source: "McDonnell Douglas DC-3" by OUTPISTON (Sketchfab, ⚠ CC BY-NC-SA 4.0
// — NonCommercial, ShareAlike; fencing rules in ../data/models/LICENSE-ASSETS.md,
// provenance in ../data/models/README.md). Output stays BY-NC-SA under
// data/models/nc/ so commercial deployments can delete it; the procedural
// buildBetsyDC3 remains the fallback.
//
// Livery: Betsy (VR-HDB, Cathay Pacific's first aircraft, 1946) flew in
// polished BARE METAL — which is exactly how this model's fuselage atlas is
// painted, so the base stays as authored. We add the historically-correct
// touches (studied from period photography — Swire archive & preserved
// VR-HDB): a Union Jack on the tail fin, era-style "CATHAY PACIFIC AIRWAYS"
// titles above the cabin windows, and the VR-HDB registration on the rear
// fuselage. NO modern jade/green anywhere.
//
// The DC-3 is a taildragger with semi-fixed gear — wheels stay visible in
// flight (PLANE_GLBS.betsy sets fixedGear so the fleet gear rule skips it).
// Its prop0_still/prop1_still nodes match the loader's spinner regex and
// join the shared airborne prop-spin automatically.
//
// Axes as authored: nose +Z (tail wheel at −Z) → loadPlaneModel() yaws 180°.
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 sharp
//   node trim_betsy_glb.mjs <scene.gltf> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_betsy_glb.mjs <scene.gltf> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
for (const anim of root.listAnimations()) {
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// ---- period markings onto the bare-metal atlas (material03, 1024²) ---------
// Coordinates are authored for the 1024² atlas: fuselage side view spans the
// upper band (nose at the right), the tail-fin island sits mid-left.
for (const tex of root.listTextures()) {
  if (!/material03/i.test(tex.getURI() || tex.getName() || '')) continue;
  const img = sharp(Buffer.from(tex.getImage()));
  const { width: W, height: H } = await img.metadata();
  const sx = W / 1024, sy = H / 1024;
  // simplified Union Jack (reads correctly at fly-mode distances)
  const UJ = (x, y, w, h) => `
    <g transform="translate(${x * sx} ${y * sy})">
      <clipPath id="uj"><rect width="${w * sx}" height="${h * sy}"/></clipPath>
      <g clip-path="url(#uj)">
        <rect width="${w * sx}" height="${h * sy}" fill="#012169"/>
        <path d="M0,0 L${w * sx},${h * sy} M${w * sx},0 L0,${h * sy}" stroke="#fff" stroke-width="${h * sy / 5}"/>
        <path d="M0,0 L${w * sx},${h * sy} M${w * sx},0 L0,${h * sy}" stroke="#C8102E" stroke-width="${h * sy / 9}"/>
        <path d="M${w * sx / 2},0 V${h * sy} M0,${h * sy / 2} H${w * sx}" stroke="#fff" stroke-width="${h * sy / 3.2}"/>
        <path d="M${w * sx / 2},0 V${h * sy} M0,${h * sy / 2} H${w * sx}" stroke="#C8102E" stroke-width="${h * sy / 5.5}"/>
      </g>
    </g>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    ${UJ(95, 430, 84, 50)}                                              <!-- Union Jack, upper tail fin -->
    <text x="${430 * sx}" y="${222 * sy}" font-family="Helvetica, Arial, sans-serif"
      font-size="${19 * sy}" font-weight="bold" letter-spacing="${6 * sx}"
      fill="#1c2430">CATHAY PACIFIC AIRWAYS</text>                       <!-- era titles above the windows -->
    <text x="${120 * sx}" y="${215 * sy}" font-family="Helvetica, Arial, sans-serif"
      font-size="${26 * sy}" font-weight="bold" letter-spacing="${3 * sx}"
      fill="#1c2430">VR-HDB</text>                                       <!-- registration, rear fuselage -->
  </svg>`;
  const out = await img.composite([{ input: Buffer.from(svg) }]).jpeg({ quality: 85 }).toBuffer();
  tex.setImage(out).setMimeType('image/jpeg');
  console.log('marked', tex.getURI() || tex.getName());
}

// polished-metal finish, within what renders without an envmap
for (const m of root.listMaterials()) {
  if (m.getMetallicFactor() > 0.3) m.setMetallicFactor(0.25);
  if (m.getRoughnessFactor() < 0.35) m.setRoughnessFactor(0.35);
}

await doc.transform(
  dedup(),
  prune(),
  quantize({ pattern: /^(?!POSITION).*$/ }),
  textureCompress({ encoder: sharp, resize: [1024, 1024], targetFormat: 'jpeg', quality: 80 }),
);
let tris = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const idx = p.getIndices();
    tris += (idx ? idx.getCount() : p.getAttribute('POSITION').getCount()) / 3;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris');
