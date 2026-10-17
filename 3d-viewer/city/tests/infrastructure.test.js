import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import * as THREE from '../../vendor/three.module.js';
import {prepareInfrastructure,InfrastructureSurfaces} from '../infrastructure-data.js';
import {BridgeLayer,geometryFor,walkingSurfaceFor} from '../bridges.js';
import {describeBuilding,createBuildingGeometry} from '../building-geometry.js';
import {BuildingIndex} from '../geo.js';
const live=JSON.parse(await readFile(new URL('../data/bridges-tai-o.json',import.meta.url)));
const proxy={id:'way/test',source:'https://www.openstreetmap.org/way/test',kind:'footway',width:4,covered:false,estimatedElevation:true,deckPath:[[0,4,0],[10,4,0]],bounds:[0,-2,10,2]};
function fixture(){
 const geometry=geometryFor(proxy),position=[...geometry.attributes.position.array],normal=[...geometry.attributes.normal.array];geometry.dispose();
 const model={id:'landsd-infrastructure/test',sourceUrl:'https://download.map.gov.hk/test',worldBounds:[[0,Math.min(...position.filter((_,i)=>i%3===1)),-2],[10,4,2]],modelGeometry:{position,normal,colour:new Array(position.length).fill(.7)},walkable:true,publicAccessSource:'https://www.islands.gov.hk/test',walkTriangleIndices:[0,1],suppresses:['way/test']};
 return {schemaVersion:1,kind:'tai-o-official-infrastructure',crs:'EPSG:2326',verticalDatum:'Hong Kong Principal Datum',models:[model]};
}
async function fetches(data,run){const old=globalThis.fetch;globalThis.fetch=async url=>({ok:true,json:async()=>structuredClone(data[url])});try{await run();}finally{globalThis.fetch=old;}}
const layer=()=>new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>0},prepare:data=>data});

test('all published exact source meshes preserve positions, normals, colours and immutable HKPD bounds',()=>{
 const records=prepareInfrastructure(live).filter(r=>r.modelGeometry);assert.equal(records.length,5);assert.equal(records.reduce((n,r)=>n+r.modelGeometry.position.length/9,0),2806);
 for(const [i,record]of records.entries()){
  const before=JSON.stringify(record.modelGeometry),g=geometryFor(record,i);
  for(const [attribute,key]of [['position','position'],['normal','normal'],['color','colour']])assert.deepEqual(g.attributes[attribute].array,new Float32Array(record.modelGeometry[key]));
  assert.deepEqual(new Set(g.attributes.bridgeFeature.array),new Set([i]));assert.equal(JSON.stringify(record.modelGeometry),before);g.dispose();
 }
 assert.equal(records.at(-1).base,-5.509200572967529,'surveyed submerged piers are never lifted to ground');
});

test('only explicitly reviewed public decks return the exact source top-face heights',()=>{
 const surfaces=new InfrastructureSurfaces();for(const r of prepareInfrastructure(live))if(r.modelGeometry)surfaces.add(r);
 assert.ok(surfaces.heights(-30663.2,3684.13).some(y=>Math.abs(y-4.058000087738037)<1e-8));
 assert.ok(surfaces.heights(-30667.61,3657.36).some(y=>Math.abs(y-2.628999948501587)<1e-8));
 assert.deepEqual(surfaces.heights(-30384,3481),[],'unverified small source bridge stays non-walkable');
 assert.deepEqual(surfaces.heights(-29945,3750),[],'unverified eastern approach stays non-walkable');
 const bad=fixture();bad.models[0].walkable='yes';assert.throws(()=>prepareInfrastructure(bad),/public deck/);
 bad.models[0].walkable=true;delete bad.models[0].publicAccessSource;assert.throws(()=>prepareInfrastructure(bad),/public deck/);
 const underside=fixture();underside.models[0].walkTriangleIndices=[2];assert.throws(()=>prepareInfrastructure(underside),/deck top face/);
 const wrongDatum=fixture();wrongDatum.verticalDatum='Chart Datum';assert.throws(()=>prepareInfrastructure(wrongDatum),/inventory/);
});

test('source triangle collision distinguishes air below and above the slab from its actual solid surfaces',()=>{
 const s=new InfrastructureSurfaces();s.add(prepareInfrastructure(fixture())[0]);
 assert.equal(s.collision(5,0,0,3,.4),null);assert.equal(s.collision(5,0,4,5.7,.4),null);
 assert.ok(s.collision(5,0,3.7,4.1,.4));assert.equal(s.collision(15,0,3.7,4.1,.4),null);
 assert.deepEqual(s.heights(5,0),[4]);assert.deepEqual(s.heights(15,0),[]);s.clear();assert.equal(s.maximumRoof(5,0),0);
});

for(const order of [['source','proxy'],['proxy','source']])test('source mesh suppresses proxy exactly once in '+order.join(' then ')+' load order',async()=>{
 const detail=layer();await fetches({source:fixture(),proxy:[proxy]},async()=>{
  await detail.load(order[0]);assert.equal(detail.stats.spans,1,'unloaded suppression targets must not reduce visible inventory');
  await detail.load(order[1]);assert.equal(detail.stats.spans,1);assert.equal(detail.stats.visibleSpans,1);assert.equal(detail.stats.sourceModels,1);assert.equal(detail.stats.publicDecks,1);assert.equal(detail.stats.estimatedElevation,0);
  const meshes=detail.pickMeshes();assert.equal(meshes.length,1);assert.ok(meshes[0].geometry.attributes.color);assert.equal(detail.loadedIds.has('way/test'),true);
  detail.group.updateMatrixWorld(true);const [hit]=new THREE.Raycaster(new THREE.Vector3(5,8,0),new THREE.Vector3(0,-1,0)).intersectObjects(meshes);
  assert.equal(detail.featureAt(hit).id,'landsd-infrastructure/test');await detail.load('source');assert.equal(detail.stats.spans,1);detail.dispose();
 });
});

