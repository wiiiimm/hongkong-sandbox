/** Exact original-source support probes for this bounded continuation; no approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-next-100-20261005/',hashes={};
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'installed-support-inputs.json'),sources=new Map(inputs.sources.map(r=>[r.uid,r]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){
 if(loaded.has(uid))return loaded.get(uid);
 const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.candidate.entry.sha256);
 const asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
 loaded.set(uid,asset);return asset;
}
const rows=[];
try{
 for(const pair of inputs.pairs){
  const source=await get(pair.uid),support=await get(pair.supportUid),geometry=source.record.modelGeometry;
  const proof=verifySupportInterface(geometry,sources.get(pair.uid).candidate.entry.worldBounds[0][1],support.record.modelGeometry);
  const query=createSourceFaceQuery(geometry);
  const unresolved=proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)}));
  const result={...pair,sourceSHA256:sources.get(pair.uid).candidate.entry.sha256,supportSHA256:sources.get(pair.supportUid).candidate.entry.sha256,
   interface:proof,unresolved,installationApproved:false};
  rows.push(result);console.log(JSON.stringify({uid:pair.uid,supportUid:pair.supportUid,passed:proof.passed,samples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length}));
 }
}finally{for(const model of loaded.values())disposeOfficialModel(model);}
for(const p of ['source-scripts/city/government-import/xl-next100-installed-supports-20261005.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
writeFileSync(new URL(base+'installed-support-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false})));
