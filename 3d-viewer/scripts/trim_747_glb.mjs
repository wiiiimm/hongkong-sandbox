// Build the fly-mode 747-400 GLB (3d-viewer/data/models/plane-747.glb) — HKS-110.
//
// Source: "Air France Boeing 747-400" by zairiqzairiq (Sketchfab, CC BY 4.0 —
// commercial OK; provenance ../data/models/README.md). 80 039 tris, a SketchUp
// -style export: untextured white hull + silver wings, REAL extended landing
// gear (twin-wheel nose strut + the -400's four main posts: two wing and two
// body bogies), geometry cabin/cockpit windows, and the Air France identity
// carried on floating decal plates with dedicated textures (AIRFRANCE titles,
// the striped tail plate, SkyTeam / AF-KLM / engine-seahorse logos).
//
// This replaces the rd.palaciosdeleon26 "Boeing 747-100": user preference for
// the correct classic-Cathay variant (-400) and the higher-fidelity airframe.
//
// What this script does (the 777 recipe, adapted to decal-based livery):
//   1. GEAR SPLIT — connected components (union-find over indices) whose world
//      bbox falls entirely inside the nose-gear box (z −14.6…−13.55) or the
//      main-gear box (x 10.85…16.25, z −26.75…−23.80; the four posts) move to
//      a "CXGear" material. loadPlaneModel() tags CXGear meshes and stepFlight
//      hides them airborne (HKS-110 fleet rule). Axes as authored: fuselage
//      along Z, NOSE at +Z (loader yaws π), up +Y; wheels reach y −0.087,
//      belly starts y 0.80, so the gear-down stance survives the waterline fit.
//   2. LIVERY REPAINT — no atlas here; the identity lives on decal textures:
//      • Air_France_Tail1 (the full fin plate, both sides, one shared UV
//        mapping) is repainted jade #00655B with the complete white brushwing
//        SVG, placed via a least-squares (u,v)→(z,y) fit sampled from the
//        plate's own vertices — the art is authored in WORLD units.
//      • Air_France_Logo1 (the title decal band, z −23.1…−13.9, y 2.67…3.40)
//        maps DIFFERENT texels to each side (per-side u↔z fits of opposite
//        sign), so the starboard prims are split onto a cloned material with
//        an independent texture; each side is painted hull-white with the jade
//        brushwing just aft of the cockpit and the serif CATHAY PACIFIC
//        wordmark behind it, world-anchored per side and u-flipped per side
//        so the lettering reads nose-first from either view (verified in the
//        CPU-raster previews — both prior fleet repaints shipped mirrored
//        text on one side first).
//      • SkyTeam / Air-France-KLM / engine-seahorse logo decal plates are
//        deleted outright (they float above the skin — no holes left behind).
//      • Winglet tips: the -400's canted winglets are welded into the big
//        hull component, so the blades are painted by TRIANGLE test (all
//        three verts inside the winglet boxes) onto a jade material — the
//        same jade-winglet touch as the reference A350.
//      Cabin windows and cockpit glass are real dark GEOMETRY on this model,
//      so the repaint never eats them.
//   3. BUDGET — light only (the source is near budget and the silhouette is
//      the point): weld + meshopt-simplify 80 k → ~60 k tris, then the shared
//      recipe: dedup/prune/quantize (POSITION stays float32 — three r160
//      reads quantized attributes raw), metallic/roughness clamps, textures
//      ≤1024 px JPEG.
//
// Nose faces +Z → loadPlaneModel() yaws 180° (cfg.rotY: Math.PI).
//
// Usage:
//   npm i @gltf-transform/core@4 @gltf-transform/extensions@4 @gltf-transform/functions@4 meshoptimizer sharp
//   node trim_747_glb.mjs <scene.gltf> <output.glb> [ratio]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, flatten, join, prune, quantize, simplify, textureCompress, weld } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';

