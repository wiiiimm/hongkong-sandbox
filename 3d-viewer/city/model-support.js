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
 const used={geometryBytes:0,residentBytes:0,triangles:0};
 for(const root of candidates){
  const ordered=[],complete=new Set(),visiting=new Set(),fallbacks=new Set();
  try{
   const visit=uid=>{
    if(complete.has(uid))return;
    if(visiting.has(uid))throw new Error('Cyclic native model support: '+uid);
    const entry=models.get(uid);if(!entry||!available(uid,'native'))throw new Error('Native model support unavailable: '+uid);
    visiting.add(uid);
    if(visiting.size+complete.size>limits.count)throw new Error('Model support group exceeds count budget');
    for(const d of modelSupportDependencies(entry)){
     if(d.kind==='native')visit(d.uid);
     else{if(!available(d.uid,'fallback',d))throw new Error('Surveyed model support unavailable: '+d.uid);fallbacks.add(d.uid);}
    }
    visiting.delete(uid);complete.add(uid);ordered.push(uid);
   };
   visit(root);
   if(ordered.some(uid=>fallbacks.has(uid)||reservedFallbacks.has(uid))||[...fallbacks].some(uid=>chosen.has(uid)))throw new Error('Native upgrade conflicts with required surveyed support');
   const extra=ordered.filter(uid=>!chosen.has(uid)),cost={geometryBytes:0,residentBytes:0,triangles:0};
   for(const uid of extra){const c=budget(models.get(uid));for(const k of Object.keys(cost))cost[k]+=c[k];}
   if(wanted.length+extra.length>limits.count||Object.keys(cost).some(k=>used[k]+cost[k]>(k==='residentBytes'&&root===selectedUid?limits.selectedResidentBytes??limits[k]:limits[k])))throw new Error('Model support group exceeds memory or triangle budget');
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
  for(const dependency of modelSupportDependencies(detail.entry))if(dependency.kind==='native'){
   const support=details.get(dependency.uid);if(!support?.active)continue;
   support.group.visible=true;for(const mesh of support.meshes||[])mesh.castShadow ||= detail.meshes?.some(m=>m.castShadow)??true;queue.push(support);
  }
 }
}
