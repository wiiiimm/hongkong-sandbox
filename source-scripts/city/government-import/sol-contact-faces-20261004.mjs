/** Resolve failed contact samples to original loaded triangles; no acceptance or edits. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {supportSurface} from './support-contact.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-remaining-20260923/',inputs={};
const sha=b=>createHash('sha256').update(b).digest('hex');
const read=p=>{const b=readFileSync(new URL(p,root));inputs[p]=sha(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);};
const prior=read(base+'sol-continuation-20261003/support-contact.json');
const sources=new Map();
for(const p of ['sol-continuation-20261003/ocean-pride/selection.json.gz','festival-pair-rescue-diagnostic-20261002/selection.json.gz'])for(const row of read(base+p).rows)sources.set(row.uid,row);
// Use the live, verified installed podium rather than its independently repacked copy.
const catPath='3d-viewer/city/data/official-models/government-xl-held-surface-20260914/catalogue.json',cat=read(catPath),entry=cat.models.find(e=>e.uid==='landsd/175935:0');
const support=sources.get(entry.uid);sources.set(entry.uid,{...support,candidate:{entry:{rootTranslation:cat.rootTranslation,...entry},path:catPath.slice(0,catPath.lastIndexOf('/')+1)+entry.asset}});
const saxonPath='source-scripts/city/government-import/accepted/government-xxl-saxon-20260911/',saxon=read(saxonPath+'catalogue.json'),saxonForms=read(saxonPath+'source-forms.json');
for(const e of saxon.models)sources.set(e.uid,{source:{building:saxonForms.find(b=>b.uid===e.uid)},candidate:{entry:{rootTranslation:saxon.rootTranslation,...e},path:saxonPath+e.asset}});
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
function incidentFaces(g,position,tolerance=.001){
 const p=new THREE.Vector3(...position),closest=new THREE.Vector3(),triangle=new THREE.Triangle(),hits=[];
 for(let i=0;i<g.index.length;i+=3){
  const vertices=[0,1,2].map(k=>Array.from(g.position.slice(g.index[i+k]*3,g.index[i+k]*3+3)));
  if([0,1,2].some(k=>position[k]<Math.min(...vertices.map(v=>v[k]))-tolerance||position[k]>Math.max(...vertices.map(v=>v[k]))+tolerance))continue;
  [triangle.a,triangle.b,triangle.c].forEach((v,k)=>v.set(...vertices[k]));triangle.closestPointToPoint(p,closest);
  const distance=closest.distanceTo(p);if(distance<=tolerance)hits.push({faceIndex:i/3,vertices,distanceM:distance,normal:triangle.getNormal(new THREE.Vector3()).toArray()});
 }
 return hits;
}
async function geometry(uid){const row=sources.get(uid),p=row.candidate.path;const raw=readFileSync(p.startsWith('/')?p:new URL(p,root));assert.equal(sha(raw),row.candidate.entry.sha256);inputs[p]=sha(raw);const loaded=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});try{return loaded.record.modelGeometry;}finally{disposeOfficialModel(loaded);}}
const rows=[];
for(const uid of ['landsd/273839:0','landsd/104302:0']){
 const previous=prior.rows.find(r=>r.uid===uid),g=await geometry(uid),s=await geometry(previous.supportUid),other=supportSurface(s);
 const failed=previous.failed.map(f=>{
  const [x,y,z]=f.position;
  // Vertical walls and edge-interior rim samples have no vertical-ray hit;
  // locate their original triangles in 3D instead of treating them as absent.
  const ownHits=incidentFaces(g,f.position);
  const supportHits=other.intersectionDetails(x,z);
  return {...f,sourceFacesAtSample:ownHits,supportFaces:supportHits,
   supportAboveSource:supportHits.filter(h=>h.height-y>.1).length};
 });
 const depths=failed.filter(f=>f.reason==='support-above-rim').map(f=>-f.gap);
 const interfaceProof=verifySupportInterface(g,sources.get(uid).candidate.entry.worldBounds[0][1],s);
 const row={uid,supportUid:previous.supportUid,sourceSHA256:previous.sourceSHA256,supportSHA256:previous.supportSHA256,interfaceProof,
  failedSamples:failed.length,sourceFacesLocated:failed.filter(f=>f.sourceFacesAtSample.length).length,
  embeddedSamples:depths.length,maximumEmbeddingM:depths.length?Math.max(...depths):0,
  failed,qualification:'Original loaded triangle indices and barycentric intersections only. Embedded coordinates and connected components do not prove semantic support or permit installation.',publication:false,modelGeometryChanges:0};
 rows.push(row);console.log(JSON.stringify({uid,failedSamples:row.failedSamples,sourceFacesLocated:row.sourceFacesLocated,embeddedSamples:row.embeddedSamples,maximumEmbeddingM:row.maximumEmbeddingM,interfacePassed:interfaceProof.passed}));
}
const saxonTower=await geometry('landsd/76364:0'),saxonPodium=await geometry('landsd/232025:0'),saxonProof=verifySupportInterface(saxonTower,sources.get('landsd/76364:0').candidate.entry.worldBounds[0][1],saxonPodium);
assert(saxonProof.passed,'The existing accepted source pair must retain its strict support result');
const representativeChecks=[{uid:'landsd/76364:0',supportUid:'landsd/232025:0',previouslyInstalled:true,passed:saxonProof.passed,strictContacts:saxonProof.strictContacts,wallIntersections:saxonProof.wallIntersections,samples:saxonProof.samples},...rows.map(r=>({uid:r.uid,supportUid:r.supportUid,passed:r.interfaceProof.passed,strictContacts:r.interfaceProof.strictContacts,wallIntersections:r.interfaceProof.wallIntersections,samples:r.interfaceProof.samples}))];
for(const p of ['source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/sol-contact-faces-20261004.mjs','3d-viewer/city/official-model-assets.js']){const b=readFileSync(new URL(p,root));inputs[p]=sha(b);}
const output=new URL(base+'sol-hold-resolution-20261004/contact-faces.json.gz',root);mkdirSync(new URL('.',output),{recursive:true});writeFileSync(output,gzipSync(JSON.stringify({rows,representativeChecks,inputHashes:inputs,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false})));
