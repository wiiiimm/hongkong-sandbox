import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {TileCache,nearbyTiles} from '../tile-cache.js';
import {PLACES,REGIONS} from '../places.js';
import {BuildingIndex,makeTerrainSampler} from '../geo.js';
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
 assert.ok(manifest.counts.buildings>110000);
 const regions=JSON.parse(readFileSync(new URL('../../../source-scripts/city/regions.json',import.meta.url)));
 assert.deepEqual(new Set(manifest.sources.map(s=>s.id)),new Set(['central',...regions.map(r=>r.id)]));
 assert.ok(manifest.boundarySource?.id==='relation/913110');assert.match(manifest.boundarySource.sha256,/^[a-f0-9]{64}$/);assert.ok(manifest.sources.every(s=>/^[a-f0-9]{64}$/.test(s.sha256)));
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

test('all 18 districts have direct settlement destinations and valid WGS84 sky observer coordinates',()=>{
 const districtPlaces=['central','wanchai','northpoint','aberdeen','kowloon','shamshuipo','kowlooncity','wongtaisin','kowloonbay','tsuenwan','tsingyi','tuenmun','yuenlong','sheungshui','taipo','shatin','saikung','lantau'];
 for(const id of districtPlaces){const p=PLACES[id];assert.ok(p,id);assert.ok(REGIONS[p.region]);const ids=nearbyTiles(manifest.tiles,...p.spawn,800);assert.ok(manifest.tiles.filter(t=>ids.includes(t.id)).reduce((n,t)=>n+t.counts.buildings,0)>20,`No settlement geometry at ${id}`);}
 for(const [id,p] of Object.entries(PLACES)){assert.ok(p.lat>22.1&&p.lat<22.6,id);assert.ok(p.lon>113.8&&p.lon<114.5,id);}
});
test('all walking arrivals lie on dry terrain triangles and clear nearby building collision volumes',()=>{
 const terrain=JSON.parse(readFileSync(new URL('../data/terrain.json',import.meta.url)));terrain.patches=(manifest.terrainPatches||[]).map(p=>JSON.parse(readFileSync(new URL('../../'+p.url,import.meta.url))));const sampler=makeTerrainSampler(terrain);
 const landTriangle=(x,z)=>{const data=terrain.patches.find(p=>makeTerrainSampler(p).contains(x,z))||terrain;const [c,r]=makeTerrainSampler(data).grid(x,z),i=Math.floor(c),j=Math.floor(r),u=c-i,v=r-j,w=data.w;const cells=u+v<=1?[j*w+i,j*w+i+1,(j+1)*w+i]:[j*w+i+1,(j+1)*w+i,(j+1)*w+i+1];return cells.every(index=>data.elev[index]>0);};
 for(const [id,p] of Object.entries(PLACES)){
  if(p.aerialOnly)continue;
  const [x,z]=p.spawn;assert.ok(sampler.contains(x,z),id);assert.ok(sampler.raw(x,z)>.5,id);assert.ok(landTriangle(x,z),`${id} starts on a fully dry terrain triangle`);
  const ids=nearbyTiles(manifest.tiles,x,z,10);
  const buildings=manifest.tiles.filter(t=>ids.includes(t.id)).flatMap(t=>JSON.parse(readFileSync(new URL(`../data/tiles/${t.id}.json`,import.meta.url))).buildings);
  if(id!=='lantaupeaks'&&!p.sectionId)assert.ok(buildings.length>0,`No geometry at ${id}`);const index=new BuildingIndex(buildings),y=sampler.height(x,z);
  assert.equal(index.collision(x,z,y,y+1.8,.55),null,`Arrival overlaps a building at ${id}`);
 }
});
