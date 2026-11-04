/** Data-only route preflight using live terrain and the city's exact collision index.
 * This is a continuous sampled corridor diagnostic, not a claimed Navigation replay.
 */
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {routeContext} from './route_context.mjs';
import {describeBuilding} from '../../../3d-viewer/city/building-geometry.js';
import {BuildingIndex,makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const read=p=>JSON.parse(readFileSync(path.join(root,p)));
const route=read('docs/astra-city/tai-o-completion/route.json');
const {manifest,sampler,buildings,index}=routeContext(route);
const footprintIndex=new BuildingIndex(buildings.map(b=>{const model=describeBuilding(b).model;return model?{...b,modelGeometry:null,base:model.bounds[1],height:model.bounds[4]-model.bounds[1],minimum:0}:b;}));
const legacyIndex=new BuildingIndex(buildings.map(b=>{const m=describeBuilding(b).model;if(!m||describeBuilding(b).openSided)return b;const a=m.bounds,xs=b.rings[0].map(p=>p[0]),zs=b.rings[0].map(p=>p[1]),x0=Math.min(...xs),x1=Math.max(...xs),z0=Math.min(...zs),z1=Math.max(...zs);let rings=b.rings;if(a[0]<x0-.1||a[3]>x1+.1||a[2]<z0-.1||a[5]>z1+.1){const loX=Math.min(x0,a[0]),hiX=Math.max(x1,a[3]),loZ=Math.min(z0,a[2]),hiZ=Math.max(z1,a[5]);rings=[[[loX,loZ],[hiX,loZ],[hiX,hiZ],[loX,hiZ],[loX,loZ]]];}return {...b,modelGeometry:null,rings,base:a[1],height:a[4]-a[1],minimum:0};}));
const samples=[];let distance=0;
for(let i=0;i<route.centreline.length-1;i++){
 const a=route.centreline[i],b=route.centreline[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
 const segment=route.segments.find(s=>s.fromIndex<=i&&s.toIndex>i),count=Math.ceil(length/.25);
 for(let k=0;k<count;k++){
  const t=k/count,x=a[0]+(b[0]-a[0])*t,z=a[1]+(b[1]-a[1])*t,y=sampler.height(x,z),raw=sampler.raw(x,z);
  const hit=index.collision(x,z,y,y+1.8,.55),centre=index.collision(x,z,y,y+1.8,0);
  samples.push({distanceMetres:distance+length*t,edge:i,sourceWayId:segment.sourceWayId,bridge:segment.kind==='bridge',position:[x,y,z],raw,mappedWater:!!sampler.mappedWater?.(x,z),collisionUid:hit?.uid||null,centreInside:!!centre,legacyAabbCollisionUid:legacyIndex.collision(x,z,y,y+1.8,.55)?.uid||null,sourceFootprintCollisionUid:footprintIndex.collision(x,z,y,y+1.8,.55)?.uid||null});
 }
 distance+=length;
}
const groups={};for(const p of samples){const g=groups[p.sourceWayId]??={samples:0,collisions:0,centreInside:0,wet:0,collisionUids:[]};g.samples++;g.collisions+=!!p.collisionUid;g.centreInside+=p.centreInside;g.wet+=p.raw<=.5||p.mappedWater;if(p.collisionUid&&!g.collisionUids.includes(p.collisionUid))g.collisionUids.push(p.collisionUid);}
const report={schemaVersion:1,status:'diagnostic-only',routeSha256:createHash('sha256').update(readFileSync(path.join(root,'docs/astra-city/tai-o-completion/route.json'))).digest('hex'),method:'Samples at <=0.25m; exact current BuildingIndex, 0.55m Navigation walk radius, 1.8m actor. No bridge elevation override, no terrain/obstacle edits. Centre-inside distinguishes overlap from clearance-disc proximity. This does not execute Navigation.',lengthMetres:route.lengthMetres,counts:{samples:samples.length,collisions:samples.filter(p=>p.collisionUid).length,centreInside:samples.filter(p=>p.centreInside).length,wet:samples.filter(p=>p.raw<=.5||p.mappedWater).length,sourceFootprintCollisions:samples.filter(p=>p.sourceFootprintCollisionUid).length,legacyAabbCollisions:samples.filter(p=>p.legacyAabbCollisionUid).length,removedFalseAabbCollisions:samples.filter(p=>p.legacyAabbCollisionUid&&!p.collisionUid).length},groups,samples};
writeFileSync(path.join(root,'docs/astra-city/tai-o-completion/route-preflight.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({counts:report.counts,groups},null,2));
