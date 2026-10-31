import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {describeBuilding as originalDescription,createBuildingGeometry as originalGeometry} from '../building-geometry.js';
import {describeBuilding,createBuildingGeometry,collisionVolumes} from '../source-bound-basic-geometry-private.js';
const packet=new URL('../../../docs/astra-city/government-import/government-xl-sha-tin-three-basic-ground-proposals-v2-20261029/summary.json',import.meta.url);
// Tests use actual private proposal rows, including the complex terminus plan.
const rows=JSON.parse(readFileSync(packet)).rows;
for(const {uid,originalBuilding,proposedBuilding} of rows){
 test(`${uid}: original body attributes and surveyed roof remain exact`,()=>{
  const before=JSON.stringify(proposedBuilding),old=originalGeometry(originalBuilding),next=createBuildingGeometry(proposedBuilding);
  for(const [name,attr] of Object.entries(old.attributes))assert.deepEqual(next.attributes[name].array.slice(0,attr.array.length),attr.array,name);
  assert.equal(JSON.stringify(proposedBuilding),before);
  const description=describeBuilding(proposedBuilding),baseline=originalDescription(originalBuilding),part=description.parts.at(-1);
  assert.deepEqual(description.parts.slice(0,-1),baseline.parts);assert.equal(part.kind,'basic-ground-continuation');
  assert.equal(part.top,baseline.parts[0].bottom);assert.equal(part.bottom,proposedBuilding.nativeFallbackGround.base);
  assert.deepEqual(collisionVolumes(proposedBuilding),description.parts);assert.equal(part.windows,false);
  const added=next.attributes.position.array.slice(old.attributes.position.array.length),ringXZ=new Set(proposedBuilding.rings.flat().map(([x,z])=>`${Math.fround(x)},${Math.fround(z)}`));
  for(let i=0;i<added.length;i+=3){assert.ok(ringXZ.has(`${added[i]},${added[i+2]}`));assert.ok([Math.fround(part.bottom),Math.fround(part.top)].includes(added[i+1]));}
  for(const value of next.attributes.cityWindows.array.slice(old.attributes.cityWindows.array.length))assert.equal(value,0);
  old.dispose();next.dispose();
 });
 test(`${uid}: no hint keeps legacy geometry; native source arrays remain unchanged`,()=>{
  const legacy=originalGeometry(originalBuilding),noHint=createBuildingGeometry(originalBuilding);for(const name of Object.keys(legacy.attributes))assert.deepEqual(noHint.attributes[name].array,legacy.attributes[name].array);
  const [x,z]=originalBuilding.rings[0][0],y=5;
  const modelGeometry={position:[x,y,z,x+1,y,z,x,y+2,z+1],index:[0,1,2]};
  const native={...proposedBuilding,modelGeometry},snapshot=JSON.stringify(modelGeometry),a=originalGeometry(native),b=createBuildingGeometry(native);
  for(const name of Object.keys(a.attributes))assert.deepEqual(b.attributes[name].array,a.attributes[name].array);
  assert.equal(JSON.stringify(modelGeometry),snapshot);assert.equal(describeBuilding(native).sourceBoundBasicContinuation,undefined);
  for(const g of [legacy,noHint,a,b])g.dispose();
 });
}
test('same object cannot reuse a stale continuation after its hint changes',()=>{
 const b=structuredClone(rows[0].proposedBuilding);describeBuilding(b);b.nativeFallbackGround.uid='another';assert.throws(()=>describeBuilding(b),/Invalid/);
});
