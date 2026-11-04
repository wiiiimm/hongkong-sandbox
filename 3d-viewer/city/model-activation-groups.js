// Availability is distinct from physical support. Every member shares one switch.
const UID=/^landsd\/[1-9]\d*:(?:0|[1-9]\d*)$/;
export function activationGroupMembers(entry){
 const value=entry?.activationGroup;
 if(value===undefined)return [entry?.uid];
 if(!Array.isArray(value)||value.length<2||value.length>64||value.some(uid=>!UID.test(uid))||new Set(value).size!==value.length||!value.includes(entry.uid))throw new Error('Invalid model activation group: '+entry?.uid);
 return [...value].sort();
}
/** Dependency-ordered closure, with cycles checked before and after grouping. */
export function activationClosure(root,models,dependencies,available,limit){
 const ordered=[],completeGroups=new Set(),visitingGroups=new Set(),encountered=new Set(),fallbacks=new Set();
 const groupFor=uid=>{
  const entry=models.get(uid);if(!entry||!available(uid,'native'))throw new Error('Native model support unavailable: '+uid);
  const members=activationGroupMembers(entry),key=members.join('|');
  for(const member of members){
   const peer=models.get(member);if(!peer||!available(member,'native'))throw new Error('Native model support unavailable: '+member);
   if(activationGroupMembers(peer).join('|')!==key)throw new Error('Conflicting model activation groups: '+member);
  }
  return {members,key};
 };
 const visitGroup=uid=>{
  const {members,key}=groupFor(uid);
  if(completeGroups.has(key))return;
  if(visitingGroups.has(key))throw new Error('Cyclic native model support or activation group: '+uid);
  visitingGroups.add(key);
  for(const member of members)encountered.add(member);
  if(encountered.size>limit)throw new Error('Model support group exceeds count budget');
  const complete=new Set(),visiting=new Set(),local=[];
  const visitMember=member=>{
   if(complete.has(member))return;
   if(visiting.has(member))throw new Error('Cyclic native model support: '+member);
   visiting.add(member);
   for(const d of dependencies(models.get(member))){
    if(d.kind==='native'){
     if(groupFor(d.uid).key===key)visitMember(d.uid);else visitGroup(d.uid);
    }else{
     if(!available(d.uid,'fallback',d))throw new Error('Surveyed model support unavailable: '+d.uid);
     fallbacks.add(d.uid);
    }
   }
   visiting.delete(member);complete.add(member);local.push(member);
  };
  for(const member of members)visitMember(member);
  ordered.push(...local);visitingGroups.delete(key);completeGroups.add(key);
 };
 visitGroup(root);
 return {ordered,fallbacks};
}
