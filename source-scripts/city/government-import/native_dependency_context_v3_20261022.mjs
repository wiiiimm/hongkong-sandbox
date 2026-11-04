import assert from 'node:assert/strict';
import {verifyDependencyContext} from './native_dependency_context_v1.mjs';
export function verifyCurrentInstalledDependency(owner,dependency,support,form,standard,binding){
 if(dependency.state!=='candidate'&&(dependency.state!=='installed'||typeof dependency.csuid==='string'))return verifyDependencyContext(owner.uid,dependency,support,form,standard);
 assert(binding&&binding.owner===owner.uid&&binding.ownerSHA256===owner.sha256,'Exact owner binding required');
 assert.deepEqual(binding.rawDependency,dependency,'Original dependency metadata changed');
 assert(binding.reviewState==='installed-verified'&&typeof binding.snapshotId==='string','Installed ledger proof required');
 assert(binding.uid===dependency.uid&&(!dependency.sha256||binding.sourceSHA256===dependency.sha256)&&binding.sourceSHA256===support?.sha256,'Installed dependency bytes changed');
 assert(binding.csuid===support.buildingCSUID&&binding.csuid===form?.buildingCSUID,'Installed dependency identity changed');
 const result=verifyDependencyContext(owner.uid,{...dependency,state:'installed',csuid:binding.csuid},support,form,standard);
 return {...result,rawDependencyState:dependency.state,installedSnapshotId:binding.snapshotId};
}
