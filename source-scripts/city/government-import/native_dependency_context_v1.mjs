import assert from'node:assert/strict';
import{modelSupportDependencies}from'../../../3d-viewer/city/model-support.js';
export function verifyDependencyContext(owner,dependency,support,form,standard){
 const d=modelSupportDependencies({uid:owner,supportDependencies:[dependency]})[0];
 assert(form?.uid===d.uid&&typeof d.csuid==='string'&&form.buildingCSUID===d.csuid,'Pinned dependency source form unavailable');
 if(d.kind==='native'){
  assert(d.state==='installed'&&support?.uid===d.uid&&support.buildingCSUID===d.csuid,'Pinned installed native dependency unavailable');
  assert(!d.sha256||d.sha256===support.sha256,'Pinned dependency source hash changed');
  return{...d,physicalSupportCredit:false};
 }
 assert(!support&&!form.modelGeometry,'Surveyed fallback replaced by detailed geometry');
 assert(standard?.uid===d.uid&&standard.existingNative===false&&Array.isArray(standard.reasons)&&!standard.reasons.length,'Surveyed fallback regression unresolved');
 return{...d,basicBeforeAfterRegressionPassed:true,physicalSupportCredit:false};
}
