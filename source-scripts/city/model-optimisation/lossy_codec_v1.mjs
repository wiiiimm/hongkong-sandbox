/** Bounded precision/LOD candidates. Originals, materials and scene poses stay immutable. */
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync, gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { createInterface } from 'node:readline';
import { MeshoptSimplifier } from 'meshoptimizer';
import { parseGLB, makeGLB, encodeExact, verifyExact, sha } from './codec.mjs';

const widths = { SCALAR:1, VEC2:2, VEC3:3, VEC4:4 };
const sizes = { 5121:1, 5123:2, 5125:4, 5126:4 };
const identity = () => [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1];
function multiply(a,b) {
  return Array.from({length:16}, (_,i) => {
    const row=i%4, col=Math.floor(i/4);
    return a[row]*b[col*4]+a[row+4]*b[col*4+1]+a[row+8]*b[col*4+2]+a[row+12]*b[col*4+3];
  });
}
function localMatrix(n) {
  if (n.matrix) { assert.equal(n.matrix.length,16); return n.matrix; }
  const [x,y,z,w]=n.rotation ?? [0,0,0,1], [sx,sy,sz]=n.scale ?? [1,1,1];
  assert.ok(Math.abs(x*x+y*y+z*z+w*w-1)<1e-5,'unit node quaternion');
  const [tx,ty,tz]=n.translation ?? [0,0,0];
  return [(1-2*y*y-2*z*z)*sx,(2*x*y+2*z*w)*sx,(2*x*z-2*y*w)*sx,0,
    (2*x*y-2*z*w)*sy,(1-2*x*x-2*z*z)*sy,(2*y*z+2*x*w)*sy,0,
    (2*x*z+2*y*w)*sz,(2*y*z-2*x*w)*sz,(1-2*x*x-2*y*y)*sz,0,tx,ty,tz,1];
}
function meshMatrices(j) {
  const result=j.meshes.map(()=>[]), children=new Set((j.nodes ?? []).flatMap(n=>n.children ?? []));
  function walk(index,parent,ancestors) {
    assert.ok(!ancestors.has(index),'acyclic scene');
    const n=j.nodes[index]; assert.ok(n,'valid node index');
    const m=multiply(parent,localMatrix(n)); assert.ok(m.every(Number.isFinite));
    assert.deepEqual([m[3],m[7],m[11],m[15]],[0,0,0,1],'affine scene pose');
    if(n.mesh!==undefined) { assert.ok(result[n.mesh]);result[n.mesh].push(m); }
    for(const child of n.children ?? []) walk(child,m,new Set([...ancestors,index]));
  }
  // Include unselected scenes and roots as well, preserving every mesh instance.
  for(let i=0;i<(j.nodes?.length ?? 0);i++) if(!children.has(i)) walk(i,identity(),new Set());
  for(const matrices of result) assert.ok(matrices.length,'mesh must have a source scene instance');
  return result;
}
function dense(source,index) {
  const a=source.json.accessors[index],v=source.json.bufferViews[a.bufferView];
  assert.ok(!a.sparse && v.buffer===0 && !v.extensions && a.count>0);
  const width=widths[a.type],size=sizes[a.componentType];assert.ok(width&&size);
  const stride=v.byteStride ?? width*size, out=Buffer.alloc(a.count*width*size);
  assert.ok(stride>=width*size && (a.byteOffset ?? 0)+(a.count-1)*stride+width*size<=v.byteLength);
  for(let i=0;i<a.count;i++) source.bin.copy(out,i*width*size,
    (v.byteOffset ?? 0)+(a.byteOffset ?? 0)+i*stride,(v.byteOffset ?? 0)+(a.byteOffset ?? 0)+i*stride+width*size);
  if(a.componentType===5126) for(let i=0;i<out.length;i+=4) assert.ok(Number.isFinite(out.readFloatLE(i)),'finite source attribute');
  return {a,bytes:out,width,size};
}
function floats(stream) {
  assert.equal(stream.a.componentType,5126,'Float32 source attribute required');
  return Float32Array.from({length:stream.bytes.length/4},(_,i)=>stream.bytes.readFloatLE(i*4));
}
function limits(positions) {
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<positions.length;i++) {const k=i%3;min[k]=Math.min(min[k],positions[i]);max[k]=Math.max(max[k],positions[i]);}
  return {min,max};
}
function triangleArea(positions,a,b,c) {
  const u=[0,1,2].map(k=>positions[b*3+k]-positions[a*3+k]),v=[0,1,2].map(k=>positions[c*3+k]-positions[a*3+k]);
  return Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);
}
export function validateLossyParameters(p) {
  assert.equal(p.adapter,'meshopt-bounded-lossy-v1');assert.equal(p.quantisation,true);
  for(const key of ['positionErrorMetres','simplificationErrorMetres','triangleRatio']) assert.ok(Number.isFinite(p[key]));
  assert.ok(p.positionErrorMetres>0 && p.positionErrorMetres<=0.1);
  assert.ok(p.triangleRatio>0 && p.triangleRatio<=1);
  assert.equal(p.simplification,p.triangleRatio<1);
  assert.ok(p.simplification ? p.simplificationErrorMetres>0 && p.simplificationErrorMetres<=0.25 : p.simplificationErrorMetres===0);
  assert.ok(Number.isInteger(p.attributeBits) && p.attributeBits>=8 && p.attributeBits<=16);
  assert.equal(p.lockBorders,true);assert.equal(p.pinPositionExtrema,true);
  assert.equal(p.geometryCodec,'meshopt');assert.equal(p.transportEncoding,'gzip');assert.equal(p.gzipLevel,9);
  return p;
}

