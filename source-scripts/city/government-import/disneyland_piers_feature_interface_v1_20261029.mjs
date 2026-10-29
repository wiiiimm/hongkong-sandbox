import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {officialModelFootprint} from '../../../3d-viewer/city/official-model-footprint-scopes.js';
import {reviewedOriginalFeatureScopes} from '../../../3d-viewer/city/official-model-reviewed-original-feature-data.js';
const base='docs/astra-city/government-import/',rows=JSON.parse(gunzipSync(readFileSync(base+'government-xl-disneyland-piers-current-selection-v1-20261029/selection.json.gz'))).rows;
assert.deepEqual(reviewedOriginalFeatureScopes['reviewed-original-feature:landsd/99482:0'],JSON.parse(readFileSync(base+'government-xl-runtime-fit-99482-reviewed-feature-scope-v1-20261022/prepared-scope.json')));
const results=[];
for(const source of rows){
 const entry={...structuredClone(source.candidate.entry),footprintScope:'reviewed-original-feature:'+source.uid},building=structuredClone(source.source.building),before=structuredClone(building);
 const boundary=officialModelFootprint(entry,building,null);assert(boundary.length>=3);assert.deepEqual(building,before);boundary[0][0]+=1000;assert.notDeepEqual(officialModelFootprint(entry,building,null),boundary);
 let rejected=0;
 for(const mutation of [{sha256:'0'.repeat(64)},{uid:'landsd/1:0'},{modelId:'wrong'},{worldBounds:[[0,0,0],[1,1,1]]},{suppressesBuildingUids:['way/334029318:0']},{variantId:'unreviewed'}]){assert.throws(()=>officialModelFootprint({...entry,...mutation},building,null));rejected++;}
 const altered=structuredClone(building);altered.rings[0][0][0]+=.01;assert.throws(()=>officialModelFootprint(entry,altered,null));rejected++;
 assert.throws(()=>officialModelFootprint(entry,{...building,topHeightHKPD:building.topHeightHKPD+.01},null));rejected++;
 assert.throws(()=>officialModelFootprint(entry,rows.find(r=>r.uid!==source.uid).source.building,null));rejected++;
 results.push({uid:source.uid,sourceSHA256:source.sourceSHA256,ordinaryGISFormUnchanged:true,boundaryDefensiveCopy:true,rejectedMutations:rejected});
}
const result={passed:true,existingLookoutScopeUnchanged:true,rows:results,totalRejectedMutations:results.reduce((n,r)=>n+r.rejectedMutations,0),installationApproved:false,sourceGeometryChanges:0};
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