const [input, output, ratioArg] = process.argv.slice(2);
if (!input || !output) { console.error('usage: node trim_747_glb.mjs <scene.gltf> <output.glb> [ratio]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();
const assetPath = name => fileURLToPath(new URL(`./assets/${name}`, import.meta.url));
for (const anim of root.listAnimations()) {               // none authored, but keep the recipe defensive
  for (const c of anim.listChannels()) c.dispose();
  for (const s of anim.listSamplers()) s.dispose();
  anim.dispose();
}

// ---- helpers (shared with trim_777_glb.mjs) ---------------------------------
const xf = (wm, x, y, z) => [
  wm[0] * x + wm[4] * y + wm[8] * z + wm[12],
  wm[1] * x + wm[5] * y + wm[9] * z + wm[13],
  wm[2] * x + wm[6] * y + wm[10] * z + wm[14]];
function components(prim) {
  const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
  const n = pos.getCount(), ia = idx.getArray();
  const parent = new Uint32Array(n).map((_, i) => i);
  const find = v => { while (parent[v] !== v) v = parent[v] = parent[parent[v]]; return v; };
  for (let i = 0; i < ia.length; i += 3) { const a = find(ia[i]); parent[find(ia[i + 1])] = a; parent[find(ia[i + 2])] = a; }
  return { find, ia, n, pos };
}
function componentBoxes(prim, wm) {
  const { find, ia, n, pos } = components(prim);
  const box = new Map(); const el = [];
  for (let v = 0; v < n; v++) {
    pos.getElement(v, el);
    const [wx, wy, wz] = xf(wm, el[0], el[1], el[2]);
    const r = find(v);
    let b = box.get(r);
    if (!b) box.set(r, b = { minX: 1 / 0, maxX: -1 / 0, minY: 1 / 0, maxY: -1 / 0, minZ: 1 / 0, maxZ: -1 / 0 });
    b.minX = Math.min(b.minX, wx); b.maxX = Math.max(b.maxX, wx);
    b.minY = Math.min(b.minY, wy); b.maxY = Math.max(b.maxY, wy);
    b.minZ = Math.min(b.minZ, wz); b.maxZ = Math.max(b.maxZ, wz);
  }
  return { find, ia, box };
}
const matName = prim => prim.getMaterial()?.getName() || '';
const CX = 13.567;                                        // fuselage centreline (world x)

// ---- 1. gear split (world coords; wheels reach y −0.087, belly starts 0.80) --
// Nose gear z −14.50…−13.69; the four main posts (wing pair z ≈ −25.0…−23.9,
// body pair z ≈ −26.6…−25.5) sit inside x 10.98…16.14 — inboard of the engine
// cowls (x ≲ 9.5 / ≳ 18) whose bottoms also dip low.
const GEAR_BOXES = [
  { x: [10.85, 16.25], y: [-0.12, 1.68], z: [-26.75, -23.80] },  // 4-post main gear + struts + doors
  { x: [13.10, 14.00], y: [-0.12, 1.45], z: [-14.60, -13.55] },  // nose gear + doors
];
const srgb = c => Math.pow((c / 255 + 0.055) / 1.055, 2.4);
const gearMat = doc.createMaterial('CXGear')
  .setBaseColorFactor([srgb(0x55), srgb(0x57), srgb(0x59), 1])
  .setRoughnessFactor(0.7).setMetallicFactor(0.1);
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const wm = node.getWorldMatrix();
  for (const prim of [...mesh.listPrimitives()]) {
    if (!prim.getIndices() || !prim.getAttribute('POSITION')) continue;
    const { find, ia, box } = componentBoxes(prim, wm);
    const isGear = new Set();
    for (const [r, b] of box)
      if (GEAR_BOXES.some(G =>
        b.minX >= G.x[0] && b.maxX <= G.x[1] &&
        b.minY >= G.y[0] && b.maxY <= G.y[1] &&
        b.minZ >= G.z[0] && b.maxZ <= G.z[1])) isGear.add(r);
    if (!isGear.size) continue;
    const gearTris = [], bodyTris = [];
    for (let i = 0; i < ia.length; i += 3)
      (isGear.has(find(ia[i])) ? gearTris : bodyTris).push(ia[i], ia[i + 1], ia[i + 2]);
    if (!bodyTris.length) { prim.setMaterial(gearMat); continue; }   // whole prim is gear
    const gp = prim.clone();
    gp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(gearTris)));
    gp.setMaterial(gearMat);
    mesh.addPrimitive(gp);
    prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(bodyTris)));
  }
}

