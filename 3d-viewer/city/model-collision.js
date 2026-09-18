/** Native surfaces and local roof bounds supplement the source footprint without AABB infill.
 * Clip source triangles to the actor's vertical span, then intersect the resulting
 * horizontal projection with its radius. Cached indices retain source arrays.
 */
const indices=new WeakMap(),CELL=4,EPS=1e-10;
function triangleIndex(model){
 let cached=indices.get(model);if(cached)return cached;
 const p=model.position,order=model.index,count=(order?.length||p.length/3)/3;
 const bounds=new Float64Array(count*6),cells=new Map(),large=[];
 for(let t=0;t<count;t++){
  const ids=[0,1,2].map(k=>(order?order[t*3+k]:t*3+k)*3),o=t*6;
  for(let a=0;a<3;a++){bounds[o+a]=Math.min(...ids.map(i=>p[i+a]));bounds[o+a+3]=Math.max(...ids.map(i=>p[i+a]));}
  const x0=Math.floor(bounds[o]/CELL),x1=Math.floor(bounds[o+3]/CELL),z0=Math.floor(bounds[o+2]/CELL),z1=Math.floor(bounds[o+5]/CELL);
  // Bound the index cost for unusually large source faces; those use AABB checks.
  if((x1-x0+1)*(z1-z0+1)>256){large.push(t);continue;}
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){const key=`${x},${z}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(t);}
 }
 cached={bounds,cells,large,count};indices.set(model,cached);return cached;
}
function clipHeight(points,y,above){
 const result=[];let previous=points.at(-1),wasInside=above?previous[1]>=y:previous[1]<=y;
 for(const current of points){
  const isInside=above?current[1]>=y:current[1]<=y;
  if(isInside!==wasInside){const t=(y-previous[1])/(current[1]-previous[1]);result.push([previous[0]+t*(current[0]-previous[0]),y,previous[2]+t*(current[2]-previous[2])]);}
  if(isInside)result.push(current);previous=current;wasInside=isInside;
 }
 return result;
}
function projectedHit(points,x,z,radius){
 let inside=false;
 for(let i=0,j=points.length-1;i<points.length;j=i++){
  const a=points[j],b=points[i],dx=b[0]-a[0],dz=b[2]-a[2],length=dx*dx+dz*dz;
  const t=length?Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[2])*dz)/length)):0;
  if((x-a[0]-dx*t)**2+(z-a[2]-dz*t)**2<=radius*radius+EPS)return true;
  if((a[2]>z)!==(b[2]>z)&&x<(b[0]-a[0])*(z-a[2])/(b[2]-a[2])+a[0])inside=!inside;
 }
 return inside;
}
function nearbyTriangles(model,x,z,radius){
 const {bounds,cells,large,count}=triangleIndex(model),x0=Math.floor((x-radius)/CELL),x1=Math.floor((x+radius)/CELL),z0=Math.floor((z-radius)/CELL),z1=Math.floor((z+radius)/CELL);
 const candidates=new Set(large);
 if((x1-x0+1)*(z1-z0+1)>4096){for(let t=0;t<count;t++)candidates.add(t);}
 else for(let i=x0;i<=x1;i++)for(let j=z0;j<=z1;j++)for(const t of cells.get(`${i},${j}`)||[])candidates.add(t);
 return {bounds,candidates};
}
/** Highest actual surface vertically above this point, or null in uncovered gaps.
 * The source footprint supplies the closed-building interior policy; native
 * triangle coverage supplies its local ceiling. Vertical walls cannot invent a
 * roof over a courtyard or extend a low wing to the tallest part of the model.
 */
export function modelRoofHeight(model,x,z){
 if(![x,z].every(Number.isFinite))return null;
 const {bounds,candidates}=nearbyTriangles(model,x,z,0),p=model.position,order=model.index;let roof=null;
 for(const t of candidates){
  const o=t*6;if(x<bounds[o]||x>bounds[o+3]||z<bounds[o+2]||z>bounds[o+5])continue;
  const a=(order?order[t*3]:t*3)*3,b=(order?order[t*3+1]:t*3+1)*3,c=(order?order[t*3+2]:t*3+2)*3;
  const ax=p[a],az=p[a+2],bx=p[b]-ax,bz=p[b+2]-az,cx=p[c]-ax,cz=p[c+2]-az,det=bx*cz-bz*cx;
  if(Math.abs(det)<=EPS)continue;
  const dx=x-ax,dz=z-az,u=(dx*cz-dz*cx)/det,v=(bx*dz-bz*dx)/det;
  if(u<-EPS||v<-EPS||u+v>1+EPS)continue;
  const y=p[a+1]+u*(p[b+1]-p[a+1])+v*(p[c+1]-p[a+1]);
  if(roof===null||y>roof)roof=y;
 }
 return roof;
}
export function modelSurfaceCollision(model,x,z,bottom,top,radius=0){
 if(![x,z,bottom,top,radius].every(Number.isFinite)||top<=bottom||radius<0)return false;
 const {bounds,candidates}=nearbyTriangles(model,x,z,radius);
 const p=model.position,order=model.index;
 for(const t of candidates){
  const o=t*6;if(x+radius<bounds[o]||x-radius>bounds[o+3]||z+radius<bounds[o+2]||z-radius>bounds[o+5]||top<=bounds[o+1]||bottom>=bounds[o+4])continue;
  let points=[0,1,2].map(k=>{const i=(order?order[t*3+k]:t*3+k)*3;return [p[i],p[i+1],p[i+2]];});
  points=clipHeight(points,bottom,true);if(!points.length)continue;
  points=clipHeight(points,top,false);if(points.length&&projectedHit(points,x,z,radius))return true;
 }
 return false;
}
