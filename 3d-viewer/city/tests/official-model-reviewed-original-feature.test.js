import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {officialModelFootprint} from '../official-model-footprint-scopes.js';
import {describeBuilding} from '../building-geometry.js';
const input=JSON.parse(readFileSync(new URL('../../../docs/astra-city/government-import/government-xl-runtime-fit-99482-reviewed-feature-scope-v1-20261022/scope-test-input.json',import.meta.url)));
const fixture=()=>structuredClone(input);
test('reviewed complete tower/ramp/bridge passes existing model validator without changing its GIS footprint',()=>{
 const {entry,building}=fixture(),before=structuredClone(building),bounds=entry.worldBounds;
 const position=[...bounds[0],bounds[1][0],bounds[0][1],bounds[0][2],...bounds[1],bounds[0][0],bounds[1][1],bounds[1][2]],index=[0,1,2,0,2,3];
 assert.equal(describeBuilding({...building,modelGeometry:{position,index}}).modelStatus,'invalid-fallback');
 const boundary=officialModelFootprint(entry,building,null);
 assert.equal(describeBuilding({...building,modelGeometry:{position,index,footprintBoundary:boundary}}).modelStatus,'usable');
 assert.deepEqual(building,before);boundary[0][0]+=1000;assert.notDeepEqual(officialModelFootprint(entry,building,null),boundary);
});
test('complete-feature scope rejects another source, form, bounds, suppression or unreviewed variant',()=>{
 const {entry,building}=fixture();
 for(const change of [{sha256:'0'.repeat(64)},{uid:'landsd/1:0'},{modelId:'wrong'},{footprintScope:'reviewed-original-feature:unknown'},{worldBounds:[[0,0,0],[1,1,1]]},{suppressesBuildingUids:['landsd/1:0']},{variantId:'unreviewed'}])assert.throws(()=>officialModelFootprint({...entry,...change},building,null));
 const altered=structuredClone(building);altered.rings[0][0][0]+=.01;assert.throws(()=>officialModelFootprint(entry,altered,null));
 assert.throws(()=>officialModelFootprint(entry,{...building,topHeightHKPD:building.topHeightHKPD+.01},null));
});
test('ordinary models retain the ordinary footprint route',()=>assert.equal(officialModelFootprint({}, {}, null),null));