// ---- 2a. drop the third-party logo decal plates -----------------------------
const DROP = new Set(['Skyteam_Logo_White1', 'Air_France_KLM_Logo1', 'Engine_Logo1']);
for (const mesh of root.listMeshes())
  for (const prim of [...mesh.listPrimitives()])
    if (DROP.has(matName(prim))) { mesh.removePrimitive(prim); prim.dispose(); }

// ---- 2b. Cathay artwork samplers (shared assets, see assets/README.md) ------
const MARK_W = 512;
const markRaw = await sharp(assetPath('cathay-brushwing.svg'))
  .resize({ width: MARK_W }).ensureAlpha().raw()
  .toBuffer({ resolveWithObject: true });
const wordRaw = await sharp(assetPath('cathay-wordmark.jpg'))
  .extract({ left: 107, top: 80, width: 289, height: 27 })
  .raw().toBuffer({ resolveWithObject: true });
const clamp01 = n => Math.max(0, Math.min(1, n));
const sampleMark = (u, v) => {
  if (u < 0 || u > 1 || v < 0 || v > 1) return 0;
  const x = Math.min(markRaw.info.width - 1, Math.round(u * (markRaw.info.width - 1)));
  const y = Math.min(markRaw.info.height - 1, Math.round((1 - v) * (markRaw.info.height - 1)));
  return markRaw.data[(y * markRaw.info.width + x) * markRaw.info.channels + 3] / 255;
};
const sampleWordmark = (u, v) => {
  if (u < 0 || u > 1 || v < 0 || v > 1) return 0;
  const x = Math.min(wordRaw.info.width - 1, Math.round(u * (wordRaw.info.width - 1)));
  const y = Math.min(wordRaw.info.height - 1, Math.round((1 - v) * (wordRaw.info.height - 1)));
  const i = (y * wordRaw.info.width + x) * wordRaw.info.channels;
  const r = wordRaw.data[i], g = wordRaw.data[i + 1], b = wordRaw.data[i + 2];
  return clamp01((Math.min(g, b) - r - 3) / 48);        // teal chroma beats a luminance threshold
};
const JADE = [0x00, 0x65, 0x5b], WHITE = [0xff, 0xff, 0xff];   // pure white — must match the untextured hull
const blend = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * clamp01(t)));

// Per-material least-squares (u,v)→(z,y) fits, one per fuselage side. The
// decals are flat plates riding the skin, so a linear fit per side is exact to
// within the plate's curvature (<0.01 uv).
function sideFits(materialName) {
  const acc = { port: [], stbd: [] };
  for (const node of root.listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const wm = node.getWorldMatrix();
    for (const prim of mesh.listPrimitives()) {
      if (matName(prim) !== materialName) continue;
      const pos = prim.getAttribute('POSITION'), uv = prim.getAttribute('TEXCOORD_0');
      if (!pos || !uv) continue;
      const e = [], t = [];
      for (let v = 0; v < pos.getCount(); v++) {
        pos.getElement(v, e); uv.getElement(v, t);
        const [wx, wy, wz] = xf(wm, e[0], e[1], e[2]);
        acc[wx < CX ? 'port' : 'stbd'].push([t[0], t[1], wz, wy]);
      }
    }
  }
  const fit = (pts, K, W) => {                            // least squares K = a*W + b
    let n = pts.length, sk = 0, sw = 0, skw = 0, sww = 0;
    for (const p of pts) { sk += p[K]; sw += p[W]; skw += p[K] * p[W]; sww += p[W] * p[W]; }
    const a = (n * skw - sk * sw) / (n * sww - sw * sw);
    return [a, (sk - a * sw) / n];
  };
  const out = {};
  for (const [s, pts] of Object.entries(acc)) {
    if (!pts.length) continue;
    const [au, bu] = fit(pts, 0, 2), [av, bv] = fit(pts, 1, 3);
    out[s] = { z: u => (u - bu) / au, y: v => (v - bv) / av };
  }
  return out;
}

