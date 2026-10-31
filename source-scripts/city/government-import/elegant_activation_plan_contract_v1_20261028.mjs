/** Actual runtime planner contract; no browser/physical/publication acceptance. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {prepareModelCatalogue,modelBudget} from '../../../3d-viewer/city/official-model-assets.js';
import {MODEL_PROFILES} from '../../../3d-viewer/city/official-models.js';
import {supportedModelPlan} from '../../../3d-viewer/city/model-support.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),input=JSON.parse(readFileSync(new URL(process.argv[2],root))),sha=b=>createHash('sha256').update(b).digest('hex');
for(const[p,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/official-models.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const entries=prepareModelCatalogue(input.catalogue,'http://127.0.0.1:4177/city/data/official-models/private-activation/catalogue.json'),models=new Map(entries.map(e=>[e.uid,e])),uids=entries.map(e=>e.uid).sort(),cases=[];
assert.equal(uids.length,16);assert.deepEqual(input.activationGroup,uids);
for(const e of entries){assert.deepEqual(e.activationGroup,uids);assert(!e.publicationApproved&&!e.placementReviewed);assert.deepEqual(e.supportDependencies??[],[]);}
for(const profile of ['desktop','mobile']){
 const limits=MODEL_PROFILES[profile];
 for(const selectedUid of uids){
  const plan=supportedModelPlan([selectedUid],models,limits,modelBudget,()=>true,selectedUid);assert.equal(plan.blocked.size,0);assert.deepEqual([...plan.wanted].sort(),uids);cases.push({profile,selectedUid,all16Wanted:true,used:plan.used});
 }
 for(const missingUid of uids){
  const plan=supportedModelPlan(uids,models,limits,modelBudget,uid=>uid!==missingUid);assert.equal(plan.wanted.length,0);assert.equal(plan.blocked.size,16);cases.push({profile,missingUid,noPartialGroupPlanned:true,blocked:plan.blocked.size});
 }
 const base=supportedModelPlan(uids,models,limits,modelBudget,()=>false);assert.equal(base.wanted.length,0);assert.equal(base.blocked.size,16);cases.push({profile,allOriginalsUnavailable:true,noDetailedModelsPlanned:true});
}
assert(verifyModuleClosure(closure,root));for(const[p,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
writeFileSync(new URL(process.argv[3],root),JSON.stringify({cases,caseCount:cases.length,allPassed:true,actualRuntimePlannerUsed:true,unchangedProductionProfiles:MODEL_PROFILES,inputHashes:{...input.inputHashes,...closure.inputHashes},completeRecursiveProductionModuleClosure:closure,physicalSupportMetadataPending:true,browserChecked:false,baseOnlyRenderingChecked:false,actualFailedDownloadLifecycleChecked:false,installationApproved:false}));
