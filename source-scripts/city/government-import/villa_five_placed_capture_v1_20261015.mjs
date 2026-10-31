/** Complete actual placed Villa streams; no geometry edits or acceptance. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
import {preflightActualRenderMesh} from './current_geometry_capture_preflight_20261011.mjs';
const root=new URL('../../../',import.meta.url),stage='source-scripts/city/government-import/local/government-xl-villa-five-current-physical-v4-20261015/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(p){const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return b;}
function read(p){return JSON.parse(bytes(p));}
const closure=snapshotModuleClosure(new URL('3d-viewer/city/official-model-assets.js',root),root);Object.assign(hashes,closure.inputHashes);
for(const p of ['villa_five_placed_capture_v1_20261015.mjs','actual_float32_model_matrix_bounds_20261011.mjs','current_geometry_capture_preflight_20261011.mjs','exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'])bytes('source-scripts/city/government-import/'+p);
const catalogue=read(stage+'catalogue.json'),forms=read(stage+'source-forms.json');
const {loadOfficialModel,disposeOfficialModel,prepareModelCatalogue}=await import(new URL('3d-viewer/city/official-model-assets.js',root)),THREE=await import(new URL('3d-viewer/vendor/three.module.js',root));
const entries=prepareModelCatalogue(catalogue,new URL('https://diagnostic.invalid/'+stage+'catalogue.json')),lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
assert.equal(entries.length,5);
for(const entry of entries){const source=catalogue.models.find(m=>m.uid===entry.uid),raw=bytes(stage+source.asset);assert.equal(sha(raw),entry.sha256);const model=await loadOfficialModel(entry,forms[entry.uid].building,lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>{assert(forms[uid]);return forms[uid].building;}});try{model.group.updateMatrixWorld(true);const meshes=[];let count=0;for(const mesh of model.meshes){const schema=preflightActualRenderMesh(mesh),p=mesh.geometry.attributes.position,m=mesh.matrixWorld.elements,index=Array.from(mesh.geometry.index.array),literal=[],v=new THREE.Vector3();for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);literal.push(v.x,v.y,v.z);}meshes.push({schema,index,literal,matrixWorldFloat64:Array.from(m),...actualFloat32ModelMatrixPositions(p.array,m)});count+=index.length/3;}assert.equal(count,entry.triangles);rows.push({uid:entry.uid,sourceSHA256:entry.sha256,completeFaces:count,meshes});}finally{disposeOfficialModel(model);}}
assert(verifyModuleClosure(closure,root));for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);
writeFileSync(new URL(process.argv[2],root),gzipSync(JSON.stringify({rows,inputHashes:hashes,closure,sourceGeometryChanges:0,explicitArithmeticOrdersNotUniversalGPUGuarantee:true})));
