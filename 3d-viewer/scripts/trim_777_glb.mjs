// Build the fly-mode 777-300ER GLB (3d-viewer/data/models/plane-777.glb) — HKS-110.
//
// Source: "Boeing 777-300er." by 777_Boeing / The F-35's Modeling Hub
// (Sketchfab, CC BY 4.0 — commercial OK; provenance ../data/models/README.md).
// 120 k tris, two primitives, ONE flat grey material, no UVs, no textures —
// so the base Cathay livery is painted as VERTEX COLOURS by position (local axes:
// x = span, y = fore-aft with the tail at +y, z = up; the Sketchfab root node
// yaws/scales it into world):
//
//   - fuselage barrel + nose → white with a pale-jade lower band
//   - tail fin → brushwing jade #005D63
//   - wings / engines / stabilisers / belly hardware → light airframe greys
//
// The project-supplied Cathay artwork in scripts/assets/ becomes small MASK
// decal textures on tangent quads: exact serif wordmarks on both forward
// fuselage sides, a jade brushwing beside each cockpit side, and the complete
// white brushwing on both sides of the fin. A generated dark window-row decal
// restores the cabin windows that the textureless source otherwise lacks.
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
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer sharp
//   node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, simplify, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_777_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
const assetPath = name => fileURLToPath(new URL(`./assets/${name}`, import.meta.url));
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
const JADE = [srgb(0x00), srgb(0x5d), srgb(0x63)];
const WHITE = [srgb(0xf4), srgb(0xf6), srgb(0xf7)];
const PALE_JADE = [srgb(0xb8), srgb(0xd4), srgb(0xd2)];
const WING = [srgb(0xe0), srgb(0xe4), srgb(0xe7)];
const BELLY = [srgb(0xac), srgb(0xb4), srgb(0xb9)];
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * Math.max(0, Math.min(1, t)));
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
      // Follow the fin's swept leading edge, including its flared root.
      // Restricting paint to the narrow centreline keeps the stabilisers grey.
      const finLeadingY = z < 0 ? 0.54 - 3 * z
        : z < 0.08 ? 0.54 + 1.75 * z
          : 0.60 + z;
      if (Math.abs(x) < 0.025 && z > -0.065 && y > finLeadingY) c = JADE;
      else if (Math.abs(x) < 0.078 && z > -0.115 && z < 0.12) {           // fuselage barrel + nose
        const lower = Math.max(0, Math.min(1, (-0.045 - z) / 0.065));
        c = mix(WHITE, PALE_JADE, lower * 0.72);
      }
      else if (Math.abs(x) < 0.09 && z <= -0.115 && z > -0.15) c = BELLY; // belly / fairing
      col[v * 3] = c[0]; col[v * 3 + 1] = c[1]; col[v * 3 + 2] = c[2];
    }
    prim.setAttribute('COLOR_0', doc.createAccessor().setType('VEC3').setArray(col));
    const m = prim.getMaterial();
    m.setBaseColorFactor([1, 1, 1, 1]).setRoughnessFactor(0.45).setMetallicFactor(0.15);
  }
}

