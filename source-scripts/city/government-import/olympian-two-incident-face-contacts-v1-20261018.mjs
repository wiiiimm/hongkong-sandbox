/** Exact source face/vertex contact context; preserves canonical low-rim failures. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {supportSurface} from './support-contact.mjs';
const dir=process.argv[2],out=process.argv[3];
const input=JSON.parse(gunzipSync(readFileSync(dir+'/geometry-inputs.json.gz'))),checks=JSON.parse(gunzipSync(readFileSync(dir+'/support-checks.json.gz')));
const support={position:[],index:[]};
for(const r of input.rows.filter(r=>!input.towerUIDs.includes(r.uid))){const n=support.position.length/3;for(const v of r.position)support.position.push(v);for(const i of r.index)support.index.push(i+n);}
const surface=supportSurface(support),rows=[];
for(const r of input.rows.filter(r=>input.towerUIDs.includes(r.uid))){
 const failures=checks.rows.find(x=>x.uid===r.uid).unresolved,cache=new Map(),sample=p=>{const k=p.join(',');if(!cache.has(k)){const h=surface.height(p[0],p[2]);cache.set(k,h===null?null:p[1]-h);}return cache.get(k);};
 const details=failures.map(f=>{
  const candidates=[];
  for(const face of f.originalSourceFaces)for(const p of face.vertices){const gap=sample(p);if(gap!==null&&gap>=-.1&&gap<=1)candidates.push({sourceFace:face.faceIndex,sourceTriangle:face.vertices,normal:face.normal,contact:p,gap,distanceM:Math.hypot(...p.map((x,i)=>x-f.position[i]))});}
  candidates.sort((a,b)=>a.distanceM-b.distanceM);
  return {position:f.position,reason:f.reason,originalGapM:f.gap??null,sameFaceContact:candidates[0]??null,incidentSourceFaces:f.originalSourceFaces};
 });
 const summary={uid:r.uid,sourceSHA256:r.sourceSHA256,canonicalFailures:failures.length,sameFaceContactWitnesses:details.filter(x=>x.sameFaceContact).length,unresolvedWithoutSameFaceContact:details.filter(x=>!x.sameFaceContact).length,maximumAlongFaceSpanM:Math.max(0,...details.filter(x=>x.sameFaceContact).map(x=>x.sameFaceContact.distanceM))};
 rows.push({...summary,details});console.log(JSON.stringify(summary));
}
writeFileSync(out,gzipSync(JSON.stringify({rows,fullAcceptance:false,qualification:'A failed point and a contacting original vertex on the same finite source triangle nominate authored surface context. Span is reported, not an admissible gap threshold. No raw canonical warning is waived; no source or pose changes.'})));
