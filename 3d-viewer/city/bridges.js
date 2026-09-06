import * as THREE from '../vendor/three.module.js';
import {prepareBridges} from './bridge-data.js';
import {prepareInfrastructure,InfrastructureSurfaces} from './infrastructure-data.js';
import {distanceToBounds} from './tile-cache.js';

// Construction details are illustrative. The route's top elevations and width
// come exclusively from the prepared record; no terrain lifting happens here.
const DECK_THICKNESS=.24,RAIL_HEIGHT=1.05,CANOPY_HEIGHT=2.8;
const TILE_SIZE=1600,TILE_LIMIT=24,RAIL_DETAIL_RADIUS=1400,UP=new THREE.Vector3(0,1,0);
const covered=record=>record.covered===true||record.covered==='yes';
const finitePoint=p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite);

function sectionsFor(record,width=record.width,lift=0){
 if(!Array.isArray(record.deckPath)||record.deckPath.length<2||!record.deckPath.every(finitePoint)||!Number.isFinite(width)||width<=0)throw new Error('Invalid prepared bridge '+record.id);
 const points=record.deckPath.filter((p,i,a)=>!i||p.some((v,k)=>Math.abs(v-a[i-1][k])>1e-7));
 const directions=points.slice(1).map((p,i)=>{
  const dx=p[0]-points[i][0],dz=p[2]-points[i][2],length=Math.hypot(dx,dz);
  return length>1e-7?[-dz/length,dx/length]:null;
 });
 const first=directions.find(Boolean);if(!first)throw new Error('Bridge has no horizontal span '+record.id);
 // Every section in a coincident-XZ stair group needs the same miter.
 // Otherwise the vertical riser twists into a spurious upward-facing wedge.
 const incoming=[],outgoing=[];let direction=first;
 for(let i=0;i<points.length;i++){incoming[i]=direction;if(directions[i])direction=directions[i];}
 direction=[...directions].reverse().find(Boolean);
 for(let i=points.length-1;i>=0;i--){if(directions[i])direction=directions[i];outgoing[i]=direction;}
 return points.map((p,i)=>{
  const before=incoming[i],after=outgoing[i];
  let nx=before[0]+after[0],nz=before[1]+after[1],length=Math.hypot(nx,nz);
  if(length<1e-6){nx=after[0];nz=after[1];length=1;}
  nx/=length;nz/=length;
  // A bounded miter keeps ordinary bends joined without long corner spikes.
  const half=width/2,amount=Math.min(half*1.8,half/Math.max(.25,nx*after[0]+nz*after[1]));
  return {left:[p[0]+nx*amount,p[1]+lift,p[2]+nz*amount],right:[p[0]-nx*amount,p[1]+lift,p[2]-nz*amount]};
 });
}
function quad(out,a,b,c,d){out.push(...a,...b,...c,...a,...c,...d);}
function lower(p,thickness){return [p[0],p[1]-thickness,p[2]];}
function solidGeometry(sections,thickness,featureIndex){
 const positions=[];
 for(let i=1;i<sections.length;i++){
  const a=sections[i-1],b=sections[i],al=lower(a.left,thickness),ar=lower(a.right,thickness),bl=lower(b.left,thickness),br=lower(b.right,thickness);
  quad(positions,a.left,b.left,b.right,a.right); // top, upward facing
  quad(positions,ar,br,bl,al);
  quad(positions,al,bl,b.left,a.left);
  quad(positions,a.right,b.right,br,ar);
  if(i===1)quad(positions,al,a.left,a.right,ar);
  if(i===sections.length-1)quad(positions,b.left,bl,br,b.right);
 }
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
 geometry.setAttribute('bridgeFeature',new THREE.Uint32BufferAttribute(new Uint32Array(positions.length/3).fill(featureIndex),1));
 geometry.computeVertexNormals();geometry.computeBoundingBox();geometry.computeBoundingSphere();
 return geometry;
}
/** Selection geometry: the same solid deck used by the visible merged meshes. */
export function geometryFor(record,featureIndex=0){
 if(!record.modelGeometry)return solidGeometry(sectionsFor(record),DECK_THICKNESS,featureIndex);
 const m=record.modelGeometry,g=new THREE.BufferGeometry();
 for(const [name,array]of [['position',m.position],['normal',m.normal],['color',m.colour]])g.setAttribute(name,new THREE.Float32BufferAttribute(array,3));
 g.setAttribute('bridgeFeature',new THREE.Uint32BufferAttribute(new Uint32Array(m.position.length/3).fill(featureIndex),1));g.computeBoundingBox();g.computeBoundingSphere();return g;
}
/** Exact visible top triangles for an explicitly accepted source deck or estimated approach. */
export function walkingSurfaceFor(record){
 if(record.modelGeometry)return record;
 if(record.walkable!==true||record.estimatedPublicApproach!==true)return null;
 const g=geometryFor(record),p=g.attributes.position,n=g.attributes.normal,walkTriangleIndices=[];
 for(let i=0;i<p.count;i+=3)if(n.getY(i)>.6&&n.getY(i+1)>.6&&n.getY(i+2)>.6)walkTriangleIndices.push(i/3);
 const b=g.boundingBox,surface={...record,base:b.min.y,height:b.max.y-b.min.y,bounds:[b.min.x,b.min.z,b.max.x,b.max.z],modelGeometry:{position:Array.from(p.array)},walkTriangleIndices};g.dispose();return surface;
}
function pushBeam(beams,a,b,width){
 const dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2];
 if(Math.hypot(dx,dy,dz)<1e-5)return;
 beams.push((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2,dx,dy,dz,width);
}
const raised=(p,y)=>[p[0],p[1]+y,p[2]];
function railBeams(sections,beams,hasCanopy){
 for(let i=1;i<sections.length;i++){
  for(const side of ['left','right']){
   const a=sections[i-1][side],b=sections[i][side],length=Math.hypot(b[0]-a[0],b[2]-a[2]);
   for(const height of [RAIL_HEIGHT,.52])pushBeam(beams,raised(a,height),raised(b,height),.055);
   const steps=Math.max(1,Math.ceil(length/3.2));
   for(let j=i===1?0:1;j<=steps;j++){
    const t=j/steps,p=a.map((v,k)=>v+(b[k]-v)*t);
    pushBeam(beams,p,raised(p,RAIL_HEIGHT),.075);
   }
   if(hasCanopy){
    const supports=Math.max(1,Math.ceil(length/5));
    for(let j=i===1?0:1;j<=supports;j++){
     const t=j/supports,p=a.map((v,k)=>v+(b[k]-v)*t);
     pushBeam(beams,p,raised(p,CANOPY_HEIGHT-.08),.10);
    }
   }
  }
 }
}
function mergeGeometries(geometries){
 const geometry=new THREE.BufferGeometry();
 for(const name of ['position','normal','bridgeFeature',...(geometries[0]?.attributes.color?['color']:[])]){
  const count=geometries.reduce((sum,g)=>sum+g.attributes[name].array.length,0);
  const values=name==='bridgeFeature'?new Uint32Array(count):new Float32Array(count);
  let offset=0;
  for(const g of geometries){values.set(g.attributes[name].array,offset);offset+=g.attributes[name].array.length;}
  geometry.setAttribute(name,new THREE.BufferAttribute(values,name==='bridgeFeature'?1:3));
 }
 geometry.computeBoundingBox();geometry.computeBoundingSphere();
 for(const g of geometries)g.dispose();
 return geometry;
}
function sourceKeys(record){
 return [record.id,record.sourceId,String(record.source||'').replace(/^https?:\/\/(?:www\.)?openstreetmap\.org\//,'')].filter(Boolean);
}

export class BridgeLayer {
 constructor({scene,sampler,onChange=()=>{},prepare=prepareBridges}){
  Object.assign(this,{sampler,onChange,prepare});
  this.group=new THREE.Group();this.group.name='Mapped footbridges and elevated walking links';scene.add(this.group);
  this.records=new Map();this.loadedIds=new Set();this.tiles=new Map();this.cache=new Map();this.errors=new Map();this.requests=new Map();this.loadedPackages=new Set();
  this.surfaces=new InfrastructureSurfaces();this.suppressedIds=new Set();
  this.features=[];this.featureIndices=new Map();this.focus=[0,420];this.radius=3000;this.cameraPosition=null;this.railVertical=0;this.closed=false;this.coveredCount=0;this.estimatedCount=0;
  this.materials={
   source:new THREE.MeshStandardMaterial({vertexColors:true,roughness:.86}),
   deck:new THREE.MeshStandardMaterial({color:'#bdbeb0',roughness:.86}),
   steps:new THREE.MeshStandardMaterial({color:'#a9aca1',roughness:.9}),
   rail:new THREE.MeshStandardMaterial({color:'#7b8580',roughness:.55,metalness:.3}),
   canopy:new THREE.MeshStandardMaterial({color:'#8eaaa0',roughness:.72,metalness:.1}),
  };
  this.boxGeometry=new THREE.BoxGeometry(1,1,1);
 }
 async load(url){
  if(this.closed)return false;
  if(this.loadedPackages.has(url))return true;
  if(this.requests.has(url))return this.requests.get(url).promise;
  const controller=new AbortController();this.errors.delete(url);
  // Defer execution so even a synchronous fetch failure sees its request entry.
  const promise=Promise.resolve().then(async()=>{
   try{
    if(this.closed)return false;
    const response=await fetch(url,{signal:controller.signal});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const data=await response.json();
    if(this.closed||controller.signal.aborted)return false;
    const prepared=data.kind==='tai-o-official-infrastructure'?prepareInfrastructure(data):await this.prepare(data,this.sampler);
    if(this.closed||controller.signal.aborted)return false;
    if(!Array.isArray(prepared))throw new Error('Invalid prepared bridge inventory');
    // Validate the entire incoming batch before changing the visible inventory.
    for(const record of prepared){
     if(!record?.id||!record.source||!Array.isArray(record.bounds)||record.bounds.length!==4||!record.bounds.every(Number.isFinite))throw new Error('Invalid prepared bridge bounds');
     if(!record.modelGeometry)sectionsFor(record);
    }
    const changed=new Set();
    for(const record of prepared){
     if(this.records.has(record.id))continue;
     this.records.set(record.id,record);this.featureIndices.set(record.id,this.features.length);this.features.push(record);
     for(const key of sourceKeys(record))this.loadedIds.add(key);
     if(record.modelGeometry){
      this.surfaces.add(record);for(const id of record.suppresses){this.suppressedIds.add(id);this.loadedIds.add(id);}
      // A source mesh can arrive after its proxy was already rendered.
      for(const [key,tile]of this.tiles)if(tile.records.some(r=>this.suppressedIds.has(r.id)))changed.add(key);
     }
     if(record.estimatedPublicApproach){
      this.surfaces.add(walkingSurfaceFor(record));
     }
     if(covered(record))this.coveredCount++;if(record.estimatedElevation)this.estimatedCount++;
     const [minX,minZ,maxX,maxZ]=record.bounds,pad=record.width||0;
     const key=`${Math.floor((minX+maxX)/2/TILE_SIZE)}_${Math.floor((minZ+maxZ)/2/TILE_SIZE)}`;
     if(!this.tiles.has(key))this.tiles.set(key,{bounds:[minX-pad,minZ-pad,maxX+pad,maxZ+pad],records:[]});
     const tile=this.tiles.get(key);tile.records.push(record);tile.bounds=[Math.min(tile.bounds[0],minX-pad),Math.min(tile.bounds[1],minZ-pad),Math.max(tile.bounds[2],maxX+pad),Math.max(tile.bounds[3],maxZ+pad)];changed.add(key);
    }
    for(const key of changed)if(this.cache.has(key))this.disposeTile(key);
    this.loadedPackages.add(url);this.plan(...this.focus,this.radius);return true;
   }catch(error){
    if(!this.closed&&!controller.signal.aborted)this.errors.set(url,error.message||String(error));
    return false;
   }finally{
    this.requests.delete(url);if(!this.closed)this.onChange();
   }
  });
  this.requests.set(url,{promise,controller});this.onChange();return promise;
 }
 async retry(){return (await Promise.all([...this.errors.keys()].map(url=>this.load(url)))).every(Boolean);}
 buildTile(key){
  if(this.closed||this.cache.has(key)||!this.tiles.has(key))return;
  const tile=this.tiles.get(key),group=new THREE.Group(),bins=new Map(),canopies=[],beams=[];
  group.name='Footbridge tile '+key;group.userData.bridgeCount=tile.records.filter(r=>!this.suppressedIds.has(r.id)).length;group.userData.deckMeshes=[];
  for(const record of tile.records){
   if(this.suppressedIds.has(record.id))continue;
   const featureIndex=this.featureIndices.get(record.id),style=record.modelGeometry?'source':record.kind==='steps'?'steps':'deck';
   if(!bins.has(style))bins.set(style,[]);bins.get(style).push(geometryFor(record,featureIndex));
   if(record.modelGeometry)continue;
   const sections=sectionsFor(record);railBeams(sections,beams,covered(record));
   if(covered(record))canopies.push(solidGeometry(sectionsFor(record,record.width+.3,CANOPY_HEIGHT),.08,featureIndex));
  }
  for(const [style,geometries] of bins){
   const mesh=new THREE.Mesh(mergeGeometries(geometries),this.materials[style]);
   mesh.name='Mapped bridge decks';mesh.castShadow=mesh.receiveShadow=true;mesh.userData.bridgeLayer=this;mesh.userData.bridgePart='deck';
   group.userData.deckMeshes.push(mesh);group.add(mesh);
  }
  if(canopies.length){
   const mesh=new THREE.Mesh(mergeGeometries(canopies),this.materials.canopy);mesh.name='Explicitly mapped covered walkways';mesh.castShadow=mesh.receiveShadow=true;mesh.userData.bridgePart='canopy';group.add(mesh);
  }
  if(beams.length){
   const mesh=new THREE.InstancedMesh(this.boxGeometry,this.materials.rail,beams.length/7);
   const matrix=new THREE.Matrix4(),position=new THREE.Vector3(),direction=new THREE.Vector3(),scale=new THREE.Vector3(),rotation=new THREE.Quaternion();
   for(let i=0;i<beams.length;i+=7){
    position.set(beams[i],beams[i+1],beams[i+2]);direction.set(beams[i+3],beams[i+4],beams[i+5]);const length=direction.length();
    rotation.setFromUnitVectors(UP,direction.divideScalar(length));scale.set(beams[i+6],length,beams[i+6]);matrix.compose(position,rotation,scale);mesh.setMatrixAt(i/7,matrix);
   }
   mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingBox();mesh.computeBoundingSphere();mesh.name='Illustrative bridge guardrails and canopy posts';mesh.userData.bridgePart='rails';mesh.castShadow=false;mesh.receiveShadow=true;mesh.visible=Math.hypot(distanceToBounds(...this.focus,tile.bounds),this.railVertical)<=RAIL_DETAIL_RADIUS;group.userData.railMesh=mesh;group.add(mesh);
  }
  this.cache.set(key,group);this.group.add(group);
 }
 plan(x,z,radius=3000,cameraPosition=this.cameraPosition){
  if(this.closed||!Number.isFinite(x)||!Number.isFinite(z))return [];
  this.focus=[x,z];this.radius=Number.isFinite(radius)?Math.max(0,Math.min(5000,radius)):3000;
  this.cameraPosition=cameraPosition;this.railVertical=cameraPosition&&Number.isFinite(cameraPosition.y)?Math.max(0,cameraPosition.y-this.sampler.height(x,z)):0;
  const wanted=[...this.tiles].map(([key,tile])=>({key,distance:distanceToBounds(x,z,tile.bounds)})).filter(t=>t.distance<=this.radius).sort((a,b)=>a.distance-b.distance||a.key.localeCompare(b.key)).slice(0,TILE_LIMIT).map(t=>t.key);
  const active=new Set(wanted);for(const key of this.cache.keys())if(!active.has(key))this.disposeTile(key);
  for(const key of wanted){
   this.buildTile(key);const rails=this.cache.get(key)?.userData.railMesh;
   if(rails)rails.visible=Math.hypot(distanceToBounds(x,z,this.tiles.get(key).bounds),this.railVertical)<=RAIL_DETAIL_RADIUS;
  }
  return wanted;
 }
 geometryFor(record){return geometryFor(record,this.featureIndices.get(record.id)??0);}
 featureAt(hit){
  if(this.closed||!this.group.visible||hit?.object?.userData?.bridgeLayer!==this||!hit.object.visible||!hit.object.parent?.visible||hit.object.parent.parent!==this.group)return undefined;
  const attribute=hit.object.geometry?.getAttribute('bridgeFeature');
  const vertex=hit.face?.a??(Number.isInteger(hit.faceIndex)?hit.faceIndex*3:undefined);
  if(!attribute||!Number.isInteger(vertex)||vertex<0||vertex>=attribute.count)return undefined;
  return this.features[attribute.getX(vertex)];
 }
 pickMeshes(){
  if(this.closed||!this.group.visible)return [];
  return [...this.cache.values()].filter(group=>group.visible).flatMap(group=>group.userData.deckMeshes.filter(mesh=>mesh.visible));
 }
 disposeTile(key){
  const group=this.cache.get(key);if(!group)return;
  group.traverse(object=>{if(object.isInstancedMesh)object.dispose();else object.geometry?.dispose();});group.removeFromParent();this.cache.delete(key);
 }
 get stats(){const active=[...this.records.values()].filter(record=>!this.suppressedIds.has(record.id));return {spans:active.length,sourceModels:[...this.surfaces.models.values()].filter(m=>!m.estimatedPublicApproach).length,publicApproaches:[...this.surfaces.models.values()].filter(m=>m.estimatedPublicApproach).length,publicDecks:[...this.surfaces.models.values()].filter(m=>m.walkable&&!m.estimatedPublicApproach).length,suppressedProxies:this.suppressedIds.size,visibleSpans:this.group.visible?[...this.cache.values()].filter(group=>group.visible).reduce((count,group)=>count+group.userData.bridgeCount,0):0,tiles:this.cache.size,pending:this.requests.size,errors:[...this.errors.keys()],covered:active.filter(covered).length,estimatedElevation:active.filter(record=>record.estimatedElevation).length};}
 dispose(){
  if(this.closed)return;this.closed=true;
  for(const {controller} of this.requests.values())controller.abort();
  for(const key of this.cache.keys())this.disposeTile(key);
  this.boxGeometry.dispose();for(const material of Object.values(this.materials))material.dispose();
  this.group.removeFromParent();this.records.clear();this.loadedIds.clear();this.surfaces.clear();this.suppressedIds.clear();this.tiles.clear();this.features.length=0;this.featureIndices.clear();this.loadedPackages.clear();this.errors.clear();this.coveredCount=this.estimatedCount=0;
 }
}
