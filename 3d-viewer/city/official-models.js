import {ModelSpatialIndex,projectedBounds} from './model-spatial-index.js';
import {ModelByteCache,yieldModelWork} from './model-byte-cache.js';
import {streamingMetrics as metrics} from './streaming-metrics.js';
import * as THREE from '../vendor/three.module.js';
import {TileCache} from './tile-cache.js?v=20260913-load2';
import {prepareModelCatalogue,modelBudget,loadOfficialModel,disposeOfficialModel} from './official-model-assets.js';
import {modelSupportDependencies,supportedModelPlan} from './model-support.js';
const MiB=1024*1024;
export const MODEL_PROFILES=Object.freeze({
 mobile:Object.freeze({count:24,concurrency:1,geometryBytes:48*MiB,residentBytes:128*MiB,selectedResidentBytes:160*MiB,triangles:450000,landmarkDistance:1800,detailDistance:300,minPixels:24,drawCalls:128}),
 desktop:Object.freeze({count:48,concurrency:1,geometryBytes:96*MiB,residentBytes:256*MiB,triangles:900000,landmarkDistance:2500,detailDistance:500,minPixels:18,drawCalls:256}),
});
/** Progressive exact-source detail; ordinary source outlines remain the fallback. */
export class OfficialModelLayer{
 constructor({stream,profile='mobile',onChange=()=>{},onReveal=()=>{},loadAsset=loadOfficialModel,warmMs=10000}){
  if(!MODEL_PROFILES[profile])throw new Error('Unknown official model profile');
  Object.assign(this,{stream,profile,onChange,onReveal,loadAsset});this.limits=MODEL_PROFILES[profile];this.warmMs=warmMs;this.byteCache=new ModelByteCache();this.lastUseful=new Map();this.smallSince=new Map();this.activating=new Map();this.activeControllers=new Map();this.changeTail=Promise.resolve();this.signature='';this.nextCheck=Infinity;this.index=null;this.dirty=true;this.drawWanted=new Set();this.matrix=new THREE.Matrix4();this.frustum=new THREE.Frustum();this.eye=new THREE.Vector3();this.models=new Map();this.catalogues=new Map();this.catalogueErrors=new Map();this.requests=new Map();this.retiring=new Map();this.releaseFailures=new Map();this.supportHolds=new Map();this.closed=false;this.lastCheck=-Infinity;this.lastPlan=-Infinity;this.lastCamera=null;this.lastOptions=null;
  this.cache=new TileCache({abortOnPause:false,limit:this.limits.count,concurrency:this.limits.concurrency,load:(uid,signal)=>this.load(uid,signal),dispose:entry=>{this.release(entry).catch(()=>{});},onChange:()=>{this.dirty=true;if(!this.closed)this.onChange();}});
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
    for(const entry of entries){modelSupportDependencies(entry);const old=this.models.get(entry.uid);if(old&&(old.sha256!==entry.sha256||old.modelId!==entry.modelId))throw new Error('Conflicting model UID '+entry.uid);}
    for(const entry of entries)if(!this.models.has(entry.uid))this.models.set(entry.uid,entry);
    this.catalogues.set(url,{models:entries.length,bytes:new TextEncoder().encode(text).length});this.index=null;this.dirty=true;this.lastPlan=-Infinity;return true;
   }catch(error){if(!this.closed&&!controller.signal.aborted)this.catalogueErrors.set(url,error.message);return false;}
   finally{this.requests.delete(url);if(!this.closed)this.onChange();}
  });this.requests.set(url,{controller,promise});return promise;
 }
 supportAvailable(uid,kind,dependency={}){
  if(this.stream.infrastructureBuildingUids?.has(uid))return false;
  const building=this.stream.getLoadedBuilding(uid);if(!building)return false;
  if(dependency.csuid&&building.buildingCSUID!==dependency.csuid)return false;
  if(kind==='fallback'){
   // A managed native model may retire before loading this tower. Baked source
   // geometry has no surveyed fallback swap in this layer and cannot stand in.
   if(building.modelGeometry&&!this.cache.entries.has(uid))return false;
   return !this.stream.cache||this.stream.cache.wanted.includes(building.tile);
  }
  return !building.modelGeometry||this.stream.detailedModels.has(uid);
 }
 async waitForSupports(meta,signal){
  const dependencies=modelSupportDependencies(meta),native=dependencies.filter(d=>d.kind==='native').map(d=>d.uid);
  if(native.length){
   if(signal.aborted)throw new DOMException('Aborted','AbortError');
   await new Promise((resolve,reject)=>{
    const finish=(error)=>{this.cache.listeners.delete(check);signal.removeEventListener('abort',cancel);error?reject(error):resolve();};
    const cancel=()=>finish(new DOMException('Aborted','AbortError'));
    const check=()=>{
     if(signal.aborted||this.closed||native.some(uid=>!this.cache.wanted.includes(uid)))return cancel();
     const error=native.map(uid=>this.cache.errors.get(uid)).find(Boolean);if(error)return finish(error);
     if(native.every(uid=>this.cache.entries.has(uid)&&this.stream.detailedModels.get(uid)?.active))finish();
    };
    this.cache.listeners.add(check);signal.addEventListener('abort',cancel,{once:true});check();
   });
  }
  for(const d of dependencies){
   if(!this.supportAvailable(d.uid,d.kind,d)||d.kind==='fallback'&&this.stream.detailedModels.has(d.uid))throw new Error('Required model support not ready: '+d.uid);
  }
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
  await this.waitForSupports(meta,signal);
  const loadStart=metrics.start();
  const entry=await this.loadAsset(meta,building,this.stream.lighting,{signal,byteCache:this.byteCache,beforeDecode:signal=>this.readyForWork(signal)});metrics.end('modelLoadMs',loadStart);
  try{
   if(signal.aborted||this.closed)throw new DOMException('Aborted','AbortError');
   await this.waitForSupports(meta,signal);
   if(this.stream.infrastructureBuildingUids?.has(uid))throw new Error('Official infrastructure already replaces this building');
   const installStart=metrics.start();
   await this.reserveDrawCalls(entry);
   if(!await this.change(()=>this.stream.setDetailedModel(uid,entry,{signal}),signal))throw new DOMException('Aborted','AbortError');
   metrics.end('modelInstallMs',installStart);this.onReveal(entry);
   return entry;
  }catch(error){await this.release(entry);throw error;}
 }
 release(entry){
  if(this.retiring.has(entry))return this.retiring.get(entry);
  const retireStart=metrics.start();this.activeControllers.get(entry.record.uid)?.abort();
  const promise=(async()=>{
   await this.activating.get(entry.record.uid)?.catch(()=>{});
   const supports=modelSupportDependencies(entry.entry||this.models.get(entry.record.uid)).filter(d=>d.kind==='native').map(d=>this.stream.detailedModels.get(d.uid)).filter(Boolean);
   // setDetailedModel removes its map entry before the asynchronous fallback
   // bake finishes. Keep supports visible until the old tower actually leaves.
   for(const support of supports)(support.supportVisibilityDependents??=new Set()).add(entry);
   // Restore every dependent's original form before removing its support. This
   // also preserves supports when a dependent fallback rebake fails.
   const dependents=[...this.stream.detailedModels.values()].filter(value=>value!==entry&&modelSupportDependencies(value.entry||this.models.get(value.record.uid)).some(d=>d.kind==='native'&&d.uid===entry.record.uid));
   for(const dependent of dependents){this.cache.entries.delete(dependent.record.uid);await this.release(dependent);}
   if(this.stream.detailedModels.get(entry.record.uid)===entry)await this.change(()=>this.stream.setDetailedModel(entry.record.uid,null));
   disposeOfficialModel(entry);for(const support of supports)support.supportVisibilityDependents.delete(entry);this.releaseFailures.delete(entry);
  })().catch(error=>{this.releaseFailures.set(entry,error.message);throw error;}).finally(()=>{metrics.end('modelRetireMs',retireStart);this.retiring.delete(entry);if(!this.closed)this.onChange();});
  this.retiring.set(entry,promise);return promise;
 }
 async reserveDrawCalls(entry){
  const cost=e=>e.budget.drawCalls??e.meshes?.length??1,total=()=>cost(entry)+[...this.cache.entries.values()].reduce((n,e)=>n+cost(e),0);
  for(const [uid,warm] of this.cache.entries){
   if(total()<=this.limits.drawCalls)break;if(this.drawWanted.has(uid))continue;
   this.cache.entries.delete(uid);this.lastUseful.delete(uid);this.cache.wanted=this.cache.wanted.filter(id=>id!==uid);await this.release(warm);
  }
  if(total()>this.limits.drawCalls)throw new Error('Model draw-call budget exceeded');
 }
 async readyForWork(signal){
  if(this.cache.paused)await new Promise((resolve,reject)=>{
   const finish=error=>{this.cache.listeners.delete(check);signal?.removeEventListener('abort',check);error?reject(error):resolve();};
   const check=()=>{if(this.closed||signal?.aborted)finish(new DOMException('Aborted','AbortError'));else if(!this.cache.paused)finish();};
   this.cache.listeners.add(check);signal?.addEventListener('abort',check,{once:true});check();
  });
  await yieldModelWork(signal);
 }
 change(operation,signal){
  const run=this.changeTail.catch(()=>{}).then(async()=>{await yieldModelWork(signal);return operation();});this.changeTail=run;return run;
 }
 setProfile(profile){
  if(!MODEL_PROFILES[profile])throw new Error('Unknown official model profile');
  if(profile===this.profile)return;this.profile=profile;this.limits=MODEL_PROFILES[profile];this.cache.limit=this.limits.count;this.dirty=true;this.cache.retry();
 }
 plan(camera,{viewportWidth,viewportHeight=800,selectedUid=null,collisionPosition=null,allowNewLoads=true,now=performance.now(),force=false}={}){
  if(this.closed)return [];viewportWidth??=viewportHeight*(camera.aspect||1);this.lastCamera=camera;this.lastOptions={viewportWidth,viewportHeight,selectedUid,collisionPosition,allowNewLoads};
  if(!(viewportWidth>0&&viewportHeight>0)){this.setLoadingPaused(true);return this.cache.wanted;}
  if(!force&&now-this.lastCheck<180)return this.cache.wanted;this.lastCheck=now;
  camera.updateMatrixWorld(true);
  const signature=[...camera.matrixWorld.elements.map(v=>Math.round(v*10000)),...camera.projectionMatrix.elements,viewportWidth,viewportHeight,selectedUid,collisionPosition?.x,collisionPosition?.y,collisionPosition?.z,allowNewLoads,this.stream.revision,this.models.size,this.profile].join('|');
  if(!force&&!this.dirty&&signature===this.signature&&now<this.nextCheck)return this.cache.wanted;
  this.lastPlan=now;this.signature=signature;this.dirty=false;this.nextCheck=Infinity;
  const planStart=metrics.start();metrics.count('plans');
  if(!this.index||this.index.entries.size!==this.models.size){const start=metrics.start();this.index=new ModelSpatialIndex(this.models);metrics.end('modelIndexMs',start);}
  this.matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);this.frustum.setFromProjectionMatrix(this.matrix);this.eye.setFromMatrixPosition(camera.matrixWorld);
  const query=this.index.query(this.frustum,this.eye),rows=new Map(query.rows.map(row=>[row.entry.uid,row]));
  for(const uid of new Set([...this.cache.entries.keys(),...this.cache.running.keys(),selectedUid].filter(Boolean))){const row=this.index.entries.get(uid);if(row)rows.set(uid,row);}
  metrics.record('plannerCandidates',rows.size);metrics.record('plannerNodes',query.visited);
  const candidates=[],warm=[],limits=this.limits,visibleUids=new Set();
  for(const {entry,box} of rows.values()){
   const uid=entry.uid,resident=this.cache.entries.has(uid),running=this.cache.running.has(uid),selected=selectedUid===uid,visible=this.frustum.intersectsBox(box),distance=box.distanceToPoint(this.eye);
   if(this.stream.infrastructureBuildingUids?.has(uid))continue;
   const building=this.stream.getLoadedBuilding(uid);if(!building||building.modelGeometry&&!this.stream.detailedModels.has(uid)&&!resident)continue;
   const collision=resident&&collisionPosition&&box.distanceToPoint(collisionPosition)<=60;
   const projected=visible?projectedBounds(box,this.matrix,viewportWidth,viewportHeight).pixels:0;
   if(visible)visibleUids.add(uid);
   const threshold=limits.minPixels*(resident?.65:1),useful=visible&&projected>=threshold;
   let keepVisible=false;
   if(resident&&visible&&!useful){if(!this.smallSince.has(uid))this.smallSince.set(uid,now);const deadline=this.smallSince.get(uid)+2000;keepVisible=now<deadline;if(keepVisible)this.nextCheck=Math.min(this.nextCheck,deadline);}else this.smallSince.delete(uid);
   if(selected||collision||useful||keepVisible){
    if(!allowNewLoads&&!resident&&!running&&!selected)continue;
    this.lastUseful.set(uid,now);candidates.push({entry,selected,collision,projected,resident,visible,distance});
   }else if(resident||running){
    if(!this.lastUseful.has(uid))this.lastUseful.set(uid,now);
    const deadline=this.lastUseful.get(uid)+(running?Math.min(1500,this.warmMs):this.warmMs);
    if(now<deadline){warm.push({entry,selected:false,collision:false,projected,resident,visible,distance});this.nextCheck=Math.min(this.nextCheck,deadline);}
   }
  }
  candidates.sort((a,b)=>Number(b.selected)-Number(a.selected)||Number(b.collision)-Number(a.collision)||Number(b.resident)-Number(a.resident)||b.projected-a.projected||a.distance-b.distance);
  warm.sort((a,b)=>(this.lastUseful.get(b.entry.uid)||0)-(this.lastUseful.get(a.entry.uid)||0));
  const support=(uid,kind,d)=>this.supportAvailable(uid,kind,d),draw=supportedModelPlan(candidates.map(c=>c.entry.uid),this.models,limits,modelBudget,support,selectedUid);
  const {wanted,blocked}=supportedModelPlan([...draw.wanted,...warm.map(c=>c.entry.uid)],this.models,limits,modelBudget,support,selectedUid);this.supportHolds=blocked;this.drawWanted=new Set(draw.wanted);
  const keep=new Set(wanted);
  for(const [uid,entry] of [...this.cache.entries].reverse()){
   if(!keep.has(uid)){this.cache.entries.delete(uid);this.lastUseful.delete(uid);this.smallSince.delete(uid);this.release(entry).catch(()=>{});continue;}
   // Offscreen detail remains decoded (and collision-ready) without drawing.
   // In-view tiny detail restores its basic form atomically before detaching.
   const supportsActive=[...this.stream.detailedModels.values()].some(d=>d!==entry&&d.active&&modelSupportDependencies(d.entry).some(dep=>dep.kind==='native'&&dep.uid===uid));
   const wantsDetail=this.drawWanted.has(uid)||visibleUids.has(uid)&&supportsActive;
   // Never hide an in-view active shell until its fallback commit has completed.
   entry.streamingInView=visibleUids.has(uid);entry.streamingVisible=wantsDetail||entry.active;
   // Three.js culls offscreen meshes every render; avoid a 180 ms hidden-shell
   // gap when the camera reverses between planner ticks.
   if(!this.activating.has(uid)&&((!wantsDetail&&visibleUids.has(uid)&&entry.active)||(wantsDetail&&!entry.active))){
    const controller=new AbortController(),signal=controller.signal;this.activeControllers.set(uid,controller);
    const work=(async()=>{
     if(wantsDetail)await this.waitForSupports(this.models.get(uid),signal);
     await this.change(async()=>{
      if(this.closed||signal.aborted||this.cache.entries.get(uid)!==entry||this.retiring.has(entry))return;
      if(wantsDetail!==this.drawWanted.has(uid))return;
      await this.stream.setDetailedModel(uid,wantsDetail?entry:null,{signal});
      if(!signal.aborted){entry.streamingVisible=wantsDetail;this.stream.sync?.();}
     },signal);
    })().catch(error=>{if(!signal.aborted){this.cache.errors.set(uid,error);entry.streamingVisible=true;}}).finally(()=>{this.activating.delete(uid);this.activeControllers.delete(uid);this.dirty=true;this.cache.notify();});this.activating.set(uid,work);
   }

  }
  this.stream.sync?.();
  if(wanted.join('|')!==this.cache.wanted.join('|'))this.cache.plan(wanted);
  metrics.end('modelPlannerMs',planStart);return wanted;
 }
 async retry(){
  await Promise.allSettled([...this.releaseFailures.keys()].map(entry=>this.release(entry)));
  await Promise.all([...this.catalogueErrors.keys()].map(url=>this.loadCatalogue(url)));this.cache.retry();
  if(this.lastCamera)this.plan(this.lastCamera,{...this.lastOptions,force:true});
 }
 setLoadingPaused(paused){this.cache.setPaused(paused);}
 get stats(){
  const entries=[...this.cache.entries.values()],held=[...new Set([...entries,...this.retiring.keys(),...this.releaseFailures.keys()])],cost=held.reduce((sum,e)=>({geometryBytes:sum.geometryBytes+e.budget.geometryBytes,residentBytes:sum.residentBytes+e.budget.residentBytes,triangles:sum.triangles+e.budget.triangles}),{geometryBytes:0,residentBytes:0,triangles:0});
  return {profile:this.profile,catalogues:this.catalogues.size,available:this.models.size,cached:entries.length,visible:entries.filter(e=>e.group.visible).length,pending:this.cache.running.size+this.requests.size,loadingPaused:this.cache.paused,retiring:this.retiring.size,wanted:this.cache.wanted.length,supportHolds:[...this.supportHolds].map(([uid,reason])=>({uid,reason})),errors:[...this.catalogueErrors.keys(),...this.cache.errors.keys(),...this.releaseFailures.keys()].map(value=>typeof value==='string'?value:'restore:'+value.record.uid),...cost,limits:this.limits,warm:entries.filter(e=>!this.drawWanted.has(e.record.uid)).length,compressed:this.byteCache.stats,drawCalls:entries.reduce((n,e)=>n+(e.group.visible?(e.budget.drawCalls??e.meshes?.length??1):0),0)};
 }
 async dispose(){
  if(this.closed)return;this.closed=true;for(const controller of this.activeControllers.values())controller.abort();for(const {controller} of this.requests.values())controller.abort();this.cache.close();this.byteCache.close();await Promise.allSettled([...this.retiring.values()]);this.models.clear();this.catalogues.clear();this.catalogueErrors.clear();
 }
}
