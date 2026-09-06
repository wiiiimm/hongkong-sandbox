import * as THREE from '../vendor/three.module.js';
import {BuildingIndex} from './geo.js';
import {makeBuildings,makeRoads,makeNature} from './world.js';
import {TileCache,distanceToBounds,nearbyTiles} from './tile-cache.js';
import {cityLighting} from './lighting.js';
export function disposeGroup(group){
 group.removeFromParent();const geometries=new Set(),materials=new Set();
 group.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of o.material?[].concat(o.material):[])materials.add(m);if(o.isInstancedMesh)o.dispose();});
 for(const g of geometries)g.dispose();for(const m of materials)m.dispose();
}
export class CityStreaming {
 constructor({manifest,terrain,sampler,scene,onChange,activity}){
  Object.assign(this,{manifest,terrain,sampler,scene,onChange,activity});this.meta=new Map(manifest.tiles.map(t=>[t.id,t]));
  this.buildings=new THREE.Group();this.roads=new THREE.Group();this.trees=new THREE.Group();scene.add(this.buildings,this.roads,this.trees);
  this.lighting={night:{value:0},activity:{value:new Float32Array(cityLighting(15).activity.slice(0,4))},retail:{value:cityLighting(15).activity[4]},elapsed:{value:0},shimmer:{value:1}};this.surfaceMask=null;this.bridgeRoadIds=new Set();this.night=this.lighting.night;this.focus=[0,420];this.detailRadius=2200;this.revision=0;
  this.cache=new TileCache({limit:30,concurrency:2,load:(id,signal)=>this.load(id,signal),dispose:entry=>{for(const g of [entry.buildings.group,entry.roads,entry.nature.group])disposeGroup(g);},onChange:()=>{this.revision++;this.sync();this.onChange?.();}});
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
  const index=new BuildingIndex(data.buildings);const buildings=await makeBuildings(data.buildings,null,{lighting:this.lighting});
  for(const mesh of buildings.group.children)mesh.userData.tile=id;
  let roads,nature;
  try{
   if(signal.aborted)throw new DOMException('Aborted','AbortError');
   roads=makeRoads(data.roads,this.sampler,this.lighting,{excludeIds:this.bridgeRoadIds});
   const [x,z]=id.split('_').map(Number),s=this.manifest.tileSize;
   nature=makeNature(data.parks,this.terrain,this.sampler,index,{bounds:[x*s,z*s,(x+1)*s,(z+1)*s],seed:(x*73856093^z*19349663)>>>0});
   if(this.surfaceMask)nature.applyMask((x,z,r)=>!!this.surfaceMask.collision(x,z,0,1000,r));
   return {id,data,index,buildings,roads,nature,pickBounds:new THREE.Box3().setFromObject(buildings.group)};
  }catch(error){disposeGroup(buildings.group);if(roads)disposeGroup(roads);if(nature)disposeGroup(nature.group);throw error;}
 }
 suppressBridgeRoads(ids){
  this.bridgeRoadIds=new Set(ids);
  for(const entry of this.cache.entries.values()){
   const roads=makeRoads(entry.data.roads,this.sampler,this.lighting,{excludeIds:this.bridgeRoadIds});
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
   if(!e.buildings.group.parent){this.buildings.add(e.buildings.group);this.roads.add(e.roads);this.trees.add(e.nature.group);}
   const visible=wanted.has(id),near=distanceToBounds(...this.focus,this.meta.get(id).bounds)<=this.detailRadius;
   e.buildings.group.visible=visible;e.roads.visible=e.nature.group.visible=visible&&near;
   for(const mesh of e.buildings.group.children)mesh.castShadow=visible&&near;
  }
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
  this.plan(...meta.centre,3200);await this.cache.waitFor([tile]);return this.cache.entries.get(tile)?.data.buildings.find(b=>b.uid===uid);
 }
 pickMeshes(ray){
  if(!this.buildings.visible)return [];
  return [...this.cache.entries.values()].filter(e=>e.buildings.group.visible&&ray.intersectsBox(e.pickBounds)).flatMap(e=>e.buildings.group.children);
 }
 featureAt(hit){return this.cache.entries.get(hit.object.userData.tile)?.data.buildings[Math.round(hit.object.geometry.attributes.feature.getX(hit.face.a))];}
 collision(x,z,bottom,top,radius=.5){
  for(const t of this.manifest.tiles){if(distanceToBounds(x,z,t.bounds)>radius)continue;const hit=this.cache.entries.get(t.id)?.index.collision(x,z,bottom,top,radius);if(hit)return hit;}return null;
 }
 maximumRoof(x,z,radius=20){
  let maximum=0;for(const id of this.required(x,z,radius)){const index=this.cache.entries.get(id)?.index;if(index)maximum=Math.max(maximum,index.maximumRoof(x,z,radius));}return maximum;
 }
 get stats(){
  let loaded=0,trees=0;for(const id of this.cache.wanted){const e=this.cache.entries.get(id);if(e){loaded+=e.data.buildings.length;trees+=e.nature.count;}}
  return {wanted:this.cache.wanted.length,cached:this.cache.entries.size,loaded:this.cache.wanted.filter(id=>this.cache.entries.has(id)).length,pending:this.cache.wanted.filter(id=>!this.cache.entries.has(id)&&!this.cache.errors.has(id)).length,errors:this.cache.wanted.filter(id=>this.cache.errors.has(id)),forms:loaded,trees};
 }
}
