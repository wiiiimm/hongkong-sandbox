/** Classify original failed terrain samples; diagnostic only, never acceptance. */
export function classifyVerticalWallCrossings(triangles, failures, height){
 if(!Array.isArray(triangles)||!Array.isArray(failures)||typeof height!=='function')throw new TypeError('Original triangles, failures and terrain sampler required');
 const incidents=new Map(),centres=new Map(),key=p=>JSON.stringify(p),faces=triangles.map((t,i)=>{
  if(t.length!==3||t.some(p=>p.length!==3||p.some(v=>!Number.isFinite(v))))throw new TypeError('Invalid original geometry');
  const a=t[1].map((v,k)=>v-t[0][k]),b=t[2].map((v,k)=>v-t[0][k]),n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],areaSquared=n.reduce((s,v)=>s+v*v,0);
  const gaps=t.map(p=>{const y=height(p[0],p[2]);return Number.isFinite(y)?p[1]-y:null;});
  for(const p of t){const k=key(p);if(!incidents.has(k))incidents.set(k,[]);incidents.get(k).push(i);}
  const c=[0,1,2].map(k=>t.reduce((s,p)=>s+p[k],0)/3),k=key(c);if(!centres.has(k))centres.set(k,[]);centres.get(k).push(i);
  return {index:i,exactlyVertical:n[1]===0&&areaSquared>0,nondegenerate:areaSquared>0,completeTerrain:gaps.every(Number.isFinite),hasVertexAboveGround:gaps.some(g=>Number.isFinite(g)&&g>=0),minimumVertexGap:gaps.every(Number.isFinite)?Math.min(...gaps):null,maximumVertexGap:gaps.every(Number.isFinite)?Math.max(...gaps):null};
 });
 const samples=failures.map(f=>{
  const ids=(f.kind==='vertex'?incidents:f.kind==='centre'?centres:null)?.get(key(f.point))??[],used=ids.map(i=>faces[i]).filter(f=>f.nondegenerate),ground=height(f.point[0],f.point[2]);
  const reasons=[];
  if(!Number.isFinite(ground)||Math.abs((f.point[1]-ground)-f.gap)>1e-9)reasons.push('original-failed-sample-terrain-mismatch');
  if(!used.length)reasons.push('original-sample-face-not-established');
  if(used.some(f=>!f.exactlyVertical))reasons.push('incident-source-face-is-not-exactly-vertical');
  if(used.some(f=>!f.completeTerrain||!f.hasVertexAboveGround))reasons.push('incident-wall-not-proven-to-emerge-through-ground');
  return {...f,originalFaces:used,verticalCrossingObserved:!reasons.length,reasons};
 });
 return {samples,allFailedSamplesAreExactVerticalWallCrossings:failures.length>0&&samples.every(s=>s.verticalCrossingObserved),acceptanceGranted:false,installationApproved:false,geometryChanges:0,qualification:'Per-sample diagnostic of exact vertical original faces crossing original terrain. It does not establish structural intent, complete foundation, accepted terrain clearance, low-rim contact, identity, neighbours or publication; existing acceptance remains unchanged.'};
}
