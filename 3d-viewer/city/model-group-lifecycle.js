import {activationGroupMembers} from './model-activation-groups.js';
import {modelSupportDependencies} from './model-support.js';
import {modelBudget,disposeOfficialModel} from './official-model-assets.js?v=20261011-model-quality1';
const aborted=()=>new DOMException('Aborted','AbortError');
const sum=costs=>[...costs].reduce((a,b)=>{for(const k of ['geometryBytes','residentBytes','triangles','drawCalls'])a[k]+=(b[k]??(k==='drawCalls'?1:0));return a;},{geometryBytes:0,residentBytes:0,triangles:0,drawCalls:0});

/** One decode flight and one scene/cache commit for a reviewed source family. */
export class AtomicModelGroups{
 constructor(layer,BudgetDeferred){this.layer=layer;this.BudgetDeferred=BudgetDeferred;this.flights=new Map();this.retirements=new Map();this.reservations=new Map();}
 reservedCosts(except){return [...this.reservations].filter(([key])=>key!==except).map(([,costs])=>sum(costs.values()));}
 members(entry){return activationGroupMembers(entry);}
 // The stream transaction requires suppressed BASIC sources explicitly too.
 // They are affected fallback records, not additional native group members.
 changesWithBasicSuppressions(replacements){
  const l=this.layer,changes=new Map(replacements);
  for(const [uid,detail] of replacements)for(const item of [detail,l.stream.detailedModels.get(uid)]){
   for(const other of item?.entry?.suppressesBuildingUids||[]){
    if(changes.has(other))continue;
    if(l.stream.detailedModels.has(other))throw new Error('Suppressed detailed source requires explicit group replacement: '+other);
    if(detail?.entry?.suppressesBuildingUids?.includes(other)){
     const building=l.stream.getLoadedBuilding(other);
     if(!building||building.modelGeometry)throw new Error('Suppressed BASIC source unavailable: '+other);
    }
    changes.set(other,null);
   }
  }
  return [...changes];
 }
 async load(uid,signal){
  const l=this.layer,members=this.members(l.models.get(uid)),key=members.join('|');
  const retirement=this.retirements.get(key);if(retirement)await retirement;
  if(signal.aborted||l.closed)throw aborted();
  const flight=this.flights.get(key);
  if(flight){
   if(flight.epoch===l.qualityEpoch){const entries=await flight.promise;if(signal.aborted)throw aborted();return entries.get(uid);}
   await flight.promise.catch(()=>{});return this.load(uid,signal);
  }
  if(members.every(id=>l.cache.entries.has(id)&&l.stream.detailedModels.get(id)===l.cache.entries.get(id)&&l.cache.entries.get(id).active&&l.cache.entries.get(id).entry.variantId===l.selectedAsset(id)?.variantId))return l.cache.entries.get(uid);
  const state={epoch:l.qualityEpoch,controller:new AbortController()};
  const cancel=()=>state.controller.abort();signal.addEventListener('abort',cancel,{once:true});if(signal.aborted)cancel();
  state.promise=this.run(members,key,state).finally(()=>{signal.removeEventListener('abort',cancel);if(this.flights.get(key)===state)this.flights.delete(key);});
  this.flights.set(key,state);
  const entries=await state.promise;if(signal.aborted)throw aborted();return entries.get(uid);
 }
 async run(members,key,state){
  const l=this.layer,signal=state.controller.signal,inside=new Set(members),decoded=new Map(),previous=new Map(members.map(uid=>[uid,l.cache.entries.get(uid)]));
  const budgetUid=inside.has(l.lastOptions?.selectedUid)?l.lastOptions.selectedUid:members[0];
  const current=()=>{
   if(signal.aborted||l.closed||state.epoch!==l.qualityEpoch||members.some(uid=>!l.cache.wanted.includes(uid)||this.members(l.models.get(uid)).join('|')!==key))throw aborted();
  };
  const costs=new Map(members.map(uid=>[uid,modelBudget(l.candidateAsset(l.models.get(uid),uid))]));
  const check=(draw=true)=>{
   current();if(l.releaseFailures.size)throw new Error('Previous model fallback restoration needs Retry');
   if(l.cache.entries.size+members.filter(uid=>!l.cache.entries.has(uid)).length>l.limits.count||!l.canAdmit(budgetUid,sum(costs.values()),{checkDrawCalls:draw,excludeGroupKey:key}))throw new this.BudgetDeferred('Atomic source group exceeds peak device budget');
  };
  const register=()=>{
   for(const [uid,entry]of decoded){l.cache.entries.set(uid,entry);l.cache.reloads.delete(uid);l.cache.errors.delete(uid);}
   for(const [uid,old]of previous)if(old&&old!==decoded.get(uid)&&l.stream.detailedModels.get(uid)!==old)disposeOfficialModel(old);
  };
  let switched=false,registered=false;
  try{
   current();
   if(typeof l.stream.setDetailedModels!=='function')throw new Error('Atomic source group replacement is unavailable');
   for(const uid of members)await l.waitForSupports(l.models.get(uid),signal,inside);
   check(false);this.reservations.set(key,costs);
   for(const uid of members){
    const source=l.models.get(uid),building=l.stream.getLoadedBuilding(uid);if(!building)throw aborted();
    const selected=l.candidateAsset(source,uid),candidates=selected===source?[source]:[selected,source];
    for(const candidate of candidates){
     l.loadingAssets.set(uid,candidate);costs.set(uid,modelBudget(candidate));check(false);
     try{
      const entry=await l.loadAsset(candidate,building,l.stream.lighting,{signal,byteCache:l.byteCache,beforeDecode:async decodeSignal=>{check(false);return l.readyForWork(decodeSignal);},getBuilding:id=>l.stream.getLoadedBuilding(id)});
      decoded.set(uid,entry);if(!entry?.budget)throw new Error('Decoded group member has no budget');costs.set(uid,entry.budget);check(false);
      entry.record.modelSource??={};Object.assign(entry.record.modelSource,{variantId:candidate.variantId??null,codec:candidate.codec??'none',tier:candidate.tier??'original',sourceSha256:candidate.sourceSha256??source.sha256,sourceMetadataSha256:candidate.sourceMetadataSha256??null});
      l.drawCosts.set(uid,entry.budget.drawCalls??entry.meshes?.length??1);break;
     }catch(error){
      const entry=decoded.get(uid);if(entry){disposeOfficialModel(entry);decoded.delete(uid);}
      if(error?.name==='AbortError'||error instanceof this.BudgetDeferred||!candidate.variantId)throw error;
      l.failedVariants.set(candidate.variantId,error.message);l.selectedAssets.set(uid,source);
     }
    }
    l.loadingAssets.delete(uid);
   }
   current();for(const uid of members)await l.waitForSupports(l.models.get(uid),signal,inside);
   await l.reserveDrawCalls({budget:sum(costs.values())});check(true);
   if(members.some(uid=>l.stream.infrastructureBuildingUids?.has(uid)))throw new Error('Official infrastructure already replaces a group member');
   switched=await l.change(()=>{check(true);return l.stream.setDetailedModels(this.changesWithBasicSuppressions([...decoded]),{signal});},signal);
   if(!switched)throw aborted();current();
   register();registered=true;for(const entry of decoded.values())l.onReveal(entry);return decoded;
  }catch(error){
   if(registered){for(const uid of members)l.cache.errors.set(uid,error);throw error;}
   // The scene API commits all members together. A late cancellation therefore
   // restores the complete prior family, or keeps a complete family on failure.
   if(switched||members.some(uid=>l.stream.detailedModels.get(uid)===decoded.get(uid)&&decoded.has(uid))){
    try{
     const restore=members.map(uid=>[uid,previous.get(uid)?.active&&l.quality!=='base'&&l.cache.wanted.includes(uid)?previous.get(uid):null]);
     const ok=await l.change(()=>l.stream.setDetailedModels(this.changesWithBasicSuppressions(restore)));if(!ok)throw new Error('Atomic source group fallback was deferred');
    }catch(restoreError){register();for(const entry of decoded.values())l.releaseFailures.set(entry,restoreError.message);}
   }
   for(const [uid,entry]of decoded)if(l.stream.detailedModels.get(uid)!==entry)disposeOfficialModel(entry);
   if(!signal.aborted&&!l.closed&&error?.name!=='AbortError')for(const uid of members)l.cache.errors.set(uid,error);
   throw error;
  }finally{this.reservations.delete(key);for(const uid of members)l.loadingAssets.delete(uid);}
 }
 release(entry){
  const l=this.layer,members=this.members(entry.entry||l.models.get(entry.record.uid)),key=members.join('|');
  if(this.retirements.has(key))return this.retirements.get(key);
  if(!members.some(uid=>l.stream.detailedModels.get(uid)===entry||l.cache.entries.get(uid)===entry)){disposeOfficialModel(entry);return Promise.resolve();}
  this.flights.get(key)?.controller.abort();
  const entries=new Map();
  for(const uid of members){
   l.activeControllers.get(uid)?.abort();const value=l.stream.detailedModels.get(uid)||l.cache.entries.get(uid);if(value)entries.set(uid,value);l.cache.entries.delete(uid);
  }
  l.cache.wanted=l.cache.wanted.filter(uid=>!members.includes(uid));
  const work=(async()=>{
   await this.flights.get(key)?.promise.catch(()=>{});
   await Promise.all(members.map(uid=>l.activating.get(uid)?.catch(()=>{})));
   const dependents=[...l.stream.detailedModels.values()].filter(value=>!members.includes(value.record.uid)&&modelSupportDependencies(value.entry).some(d=>d.kind==='native'&&members.includes(d.uid)));
   for(const dependent of dependents){l.cache.entries.delete(dependent.record.uid);await l.release(dependent);}
   const changes=members.map(uid=>[uid,null]);
   if(members.some(uid=>l.stream.detailedModels.has(uid))){const ok=await l.change(()=>l.stream.setDetailedModels(this.changesWithBasicSuppressions(changes)));if(!ok)throw new Error('Atomic source group fallback was deferred');}
   for(const value of entries.values()){disposeOfficialModel(value);l.releaseFailures.delete(value);}
  })().catch(error=>{for(const value of entries.values())l.releaseFailures.set(value,error.message);throw error;}).finally(()=>{
   this.retirements.delete(key);for(const value of entries.values())l.retiring.delete(value);l.dirty=true;if(!l.closed)l.onChange();
  });
  this.retirements.set(key,work);for(const value of entries.values())l.retiring.set(value,work);return work;
 }
 planVisibility(visibleUids){
  const l=this.layer,seen=new Set();
  for(const entry of l.cache.entries.values()){
   const members=this.members(entry.entry),key=members.join('|');if(members.length<2||seen.has(key))continue;seen.add(key);
   const values=members.map(uid=>l.cache.entries.get(uid));if(values.some(v=>!v)||this.retirements.has(key))continue;
   const visible=members.some(uid=>visibleUids.has(uid));
   const wants=()=>members.some(uid=>l.drawWanted.has(uid))||visible&&[...l.stream.detailedModels.values()].some(d=>d.active&&!members.includes(d.record.uid)&&modelSupportDependencies(d.entry).some(dep=>dep.kind==='native'&&members.includes(dep.uid)));
   const wanted=wants();
   for(const value of values){value.streamingInView=visibleUids.has(value.record.uid);value.streamingVisible=wanted||value.active;}
   if(members.some(uid=>l.activating.has(uid))||!((wanted&&values.some(v=>!v.active))||(!wanted&&visible&&values.some(v=>v.active))))continue;
   const controller=new AbortController(),signal=controller.signal;
   const work=(async()=>{
    if(wanted)for(const uid of members)await l.waitForSupports(l.models.get(uid),signal,new Set(members));
    await l.change(async()=>{
     if(signal.aborted||l.closed||members.some((uid,i)=>l.cache.entries.get(uid)!==values[i])||wanted!==wants())return;
     const ok=await l.stream.setDetailedModels(this.changesWithBasicSuppressions(members.map((uid,i)=>[uid,wanted?values[i]:null])),{signal});if(!ok)throw aborted();
     for(const value of values)value.streamingVisible=wanted;
    },signal);
   })().catch(error=>{if(!signal.aborted&&error?.name!=='AbortError')for(const uid of members)l.cache.errors.set(uid,error);}).finally(()=>{
    for(const uid of members){if(l.activating.get(uid)===work)l.activating.delete(uid);if(l.activeControllers.get(uid)===controller)l.activeControllers.delete(uid);}
    l.dirty=true;l.cache.notify();
   });
   for(const uid of members){l.activating.set(uid,work);l.activeControllers.set(uid,controller);}
  }
 }
}
