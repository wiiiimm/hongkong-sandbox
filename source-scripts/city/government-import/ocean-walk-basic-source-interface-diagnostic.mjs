/** Diagnostic: original podium versus actual unchanged basic tower geometry. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=hash(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const old='docs/astra-city/government-import/government-xl-ocean-walk-complete-source-local-20261008/';
const original=read(old+'selection.json.gz').rows[0];assert.equal(original.uid,'landsd/81743:0');
const tile=read('3d-viewer/'+original.source.tile);assert.deepEqual(tile.buildings.find(b=>b.uid===original.uid),original.source.building);
const manifestPath='3d-viewer/city/data/manifest.json',manifest=read(manifestPath),installed=new Set(manifest.officialModelCatalogues.flatMap(u=>read('3d-viewer/'+u).models.map(m=>m.uid)));
assert(!installed.has(original.uid));
const raw=readFileSync(new URL(original.candidate.path,root));assert.equal(hash(raw),original.sourceSHA256);hashes[original.candidate.path]=hash(raw);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const model=await loadOfficialModel(original.candidate.entry,original.source.building,lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>tile.buildings.find(b=>b.uid===uid)}),rows=[];
try{for(const uid of ['landsd/203829:0','landsd/203832:0','landsd/203836:0','landsd/204242:0','landsd/336959:0','landsd/336960:0']){
 const b=tile.buildings.find(b=>b.uid===uid);assert(b&&!installed.has(uid));
 const geometry=createBuildingGeometry(b),position=Array.from(geometry.attributes.position.array),index=geometry.index?Array.from(geometry.index.array):Array.from({length:position.length/3},(_,i)=>i);
 const proof=verifySupportInterface({position,index},b.base+(b.minimum||0),model.record.modelGeometry);
 rows.push({uid,supportUid:original.uid,buildingCSUID:b.buildingCSUID,supportSHA256:original.sourceSHA256,interface:proof});geometry.dispose();
}}
finally{disposeOfficialModel(model);}
assert.equal(hash(readFileSync(new URL(manifestPath,root))),hashes[manifestPath]);
for(const p of ['source-scripts/city/government-import/ocean-walk-basic-source-interface-diagnostic.mjs','3d-viewer/city/building-geometry.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/official-model-footprint-scopes.js','3d-viewer/city/official-model-footprint-scopes-ocean-walk.js','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs'])hashes[p]=hash(readFileSync(new URL(p,root)));
const out=new URL('docs/astra-city/government-import/government-xl-ocean-walk-six-basic-interfaces-20261008/',root);assert(!existsSync(new URL('diagnostic.json',out)));mkdirSync(out,{recursive:true});
writeFileSync(new URL('diagnostic.json',out),JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,passed:r.interface.passed,samples:r.interface.samples,strictContacts:r.interface.strictContacts,unresolved:r.interface.unresolved.length}))));
