/** Read-only exact current BASIC neighbour geometry, not support or acceptance. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/',input=base+'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011',out=base+'government-xl-vancor-basic-253697-whole-projection-diagnostic-v2-20261011',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(path,h){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u);if(h!==undefined)assert.equal(sha(b),h,path);hashes[path]=sha(b);return b;}
function read(path,h){const b=bytes(path,h);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],'d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43');
const proposal=read(input+'/proposal-input.json');for(const r of proposal.completeCurrentCatalogueRefs)bytes(r.path,r.sha256);assert.deepEqual(proposal.completeCurrentCatalogueRefs.map(r=>r.path),manifest.officialModelCatalogues.map(p=>'3d-viewer/'+p));
for(const [p,h]of Object.entries(proposal.completeCurrentTileHashes))bytes(p,h);
bytes(proposal.retainedParent.path,proposal.retainedParent.sha256);
const forms=read(input+'/complete-proposed-region-current-forms.json.gz');assert.equal(forms.rows.length,80);assert.equal(new Set(forms.rows.map(r=>r.building.uid)).size,80);
const rows=forms.rows.filter(r=>r.building.uid==='landsd/253697:0');assert.equal(rows.length,1);const actor=rows[0];assert.equal(actor.existingNative,false);assert.equal(actor.building.buildingCSUID,'3557118534T20050430');
for(const r of proposal.completeCurrentCatalogueRefs)assert(!read(r.path,r.sha256).models.some(e=>e.uid===actor.building.uid));
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);Object.assign(hashes,closure.inputHashes);
for(const p of ['source-scripts/city/government-import/xl-vancor-current-basic-253697-geometry-v2-20261011.mjs','source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs','source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs'])bytes(p);
const {createBuildingGeometry}=await import(new URL('3d-viewer/city/building-geometry.js',root).href),geometry=createBuildingGeometry(actor.building);let captured;
try{const p=geometry.attributes.position;assert(p.array instanceof Float32Array);assert(Array.from(p.array).every(Number.isFinite));const ix=geometry.index?Array.from(geometry.index.array):Array.from({length:p.count},(_,i)=>i);assert(ix.length%3===0&&ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));const matrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],f32=actualFloat32ModelMatrixPositions(p.array,matrix);assert.deepEqual(f32.leftAssociatedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));assert.deepEqual(f32.balancedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));captured={uid:actor.building.uid,currentForm:actor.building,completePosition:Array.from(p.array),completeIndex:ix,completeNormals:Array.from(geometry.attributes.normal.array),identityWorldMatrix:matrix,...f32,completeFaces:ix.length/3,completeVertices:p.count};}finally{geometry.dispose();}
for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);assert(verifyModuleClosure(closure,root));const target=out+'/complete-current-basic-geometry.json.gz';assert(!existsSync(new URL(target,root)));writeFileSync(new URL(target,root),gzipSync(JSON.stringify({actor:captured,inputHashes:hashes,recursiveProductionModuleClosure:closure,startAndEndInputsVerified:true,sourceGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));console.log(JSON.stringify({uid:captured.uid,faces:captured.completeFaces,vertices:captured.completeVertices,physicalAccepted:false}));
