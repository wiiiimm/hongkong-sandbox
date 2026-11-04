/** Exact current surveyed fallback binding for legacy UID-only catalogue rows. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {verifyCurrentInstalledDependency as previous} from './native_dependency_context_v3_20261022.mjs';
import {verifyDependencyContext} from './native_dependency_context_v1.mjs';

export function verifyBoundSurveyedFallback(owner,dependency,support,form,standard,binding,tile){
 assert(['fallback','surveyed-footprint-fallback'].includes(dependency.state));
 assert(!dependency.csuid,'Already pinned fallback must use its original verifier');
 assert(binding?.kind==='exact-current-surveyed-fallback');
 assert(binding.owner===owner.uid&&binding.ownerSHA256===owner.sha256);
 assert(binding.ownerReviewState==='installed-verified'&&typeof binding.snapshotId==='string'&&binding.snapshotId.length>0);
 assert.deepEqual(binding.rawDependency,dependency,'Original fallback metadata changed');
 assert(binding.uid===dependency.uid&&typeof binding.csuid==='string'&&binding.csuid.length>0);
 assert(!support&&!form?.modelGeometry,'Fallback must remain BASIC');
 assert.deepEqual(binding.sourceForm,form,'Bound fallback source form changed');
 const matches=tile.buildings.filter(b=>b.uid===dependency.uid);
 assert.equal(matches.length,1,'Fallback source must be unique');
 assert.deepEqual(matches[0],form,'Actual current tile differs from proposed form');
 assert.equal(form.buildingCSUID,binding.csuid);
 return {...verifyDependencyContext(owner.uid,{...dependency,csuid:binding.csuid},support,form,standard),
  rawDependencyState:dependency.state,exactCurrentSourceBinding:true};
}

export function verifyCurrentInstalledDependency(owner,dependency,support,form,standard,binding){
 if(!['fallback','surveyed-footprint-fallback'].includes(dependency.state)||dependency.csuid)
  return previous(owner,dependency,support,form,standard,binding);
 assert(binding?.sourceTile&&/^3d-viewer\/city\/data\/tiles\/[^/]+\.json$/.test(binding.sourceTile.path));
 const raw=readFileSync(new URL('../../../'+binding.sourceTile.path,import.meta.url));
 assert.equal(createHash('sha256').update(raw).digest('hex'),binding.sourceTile.sha256,'Fallback source tile changed');
 return verifyBoundSurveyedFallback(owner,dependency,support,form,standard,binding,JSON.parse(raw));
}
