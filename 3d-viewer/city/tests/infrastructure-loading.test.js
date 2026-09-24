import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {BridgeLayer,geometryFor} from '../bridges.js';
import {prepareInfrastructure} from '../infrastructure-data.js';
import {clippedProxyParts,validateProxyClips,retainedRoads} from '../infrastructure-replacements.js';
import {CityStreaming} from '../streaming.js';
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
const response=data=>({ok:true,json:async()=>structuredClone(data)});
const proxy={id:'way/10',source:'https://www.openstreetmap.org/way/10',kind:'footway',width:2,bounds:[0,-1,20,11],deckPath:[[0,4,0],[10,6,0],[10,8,10],[20,10,10]],estimatedElevation:true};
const clip={id:proxy.id,source:proxy.source,originalLengthMetres:30,retainedLengthMetres:12,replacedLengthMetres:18,keepPaths:[[[0,0],[6,0]],[[14,10],[20,10]]],policy:'Reviewed original path minus exact source projection; retained endpoints are derived.'};
function source(id='official/test'){
 const g=geometryFor({...proxy,deckPath:[[6,5.2,0],[10,6,0],[10,8,10],[14,8.8,10]]}),b=g.boundingBox;
 const r={id,sourceUrl:'https://example.gov.hk/source',worldBounds:[b.min.toArray(),b.max.toArray()],modelGeometry:{position:Array.from(g.attributes.position.array),normal:Array.from(g.attributes.normal.array),colour:new Array(g.attributes.position.array.length).fill(.5)},walkable:false,walkTriangleIndices:[],suppresses:[],suppressesBuildingUids:['landsd/1:0'],buildingMatches:[{uid:'landsd/1:0',objectId:1,buildingCSUID:'exact-csuid',policy:'Exact source identity and reviewed footprint overlap.'}]};g.dispose();return r;
}
const inventory=(options={})=>({schemaVersion:1,kind:'official-infrastructure',crs:'EPSG:2326',verticalDatum:'Hong Kong Principal Datum',models:[source()],proxyClips:[structuredClone(clip)],...options});
const layer=()=>new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>2},prepare:data=>data});
function pick(detail,x,z){detail.group.updateMatrixWorld(true);const ray=new THREE.Raycaster(new THREE.Vector3(x,30,z),new THREE.Vector3(0,-1,0));return ray.intersectObjects(detail.pickMeshes()).map(hit=>detail.featureAt(hit));}

