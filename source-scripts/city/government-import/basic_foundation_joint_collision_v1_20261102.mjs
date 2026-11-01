/** Complete scoped BASIC collision replay with all proposed foundations active.
 * Production BuildingIndex, roofs and original parts remain authoritative.
 * This is finite probe evidence, not native/joint-scene or visual approval.
 */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {BuildingIndex,inPolygon} from '../../../3d-viewer/city/geo.js';
import {collisionVolumes} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3],sha=b=>createHash('sha256').update(b).digest('hex');
const bytes=readFileSync(new URL(inputPath,root)),input=JSON.parse(bytes),pins={...input.inputHashes,[inputPath]:sha(bytes)};
for(const [p,h] of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const forms=input.currentForms;assert.equal(forms.length,input.expectedFormCount);assert.equal(new Set(forms.map(b=>b.uid)).size,forms.length);
const proposals=input.proposals;assert(proposals.length>0&&new Set(proposals.map(p=>p.uid)).size===proposals.length);
const changed=structuredClone(forms),extensions=[],rows=[];
for(const p of proposals){
 const before=forms.find(b=>b.uid===p.uid);assert(before);assert.deepEqual(before,p.building);
 assert(!before.modelGeometry&&before.foundationBase===undefined);assert.equal(before.baseSource,'terrain-estimated');assert.equal(before.heightSource,'estimated');assert.equal(before.baseHeightHKPD,null);assert.equal(before.topHeightHKPD,null);assert(Number.isFinite(p.foundationBase)&&p.foundationBase<before.base-.02);
 const after={...structuredClone(before),foundationBase:p.foundationBase};changed[changed.findIndex(b=>b.uid===p.uid)]=after;
 const a=collisionVolumes(before),b=collisionVolumes(after),own=[];
 if(before.structureType==='Open-sided Structure'){
  assert.equal(a.length,b.length);
  for(let i=0;i<a.length;i++)if(a[i].kind==='post'){
   assert.equal(b[i].bottom,p.foundationBase);assert.deepEqual({...b[i],bottom:a[i].bottom},a[i]);assert(b[i].bottom<a[i].bottom);own.push({uid:p.uid,volume:b[i],oldBottom:a[i].bottom});
  }else{assert.equal(a[i].kind,'roof');assert.deepEqual(a[i],b[i]);}
 }else{
  assert.equal(before.structureType,'Temporary Structure');assert.equal(a.length,1);assert.equal(a[0].kind,'building');assert.equal(b.length,2);assert.deepEqual(a[0],b[0]);
  const f=b[1];assert.equal(f.kind,'foundation');assert.equal(f.windows,false);assert.equal(f.bottom,p.foundationBase);assert.equal(f.top,before.base);assert.deepEqual(f.rings,before.rings);own.push({uid:p.uid,volume:f,oldBottom:f.top});
 }
 assert(own.length>0);extensions.push(...own);rows.push({uid:p.uid,extensionCount:own.length,originalVolumeCount:a.length,afterVolumeCount:b.length,probes:0,addedTargetCollisionProbes:0,addedGlobalCollisionProbes:0});
}
const allOld=new BuildingIndex(structuredClone(forms)),allNew=new BuildingIndex(changed),addedOnly=new BuildingIndex(proposals.map(p=>changed.find(b=>b.uid===p.uid)));
for(let i=0;i<forms.length;i++)if(!proposals.some(p=>p.uid===forms[i].uid))assert.deepEqual(allOld.volumes[i],allNew.volumes[i]);
for(const {uid,volume:v,oldBottom} of extensions){
 const row=rows.find(r=>r.uid===uid),before=forms.find(b=>b.uid===uid),after=changed.find(b=>b.uid===uid),old=new BuildingIndex([structuredClone(before)]),next=new BuildingIndex([structuredClone(after)]),[x0,z0,x1,z1]=v.bounds;
 for(const x of [x0-.1,x0,(x0+x1)/2,x1,x1+.1])for(const z of [z0-.1,z0,(z0+z1)/2,z1,z1+.1])for(const radius of [0,.55,2]){
  assert.equal(old.maximumRoof(x,z,radius),next.maximumRoof(x,z,radius));assert.equal(allOld.maximumRoof(x,z,radius),allNew.maximumRoof(x,z,radius));
  for(const bottom of [v.bottom-.02,v.bottom+.02,(v.bottom+oldBottom)/2,oldBottom-.02,oldBottom,oldBottom+.02,v.top+.02])for(const height of [.02,1.8]){
   const top=bottom+height,c=!!old.collision(x,z,bottom,top,radius),d=!!next.collision(x,z,bottom,top,radius),e=!!allOld.collision(x,z,bottom,top,radius),f=!!allNew.collision(x,z,bottom,top,radius);
   assert(!c||d,'Target collision removed');assert(!e||f,'Scoped collision removed');
   if(c!==d){assert(bottom<oldBottom&&top>v.bottom);if(radius===0)assert(extensions.some(q=>q.uid===uid&&inPolygon(x,z,q.volume.rings)));row.addedTargetCollisionProbes++;}
   if(e!==f){assert(!e&&f);assert(addedOnly.collision(x,z,bottom,top,radius),'Unattributed scoped collision change');row.addedGlobalCollisionProbes++;}
   row.probes++;
  }
 }
}
for(const row of rows)assert(row.addedTargetCollisionProbes>0);
assert(verifyModuleClosure(closure,root));for(const [p,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const report={uids:proposals.map(p=>p.uid),forms:forms.length,unchangedRegionalForms:forms.length-proposals.length,rows,probes:rows.reduce((s,r)=>s+r.probes,0),simultaneousBasicFoundationProbesPassed:true,originalPartsAndRoofPreserved:true,collisionReviewApproved:false,jointNativeSceneApproved:false,visualReviewApproved:false,installationApproved:false,productionChanges:0,inputHashes:{...pins,...closure.inputHashes},completeRecursiveProductionModuleClosure:closure,qualification:'All private BASIC foundation proposals are active simultaneously in the complete current BASIC scope. Existing production collision and roof probes are monotone; changes are attributed to the proposed forms. This is finite BASIC-only probe evidence, not native intersection, visual, source support or publication approval.'};
writeFileSync(new URL(outputPath,root),JSON.stringify(report));console.log(JSON.stringify({forms:forms.length,proposals:proposals.length,extensions:extensions.length,probes:report.probes}));
