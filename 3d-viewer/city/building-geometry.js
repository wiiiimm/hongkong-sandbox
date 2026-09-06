import * as THREE from '../vendor/three.module.js';
import {mergeGeometries} from '../vendor/BufferGeometryUtils.js';

const cache=new WeakMap(),modelCache=new WeakMap();
const finite=Number.isFinite;
function insideRing(x,z,ring){
 let inside=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const [ax,az]=ring[i],[bx,bz]=ring[j];
  if((az>z)!==(bz>z)&&x<(bx-ax)*(z-az)/(bz-az)+ax)inside=!inside;
 }
 return inside;
}
const inside=(x,z,rings)=>insideRing(x,z,rings[0])&&!rings.slice(1).some(r=>insideRing(x,z,r));
const openRing=ring=>ring.length>1&&ring[0][0]===ring.at(-1)[0]&&ring[0][1]===ring.at(-1)[1]?ring.slice(0,-1):ring;
export function isOpenSidedBuilding(building){return building.structureType==='Open-sided Structure'||building.sourceAttributes?.BuildingBlockType==='Open-sided Structure'||building.kind==='roof';}

function validModel(building){
 const model=building.modelGeometry;if(!model||typeof model!=='object')return null;
 if(modelCache.has(model))return modelCache.get(model);
 const array=a=>Array.isArray(a)||ArrayBuffer.isView(a),p=model.position,n=model.normal,index=model.index;
 let result=null;
 if(array(p)&&p.length>=9&&p.length%3===0&&p.length<=3000000&&(!n||(array(n)&&n.length===p.length))&&(!index||(array(index)&&index.length>=3&&index.length%3===0))){
  const vertices=p.length/3,bounds=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity];let valid=true;
  for(let i=0;i<p.length;i++){
   if(!finite(p[i])||(n&&!finite(n[i]))){valid=false;break;}
   const axis=i%3;bounds[axis]=Math.min(bounds[axis],p[i]);bounds[axis+3]=Math.max(bounds[axis+3],p[i]);
  }
  if(index){for(const i of index)if(!Number.isInteger(i)||i<0||i>=vertices){valid=false;break;}}
  else if(p.length%9!==0)valid=false;
  if(valid&&bounds[4]>bounds[1]+.001&&bounds[3]>bounds[0]&&bounds[5]>bounds[2]){
   const xs=building.rings?.[0]?.map(p=>p[0])||[],zs=building.rings?.[0]?.map(p=>p[1])||[];
   const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs),margin=Math.max(20,Math.hypot(maxX-minX,maxZ-minZ));
   if(bounds[0]>=minX-margin&&bounds[3]<=maxX+margin&&bounds[2]>=minZ-margin&&bounds[5]<=maxZ+margin&&bounds[1]>-1000&&bounds[4]<5000)result={...model,bounds};
  }
 }
 modelCache.set(model,result);return result;
}

function supportRings(rings){
 const outer=openRing(rings[0]),edges=[];let perimeter=0;
 for(let i=0;i<outer.length;i++){
  const a=outer[i],b=outer[(i+1)%outer.length],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
  if(length>.01){edges.push({a,b,length,start:perimeter});perimeter+=length;}
 }
 // Roof plans do not locate columns. These sparse supports are illustrative,
 // bounded to eight posts and kept wholly within the actual sourced footprint.
 const count=Math.min(8,Math.max(2,Math.ceil(perimeter/7))),result=[];
 for(let i=0;i<count;i++){
  const along=perimeter*(i+.5)/count,edge=edges.find(e=>along>=e.start&&along<e.start+e.length)||edges.at(-1);
  if(!edge)continue;
  const t=(along-edge.start)/edge.length,dx=(edge.b[0]-edge.a[0])/edge.length,dz=(edge.b[1]-edge.a[1])/edge.length;
  for(const side of [1,-1]){
   const x=edge.a[0]+(edge.b[0]-edge.a[0])*t-dz*.25*side,z=edge.a[1]+(edge.b[1]-edge.a[1])*t+dx*.25*side,half=.11;
   const ring=[[x-half,z-half],[x+half,z-half],[x+half,z+half],[x-half,z+half],[x-half,z-half]];
   if(ring.every(([px,pz])=>inside(px,pz,rings))&&result.every(r=>Math.hypot(r[0][0]-ring[0][0],r[0][1]-ring[0][1])>1)){
    result.push(ring);break;
   }
  }
 }
 return result;
}

