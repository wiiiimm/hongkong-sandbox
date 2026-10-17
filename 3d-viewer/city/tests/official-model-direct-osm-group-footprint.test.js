import test from 'node:test';
import assert from 'node:assert/strict';
import {directOsmGroupScopes} from '../official-model-direct-osm-group-data.js';
import {officialModelFootprint,modelFootprintScopeKeys} from '../official-model-footprint-scopes.js';
import {describeBuilding} from '../building-geometry.js';
for(const [key,scope] of Object.entries(directOsmGroupScopes)){
 function fixture(){const forms=structuredClone(scope.forms),building=forms.find(b=>b.uid===scope.uid);return {forms,building,entry:{uid:scope.uid,modelId:scope.modelId,sha256:scope.sha256,footprintScope:key,suppressesBuildingUids:[]},getBuilding:uid=>forms.find(b=>b.uid===uid)};}
 test('direct shared-OSM complete footprint preserves every current component '+key,()=>{
  const f=fixture(),before=structuredClone(f.forms),boundary=officialModelFootprint(f.entry,f.building,f.getBuilding);
  assert.deepEqual(boundary,f.forms.flatMap(b=>b.rings[0]));assert.deepEqual(f.forms,before);assert.deepEqual(f.entry.suppressesBuildingUids,[]);
  boundary[0][0]+=1000;assert.deepEqual(officialModelFootprint(f.entry,f.building,f.getBuilding),f.forms.flatMap(b=>b.rings[0]));
 });
 test('direct shared-OSM context rejects changed source identity, geometry, unavailable forms and suppression '+key,()=>{
  const f=fixture();for(const change of [{uid:'landsd/1:0'},{modelId:'other'},{sha256:'0'.repeat(64)},{footprintScope:'direct-osm-group:landsd/1:0'},{suppressesBuildingUids:[f.forms.find(b=>b.uid!==scope.uid).uid]}])assert.throws(()=>officialModelFootprint({...f.entry,...change},f.building,f.getBuilding));
  assert.throws(()=>officialModelFootprint(f.entry,f.building,()=>null));
  for(const field of ['objectId','buildingCSUID','parent','osmRefs','rings']){const a=fixture(),other=a.forms.find(b=>b.uid!==scope.uid);if(field==='rings')other.rings[0][0][0]+=.001;else if(field==='osmRefs')other.osmRefs=['other'];else other[field]='other';assert.throws(()=>officialModelFootprint(a.entry,a.building,a.getBuilding));}
 });
}
test('direct shared-OSM contexts cannot expand the ordinary footprint rule or market key list',()=>{
 assert.equal(Object.keys(directOsmGroupScopes).length,6);assert.equal(modelFootprintScopeKeys.length,3);
 assert.equal(officialModelFootprint({}, {}, null),null);
 const key=Object.keys(directOsmGroupScopes)[0],s=directOsmGroupScopes[key],b=s.forms.find(b=>b.uid===s.uid),boundary=officialModelFootprint({...s,footprintScope:key},b,u=>s.forms.find(f=>f.uid===u));
 const maxX=Math.max(...boundary.map(p=>p[0]))+1000,maxZ=Math.max(...boundary.map(p=>p[1]))+1000;
 assert.equal(describeBuilding({...b,base:0,height:20,minimum:0,modelGeometry:{position:[maxX,0,maxZ,maxX+1,0,maxZ,maxX,1,maxZ+1],index:[0,1,2],footprintBoundary:boundary}}).modelStatus,'invalid-fallback');
});

test('direct OSM sources retain differing parent IDs without admitting transitive references',()=>{
 const scope=directOsmGroupScopes['direct-osm-group:landsd/227593:0'];const primary=scope.forms.find(b=>b.uid===scope.uid);assert(scope.forms.some(b=>b.parent!==primary.parent));const forms=structuredClone(scope.forms),entry={uid:scope.uid,modelId:scope.modelId,sha256:scope.sha256,footprintScope:'direct-osm-group:'+scope.uid};assert(officialModelFootprint(entry,primary,u=>forms.find(b=>b.uid===u)).length);forms.find(b=>b.uid!==scope.uid).osmRefs=['relation/transitive-only'];assert.throws(()=>officialModelFootprint(entry,primary,u=>forms.find(b=>b.uid===u)));});
