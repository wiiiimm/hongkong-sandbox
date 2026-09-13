import test from 'node:test';
import assert from 'node:assert/strict';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../vendor/three.module.js';
import {GLTFLoader} from '../../vendor/GLTFLoader.js';
import {CityStreaming} from '../streaming.js';
import {OfficialModelLayer,MODEL_PROFILES} from '../official-models.js';
import {prepareModelCatalogue,modelBudget,loadOfficialModel,disposeOfficialModel} from '../official-model-assets.js';
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
function fixture(){
 const g=new THREE.BoxGeometry(10,10,10);g.translate(5,7,5);const p=g.attributes.position.array,n=g.attributes.normal.array,c=new Float32Array(p.length).fill(.5),index=g.index.array,arrays=[p,n,c,index],offsets=[];let size=0;
 for(const a of arrays){offsets.push(size);size+=a.byteLength;}const binary=Buffer.alloc(size);arrays.forEach((a,i)=>Buffer.from(a.buffer,a.byteOffset,a.byteLength).copy(binary,offsets[i]));
 const nodes=[{translation:[834500,0,-816500],mesh:0}],materials=[{pbrMetallicRoughness:{baseColorFactor:[.8,.7,.6,1],roughnessFactor:.7,metallicFactor:.1}}];
 const json={asset:{version:'2.0'},scene:0,scenes:[{nodes:[0]}],nodes,materials,buffers:[{byteLength:size}],bufferViews:arrays.map((a,i)=>({buffer:0,byteOffset:offsets[i],byteLength:a.byteLength})),accessors:arrays.map((a,i)=>({bufferView:i,componentType:i===3?5123:5126,count:i===3?a.length:a.length/3,type:i===3?'SCALAR':'VEC3',...(i===0?{min:[0,2,0],max:[10,12,10]}:{})})),meshes:[{primitives:[{attributes:{POSITION:0,NORMAL:1,COLOR_0:2},indices:3,material:0}]}]};
 let text=JSON.stringify(json);text+=' '.repeat((4-Buffer.byteLength(text)%4)%4);const glb=Buffer.alloc(28+Buffer.byteLength(text)+binary.length);glb.writeUInt32LE(0x46546c67,0);glb.writeUInt32LE(2,4);glb.writeUInt32LE(glb.length,8);glb.writeUInt32LE(Buffer.byteLength(text),12);glb.writeUInt32LE(0x4e4f534a,16);glb.write(text,20);const at=20+Buffer.byteLength(text);glb.writeUInt32LE(binary.length,at);glb.writeUInt32LE(0x004e4942,at+4);binary.copy(glb,at+8);const compressed=gzipSync(glb);g.dispose();
 const meta={uid:'landsd/1:0',objectId:1,buildingCSUID:'one',modelId:'B0001',sourceTile:'test',sourceTileRevision:'2026-01-01',worldBounds:[[0,2,0],[10,12,10]],triangles:index.length/3,recordedBaseHeight:2,recordedTopHeight:10,asset:'models/test.glb.gz',encoding:'gzip',bytes:compressed.length,glbBytes:glb.length,decodedGeometryBytes:size,indexedVertices:p.length/3,sha256:createHash('sha256').update(compressed).digest('hex'),priority:'landmark'};
 const catalogue={schemaVersion:1,kind:'official-model-catalogue',crs:'EPSG:2326',verticalDatum:'Hong Kong Principal Datum',rootTranslation:[-834500,0,816500],counts:{packedModels:1},models:[meta]},building={uid:meta.uid,id:'landsd/1',objectId:1,buildingCSUID:'one',tile:'0_0',kind:'yes',base:2,height:8,minimum:0,baseHeightHKPD:2,topHeightHKPD:10,rings:[[[0,0],[10,0],[10,10],[0,10],[0,0]]],centre:[5,5],activity:{profile:1,retailTop:2}};
 const data={id:'0_0',buildings:[building],roads:[],parks:[]},terrain={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta:{georef:{bE:834500,bN:816500,aE:70,aN:-70}}},manifest={tileSize:2000,tiles:[{id:'0_0',url:'tile',bounds:[0,0,2000,2000],centre:[1000,1000]}]};
 const stream=new CityStreaming({manifest,terrain,sampler:{height:()=>2},scene:new THREE.Scene(),activity:{buildings:{[building.uid]:building.activity}}});
 return {catalogue,meta,building,data,stream,compressed,nodes,materials};
}
const response=(data)=>new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});
const camera=()=>{const c=new THREE.PerspectiveCamera(50,1,1,100000);c.position.set(5,10,100);c.lookAt(5,7,5);c.updateProjectionMatrix();return c;};
async function sourceReady(f){f.stream.cache.plan(['0_0']);await f.stream.cache.waitFor(['0_0']);}

