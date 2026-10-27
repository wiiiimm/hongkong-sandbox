import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {CityStreaming} from '../streaming.js';
const uid=n=>'landsd/'+n+':0';
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
function fixture(){
 const stream=Object.create(CityStreaming.prototype),pending=[],disposed=[],frames=[];
 Object.assign(stream,{detailedModels:new Map(),infrastructureBuildingUids:new Set(),infrastructureErrors:new Map(),buildings:new THREE.Group(),revision:0});
 const entry=n=>({id:'tile'+n,data:{id:'tile'+n,buildings:[{uid:uid(n)}]},buildings:{group:new THREE.Group()},models:stream.detailedModels,exclusions:stream.infrastructureBuildingUids});
 const a=entry(1),b=entry(2);stream.cache={closed:false,entries:new Map([[a.id,a],[b.id,b]])};stream.buildings.add(a.buildings.group,b.buildings.group);
 stream.sync=()=>frames.push([...stream.detailedModels.keys()]);
 stream.prepareBuildings=(data,signal,models)=>new Promise((resolve,reject)=>{
  const group=new THREE.Group();group.userData.disposableMaterials=[{dispose:()=>disposed.push(data.id)}];
  pending.push({id:data.id,group,signal,models,resolve:()=>resolve({buildings:{group},index:{models},models,exclusions:stream.infrastructureBuildingUids}),reject});
 });
 const detail=n=>({entry:{uid:uid(n)},record:{uid:uid(n),modelGeometry:{}},group:new THREE.Group(),active:false});
 return {stream,pending,disposed,frames,details:[detail(1),detail(2)],oldGroups:[a.buildings.group,b.buildings.group]};
}
async function staged(f){while(f.pending.length<2)await tick();}
test('two-tile source group changes rendering and collision only after every bake is ready',async()=>{
 const f=fixture(),changes=f.details.map(d=>[d.record.uid,d]),work=f.stream.setDetailedModels(changes);await staged(f);
 f.pending[0].resolve();await tick();assert.equal(f.stream.detailedModels.size,0);assert.ok(f.oldGroups.every(g=>g.parent===f.stream.buildings));assert.ok(f.details.every(d=>!d.active));
 f.pending[1].resolve();assert.equal(await work,true);assert.deepEqual(f.frames,[[uid(1),uid(2)]]);assert.ok(f.details.every(d=>d.active&&d.group.parent===f.stream.buildings));
 for(const tile of f.stream.cache.entries.values()){assert.equal(tile.models,f.stream.detailedModels);assert.equal(tile.index.models,f.stream.detailedModels);}
});
test('a failed peer bake keeps both prior basics and disposes every staged success',async()=>{
 const f=fixture(),work=f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,d]));await staged(f);f.pending[0].resolve();f.pending[1].reject(new Error('bake failed'));
 await assert.rejects(work,/bake failed/);assert.equal(f.stream.detailedModels.size,0);assert.ok(f.oldGroups.every(g=>g.parent===f.stream.buildings));assert.deepEqual(f.disposed,['tile1']);assert.ok(f.details.every(d=>!d.active));
});
test('abort after one prepared tile cannot expose a partial group',async()=>{
 const f=fixture(),controller=new AbortController(),work=f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,d]),{signal:controller.signal});await staged(f);
 f.pending[0].resolve();controller.abort();f.pending[1].resolve();assert.equal(await work,false);assert.equal(f.stream.detailedModels.size,0);assert.deepEqual(f.disposed.sort(),['tile1','tile2']);assert.ok(f.oldGroups.every(g=>g.parent===f.stream.buildings));
});
test('a concurrent detailed-map change is preserved, never rolled back by the stale transaction',async()=>{
 const f=fixture(),work=f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,d]));await staged(f);const concurrent=new Map([[uid(3),{}]]);f.stream.detailedModels=concurrent;
 for(const p of f.pending)p.resolve();assert.equal(await work,false);assert.equal(f.stream.detailedModels,concurrent);assert.deepEqual(f.disposed.sort(),['tile1','tile2']);
});
test('source-tile eviction before commit leaves the previous complete visible group intact',async()=>{
 const f=fixture();for(const d of f.details){d.active=true;f.stream.detailedModels.set(d.record.uid,d);f.stream.buildings.add(d.group);}
 const work=f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,null]));await staged(f);f.stream.cache.entries.delete('tile2');for(const p of f.pending)p.resolve();assert.equal(await work,false);assert.equal(f.stream.detailedModels.size,2);assert.ok(f.details.every(d=>d.active));
});
test('fallback of a source group removes all details in one visible commit',async()=>{
 const f=fixture();for(const d of f.details){d.active=true;f.stream.detailedModels.set(d.record.uid,d);f.stream.buildings.add(d.group);}
 const work=f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,null]));await staged(f);f.pending[0].resolve();await tick();assert.ok(f.details.every(d=>d.active));
 f.pending[1].resolve();assert.equal(await work,true);assert.equal(f.stream.detailedModels.size,0);assert.ok(f.details.every(d=>!d.active&&!d.group.parent));assert.deepEqual(f.frames,[[]]);
});
test('external basic suppressions cannot sneak into a group transaction',async()=>{
 const f=fixture();f.details[0].entry.suppressesBuildingUids=[uid(3)];await assert.rejects(f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,d])),/every suppressed source/);assert.equal(f.pending.length,0);assert.equal(f.stream.detailedModels.size,0);
});
test('a source absent from the basic cache defers activation without mutating the scene',async()=>{
 const f=fixture();f.stream.cache.entries.delete('tile2');assert.equal(await f.stream.setDetailedModels(f.details.map(d=>[d.record.uid,d])),false);assert.equal(f.pending.length,0);assert.equal(f.stream.detailedModels.size,0);
});
test('group declarations cannot be bypassed by either single-model or partial batch calls',async()=>{
 const f=fixture(),members=[uid(1),uid(2)];for(const d of f.details)d.entry.activationGroup=members;
 await assert.rejects(f.stream.setDetailedModel(uid(1),f.details[0]),/atomic/);
 await assert.rejects(f.stream.setDetailedModels([[uid(1),f.details[0]]]),/Incomplete next/);
 for(const d of f.details){d.active=true;f.stream.detailedModels.set(d.record.uid,d);}
 await assert.rejects(f.stream.setDetailedModel(uid(1),null),/atomic/);
 await assert.rejects(f.stream.setDetailedModels([[uid(1),null]]),/Incomplete previous/);
 assert.equal(f.pending.length,0);assert.equal(f.stream.detailedModels.size,2);
});
