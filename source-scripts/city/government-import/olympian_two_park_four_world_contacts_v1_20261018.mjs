import{readFileSync,writeFileSync}from'node:fs';import{gunzipSync,gzipSync}from'node:zlib';import{verifySupportInterface}from'./support-interface.mjs';import{supportSurface}from'./support-contact.mjs';
const dir=process.argv[2],input=JSON.parse(gunzipSync(readFileSync(dir+'/inputs.json.gz'))),rows=[];
const geometry=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)});
for(const[mode,w]of Object.entries(input.worlds)){
 const supports=input.supportUIDs.map(uid=>({uid,surface:supportSurface(geometry(w[uid]))})),combined=geometry(input.supportUIDs.flatMap(uid=>w[uid]));
 for(const uid of input.targetUIDs){const g=geometry(w[uid]),bottom=Math.min(...w[uid].flat().map(p=>p[1])),proof=verifySupportInterface(g,bottom,combined),details=[];
  for(const failure of proof.unresolved){const p=failure.position,contacts=[];
   for(const support of supports)for(const hit of support.surface.intersectionDetails(p[0],p[2])){const gap=p[1]-hit.height;if(gap>=-.1&&gap<=1)contacts.push({supportUid:support.uid,...hit,gap});}
   let path=null;if(!contacts.length){const old=input.paths.find(x=>x.uid===uid&&Math.hypot(...x.position.map((v,k)=>v-p[k]))<=.001);if(old){const end=old.witness.contact.point,heights=supports.flatMap(x=>x.surface.intersectionDetails(end[0],end[2]).map(h=>h.height)),h=heights.length?Math.max(...heights):null;path={original:old,endpointGap:h===null?null:end[1]-h,endpointPassed:h!==null&&end[1]-h>=-.1&&end[1]-h<=1};}}
   details.push({position:p,reason:failure.reason,contacts,path});
  }
  rows.push({uid,mode,proof,details});console.log(JSON.stringify({uid,mode,samples:proof.samples,strict:proof.strictContacts,lowerContacts:details.filter(x=>x.contacts.length).length,paths:details.filter(x=>x.path?.endpointPassed).length,unresolved:details.filter(x=>!x.contacts.length&&!x.path?.endpointPassed).length}));
 }
}
writeFileSync(dir+'/contacts.json.gz',gzipSync(JSON.stringify({rows,fullAcceptance:false})));
