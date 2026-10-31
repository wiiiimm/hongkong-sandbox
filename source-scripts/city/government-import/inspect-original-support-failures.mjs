/** Inspect exact original support surfaces at failed samples; no acceptance. */
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
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'support-inputs.json'),checks=read(base+'support-checks.json.gz');
const sources=new Map(inputs.sources.map(r=>[r.uid,r]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const rows=[];
for(const check of checks.rows){
 const row=sources.get(check.supportUid),raw=readFileSync(new URL(row.candidate.path,root));
 hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),check.supportSHA256);
 const asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
 try{
  const geometry=asset.record.modelGeometry,surface=supportSurface(geometry);
  const tri=new THREE.Triangle(),point=new THREE.Vector3(),nearest=new THREE.Vector3();
  const samples=[];
  for(const failure of check.interface.unresolved){
   point.fromArray(failure.position);let best=null;
   for(let i=0;i<geometry.index.length;i+=3){
    [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(geometry.position,geometry.index[i+k]*3));
    tri.closestPointToPoint(point,nearest);const distance=point.distanceTo(nearest);
    if(!best||distance<best.distanceM)best={faceIndex:i/3,distanceM:distance,
     closestOriginalPosition:nearest.toArray(),horizontalDistanceM:Math.hypot(point.x-nearest.x,point.z-nearest.z),
     verticalGapM:point.y-nearest.y,vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()]};
   }
   const layers=surface.intersectionDetails(point.x,point.z);
   samples.push({...failure,exactVerticalLayers:layers,nearestOriginalSupportFace:best,
    hasContactLayer:layers.some(h=>point.y-h.height>=-.1&&point.y-h.height<=1),
    contactWithinExistingOneMillimetre:best.distanceM<=.001});
  }
  rows.push({uid:check.uid,supportUid:check.supportUid,sourceSHA256:check.sourceSHA256,
   supportSHA256:check.supportSHA256,samples,unresolved:samples.length,
   withinExistingOneMillimetre:samples.filter(s=>s.contactWithinExistingOneMillimetre).length,
   unchangedInterfacePassed:check.interface.passed,installationApproved:false});
 }finally{disposeOfficialModel(asset);}
}
for(const p of ['source-scripts/city/government-import/inspect-original-support-failures.mjs',
 'source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
const result={rows,inputHashes:hashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false,
 qualification:'Exact unchanged support-face and layer diagnostics. No contact limit, highest-surface rule or physical/publication gate is changed.'};
writeFileSync(new URL(base+'support-failure-surfaces.json.gz',root),gzipSync(JSON.stringify(result)));
console.log(JSON.stringify(rows.map(({samples,...r})=>r)));