test('verified native GLB keeps indexed buffers, source transforms/material provenance and shared city night uniforms',async t=>{
 const f=fixture();t.after(()=>f.stream.cache.close());const meta=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0],r=await loadOfficialModel(meta,f.building,f.stream.lighting,{fetcher:async()=>new Response(f.compressed)});t.after(()=>disposeOfficialModel(r));
 assert.equal(r.record.baseHeightHKPD,2);assert.equal(r.record.topHeightHKPD,10);assert.equal(r.bounds.max.y,12);assert.equal(r.record.modelGeometry.position.constructor,Float64Array);assert.equal(r.meshes[0].geometry.index.count,36);
 assert.deepEqual(r.record.modelSource.originalNodes,f.nodes);assert.deepEqual(r.record.modelSource.originalMaterials,f.materials);assert.deepEqual(r.group.position.toArray(),[-834500,0,816500]);
 assert.deepEqual(Object.keys(r.meshes[0].geometry.attributes).sort(),['color','normal','position']);
 const shader={uniforms:{},vertexShader:'#include <common>\n#include <begin_vertex>',fragmentShader:'#include <common>\n#include <color_fragment>\n#include <emissivemap_fragment>'};r.meshes[0].material.onBeforeCompile(shader);assert.equal(shader.uniforms.uCityNight,f.stream.lighting.night);assert.equal(shader.uniforms.uCityActivity,f.stream.lighting.activity);assert.equal(shader.uniforms.cityLight.value.y,1);assert.match(shader.vertexShader,/uniform vec4 cityLight/);assert.match(shader.fragmentShader,/bedtime/);
 assert.ok(modelBudget(meta).residentBytes>meta.decodedGeometryBytes*2);
});
test('wrong hash, truncated body, altered source UID/heights and incorrect placement all retain fallback',async t=>{
 const f=fixture();t.after(()=>f.stream.cache.close());const meta=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0],fetcher=async()=>new Response(f.compressed);
 for(const [edit,pattern] of [[{sha256:'0'.repeat(64)},/SHA-256/],[{bytes:meta.bytes+1},/byte count/],[{bytes:meta.bytes-1},/exceeds/],[{worldBounds:[[1,2,0],[10,12,10]]},/placement/]])await assert.rejects(loadOfficialModel({...meta,...edit},f.building,f.stream.lighting,{fetcher}),pattern);
 await assert.rejects(loadOfficialModel(meta,{...f.building,buildingCSUID:'wrong'},f.stream.lighting,{fetcher}),/does not match/);await assert.rejects(loadOfficialModel(meta,{...f.building,topHeightHKPD:12},f.stream.lighting,{fetcher}),/does not match/);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.building.height,8);
});
test('progressive detail swaps exact UID rendering/picking/collision and eviction restores its original outline',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});assert.equal(await layer.loadCatalogue('http://localhost/catalogue.json'),true);
 const c=camera();assert.deepEqual(layer.plan(c,{viewportHeight:800,force:true}),[f.meta.uid]);await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);
 assert.equal(f.stream.cache.entries.get('0_0').buildings.group.children.length,0);assert.equal(f.stream.maximumRoof(5,5,1),12);assert.equal(f.stream.getLoadedBuilding(f.meta.uid).modelId,f.meta.modelId);
 entry.group.updateMatrixWorld(true);const ray=new THREE.Raycaster(new THREE.Vector3(5,30,5),new THREE.Vector3(0,-1,0)),hit=ray.intersectObjects(f.stream.pickMeshes(ray.ray))[0];assert.ok(hit);assert.equal(f.stream.featureAt(hit).uid,f.meta.uid);assert.equal(f.stream.featureAt(hit).topHeightHKPD,10);
 f.stream.buildings.visible=false;assert.equal(f.stream.pickMeshes(ray.ray).length,0);f.stream.buildings.visible=true;
 let disposed=0;entry.meshes[0].geometry.addEventListener('dispose',()=>disposed++);c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);assert.equal(disposed,1);assert.equal(layer.stats.cached,0);
});
test('failed model download uses Retry and only activates detail after successful verification',async t=>{
 const f=fixture();let failed=true;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?(failed?new Response('',{status:503}):new Response(f.compressed)):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await assert.rejects(layer.cache.waitFor([f.meta.uid]),/503/);assert.equal(f.stream.detailedModels.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
 while(layer.cache.running.size)await tick();failed=false;await layer.retry();await layer.cache.waitFor([f.meta.uid]);assert.equal(f.stream.maximumRoof(5,5,1),12);assert.equal(layer.stats.errors.length,0);
});
test('camera travel cancels a pending source request; late completion cannot replace the fallback',async t=>{
 const f=fixture();let release;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?new Promise(resolve=>{release=resolve;}):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});while(!release)await tick();c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});release(new Response(f.compressed));while(layer.cache.running.size)await tick();assert.equal(f.stream.detailedModels.size,0);assert.equal(layer.cache.entries.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
});
test('catalogues reject ambiguous duplicate IDs, wrong datum, invalid assembly suppressions and external decoder assets',()=>{
 const f=fixture();try{
  assert.throws(()=>prepareModelCatalogue({...f.catalogue,verticalDatum:'sea level'},'http://localhost/c.json'),/catalogue/);
  assert.throws(()=>prepareModelCatalogue({...f.catalogue,counts:{packedModels:2},models:[f.meta,f.meta]},'http://localhost/c.json'),/entry/);
  for(const suppressesBuildingUids of [[f.meta.uid],['landsd/2:0','landsd/2:0'],['bad']])assert.throws(()=>prepareModelCatalogue({...f.catalogue,models:[{...f.meta,suppressesBuildingUids}]},'http://localhost/c.json'),/assembly suppression/);
  assert.throws(()=>prepareModelCatalogue({...f.catalogue,models:[{...f.meta,asset:'https://other.test/a.glb.gz'}]},'http://localhost/c.json'),/origin/);
 }finally{f.stream.cache.close();}
});
test('planner respects geometry, collision-memory, count and triangle budgets without rebaking on each camera frame',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async()=>response(f.catalogue));let loads=0;
 const stub={lighting:f.stream.lighting,detailedModels:new Map(),getLoadedBuilding:()=>f.building,setDetailedModel:async()=>true};
 const layer=new OfficialModelLayer({stream:stub,loadAsset:async()=>{loads++;throw new Error('fixture hold');}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');
 for(let i=2;i<70;i++)layer.models.set(`landsd/${i}:0`,{...layer.models.get(f.meta.uid),uid:`landsd/${i}:0`,decodedGeometryBytes:2*1024*1024,triangles:30000,indexedVertices:10000});
 const c=camera(),wanted=layer.plan(c,{force:true}),cost=wanted.map(uid=>modelBudget(layer.models.get(uid))).reduce((a,b)=>({geometryBytes:a.geometryBytes+b.geometryBytes,residentBytes:a.residentBytes+b.residentBytes,triangles:a.triangles+b.triangles}),{geometryBytes:0,residentBytes:0,triangles:0});
 assert.ok(wanted.length<=MODEL_PROFILES.mobile.count);for(const k of ['geometryBytes','residentBytes','triangles'])assert.ok(cost[k]<=MODEL_PROFILES.mobile[k]);assert.ok(wanted.length<layer.models.size);for(let i=0;i<100;i++)layer.plan(c,{now:0});assert.ok(layer.cache.running.size<=1);assert.equal(f.stream.detailedModels.size,0);
});

