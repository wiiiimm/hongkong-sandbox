/** Exact unchanged Florient Rise basic towers versus new original WEST9ZONE source. Diagnostic only. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),hashes={},hash=b=>createHash('sha256').update(b).digest('hex');
function read(path){const b=readFileSync(new URL(path,root));hashes[path]=hash(b);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const exportPath='source-scripts/city/government-import/local/government-xl-west9zone-current-retained-terrain-20261007/runtime-geometry.json.gz';
const exported=read(exportPath),support=exported.rows.find(r=>r.uid==='landsd/227099:0');assert(support);
for(const [p,h] of Object.entries(exported.inputHashes)){assert.equal(hash(readFileSync(new URL(p,root))),h);hashes[p]=h;}
const doc='docs/astra-city/government-import/government-xl-west9zone-current-retained-terrain-20261007/';
const inputs=read(doc+'neighbour-inputs.json.gz'),manifest=read('3d-viewer/city/data/manifest.json');
const installed=manifest.officialModelCatalogues.flatMap(u=>read('3d-viewer/'+u).models);
const selection=read(doc+'selection.json.gz');const entry=selection.rows.find(r=>r.uid===support.uid);assert(entry&&entry.sourceSHA256===support.sourceSHA256);
const rows=[];
for(const [uid,csuid] of [['landsd/81972:0','3467319919T20090204'],['landsd/83691:0','3467519990T20090204']]){
 const b=inputs.rows.find(r=>r.building.uid===uid)?.building;assert(b&&b.structureType==='Tower'&&b.buildingCSUID===csuid&&!installed.some(r=>r.uid===uid));
 const tile=manifest.tiles.find(t=>read('3d-viewer/'+t.url).buildings.some(f=>f.uid===uid));assert(tile);
 assert.deepEqual(read('3d-viewer/'+tile.url).buildings.find(f=>f.uid===uid),b);
 const geometry=createBuildingGeometry(b);
 try{
  const position=Array.from(geometry.attributes.position.array),index=geometry.index?Array.from(geometry.index.array):Array.from({length:position.length/3},(_,i)=>i);
  const proof=verifySupportInterface({position,index},b.base+(b.minimum||0),{position:support.position,index:support.index});
  rows.push({uid,buildingCSUID:csuid,supportUid:support.uid,supportCSUID:entry.source.buildingCSUID,supportSHA256:support.sourceSHA256,interface:proof,strictAllContacts:proof.samples>0&&proof.strictContacts===proof.samples&&proof.unresolved.length===0});
 }finally{geometry.dispose();}
}
for(const p of ['source-scripts/city/government-import/west9zone-basic-new-source-support-diagnostic.mjs','3d-viewer/city/building-geometry.js','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs'])hashes[p]=hash(readFileSync(new URL(p,root)));
for(const [p,h] of Object.entries(hashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
const output='source-scripts/city/government-import/local/government-xl-distinct-three-source-followthrough-20261007/west9zone-basic-new-source-support.json';assert(!existsSync(new URL(output,root)));
writeFileSync(new URL(output,root),JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,qualification:'Explicit exact UID/CSUID geometries only. Different OSM parents are retained as raw source data. Contact alone does not establish compound identity or grant neighbour acceptance.'},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,samples:r.interface.samples,strict:r.interface.strictContacts,unresolved:r.interface.unresolved.length,strictAll:r.strictAllContacts}))));
