/** Resolve only an existing recorded edge to independently pinned current originals. */
import assert from 'node:assert/strict';
export function resolveRecordedCurrentDependency(owner,dependency,support,binding){
 assert(owner&&support&&binding);
 assert.equal(owner.uid,binding.ownerUID);assert.equal(dependency.uid,binding.supportUID);assert.equal(support.uid,binding.supportUID);
 assert.deepEqual(dependency,binding.originalRecordedDependency);
 assert.equal(dependency.state,'candidate');assert.equal(binding.currentSupportIsUniquelyInstalled,true);
 for(const [entry,pin] of [[owner,binding.owner],[support,binding.support]]){
  assert.equal(entry.sha256,pin.sourceSHA256);assert.match(pin.sourceSHA256,/^[0-9a-f]{64}$/);
  assert.equal(entry.buildingCSUID,pin.buildingCSUID);assert.equal(entry.modelId,pin.modelId);
  assert(pin.buildingCSUID&&pin.modelId&&pin.catalogue?.path&&/^[0-9a-f]{64}$/.test(pin.catalogue.sha256));
 }
 if(dependency.csuid!==undefined)assert.equal(dependency.csuid,support.buildingCSUID);
 return {uid:support.uid,state:'installed',csuid:support.buildingCSUID,originalRecordedDependency:dependency,currentSourceBinding:binding,qualification:'Current exact installed lookup of the existing recorded edge only; full original geometric support remains mandatory.',supportAccepted:false};
}