test('retained proxy endpoints interpolate original height and preserve intervening corners',()=>{
 const c={...clip,retainedLengthMetres:20,replacedLengthMetres:10,keepPaths:[[[5,0],[10,0],[10,10],[15,10]]]};
 assert.deepEqual(clippedProxyParts(proxy,c)[0].deckPath,[[5,5,0],[10,6,0],[10,8,10],[15,9,10]]);
 assert.throws(()=>clippedProxyParts(proxy,{...c,keepPaths:[[[5,0],[15,10]]]}),/corners/);
 assert.throws(()=>clippedProxyParts(proxy,{...clip,keepPaths:[[[.1,.1],[6,0]]]}),/leaves original path/);
 assert.throws(()=>clippedProxyParts(proxy,{...clip,keepPaths:[[[6,0],[0,0]]]}),/direction/);
 assert.throws(()=>validateProxyClips([{...clip,retainedLengthMetres:14}]),/lengths/);
 assert.throws(()=>validateProxyClips([{...clip,keepPaths:[]}]),/Invalid/);
 assert.deepEqual(proxy.deckPath,[[0,4,0],[10,6,0],[10,8,10],[20,10,10]]);
});
for(const order of ['source first','proxy first'])test(`partial proxy replacement, source picking and tower activation: ${order}`,async t=>{
 const detail=layer();t.after(()=>detail.dispose());t.mock.method(globalThis,'fetch',async url=>response(url==='source'?inventory():[proxy]));
 const first=order==='source first'?'source':'proxy',second=first==='source'?'proxy':'source';
 assert.equal(await detail.load(first),true);
 if(first==='source'){assert.equal(detail.proxyClips.size,0);assert.equal(detail.loadedIds.has(proxy.id),false);assert.deepEqual([...detail.suppressedBuildingUids],['landsd/1:0']);}
 assert.equal(await detail.load(second),true);assert.equal(detail.proxyClips.size,1);assert.equal(detail.renderParts(proxy).length,2);
 assert.equal(pick(detail,2,0)[0].id,proxy.id);assert.equal(pick(detail,18,10)[0].id,proxy.id);assert.equal(pick(detail,10,5)[0].id,'official/test');
 assert.ok(pick(detail,10,5).every(r=>r.id!=='way/10'),'proxy middle has actually gone');
 const highlight=detail.geometryFor(proxy);assert.equal(highlight.attributes.position.count,72);highlight.dispose();
 assert.equal(detail.surfaces.heights(10,5).length,0,'visual source is never made walkable');
 assert.ok(detail.surfaces.collision(10,5,0,15,.55),'original source still collides');
 assert.equal(await detail.load('source'),true);assert.equal(detail.stats.sourceModels,1);
});
test('failed and malformed complete source packages preserve all fallbacks and Retry activates the replacement',async t=>{
 const detail=layer();t.after(()=>detail.dispose());let fault='network';
 t.mock.method(globalThis,'fetch',async url=>{
  if(url==='proxy')return response([proxy]);if(fault==='network')return{ok:false,status:503};
  const d=inventory();if(fault==='second-model'){const bad=source('bad');bad.modelGeometry.position[0]=null;d.models.push(bad);}
  if(fault==='off-path'){d.proxyClips[0].keepPaths[0]=[[0,.1],[6,.1]];}
  return response(d);
 });
 await detail.load('proxy');const mesh=detail.pickMeshes()[0];
 for(const failure of ['network','second-model','off-path']){fault=failure;assert.equal(await detail.load('source'),false);assert.equal(detail.suppressedBuildingUids.size,0);assert.equal(detail.proxyClips.size,0);assert.equal(detail.surfaces.models.size,0);assert.equal(detail.pickMeshes()[0],mesh);assert.equal(detail.renderParts(proxy).length,1);}
 fault=null;assert.equal(await detail.retry(),true);assert.equal(detail.suppressedBuildingUids.size,1);assert.equal(detail.renderParts(proxy).length,2);
});
test('duplicate conflicting source meshes cannot activate additional tower suppression',async t=>{
 const detail=layer();t.after(()=>detail.dispose());let bad=false;
 t.mock.method(globalThis,'fetch',async()=>{const d=inventory({proxyClips:[]});if(bad){d.models[0].modelGeometry.colour[0]=.9;d.models[0].suppressesBuildingUids=['landsd/2:0'];d.models[0].buildingMatches=[{uid:'landsd/2:0',objectId:2,buildingCSUID:'two',policy:'Reviewed.'}];}return response(d);});
 assert.equal(await detail.load('one'),true);bad=true;assert.equal(await detail.load('two'),false);assert.deepEqual([...detail.suppressedBuildingUids],['landsd/1:0']);
});
test('late official completion after disposal cannot hide roads or building outlines',async t=>{
 const detail=layer();let release;t.mock.method(globalThis,'fetch',()=>new Promise(resolve=>{release=resolve;}));
 const loading=detail.load('source');await tick();detail.dispose();release(response(inventory()));assert.equal(await loading,false);assert.equal(detail.suppressedBuildingUids.size,0);assert.equal(detail.pendingProxyClips.size,0);assert.equal(detail.loadedIds.size,0);
});
test('road tails are retained from verified paths across tile seams, including road-only proxies',async t=>{
 const straight={...clip,originalLengthMetres:20,retainedLengthMetres:10,replacedLengthMetres:10,keepPaths:[[[5,2],[10,2],[15,2]]]};
 const road={id:'way/10',kind:'unclassified',bridge:true,layer:2,path:[[0,2],[20,2]],tags:{foot:'no'}};
 const left=retainedRoads([road],new Map([[road.id,straight]]),[0,0,10,10]),right=retainedRoads([road],new Map([[road.id,straight]]),[10,0,20,10]);
 assert.deepEqual(left[0].path,[[5,2],[10,2]]);assert.deepEqual(right[0].path,[[10,2],[15,2]]);assert.equal(left[0].tags,road.tags);
 const detail=new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>2}});t.after(()=>detail.dispose());
 t.mock.method(globalThis,'fetch',async url=>response(url==='source'?inventory({proxyClips:[straight]}):{schemaVersion:1,bridges:[{...road,source:proxy.source,role:'bridge'}]}));
 assert.equal(await detail.load('source'),true);assert.equal(detail.proxyClips.size,0);assert.equal(await detail.load('roads'),true);assert.equal(detail.proxyClips.size,1);assert.equal(detail.records.has(road.id),false);assert.equal(detail.loadedIds.has(road.id),false,'street renderer retains clipped road tails');
});
function streamFixture(){
 const buildings=[1,2].map((n)=>({uid:`landsd/${n}:0`,id:`landsd/${n}`,tile:'0_0',kind:'yes',base:2,height:12,minimum:0,rings:[[[n*20,0],[n*20+10,0],[n*20+10,10],[n*20,10],[n*20,0]]],centre:[n*20+5,5]}));
 const data={id:'0_0',buildings,roads:[],parks:[]},manifest={tileSize:2000,tiles:[{id:'0_0',url:'tile',bounds:[0,0,2000,2000],centre:[1000,1000]}]},terrain={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta:{georef:{bE:834500,bN:816500,aE:70,aN:-70}}};
 return {data,stream:new CityStreaming({manifest,terrain,sampler:{height:()=>2},scene:new THREE.Scene(),activity:{buildings:{}}})};
}
async function ready(stream){stream.cache.plan(['0_0']);await stream.cache.waitFor(['0_0']);return stream.cache.entries.get('0_0');}
test('cached tower outline suppression swaps collision and render buffers, preserves source picking and restores fallback',async t=>{
 const {stream,data}=streamFixture();t.after(()=>stream.cache.close());t.mock.method(globalThis,'fetch',async()=>response(data));const entry=await ready(stream),original=entry.data.buildings.map(b=>structuredClone(b));
 let disposed=0;entry.buildings.group.children.forEach(m=>m.geometry.addEventListener('dispose',()=>disposed++));
 const loading=stream.suppressInfrastructureBuildings(['landsd/1:0']);assert.equal(stream.collision(25,5,2,4)?.uid,'landsd/1:0','fallback remains until rebake finishes');await loading;
 assert.equal(stream.collision(25,5,2,4),null);assert.equal(stream.collision(45,5,2,4)?.uid,'landsd/2:0');assert.ok(disposed>0);
 const mesh=entry.buildings.group.children[0];assert.equal(mesh.geometry.attributes.feature.getX(0),1);assert.equal(stream.featureAt({object:mesh,face:{a:0}}).uid,'landsd/2:0');assert.equal(stream.stats.suppressedBuildings,1);assert.deepEqual(entry.data.buildings,original);
 assert.equal((await stream.getBuilding('0_0','landsd/1:0')).uid,'landsd/1:0');await stream.suppressInfrastructureBuildings([]);assert.equal(stream.collision(25,5,2,4)?.uid,'landsd/1:0');assert.equal(stream.stats.suppressedBuildings,0);
});
test('suppression is applied to future tiles; latest selection wins during a pending rebake',async t=>{
 const {stream,data}=streamFixture();t.after(()=>stream.cache.close());t.mock.method(globalThis,'fetch',async()=>response(data));await stream.suppressInfrastructureBuildings(['landsd/1:0']);const entry=await ready(stream);assert.equal(entry.suppressedBuildings,1);assert.equal(stream.collision(25,5,2,4),null);
 const restoring=stream.suppressInfrastructureBuildings([]),resuppressing=stream.suppressInfrastructureBuildings(['landsd/2:0']);await Promise.all([restoring,resuppressing]);assert.equal(stream.collision(25,5,2,4)?.uid,'landsd/1:0');assert.equal(stream.collision(45,5,2,4),null);assert.equal(entry.suppressedBuildings,1);
});
test('tile eviction during a replacement bake disposes late buffers instead of reattaching them',async t=>{
 const {stream,data}=streamFixture();t.mock.method(globalThis,'fetch',async()=>response(data));await ready(stream);const pending=stream.suppressInfrastructureBuildings(['landsd/1:0']);stream.cache.close();await assert.rejects(pending,{name:'AbortError'});assert.equal(stream.buildings.children.length,0);assert.equal(stream.cache.entries.size,0);
});

