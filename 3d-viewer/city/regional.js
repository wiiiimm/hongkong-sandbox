import * as THREE from '../vendor/three.module.js';
import {SURFACE_STYLES,surfaceBounds,validateRegionalPackage} from './regional-data.js';
import {distanceToBounds} from './tile-cache.js';

// Surface detail is draped over the retained terrain. These visual layers do not
// establish surveyed deck elevations or change pedestrian access/collisions.
export function surfaceGeometry(surface,sampler) {
 const rings=surface.rings.map(r=>r.slice(0,-1).map(p=>new THREE.Vector2(...p)));
 const faces=THREE.ShapeUtils.triangulateShape(rings[0],rings.slice(1));
 const points=rings.flat(),positions=[];
 const addTriangle=(a,b,c)=>{
  const stack=[[a,b,c,0]];
  while(stack.length){
   const [p,q,r,depth]=stack.pop();
   const lengths=[p.distanceToSquared(q),q.distanceToSquared(r),r.distanceToSquared(p)];
   const edge=lengths.indexOf(Math.max(...lengths));
   if(lengths[edge]>24*24&&depth<14){
    const corners=[p,q,r],a=corners[edge],b=corners[(edge+1)%3],c=corners[(edge+2)%3],mid=a.clone().add(b).multiplyScalar(.5);
    stack.push([a,mid,c,depth+1],[mid,b,c,depth+1]);continue;
   }
   const ordered=(q.x-p.x)*(r.y-p.y)-(q.y-p.y)*(r.x-p.x)>0?[p,r,q]:[p,q,r];
   for(const v of ordered)positions.push(v.x,sampler.height(v.x,v.y)+.26,v.y);
  }
 };
 for(const face of faces)addTriangle(...face.map(i=>points[i]));
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.computeVertexNormals();return geometry;
}
export class RegionalDetail {
 constructor({scene,sampler,onChange=()=>{}}){
  Object.assign(this,{sampler,onChange});this.group=new THREE.Group();this.group.name='Mapped beaches, piers and neighbourhood surfaces';scene.add(this.group);
  this.disposed=false;this.controllers=new Map();this.tiles=new Map();this.cache=new Map();this.sources=new Set();this.mappedSurfaces=[];this.errors=new Map();this.pending=0;this.focus=[0,420];this.radius=3000;this.requests=new Map();this.loadedPackages=new Set();this.surfaceCount=0;
  this.boundaryMaterial=new THREE.LineBasicMaterial({color:'#dddcc3',transparent:true,opacity:.7});
  this.materials=new Map(Object.entries(SURFACE_STYLES).map(([kind,color])=>[kind,new THREE.MeshStandardMaterial({color,roughness:.96,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-3,polygonOffsetUnits:-3})]));
 }
 async load(url){
  if(this.disposed)return;
  if(this.loadedPackages.has(url))return;
  if(this.requests.has(url))return this.requests.get(url);
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);this.controllers.set(url,controller);
  this.pending++;this.errors.delete(url);this.onChange();
  const request=(async()=>{
   try{
    const response=await fetch(url,{signal:controller.signal});if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const data=validateRegionalPackage(await response.json());
    if(this.disposed)return;
    for(const surface of data.surfaces){
     if(this.sources.has(surface.id))continue;this.sources.add(surface.id);this.mappedSurfaces.push(surface);this.surfaceCount++;
     const bounds=surfaceBounds(surface),x=(bounds[0]+bounds[2])/2,z=(bounds[1]+bounds[3])/2,key=`${Math.floor(x/1600)}_${Math.floor(z/1600)}`;
     if(!this.tiles.has(key))this.tiles.set(key,{bounds:[...bounds],surfaces:[]});
     const tile=this.tiles.get(key);tile.surfaces.push(surface);tile.bounds=[Math.min(tile.bounds[0],bounds[0]),Math.min(tile.bounds[1],bounds[1]),Math.max(tile.bounds[2],bounds[2]),Math.max(tile.bounds[3],bounds[3])];
     // A later package can extend a tile at a regional seam.
     if(this.cache.has(key)){this.disposeTile(key);}
    }
    this.loadedPackages.add(url);this.plan(...this.focus,this.radius);
   }catch(error){if(!this.disposed)this.errors.set(url,error.message);}
   finally{clearTimeout(timer);this.controllers.delete(url);this.pending--;this.requests.delete(url);if(!this.disposed)this.onChange();}
  })();
  this.requests.set(url,request);return request;
 }
 retry(){return Promise.all([...this.errors.keys()].map(url=>this.load(url)));}
 buildTile(key){
  if(this.disposed)return;
  const tile=this.tiles.get(key),group=new THREE.Group(),bins=new Map(),boundaries=[];
  for(const surface of tile.surfaces){
   const geometry=surfaceGeometry(surface,this.sampler),array=geometry.attributes.position.array;
   if(!bins.has(surface.kind))bins.set(surface.kind,[]);bins.get(surface.kind).push(array);geometry.dispose();
   if(surface.kind==='pitch')for(const ring of surface.rings)for(let i=1;i<ring.length;i++){const a=ring[i-1],b=ring[i],steps=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/20));for(let j=0;j<steps;j++)for(const t of [j/steps,(j+1)/steps]){const x=a[0]+(b[0]-a[0])*t,z=a[1]+(b[1]-a[1])*t;boundaries.push(x,this.sampler.height(x,z)+.31,z);}}
  }
  for(const [kind,arrays] of bins){
   const positions=new Float32Array(arrays.reduce((n,a)=>n+a.length,0));let offset=0;for(const a of arrays){positions.set(a,offset);offset+=a.length;}
   const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.computeVertexNormals();
   const mesh=new THREE.Mesh(geometry,this.materials.get(kind));mesh.receiveShadow=true;mesh.name=kind;group.add(mesh);
  }
  if(boundaries.length){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(boundaries,3));group.add(new THREE.LineSegments(geometry,this.boundaryMaterial));}
  group.userData.surfaces=tile.surfaces.length;this.group.add(group);this.cache.set(key,group);
 }
 plan(x,z,radius=3000){
  if(this.disposed)return;
  this.focus=[x,z];this.radius=Math.min(radius,5000);
  const wanted=[...this.tiles].map(([key,tile])=>({key,d:distanceToBounds(x,z,tile.bounds)})).filter(t=>t.d<=this.radius).sort((a,b)=>a.d-b.d||a.key.localeCompare(b.key)).slice(0,24).map(t=>t.key);
  const active=new Set(wanted);
  for(const key of this.cache.keys())if(!active.has(key))this.disposeTile(key);
  for(const key of wanted)if(!this.cache.has(key))this.buildTile(key);
 }
 disposeTile(key){const group=this.cache.get(key);group.traverse(o=>o.geometry?.dispose());group.removeFromParent();this.cache.delete(key);}
 get stats(){return {surfaces:this.surfaceCount,visibleSurfaces:[...this.cache.values()].reduce((n,g)=>n+g.userData.surfaces,0),tiles:this.cache.size,pending:this.pending,errors:[...this.errors.keys()],packages:this.loadedPackages.size};}
 dispose(){this.disposed=true;for(const controller of this.controllers.values())controller.abort();for(const key of this.cache.keys())this.disposeTile(key);for(const material of this.materials.values())material.dispose();this.boundaryMaterial.dispose();this.group.removeFromParent();}
}
