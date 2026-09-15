import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {BridgeLayer,geometryFor} from '../bridges.js';

const prepared=(id='way/1',x=0,extra={})=>({id,source:'https://www.openstreetmap.org/'+id,sourceId:id,kind:'footway',role:'bridge',width:3,covered:false,estimatedElevation:true,elevationBasis:'Test-only supplied elevation',widthBasis:'Test supplied width',deckPath:[[x,8,0],[x+20,8,0]],bounds:[x-1.5,-1.5,x+21.5,1.5],...extra});
const layer=()=>new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>{throw new Error('Renderer must not resample route heights');}},prepare:records=>records});
const response=data=>({ok:true,json:async()=>data});

async function withFetch(fetcher,run){const previous=globalThis.fetch;globalThis.fetch=fetcher;try{return await run();}finally{globalThis.fetch=previous;}}

test('solid deck preserves supplied top heights and width with outward-facing top and underside',()=>{
 const geometry=geometryFor(prepared()),p=geometry.attributes.position,n=geometry.attributes.normal;
 assert.equal(p.count,36,'one closed six-face span');assert.equal(geometry.attributes.bridgeFeature.count,p.count);
 assert.equal(geometry.boundingBox.min.x,0);assert.equal(geometry.boundingBox.max.x,20);
 assert.equal(geometry.boundingBox.min.z,-1.5);assert.equal(geometry.boundingBox.max.z,1.5);
 assert.equal(geometry.boundingBox.max.y,8);assert.ok(Math.abs(geometry.boundingBox.min.y-7.76)<1e-6);
 for(let i=0;i<6;i++)assert.ok(n.getY(i)>.999,'top faces upwards');
 for(let i=6;i<12;i++)assert.ok(n.getY(i)<-.999,'underside faces downwards');
 assert.ok([...p.array].every(Number.isFinite));geometry.dispose();
});

test('bent and sloping source spans join without extreme miter spikes or terrain lifting',()=>{
 const record=prepared('way/2',0,{width:4,deckPath:[[0,3,0],[10,6,0],[10,9,10],[10.01,9,0]]});
 const geometry=geometryFor(record,23),p=geometry.attributes.position;
 assert.ok([...p.array].every(Number.isFinite));assert.ok(geometry.boundingBox.min.x>=-3.7&&geometry.boundingBox.max.x<=13.7);
 assert.equal(geometry.boundingBox.max.y,9);assert.ok(Math.abs(geometry.boundingBox.min.y-2.76)<1e-6);
 assert.deepEqual(new Set(geometry.attributes.bridgeFeature.array),new Set([23]));
 assert.throws(()=>geometryFor({...record,width:NaN}),/Invalid prepared/);
 assert.throws(()=>geometryFor({...record,deckPath:[[0,3,0],[0,8,0]]}),/horizontal span/);geometry.dispose();
});

test('explicit cover creates a canopy, while uncovered and name-only covered hints do not',async()=>{
 const detail=layer();
 await withFetch(async()=>response([prepared('way/1',0,{covered:true}),prepared('way/2',100,{name:'Covered Walkway',covered:'no'}),prepared('way/3',200,{covered:'yes'})]),async()=>{
  assert.equal(await detail.load('bridges.json'),true);
  const group=[...detail.cache.values()][0],roof=group.children.find(mesh=>mesh.userData.bridgePart==='canopy');
  assert.ok(roof);assert.deepEqual(new Set(roof.geometry.attributes.bridgeFeature.array),new Set([0,2]));
  assert.ok(Math.abs(roof.geometry.boundingBox.max.y-10.8)<1e-6);
  const rails=group.children.find(mesh=>mesh.isInstancedMesh);assert.ok(rails?.count>0);assert.equal(detail.stats.covered,2);
  assert.equal(group.children.filter(mesh=>mesh.userData.bridgePart==='deck').length,1,'decks share one draw per style');
  detail.dispose();
 });
});

test('ray picking a merged deck returns the original source record and selection geometry',async()=>{
 const detail=layer(),records=[prepared('way/11'),prepared('way/12',100)];
 await withFetch(async()=>response(records),async()=>{
  await detail.load('bridges.json');detail.group.updateMatrixWorld(true);
  const ray=new THREE.Raycaster(new THREE.Vector3(110,20,0),new THREE.Vector3(0,-1,0));
  const [hit]=ray.intersectObjects(detail.pickMeshes());assert.ok(hit);assert.equal(detail.featureAt(hit),records[1]);
  const geometry=detail.geometryFor(records[1]);assert.deepEqual(new Set(geometry.attributes.bridgeFeature.array),new Set([1]));geometry.dispose();
  assert.equal(detail.featureAt({object:new THREE.Mesh(),face:{a:0}}),undefined);
  detail.group.visible=false;assert.equal(detail.pickMeshes().length,0);assert.equal(detail.stats.visibleSpans,0);assert.equal(detail.featureAt(hit),undefined);
  detail.group.visible=true;detail.dispose();assert.equal(detail.featureAt(hit),undefined);
 });
});

test('failed loads preserve source suppression, retries succeed and duplicate packages do not duplicate decks',async()=>{
 const detail=layer();let calls=0;
 await withFetch(async()=>{calls++;return calls===1?{ok:false,status:503}:response([prepared('bridge:42',0,{source:'https://www.openstreetmap.org/way/42',sourceId:'way/42'})]);},async()=>{
  assert.equal(await detail.load('bridges.json'),false);assert.equal(detail.records.size,0);assert.equal(detail.loadedIds.size,0);assert.deepEqual(detail.stats.errors,['bridges.json']);
  assert.equal(await detail.retry(),true);assert.equal(detail.stats.pending,0);assert.equal(detail.stats.errors.length,0);assert.equal(detail.stats.spans,1);
  assert.ok(detail.loadedIds.has('way/42'));assert.ok(detail.loadedIds.has('bridge:42'));
  await detail.load('overlap.json');assert.equal(detail.stats.spans,1);assert.equal(detail.stats.visibleSpans,1);assert.equal(detail.stats.estimatedElevation,1);
  detail.dispose();
 });
});

