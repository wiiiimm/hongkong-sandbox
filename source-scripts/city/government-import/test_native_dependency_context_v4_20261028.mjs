import test from 'node:test';
import assert from 'node:assert/strict';
import {verifyBoundSurveyedFallback as verify,verifyCurrentInstalledDependency} from './native_dependency_context_v4_20261028.mjs';
const owner={uid:'landsd/1:0',sha256:'owner'},dependency={uid:'landsd/2:0',state:'surveyed-footprint-fallback'},
 form={uid:dependency.uid,buildingCSUID:'survey-id'},standard={uid:dependency.uid,existingNative:false,reasons:[]},
 binding={kind:'exact-current-surveyed-fallback',owner:owner.uid,ownerSHA256:owner.sha256,ownerReviewState:'installed-verified',snapshotId:'snapshot',rawDependency:dependency,uid:dependency.uid,csuid:form.buildingCSUID,sourceForm:form},tile={buildings:[form]};
test('exact current fallback preserves raw row and grants no support credit',()=>{
 const result=verify(owner,dependency,undefined,form,standard,binding,tile);
 assert.equal(result.physicalSupportCredit,false);assert.equal(result.basicBeforeAfterRegressionPassed,true);
 assert.equal(dependency.csuid,undefined);
});
test('all binding, identity, replacement and regression mutations reject',()=>{
 const args=[owner,dependency,undefined,form,standard,binding,tile];
 const mutations=[
  [0,{...owner,sha256:'changed'}],[1,{...dependency,state:'installed'}],
  [2,{uid:dependency.uid}],[3,{...form,modelGeometry:{}}],
  [3,{...form,buildingCSUID:'wrong'}],[4,{...standard,reasons:['ground-gap']}],
  [4,{...standard,existingNative:true}],[5,null],
  [5,{...binding,ownerReviewState:'pending'}],[5,{...binding,csuid:'wrong'}],
  [5,{...binding,sourceForm:{...form,height:99}}],[5,{...binding,rawDependency:{...dependency,csuid:'invented'}}],
  [6,{buildings:[]}],[6,{buildings:[form,form]}],
 ];
 for(const [i,value] of mutations){const changed=args.slice();changed[i]=value;assert.throws(()=>verify(...changed));}
});
test('real verifier rejects missing tile proof; pinned/native paths keep old guards',()=>{
 assert.throws(()=>verifyCurrentInstalledDependency(owner,dependency,undefined,form,standard,binding));
 assert.throws(()=>verifyCurrentInstalledDependency(owner,{...dependency,csuid:'wrong'},undefined,form,standard,binding));
 assert.throws(()=>verifyCurrentInstalledDependency(owner,{...dependency,state:'installed'},undefined,form,standard,binding));
});
