/** Complete actual BASIC actor census, no ownership/collision/support credit. */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/',input=base+'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011',out=base+'government-xl-vancor-complete-current-foreign-basic-context-v2-20261011',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(path,h){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u);if(h!==undefined)assert.equal(sha(b),h,path);hashes[path]=sha(b);return b;}
function read(path,h){const b=bytes(path,h);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],'d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43');
const proposal=read(input+'/proposal-input.json');assert.deepEqual(proposal.completeCurrentCatalogueRefs.map(r=>r.path),manifest.officialModelCatalogues.map(p=>'3d-viewer/'+p));
const native=new Set();for(const r of proposal.completeCurrentCatalogueRefs)for(const e of read(r.path,r.sha256).models){assert(!native.has(e.uid));native.add(e.uid);}assert.equal(native.size,6642);
for(const[p,h]of Object.entries(proposal.completeCurrentTileHashes))bytes(p,h);bytes(proposal.retainedParent.path,proposal.retainedParent.sha256);
const forms=read(input+'/complete-proposed-region-current-forms.json.gz');assert.equal(forms.rows.length,80);assert.equal(new Set(forms.rows.map(r=>r.building.uid)).size,80);
for(const r of forms.rows)assert.equal(r.existingNative,native.has(r.building.uid),r.building.uid);
const owned=forms.rows.filter(r=>r.building.uid==='landsd/147956:0');assert.equal(owned.length,1);assert(!native.has(owned[0].building.uid));
const natives=forms.rows.filter(r=>r.existingNative);assert.deepEqual(natives.map(r=>r.building.uid),['landsd/186864:0','landsd/236490:0']);
const foreign=forms.rows.filter(r=>!r.existingNative&&r.building.uid!=='landsd/147956:0');assert.equal(foreign.length,77);for(const r of foreign)assert(!native.has(r.building.uid));
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);Object.assign(hashes,closure.inputHashes);
for(const p of ['source-scripts/city/government-import/xl-vancor-complete-current-foreign-basic-geometry-v2-20261011.mjs','source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs','source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs'])bytes(p);
const {createBuildingGeometry}=await import(new URL('3d-viewer/city/building-geometry.js',root).href),rows=[];
for(const actor of foreign){const geometry=createBuildingGeometry(actor.building);try{
 const p=geometry.attributes.position;assert(p.array instanceof Float32Array);assert(Array.from(p.array).every(Number.isFinite));const ix=geometry.index?Array.from(geometry.index.array):Array.from({length:p.count},(_,i)=>i);assert(ix.length%3===0&&ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));
 const matrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],f32=actualFloat32ModelMatrixPositions(p.array,matrix);assert.deepEqual(f32.leftAssociatedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));assert.deepEqual(f32.balancedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));
 rows.push({uid:actor.building.uid,currentForm:actor.building,completePosition:Array.from(p.array),completeIndex:ix,completeNormals:Array.from(geometry.attributes.normal.array),identityWorldMatrix:matrix,...f32,completeFaces:ix.length/3,completeVertices:p.count});
 }finally{geometry.dispose();}}
for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);assert(verifyModuleClosure(closure,root));mkdirSync(new URL(out+'/',root),{recursive:true});const target=out+'/complete-current-foreign-basic-geometry.json.gz';assert(!existsSync(new URL(target,root)));
writeFileSync(new URL(target,root),gzipSync(JSON.stringify({rows,completeRegionalForms:80,completeForeignBasics:77,ownedUID:'landsd/147956:0',completeRegionalNativeUIDs:['landsd/186864:0','landsd/236490:0'],inputHashes:hashes,recursiveProductionModuleClosure:closure,startAndEndInputsVerified:true,sourceGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));console.log(JSON.stringify({completeForeignBasics:rows.length,physicalAccepted:false}));
