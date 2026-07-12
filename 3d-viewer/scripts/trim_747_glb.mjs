// Build the fly-mode 747 GLB (3d-viewer/data/models/plane-747.glb) — HKS-110.
//
// Source: "Boeing 747-100" by Marine / rd.palaciosdeleon26 (Sketchfab,
// CC BY 4.0 — commercial OK; provenance ../data/models/README.md). A clean
// 35.5 k-tri flight-sim-grade airframe, but its livery texture carries full
// ANA (All Nippon Airways) branding — third-party airline identity we must
// NOT ship. This script repaints that texture into OUR OWN Cathay-style
// treatment before the standard optimisation recipe:
//
//   1. pixel pass over the fuselage/tail atlas: every ANA blue (navy
//      cheatline, cyan band, tail wash) is remapped to brushwing jade
//      (#00655B), luminance preserved — the twin window-line stripes become
//      the classic 90s CX green cheatline of their own accord;
//   2. SVG overlay: airline titles (“All Nippon Airways”, 全日空), hinomaru,
//      star, registrations (JA8157 / 157 / mirrored wing reg) painted out
//      hull-white/grey; the fins’ leftover white “ANA” letters flooded jade,
//      then our white brushwing stroke drawn across each fin;
//   3. dedup / prune / quantize (POSITION float32 — three r160 reads
//      quantized attributes raw) + textures resized ≤1024 px JPEG.
//
// Axes as authored: nose −Z (no yaw needed in loadPlaneModel()).
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 sharp
//   node trim_747_glb.mjs <scene.gltf> <output.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp';

const [input, output] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_747_glb.mjs <scene.gltf> <output.glb>'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();

// ---- 1+2. repaint the ANA atlas (2048×2048) into our Cathay treatment ------
const JADE = [0x00, 0x65, 0x5b];
for (const tex of root.listTextures()) {
  if (!/smallspecmap/i.test(tex.getURI() || tex.getName() || '')) continue;
  const img = sharp(Buffer.from(tex.getImage()));
  const { width: W, height: H } = await img.metadata();
  const raw = await img.raw().toBuffer({ resolveWithObject: true });
  const d = raw.data, ch = raw.info.channels;
  for (let i = 0; i < d.length; i += ch) {
    const r = d[i], g = d[i + 1], b = d[i + 2];
    if (b > g + 20 && b > r * 1.3 + 20) {              // ANA navy + cyan family
      const t = (r + g + b) / (3 * 110);               // keep the shading
      d[i] = Math.min(255, JADE[0] * t);
      d[i + 1] = Math.min(255, JADE[1] * t);
      d[i + 2] = Math.min(255, JADE[2] * t);
    }
  }
  // overlays are authored for 2048² and scaled by sx/sy for safety
  const sx = W / 2048, sy = H / 2048;
  const R = (x, y, w, h, fill) =>
    `<rect x="${x * sx}" y="${y * sy}" width="${w * sx}" height="${h * sy}" fill="${fill}"/>`;
  const white = '#f4f5f4', grey = '#b9bcbe';
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    ${R(325, 680, 290, 115, grey)}                            <!-- mirrored wing registration -->
    ${R(0, 1075, 60, 60, white)} ${R(1030, 1075, 60, 60, white)}      <!-- 空 char, both halves -->
    ${R(55, 1085, 265, 55, white)} ${R(1080, 1085, 250, 60, white)}   <!-- All Nippon Airways titles -->
    ${R(290, 1455, 445, 90, white)} ${R(1325, 1455, 450, 90, white)}  <!-- 全日空 + star + hinomaru -->
    ${R(245, 1725, 90, 65, grey)} ${R(1230, 1725, 200, 65, grey)}      <!-- "157" nose-gear door tags -->
    ${R(180, 1860, 150, 55, white)} ${R(1205, 1860, 150, 55, white)}  <!-- JA8157 registrations -->
    ${R(0, 1890, 170, 40, white)} ${R(1005, 1890, 215, 40, white)}    <!-- BOEING 747 titles -->
    ${R(585, 1690, 365, 358, '#00655b')} ${R(1455, 1690, 593, 358, '#00655b')}  <!-- fins: flood the ANA letters jade -->
    <g stroke="${white}" stroke-width="${34 * sx}" fill="none" stroke-linecap="round">
      <path d="M ${640 * sx} ${1980 * sy} Q ${770 * sx} ${1900 * sy} ${910 * sx} ${1750 * sy}"/>
      <path d="M ${1540 * sx} ${1980 * sy} Q ${1670 * sx} ${1900 * sy} ${1810 * sx} ${1750 * sy}"/>
    </g></svg>`;
  const out = await sharp(d, { raw: { width: W, height: H, channels: ch } })
    .composite([{ input: Buffer.from(svg) }])
    .png().toBuffer();
  tex.setImage(out).setMimeType('image/png');
  console.log('repainted', tex.getURI() || tex.getName());
}

// ---- 3. standard static-airframe recipe ------------------------------------
for (const anim of root.listAnimations()) {
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}
// FS-style exports leave metallic at 1.0 — near-black without an envmap
for (const m of root.listMaterials()) {
  if (m.getMetallicFactor() > 0.2) m.setMetallicFactor(0.15);
  if (m.getRoughnessFactor() < 0.4) m.setRoughnessFactor(0.5);
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