test('malformed source batches cannot add floors, hide proxies or partially change the live inventory',async()=>{
 const detail=layer(),bad=fixture();bad.models.push({...structuredClone(bad.models[0]),id:'landsd-infrastructure/bad'});bad.models[1].modelGeometry.position[0]=NaN;
 await fetches({proxy:[proxy],bad},async()=>{
  await detail.load('proxy');const mesh=detail.pickMeshes()[0];assert.equal(await detail.load('bad'),false);
  assert.equal(detail.records.size,1);assert.equal(detail.surfaces.models.size,0);assert.equal(detail.suppressedIds.size,0);assert.equal(detail.pickMeshes()[0],mesh);assert.equal(detail.stats.spans,1);detail.dispose();
 });
});


test('both estimated approaches share visible floor geometry and keep source disagreement explicit',async()=>{
 const detail=layer();await fetches({live},async()=>{
  assert.equal(await detail.load('live'),true);detail.plan(-30660,3688,1000);
  assert.equal(detail.stats.sourceModels,5);assert.equal(detail.stats.publicApproaches,2);assert.equal(detail.stats.publicDecks,2);assert.equal(detail.stats.spans,7);
  const records=[...detail.records.values()].filter(r=>r.estimatedPublicApproach);
  for(const record of records){
   const surface=detail.surfaces.models.get(record.id),geometry=detail.geometryFor(record);
   assert.deepEqual(walkingSurfaceFor(record).modelGeometry.position,surface.modelGeometry.position);assert.deepEqual(surface.modelGeometry.position,Array.from(geometry.attributes.position.array),'walking reuses actual Float32 vertices from visible geometry');
   assert.ok(Number.isFinite(record.length)&&record.length>0);assert.ok(Number.isFinite(surface.base)&&Number.isFinite(surface.height));assert.equal(surface.base+surface.height,geometry.boundingBox.max.y);assert.equal(record.estimatedElevation,true);assert.match(record.elevationBasis,/Illustrative/);
   for(const p of [record.deckPath[0],record.deckPath.at(-1)])assert.ok(detail.surfaces.heights(p[0],p[2]).some(y=>Math.abs(y-p[1])<2e-4));
   assert.equal(surface.walkTriangleIndices.length,2*record.deckPath.slice(1).filter((p,i)=>Math.hypot(p[0]-record.deckPath[i][0],p[2]-record.deckPath[i][2])>1e-6).length);geometry.dispose();
  }
  const entry=records.find(r=>r.id.endsWith('48126232')).anchors.publicConnector;
  assert.equal(entry.estimatedHorizontalAlignment,true);assert.match(entry.sourceDiscrepancy,/side railing/);assert.ok(entry.maximumDistanceFromOriginalSegmentMetres>1&&entry.maximumDistanceFromOriginalSegmentMetres<2);
  assert.ok(detail.surfaces.heights(-30657.4,3687).some(y=>Math.abs(y-3.4145)<1e-4),'first illustrative stair tread starts at the low landing');
  detail.dispose();
 });
});

test('two current source canopies retain their records while shared visual/collision clearance uses an explicit estimate',async()=>{
 const tile=JSON.parse(await readFile(new URL('../data/tiles/-16_1.json',import.meta.url)));
 const originals=(tile.buildings||tile).filter(b=>['landsd/169618:0','landsd/182398:0'].includes(b.uid));assert.equal(originals.length,2);
 for(const b of originals){
  const original=JSON.stringify(b),description=describeBuilding(b),roof=description.parts.find(p=>p.kind==='roof'),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();
  assert.ok(description.estimate);assert.match(description.placementNote,/illustrative, not surveyed/);
  assert.ok(Math.abs(roof.top-7.058000087738037)<1e-8);assert.ok(Math.abs(geometry.boundingBox.max.y-roof.top)<1e-6);
  const [x,z]=b.centre,index=new BuildingIndex([b]);assert.equal(index.collision(x,z,4.1,5.7,0),null,'canopy roof no longer intersects an actor above the source deck');
  assert.ok(index.collision(x,z,roof.bottom+.01,roof.top+.1,0));assert.equal(JSON.stringify(b),original,'raw NULL elevations/footprint/base are unchanged');geometry.dispose();
  const measured={...b,baseHeightHKPD:2,topHeightHKPD:6};assert.equal(describeBuilding(measured).estimate,null,'never override a subsequently measured canopy');
  const other={...b,uid:'landsd/unrelated:0'};assert.equal(describeBuilding(other).estimate,null,'no general clearance hack');
 }
});

test('a stair at a bend retains vertical risers instead of twisted upward wedges',()=>{
 const record={...proxy,walkable:true,estimatedPublicApproach:true,width:1.5,deckPath:[[0,1,0],[2,1,0],[2,1.2,0],[3,1.2,2],[3,1.4,2],[4,1.4,3]]};
 const surface=walkingSurfaceFor(record),p=surface.modelGeometry.position;
 assert.equal(surface.walkTriangleIndices.length,6,'only the three horizontal-distance tread pairs are floors');
 for(const i of surface.walkTriangleIndices){const y=[p[i*9+1],p[i*9+4],p[i*9+7]];assert.ok(Math.max(...y)-Math.min(...y)<1e-6,'all selected fixture tread triangles are horizontal');}
});
