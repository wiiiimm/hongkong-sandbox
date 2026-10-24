import test from 'node:test';
import assert from 'node:assert/strict';
import { makeGLB, parseGLB, encodeExact } from './codec.mjs';
import { deriveLossy, verifyLossy, preserveSmallFaces } from './lossy_codec.mjs';

const parameters=(simplification=false)=>({adapter:'meshopt-bounded-lossy-v2',quantisation:true,
  positionErrorMetres:0.02,simplification,triangleRatio:simplification?0.35:1,
  simplificationErrorMetres:simplification?0.2:0,attributeBits:10,
  lockBorders:true,pinPositionExtrema:true,preventQuantisationFaceCollapseAndFlip:true,geometryCodec:'meshopt',transportEncoding:'gzip',gzipLevel:9});
function fixture() {
  const positions=[];for(let y=0;y<8;y++) for(let x=0;x<8;x++) positions.push(x*0.1234,y*0.1234,Math.sin(x+y)*0.0323);
  positions.push(0.4567,0.4567,0.0123); // An unused original vertex.
  const indices=[];for(let y=0;y<7;y++) for(let x=0;x<7;x++) {const a=y*8+x;indices.push(a,a+1,a+8,a+1,a+9,a+8);}
  indices.push(0,0,0); // A genuine source degenerate, retained by high.
  const count=positions.length/3,data=[positions,Array(count).fill([0.2,0.3,0.9]).flat(),Array(count).fill([0.234123,0.41234,0.82341]).flat()];
  let offset=0;const views=[],accessors=[],pieces=[];
  for(const values of data) {const bytes=Buffer.alloc(values.length*4);values.forEach((v,i)=>bytes.writeFloatLE(v,i*4));
    views.push({buffer:0,byteOffset:offset,byteLength:bytes.length,target:34962});
    accessors.push({bufferView:views.length-1,componentType:5126,type:'VEC3',count});offset+=bytes.length;pieces.push(bytes);}
  const indexBytes=Buffer.alloc(indices.length*4);indices.forEach((v,i)=>indexBytes.writeUInt32LE(v,i*4));
  views.push({buffer:0,byteOffset:offset,byteLength:indexBytes.length,target:34963});
  accessors.push({bufferView:3,componentType:5125,type:'SCALAR',count:indices.length});pieces.push(indexBytes);
  const bin=Buffer.concat(pieces);
  return makeGLB({asset:{version:'2.0'},buffers:[{byteLength:bin.length}],bufferViews:views,accessors,
    meshes:[{primitives:[{attributes:{POSITION:0,NORMAL:1,COLOR_0:2},indices:3,material:0}]}],
    materials:[{pbrMetallicRoughness:{baseColorFactor:[1,1,1,1]}}],
    nodes:[{matrix:[2,0,0,0,0,0,-1,0,0,1,0,0,834500,12,-816500,1],children:[1]},{mesh:0}],scenes:[{nodes:[0]}],scene:0},bin);
}
test('high preserves topology and unused vertices; error is bounded in transformed metres',async()=>{
  const original=fixture(),p=parameters(),d=await deriveLossy(original,p),s=parseGLB(original),o=parseGLB(d.glb);
  assert.equal(d.metrics.originalVertices,d.metrics.vertices);assert.equal(d.metrics.originalTriangles,d.metrics.triangles);
  assert.equal(d.metrics.sourceDegenerateFaces,1);assert.equal(d.metrics.outputDegenerateFaces,1);
  assert.ok(d.metrics.maxPositionQuantisationErrorMetres>0);assert.ok(d.metrics.maxPositionQuantisationErrorMetres<=p.positionErrorMetres);
  assert.deepEqual(o.json.nodes,s.json.nodes);assert.deepEqual(o.json.materials,s.json.materials);
  assert.ok(d.metrics.maxColourComponentError>0);assert.ok(d.metrics.maxLocalNormalAngleDegrees>0);
  const output=await encodeExact(d.glb),verified=await verifyLossy(original,output.glb,p);
  assert.equal(verified.sourceGeometryExact,false);assert.equal(verified.derivedMeshRoundtripExact,true);
});
test('LOD reduces triangles, compacts all attributes and honours estimated error ceiling',async()=>{
  const p=parameters(true),d=await deriveLossy(fixture(),p),j=parseGLB(d.glb).json;
  assert.ok(d.metrics.triangles<d.metrics.originalTriangles);assert.ok(d.metrics.removedVertices>0);
  assert.ok(d.metrics.simplifierEstimatedErrorMetres<=p.simplificationErrorMetres+1e-6);
  const primitive=j.meshes[0].primitives[0];
  assert.ok(Object.values(primitive.attributes).every(index=>j.accessors[index].count===d.metrics.vertices));
  assert.equal(d.metrics.topologyPreserved,false);assert.equal(d.metrics.hausdorffErrorMetres,null);
});
test('reject changed pose, corrupt output, recipe mismatch and nonfinite input',async()=>{
  const original=fixture(),p=parameters(),derived=await deriveLossy(original,p),output=await encodeExact(derived.glb);
  const corrupt=parseGLB(output.glb);corrupt.json.nodes[0].matrix[13]+=1;
  await assert.rejects(verifyLossy(original,makeGLB(corrupt.json,corrupt.bin),p),/metadata/);
  await assert.rejects(verifyLossy(original,output.glb,{...p,attributeBits:8}));
  const bad=parseGLB(original);bad.bin.writeFloatLE(NaN,0);
  await assert.rejects(deriveLossy(makeGLB(bad.json,bad.bin),p),/finite/);
});
test('reject unsafe, unpinned precision settings',async()=>{
  for(const patch of [{positionErrorMetres:2},{attributeBits:1},{triangleRatio:0},{lockBorders:false},{simplificationErrorMetres:NaN}]) {
    await assert.rejects(deriveLossy(fixture(),{...parameters(),...patch}));
  }
});
test('restore original tiny-face positions on collapse or reversed winding',()=>{
  const positions=Float32Array.from([0,0,0,1,0,0,0,0.0001,0]);
  for(const y of [0,-0.0001]) {
    const quantised=Float32Array.from([0,0,0,1,0,0,0,y,0]);
    const result=preserveSmallFaces(positions,quantised,Uint32Array.from([0,1,2]));
    assert.deepEqual(quantised,positions);assert.equal(result.quantisationProtectedFaces,1);
  }
  const flat=Float32Array.from([0,0,0,1,1,0,2,2,0]),expanded=Float32Array.from([0,0,0,1,1,0,2,2.1,0]);
  preserveSmallFaces(flat,expanded,Uint32Array.from([0,1,2]));assert.deepEqual(expanded,flat);
});
