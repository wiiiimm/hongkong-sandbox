/** Complete exact source interfaces; source recovery is never acceptance. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),doc='docs/astra-city/government-import/government-xl-hsbc-centre-supports-20261005/',hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const towers=read(doc+'selection.json.gz').rows;
const podium=read('docs/astra-city/government-import/government-xl-next-100-20261005/check-selection.json.gz').rows.find(r=>r.uid==='landsd/265848:0');
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=[];
async function load(row){const raw=readFileSync(new URL(row.candidate.path,root));assert.equal(sha(raw),row.sourceSHA256);hashes[row.candidate.path]=sha(raw);
 const result=await loadOfficialModel({...row.candidate.entry,assetURL:'https://exact-source.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});loaded.push(result);return result;}
const rows=[];
try{const support=await load(podium);
 for(const row of towers){const asset=await load(row);const proof=verifySupportInterface(asset.record.modelGeometry,row.candidate.entry.worldBounds[0][1],support.record.modelGeometry);
  rows.push({uid:row.uid,supportUid:podium.uid,sourceSHA256:row.sourceSHA256,supportSHA256:podium.sourceSHA256,interface:proof});
  console.log(JSON.stringify({uid:row.uid,samples:proof.samples,strict:proof.strictContacts,walls:proof.wallIntersections,unresolved:proof.unresolved.length,passed:proof.passed}));
 }
}finally{for(const model of loaded)disposeOfficialModel(model);}
for(const path of ['source-scripts/city/government-import/hsbc-centre-native-interfaces-20261005.mjs','source-scripts/city/government-import/support-interface.mjs','3d-viewer/city/official-model-assets.js'])hashes[path]=sha(readFileSync(new URL(path,root)));
writeFileSync(new URL(doc+'interfaces.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,modelGeometryChanges:0,scriptExternalAICalls:0,publication:false})));
