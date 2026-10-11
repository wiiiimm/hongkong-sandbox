/** Full precision, order-preserving bufferView encoding; no geometry transforms. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync, gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { createInterface } from 'node:readline';
import { MeshoptEncoder } from 'meshoptimizer';
// Independent decode uses the exact module shipped with the viewer.
import { MeshoptDecoder } from '../../../3d-viewer/vendor/meshopt_decoder.module.js';

const EXT = 'EXT_meshopt_compression';
export const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const widths = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };
const sizes = { 5121: 1, 5123: 2, 5125: 4, 5126: 4 };

export function parseGLB(bytes) {
  assert.equal(bytes.readUInt32LE(0), 0x46546c67, 'GLB magic');
  assert.equal(bytes.readUInt32LE(4), 2, 'GLB version');
  assert.equal(bytes.readUInt32LE(8), bytes.length, 'GLB length');
  const n = bytes.readUInt32LE(12);
  assert.equal(n % 4, 0);
  assert.equal(bytes.readUInt32LE(16), 0x4e4f534a);
  const json = JSON.parse(bytes.subarray(20, 20 + n).toString());
  const offset = 20 + n;
  assert.equal(bytes.readUInt32LE(offset + 4), 0x004e4942);
  const bin = bytes.subarray(offset + 8);
  assert.equal(bin.length, bytes.readUInt32LE(offset));
  return { json, bin };
}

export function makeGLB(json, bin) {
  const raw = Buffer.from(JSON.stringify(json));
  const padded = Buffer.alloc(Math.ceil(raw.length / 4) * 4, 32);
  raw.copy(padded);
  const data = Buffer.alloc(Math.ceil(bin.length / 4) * 4);
  bin.copy(data);
  const header = Buffer.alloc(20);
  header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4);
  header.writeUInt32LE(28 + padded.length + data.length, 8);
  header.writeUInt32LE(padded.length, 12); header.writeUInt32LE(0x4e4f534a, 16);
  const binaryHeader = Buffer.alloc(8);
  binaryHeader.writeUInt32LE(data.length); binaryHeader.writeUInt32LE(0x004e4942, 4);
  return Buffer.concat([header, padded, binaryHeader, data]);
}

function validateSource({ json: j, bin }) {
  assert.equal(j.buffers.length, 1, 'one embedded source buffer required');
  assert.ok(!j.buffers[0].uri && j.buffers[0].byteLength <= bin.length);
  assert.ok(!j.images?.length && !j.textures?.length, 'geometry-only adapter');
  assert.ok(!j.animations?.length && !j.skins?.length, 'static source only');
  assert.ok(!j.extensionsUsed?.length && !j.extensionsRequired?.length, 'unencoded source required');
  for (const a of j.accessors) {
    assert.ok(!a.sparse && Number.isInteger(a.bufferView), 'dense accessors required');
    assert.ok(widths[a.type] && sizes[a.componentType], 'supported accessor format');
    const v = j.bufferViews[a.bufferView];
    const element = widths[a.type] * sizes[a.componentType];
    const stride = v.byteStride ?? element;
    assert.ok(a.count > 0 && stride >= element);
    assert.ok((a.byteOffset ?? 0) + (a.count - 1) * stride + element <= v.byteLength);
    if (a.componentType === 5126) {
      for (let i = 0; i < a.count; i++) for (let k = 0; k < widths[a.type]; k++) {
        assert.ok(Number.isFinite(bin.readFloatLE((v.byteOffset ?? 0) + (a.byteOffset ?? 0) + i * stride + k * 4)), 'finite attribute');
      }
    }
  }
  for (const n of j.nodes ?? []) for (const key of ['matrix', 'translation', 'rotation', 'scale']) {
    assert.ok(!n[key] || n[key].every(Number.isFinite), 'finite source transform');
  }
  for (const mesh of j.meshes) for (const p of mesh.primitives) {
    assert.equal(p.mode ?? 4, 4, 'triangle source required');
    assert.ok(!p.targets?.length, 'no morph target processing');
    const vertices = j.accessors[p.attributes.POSITION].count;
    if (p.indices === undefined) { assert.equal(vertices % 3, 0); continue; }
    const a = j.accessors[p.indices];
    assert.equal(a.type, 'SCALAR'); assert.ok([5123, 5125].includes(a.componentType));
    assert.equal(a.count % 3, 0);
    const v = j.bufferViews[a.bufferView], size = sizes[a.componentType];
    for (let i = 0; i < a.count; i++) {
      const off = (v.byteOffset ?? 0) + (a.byteOffset ?? 0) + i * size;
      assert.ok(bin.readUIntLE(off, size) < vertices, 'index within POSITION accessor');
    }
  }
  for (const v of j.bufferViews) {
    assert.equal(v.buffer, 0); assert.ok(!v.extensions);
    assert.ok(v.byteLength > 0 && (v.byteOffset ?? 0) + v.byteLength <= j.buffers[0].byteLength);
  }
}

export async function encodeExact(sourceBytes) {
  await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
  const source = parseGLB(sourceBytes);
  validateSource(source);
  const j = structuredClone(source.json);
  const pieces = [];
  let offset = 0;
  const start = performance.now();
  for (let index = 0; index < j.bufferViews.length; index++) {
    const view = j.bufferViews[index];
    const accessors = j.accessors.filter(a => a.bufferView === index);
    assert.ok(accessors.length, 'unreferenced source view is unsupported');
    const indices = view.target === 34963 || j.meshes.some(m => m.primitives.some(p => p.indices !== undefined && j.accessors[p.indices].bufferView === index));
    const stride = indices ? sizes[accessors[0].componentType] : (view.byteStride ?? widths[accessors[0].type] * sizes[accessors[0].componentType]);
    assert.ok(indices ? [2, 4].includes(stride) : (stride % 4 === 0 && stride <= 256));
    assert.ok(!indices || accessors.every(a => a.type === 'SCALAR' && sizes[a.componentType] === stride));
    assert.equal(view.byteLength % stride, 0, 'exact view layout required');
    const raw = source.bin.subarray(view.byteOffset ?? 0, (view.byteOffset ?? 0) + view.byteLength);
    // INDICES preserves even degenerate faces and the exact corner sequence.
    const mode = indices ? 'INDICES' : 'ATTRIBUTES';
    const count = raw.length / stride;
    const encoded = Buffer.from(MeshoptEncoder.encodeGltfBuffer(raw, count, stride, mode));
    const padding = Buffer.alloc((4 - offset % 4) % 4);
    pieces.push(padding, encoded); offset += padding.length;
    view.buffer = 1;
    view.extensions = { [EXT]: { buffer: 0, byteOffset: offset, byteLength: encoded.length, byteStride: stride, count, mode, filter: 'NONE' } };
    offset += encoded.length;
  }
  const encodeMs = performance.now() - start;
  j.buffers = [{ byteLength: offset }, { byteLength: source.json.buffers[0].byteLength, extensions: { [EXT]: { fallback: true } } }];
  j.extensionsUsed = [EXT]; j.extensionsRequired = [EXT];
  const glb = makeGLB(j, Buffer.concat(pieces));
  const decodeStart = performance.now();
  const verified = await verifyExact(sourceBytes, glb);
  return { glb, metrics: { ...verified, encodeMs, roundtripVerificationMs: performance.now() - decodeStart } };
}

export async function verifyExact(sourceBytes, outputBytes) {
  await MeshoptDecoder.ready;
  const source = parseGLB(sourceBytes), output = parseGLB(outputBytes);
  assert.deepEqual(output.json.extensionsRequired, [EXT]);
  assert.deepEqual(output.json.extensionsUsed, [EXT]);
  assert.equal(output.json.buffers.length, 2);
  assert.deepEqual(output.json.buffers[1], { byteLength: source.json.buffers[0].byteLength, extensions: { [EXT]: { fallback: true } } });
  assert.equal(output.json.buffers[0].byteLength <= output.bin.length, true);
  const restored = structuredClone(output.json);
  let decodedBytes = 0;
  let codecDecodeMs = 0;
  const viewHashes = [];
  for (let i = 0; i < restored.bufferViews.length; i++) {
    const v = restored.bufferViews[i], e = v.extensions[EXT];
    assert.equal(e.filter, 'NONE'); assert.ok(['ATTRIBUTES', 'INDICES'].includes(e.mode));
    assert.equal(e.buffer, 0); assert.equal(e.count * e.byteStride, v.byteLength);
    assert.ok(e.byteOffset + e.byteLength <= output.json.buffers[0].byteLength);
    const data = Buffer.alloc(v.byteLength);
    const started = performance.now();
    MeshoptDecoder.decodeGltfBuffer(data, e.count, e.byteStride, output.bin.subarray(e.byteOffset, e.byteOffset + e.byteLength), e.mode, e.filter);
    codecDecodeMs += performance.now() - started;
    const original = source.json.bufferViews[i];
    assert.deepEqual(data, source.bin.subarray(original.byteOffset ?? 0, (original.byteOffset ?? 0) + original.byteLength), `exact bufferView ${i}`);
    viewHashes.push(sha(data)); decodedBytes += data.length;
    v.buffer = 0; delete v.extensions;
  }
  restored.buffers = source.json.buffers; delete restored.extensionsUsed; delete restored.extensionsRequired;
  assert.deepEqual(restored, source.json, 'all source metadata and transforms unchanged');
  const vertices = source.json.meshes.reduce((n,m) => n + m.primitives.reduce((n,p) => n + source.json.accessors[p.attributes.POSITION].count, 0), 0);
  const triangles = source.json.meshes.reduce((n,m) => n + m.primitives.reduce((n,p) => n + source.json.accessors[p.indices ?? p.attributes.POSITION].count / 3, 0), 0);
  return { exactBufferViewSha256: viewHashes, decodedAccessorBytes: decodedBytes, vertices, triangles, codecDecodeMs, maxAttributeError: 0, worldPlacementErrorMetres: 0, indexOrderPreserved: true, sourceMetadataPreserved: true };
}

async function processRequest(request) {
  const bytes = readFileSync(request.source);
  assert.equal(sha(bytes), request.sourceSha256, 'source hash');
  const started = performance.now();
  const native = gunzipSync(bytes);
  const { glb, metrics } = await encodeExact(native);
  const output = gzipSync(glb, { level: 9, mtime: 0 });
  const hash = sha(output), path = resolve(request.artifactDirectory, `${hash}.glb.gz`);
  mkdirSync(dirname(path), { recursive: true });
  if (existsSync(path)) assert.equal(sha(readFileSync(path)), hash);
  else writeFileSync(path, output, { flag: 'wx' });
  const readback = readFileSync(path);
  assert.equal(sha(readback), hash);
  await verifyExact(native, gunzipSync(readback));
  return { artifact: { path, sha256: hash }, metrics: {
    ...metrics, originalDownloadBytes: bytes.length, downloadBytes: output.length,
    originalGLBBytes: native.length, glbBytes: glb.length,
    savedBytes: bytes.length - output.length, beneficial: output.length < bytes.length,
    compressionRatio: output.length / bytes.length, processingMs: performance.now() - started,
    codec: 'meshopt', codecVersion: '0.24.0', transportEncoding: 'gzip',
    residentGeometryBytesEstimate: metrics.decodedAccessorBytes,
    residentMethod: 'sum of unchanged bufferView byteLengths; excludes JS, decoder, GPU overhead and temporary peaks',
    peakMemoryBytes: null, deviceFrameTimeMs: null,
    timingEnvironment: { node: process.versions.node, platform: process.platform, architecture: process.arch, decoderSupported: MeshoptDecoder.supported, wasmSIMD: null }
  } };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  for await (const line of createInterface({ input: process.stdin })) {
    try { process.stdout.write(JSON.stringify({ ok: true, ...await processRequest(JSON.parse(line)) }) + '\n'); }
    catch (error) { process.stdout.write(JSON.stringify({ ok: false, error: error.message.slice(0, 600) }) + '\n'); }
  }
}
