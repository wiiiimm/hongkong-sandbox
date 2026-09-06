import * as THREE from '../vendor/three.module.js';
import {TileCache} from './tile-cache.js';
import {prepareModelCatalogue,modelBudget,loadOfficialModel,disposeOfficialModel} from './official-model-assets.js';
const MiB=1024*1024;
export const MODEL_PROFILES=Object.freeze({
 mobile:Object.freeze({count:24,concurrency:1,geometryBytes:48*MiB,residentBytes:128*MiB,triangles:450000,landmarkDistance:1800,detailDistance:300,minPixels:24}),
 desktop:Object.freeze({count:48,concurrency:2,geometryBytes:96*MiB,residentBytes:256*MiB,triangles:900000,landmarkDistance:2500,detailDistance:500,minPixels:18}),
});
/** Progressive exact-source detail; ordinary source outlines remain the fallback. */
export class OfficialModelLayer{
 constructor({stream,profile='mobile',onChange=()=>{},loadAsset=loadOfficialModel}){
  if(!MODEL_PROFILES[profile])throw new Error('Unknown official model profile');
  Object.assign(this,{stream,profile,onChange,loadAsset});this.limits=MODEL_PROFILES[profile];this.models=new Map();this.catalogues=new Map();this.catalogueErrors=new Map();this.requests=new Map();this.retiring=new Map();this.releaseFailures=new Map();this.closed=false;this.lastPlan=-Infinity;this.lastCamera=null;this.lastOptions=null;
  this.cache=new TileCache({limit:this.limits.count,concurrency:this.limits.concurrency,load:(uid,signal)=>this.load(uid,signal),dispose:entry=>{this.release(entry).catch(()=>{});},onChange:()=>{if(!this.closed)this.onChange();}});
 }
 async loadCatalogue(input){
  if(this.closed)return false;const url=new URL(input,globalThis.location?.href||'http://localhost/').href;
  if(this.catalogues.has(url))return true;if(this.requests.has(url))return this.requests.get(url).promise;
  const controller=new AbortController();this.catalogueErrors.delete(url);
  const promise=Promise.resolve().then(async()=>{
   try{
    const response=await fetch(url,{signal:controller.signal});if(!response.ok)throw new Error('Model catalogue HTTP '+response.status);
    const text=await response.text();if(text.length>1024*1024)throw new Error('Model catalogue exceeds compact inventory budget');
    const entries=prepareModelCatalogue(JSON.parse(text),url);
    if(this.closed||controller.signal.aborted)return false;
    for(const entry of entries){const old=this.models.get(entry.uid);if(old&&(old.sha256!==entry.sha256||old.modelId!==entry.modelId))throw new Error('Conflicting model UID '+entry.uid);}
    for(const entry of entries)if(!this.models.has(entry.uid))this.models.set(entry.uid,entry);
    this.catalogues.set(url,{models:entries.length,bytes:new TextEncoder().encode(text).length});this.lastPlan=-Infinity;return true;
   }catch(error){if(!this.closed&&!controller.signal.aborted)this.catalogueErrors.set(url,error.message);return false;}
   finally{this.requests.delete(url);if(!this.closed)this.onChange();}
  });this.requests.set(url,{controller,promise});return promise;
 }
 async load(uid,signal){
  // Retired source geometry remains visible only until its fallback bake swaps.
  // Wait for that release before starting another decode; don't accumulate two
  // regions' collision arrays during rapid travel.
  await Promise.all([...this.retiring.values()]);
  if(signal.aborted||this.closed)throw new DOMException('Aborted','AbortError');
  if(this.releaseFailures.size)throw new Error('Previous model fallback restoration needs Retry');
  const meta=this.models.get(uid),building=this.stream.getLoadedBuilding(uid);
  if(!building)throw new Error('Official model source tile is not loaded');
  const entry=await this.loadAsset(meta,building,this.stream.lighting,{signal});
  try{
   if(signal.aborted||this.closed)throw new DOMException('Aborted','AbortError');
   if(this.stream.infrastructureBuildingUids?.has(uid))throw new Error('Official infrastructure already replaces this building');
   if(!await this.stream.setDetailedModel(uid,entry,{signal}))throw new DOMException('Aborted','AbortError');
   return entry;
  }catch(error){await this.release(entry);throw error;}
 }
 release(entry){
  if(this.retiring.has(entry))return this.retiring.get(entry);
  const promise=(async()=>{
   if(this.stream.detailedModels.get(entry.record.uid)===entry)await this.stream.setDetailedModel(entry.record.uid,null);
   disposeOfficialModel(entry);this.releaseFailures.delete(entry);
  })().catch(error=>{this.releaseFailures.set(entry,error.message);throw error;}).finally(()=>{this.retiring.delete(entry);if(!this.closed)this.onChange();});
  this.retiring.set(entry,promise);return promise;
 }
 plan(camera,{viewportHeight=800,selectedUid=null,now=performance.now(),force=false}={}){
  if(this.closed)return [];this.lastCamera=camera;this.lastOptions={viewportHeight,selectedUid};
  if(!force&&now-this.lastPlan<180)return this.cache.wanted;this.lastPlan=now;
  camera.updateMatrixWorld(true);const matrix=new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse),frustum=new THREE.Frustum().setFromProjectionMatrix(matrix),eye=new THREE.Vector3().setFromMatrixPosition(camera.matrixWorld);
  const candidates=[],limits=this.limits,pixels=Math.max(1,Math.min(8192,viewportHeight)),fov=THREE.MathUtils.degToRad(camera.getEffectiveFOV());
  for(const entry of this.models.values()){
   const box=new THREE.Box3(new THREE.Vector3(...entry.worldBounds[0]),new THREE.Vector3(...entry.worldBounds[1])),distance=box.distanceToPoint(eye),resident=this.cache.entries.has(entry.uid),selected=selectedUid===entry.uid;
   const range=(entry.priority==='landmark'?limits.landmarkDistance:limits.detailDistance)*(resident?1.2:1);
   const extent=box.getSize(new THREE.Vector3()),projected=Math.max(extent.x,extent.y,extent.z)*pixels/(2*Math.tan(fov/2)*Math.max(1,box.getCenter(new THREE.Vector3()).distanceTo(eye)));
   const visible=frustum.intersectsBox(box);
   if(distance>range||!visible&&!resident||!selected&&projected<limits.minPixels*(resident?.75:1)||this.stream.infrastructureBuildingUids?.has(entry.uid))continue;
   const building=this.stream.getLoadedBuilding(entry.uid);if(!building||building.modelGeometry&&!this.stream.detailedModels.has(entry.uid))continue;
   candidates.push({entry,distance,selected,projected,visible});
  }
  candidates.sort((a,b)=>Number(b.selected)-Number(a.selected)||Number(b.visible)-Number(a.visible)||a.distance-b.distance||b.projected-a.projected||a.entry.uid.localeCompare(b.entry.uid));
  const wanted=[];let geometry=0,resident=0,triangles=0;
  for(const {entry} of candidates){const cost=modelBudget(entry);if(wanted.length>=limits.count||geometry+cost.geometryBytes>limits.geometryBytes||resident+cost.residentBytes>limits.residentBytes||triangles+cost.triangles>limits.triangles)continue;wanted.push(entry.uid);geometry+=cost.geometryBytes;resident+=cost.residentBytes;triangles+=cost.triangles;}
  // Release models outside the selected distance/budget set. Fallback restoration
  // completes before each buffer is disposed; no model is silently dropped.
  const keep=new Set(wanted);for(const [uid,entry] of this.cache.entries)if(!keep.has(uid)){this.cache.entries.delete(uid);this.release(entry).catch(()=>{});}
  if(wanted.join('|')!==this.cache.wanted.join('|'))this.cache.plan(wanted);
  return wanted;
 }
 async retry(){
  await Promise.allSettled([...this.releaseFailures.keys()].map(entry=>this.release(entry)));
  await Promise.all([...this.catalogueErrors.keys()].map(url=>this.loadCatalogue(url)));this.cache.retry();
  if(this.lastCamera)this.plan(this.lastCamera,{...this.lastOptions,force:true});
 }
 get stats(){
  const entries=[...this.cache.entries.values()],held=[...new Set([...entries,...this.retiring.keys(),...this.releaseFailures.keys()])],cost=held.reduce((sum,e)=>({geometryBytes:sum.geometryBytes+e.budget.geometryBytes,residentBytes:sum.residentBytes+e.budget.residentBytes,triangles:sum.triangles+e.budget.triangles}),{geometryBytes:0,residentBytes:0,triangles:0});
  return {profile:this.profile,catalogues:this.catalogues.size,available:this.models.size,cached:entries.length,visible:entries.filter(e=>e.group.visible).length,pending:this.cache.running.size+this.requests.size,retiring:this.retiring.size,wanted:this.cache.wanted.length,errors:[...this.catalogueErrors.keys(),...this.cache.errors.keys(),...this.releaseFailures.keys()].map(value=>typeof value==='string'?value:'restore:'+value.record.uid),...cost,limits:this.limits};
 }
 async dispose(){
  if(this.closed)return;this.closed=true;for(const {controller} of this.requests.values())controller.abort();this.cache.close();await Promise.allSettled([...this.retiring.values()]);this.models.clear();this.catalogues.clear();this.catalogueErrors.clear();
 }
}
