import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {describeBuilding,createBuildingGeometry,collisionVolumes} from '../building-geometry.js';
import {proceduralFootprintCorrection} from '../procedural-footprint-corrections.js';
const base=new URL('../../../docs/astra-city/government-import/',import.meta.url);
const proposal=JSON.parse(readFileSync(new URL('government-xl-villa-private-canopy-quantised-boundary-v2-20261015/proposal.json',base)));
const capture=JSON.parse(readFileSync(new URL('government-xl-villa-private-canopy-collision-v2-20261015/rendered.json',base)));
test('integrated canopy matches complete collision-tested production meshes without mutating official form',()=>{
 const building=structuredClone(proposal.currentForm),before=JSON.stringify(building),g=createBuildingGeometry(building);
 const expected=capture.rows.filter(r=>r.mode==='privateCandidate').flatMap(r=>r.index.flatMap(i=>r.position.slice(i*3,i*3+3)));
 assert.deepEqual(Array.from(g.attributes.position.array),expected);
 assert.equal(collisionVolumes(building),describeBuilding(building).parts);
 assert.equal(collisionVolumes(building).filter(p=>p.kind==='roof').length,2);
 assert.equal(JSON.stringify(building),before);g.dispose();
});
test('correction rejects changed identity, geometry, elevations or detailed replacement',()=>{
 for(const edit of [b=>b.uid='landsd/other:0',b=>b.buildingCSUID+='x',b=>b.base+=.01,b=>b.height+=.01,b=>b.rings[0][0][0]+=.01,b=>b.modelGeometry={},b=>b.structureType='Tower']){
  const b=structuredClone(proposal.currentForm);assert.ok(proceduralFootprintCorrection(b));edit(b);assert.equal(proceduralFootprintCorrection(b),null);
 }
});
test('cached description does not retain correction after identity changes',()=>{
 const b=structuredClone(proposal.currentForm);assert.equal(describeBuilding(b).parts.filter(p=>p.kind==='roof').length,2);b.buildingCSUID+='changed';assert.equal(describeBuilding(b).parts.filter(p=>p.kind==='roof').length,1);
});
