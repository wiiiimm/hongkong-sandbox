// Replacement metadata never changes source meshes or grants walking access.
const finitePath=path=>Array.isArray(path)&&path.length>=2&&path.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite));
const length=path=>path.slice(1).reduce((sum,p,i)=>sum+Math.hypot(p[0]-path[i][0],p[1]-path[i][1]),0);
export function validateProxyClips(clips=[]){
 if(!Array.isArray(clips))throw new Error('Invalid infrastructure proxy clips');
 const seen=new Set();
 for(const c of clips){
  if(!c||typeof c.id!=='string'||!c.id||seen.has(c.id)||typeof c.source!=='string'||!/^https?:\/\//.test(c.source)||typeof c.policy!=='string'||!c.policy||!Array.isArray(c.keepPaths)||!c.keepPaths.length||!c.keepPaths.every(finitePath))throw new Error('Invalid infrastructure proxy clip '+c?.id);
  const sizes=[c.originalLengthMetres,c.retainedLengthMetres,c.replacedLengthMetres];
  if(!sizes.every(v=>Number.isFinite(v)&&v>0)||Math.abs(sizes[0]-sizes[1]-sizes[2])>.02||Math.abs(c.keepPaths.reduce((sum,p)=>sum+length(p),0)-sizes[1])>.02||c.keepPaths.some(p=>length(p)<1e-6))throw new Error('Invalid infrastructure proxy clip lengths '+c.id);
  if(c.withinExactSourceProjectionMetres!==undefined&&!(Number.isFinite(c.withinExactSourceProjectionMetres)&&c.withinExactSourceProjectionMetres>0&&c.withinExactSourceProjectionMetres<=sizes[0]+.02))throw new Error('Invalid source overlap '+c.id);
  seen.add(c.id);
 }
 return clips;
}
/** Keep exact original vertices and interpolate only the derived cut endpoints. */
export function clippedProxyParts(record,clip){
 const path=record.deckPath,distances=[0];
 for(let i=1;i<path.length;i++)distances.push(distances.at(-1)+Math.hypot(path[i][0]-path[i-1][0],path[i][2]-path[i-1][2]));
 if(Math.abs(distances.at(-1)-clip.originalLengthMetres)>.025)throw new Error('Proxy clip source length mismatch '+clip.id);
 const locate=point=>{
  let best=null;
  for(let i=1;i<path.length;i++){
   const a=path[i-1],b=path[i],dx=b[0]-a[0],dz=b[2]-a[2],square=dx*dx+dz*dz;if(square<1e-14)continue;
   const t=Math.max(0,Math.min(1,((point[0]-a[0])*dx+(point[1]-a[2])*dz)/square)),gap=Math.hypot(point[0]-a[0]-dx*t,point[1]-a[2]-dz*t);
   if(!best||gap<best.gap)best={gap,distance:distances[i-1]+Math.sqrt(square)*t,point:a.map((v,k)=>v+(b[k]-v)*t)};
  }
  if(!best||best.gap>.002)throw new Error('Proxy clip leaves original path '+clip.id);
  return best;
 };
 const ranges=clip.keepPaths.map(keep=>{
  const locations=keep.map(locate),start=locations[0],end=locations.at(-1);
  if(end.distance-start.distance<1e-6||locations.some((p,i)=>i&&p.distance<locations[i-1].distance-1e-6)||Math.abs(end.distance-start.distance-length(keep))>.002)throw new Error('Proxy clip changes original direction or corners '+clip.id);
  return {start,end};
 }).sort((a,b)=>a.start.distance-b.start.distance);
 for(let i=1;i<ranges.length;i++)if(ranges[i].start.distance<ranges[i-1].end.distance-1e-6)throw new Error('Overlapping retained proxy paths '+clip.id);
 return ranges.map(({start,end})=>({...record,deckPath:[start.point,...path.filter((p,i)=>distances[i]>start.distance+1e-6&&distances[i]<end.distance-1e-6),end.point],length:end.distance-start.distance,proxyClip:clip}));
}
// Street tiles retain simplified paths. Cut the validated original retained paths
// at tile boundaries, rather than projecting them onto those simplified chords.
function segmentInBounds(a,b,bounds){
 let enter=0,exit=1;const dx=b[0]-a[0],dz=b[1]-a[1];
 for(const [p,q] of [[-dx,a[0]-bounds[0]],[dx,bounds[2]-a[0]],[-dz,a[1]-bounds[1]],[dz,bounds[3]-a[1]]]){
  if(Math.abs(p)<1e-14){if(q<0)return null;continue;}
  const t=q/p;if(p<0)enter=Math.max(enter,t);else exit=Math.min(exit,t);if(enter>=exit)return null;
 }
 return [[a[0]+dx*enter,a[1]+dz*enter],[a[0]+dx*exit,a[1]+dz*exit]];
}
export function retainedRoads(roads,clips,bounds){
 return roads.flatMap(road=>{
  const clip=clips.get(road.id);if(!clip)return [road];
  const parts=[];
  for(const path of clip.keepPaths){
   let current=null;
   for(let i=1;i<path.length;i++){
    const segment=segmentInBounds(path[i-1],path[i],bounds);
    if(!segment){current=null;continue;}
    if(current&&Math.hypot(current.at(-1)[0]-segment[0][0],current.at(-1)[1]-segment[0][1])<1e-6)current.push(segment[1]);
    else{current=segment;parts.push(current);}
   }
  }
  return parts.map(path=>({...road,path,proxyClip:clip}));
 });
}
