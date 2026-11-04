/** Diagnostic only: compare the viewer's actual roof/post volumes on candidate terrain. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
import {describeBuilding,isOpenSidedBuilding} from '../../../3d-viewer/city/building-geometry.js';
import {makeTerrainSampler,inPolygon} from '../../../3d-viewer/city/geo.js';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const doc=process.argv[2];assert(doc,'A fresh diagnostic folder is required');
const hashes={},sha=raw=>createHash('sha256').update(raw).digest('hex');
const read=path=>{const raw=readFileSync(resolve(root,path));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);};
const manifest=read('3d-viewer/city/data/manifest.json'),base=read('3d-viewer/city/data/terrain.json');
const installed=manifest.terrainPatches.map(entry=>({entry,data:read('3d-viewer/'+entry.url)}));
const before=makeTerrainSampler({...base,patches:installed.map(row=>row.data)});
const cases=read(doc+'/selection.json'),rows=[];
for(const item of cases.rows){
 const selection=read(item.document+'/neighbour-inputs.json.gz');
 const historical=read(item.document+'/neighbour-checks.json');
 for(const [path,expected] of Object.entries(selection.inputHashes))assert.equal(sha(readFileSync(resolve(root,path))),expected,path);
 const replacements=new Set(selection.patches.flatMap(p=>p.replaces?[p.replaces.url]:[]));
 const unavailable=[...replacements].filter(url=>!installed.some(row=>row.entry.url===url));
 if(unavailable.length){
  rows.push({document:item.document,candidateIds:selection.candidateIds,neighbours:item.neighbours,skipped:true,reason:'historical-replacement-no-longer-current',unavailable,actualPartRegressionPassed:false,installationApproved:false});
  continue;
 }
 for(const p of selection.patches)if(p.replaces)assert.equal(hashes['3d-viewer/'+p.replaces.url],p.replaces.sha256,'Current replacement bytes must match');
 const proposed=selection.patches.map(p=>{const data=read(p.path);assert.equal(hashes[p.path],p.sha256);return data;});
 const after=makeTerrainSampler({...base,patches:[...installed.filter(row=>!replacements.has(row.entry.url)).map(row=>row.data),...proposed]});
 for(const uid of item.neighbours){
  const source=selection.rows.find(row=>row.building.uid===uid);assert(source&&!source.existingNative);
  const b=source.building,description=describeBuilding(b);
  assert(isOpenSidedBuilding(b)&&!b.modelGeometry&&!description.model&&!description.estimate);
  assert(description.parts.every(part=>part.kind==='roof'||part.kind==='post'));
  const parts=description.parts.map(part=>{
   const outer=part.rings[0],xs=outer.map(p=>p[0]),zs=outer.map(p=>p[1]);
   const lo=[Math.min(...xs),Math.min(...zs)],hi=[Math.max(...xs),Math.max(...zs)];
   const points=part.rings.flat().map(p=>[Math.fround(p[0]),Math.fround(p[1])]);
   const step=Math.min(2,Math.max(.05,Math.min(hi[0]-lo[0],hi[1]-lo[1])));
   for(let x=lo[0]+step/2;x<hi[0];x+=step)for(let z=lo[1]+step/2;z<hi[1];z+=step)if(inPolygon(x,z,part.rings))points.push([Math.fround(x),Math.fround(z)]);
   const old=points.map(([x,z])=>before.height(x,z)),next=points.map(([x,z])=>after.height(x,z));
   const bottom=Math.fround(part.bottom),top=Math.fround(part.top);
   const minOldGap=bottom-Math.max(...old),minNewGap=bottom-Math.max(...next),maxOldGap=bottom-Math.min(...old),maxNewGap=bottom-Math.min(...next),reasons=[];
   if(minNewGap<Math.min(-.5,minOldGap)-.25)reasons.push('increased-rendered-part-burial');
   if(part.kind==='post'&&maxNewGap>Math.max(1,maxOldGap)+.25)reasons.push('increased-rendered-post-ground-gap');
   if(Math.max(...next)>Math.max(top-.1,Math.max(...old))+.25)reasons.push('increased-rendered-part-top-burial');
   return {kind:part.kind,bottom,top,samples:points.length,beforeGap:[minOldGap,maxOldGap],afterGap:[minNewGap,maxNewGap],reasons};
  });
  assert(parts.filter(part=>part.kind==='post').length>=2,'No support credit for a roof without rendered posts');
  rows.push({document:item.document,candidateIds:selection.candidateIds,uid,previousReasons:historical.rows.find(row=>row.uid===uid).reasons,parts,actualPartRegressionPassed:parts.every(part=>!part.reasons.length),installationApproved:false});
 }
}
for(const path of ['3d-viewer/city/building-geometry.js','3d-viewer/city/tai-o-estimates.js','3d-viewer/city/geo.js','source-scripts/city/government-import/check-neighbours.mjs','source-scripts/city/government-import/xl-open-sided-neighbour-diagnostic.mjs'])hashes[path]=sha(readFileSync(resolve(root,path)));
const result={rows,inputHashes:hashes,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,qualification:'Current viewer terrain and actual sourced roof/post volumes, preserving existing numeric regression limits. Historical whole-footprint warnings are diagnostic routing only. No source identity, source contact, foundation, native neighbours, reviews or installation gates are waived. Interior samples do not prove complete solid clearance or installation readiness.'};
writeFileSync(resolve(root,doc+'/geometry-checks.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({pairs:rows.length,actualPartRegressionPassed:rows.filter(row=>row.actualPartRegressionPassed).length,failed:rows.filter(row=>!row.actualPartRegressionPassed).map(row=>({uid:row.uid,document:row.document}))}));
