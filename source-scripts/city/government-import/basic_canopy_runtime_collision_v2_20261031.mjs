/** Verify existing production collision semantics for private canopy post extensions. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {BuildingIndex,inPolygon} from '../../../3d-viewer/city/geo.js';
import {collisionVolumes} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3],sha=b=>createHash('sha256').update(b).digest('hex');
const input=JSON.parse(readFileSync(new URL(inputPath,root))),pins={...input.inputHashes,[inputPath]:sha(readFileSync(new URL(inputPath,root)))};
for(const [p,h] of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const before=structuredClone(input.building),after={...structuredClone(before),foundationBase:input.foundationBase};
assert.equal(before.structureType,'Open-sided Structure');assert.equal(before.kind,'roof');assert(!before.modelGeometry&&before.foundationBase===undefined);assert(input.foundationBase<before.base-.02);
const oldVolumes=collisionVolumes(before),newVolumes=collisionVolumes(after);assert.equal(newVolumes.length,oldVolumes.length);
const posts=[];
for(let i=0;i<oldVolumes.length;i++){
 const a=oldVolumes[i],b=newVolumes[i];
 if(a.kind==='post'){assert.equal(b.bottom,input.foundationBase);assert.deepEqual({...b,bottom:a.bottom},a);assert(b.bottom<a.bottom);posts.push({before:a,after:b});}
 else{assert.equal(a.kind,'roof');assert.deepEqual(b,a);}
}
assert(posts.length>0);
const forms=input.currentForms;assert(Number.isInteger(input.expectedFormCount)&&input.expectedFormCount>0);assert.equal(forms.length,input.expectedFormCount);assert.deepEqual(forms.find(b=>b.uid===before.uid),before);
const changed=structuredClone(forms);changed[changed.findIndex(b=>b.uid===before.uid)]=after;
const old=new BuildingIndex([before]),next=new BuildingIndex([after]),allOld=new BuildingIndex(structuredClone(forms)),allNew=new BuildingIndex(changed);
for(let i=0;i<forms.length;i++)if(forms[i].uid!==before.uid)assert.deepEqual(allNew.volumes[i],allOld.volumes[i]);
const report={uid:before.uid,postCount:posts.length,probes:0,roofSamples:0,addedTargetCollisionProbes:0,addedGlobalCollisionProbes:0,unchangedRegionalForms:forms.length-1,allRoofPartsExactlyRetained:true,onlyPostBottomsChanged:true,allPostFootprintsAndTopsExactlyRetained:true,collisionReviewApproved:false,visualReviewApproved:false,installationApproved:false};
for(const {before:a,after:b} of posts){
 const [x0,z0,x1,z1]=b.bounds;
 for(const x of [x0-.1,x0,(x0+x1)/2,x1,x1+.1])for(const z of [z0-.1,z0,(z0+z1)/2,z1,z1+.1])for(const radius of [0,.55,2]){
  assert.equal(old.maximumRoof(x,z,radius),next.maximumRoof(x,z,radius));report.roofSamples++;
  for(const bottom of [b.bottom-.02,b.bottom+.02,(b.bottom+a.bottom)/2,a.bottom-.02,a.bottom,a.bottom+.02,a.top+.02])for(const height of [.02,1.8]){
   const top=bottom+height,c=!!old.collision(x,z,bottom,top,radius),d=!!next.collision(x,z,bottom,top,radius);assert(!c||d,'Existing collision removed');
   if(c!==d){assert(bottom<a.bottom&&top>b.bottom,'Collision changed outside post extension');if(radius===0)assert(posts.some(p=>inPolygon(x,z,p.after.rings)));report.addedTargetCollisionProbes++;}
   const e=!!allOld.collision(x,z,bottom,top,radius),f=!!allNew.collision(x,z,bottom,top,radius);assert(!e||f,'Regional collision removed');if(e!==f){assert(!c&&d);report.addedGlobalCollisionProbes++;}report.probes++;
  }
 }
}
assert(report.addedTargetCollisionProbes>0);assert(verifyModuleClosure(closure,root));for(const [p,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
report.inputHashes={...pins,...closure.inputHashes};report.completeRecursiveProductionModuleClosure=closure;
report.qualification='Production collision parts preserve every roof, post footprint/top and all other scoped BASIC volumes exactly; only post bottoms extend down to the proposal. Finite actual BuildingIndex probes verify monotonic collision and attribute sampled regional differences to these extensions. Zero regional differences is allowed when existing volumes already block them. This does not prove absence of native intersections or approve scene/visual/support/installation.';
writeFileSync(new URL(outputPath,root),JSON.stringify(report));console.log(JSON.stringify({uid:report.uid,posts:posts.length,probes:report.probes,addedTargetCollisionProbes:report.addedTargetCollisionProbes,addedGlobalCollisionProbes:report.addedGlobalCollisionProbes}));