test('abort during asynchronous GLTF parsing disposes the late source geometry',async t=>{
 const f=fixture();t.after(()=>f.stream.cache.close());const meta=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0],controller=new AbortController();let finish,parsed;
 const pending=loadOfficialModel(meta,f.building,f.stream.lighting,{signal:controller.signal,fetcher:async()=>new Response(f.compressed),loader:{parseAsync:async bytes=>{parsed=await new GLTFLoader().parseAsync(bytes,'');await new Promise(resolve=>{finish=resolve;});return parsed;}}});
 const rejected=assert.rejects(pending,{name:'AbortError'});while(!finish)await tick();let disposed=0;parsed.scene.traverse(o=>{if(o.isMesh)o.geometry.addEventListener('dispose',()=>disposed++);});controller.abort();finish();await rejected;assert.equal(disposed,1);assert.equal(f.stream.detailedModels.size,0);
});
test('failed fallback restoration retains source geometry and its memory reservation until Retry succeeds',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?new Response(f.compressed):response(f.catalogue));await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);let disposed=0;entry.meshes[0].geometry.addEventListener('dispose',()=>disposed++);
 const restore=f.stream.refreshBuildings.bind(f.stream);let fail=true;t.mock.method(f.stream,'refreshBuildings',async()=>{if(fail)throw new Error('fixture bake failure');return restore();});c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});await Promise.allSettled([...layer.retiring.values()]);
 assert.equal(disposed,0);assert.equal(f.stream.detailedModels.get(f.meta.uid),entry);assert.ok(layer.stats.residentBytes>0);assert.deepEqual(layer.stats.errors,['restore:'+f.meta.uid]);
 fail=false;await layer.retry();assert.equal(disposed,1);assert.equal(f.stream.detailedModels.size,0);assert.equal(layer.stats.residentBytes,0);assert.equal(layer.stats.errors.length,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
});
test('pre-existing baked government models and source infrastructure take precedence over optional compact detail',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');await f.stream.suppressInfrastructureBuildings([f.meta.uid]);assert.deepEqual(layer.plan(camera(),{force:true}),[]);
 await f.stream.suppressInfrastructureBuildings([]);f.stream.cache.entries.get('0_0').data.buildings[0].modelGeometry={position:[0,0,0]};assert.deepEqual(layer.plan(camera(),{force:true}),[]);
});
test('turning away briefly retains nearby decoded detail without another model or material bake',async t=>{
 const f=fixture();let downloads=0;t.mock.method(globalThis,'fetch',async url=>{if(url==='tile')return response(f.data);if(String(url).endsWith('.gz')){downloads++;return new Response(f.compressed);}return response(f.catalogue);});await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid),mesh=entry.meshes[0],fallback=f.stream.cache.entries.get('0_0').buildings.group;
 c.lookAt(5,10,1000);layer.plan(c,{force:true});c.lookAt(5,7,5);layer.plan(c,{force:true});assert.equal(layer.cache.entries.get(f.meta.uid).meshes[0],mesh);assert.equal(f.stream.cache.entries.get('0_0').buildings.group,fallback);assert.equal(downloads,1);
});

