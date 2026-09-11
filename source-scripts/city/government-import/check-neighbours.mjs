/** Compare existing neighbouring forms before/after staged terrain, without changing runtime. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrainSampler,inPolygon} from '../../../3d-viewer/city/geo.js';
const root=new URL('../../../',import.meta.url),doc=process.argv[2]||'docs/astra-city/government-import/government-200-20260911/resolution/',hash=b=>createHash('sha256').update(b).digest('hex'),inputs={};
const read=p=>{const raw=readFileSync(new URL(p,root));inputs[p]=hash(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};
const manifest=read('3d-viewer/city/data/manifest.json'),data=read('3d-viewer/city/data/terrain.json'),selection=read(doc+'neighbour-inputs.json.gz');
for(const [p,h] of Object.entries(selection.inputHashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
data.patches=manifest.terrainPatches.map(p=>read('3d-viewer/'+p.url));const before=makeTerrainSampler(data),patched={...data,patches:[...data.patches,...selection.patches.map(p=>{const d=read(p.path);assert.equal(inputs[p.path],p.sha256);return d;})]},after=makeTerrainSampler(patched),targets=new Set(selection.candidateIds),rows=[];
for(const {building:b,patchIndexes,existingNative} of selection.rows){
 const points=b.rings.flat().map(p=>[p[0],p[1]]),outer=b.rings[0],xs=outer.map(p=>p[0]),zs=outer.map(p=>p[1]),lo=[Math.min(...xs),Math.min(...zs)],hi=[Math.max(...xs),Math.max(...zs)];
 const step=Math.max(2,Math.sqrt((hi[0]-lo[0])*(hi[1]-lo[1])/2500));
 for(let x=lo[0]+step/2;x<hi[0];x+=step)for(let z=lo[1]+step/2;z<hi[1];z+=step)if(inPolygon(x,z,b.rings))points.push([x,z]);
 const old=points.map(([x,z])=>before.height(x,z)),next=points.map(([x,z])=>after.height(x,z)),base=b.base+(b.minimum||0),top=b.base+b.height,minOldGap=base-Math.max(...old),minNewGap=base-Math.max(...next),maxOldGap=base-Math.min(...old),maxNewGap=base-Math.min(...next),maxDelta=Math.max(...next.map((v,i)=>Math.abs(v-old[i]))),reasons=[];
 if(!targets.has(b.uid)){
  if(existingNative&&maxDelta>.004)reasons.push('existing-native-neighbour-requires-full-mesh-check');
  if(minNewGap<Math.min(-.5,minOldGap)-.25)reasons.push('increased-neighbour-burial');
  if(maxNewGap>Math.max(1,maxOldGap)+.25)reasons.push('increased-neighbour-ground-gap');
  if(Math.max(...next)>Math.max(top-.1,Math.max(...old))+.25)reasons.push('increased-neighbour-roof-burial');
 }
 rows.push({uid:b.uid,patchIndexes,checks:points.length,existingNative,candidate:targets.has(b.uid),maxGroundChange:maxDelta,beforeGap:[minOldGap,maxOldGap],afterGap:[minNewGap,maxNewGap],reasons});
}
const report={rows,inputHashes:inputs,sourceInputHashes:selection.inputHashes,patches:selection.patches.map((p,i)=>({...p,neighbours:rows.filter(r=>r.patchIndexes.includes(i)).length,blockedBy:rows.filter(r=>r.patchIndexes.includes(i)&&r.reasons.length).map(r=>r.uid)})),aiCalls:0,publication:false,qualification:'Conservative neighbour regression guard. Exact current source polygons and source heights, vertices and <=2m interior samples for ordinary forms. Existing native neighbours with changed ground need a separate full-mesh check. No model elevations moved.'};
writeFileSync(new URL(doc+'neighbour-checks.json',root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({forms:rows.length,flagged:rows.filter(r=>r.reasons.length).length,clearPatches:report.patches.filter(p=>!p.blockedBy.length).length,clearModels:report.patches.filter(p=>!p.blockedBy.length).flatMap(p=>p.uids).length}));
