/** Read-only full-face distances at previously failed original contact samples. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const root=new URL('../../../',import.meta.url),[inputsPath,checksPath,outputPath]=process.argv.slice(2),hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const inputs=read(inputsPath),checks=read(checksPath),sources=new Map(inputs.sources.map(r=>[r.uid,r]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){if(loaded.has(uid))return loaded.get(uid);const r=sources.get(uid),b=readFileSync(new URL(r.candidate.path,root));assert.equal(sha(b),r.sourceSHA256);hashes[r.candidate.path]=sha(b);const m=await loadOfficialModel({...r.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},r.source.building,lighting,{fetcher:async()=>new Response(b)});loaded.set(uid,m);return m;}
const rows=[];
try{for(const row of checks.rows){
 const support=(await get(row.supportUid)).record.modelGeometry,source=(await get(row.uid)).record.modelGeometry;
 const tri=new THREE.Triangle(),p=new THREE.Vector3(),q=new THREE.Vector3(),normal=new THREE.Vector3();
 const samples=[];
 for(const raw of row.interface.unresolved){
  p.fromArray(raw.position);let nearest=null;const exact=[];
  for(let f=0;f<support.index.length/3;f++){
   [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(support.position,support.index[f*3+k]*3));tri.closestPointToPoint(p,q);const distanceM=p.distanceTo(q);
   if(!nearest||distanceM<nearest.distanceM){nearest={faceIndex:f,distanceM,point:q.toArray(),normal:tri.getNormal(normal).toArray(),vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()]};}
   if(distanceM<=.001)exact.push({faceIndex:f,distanceM,normal:tri.getNormal(normal).toArray(),vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()]});
  }
  const sourceFaces=[];
  for(let f=0;f<source.index.length/3;f++){
   [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(source.position,source.index[f*3+k]*3));tri.closestPointToPoint(p,q);if(p.distanceTo(q)<=.001)sourceFaces.push({faceIndex:f,normal:tri.getNormal(normal).toArray(),vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()]});
  }
  assert(nearest&&sourceFaces.length);samples.push({raw,nearestOriginalSupportFace:nearest,originalSupportFacesWithin1mm:exact,incidentOriginalSourceFaces:sourceFaces});
 }
 const buckets={within1mm:0,from1to10mm:0,from10to100mm:0,from100to500mm:0,over500mm:0};
 for(const s of samples){const d=s.nearestOriginalSupportFace.distanceM;buckets[d<=.001?'within1mm':d<=.01?'from1to10mm':d<=.1?'from10to100mm':d<=.5?'from100to500mm':'over500mm']++;}
 const result={uid:row.uid,supportUid:row.supportUid,sourceSHA256:sources.get(row.uid).sourceSHA256,supportSHA256:sources.get(row.supportUid).sourceSHA256,unresolvedSamples:samples.length,distanceBuckets:buckets,maximumNearestDistanceM:Math.max(...samples.map(s=>s.nearestOriginalSupportFace.distanceM)),samples};rows.push(result);console.log(JSON.stringify({...result,samples:undefined}));
}}finally{for(const m of loaded.values())disposeOfficialModel(m);}
for(const p of ['source-scripts/city/government-import/original-failed-interface-distances.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
writeFileSync(new URL(outputPath,root),gzipSync(JSON.stringify({rows,inputHashes:hashes,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,qualification:'Complete nearest-original-triangle distance diagnostics, not structural support or acceptance. All raw interface failures remain. Near walls can be parallel, unconnected or embedded; no distance bucket grants installation credit.'})));
