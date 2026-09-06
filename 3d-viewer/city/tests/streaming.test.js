import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {TileCache,nearbyTiles} from '../tile-cache.js';
const next=()=>new Promise(resolve=>setTimeout(resolve,0));
function harness(options={}){
 const deferred=new Map(),disposed=[],loads=[];
 const cache=new TileCache({concurrency:2,limit:3,...options,load:(id,signal)=>{loads.push(id);return new Promise((resolve,reject)=>deferred.set(id,{resolve,reject,signal}));},dispose:v=>disposed.push(v)});
 return {cache,deferred,disposed,loads};
}
test('late completion after travelling away is disposed, never attached',async()=>{
 const {cache,deferred,disposed}=harness();cache.plan(['central']);await next();cache.plan(['lantau']);await next();
 assert.equal(deferred.get('central').signal.aborted,true);
 deferred.get('central').resolve('central geometry');deferred.get('lantau').resolve('lantau geometry');await next();
 assert.equal(cache.entries.has('central'),false);assert.equal(cache.entries.get('lantau'),'lantau geometry');assert.deepEqual(disposed,['central geometry']);cache.close();
});
test('a failed section blocks readiness until an explicit retry succeeds',async()=>{
 const {cache,deferred}=harness();cache.plan(['a']);await next();const wait=assert.rejects(cache.waitFor(['a']),/offline/);
 deferred.get('a').reject(new Error('offline'));await wait;assert.equal(cache.ready(['a']),false);cache.retry();await next();deferred.get('a').resolve('a');await cache.waitFor(['a']);assert.equal(cache.ready(['a']),true);cache.close();
});
test('district changes cancel the old arrival request',async()=>{
 const {cache}=harness();cache.plan(['a']);const wait=assert.rejects(cache.waitFor(['a']),{name:'AbortError'});cache.plan(['b']);await wait;cache.close();
});
test('cache evicts old geometry and never launches more than its concurrency',async()=>{
 const {cache,deferred,disposed,loads}=harness();cache.plan(['a','b','c']);await next();assert.equal(loads.length,2);
 deferred.get('a').resolve('a');deferred.get('b').resolve('b');await next();deferred.get('c').resolve('c');await cache.waitFor(['a','b','c']);
 cache.plan(['d','e']);await next();assert.ok(cache.entries.size+cache.running.size<=3);deferred.get('d').resolve('d');deferred.get('e').resolve('e');await cache.waitFor(['d','e']);assert.ok(cache.entries.size<=3);assert.ok(disposed.length>=2);cache.close();
});
test('large footprints are selected by their bounds across tile edges',()=>{
 const t=[{id:'wide',bounds:[0,0,4500,100],centre:[1000,1000]},{id:'far',bounds:[9000,9000,10000,10000],centre:[9500,9500]}];assert.deepEqual(nearbyTiles(t,4400,40,30),['wide']);
});
const manifest=JSON.parse(readFileSync(new URL('../data/manifest.json',import.meta.url)));
test('expanded dataset has unique building ownership, complete source provenance and valid tile bounds',()=>{
 assert.ok(manifest.counts.buildings>40000);assert.equal(manifest.sources.length,5);assert.ok(manifest.sources.every(s=>/^[a-f0-9]{64}$/.test(s.sha256)));
 const ids=new Set();let total=0;
 for(const meta of manifest.tiles){
  const data=JSON.parse(readFileSync(new URL(`../data/tiles/${meta.id}.json`,import.meta.url)));assert.equal(data.id,meta.id);assert.equal(data.buildings.length,meta.counts.buildings);
  for(const b of data.buildings){assert.equal(ids.has(b.uid),false);ids.add(b.uid);assert.equal(b.tile,meta.id);assert.ok(b.height>b.minimum);for(const [x,z] of b.rings[0])assert.ok(x>=meta.bounds[0]&&x<=meta.bounds[2]&&z>=meta.bounds[1]&&z<=meta.bounds[3]);}
  total+=data.buildings.length;
 }
 assert.equal(total,manifest.counts.buildings);
});
test('all new destination regions have nearby building geometry',()=>{
 for(const [x,z] of [[956,-3511],[4151,-399],[8068,2479],[-487,4252],[5390,7684],[-22436,-197],[-30585,3554],[-16462,2469],[-14706,-1183]]){
  const ids=nearbyTiles(manifest.tiles,x,z,800);const count=manifest.tiles.filter(t=>ids.includes(t.id)).reduce((n,t)=>n+t.counts.buildings,0);assert.ok(count>20,`No settlement buildings near ${x},${z}`);
 }
});
