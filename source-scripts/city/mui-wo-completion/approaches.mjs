/** Visible, explicitly estimated connections to unchanged source deck openings. */
import {writeFileSync} from 'node:fs';
import {root,read,sampler,stagedSurfaces} from './context.mjs';
const surfaces=stagedSurfaces(false),routes=read('docs/astra-city/mui-wo-completion/routes-staged.json'),records=[];
const point=(p,y)=>[p[0],y,p[1]],lerp=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t),distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
function record(id,name,points,source,reference,note,sourcePath){
 const width=1.5,x=points.map(p=>p[0]),z=points.map(p=>p[2]);
 records.push({id:'mui-wo-access/'+id,name,source,publicAccessSource:reference,sourcePath,kind:'ramp',role:'access',walkable:true,estimatedPublicApproach:true,estimatedElevation:true,width,deckPath:points,bounds:[Math.min(...x)-width,Math.min(...z)-width,Math.max(...x)+width,Math.max(...z)+width],elevationBasis:note,widthBasis:'1.5m illustrative walking width within the mapped public approach; not a surveyed width or accessibility standard.',heightDatum:'Hong Kong Principal Datum',approximation:true});
}
const promenade=read('source-scripts/city/mui-wo-completion/promenade-route.json'),a=promenade.streetPosition,b=promenade.outsideOpening,c=promenade.sourceDeckEntry,y0=sampler.height(...a),y1=surfaces.heights(...c)[0],d0=distance(a,b),d1=distance(b,c);
if(!Number.isFinite(y1))throw Error('No source floor at reviewed east opening');
record('promenade-east','Silvermine Bay promenade public opening',[point(a,y0),point(b,y0+(y1-y0)*d0/(d0+d1)),point(c,y1)],'https://www.openstreetmap.org/way/552532076',promenade.publicAccessSource,'Estimated short public connector from retained street node6598342309 through an existing source-railing opening. Endpoint heights are staged terrain and original source floor; intermediate height is linear. The source railing/mesh and OSM line remain intact.',[a,b,c]);
const town=routes.legs.find(l=>l.id==='muiwo-town--silvermine-beach'),bridgePoint=town.centreline[10],streetPoint=town.centreline[11],deckY=surfaces.heights(...bridgePoint)[0];
if(!Number.isFinite(deckY))throw Error('No River Silver source floor at public north landing');
record('silver-bridge-north','River Silver pedestrian bridge north landing',[point(bridgePoint,deckY),point(streetPoint,sampler.height(...streetPoint))],'https://www.openstreetmap.org/way/762011407','https://www.openstreetmap.org/way/701768072','Estimated short visible landing along the exact public source edge. Meets the unchanged source bridge deck and staged terrain; no railing removal or source height adjustment.',[bridgePoint,streetPoint]);
const way=read('3d-viewer/city/data/bridges.json').bridges.find(b=>b.id==='way/204797331');
for(const [side,line] of [['south',way.path],['north',[...way.path].reverse()]]){
 const [start,end]=line,length=distance(start,end);let lo=0,hi=length;
 const first=Array.from({length:Math.ceil(length/.1)+1},(_,i)=>Math.min(length,i*.1)).find(d=>surfaces.heights(...lerp(start,end,d/length)).length);
 if(first===undefined)throw Error('No Wang Tong public source deck');
 lo=Math.max(0,first-.2);hi=first;for(let i=0;i<40;i++){const mid=(lo+hi)/2;if(surfaces.heights(...lerp(start,end,mid/length)).length)hi=mid;else lo=mid;}
 const boundary=(lo+hi)/2,inside=lerp(start,end,(boundary+1)/length),landing=lerp(start,end,Math.max(0,boundary-.85)/length),y=surfaces.heights(...inside)[0];
 record('wang-tong-'+side,'Wang Tong pedestrian bridge '+side+' landing',[point(start,sampler.height(...start)),point(landing,y),point(inside,y)],way.source,'https://www.hyd.gov.hk/en/our_projects/walkability_projects/district_facilities/6850th/index.html','Estimated visible landing/ramp along the retained public pedestrian bridge centreline. Terrain endpoint and source upper pedestrian deck are exact inputs; profile/width between them are illustrative. Other source bridge components remain intact.',line);
}
writeFileSync(root+'/source-scripts/city/mui-wo-completion/approaches.json',JSON.stringify({schemaVersion:1,region:'mui-wo',records,limits:['These four short approach profiles are explicit estimates, not surveyed infrastructure geometry.','Walking acceptance depends on actual Navigation collision replay; creating a profile does not prove access.']},null,2)+'\n');
console.log(records.map(r=>({id:r.id,deckPath:r.deckPath})));