test('cancellation during fallback rebake never attaches a late source model',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):new Response(f.compressed));await sourceReady(f);
 const meta=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0],entry=await loadOfficialModel(meta,f.building,f.stream.lighting,{fetcher:async()=>new Response(f.compressed)}),controller=new AbortController();t.after(()=>{disposeOfficialModel(entry);f.stream.cache.close();});
 const pending=f.stream.setDetailedModel(f.meta.uid,entry,{signal:controller.signal});controller.abort();assert.equal(await pending,false);assert.equal(entry.active,false);assert.equal(entry.group.parent,null);assert.equal(f.stream.detailedModels.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);
});

// Opaque landmark shells must retain source materials without invented windows.
test('catalogue window opt-out preserves geometry and default building lighting',async t=>{
 const f=fixture();t.after(()=>f.stream.cache.close());
 for(const setting of [undefined,false]){
  const catalogue={...f.catalogue,models:[{...f.meta,proceduralWindows:setting}]};
  const meta=prepareModelCatalogue(catalogue,'http://localhost/catalogue.json')[0];
  const result=await loadOfficialModel(meta,f.building,f.stream.lighting,{fetcher:async()=>new Response(f.compressed)});
  const shader={uniforms:{},vertexShader:'#include <common>\n#include <begin_vertex>',fragmentShader:'#include <common>\n#include <color_fragment>\n#include <emissivemap_fragment>'};
  result.meshes[0].material.onBeforeCompile(shader);
  assert.equal(shader.uniforms.cityWindows.value,setting===false?0:1);
  assert.equal(result.bounds.max.y,12);
  assert.deepEqual(result.record.modelSource.originalMaterials,f.materials);
  disposeOfficialModel(result);
 }
});

