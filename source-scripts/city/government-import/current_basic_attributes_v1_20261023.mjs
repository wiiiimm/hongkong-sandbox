/** Capture complete production BASIC geometry; no runtime or input mutations. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeBuildings} from '../../../3d-viewer/city/world.js';
import {describeBuilding} from '../../../3d-viewer/city/building-geometry.js';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[inputPath,outPath]=process.argv.slice(2),hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(path,expected){const raw=readFileSync(new URL(path,root)),h=sha(raw);if(expected)assert.equal(h,expected,path);if(hashes[path])assert.equal(hashes[path],h);hashes[path]=h;return raw;}
const input=JSON.parse(gunzipSync(bytes(inputPath)));
for(const q of input.evidenceRefs)bytes(q.path,q.sha256);
bytes(input.currentManifest.path,input.currentManifest.sha256);
const closure=snapshotModuleClosure(import.meta.url,root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
Object.assign(hashes,closure.inputHashes);const rows=[];
for(const building of input.rows){
 const original=JSON.stringify(building),built=await makeBuildings([building],null,{worker:false,yield:false}),meshes=[];built.group.updateMatrixWorld(true);
 try{
  built.group.traverse(mesh=>{if(!mesh.isMesh)return;assert.deepEqual(mesh.matrixWorld.elements,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);const p=mesh.geometry.attributes.position,index=mesh.geometry.index;assert(p.array instanceof Float32Array);const literal=Array.from(p.array),ar=actualFloat32ModelMatrixPositions(p.array,mesh.matrixWorld.elements);assert.deepEqual(ar.leftAssociatedPerMultiplyAddFloat32WorldPosition,literal);assert.deepEqual(ar.balancedPerMultiplyAddFloat32WorldPosition,literal);meshes.push({position:literal,index:index?Array.from(index.array):Array.from({length:p.count},(_,i)=>i),completeUnusedPositionVertices:p.count,identityArithmeticAllThreeExactlyEqual:true});});
  assert.equal(JSON.stringify(building),original);assert(meshes.length);rows.push({uid:building.uid,building,description:describeBuilding(building),meshes,completeFaces:meshes.reduce((n,m)=>n+m.index.length/3,0)});
 }finally{built.group.traverse(m=>m.geometry?.dispose());for(const material of built.materials)material.dispose();}
}
verifyModuleClosure(closure,root);for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
writeFileSync(new URL(outPath,root),gzipSync(JSON.stringify({rows,inputHashes:hashes,startEndAllInputsVerified:true,sourceGeometryChanges:0,installationApproved:false})));