/** Shared visual/collision volumes. Recorded elevations remain immutable. */
export function describeBuilding(building){
 const signature=[building.base,building.height,building.minimum,building.foundationBase,isOpenSidedBuilding(building)].join('|'),previous=cache.get(building);
 if(previous?.signature===signature&&previous.rings===building.rings&&previous.model===building.modelGeometry)return previous.description;
 const model=validModel(building),base=building.base,minimum=building.minimum||0,bottom=model?model.bounds[1]:base+minimum,top=model?model.bounds[4]:base+building.height,parts=[];
 if(!finite(bottom)||!finite(top)||top<=bottom||!building.rings?.length)return {parts,openSided:false,illustrativeSupports:0};
 const foundationTop=model?Math.min(base,bottom):base,foundation=finite(building.foundationBase)&&building.foundationBase<foundationTop-.02?building.foundationBase:null,openSided=isOpenSidedBuilding(building);
 if(openSided){
  const thickness=Math.min(.28,(top-bottom)*.16),roofBottom=top-thickness;
  parts.push({kind:'roof',rings:building.rings,bottom:roofBottom,top,windows:false});
  const postBottom=foundation??bottom;
  if(roofBottom>postBottom+.02)for(const ring of supportRings(building.rings))parts.push({kind:'post',rings:[ring],bottom:postBottom,top:roofBottom,windows:false,illustrative:true});
 }else{
  let collisionRings=building.rings;
  if(model){const xs=building.rings[0].map(p=>p[0]),zs=building.rings[0].map(p=>p[1]),x0=Math.min(...xs),x1=Math.max(...xs),z0=Math.min(...zs),z1=Math.max(...zs),a=model.bounds;
   if(a[0]<x0-.1||a[3]>x1+.1||a[2]<z0-.1||a[5]>z1+.1){const minX=Math.min(x0,a[0]),maxX=Math.max(x1,a[3]),minZ=Math.min(z0,a[2]),maxZ=Math.max(z1,a[5]);collisionRings=[[[minX,minZ],[maxX,minZ],[maxX,maxZ],[minX,maxZ],[minX,minZ]]];}
  }
  parts.push({kind:'building',rings:collisionRings,bottom,top,windows:true});
  if(foundation!==null)parts.push({kind:'foundation',rings:building.rings,bottom:foundation,top:foundationTop,windows:false,illustrative:true});
 }
 for(const part of parts){const xs=part.rings[0].map(p=>p[0]),zs=part.rings[0].map(p=>p[1]);part.bounds=[Math.min(...xs),Math.min(...zs),Math.max(...xs),Math.max(...zs)];}
 const description={parts,openSided,model:model||null,modelStatus:model?'usable':building.modelGeometry?'invalid-fallback':'absent',illustrativeSupports:parts.filter(p=>p.kind==='post').length,roofThickness:openSided?top-parts[0].bottom:0,foundationApplied:foundation!==null};
 cache.set(building,{signature,rings:building.rings,model:building.modelGeometry,description});return description;
}

export function collisionVolumes(building){return describeBuilding(building).parts;}

/** Geometry stays in the shared makeBuildings palette batches and picking index. */
export function createBuildingGeometry(building){
 const description=describeBuilding(building),geometries=description.parts.filter(part=>!description.model||part.kind==='foundation').map(part=>{
  const path=ring=>openRing(ring).map(([x,z])=>new THREE.Vector2(x,-z));
  const shape=new THREE.Shape(path(part.rings[0]));for(const hole of part.rings.slice(1))shape.holes.push(new THREE.Path(path(hole)));
  const geometry=new THREE.ExtrudeGeometry(shape,{depth:part.top-part.bottom,bevelEnabled:false,steps:1,curveSegments:1});
  geometry.rotateX(-Math.PI/2);geometry.translate(0,part.bottom,0);geometry.clearGroups();
  geometry.setAttribute('cityWindows',new THREE.Float32BufferAttribute(new Float32Array(geometry.attributes.position.count).fill(part.windows?1:0),1));return geometry;
 });
 if(description.model){
  const data=description.model;let geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(data.position,3));
  if(data.index)geometry.setIndex(Array.from(data.index));
  if(data.normal){geometry.setAttribute('normal',new THREE.Float32BufferAttribute(data.normal,3));geometry.normalizeNormals();}else geometry.computeVertexNormals();
  if(geometry.index){const source=geometry;geometry=source.toNonIndexed();source.dispose();}
  const count=geometry.attributes.position.count,mask=new Float32Array(count),normal=geometry.attributes.normal,position=geometry.attributes.position;
  for(let i=0;i<count;i++)mask[i]=!description.openSided&&Math.abs(normal.getY(i))<.6&&position.getY(i)>=building.base+(building.minimum||0)?1:0;
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(count*2),2));geometry.setAttribute('cityWindows',new THREE.Float32BufferAttribute(mask,1));geometry.clearGroups();geometries.unshift(geometry);
 }
 if(!geometries.length){
  const geometry=new THREE.BufferGeometry();for(const [name,size] of [['position',3],['normal',3],['uv',2],['cityWindows',1]])geometry.setAttribute(name,new THREE.Float32BufferAttribute([],size));return geometry;
 }
 if(geometries.length===1)return geometries[0];
 const result=mergeGeometries(geometries,false);for(const geometry of geometries)geometry.dispose();return result;
}