test('invalid prepared batches fail atomically before any old bridge-road IDs are suppressed',async()=>{
 const detail=layer();
 await withFetch(async()=>response([prepared(),prepared('bad',100,{deckPath:[[100,8,0],[NaN,8,0]]})]),async()=>{
  assert.equal(await detail.load('bad.json'),false);assert.equal(detail.records.size,0);assert.equal(detail.loadedIds.size,0);assert.equal(detail.cache.size,0);assert.equal(detail.stats.errors.length,1);detail.dispose();
 });
});

test('territory caching is bounded and distant deck/instance buffers are disposed',async()=>{
 const detail=layer(),records=Array.from({length:50},(_,i)=>prepared('way/'+i,(i%10-5)*1700,{deckPath:[[(i%10-5)*1700,8,Math.floor(i/10)*1700],[(i%10-5)*1700+20,8,Math.floor(i/10)*1700]],bounds:[(i%10-5)*1700,Math.floor(i/10)*1700,(i%10-5)*1700+20,Math.floor(i/10)*1700]}));
 await withFetch(async()=>response(records),async()=>{
  await detail.load('many.json');detail.plan(0,3400,5000);assert.equal(detail.stats.tiles,24);assert.equal(detail.stats.spans,50);
  let disposed=0,instancesDisposed=0,sharedDisposed=0;
  detail.boxGeometry.addEventListener('dispose',()=>sharedDisposed++);
  for(const group of detail.cache.values())group.traverse(object=>{
   if(object.isInstancedMesh)object.addEventListener('dispose',()=>instancesDisposed++);
   else object.geometry?.addEventListener('dispose',()=>disposed++);
  });
  detail.plan(80000,80000,100);assert.equal(detail.stats.tiles,0);assert.ok(disposed>0);assert.ok(instancesDisposed>0);assert.equal(sharedDisposed,0,'shared rail geometry survives tile eviction');
  detail.plan(0,0);assert.ok(detail.stats.tiles>0);detail.dispose();assert.equal(sharedDisposed,1);
 });
});

test('teardown prevents late fetch completion from resurrecting records, geometry or callbacks',async()=>{
 let release,signals=[],changes=0;
 const detail=new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>0},prepare:records=>records,onChange:()=>changes++});
 await withFetch((url,{signal})=>{signals.push(signal);return new Promise(resolve=>{release=resolve;});},async()=>{
  const pending=detail.load('late.json');await Promise.resolve();assert.equal(signals.length,1);detail.dispose();const before=changes;
  assert.equal(signals[0].aborted,true);release(response([prepared()]));assert.equal(await pending,false);
  assert.equal(detail.records.size,0);assert.equal(detail.cache.size,0);assert.equal(detail.loadedIds.size,0);assert.equal(detail.group.parent,null);assert.equal(changes,before);
  assert.deepEqual(detail.plan(0,0),[]);detail.buildTile('0_0');assert.equal(await detail.load('again.json'),false);assert.equal(detail.stats.pending,0);assert.equal(detail.pickMeshes().length,0);
 });
});

test('teardown also guards a late asynchronous preparation result',async()=>{
 let finish;
 const detail=new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>0},prepare:()=>new Promise(resolve=>{finish=resolve;})});
 await withFetch(async()=>response([]),async()=>{
  const pending=detail.load('preparing.json');while(!finish)await Promise.resolve();detail.dispose();finish([prepared()]);assert.equal(await pending,false);assert.equal(detail.cache.size,0);assert.equal(detail.records.size,0);
 });
});


test('distant bridges retain decks and canopies while sub-pixel rail details are hidden',async()=>{
 const detail=layer();
 await withFetch(async()=>response([prepared('way/1'),prepared('way/2',2600,{covered:true})]),async()=>{
  await detail.load('distance.json');detail.plan(0,0,3000);assert.equal(detail.pickMeshes().length,2);
  const distant=[...detail.cache.values()].find(group=>group.children.some(mesh=>mesh.userData.bridgePart==='canopy'));
  assert.ok(distant);assert.equal(distant.userData.railMesh.visible,false);assert.equal(distant.userData.railMesh.castShadow,false);
  assert.equal(distant.children.find(mesh=>mesh.userData.bridgePart==='canopy').visible,true);
  const oldDeck=distant.userData.deckMeshes[0];detail.plan(90000,0,100);assert.equal(detail.featureAt({object:oldDeck,face:{a:0}}),undefined,'evicted geometry cannot be picked');
  detail.dispose();
 });
});


test('high aerial cameras hide rail instances without rebuilding or hiding bridge decks',async()=>{
 const detail=new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>30},prepare:records=>records});
 await withFetch(async()=>response([prepared()]),async()=>{
  await detail.load('altitude.json');const group=[...detail.cache.values()][0],deck=detail.pickMeshes()[0];
  detail.plan(0,0,3000,new THREE.Vector3(0,2030,0));assert.equal(group.userData.railMesh.visible,false);assert.equal(detail.pickMeshes()[0],deck);
  detail.plan(0,0,3000,new THREE.Vector3(0,100,0));assert.equal(group.userData.railMesh.visible,true);assert.equal(detail.pickMeshes()[0],deck);
  detail.dispose();
 });
});
