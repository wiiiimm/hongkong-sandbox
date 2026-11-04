import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {describeBuilding,createBuildingGeometry} from '../building-geometry.js';
const read=url=>JSON.parse(readFileSync(new URL(url,import.meta.url)));
test('all extended Mui Wo source models use the existing geometry and collision contract',()=>{
 const manifest=read('../data/manifest.json');let models=0,vertices=0;
 for(const tile of manifest.tiles.filter(t=>t.bounds[0]<-15000&&t.bounds[2]>-19000&&t.bounds[1]<4000&&t.bounds[3]>1000)){
  for(const building of read('../../'+tile.url).buildings){
   if(!building.modelGeometry)continue;
   const desc=describeBuilding(building);assert.equal(desc.modelStatus,'usable',building.uid);assert.ok(desc.parts.length>0);
   assert.equal(building.buildingCSUID,building.modelGeometry.buildingCSUID);const geometry=createBuildingGeometry(building);assert.ok(geometry.attributes.position.count>=building.modelGeometry.position.length/3);assert.equal(geometry.attributes.cityWindows.count,geometry.attributes.position.count);geometry.dispose();models++;vertices+=building.modelGeometry.position.length/3;
  }
 }
 assert.equal(models,1327);assert.equal(vertices,590424);
});