export async function deriveLossy(sourceBytes, parameters) {
  const p=validateLossyParameters(parameters);await MeshoptSimplifier.ready;
  const source=parseGLB(sourceBytes),j=structuredClone(source.json);
  assert.equal(j.buffers.length,1);assert.ok(!j.buffers[0].uri);
  assert.ok(!j.images?.length&&!j.textures?.length&&!j.animations?.length&&!j.skins?.length,'static geometry-only source');
  assert.ok(!j.extensionsUsed?.length&&!j.extensionsRequired?.length,'unencoded source');
  const matrices=meshMatrices(j),pieces=[];let offset=0;
  j.accessors=[];j.bufferViews=[];
  function append(stream,bytes,count,target) {
    const padding=Buffer.alloc((4-offset%4)%4);pieces.push(padding);offset+=padding.length;
    const view=j.bufferViews.length;j.bufferViews.push({buffer:0,byteOffset:offset,byteLength:bytes.length,target});
    pieces.push(bytes);offset+=bytes.length;
    const a={...structuredClone(stream.a),bufferView:view,count};delete a.byteOffset;delete a.min;delete a.max;
    if(a.type==='VEC3' && target===34962 && stream.position) {const range=limits(floats({...stream,bytes}));a.min=range.min;a.max=range.max;}
    const index=j.accessors.length;j.accessors.push(a);return index;
  }
  const diagnostics=[];
  for(let mi=0;mi<j.meshes.length;mi++) for(let pi=0;pi<j.meshes[mi].primitives.length;pi++) {
    const original=source.json.meshes[mi].primitives[pi],primitive=j.meshes[mi].primitives[pi];
    assert.equal(original.mode ?? 4,4);assert.ok(!original.targets?.length,'no morph targets');
    const streams=Object.fromEntries(Object.entries(original.attributes).map(([key,value])=>[key,dense(source,value)]));
    const position=streams.POSITION;assert.equal(position.a.type,'VEC3');position.position=true;
    const positions=floats(position),count=position.a.count;
    for(const stream of Object.values(streams)) assert.equal(stream.a.count,count);
    let indices;
    if(original.indices===undefined) {assert.equal(count%3,0);indices=Uint32Array.from({length:count},(_,i)=>i);}
    else {const stream=dense(source,original.indices);assert.equal(stream.a.type,'SCALAR');assert.ok([5123,5125].includes(stream.a.componentType));
      indices=Uint32Array.from({length:stream.a.count},(_,i)=>stream.bytes.readUIntLE(i*stream.size,stream.size));}
    assert.equal(indices.length%3,0);for(const index of indices) assert.ok(index<count);
    const originalIndices=Uint32Array.from(indices),range=limits(positions);
    const maxNorm=Math.max(...matrices[mi].map(m=>Math.hypot(m[0],m[1],m[2],m[4],m[5],m[6],m[8],m[9],m[10])));
    assert.ok(maxNorm>0 && Number.isFinite(maxNorm));
    const locks=Uint8Array.from({length:count},(_,i)=>[0,1,2].some(k=>positions[i*3+k]===range.min[k]||positions[i*3+k]===range.max[k])?1:0);
    let simplifierError=0;
    if(p.simplification && indices.length>3) {
      const attribStreams=['NORMAL','COLOR_0'].filter(k=>streams[k]?.a.componentType===5126).map(k=>floats(streams[k]));
      const stride=attribStreams.reduce((n,x)=>n+x.length/count,0);
      const attributes=new Float32Array(count*Math.max(1,stride));
      if(stride) for(let i=0;i<count;i++) {let k=0;for(const stream of attribStreams) for(let a=0;a<stream.length/count;a++) attributes[i*stride+k++]=stream[i*(stream.length/count)+a];}
      const target=Math.max(3,Math.floor(indices.length*p.triangleRatio/3)*3);
      [indices,simplifierError]=MeshoptSimplifier.simplifyWithAttributes(indices,positions,3,attributes,Math.max(1,stride),
        Array(Math.max(1,stride)).fill(stride?1:0),locks,target,p.simplificationErrorMetres/maxNorm,['LockBorder','ErrorAbsolute']);
      assert.ok(indices.length>0 && indices.length<=originalIndices.length && indices.length%3===0);
      assert.ok(simplifierError*maxNorm<=p.simplificationErrorMetres+1e-6,'bounded estimated simplifier error');
    }
    const step=2**Math.floor(Math.log2(2*p.positionErrorMetres/(Math.sqrt(3)*maxNorm)));
    const quantised=Float32Array.from(positions);let maxPositionError=0,preservedForPrecision=0;
    for(let i=0;i<count;i++) {
      const candidate=[0,1,2].map(k=>locks[i]?positions[i*3+k]:Math.fround(Math.round(positions[i*3+k]/step)*step));
      const delta=candidate.map((v,k)=>v-positions[i*3+k]);
      const error=Math.max(...matrices[mi].map(m=>Math.hypot(m[0]*delta[0]+m[4]*delta[1]+m[8]*delta[2],
        m[1]*delta[0]+m[5]*delta[1]+m[9]*delta[2],m[2]*delta[0]+m[6]*delta[1]+m[10]*delta[2])));
      if(!Number.isFinite(error)||error>p.positionErrorMetres) {preservedForPrecision++;continue;}
      maxPositionError=Math.max(maxPositionError,error);quantised.set(candidate,i*3);
    }
    const remap=new Map(),kept=[];
    if(p.simplification) {
      for(const index of indices) if(!remap.has(index)) {remap.set(index,kept.length);kept.push(index);}
    }
    if(!p.simplification) for(let i=0;i<count;i++) {remap.set(i,i);kept.push(i);}
    let maxNormalAngleDegrees=0,maxColourComponentError=0;
    const attributes={};
    for(const [semantic,stream] of Object.entries(streams)) {
      const bytes=Buffer.alloc(kept.length*stream.width*stream.size);
      for(let i=0;i<kept.length;i++) {
        const old=kept[i];stream.bytes.copy(bytes,i*stream.width*stream.size,old*stream.width*stream.size,(old+1)*stream.width*stream.size);
        if(semantic==='POSITION') for(let k=0;k<3;k++) bytes.writeFloatLE(quantised[old*3+k],(i*3+k)*4);
        if(['NORMAL','COLOR_0','COLOR_1'].includes(semantic) && stream.a.componentType===5126) {
          const before=[],after=[];
          for(let k=0;k<stream.width;k++) {
            const value=stream.bytes.readFloatLE((old*stream.width+k)*4),q=Math.fround(Math.round(value*2**p.attributeBits)/2**p.attributeBits);
            before.push(value);after.push(q);bytes.writeFloatLE(q,(i*stream.width+k)*4);
            if(semantic.startsWith('COLOR')) maxColourComponentError=Math.max(maxColourComponentError,Math.abs(value-q));
          }
          if(semantic==='NORMAL') {
            const a=Math.hypot(...before),b=Math.hypot(...after);
            if(a>0&&b>0) maxNormalAngleDegrees=Math.max(maxNormalAngleDegrees,Math.acos(Math.max(-1,Math.min(1,before.reduce((n,v,k)=>n+v*after[k],0)/(a*b))))*180/Math.PI);
            else assert.equal(a,b,'do not collapse a nonzero normal');
          }
        }
      }
      attributes[semantic]=append(stream,bytes,kept.length,34962);
    }
    const packedIndices=Buffer.alloc(indices.length*4);
    for(let i=0;i<indices.length;i++) packedIndices.writeUInt32LE(remap.get(indices[i]),i*4);
    primitive.attributes=attributes;
    primitive.indices=append({a:{componentType:5125,type:'SCALAR'}},packedIndices,indices.length,34963);
    let sourceDegenerateFaces=0,outputDegenerateFaces=0,quantisationCollapsedFaces=0;
    for(let i=0;i<originalIndices.length;i+=3) if(triangleArea(positions,...originalIndices.subarray(i,i+3))===0) sourceDegenerateFaces++;
    for(let i=0;i<indices.length;i+=3) {const ids=indices.subarray(i,i+3);if(triangleArea(quantised,...ids)===0) {outputDegenerateFaces++;if(triangleArea(positions,...ids)>0) quantisationCollapsedFaces++;}}
    diagnostics.push({mesh:mi,primitive:pi,originalVertices:count,vertices:kept.length,
      originalTriangles:originalIndices.length/3,triangles:indices.length/3,
      triangleRatio:indices.length/originalIndices.length,requestedTriangleRatio:p.triangleRatio,
      maxPositionQuantisationErrorMetres:maxPositionError,positionGridMetres:step,
      simplifierEstimatedErrorMetres:simplifierError*maxNorm,
      combinedEstimatedErrorMetres:simplifierError*maxNorm+maxPositionError,
      maxLocalNormalAngleDegrees:maxNormalAngleDegrees,maxColourComponentError,
      preservedVerticesForFloat32Budget:preservedForPrecision,sourceDegenerateFaces,outputDegenerateFaces,quantisationCollapsedFaces,
      removedVertices:count-kept.length,extremaPinned:true,bordersLockedDuringSimplification:true});
  }
  j.buffers=[{byteLength:offset}];const glb=makeGLB(j,Buffer.concat(pieces));
  const max=key=>Math.max(...diagnostics.map(d=>d[key]));const sum=key=>diagnostics.reduce((n,d)=>n+d[key],0);
  return {glb,metrics:{primitiveDiagnostics:diagnostics,originalVertices:sum('originalVertices'),originalTriangles:sum('originalTriangles'),
    vertices:sum('vertices'),triangles:sum('triangles'),removedVertices:sum('removedVertices'),
    originalDecodedAccessorBytes:source.json.bufferViews.reduce((n,v)=>n+v.byteLength,0),
    maxPositionQuantisationErrorMetres:max('maxPositionQuantisationErrorMetres'),
    simplifierEstimatedErrorMetres:max('simplifierEstimatedErrorMetres'),combinedEstimatedErrorMetres:max('combinedEstimatedErrorMetres'),
    maxLocalNormalAngleDegrees:max('maxLocalNormalAngleDegrees'),maxColourComponentError:max('maxColourComponentError'),
    sourceDegenerateFaces:sum('sourceDegenerateFaces'),outputDegenerateFaces:sum('outputDegenerateFaces'),quantisationCollapsedFaces:sum('quantisationCollapsedFaces'),
    sourceScenePosesAndMaterialsPreserved:true,topologyPreserved:!p.simplification,lossy:true,
    hausdorffErrorMetres:null,deviceFrameTimeMs:null,peakMemoryBytes:null,
    errorMethod:'All vertex quantisation displacements measured through every source node world matrix; simplifier absolute weighted quadric error is an estimate, not a Hausdorff or visual-error guarantee.'}};
}

