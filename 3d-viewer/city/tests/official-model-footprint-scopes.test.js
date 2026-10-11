import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {officialModelFootprint,modelFootprintScopeKeys} from '../official-model-footprint-scopes.js';
import {describeBuilding} from '../building-geometry.js';
const root=new URL('../../../',import.meta.url);
const rows=JSON.parse(gunzipSync(readFileSync(new URL('docs/astra-city/government-import/government-xl-held-component-recovery-20261008/physical-selection.json.gz',root)))).rows;
const review=JSON.parse(readFileSync(new URL('docs/astra-city/government-import/government-xl-six-source-identity-review-20261008/review.json',root)));
function fixture(uid){
 const row=rows.find(r=>r.uid===uid),forms=structuredClone(review.rows.find(r=>r.uid===uid).groupForms),building=forms.find(b=>b.uid===uid);
 const entry={...row.candidate.entry,footprintScope:uid,suppressesBuildingUids:forms.filter(b=>b.uid!==uid).map(b=>b.uid)};
 return {row,forms,building,entry,getBuilding:uid=>forms.find(b=>b.uid===uid)};
}
for(const uid of modelFootprintScopeKeys.filter(uid=>uid!=='landsd/81743:0')){
 test('complete market scope preserves source footprint and existing model bounds guard '+uid,()=>{
  const f=fixture(uid),before=structuredClone(f.building),boundary=officialModelFootprint(f.entry,f.building,f.getBuilding);
  const [lo,hi]=f.row.native.model.worldBounds;
  const position=[...lo,hi[0],lo[1],lo[2],hi[0],hi[1],hi[2],lo[0],hi[1],hi[2]],index=[0,1,2,0,2,3];
  assert.equal(describeBuilding({...f.building,modelGeometry:{position,index}}).modelStatus,'invalid-fallback');
  assert.equal(describeBuilding({...f.building,modelGeometry:{position,index,footprintBoundary:boundary}}).modelStatus,'usable');
  assert.deepEqual(f.building,before);
  boundary[0][0]=1e9;assert.notEqual(officialModelFootprint(f.entry,f.building,f.getBuilding)[0][0],1e9);
 });
 test('changed or unavailable current market member rejects '+uid,()=>{
  const f=fixture(uid),other=f.forms.find(b=>b.uid!==uid);
  assert.throws(()=>officialModelFootprint(f.entry,f.building,()=>null),/changed or unavailable/);
  other.rings[0][0][0]+=.01;assert.throws(()=>officialModelFootprint(f.entry,f.building,f.getBuilding),/changed or unavailable/);
 });
 test('scope cannot migrate to another mesh, UID, model ID or suppression set '+uid,()=>{
  const f=fixture(uid);
  for(const change of [{sha256:'0'.repeat(64)},{uid:'landsd/1:0'},{modelId:'wrong'},{footprintScope:'unknown'},{suppressesBuildingUids:[]}])assert.throws(()=>officialModelFootprint({...f.entry,...change},f.building,f.getBuilding));
  assert.throws(()=>officialModelFootprint(f.entry,f.building,null));
 });
}
test('ordinary models keep their existing footprint route',()=>assert.equal(officialModelFootprint({}, {}, null),null));

const oceanRows=JSON.parse(gunzipSync(readFileSync(new URL('docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz',root)))).rows;
const oceanContext=JSON.parse(gunzipSync(readFileSync(new URL('docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/context.json.gz',root)))).rows;
function oceanFixture(){const uid='landsd/81743:0',row=oceanRows.find(r=>r.uid===uid),forms=structuredClone(oceanContext.find(r=>r.uid===uid).groupForms);return {row,forms,building:forms.find(b=>b.uid===uid),entry:{...row.candidate.entry,footprintScope:uid,suppressesBuildingUids:[]},getBuilding:uid=>forms.find(b=>b.uid===uid)};}
test('Ocean Walk geographic context retains every upper and ancillary component',()=>{
 const f=oceanFixture(),before=structuredClone(f.forms),boundary=officialModelFootprint(f.entry,f.building,f.getBuilding);
 assert.equal(f.forms.length,18);assert(boundary.length>f.building.rings[0].length);assert.deepEqual(f.forms,before);assert.deepEqual(f.entry.suppressesBuildingUids,[]);
 const tower=f.forms.find(b=>b.name==='Pierhead Garden Tower 1');assert(tower&&tower.topHeightHKPD>100);
 assert.throws(()=>officialModelFootprint({...f.entry,suppressesBuildingUids:[tower.uid]},f.building,f.getBuilding),/suppression differs/);
});
test('Ocean Walk scope rejects wrong original bytes or any changed/unavailable retained component',()=>{
 const f=oceanFixture(),other=f.forms.find(b=>b.uid!==f.entry.uid);
 assert.throws(()=>officialModelFootprint({...f.entry,sha256:'0'.repeat(64)},f.building,f.getBuilding));
 assert.throws(()=>officialModelFootprint(f.entry,f.building,()=>null),/changed or unavailable/);
 other.objectId++;assert.throws(()=>officialModelFootprint(f.entry,f.building,f.getBuilding),/changed or unavailable/);
});
