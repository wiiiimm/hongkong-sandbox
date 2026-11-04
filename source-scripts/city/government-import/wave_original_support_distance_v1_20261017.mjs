/** Incremental exact support evidence; retain runtime rejections per pair. No approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {supportSurface} from './support-contact.mjs';
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
 catch(error){if(error.message==='Official model does not fit its matched footprint')error.sourceUid=uid;throw error;}
 loaded.set(uid,asset);return asset;
}
const rows=[];
for(const p of ['source-scripts/city/government-import/wave_original_support_distance_v1_20261017.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
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
  const query=createSourceFaceQuery(geometry), layers=supportSurface(support.record.modelGeometry);
  const supportGeometry=support.record.modelGeometry, tri=new THREE.Triangle(), pt=new THREE.Vector3(), nearest=new THREE.Vector3(), norm=new THREE.Vector3();
  const nearestPodiumFace=position=>{pt.fromArray(position);let best=null;for(let i=0;i<supportGeometry.index.length;i+=3){[tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(supportGeometry.position,supportGeometry.index[i+k]*3));tri.closestPointToPoint(pt,nearest);const distanceM=nearest.distanceTo(pt);if(!best||distanceM<best.distanceM)best={faceIndex:i/3,distanceM,closestPoint:nearest.toArray(),normal:tri.getNormal(norm).toArray(),vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()]};}return best;};
  const unresolved=proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position),nearestPodiumFace:nearestPodiumFace(f.position),allOriginalPodiumLayers:layers.intersectionDetails(f.position[0],f.position[2]).map(h=>({...h,gap:f.position[1]-h.height}))}));
  const result={...pair,sourceSHA256:sources.get(pair.uid).candidate.entry.sha256,supportSHA256:sources.get(pair.supportUid).candidate.entry.sha256,
   interface:proof,unresolved,installationApproved:false};
  rows.push(result);save();console.log(JSON.stringify({uid:pair.uid,supportUid:pair.supportUid,passed:proof.passed,samples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length}));
 }
}finally{for(const model of loaded.values())disposeOfficialModel(model);}
save();