test('curated public approaches keep their own geometry when their parent mapped way is clipped',async t=>{
 const detail=layer();t.after(()=>detail.dispose());
 const approach={...proxy,id:'public-approach',deckPath:[[7,5.4,0],[10,6,0]],walkable:true,estimatedPublicApproach:true,publicAccessSource:'https://example.gov.hk/public-path',elevationBasis:'Explicit estimated public landing.',widthBasis:'Explicit estimated width.'};
 t.mock.method(globalThis,'fetch',async url=>response(url==='source'?inventory({approaches:[approach]}):[proxy]));
 assert.equal(await detail.load('source'),true);assert.equal(detail.proxyClips.size,0);assert.equal(await detail.load('proxy'),true);
 assert.equal(detail.renderParts(detail.records.get(approach.id)).length,1);assert.equal(detail.renderParts(proxy).length,2);assert.ok(detail.surfaces.heights(8,0).length);
});
test('fully suppressed tiles release even unused facade materials on cache disposal',async t=>{
 const {stream,data}=streamFixture();t.mock.method(globalThis,'fetch',async()=>response(data));await stream.suppressInfrastructureBuildings(data.buildings.map(b=>b.uid));const entry=await ready(stream);assert.equal(entry.buildings.group.children.length,0);
 let disposed=0;for(const m of entry.buildings.materials)m.addEventListener('dispose',()=>disposed++);stream.cache.close();assert.equal(disposed,8);
});

test('declared complete package counts reject a missing deck half, and empty source meshes cannot hide outlines',()=>{
 const second=source('second');second.suppressesBuildingUids=[];
 const d=inventory({models:[source(),second],counts:{models:2}});assert.equal(prepareInfrastructure(d).length,2);d.models.pop();assert.throws(()=>prepareInfrastructure(d),/Incomplete source infrastructure count models/);
 const empty=source();empty.modelGeometry.position.fill(0);empty.worldBounds=[[0,0,0],[0,0,0]];assert.throws(()=>prepareInfrastructure(inventory({models:[empty]})),/Empty source infrastructure surface/);
});
