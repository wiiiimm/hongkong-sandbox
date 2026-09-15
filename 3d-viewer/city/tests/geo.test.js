import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {makeTerrainSampler,BuildingIndex,inPolygon,segmentDistanceSq,ORIGIN} from '../geo.js';
const square=[[0,0],[20,0],[20,20],[0,20],[0,0]];
const courtyard=[[5,5],[5,15],[15,15],[15,5],[5,5]];
test('courtyards stay open, but their walls block a pedestrian radius',()=>{
 const b={rings:[square,courtyard],base:3,minimum:0,height:30};
 const index=new BuildingIndex([b],10);
 assert.equal(inPolygon(10,10,b.rings),false);assert.equal(index.collision(10,10,3,5,.5),null);
 assert.equal(index.collision(5.1,10,3,5,.5),b);assert.equal(index.collision(2,2,3,5),b);
 assert.equal(index.collision(20.2,10,3,5,.5),b);assert.equal(index.collision(21,10,3,5,.5),null);
});
test('minimum heights allow passing beneath a bridge-like building part',()=>{
 const b={rings:[square],base:3,minimum:6,height:20},index=new BuildingIndex([b]);
 assert.equal(index.collision(10,10,3,5),null);assert.equal(index.collision(10,10,9,12),b);assert.equal(index.collision(10,10,24,26),null);
});
test('spatial hash finds a boundary collision in the neighbouring cell',()=>{
 const b={rings:[square],base:0,minimum:0,height:20},index=new BuildingIndex([b],10);
 assert.equal(index.collision(-.2,10,0,2,.5),b);assert.equal(segmentDistanceSq(-3,7,[0,0],[0,10]),9);
});
test('ground height follows the mesh triangle, not a bilinear saddle',()=>{
 const data={w:2,h:2,elev:[2,12,22,62],meta:{georef:{aE:70,bE:ORIGIN[0],aN:-70,bN:ORIGIN[1]}}};
 const sample=makeTerrainSampler(data);
 assert.equal(sample.raw(17.5,17.5),9.5);assert.equal(sample.height(52.5,52.5),39.5);
 assert.equal(sample.contains(-1,0),false);assert.equal(sample.contains(69,69),true);
});
const city=JSON.parse(readFileSync(new URL('../data/central.json',import.meta.url)));
test('bundled city retains real footprints, valid heights and per-feature provenance',()=>{
 assert.ok(city.buildings.length>9000);assert.deepEqual(city.meta.origin,ORIGIN);
 for(const b of city.buildings){
  assert.match(b.id,/^(way|relation)\/\d+$/);assert.ok(b.height>b.minimum&&b.height<600);assert.ok(Number.isFinite(b.base));assert.ok(['tagged','levels','estimated'].includes(b.heightSource));
  for(const r of b.rings){assert.ok(r.length>=4);assert.deepEqual(r[0],r.at(-1));assert.ok(r.every(p=>p.length===2&&p.every(Number.isFinite)));}
 }
 assert.equal(city.meta.counts.buildings,city.buildings.length);
});
test('known tower heights and named building parts survive the import',()=>{
 const ifc=city.buildings.find(b=>b.name==='Two International Finance Centre');assert.equal(ifc.height,415.8);assert.ok(Math.abs(ifc.centre[0]+45.4)<.5);
 const boc=city.buildings.filter(b=>b.name==='Bank of China Tower');assert.ok(boc.length>0);assert.ok(Math.max(...boc.map(b=>b.height))>=300);
});
