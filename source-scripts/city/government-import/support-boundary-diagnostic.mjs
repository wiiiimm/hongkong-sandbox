/** Inspect exact failed rays and nearby rays; never change a contact decision. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function bytes(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return raw;}
function read(path){const raw=bytes(path);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const input=read(base+'inputs.json'),rows=[];
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
for(const scope of input.scopes){
 const sources=read(scope.previous+'/support-inputs.json').sources;
 const checks=read(scope.previous+'/support-checks.json.gz');
 const pairs=checks.rows.filter(r=>scope.uids.includes(r.uid));
 assert.equal(pairs.length,scope.uids.length);
 for(const pair of pairs){
  const row=sources.find(r=>r.uid===pair.supportUid),raw=bytes(row.candidate.path);
  assert.equal(sha(raw),pair.supportSHA256);assert.equal(sha(raw),row.sourceSHA256);
  const source=sources.find(r=>r.uid===pair.uid);
  assert.equal(sha(bytes(source.candidate.path)),pair.sourceSHA256);
  const model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
  try{
   const surface=supportSurface(model.record.modelGeometry);
   const failures=pair.unresolved.map(f=>{
    const exact=surface.intersectionDetails(f.position[0],f.position[2]);
    const highest=exact.at(-1),exactGap=highest?f.position[1]-highest.height:null;
    assert.equal(exactGap,f.gap??null,'The frozen failed ray changed');
    const probes=[];
    for(const distance of [.001,.01])for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){
     const x=f.position[0]+distance*dx,z=f.position[2]+distance*dz,hits=surface.intersectionDetails(x,z),hit=hits.at(-1);
     probes.push({offsetXZ:[distance*dx,distance*dz],highestHeight:hit?.height??null,gap:hit?f.position[1]-hit.height:null,highestFace:hit?.faceIndex??null});
    }
    return {...f,exactIntersections:exact,nearbyRays:probes,
     contactLayerPresent:exact.some(hit=>{const gap=f.position[1]-hit.height;return gap>=-.1&&gap<=1;}),
     highestBoundaryHit:highest?Math.min(...highest.barycentric)<=1e-7:false,
     qualification:'Offsets diagnose support boundaries only. They do not move the source, replace its original ray or clear a failed contact.'};
   });
   rows.push({uid:pair.uid,supportUid:pair.supportUid,sourceSHA256:pair.sourceSHA256,supportSHA256:pair.supportSHA256,
    originalInterfacePassed:pair.interface.passed,originalSamples:pair.interface.samples,failures,installationApproved:false});
  }finally{disposeOfficialModel(model);}
 }
}
for(const path of ['source-scripts/city/government-import/support-boundary-diagnostic.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])bytes(path);
writeFileSync(new URL(base+'boundary-rays.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,modelGeometryChanges:0,scriptExternalAICalls:0,publication:false})));
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,failed:r.failures.length,boundaryHits:r.failures.filter(f=>f.highestBoundaryHit).length,lowerContactLayer:r.failures.filter(f=>f.contactLayerPresent).length}))));