test('real source-tile replacement activates a tower only after its native support and retires tower first',async t=>{
 const f=fixture(),supportUid='landsd/2:0';f.meta.supportDependencies=[{uid:supportUid,state:'candidate'}];
 f.catalogue.models.push({...f.meta,uid:supportUid,objectId:2,buildingCSUID:'two',modelId:'B0002',supportDependencies:[]});f.catalogue.counts.packedModels=2;
 f.data.buildings.push({...f.building,uid:supportUid,id:'landsd/2',objectId:2,buildingCSUID:'two'});
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const events=[],replace=f.stream.setDetailedModel.bind(f.stream);t.mock.method(f.stream,'setDetailedModel',async(uid,value,options)=>{
  if(uid===f.meta.uid&&value)assert.equal(f.stream.detailedModels.get(supportUid)?.active,true);
  if(uid===supportUid&&!value)assert.equal(f.stream.detailedModels.has(f.meta.uid),false);
  const result=await replace(uid,value,options);events.push((value?'add:':'remove:')+uid);return result;
 });
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');
 const c=camera();assert.deepEqual(layer.plan(c,{force:true,selectedUid:f.meta.uid}),[supportUid,f.meta.uid]);await layer.cache.waitFor([f.meta.uid]);assert.equal(f.stream.detailedModels.size,2);
 c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);assert.equal(f.stream.detailedModels.size,0);
 assert.deepEqual(events,['add:'+supportUid,'add:'+f.meta.uid,'remove:'+f.meta.uid,'remove:'+supportUid]);
});


test('an active government assembly hides its bundled fallback forms and restores them on eviction',async t=>{
 const f=fixture(),bundledUid='landsd/2:0';f.catalogue.models[0].suppressesBuildingUids=[bundledUid];
 f.data.buildings.push({...f.building,uid:bundledUid,id:'landsd/2',objectId:2,buildingCSUID:'two',rings:[[[20,0],[30,0],[30,10],[20,10],[20,0]]],centre:[25,5]});
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):String(url).endsWith('.gz')?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');
 assert.ok(f.stream.collision(25,5,2,11,1));const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);
 assert.equal(f.stream.collision(25,5,2,11,1),null);assert.equal(f.stream.cache.entries.get('0_0').detailSuppressions.has(bundledUid),true);
 c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);assert.ok(f.stream.collision(25,5,2,11,1));
});
