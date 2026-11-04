/** Exact source support proof for the five already-installed Vision City towers. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..'),hash=raw=>createHash('sha256').update(raw).digest('hex'),inputHashes={};
const read=path=>{const raw=readFileSync(resolve(root,path));inputHashes[path]=hash(raw);return JSON.parse(raw);};
const stage='source-scripts/city/government-import/accepted/government-xl-citywalk-source-20261004/',
 doc='docs/astra-city/government-import/government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue/';
const support=read(stage+'catalogue.json').models[0],url='city/data/official-models/support-review-20260909/catalogue.json',
 cat=read('3d-viewer/'+url),towers=cat.models.filter(m=>m.supportDependencies?.some(d=>d.uid===support.uid));
assert.equal(towers.length,5);
const manifest=read('3d-viewer/city/data/manifest.json'),ids=new Set(towers.map(m=>m.uid)),forms=new Map([[support.uid,read(stage+'source-forms.json')[0]]]);
for(const tile of manifest.tiles){
 if(forms.size===6)break;
 const path='3d-viewer/'+tile.url,raw=readFileSync(resolve(root,path)),data=JSON.parse(raw);
 let touched=false;for(const b of data.buildings)if(ids.has(b.uid)){forms.set(b.uid,b);touched=true;}
 if(touched)inputHashes[path]=hash(raw);
}
assert.equal(forms.size,6);
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
async function geometry(entry,cataloguePath){
 const prepared=prepareModelCatalogue({...read(cataloguePath),models:[entry],counts:{packedModels:1}},pathToFileURL(resolve(root,cataloguePath)).href)[0],
 path=resolve(dirname(cataloguePath),entry.asset),raw=readFileSync(resolve(root,path));
 assert.equal(hash(raw),entry.sha256);inputHashes[path]=hash(raw);
 const model=await loadOfficialModel(prepared,forms.get(entry.uid),lighting,{fetcher:async()=>new Response(raw)}),g=model.record.modelGeometry,
 result={position:Array.from(g.position),index:Array.from(g.index)};
 disposeOfficialModel(model);return result;
}
const podium=await geometry(support,stage+'catalogue.json'),rows=[];
for(const tower of towers){
 const proof=verifySupportInterface(await geometry(tower,'3d-viewer/'+url),tower.worldBounds[0][1],podium);
 rows.push({uid:tower.uid,sourceSHA256:tower.sha256,supportUid:support.uid,supportSHA256:support.sha256,passed:proof.passed,interfaceProof:proof});
}
for(const path of ['source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs',
 'source-scripts/city/government-import/citywalk-tower-dependencies-20261004.mjs'])inputHashes[path]=hash(readFileSync(resolve(root,path)));
const report={rows,inputHashes,sourceGeometryChanged:false,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false};
writeFileSync(resolve(root,doc+'tower-support.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,passed:r.passed,samples:r.interfaceProof.samples,strict:r.interfaceProof.strictContacts,walls:r.interfaceProof.wallIntersections,failed:r.interfaceProof.unresolved.length}))));