export async function verifyLossy(sourceBytes,outputBytes,parameters) {
  const derived=await deriveLossy(sourceBytes,parameters);
  const decoded=await verifyExact(derived.glb,outputBytes);
  // The exact codec equality is against the derived mesh, never against originals.
  const {worldPlacementErrorMetres,maxAttributeError,indexOrderPreserved,sourceMetadataPreserved,...codecMetrics}=decoded;
  return {...codecMetrics,...derived.metrics,derivedMeshRoundtripExact:true,
    sourceSceneTransformError:0,sourceGeometryExact:false};
}

async function processRequest(request) {
  const recipe=request.recipe;assert.equal(recipe.lossy,true);validateLossyParameters(recipe.parameters);
  const compressed=readFileSync(request.source);assert.equal(sha(compressed),request.sourceSha256);
  const native=gunzipSync(compressed),start=performance.now();
  const derived=await deriveLossy(native,recipe.parameters),derivedMs=performance.now()-start;
  const encoded=await encodeExact(derived.glb);
  const output=gzipSync(encoded.glb,{level:9,mtime:0}),hash=sha(output),path=resolve(request.artifactDirectory,`${hash}.glb.gz`);
  mkdirSync(dirname(path),{recursive:true});
  if(existsSync(path)) assert.equal(sha(readFileSync(path)),hash);else writeFileSync(path,output,{flag:'wx'});
  const readback=readFileSync(path);assert.equal(sha(readback),hash);
  const verification=await verifyExact(derived.glb,gunzipSync(readback));
  const {worldPlacementErrorMetres,maxAttributeError,indexOrderPreserved,sourceMetadataPreserved,...codecMetrics}=verification;
  return {artifact:{path,sha256:hash},metrics:{...codecMetrics,...derived.metrics,
    derivedMeshRoundtripExact:true,sourceGeometryExact:false,sourceSceneTransformError:0,
    originalDownloadBytes:compressed.length,downloadBytes:output.length,originalGLBBytes:native.length,glbBytes:encoded.glb.length,
    savedBytes:compressed.length-output.length,beneficial:output.length<compressed.length,compressionRatio:output.length/compressed.length,
    derivationMs:derivedMs,encodeMs:encoded.metrics.encodeMs,processingMs:performance.now()-start,
    codec:'meshopt',codecVersion:'0.24.0',transportEncoding:'gzip',tier:recipe.tier,
    residentGeometryBytesEstimate:codecMetrics.decodedAccessorBytes,
    residentMethod:'Derived bufferView bytes; excludes source collision geometry, JS/GPU/decoder overhead and temporary peaks.',
    timingEnvironment:{node:process.versions.node,platform:process.platform,architecture:process.arch,wasmSIMD:null}}};
}

if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  for await(const line of createInterface({input:process.stdin})) {
    try {process.stdout.write(JSON.stringify({ok:true,...await processRequest(JSON.parse(line))})+'\n');}
    catch(error) {process.stdout.write(JSON.stringify({ok:false,error:error.message.slice(0,600)})+'\n');}
  }
}