// ---- source-backed Cathay decals -------------------------------------------
const markSvg = await readFile(assetPath('cathay-brushwing.svg'), 'utf8');
const markPng = async colour => sharp(Buffer.from(markSvg.replace(/#005d63/gi, colour)))
  .resize({ width: 512 }).png().toBuffer();
const greenMarkTex = doc.createTexture('CX brushwing jade')
  .setImage(await markPng('#005d63')).setMimeType('image/png');
const whiteMarkTex = doc.createTexture('CX brushwing white')
  .setImage(await markPng('#ffffff')).setMimeType('image/png');

// Crop the brushwing out of the supplied lock-up and turn only the official
// serif lettering into an antialiased transparent jade mask.
const wordRaw = await sharp(assetPath('cathay-wordmark.jpg'))
  .extract({ left: 107, top: 80, width: 289, height: 27 })
  .raw().toBuffer({ resolveWithObject: true });
const wordRgba = new Uint8ClampedArray(wordRaw.info.width * wordRaw.info.height * 4);
for (let p = 0; p < wordRaw.info.width * wordRaw.info.height; p++) {
  const si = p * wordRaw.info.channels, di = p * 4;
  const r = wordRaw.data[si], g = wordRaw.data[si + 1], b = wordRaw.data[si + 2];
  wordRgba[di] = 0x00; wordRgba[di + 1] = 0x5d; wordRgba[di + 2] = 0x63;
  wordRgba[di + 3] = Math.round(255 * Math.max(0, Math.min(1, (Math.min(g, b) - r - 3) / 48)));
}
const wordTex = doc.createTexture('CX serif wordmark').setImage(await sharp(
  Buffer.from(wordRgba.buffer),
  { raw: { width: wordRaw.info.width, height: wordRaw.info.height, channels: 4 } },
).png().toBuffer()).setMimeType('image/png');

// The textureless source also has no visible cabin windows. A tiny generated
// row texture gives both sides the long 777-300ER window rhythm without adding
// dozens of meshes.
let windowX = 8;
const windowRects = [];
for (let i = 0; i < 61; i++) {
  if ([11, 29, 47].includes(i)) windowX += 13;          // door-sized breaks
  windowRects.push(`<rect x="${windowX}" y="18" width="8" height="28" rx="4"/>`);
  windowX += 15;
}
const windowSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${windowX + 8}" height="64"><g fill="#343b42">${windowRects.join('')}</g></svg>`;
const windowTex = doc.createTexture('CX cabin windows')
  .setImage(await sharp(Buffer.from(windowSvg)).png().toBuffer()).setMimeType('image/png');

const decalMaterial = (name, texture) => doc.createMaterial(name)
  .setBaseColorTexture(texture).setBaseColorFactor([1, 1, 1, 1])
  .setAlphaMode('MASK').setAlphaCutoff(0.08).setDoubleSided(true)
  .setRoughnessFactor(0.5).setMetallicFactor(0.05);
const wordMat = decalMaterial('CXWordmark', wordTex);
const greenMarkMat = decalMaterial('CXNoseBrushwing', greenMarkTex);
const windowMat = decalMaterial('CXCabinWindows', windowTex);
const tailMat = decalMaterial('CXTailBrushwing', whiteMarkTex);

const meshNode = root.listNodes().find(n => n.getMesh());
const decalParent = meshNode?.getParentNode();
function addSideDecals(name, x, yA, yB, z0, z1, material, flipNegative = false) {
  for (const side of [-1, 1]) {
    const uv = flipNegative && side > 0
      ? [1, 1, 0, 1, 0, 0, 1, 0]
      : [0, 1, 1, 1, 1, 0, 0, 0];
    const prim = doc.createPrimitive()
      .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(new Float32Array([
        side * x, yA, z0, side * x, yB, z0,
        side * x, yB, z1, side * x, yA, z1,
      ])))
      .setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(new Float32Array(uv)))
      .setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint16Array([0, 1, 2, 0, 2, 3])))
      .setMaterial(material);
    const node = doc.createNode(`${name}-${side < 0 ? 'port' : 'starboard'}`)
      .setMesh(doc.createMesh(`${name}-${side < 0 ? 'port' : 'starboard'}`).addPrimitive(prim));
    if (decalParent) decalParent.addChild(node);
    else root.getDefaultScene().addChild(node);
  }
}

function addTailDecals() {
  for (const side of [-1, 1]) {
    const prim = doc.createPrimitive()
      .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(new Float32Array([
        side * 0.0115, 0.865, 0.095, side * 0.0115, 0.705, 0.095,
        side * 0.0070, 0.810, 0.215, side * 0.0070, 0.905, 0.215,
      ])))
      .setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(new Float32Array([
        0, 1, 1, 1, 1, 0, 0, 0,
      ])))
      .setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint16Array([0, 1, 2, 0, 2, 3])))
      .setMaterial(tailMat);
    const node = doc.createNode(`CX-tail-mark-${side < 0 ? 'port' : 'starboard'}`)
      .setMesh(doc.createMesh(`CX-tail-mark-${side < 0 ? 'port' : 'starboard'}`).addPrimitive(prim));
    if (decalParent) decalParent.addChild(node);
    else root.getDefaultScene().addChild(node);
  }
}

// y decreases towards the nose. Brushwing UVs keep their pointed end forward;
// only the wordmark flips on the far side so its letters remain readable.
addSideDecals('CX-wordmark', 0.0845, -0.27, -0.62, -0.050, -0.020, wordMat, true);
addSideDecals('CX-nose-mark', 0.0825, -0.70, -0.785, -0.090, -0.012, greenMarkMat);
addSideDecals('CX-windows', 0.0840, 0.58, -0.67, -0.073, -0.057, windowMat, true);
addTailDecals();

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
