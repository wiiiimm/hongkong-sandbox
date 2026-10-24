import assert from 'node:assert/strict';
import {featureForm,reviewedOriginalFeatureFootprint as scope} from './reviewed_original_feature_footprint_v2.mjs';
const building={uid:'landsd/99482:0',objectId:99482,buildingCSUID:'3659434533T20050430',rings:[[[1,1],[2,1],[2,2],[1,1]]],baseHeightHKPD:8.5,topHeightHKPD:27.8};
const entry={uid:building.uid,modelId:'B365943453301063C0',sha256:'a'.repeat(64),worldBounds:[[0,5,0],[60,39,60]],footprintScope:'reviewed-original-feature:landsd/99482:0'};
const reviewed={policy:'reviewed-original-feature-v1',identityReviewed:true,uid:entry.uid,modelId:entry.modelId,sha256:entry.sha256,worldBounds:entry.worldBounds,form:featureForm(building),boundary:[[0,0],[60,0],[60,60],[0,60]],sourceReview:{path:'docs/astra-city/government-import/fixture/review.json',sha256:'b'.repeat(64)}};
const registry={[entry.footprintScope]:reviewed};
const before=JSON.stringify({entry,building,registry});
assert.deepEqual(scope(entry,building,registry),reviewed.boundary);
assert.equal(JSON.stringify({entry,building,registry}),before);
for(const changed of [{...entry,sha256:'c'.repeat(64)},{...entry,modelId:'wrong'},{...entry,uid:'landsd/1:0'},{...entry,worldBounds:[[0,5,0],[61,39,60]]},{...entry,variantId:'unreviewed-derived'},{...entry,suppressesBuildingUids:['landsd/1:0']}])assert.throws(()=>scope(changed,building,registry));
for(const changed of [{...building,topHeightHKPD:28},{...building,rings:[[[1,1],[3,1],[2,2],[1,1]]]}])assert.throws(()=>scope(entry,changed,registry));
assert.throws(()=>scope(entry,building,{}));
assert.throws(()=>scope(entry,building,{[entry.footprintScope]:{...reviewed,identityReviewed:false}}));
assert.throws(()=>scope(entry,building,{[entry.footprintScope]:{...reviewed,boundary:[[0,0],[100,0],[0,60]]}}));
console.log('complete original feature: exact source/form/bounds, approval, suppression and variant fences passed');

const reordered={...reviewed,form:Object.fromEntries(Object.keys(reviewed.form).sort().map(k=>[k,reviewed.form[k]]))};
assert.deepEqual(scope(entry,building,{[entry.footprintScope]:reordered}),reviewed.boundary);
console.log('persisted JSON object-key ordering is handled without changing field values');
