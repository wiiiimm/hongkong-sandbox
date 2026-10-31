/** Exact original shared-edge paths to podium contacts, diagnostic only. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {supportSurface} from './support-contact.mjs';
const dir=process.argv[2],out=process.argv[3],read=p=>JSON.parse(gunzipSync(readFileSync(p)));
const input=read(dir+'/geometry-inputs.json.gz'),checks=read(dir+'/support-checks.json.gz'),exact=read(process.argv[4]);
const support={position:[],index:[]};
for(const r of input.rows.filter(r=>!input.towerUIDs.includes(r.uid))){const n=support.position.length/3;for(const v of r.position)support.position.push(v);for(const i of r.index)support.index.push(i+n);}
const surface=supportSurface(support),rows=[],key=p=>p.join(',');
for(const r of input.rows.filter(r=>input.towerUIDs.includes(r.uid))){
 const faces=Array.from({length:r.index.length/3},(_,i)=>[0,1,2].map(k=>r.position.slice(r.index[i*3+k]*3,r.index[i*3+k]*3+3)));
 const edges=new Map(),adj=faces.map(()=>[]),seeds=new Map(),cache=new Map();
 const gap=p=>{const k=key(p);if(!cache.has(k)){const h=surface.height(p[0],p[2]);cache.set(k,h===null?null:p[1]-h);}return cache.get(k);};
 faces.forEach((f,i)=>{for(const p of f){const d=gap(p);if(d!==null&&d>=-.1&&d<=1&&!seeds.has(i))seeds.set(i,{point:p,gap:d});}
  for(let k=0;k<3;k++){const a=f[k],b=f[(k+1)%3];if(key(a)===key(b))continue;const e=[key(a),key(b)].sort().join('|');if(!edges.has(e))edges.set(e,{vertices:[a,b],faces:[]});edges.get(e).faces.push(i);}
 });
 const ceiling=Math.max(r.bottom+.35,...[...seeds.values()].map(s=>s.point[1]));
 const clip=e=>{let [a,b]=e;if(a[1]>ceiling&&b[1]>ceiling)return null;if(a[1]>ceiling||b[1]>ceiling){const t=(ceiling-a[1])/(b[1]-a[1]),p=a.map((v,i)=>v+t*(b[i]-v));if(a[1]>ceiling)a=p;else b=p;}return Math.hypot(...a.map((v,i)=>v-b[i]))>1e-9?[a,b]:null;};
 for(const e of edges.values()){const clipped=clip(e.vertices);if(!clipped)continue;for(const a of e.faces)for(const b of e.faces)if(a!==b)adj[a].push({face:b,edge:e.vertices,clipped});}
 const next=new Map(),queue=[];
 for(const i of seeds.keys()){next.set(i,null);queue.push(i);}
 for(let q=0;q<queue.length;q++){const a=queue[q];for(const edge of adj[a])if(!next.has(edge.face)){next.set(edge.face,{face:a,edge:edge.edge,clipped:edge.clipped});queue.push(edge.face);}}
 const details=checks.rows.find(x=>x.uid===r.uid).unresolved.map(f=>{
  const allowed=exact.rows.find(x=>x.uid===r.uid).details.find(x=>JSON.stringify(x.position)===JSON.stringify(f.position)).exactStartFaces;
  const start=allowed.find(i=>next.has(i));
  if(start===undefined)return {position:f.position,reason:f.reason,witness:null,incidentFaces:f.originalSourceFaces.map(x=>x.faceIndex)};
  const chain=[start],sharedEdges=[],clippedSharedEdges=[];let current=start;
  while(next.get(current)!==null){const n=next.get(current);assert(n);sharedEdges.push(n.edge);clippedSharedEdges.push(n.clipped);current=n.face;chain.push(current);assert(chain.length<=faces.length);}
  assert(seeds.has(current));const contact=seeds.get(current);
  for(let i=0;i<sharedEdges.length;i++)for(const p of sharedEdges[i])assert(faces[chain[i]].some(v=>key(v)===key(p))&&faces[chain[i+1]].some(v=>key(v)===key(p)));
  const ys=chain.flatMap(i=>faces[i].map(v=>v[1]));
  const path=[f.position,...clippedSharedEdges.map(e=>e[0].map((v,k)=>(v+e[1][k])/2)),contact.point];
  assert(path.every(p=>p[1]<=ceiling+1e-9));
  for(let i=0;i<clippedSharedEdges.length;i++)for(const p of clippedSharedEdges[i]){const [a,b]=sharedEdges[i],delta=b.map((v,k)=>v-a[k]),den=delta.reduce((s,x)=>s+x*x,0),t=p.reduce((s,v,k)=>s+(v-a[k])*delta[k],0)/den;assert(t>=-1e-9&&t<=1+1e-9);assert(Math.hypot(...p.map((v,k)=>v-a[k]-t*delta[k]))<1e-8);}

  return {position:f.position,reason:f.reason,witness:{faces:chain,sharedEdges,clippedSharedEdges,continuousLowPath:path,contactRegionCeiling:ceiling,maximumPathHeight:Math.max(...path.map(p=>p[1])),contact,contactFace:current,pathFaceHeightRange:[Math.min(...ys),Math.max(...ys)],straightLineDistanceM:Math.hypot(...contact.point.map((x,i)=>x-f.position[i]))}};
 });
 const good=details.filter(x=>x.witness),summary={uid:r.uid,sourceSHA256:r.sourceSHA256,sourceFaces:faces.length,contactFaces:seeds.size,canonicalFailures:details.length,sharedEdgeWitnesses:good.length,withoutSharedEdgeWitness:details.length-good.length,maximumPathFaces:Math.max(0,...good.map(x=>x.witness.faces.length)),maximumPathHeight:Math.max(0,...good.map(x=>x.witness.maximumPathHeight))};
 console.log(JSON.stringify(summary));rows.push({...summary,details});
}
writeFileSync(out,gzipSync(JSON.stringify({rows,fullAcceptance:false,sourceSpecificInterfaceInterpretationAccepted:false,qualification:'All actual path waypoints are at or below the maximum original contacting-vertex height or canonical low-rim band, whichever is higher. Consecutive waypoints lie on the same finite convex original triangle; no source mesh modification. Exact shared nonzero source edges connect each reported path to an original vertex with existing strict podium clearance. Full source mesh examined; path heights/spans reported without acceptance thresholds. Connectivity alone does not prove support or clear raw failures. No source geometry, pose or policy changes.'})));