// ---- 2c. tail plate → jade fin + white brushwing ----------------------------
// Fin plate z −40.28…−33.11, y 3.59…7.99; both sides share one UV mapping
// (identical fits), so a single repaint serves both — the world-space z
// anchoring keeps the stroke sweeping nose-ward on either side.
{
  const tailMat = root.listMaterials().find(m => m.getName() === 'Air_France_Tail1');
  const tex = tailMat.getBaseColorTexture();
  const { port } = sideFits('Air_France_Tail1');
  const meta = await sharp(Buffer.from(tex.getImage())).metadata();
  const TW = meta.width, TH = meta.height;
  const buf = Buffer.alloc(TW * TH * 3);
  const finMark = (z, y) => sampleMark((z + 40.10) / 6.55, (y - 4.35) / 3.30);
  for (let py = 0; py < TH; py++) for (let px = 0; px < TW; px++) {
    const z = port.z((px + 0.5) / TW), y = port.y((py + 0.5) / TH);
    const c = blend(JADE, WHITE, finMark(z, y));
    const i = (py * TW + px) * 3;
    buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2];
  }
  tex.setImage(await sharp(buf, { raw: { width: TW, height: TH, channels: 3 } }).png().toBuffer())
     .setMimeType('image/png');
}

// ---- 2d. title decal → white + jade nose brushwing + CATHAY PACIFIC ---------
// The two sides map opposite-signed u↔z (a shared texture would put a mark
// painted at the port nose at the STARBOARD TAIL), so the starboard prims are
// re-homed onto a cloned material/texture and each side is painted with its
// own fit. Placement (world units; 1 unit ≈ 2.425 m, nose at z −11.1, cockpit
// glass z −13.66…−12.97 / y 3.40…3.63, decal band z −23.1…−13.9 / y 2.67…3.40):
const TITLE_ZF = -15.55, TITLE_ZA = -21.25;               // wordmark fore/aft (≈13.8 m long)
const TITLE_Y0 = 2.84, TITLE_Y1 = 3.36;                   // its cap band, clear of both window rows
const NOSE_Z0 = -14.85, NOSE_Z1 = -14.18;                 // jade brushwing just aft of the cockpit
const NOSE_Y0 = 2.80, NOSE_Y1 = 3.36;
{
  const logoMat = root.listMaterials().find(m => m.getName() === 'Air_France_Logo1');
  const stbdMat = logoMat.clone().setName('CX_Titles_Stbd');
  const stbdTex = doc.createTexture('CX_Titles_Stbd')
    .setImage(logoMat.getBaseColorTexture().getImage())
    .setMimeType(logoMat.getBaseColorTexture().getMimeType());
  stbdMat.setBaseColorTexture(stbdTex);
  for (const node of root.listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const wm = node.getWorldMatrix();
    for (const prim of [...mesh.listPrimitives()]) {
      if (matName(prim) !== 'Air_France_Logo1') continue;
      // triangle-level split: a single prim can carry both sides' plates
      const pos = prim.getAttribute('POSITION'), ia = prim.getIndices().getArray();
      const e = [];
      const sideX = v => { pos.getElement(v, e); return xf(wm, e[0], e[1], e[2])[0]; };
      const portTris = [], stbdTris = [];
      for (let i = 0; i < ia.length; i += 3)
        ((sideX(ia[i]) + sideX(ia[i + 1]) + sideX(ia[i + 2])) / 3 > CX ? stbdTris : portTris)
          .push(ia[i], ia[i + 1], ia[i + 2]);
      if (!stbdTris.length) continue;
      if (!portTris.length) { prim.setMaterial(stbdMat); continue; }
      const sp = prim.clone();
      sp.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(stbdTris)));
      sp.setMaterial(stbdMat);
      mesh.addPrimitive(sp);
      prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(portTris)));
    }
  }
  const fits = sideFits('Air_France_Logo1');              // port prims only now
  fits.stbd = sideFits('CX_Titles_Stbd').stbd;
  // flip: the wordmark's left end must sit nose-ward on both sides (each side
  // is viewed from outboard, nose to the viewer's left) — verified in renders.
  const paint = async (mat, F, flip) => {
    const tex = mat.getBaseColorTexture();
    const meta = await sharp(Buffer.from(tex.getImage())).metadata();
    const TW = meta.width, TH = meta.height;
    const buf = Buffer.alloc(TW * TH * 3);
    for (let py = 0; py < TH; py++) for (let px = 0; px < TW; px++) {
      const z = F.z((px + 0.5) / TW), y = F.y((py + 0.5) / TH);
      const uT = flip ? (TITLE_ZF - z) / (TITLE_ZF - TITLE_ZA) : (z - TITLE_ZA) / (TITLE_ZF - TITLE_ZA);
      const uN = flip ? (NOSE_Z0 - z) / (NOSE_Z0 - NOSE_Z1) : (z - NOSE_Z1) / (NOSE_Z0 - NOSE_Z1);
      const mark = Math.max(
        sampleWordmark(uT, (y - TITLE_Y0) / (TITLE_Y1 - TITLE_Y0)),
        sampleMark(uN, (y - NOSE_Y0) / (NOSE_Y1 - NOSE_Y0)));
      const c = blend(WHITE, JADE, mark);
      const i = (py * TW + px) * 3;
      buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2];
    }
    tex.setImage(await sharp(buf, { raw: { width: TW, height: TH, channels: 3 } }).png().toBuffer())
       .setMimeType('image/png');
  };
  await paint(logoMat, fits.port, false);
  await paint(stbdMat, fits.stbd, true);
}

