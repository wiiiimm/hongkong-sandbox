/** Complete actual BASIC actor census, no ownership/collision/support credit. */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/',input=base+'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011',out=base+'government-xl-king-cheung-95691-complete-current-four-foreign-basic-context-v1-20261011',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(path,h){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u);if(h!==undefined)assert.equal(sha(b),h,path);hashes[path]=sha(b);return b;}
function read(path,h){const b=bytes(path,h);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],'d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43');
const proposal=read(input+'/complete-current-actual-source-and-ground.json.gz');assert(proposal.startAndEndInputsVerified);assert.equal(proposal.uid,'landsd/95691:0');
assert.deepEqual(proposal.completeCurrentCatalogueRefs.map(r=>r.path),manifest.officialModelCatalogues.map(p=>'3d-viewer/'+p));
const native=new Set();for(const r of proposal.completeCurrentCatalogueRefs)for(const e of read(r.path,r.sha256).models){assert(!native.has(e.uid));native.add(e.uid);}assert.equal(native.size,6642);
for(const[p,h]of Object.entries(proposal.inputHashes))bytes(p,h);
const forms=proposal.completeCurrentForms;assert(Array.isArray(forms));assert.equal(forms.length,5);assert.equal(new Set(forms.map(r=>r.uid)).size,5);
const owned=forms.filter(r=>r.uid==='landsd/95691:0');assert.equal(owned.length,1);assert(!native.has(owned[0].uid));
assert(forms.every(r=>!native.has(r.uid)));
const foreign=forms.filter(r=>r.uid!=='landsd/95691:0');assert.equal(foreign.length,4);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);Object.assign(hashes,closure.inputHashes);
for(const p of ['source-scripts/city/government-import/xl-king-cheung-95691-current-four-foreign-basic-geometry-v1-20261011.mjs','source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs','source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs'])bytes(p);
const {createBuildingGeometry}=await import(new URL('3d-viewer/city/building-geometry.js',root).href),rows=[];
for(const actor of foreign){const geometry=createBuildingGeometry(actor);try{
 const p=geometry.attributes.position;assert(p.array instanceof Float32Array);assert(Array.from(p.array).every(Number.isFinite));const ix=geometry.index?Array.from(geometry.index.array):Array.from({length:p.count},(_,i)=>i);assert(ix.length%3===0&&ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));
 const matrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],f32=actualFloat32ModelMatrixPositions(p.array,matrix);assert.deepEqual(f32.leftAssociatedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));assert.deepEqual(f32.balancedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));
 rows.push({uid:actor.uid,currentForm:actor,completePosition:Array.from(p.array),completeIndex:ix,completeNormals:Array.from(geometry.attributes.normal.array),identityWorldMatrix:matrix,...f32,completeFaces:ix.length/3,completeVertices:p.count});
 }finally{geometry.dispose();}}
for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);assert(verifyModuleClosure(closure,root));mkdirSync(new URL(out+'/',root),{recursive:true});const target=out+'/complete-current-foreign-basic-geometry.json.gz';assert(!existsSync(new URL(target,root)));
writeFileSync(new URL(target,root),gzipSync(JSON.stringify({rows,completeRegionalForms:5,completeForeignBasics:4,ownedUID:'landsd/95691:0',completeRegionalNativeUIDs:[],inputHashes:hashes,recursiveProductionModuleClosure:closure,startAndEndInputsVerified:true,sourceGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));console.log(JSON.stringify({completeForeignBasics:rows.length,physicalAccepted:false}));
