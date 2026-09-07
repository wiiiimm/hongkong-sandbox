import * as THREE from '../vendor/three.module.js';
import {BuildingIndex} from './geo.js';
import {makeBuildings,makeRoads,makeNature} from './world.js';
import {TileCache,distanceToBounds,nearbyTiles} from './tile-cache.js';
import {retainedRoads,validateProxyClips} from './infrastructure-replacements.js';
import {cityLighting} from './lighting.js';
export function disposeGroup(group){
 group.removeFromParent();const geometries=new Set(),materials=new Set(group.userData.disposableMaterials||[]);
 group.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of o.material?[].concat(o.material):[])materials.add(m);if(o.isInstancedMesh)o.dispose();});
 for(const g of geometries)g.dispose();for(const m of materials)m.dispose();
}
export class CityStreaming {
 constructor({manifest,terrain,sampler,scene,onChange,activity,inspection}){
  Object.assign(this,{manifest,terrain,sampler,scene,onChange,activity,inspection});this.meta=new Map(manifest.tiles.map(t=>[t.id,t]));
  this.buildings=new THREE.Group();this.roads=new THREE.Group();this.trees=new THREE.Group();scene.add(this.buildings,this.roads,this.trees);
  this.lighting={night:{value:0},activity:{value:new Float32Array(cityLighting(15).activity.slice(0,4))},retail:{value:cityLighting(15).activity[4]},elapsed:{value:0},shimmer:{value:1}};this.surfaceMask=null;this.bridgeRoadIds=new Set();this.infrastructureBuildingUids=new Set();this.infrastructureRoadClips=new Map();this.infrastructureErrors=new Map();this.detailedModels=new Map();this.night=this.lighting.night;this.focus=[0,420];this.detailRadius=2200;this.revision=0;
  this.cache=new TileCache({limit:30,concurrency:2,load:(id,signal)=>this.load(id,signal),dispose:entry=>{for(const g of [entry.buildings.group,entry.roads,entry.nature.group])disposeGroup(g);},onChange:()=>{this.revision++;this.sync();this.suppressInfrastructureBuildings(this.infrastructureBuildingUids).catch(()=>{});this.onChange?.();}});
 }
 async load(id,signal){
  const read=async(url,label)=>{const response=await fetch(url,{signal});if(!response.ok)throw new Error(`${label} ${id}: HTTP ${response.status}`);return response.json();};
  // Profiles must arrive before facade attributes are baked. Both requests share
  // the tile cancellation signal and the existing readiness/retry lifecycle.
  const [data,activity]=await Promise.all([read(this.meta.get(id).url,'City section'),this.manifest.activityTiles?read(`city/data/activity/${id}.json`,'City activity'):this.activity]);
  if(signal.aborted)throw new DOMException('Aborted','AbortError');
  if(data.id!==id||!Array.isArray(data.buildings))throw new Error('Invalid city section '+id);
  if(!activity?.buildings||typeof activity.buildings!=='object'||Array.isArray(activity.buildings))throw new Error('Invalid city activity '+id);
  for(const b of data.buildings){
   const entry=activity.buildings[b.uid];
   if(this.manifest.activityTiles&&(!entry||!Number.isInteger(entry.profile)||entry.profile<0||entry.profile>4||!Number.isFinite(entry.retailTop)||entry.retailTop<0))throw new Error(`Invalid city activity ${id} for ${b.uid}`);
   b.activity=entry;
  }
  const baked=await this.prepareBuildings(data,signal),{index,buildings}=baked;
  let roads,nature;
  try{
   if(signal.aborted)throw new DOMException('Aborted','AbortError');
   roads=this.makeTileRoads(data);
   const [x,z]=id.split('_').map(Number),s=this.manifest.tileSize;
   nature=makeNature(data.parks,this.terrain,this.sampler,baked.suppressedBuildings?new BuildingIndex(data.buildings):index,{bounds:[x*s,z*s,(x+1)*s,(z+1)*s],seed:(x*73856093^z*19349663)>>>0});
   if(this.surfaceMask)nature.applyMask((x,z,r)=>!!this.surfaceMask.collision(x,z,0,1000,r));
   return {id,data,...baked,roads,nature};
  }catch(error){disposeGroup(buildings.group);if(roads)disposeGroup(roads);if(nature)disposeGroup(nature.group);throw error;}
 }
 async prepareBuildings(data,signal){
  // Each bake uses a stable replacement set. If a package completes while this
  // asynchronous tile is baking, discard that bake and use the latest set.
  for(;;){
   const exclusions=this.infrastructureBuildingUids,models=this.detailedModels,indices=[];
   const features=data.buildings.filter((b,i)=>{if(exclusions.has(b.uid)||models.has(b.uid))return false;indices.push(i);return true;});
   const buildings=await makeBuildings(features,null,{lighting:this.lighting});buildings.group.userData.disposableMaterials=buildings.materials;
   if(signal?.aborted||this.cache.closed){disposeGroup(buildings.group);throw new DOMException('Aborted','AbortError');}
   if(exclusions!==this.infrastructureBuildingUids||models!==this.detailedModels){disposeGroup(buildings.group);continue;}
   for(const mesh of buildings.group.children){
    mesh.userData.tile=data.id;
    const attribute=mesh.geometry.attributes.feature;
    for(let i=0;i<attribute.count;i++)attribute.setX(i,indices[attribute.getX(i)]);
   }
   return {buildings,index:new BuildingIndex(data.buildings.filter(b=>!exclusions.has(b.uid)).map(b=>models.get(b.uid)?.record||b)),exclusions,models,suppressedBuildings:data.buildings.filter(b=>exclusions.has(b.uid)).length,pickBounds:new THREE.Box3().setFromObject(buildings.group)};
  }
 }
 async suppressInfrastructureBuildings(ids){
  const next=new Set(ids);
  if([...next].some(uid=>typeof uid!=='string'||!uid))throw new Error('Invalid infrastructure building UID');
  const previous=this.infrastructureBuildingUids;
  if(next.size!==previous.size||[...next].some(uid=>!previous.has(uid)))this.infrastructureBuildingUids=next;
  return this.refreshBuildings();
 }
 async refreshBuildings(){
  if(this.cache.closed)return;
  const jobs=[];
  for(const entry of this.cache.entries.values()){
   if(!entry.infrastructureUpdate&&entry.data.buildings.some(b=>entry.exclusions.has(b.uid)!==this.infrastructureBuildingUids.has(b.uid)||entry.models?.get(b.uid)!==this.detailedModels.get(b.uid))){
    entry.infrastructureUpdate=(async()=>{
     const baked=await this.prepareBuildings(entry.data);
     if(this.cache.closed||this.cache.entries.get(entry.id)!==entry){disposeGroup(baked.buildings.group);return;}
     // Commit rendering and collision together; the previous outline stays until
     // the replacement bake succeeds. Raw source records and picking IDs remain.
     disposeGroup(entry.buildings.group);Object.assign(entry,baked);
     this.buildings.add(entry.buildings.group);this.inspection?.register(entry.buildings.group,'structures');this.infrastructureErrors.delete(entry.id);this.revision++;this.sync();this.onChange?.();
    })().catch(error=>{if(!this.cache.closed){this.infrastructureErrors.set(entry.id,error.message);this.onChange?.();}throw error;}).finally(()=>{delete entry.infrastructureUpdate;});
   }
   if(entry.infrastructureUpdate)jobs.push(entry.infrastructureUpdate);
  }
  await Promise.all(jobs);
 }
 getLoadedBuilding(uid){
  const detail=this.detailedModels.get(uid);if(detail?.active)return detail.record;
  for(const entry of this.cache.entries.values()){const b=entry.data.buildings.find(b=>b.uid===uid);if(b)return b;}return null;
 }
 async setDetailedModel(uid,detail,{signal}={}){
  if(signal?.aborted)return false;
  const old=this.detailedModels.get(uid);if(old===detail)return true;
  if(detail&&(detail.record.uid!==uid||!detail.group||!detail.record.modelGeometry))throw new Error('Invalid detailed building replacement');
  this.detailedModels=new Map(this.detailedModels);if(detail)this.detailedModels.set(uid,detail);else this.detailedModels.delete(uid);
  const cancel=()=>{if((this.detailedModels.get(uid)||null)===(detail||null)){this.detailedModels=new Map(this.detailedModels);if(old)this.detailedModels.set(uid,old);else this.detailedModels.delete(uid);}};
  signal?.addEventListener('abort',cancel,{once:true});
  try{await this.refreshBuildings();}
  catch(error){
   // Keep the previous visible geometry if a replacement bake fails.
   cancel();throw error;
  }finally{signal?.removeEventListener('abort',cancel);}
  if((this.detailedModels.get(uid)||null)!==(detail||null))return false;
  if(old){old.active=false;old.group.removeFromParent();}
  if(detail&&!this.cache.closed){detail.active=true;this.buildings.add(detail.group);this.inspection?.register(detail.group,'structures');}
  this.revision++;this.sync();this.onChange?.();return !this.cache.closed;
 }
 makeTileRoads(data){
  const [x,z]=data.id.split('_').map(Number),s=this.manifest.tileSize;
  return makeRoads(retainedRoads(data.roads,this.infrastructureRoadClips,[x*s,z*s,(x+1)*s,(z+1)*s]),this.sampler,this.lighting,{excludeIds:this.bridgeRoadIds});
 }
 suppressBridgeRoads(ids,proxyClips=[]){
  const clips=validateProxyClips([...proxyClips]);
  const nextIds=new Set(ids),nextClips=new Map(clips.map(c=>[c.id,c]));
  if(nextIds.size===this.bridgeRoadIds.size&&[...nextIds].every(id=>this.bridgeRoadIds.has(id))&&nextClips.size===this.infrastructureRoadClips.size&&[...nextClips].every(([id,c])=>this.infrastructureRoadClips.get(id)===c))return;
  this.bridgeRoadIds=nextIds;this.infrastructureRoadClips=nextClips;
  for(const entry of this.cache.entries.values()){
   const roads=this.makeTileRoads(entry.data);
   disposeGroup(entry.roads);entry.roads=roads;this.roads.add(roads);
  }this.sync();
 }
 setSurfaceExclusions(surfaces){
  this.surfaceMask=new BuildingIndex(surfaces.map(s=>({...s,base:-1000,minimum:0,height:10000})));
  for(const e of this.cache.entries.values())e.nature.applyMask((x,z,r)=>!!this.surfaceMask.collision(x,z,0,1000,r));
 }
 sync(){
  const wanted=new Set(this.cache.wanted);
  for(const [id,e] of this.cache.entries){
   if(!e.buildings.group.parent){this.buildings.add(e.buildings.group);this.inspection?.register(e.buildings.group,'structures');this.roads.add(e.roads);this.trees.add(e.nature.group);}
   const visible=wanted.has(id),near=distanceToBounds(...this.focus,this.meta.get(id).bounds)<=this.detailRadius;
   e.buildings.group.visible=visible;e.roads.visible=e.nature.group.visible=visible&&near;
   for(const mesh of e.buildings.group.children)mesh.castShadow=visible&&near;
  }
  for(const detail of this.detailedModels.values()){detail.group.visible=detail.active&&wanted.has(detail.record.tile)&&this.cache.entries.has(detail.record.tile);for(const mesh of detail.meshes||[])mesh.castShadow=detail.group.visible&&distanceToBounds(...this.focus,[detail.bounds.min.x,detail.bounds.min.z,detail.bounds.max.x,detail.bounds.max.z])<=this.detailRadius;}
 }
 plan(x,z,radius=3200){
  this.focus=[x,z];const ids=nearbyTiles(this.manifest.tiles,x,z,radius,24);
  if(ids.join('|')!==this.cache.wanted.join('|'))this.cache.plan(ids);else this.sync();return ids;
 }
 required(x,z,r=35){return this.manifest.tiles.filter(t=>distanceToBounds(x,z,t.bounds)<=r).map(t=>t.id);}
 readyAt(x,z,r=35){return this.cache.ready(this.required(x,z,r));}
 async arrive(x,z,radius=3200){this.plan(x,z,radius);return this.cache.waitFor(this.required(x,z,500));}
 async getBuilding(tile,uid){
  const meta=this.meta.get(tile);if(!meta)throw new Error('Unknown city section');
  this.plan(...meta.centre,3200);await this.cache.waitFor([tile]);return this.getLoadedBuilding(uid);
 }
 pickMeshes(ray){
  if(!this.buildings.visible)return [];
  return [...this.cache.entries.values()].filter(e=>e.buildings.group.visible&&ray.intersectsBox(e.pickBounds)).flatMap(e=>e.buildings.group.children).concat([...this.detailedModels.values()].filter(d=>d.active&&d.group.visible&&ray.intersectsBox(d.bounds)).flatMap(d=>d.meshes));
 }
 featureAt(hit){const detail=this.detailedModels.get(hit.object.userData.officialBuildingUid);if(detail?.active)return detail.record;return this.cache.entries.get(hit.object.userData.tile)?.data.buildings[Math.round(hit.object.geometry.attributes.feature.getX(hit.face.a))];}
 collision(x,z,bottom,top,radius=.5){
  for(const detail of this.detailedModels.values())if(detail.active){const b=detail.bounds;if(x+radius>=b.min.x&&x-radius<=b.max.x&&z+radius>=b.min.z&&z-radius<=b.max.z){detail.index??=new BuildingIndex([detail.record]);const hit=detail.index.collision(x,z,bottom,top,radius);if(hit)return hit;}}
  for(const t of this.manifest.tiles){if(distanceToBounds(x,z,t.bounds)>radius)continue;const hit=this.cache.entries.get(t.id)?.index.collision(x,z,bottom,top,radius);if(hit)return hit;}return null;
 }
 maximumRoof(x,z,radius=20){
  let maximum=0;for(const detail of this.detailedModels?.values()||[])if(detail.active&&distanceToBounds(x,z,[detail.bounds.min.x,detail.bounds.min.z,detail.bounds.max.x,detail.bounds.max.z])<=radius)maximum=Math.max(maximum,detail.bounds.max.y,detail.record.base+detail.record.height);for(const id of this.required(x,z,radius)){const index=this.cache.entries.get(id)?.index;if(index)maximum=Math.max(maximum,index.maximumRoof(x,z,radius));}return maximum;
 }
 get stats(){
  let loaded=0,trees=0,suppressedBuildings=0;for(const id of this.cache.wanted){const e=this.cache.entries.get(id);if(e){loaded+=e.data.buildings.length;trees+=e.nature.count;suppressedBuildings+=e.suppressedBuildings||0;}}
  return {wanted:this.cache.wanted.length,cached:this.cache.entries.size,loaded:this.cache.wanted.filter(id=>this.cache.entries.has(id)).length,pending:this.cache.wanted.filter(id=>!this.cache.entries.has(id)&&!this.cache.errors.has(id)).length,errors:this.cache.wanted.filter(id=>this.cache.errors.has(id)),forms:loaded,trees,suppressedBuildings,detailedModels:[...this.detailedModels.values()].filter(d=>d.active).length,infrastructureErrors:[...this.infrastructureErrors.keys()]};
 }
}
