import {activationClosure,activationGroupMembers} from './model-activation-groups.js';
// Support relationships are source metadata, not an alternative height system.
const UID=/^landsd\/[1-9]\d*:(?:0|[1-9]\d*)$/;
export function modelSupportDependencies(entry){
 const source=entry?.supportDependencies??[];
 if(!Array.isArray(source)||source.length>64)throw new Error('Invalid model support dependencies');
 const result=new Map();
 for(const value of source){
  // Early reviewed catalogues used strings for retained surveyed podiums.
  const item=typeof value==='string'?{uid:value,state:'fallback'}:value;
  if(!item||!UID.test(item.uid)||!['candidate','installed','fallback','surveyed-footprint-fallback'].includes(item.state))throw new Error('Invalid model support dependency for '+entry?.uid);
  const kind=['candidate','installed'].includes(item.state)?'native':'fallback';
  if(result.has(item.uid)&&result.get(item.uid).kind!==kind)throw new Error('Conflicting model support dependency '+item.uid);
  result.set(item.uid,{...item,kind});
 }
 return [...result.values()];
}
/** Dependency-first closure. Cycles and unavailable sources keep the original forms. */
export function supportedModelPlan(candidates,models,limits,budget,available,selectedUid=null){
 const wanted=[],chosen=new Set(),reservedFallbacks=new Set(),blocked=new Map();
 const used={geometryBytes:0,residentBytes:0,triangles:0,drawCalls:0};
 for(const root of candidates){
  try{
   const {ordered,fallbacks}=activationClosure(root,models,modelSupportDependencies,available,limits.count);
   if(ordered.some(uid=>fallbacks.has(uid)||reservedFallbacks.has(uid))||[...fallbacks].some(uid=>chosen.has(uid)))throw new Error('Native upgrade conflicts with required surveyed support');
   const extra=ordered.filter(uid=>!chosen.has(uid)),cost={geometryBytes:0,residentBytes:0,triangles:0,drawCalls:0};
   for(const uid of extra){const c=budget(models.get(uid));for(const k of Object.keys(cost))cost[k]+=c[k]??(k==='drawCalls'?1:0);}
   if(wanted.length+extra.length>limits.count||Object.keys(cost).some(k=>used[k]+cost[k]>(k==='residentBytes'&&root===selectedUid?limits.selectedResidentBytes??limits[k]:limits[k]??Infinity)))throw new Error('Model support group exceeds memory, triangle or draw-call budget');
   for(const uid of extra){chosen.add(uid);wanted.push(uid);}for(const uid of fallbacks)reservedFallbacks.add(uid);for(const k of Object.keys(cost))used[k]+=cost[k];
  }catch(error){blocked.set(root,error.message);}
 }
 return {wanted,blocked,used};
}
/** Native supports remain visible across a source-tile boundary with their tower. */
export function retainVisibleNativeSupports(details){
 const queue=[...details.values()].filter(d=>d.active&&(d.group.visible||[...(d.supportVisibilityDependents||[])].some(t=>t.active&&t.group.visible))),seen=new Set();
 for(const detail of queue)detail.group.visible=true;
 for(let i=0;i<queue.length;i++){
  const detail=queue[i];if(seen.has(detail))continue;seen.add(detail);
  const dependencies=[...modelSupportDependencies(detail.entry),...activationGroupMembers(detail.entry).filter(uid=>uid!==detail.entry?.uid).map(uid=>({uid,kind:'native'}))];
  for(const dependency of dependencies)if(dependency.kind==='native'){
   const support=details.get(dependency.uid);if(!support?.active)continue;
   support.group.visible=true;for(const mesh of support.meshes||[])mesh.castShadow ||= detail.meshes?.some(m=>m.castShadow)??true;queue.push(support);
  }
 }
}
