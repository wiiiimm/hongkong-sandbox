/** Compare unchanged acceptance and diagnose exact source interfaces in a fresh stage. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {performance} from 'node:perf_hooks';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
import {supportSurface} from './support-contact.mjs';
import {trianglePointIndex} from './triangle-point-index.mjs';

const root=resolve(new URL('../../../',import.meta.url).pathname),inputPath=resolve(process.argv[2]),outputPath=resolve(process.argv[3]);
const input=JSON.parse(readFileSync(inputPath)),hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={};
const baseline=await import(pathToFileURL(resolve(root,input.baseline.path)).href);
assert.equal(hash(readFileSync(resolve(root,input.baseline.path))),input.baseline.sha256);
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},cache=new Map();
async function geometry(uid){
 if(cache.has(uid))return cache.get(uid);
 const source=input.sources[uid];assert(source,'Missing exact source '+uid);
 const path=resolve(root,source.path),raw=readFileSync(path);assert.equal(hash(raw),source.entry.sha256);inputHashes[source.path]=hash(raw);
 const model=await loadOfficialModel({...source.entry,assetURL:'https://diagnostic.invalid/source.glb.gz'},source.form,lighting,{fetcher:async()=>new Response(raw)});
 try{const g=model.record.modelGeometry,result={position:Array.from(g.position),index:Array.from(g.index)};cache.set(uid,result);return result;}
 finally{disposeOfficialModel(model);}
}
function incident(g,index,position){
 const tri=new THREE.Triangle(),point=new THREE.Vector3(...position),closest=new THREE.Vector3(),hits=[];
 for(const faceIndex of index.candidates(position)){
  [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(g.position,g.index[faceIndex*3+k]*3));
  tri.closestPointToPoint(point,closest);
  if(closest.distanceTo(point)<=.001)hits.push({faceIndex,vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()],normal:tri.getNormal(new THREE.Vector3()).toArray()});
 }return hits;
}
const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)],rows=[];
for(const pair of input.pairs){
 const {uid,supportUid}=pair,g=await geometry(uid),support=await geometry(supportUid),bottom=input.sources[uid].entry.worldBounds[0][1];
 const metrics={},proof=verifySupportInterface(g,bottom,support,{metrics}),reference=baseline.verifySupportInterface(g,bottom,support);
 assert.deepEqual(proof,reference,'Indexed checker changed complete acceptance evidence for '+uid);
 const elapsed={baseline:[],indexed:[]};
 for(let run=0;run<3;run++)for(const mode of run%2?['indexed','baseline']:['baseline','indexed']){
  const start=performance.now();(mode==='baseline'?baseline.verifySupportInterface:verifySupportInterface)(g,bottom,support);elapsed[mode].push(performance.now()-start);
 }
 const benchmark={baselineMedianMs:median(elapsed.baseline),indexedMedianMs:median(elapsed.indexed),runs:3,elapsedMs:elapsed};
 const diagnostic=[];
 if(pair.inspectUnresolved){
  const index=trianglePointIndex(g),surface=supportSurface(support);
  for(const failure of proof.unresolved){
   const [x,y,z]=failure.position,deck=surface.height(x,z),sourceFaces=incident(g,index,failure.position);
   const deckFaces=deck===null?[]:incident(g,index,[x,deck,z]),deckIds=new Set(deckFaces.map(f=>f.faceIndex));
   const sameVerticalFaces=sourceFaces.filter(f=>Math.abs(f.normal[1])<=1e-6&&deckIds.has(f.faceIndex));
   diagnostic.push({...failure,sourceFaceIndices:sourceFaces.map(f=>f.faceIndex),sameOriginalVerticalWallFaces:sameVerticalFaces.map(f=>f.faceIndex),
    classification:deck===null?'missing-vertical-support':sameVerticalFaces.length?'same-wall-intersection-outside-current-contract':sourceFaces.length?'source-face-present-no-same-wall-contact':'source-sample-face-not-found'});
  }
 }
 const row={uid,supportUid,sourceSHA256:input.sources[uid].entry.sha256,supportSHA256:input.sources[supportUid].entry.sha256,
  proof,metrics,benchmark,completeEvidenceEqual:true,unresolvedSourceDiagnostics:diagnostic,installationApproved:false};
 rows.push(row);console.log(JSON.stringify({uid,samples:proof.samples,strict:proof.strictContacts,walls:proof.wallIntersections,unresolved:proof.unresolved.length,baselineMs:benchmark.baselineMedianMs,indexedMs:benchmark.indexedMedianMs,exactTests:metrics.exactTriangleTests,oldTriangleVisits:metrics.priorFullScanTriangleVisits}));
}
for(const path of ['source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs','source-scripts/city/government-import/workflow-support-check.mjs','3d-viewer/city/official-model-assets.js'])inputHashes[path]=hash(readFileSync(resolve(root,path)));
writeFileSync(outputPath,JSON.stringify({rows,inputHashes,sourceGeometryChanged:false,publication:false,modelGeometryChanges:0,scriptExternalAICalls:0,
 qualification:'Full indexed and baseline support-interface outputs match exactly. Timings are local CPU microbenchmarks, not whole-pipeline throughput or viewer FPS. Source-face diagnostics do not expand the 0.5m interface contract or grant installation.'},null,2)+'\n');
