// Throwaway CPU rasteriser: orthographic z-buffer render of a GLB, textured
// (baseColor texture or factor), lambert-ish shading. No GPU / SwiftShader.
// usage: node render_glb_preview.tmp.mjs <in.glb> <out.png> <yawDeg> [pitchDeg]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import sharp from 'sharp';

const [input, output, yawArg, pitchArg] = process.argv.slice(2);
const yaw = (Number(yawArg) || 0) * Math.PI / 180;
const pitch = (Number(pitchArg) || 0) * Math.PI / 180;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(input);
const root = doc.getRoot();

// decode textures once
const texPix = new Map();
for (const t of root.listTextures()) {
  const r = await sharp(Buffer.from(t.getImage())).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  texPix.set(t, r);
}
const xf = (m, x, y, z) => [
  m[0] * x + m[4] * y + m[8] * z + m[12],
  m[1] * x + m[5] * y + m[9] * z + m[13],
  m[2] * x + m[6] * y + m[10] * z + m[14]];
const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
const view = ([x, y, z]) => {
  const vx = x * cy + z * sy, vz = -x * sy + z * cy;
  return [vx, y * cp - vz * sp, y * sp + vz * cp];      // screen x, screen y(up), depth
};
// gather verts
const tris = [];
let min = [1e9, 1e9], max = [-1e9, -1e9];
for (const node of root.listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const wm = node.getWorldMatrix();
  for (const prim of mesh.listPrimitives()) {
    const pos = prim.getAttribute('POSITION');
    if (!pos) continue;
    const uv = prim.getAttribute('TEXCOORD_0');
    const idx = prim.getIndices();
    const ia = idx ? idx.getArray() : [...Array(pos.getCount()).keys()];
    const mat = prim.getMaterial();
    const bcf = mat?.getBaseColorFactor() || [1, 1, 1, 1];
    const t = mat?.getBaseColorTexture();
    const px = t ? texPix.get(t) : null;
    const el = [];
    for (let i = 0; i < ia.length; i += 3) {
      const V = [], U = [];
      for (let j = 0; j < 3; j++) {
        pos.getElement(ia[i + j], el);
        const v = view(xf(wm, el[0], el[1], el[2]));
        V.push(v);
        min[0] = Math.min(min[0], v[0]); max[0] = Math.max(max[0], v[0]);
        min[1] = Math.min(min[1], v[1]); max[1] = Math.max(max[1], v[1]);
        if (uv) { const e = []; uv.getElement(ia[i + j], e); U.push(e); }
      }
      tris.push({ V, U: uv ? U : null, px, bcf });
    }
  }
}
const W = 1600;
const scale = (W - 80) / Math.max(max[0] - min[0], 1e-6);
const H = Math.ceil((max[1] - min[1]) * scale) + 80;
const img = new Uint8ClampedArray(W * H * 3).fill(235);
const zbuf = new Float32Array(W * H).fill(-1e9);
const sx = v => 40 + (v[0] - min[0]) * scale;
const syc = v => H - 40 - (v[1] - min[1]) * scale;
const srgb2lin = c => Math.pow(c, 2.2), lin2srgb = c => Math.pow(c, 1 / 2.2);
for (const { V, U, px, bcf } of tris) {
  const P = V.map(v => [sx(v), syc(v)]);
  const minx = Math.max(0, Math.floor(Math.min(P[0][0], P[1][0], P[2][0]))), maxx = Math.min(W - 1, Math.ceil(Math.max(P[0][0], P[1][0], P[2][0])));
  const miny = Math.max(0, Math.floor(Math.min(P[0][1], P[1][1], P[2][1]))), maxy = Math.min(H - 1, Math.ceil(Math.max(P[0][1], P[1][1], P[2][1])));
  const [A, B, C] = P, den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1]);
  if (!den) continue;
  // face normal in view space for shading
  const e1 = [V[1][0] - V[0][0], V[1][1] - V[0][1], V[1][2] - V[0][2]];
  const e2 = [V[2][0] - V[0][0], V[2][1] - V[0][1], V[2][2] - V[0][2]];
  let nx = e1[1] * e2[2] - e1[2] * e2[1], ny = e1[2] * e2[0] - e1[0] * e2[2], nz = e1[0] * e2[1] - e1[1] * e2[0];
  const nl = Math.hypot(nx, ny, nz) || 1;
  const light = 0.55 + 0.45 * Math.abs((ny * 0.6 + nz * 0.8) / nl);
  for (let y = miny; y <= maxy; y++) for (let x = minx; x <= maxx; x++) {
    const w1 = ((B[1] - C[1]) * (x - C[0]) + (C[0] - B[0]) * (y - C[1])) / den,
          w2 = ((C[1] - A[1]) * (x - C[0]) + (A[0] - C[0]) * (y - C[1])) / den, w3 = 1 - w1 - w2;
    if (w1 < 0 || w2 < 0 || w3 < 0) continue;
    const depth = w1 * V[0][2] + w2 * V[1][2] + w3 * V[2][2];
    const p = y * W + x;
    if (depth <= zbuf[p]) continue;
    zbuf[p] = depth;
    let r = bcf[0], g = bcf[1], b = bcf[2];   // linear
    if (px && U) {
      let u = w1 * U[0][0] + w2 * U[1][0] + w3 * U[2][0];
      let v = w1 * U[0][1] + w2 * U[1][1] + w3 * U[2][1];
      u -= Math.floor(u); v -= Math.floor(v);
      const tx = Math.min(px.info.width - 1, Math.round(u * (px.info.width - 1)));
      const ty = Math.min(px.info.height - 1, Math.round(v * (px.info.height - 1)));
      const ti = (ty * px.info.width + tx) * px.info.channels;
      r *= srgb2lin(px.data[ti] / 255); g *= srgb2lin(px.data[ti + 1] / 255); b *= srgb2lin(px.data[ti + 2] / 255);
    }
    img[p * 3] = 255 * lin2srgb(r * light);
    img[p * 3 + 1] = 255 * lin2srgb(g * light);
    img[p * 3 + 2] = 255 * lin2srgb(b * light);
  }
}
await sharp(Buffer.from(img.buffer), { raw: { width: W, height: H, channels: 3 } }).png().toFile(output);
console.log('wrote', output, `${W}x${H}`);
