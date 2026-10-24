/** Real held-source incident-face equivalence and local CPU measurements. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {performance} from 'node:perf_hooks';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {createSourceFaceQuery} from './source-face-query.mjs';
import {supportSurface} from './support-contact.mjs';

const root=resolve(new URL('../../../',import.meta.url).pathname),prior=JSON.parse(readFileSync(process.argv[2])),inputs=JSON.parse(readFileSync(process.argv[3])),output=process.argv[4];
const hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={},rows=[],lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
async function geometry(uid){
 const source=inputs.sources[uid],raw=readFileSync(resolve(root,source.path));assert.equal(hash(raw),source.entry.sha256);inputHashes[source.path]=hash(raw);
 const model=await loadOfficialModel({...source.entry,assetURL:'https://diagnostic.invalid/source.glb.gz'},source.form,lighting,{fetcher:async()=>new Response(raw)});
 try{return {position:Array.from(model.record.modelGeometry.position),index:Array.from(model.record.modelGeometry.index)};}finally{disposeOfficialModel(model);}
}
// Frozen 4 October incidentFaces algorithm: identical AABB and narrow-phase rules.
function baseline(g,position,tolerance=.001){
 const p=new THREE.Vector3(...position),closest=new THREE.Vector3(),triangle=new THREE.Triangle(),hits=[];
 for(let i=0;i<g.index.length;i+=3){
  const vertices=[0,1,2].map(k=>Array.from(g.position.slice(g.index[i+k]*3,g.index[i+k]*3+3)));
  if([0,1,2].some(k=>position[k]<Math.min(...vertices.map(v=>v[k]))-tolerance||position[k]>Math.max(...vertices.map(v=>v[k]))+tolerance))continue;
  [triangle.a,triangle.b,triangle.c].forEach((v,k)=>v.set(...vertices[k]));triangle.closestPointToPoint(p,closest);
  const distanceM=closest.distanceTo(p);if(distanceM<=tolerance)hits.push({faceIndex:i/3,vertices,distanceM,normal:triangle.getNormal(new THREE.Vector3()).toArray()});
 }return hits;
}
const median=v=>[...v].sort((a,b)=>a-b)[Math.floor(v.length/2)];
for(const row of prior.rows.filter(r=>r.proof.unresolved.length)){
 const g=await geometry(row.uid),support=await geometry(row.supportUid),surface=supportSurface(support);
 const points=row.proof.unresolved.map(f=>f.position),metrics={},start=performance.now(),query=createSourceFaceQuery(g,{metrics}),indexBuildMs=performance.now()-start;
 const indexResults=points.map(query),baselineStart=performance.now(),baselineResults=points.map(p=>baseline(g,p)),baselineFullMs=performance.now()-baselineStart;
 assert.deepEqual(indexResults,baselineResults,'Source face evidence changed for '+row.uid);
 // Full baseline is measured once to avoid spending the saving on repeated slow scans.
 const timed=[];for(let run=0;run<3;run++){const t=performance.now();points.forEach(query);timed.push(performance.now()-t);}
 const indexedFullMs=indexBuildMs+median(timed),diagnostics=[];
 for(let i=0;i<points.length;i++){
  const p=points[i],deck=surface.height(p[0],p[2]),deckHits=deck===null?[]:query([p[0],deck,p[2]]),deckIds=new Set(deckHits.map(f=>f.faceIndex));
  diagnostics.push({position:p,sourceFaces:indexResults[i],deckHeight:deck,
   sameOriginalWallFaces:indexResults[i].filter(f=>Math.abs(f.normal[1])<=1e-6&&deckIds.has(f.faceIndex)).map(f=>f.faceIndex)});
 }
 rows.push({uid:row.uid,supportUid:row.supportUid,sourceSHA256:row.sourceSHA256,supportSHA256:row.supportSHA256,
  unresolvedSamples:points.length,sourceFacesLocated:indexResults.filter(r=>r.length).length,completeBaselineEvidenceEqual:true,
  benchmark:{baselineFullMs,indexBuildMs,indexedQueryMedianMs:median(timed),indexedFullMs,speedup:baselineFullMs/indexedFullMs,indexedWarmRuns:3,baselineRuns:1},
  metrics,diagnostics,installationApproved:false});
 console.log(JSON.stringify({uid:row.uid,unresolved:points.length,sourceFacesLocated:indexResults.filter(r=>r.length).length,baselineMs:baselineFullMs,indexedMs:indexedFullMs,speedup:baselineFullMs/indexedFullMs}));
}
for(const path of ['source-scripts/city/government-import/workflow-face-benchmark.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/triangle-point-index.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])inputHashes[path]=hash(readFileSync(resolve(root,path)));
writeFileSync(output,gzipSync(JSON.stringify({rows,inputHashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false,
 qualification:'Complete original incident-face outputs match exactly for every unresolved source sample. CPU timing includes index build, excludes source decoding, support indexing, terrain and browser work. Diagnostic lookup improvement is not whole-pipeline speedup or installation approval.'})));
