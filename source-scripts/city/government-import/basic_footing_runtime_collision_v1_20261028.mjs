/** Exercise production BASIC collision before/after one private footing. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {BuildingIndex,inPolygon} from '../../../3d-viewer/city/geo.js';
import {collisionVolumes} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3];
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const input=JSON.parse(readFileSync(new URL(inputPath,root)));
const pins={...input.inputHashes,[inputPath]:sha(readFileSync(new URL(inputPath,root)))};
for(const [p,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const before=structuredClone(input.building),after={...structuredClone(input.building),foundationBase:input.foundationBase};
assert.equal(before.structureType,'Podium');assert.equal(before.kind,'yes');assert.equal(before.minimum,0);
assert(!before.modelGeometry&&before.foundationBase===undefined);
const oldVolumes=collisionVolumes(before),newVolumes=collisionVolumes(after);
assert.equal(oldVolumes.length,1);assert.equal(newVolumes.length,2);
assert.deepEqual(newVolumes[0],oldVolumes[0]);
const added=newVolumes[1];
assert.equal(added.kind,'foundation');assert.equal(added.windows,false);assert.equal(added.illustrative,true);
assert.deepEqual(added.rings,before.rings);assert.deepEqual(added.bounds,oldVolumes[0].bounds);
assert.equal(added.bottom,input.foundationBase);assert.equal(added.top,before.base);
const old=new BuildingIndex([before]),next=new BuildingIndex([after]);
const forms=input.currentForms;assert.equal(forms.length,156);
assert.deepEqual(forms.find(b=>b.uid===before.uid),before);
const allOld=new BuildingIndex(structuredClone(forms));
const changed=structuredClone(forms);changed[changed.findIndex(b=>b.uid===before.uid)]=after;
const allNew=new BuildingIndex(changed);
for(let i=0;i<forms.length;i++)if(forms[i].uid!==before.uid)assert.deepEqual(allNew.volumes[i],allOld.volumes[i]);
const [x0,z0,x1,z1]=added.bounds;
const heights=[added.bottom-.02,added.bottom+.02,(added.bottom+added.top)/2,added.top-.02,added.top,added.top+.02,before.base+before.height+.02];
const report={uid:before.uid,probes:0,addedTargetCollisionProbes:0,addedGlobalCollisionProbes:0,unchangedRegionalForms:155,
 oldCollisionVolumesExactlyRetained:true,onlyAddedCollisionVolumeIsSameFootprintBelowBase:true,roofSamples:0,
 geometryChanges:0,governmentGeometryChanges:0,collisionReviewApproved:false,visualReviewApproved:false,installationApproved:false};
for(let xi=0;xi<=Math.ceil((x1-x0+4)/.25);xi++)for(let zi=0;zi<=Math.ceil((z1-z0+4)/.25);zi++){
 const x=x0-2+xi*.25,z=z0-2+zi*.25;
 for(const radius of [0,.55,2]){
  assert.equal(old.maximumRoof(x,z,radius),next.maximumRoof(x,z,radius));report.roofSamples++;
  for(const bottom of heights)for(const envelopeHeight of [.02,1.8]){
   const top=bottom+envelopeHeight,a=!!old.collision(x,z,bottom,top,radius),b=!!next.collision(x,z,bottom,top,radius);
   assert(!a||b,'Existing collision was removed');
   if(a!==b){
    assert(bottom<added.top&&top>added.bottom,'Collision changed outside intended vertical interval');
    if(radius===0)assert(inPolygon(x,z,added.rings),'Point collision changed outside unchanged footprint');
    report.addedTargetCollisionProbes++;
   }
   const c=!!allOld.collision(x,z,bottom,top,radius),d=!!allNew.collision(x,z,bottom,top,radius);
   assert(!c||d,'Regional collision was removed');
   if(c!==d){assert(!a&&b,'Regional change was not due solely to target footing');report.addedGlobalCollisionProbes++;}
   report.probes++;
  }
 }
}
assert(report.addedTargetCollisionProbes>0&&report.addedGlobalCollisionProbes>0);
assert(verifyModuleClosure(closure,root));
for(const [p,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
report.inputHashes={...pins,...closure.inputHashes};report.completeRecursiveProductionModuleClosure=closure;
report.qualification='Production BuildingIndex and collisionVolumes: exact old volume retained, one same-footprint illustrative volume below recorded base,155other BASIC volumes unchanged, roof queries unchanged over the stated grid, monotonic target/regional collision, and every sampled regional difference attributable only to the added target volume. Finite samples are not a universal movement/closed-solid proof. Native assembly and actual viewer/terrain acceptance remain separate.';
writeFileSync(new URL(outputPath,root),JSON.stringify(report));
console.log(JSON.stringify({probes:report.probes,addedTargetCollisionProbes:report.addedTargetCollisionProbes,addedGlobalCollisionProbes:report.addedGlobalCollisionProbes}));
