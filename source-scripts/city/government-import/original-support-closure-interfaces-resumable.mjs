/** Incremental exact support evidence; retain runtime rejections per pair. No approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'support-inputs.json'),sources=new Map(inputs.sources.map(r=>[r.uid,r]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){
 if(loaded.has(uid))return loaded.get(uid);
 const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.candidate.entry.sha256);
 let asset;
 try{asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});}
 catch(error){if(['Official model does not fit its matched footprint','Model does not match the loaded official building source'].includes(error.message))error.sourceUid=uid;throw error;}
 loaded.set(uid,asset);return asset;
}
const previousBase=process.argv[3];
assert(previousBase?.startsWith('docs/astra-city/government-import/government-xl-')&&previousBase.endsWith('/')&&!previousBase.includes('..'));
const previous=read(previousBase+'support-checks.json.gz'),previousInputs=read(previousBase+'support-inputs.json');
for(const [path,expected] of Object.entries(previous.inputHashes)){
 const actual=sha(readFileSync(new URL(path,root)));assert.equal(actual,expected);hashes[path]=actual;
}
const previousSources=new Map(previousInputs.sources.map(r=>[r.uid,r]));
const rows=[];
for(const p of ['source-scripts/city/government-import/original-support-closure-interfaces-resumable.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
function save(){writeFileSync(new URL(base+'support-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false})));}
try{
 for(const pair of inputs.pairs){
  const prior=previous.rows.filter(r=>r.uid===pair.uid&&r.supportUid===pair.supportUid);
  assert(prior.length<=1);
  if(prior.length){
   for(const uid of [pair.uid,pair.supportUid])assert.equal(JSON.stringify(previousSources.get(uid)),JSON.stringify(sources.get(uid)));
   assert.equal(prior[0].sourceSHA256,sources.get(pair.uid).sourceSHA256);assert.equal(prior[0].supportSHA256,sources.get(pair.supportUid).sourceSHA256);
   rows.push(prior[0]);save();console.log(JSON.stringify({uid:pair.uid,supportUid:pair.supportUid,reusedSavedInterface:true}));continue;
  }
  let source,support;
  try{source=await get(pair.uid);support=await get(pair.supportUid);}
  catch(error){
   if(!['Official model does not fit its matched footprint','Model does not match the loaded official building source'].includes(error.message)||!error.sourceUid){save();throw error;}
   const result={...pair,sourceSHA256:sources.get(pair.uid).candidate.entry.sha256,supportSHA256:sources.get(pair.supportUid).candidate.entry.sha256,
    interface:null,loadFailure:{uid:error.sourceUid,reason:error.message==='Official model does not fit its matched footprint'?'runtime-source-footprint-fit':'runtime-source-binding',message:error.message},installationApproved:false};
   rows.push(result);save();console.log(JSON.stringify(result));continue;
  }
  const geometry=source.record.modelGeometry;
  const proof=verifySupportInterface(geometry,sources.get(pair.uid).candidate.entry.worldBounds[0][1],support.record.modelGeometry);
  const query=createSourceFaceQuery(geometry);
  const unresolved=proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)}));
  const result={...pair,sourceSHA256:sources.get(pair.uid).candidate.entry.sha256,supportSHA256:sources.get(pair.supportUid).candidate.entry.sha256,
   interface:proof,unresolved,installationApproved:false};
  rows.push(result);save();console.log(JSON.stringify({uid:pair.uid,supportUid:pair.supportUid,passed:proof.passed,samples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length}));
 }
}finally{for(const model of loaded.values())disposeOfficialModel(model);}
save();
