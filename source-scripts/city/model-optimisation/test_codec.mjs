import test from 'node:test';
import assert from 'node:assert/strict';
import { makeGLB, encodeExact, verifyExact, parseGLB } from './codec.mjs';

function fixture(indexType = 5123) {
  const positions = Buffer.alloc(48);
  [0,0,0, 1,0,0, 0,1,0, 2,2,2].forEach((v,i) => positions.writeFloatLE(v,i*4));
  const indices = Buffer.alloc(indexType === 5123 ? 12 : 24);
  // An ordinary face, repeated-position zero-area face, and unused vertex.
  [2,0,1, 0,0,0].forEach((v,i) => indices.writeUIntLE(v,i*(indexType===5123?2:4),indexType===5123?2:4));
  const bin = Buffer.concat([positions,indices]);
  const json = { asset:{version:'2.0'}, buffers:[{byteLength:bin.length}],
    bufferViews:[{buffer:0,byteOffset:0,byteLength:48,target:34962},{buffer:0,byteOffset:48,byteLength:indices.length,target:34963}],
    accessors:[{bufferView:0,componentType:5126,type:'VEC3',count:4,min:[0,0,0],max:[2,2,2]},{bufferView:1,componentType:indexType,type:'SCALAR',count:6}],
    meshes:[{primitives:[{attributes:{POSITION:0},indices:1,mode:4,material:0}]}],
    materials:[{pbrMetallicRoughness:{baseColorFactor:[0.2,0.4,0.6,1]}}],
    nodes:[{mesh:0,matrix:[1,0,0,0,0,0,-1,0,0,1,0,0,834500,10,-816500,1]}],scenes:[{nodes:[0]}],scene:0 };
  return makeGLB(json, bin);
}
for (const type of [5123,5125]) test(`exact indices ${type}, degenerate faces, unused vertices and surveyed matrix`, async () => {
  const input=fixture(type), {glb,metrics}=await encodeExact(input);
  assert.equal(metrics.triangles,2);assert.equal(metrics.vertices,4);
  assert.equal(metrics.worldPlacementErrorMetres,0);
  await verifyExact(input,glb);
});
test('detect damaged encoded bytes and altered source transforms', async () => {
  const input=fixture(), {glb}=await encodeExact(input);
  const parsed=parseGLB(glb);parsed.json.nodes[0].matrix[13]+=1;
  await assert.rejects(verifyExact(input,makeGLB(parsed.json,parsed.bin)), /metadata/);
  const corrupt=Buffer.from(parsed.bin);corrupt[parsed.json.bufferViews[0].extensions.EXT_meshopt_compression.byteOffset]^=127;
  parsed.json.nodes[0].matrix[13]-=1;
  await assert.rejects(verifyExact(input,makeGLB(parsed.json,corrupt)));
});
test('reject nonfinite attributes and external/textured sources', async () => {
  const input=fixture(), {json,bin}=parseGLB(input);
  const bad=Buffer.from(bin);bad.writeFloatLE(NaN,0);
  await assert.rejects(encodeExact(makeGLB(json,bad)), /finite/);
  json.images=[{uri:'texture.png'}];
  await assert.rejects(encodeExact(makeGLB(json,bin)), /geometry-only/);
});
