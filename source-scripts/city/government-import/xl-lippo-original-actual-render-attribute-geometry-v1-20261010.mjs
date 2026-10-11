/** Source-only actual render attributes/matrices and explicit Float32 arithmetic. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3];
assert(inputPath?.startsWith('docs/astra-city/government-import/'));assert(outputPath?.startsWith('docs/astra-city/government-import/'));assert(!existsSync(new URL(outputPath,root)));
const sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function bytes(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return b;}
const closure=snapshotModuleClosure(import.meta.url,root);Object.assign(hashes,closure.inputHashes);const input=JSON.parse(gunzipSync(bytes(inputPath)));
assert(input.rows.length===3&&new Set(input.rows.map(r=>r.uid)).size===3);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const r of input.rows){
 const raw=bytes(r.path);assert.equal(sha(raw),r.entry.sha256);let model;
 try{
  model=await loadOfficialModel({...r.entry,assetURL:'https://diagnostic.invalid/unchanged-original.glb.gz'},r.building,lighting,{fetcher:async()=>new Response(raw)});
  model.group.updateMatrixWorld(true);const meshes=[],position=[],index=[],roundedWorld=[],float32ModelMatrixWorld=[];let offset=0;
  for(const mesh of model.meshes){
   const p=mesh.geometry.attributes.position,idx=mesh.geometry.index.array,m=mesh.matrixWorld.elements,f32m=m.map(Math.fround),actual=new THREE.Vector3();assert(p.array instanceof Float32Array);assert(idx.length%3===0&&m.every(Number.isFinite));
   meshes.push({name:mesh.name,positionAttributeArrayType:p.array.constructor.name,completeOriginalVertexAttribute:Array.from(p.array),completeOriginalIndex:Array.from(idx),matrixWorldFloat64:Array.from(m),modelMatrixUniformFloat32:f32m,completeNormalAttribute:Array.from(mesh.geometry.attributes.normal.array),completeColorAttribute:Array.from(mesh.geometry.attributes.color.array)});
   for(let i=0;i<p.count;i++){
    actual.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);position.push(...actual.toArray());roundedWorld.push(...actual.toArray().map(Math.fround));
    const xyz=[p.getX(i),p.getY(i),p.getZ(i)];
    for(let j=0;j<3;j++)float32ModelMatrixWorld.push(Math.fround(Math.fround(Math.fround(Math.fround(f32m[j]*xyz[0])+Math.fround(f32m[4+j]*xyz[1]))+Math.fround(f32m[8+j]*xyz[2]))+f32m[12+j]));
   }
   for(const j of idx)index.push(j+offset);offset+=p.count;
  }
  assert.equal(index.length/3,r.entry.triangles);assert.deepEqual(position,Array.from(model.record.modelGeometry.position));assert.deepEqual(index,Array.from(model.record.modelGeometry.index));
  rows.push({uid:r.uid,sourceSHA256:sha(raw),completeFaces:index.length/3,actualRenderMeshes:meshes,index,worldPositionFloat64:position,roundedWorldPositionFloat32:roundedWorld,explicitFloat32ModelMatrixWorldPosition:float32ModelMatrixWorld,sourceGeometryChanges:0});
  console.log(JSON.stringify({uid:r.uid,faces:index.length/3,meshes:meshes.map(m=>({vertices:m.completeOriginalVertexAttribute.length/3,matrix:m.matrixWorldFloat64}))}));
 }finally{if(model)disposeOfficialModel(model);}
}
for(const [path,pin] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pin);assert(verifyModuleClosure(closure,root));
writeFileSync(new URL(outputPath,root),gzipSync(JSON.stringify({rows,inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startAndEndInputHashesVerified:true,sourceGeometryChanges:0,identityAccepted:false,physicalAccepted:false,installationApproved:false,qualification:'Complete actual Float32 render vertex attributes and unchanged literal source mesh matrices exported. Both rounded-world representation and explicitly declared Float32 model-matrix arithmetic are diagnostics, not a universal GPU model-view/camera rounding guarantee. Complete renderer camera/model-view checks remain separate. No geometry, root, matrix or production files changed.'})));
