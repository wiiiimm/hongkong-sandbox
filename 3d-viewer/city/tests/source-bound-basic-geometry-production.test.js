import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as production from '../building-geometry.js';
import * as core from '../building-geometry-core.js';
import * as prototype from '../source-bound-basic-geometry-private.js';
const rows=JSON.parse(readFileSync(new URL('../../../docs/astra-city/government-import/government-xl-sha-tin-three-basic-ground-proposals-v2-20261029/summary.json',import.meta.url))).rows;
const equal=(a,b)=>{assert.deepEqual(Object.keys(a.attributes),Object.keys(b.attributes));for(const k of Object.keys(a.attributes))assert.deepEqual(a.attributes[k].array,b.attributes[k].array);assert.deepEqual(a.index?.array,b.index?.array);};
test('production core is the exact original geometry implementation',()=>{
 assert.equal(createHash('sha256').update(readFileSync(new URL('../building-geometry-core.js',import.meta.url))).digest('hex'),'f3336a37c5164a78c931c702ad2ca5f62ed872adab9513787d3f8517fb3bdd4e');
 assert.equal(production.prepareModelGeometry,core.prepareModelGeometry);assert.equal(production.isOpenSidedBuilding,core.isOpenSidedBuilding);
});
for(const row of rows){
 test(row.uid+': production adapter equals the browser-tested prototype',()=>{
  const a=production.createBuildingGeometry(row.proposedBuilding),b=prototype.createBuildingGeometry(row.proposedBuilding);equal(a,b);assert.deepEqual(production.describeBuilding(row.proposedBuilding),prototype.describeBuilding(row.proposedBuilding));assert.deepEqual(production.collisionVolumes(row.proposedBuilding),prototype.collisionVolumes(row.proposedBuilding));a.dispose();b.dispose();
 });
 test(row.uid+': unmodified BASIC and native fallback routing keep the original core',()=>{
  const [x,z]=row.originalBuilding.rings[0][0];
  for(const building of [row.originalBuilding,{...row.proposedBuilding,modelGeometry:{position:[x,5,z,x+1,5,z,x,7,z+1],index:[0,1,2]}}]){
   const a=production.createBuildingGeometry(building),b=core.createBuildingGeometry(building);equal(a,b);assert.deepEqual(production.describeBuilding(building),core.describeBuilding(building));a.dispose();b.dispose();
  }
 });
}