// (No winglet treatment: despite the -400 title this hull carries NO winglet
// blades — the wingtips top out at y 3.36, tip-light housings only — so the
// A350-style jade winglet touch has nothing to land on.)

// Untextured materials (most of the airframe) don't need UVs, but the export
// ships float32 TEXCOORD_0 everywhere — and its out-of-[0,1] values also make
// quantize() skip the channel. Dropping the dead UVs saves ~8 B/vertex and
// lets weld() merge vertices the stray UVs would otherwise split.
for (const mesh of root.listMeshes())
  for (const prim of mesh.listPrimitives())
    if (!prim.getMaterial()?.getBaseColorTexture())
      for (const sem of prim.listSemantics())
        if (sem.startsWith('TEXCOORD')) prim.setAttribute(sem, null);

// ---- 3. budget (light — the source is near target) ---------------------------
// flatten+join first: this SketchUp export ships 348 nodes / 133 meshes whose
// per-prim accessor overhead alone costs ~0.9 MB; joining also lets weld and
// simplify work across the old part boundaries.
const ratio = Number(ratioArg) || 0.80;
await doc.transform(flatten(), join(), weld(), simplify({ simplifier: MeshoptSimplifier, ratio, error: 0.002 }));
// material sanity: clamp defensively like the rest of the fleet
for (const m of root.listMaterials()) {
  if (m.getMetallicFactor() > 0.2) m.setMetallicFactor(0.15);
  if (m.getRoughnessFactor() < 0.4) m.setRoughnessFactor(0.5);
}
await doc.transform(
  dedup(), prune(),
  quantize({ pattern: /^(?!POSITION).*$/, quantizeNormal: 8 }),
  textureCompress({ encoder: sharp, resize: [1024, 1024], targetFormat: 'jpeg', quality: 80 }),
);

let tris = 0, gear = 0;
for (const mesh of root.listMeshes())
  for (const p of mesh.listPrimitives()) {
    const t = (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3;
    tris += t;
    if (p.getMaterial()?.getName() === 'CXGear') gear += t;
  }
await io.write(output, doc);
console.log('wrote', output, '—', Math.round(tris), 'tris (', Math.round(gear), 'gear )');
