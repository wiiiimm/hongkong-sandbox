/** Document sub-metre street-centre deviations; source centreline stays immutable. */
import {writeFileSync} from 'node:fs';
import path from 'node:path';
import {root,read,routeContext} from './route_context.mjs';
import {makeRouteNavigation,loadRouteSurfaces} from './route_navigation.mjs';
const route=read('docs/astra-city/tai-o-completion/route.json'),connector=read('source-scripts/city/tai-o-completion/route-entry.json');
const [replaceFrom,replaceTo]=connector.replacesSourceIndices,guide=[...route.centreline.slice(0,replaceFrom+1),...connector.centreline.slice(1),...route.centreline.slice(replaceTo+1)];
const shift=connector.centreline.length-1-(replaceTo-replaceFrom);
const sourceForEdge=e=>e<replaceFrom?{sourceEdge:e}:e<replaceFrom+connector.centreline.length-1?{connectorId:connector.id,connectorEdge:e-replaceFrom}:{sourceEdge:e-shift};
const guideIndexForSource=i=>i<=replaceFrom?i:i>=replaceTo?i+shift:-1;
const context=routeContext(route),{sampler,index}=context,surfaces=await loadRouteSurfaces({sampler}),nav=makeRouteNavigation({...context,surfaces}),samples=[],cumulative=[0];
for(let i=0;i<guide.length-1;i++){const a=guide[i],b=guide[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);cumulative.push(cumulative.at(-1)+length);}
const at=distance=>{let i=0;while(i<cumulative.length-2&&cumulative[i+1]<distance)i++;const t=Math.max(0,Math.min(1,(distance-cumulative[i])/(cumulative[i+1]-cumulative[i]))),a=guide[i],b=guide[i+1];return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];};
for(let edge=0;edge<guide.length-1;edge++){
 const length=cumulative[edge+1]-cumulative[edge],count=Math.ceil(length/.25);
 for(let i=0;i<count;i++){const distance=cumulative[edge]+length*i/count;samples.push({edge,fraction:i/count,distance,point:at(distance)});}
}
samples.push({edge:guide.length-2,fraction:1,distance:cumulative.at(-1),point:guide.at(-1)});
const clear=([x,z],radius=.55)=>nav.groundHeights(x,z).some(y=>!nav.collides(x,z,y,y+1.8,radius,true));
for(const sample of samples){
 let a=at(Math.max(0,sample.distance-.25)),b=at(Math.min(cumulative.at(-1),sample.distance+.25)),length=Math.hypot(b[0]-a[0],b[1]-a[1]);
 if(length<1e-6){a=guide[sample.edge];b=guide[sample.edge+1];length=Math.hypot(b[0]-a[0],b[1]-a[1]);}
 sample.normal=[-(b[1]-a[1])/length,(b[0]-a[0])/length];sample.choices=[];
 for(let k=-15;k<=15;k++){const offset=k*.05,point=sample.point.map((v,i)=>v+sample.normal[i]*offset);if(clear(point))sample.choices.push({offset,point,cost:Infinity,previous:-1});}
 if(!sample.choices.length)throw Error(`No public-street clearance within0.75m at${sample.distance}m edge${sample.edge}`);
}
for(const choice of samples[0].choices)if(choice.offset===0)choice.cost=0;
for(let i=1;i<samples.length;i++){
 const sample=samples[i],previous=samples[i-1];
 for(const choice of sample.choices){
  const candidates=previous.choices.map((before,k)=>({before,k,cost:before.cost+choice.offset**2+30*(before.offset-choice.offset)**2})).filter(({before,cost})=>Number.isFinite(cost)&&Math.abs(before.offset-choice.offset)<=.301).sort((a,b)=>a.cost-b.cost);
  for(const {before,k,cost} of candidates){
   const gap=Math.hypot(choice.point[0]-before.point[0],choice.point[1]-before.point[1]);if(gap>.55)continue;
   if(![.25,.5,.75].every(t=>clear(before.point.map((v,j)=>v+(choice.point[j]-v)*t),.55)))continue;
   choice.cost=cost;choice.previous=k;break;
  }
 }
 if(!sample.choices.some(c=>Number.isFinite(c.cost)))throw Error(`No continuous clearance transition at${sample.distance}m edge${sample.edge}`);
}
let last=samples.at(-1).choices.reduce((a,c,i,all)=>c.cost<all[a].cost?i:a,0);const selected=[];
for(let i=samples.length-1;i>=0;i--){const c=samples[i].choices[last];selected.push(c);last=c.previous;}selected.reverse();
route.walkCentreline=selected.map(c=>c.point);route.sourceOffsets=samples.flatMap((s,i)=>selected[i].offset?[{walkIndex:i,...sourceForEdge(s.edge),sourceFraction:s.fraction,offsetMetres:selected[i].offset}]:[]);
route.walkSampleSources=samples.map(s=>({...sourceForEdge(s.edge),fraction:s.fraction}));route.publicConnectors=[connector];
for(const stop of route.stops)stop.walkIndex=samples.findIndex(s=>s.edge===guideIndexForSource(stop.index)&&s.fraction===0);route.stops.at(-1).walkIndex=samples.length-1;
route.alignment={maximumOffsetMetres:Math.max(...selected.map(c=>Math.abs(c.offset))),adjustedSamples:route.sourceOffsets.length,sampleCount:samples.length,maximumSourceSpacingMetres:.25,clearanceRadiusMetres:.55,connectingSegmentRadiusMetres:.55,method:'Minimum-cost lateral deviations in 0.05 m steps, bounded to 0.75 m of the unchanged public OSM street centreline or the separately documented public connector, checked against authoritative building footprints and exact model surfaces. Four checks per short link prevent corner-cutting. These are gameplay clearance positions within the mapped public-street corridor, not a surveyed replacement alignment.',bridgeStatus:'Uses the published BridgeLayer loader, exact source floor triangles and its rendered estimated-approach triangles; full Navigation replay remains a separate acceptance check.'};
writeFileSync(path.join(root,'docs/astra-city/tai-o-completion/route.json'),JSON.stringify(route,null,2)+'\n');
console.log(JSON.stringify(route.alignment,null,2));
