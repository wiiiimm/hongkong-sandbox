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
const currentForms=new Map();
for(const row of inputs.sources){const tile=read('3d-viewer/'+row.source.tile);for(const b of tile.buildings)currentForms.set(b.uid,b);assert.deepEqual(currentForms.get(row.uid),row.source.building);}
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){
 if(loaded.has(uid))return loaded.get(uid);
 const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.candidate.entry.sha256);
 let asset;
 try{asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>currentForms.get(uid)});}
 catch(error){if(error.message==='Official model does not fit its matched footprint')error.sourceUid=uid;throw error;}
 loaded.set(uid,asset);return asset;
}
const rows=[];
for(const p of ['source-scripts/city/government-import/ocean-walk-original-component-interfaces.mjs','3d-viewer/city/official-model-footprint-scopes.js','3d-viewer/city/official-model-footprint-scopes-ocean-walk.js','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
function save(){writeFileSync(new URL(base+'support-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false})));}
try{
 for(const pair of inputs.pairs){
  let source,support;
  try{source=await get(pair.uid);support=await get(pair.supportUid);}
  catch(error){
   if(error.message!=='Official model does not fit its matched footprint'||!error.sourceUid){save();throw error;}
   const result={...pair,sourceSHA256:sources.get(pair.uid).candidate.entry.sha256,supportSHA256:sources.get(pair.supportUid).candidate.entry.sha256,
    interface:null,loadFailure:{uid:error.sourceUid,reason:'runtime-source-footprint-fit',message:error.message},installationApproved:false};
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
