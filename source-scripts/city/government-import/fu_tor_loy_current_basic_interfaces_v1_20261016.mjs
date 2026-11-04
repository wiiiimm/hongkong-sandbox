/** Diagnostic: original podium versus actual unchanged basic tower geometry. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=hash(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const closures=['3d-viewer/city/building-geometry.js','3d-viewer/city/official-model-assets.js','source-scripts/city/government-import/support-interface.mjs'].map(p=>snapshotModuleClosure(new URL(p,root),root));for(const c of closures){assert(c.completeAuditedLiteralImportClosure&&c.computedImportsRejected);Object.assign(hashes,c.inputHashes);}
const old='docs/astra-city/government-import/government-xl-fu-tor-loy-current-ground-v2-20261016/';
const original=read(old+'selection.json.gz').rows[0];assert.equal(original.uid,'landsd/228219:0');
const tile=read('3d-viewer/'+original.source.tile);assert.deepEqual(tile.buildings.find(b=>b.uid===original.uid),original.source.building);
const manifestPath='3d-viewer/city/data/manifest.json',manifest=read(manifestPath),installed=new Set(manifest.officialModelCatalogues.flatMap(u=>read('3d-viewer/'+u).models.map(m=>m.uid)));
assert(!installed.has(original.uid));
const raw=readFileSync(new URL(original.candidate.path,root));assert.equal(hash(raw),original.sourceSHA256);hashes[original.candidate.path]=hash(raw);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const model=await loadOfficialModel(original.candidate.entry,original.source.building,lighting,{fetcher:async()=>new Response(raw)}),rows=[];
try{for(const uid of ['landsd/231442:0','landsd/232818:0','landsd/233770:0','landsd/233775:0']){
 const b=tile.buildings.find(b=>b.uid===uid);assert(b&&!installed.has(uid));assert.equal(b.parent,original.source.building.parent);
 const geometry=createBuildingGeometry(b),position=Array.from(geometry.attributes.position.array),index=geometry.index?Array.from(geometry.index.array):Array.from({length:position.length/3},(_,i)=>i);
 const proof=verifySupportInterface({position,index},b.base+(b.minimum||0),model.record.modelGeometry);
 rows.push({uid,supportUid:original.uid,buildingCSUID:b.buildingCSUID,supportSHA256:original.sourceSHA256,interface:proof});geometry.dispose();
}}
finally{disposeOfficialModel(model);}
assert.equal(hash(readFileSync(new URL(manifestPath,root))),hashes[manifestPath]);
for(const p of ['source-scripts/city/government-import/fu_tor_loy_current_basic_interfaces_v1_20261016.mjs','3d-viewer/city/building-geometry.js','3d-viewer/city/official-model-assets.js','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs'])hashes[p]=hash(readFileSync(new URL(p,root)));
for(const c of closures)assert(verifyModuleClosure(c,root));for(const [p,h] of Object.entries(hashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
const out=new URL('docs/astra-city/government-import/government-xl-fu-tor-loy-current-basic-interfaces-v1-20261016/',root);mkdirSync(out,{recursive:true});
writeFileSync(new URL('diagnostic.json',out),JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,passed:r.interface.passed,samples:r.interface.samples,strictContacts:r.interface.strictContacts,unresolved:r.interface.unresolved.length}))));
