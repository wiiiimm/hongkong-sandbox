import test from 'node:test';
import assert from 'node:assert/strict';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../vendor/three.module.js';
import {GLTFLoader} from '../../vendor/GLTFLoader.js';
import {CityStreaming} from '../streaming.js';
import {OfficialModelLayer,MODEL_PROFILES} from '../official-models.js';
import {prepareModelCatalogue,modelBudget,loadOfficialModel,disposeOfficialModel} from '../official-model-assets.js';
import {sourceMetadataHash} from '../model-variants.js';
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
const modelRequest=url=>{try{return new URL(url).pathname.endsWith('.gz');}catch{return false;}};
const response=(data)=>new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});
const camera=()=>{const c=new THREE.PerspectiveCamera(50,1,1,100000);c.position.set(5,10,100);c.lookAt(5,7,5);c.updateProjectionMatrix();return c;};
async function sourceReady(f){f.stream.cache.plan(['0_0']);await f.stream.cache.waitFor(['0_0']);}
const repeat=c=>c.repeat(64);
async function variantDescriptor(f,{asset='variants/quality.glb.gz',bytes=f.compressed,glbBytes=f.meta.glbBytes,tier='balanced',variantId=repeat('b')}={}){
 const gates=Object.fromEntries(['sourceIdentity','geometry','placement','visual','collision','devicePerformance'].map(g=>[g,'passed']));
 return {uid:f.meta.uid,runtimeVersion:1,status:'approved',sourceSha256:f.meta.sha256,sourceMetadataSha256:await sourceMetadataHash(f.meta,f.catalogue),variantId,revisionId:repeat('c'),recipeSha256:repeat('d'),sha256:createHash('sha256').update(bytes).digest('hex'),tier,codec:'none',collisionPolicy:'validated-variant',lossy:true,bytes:bytes.length,glbBytes,decodedGeometryBytes:f.meta.decodedGeometryBytes,triangles:f.meta.triangles,indexedVertices:f.meta.indexedVertices,encoding:'gzip',asset,minPixels:0,maxPixels:1000000,worldBounds:f.meta.worldBounds,maxPositionErrorMetres:0,approval:{artifactSha256:createHash('sha256').update(bytes).digest('hex'),gates}};
}
function fakeEntry(meta,building){
 return {entry:meta,record:{...building,uid:meta.uid,modelGeometry:{position:new Float64Array(),index:new Uint32Array(),triangles:0,worldBounds:meta.worldBounds},modelSource:{}},group:new THREE.Group(),meshes:[],active:false,budget:{...modelBudget(meta),drawCalls:1}};
}
function fakeStreamingSwaps(stream){
 stream.sync=()=>{};
 stream.setDetailedModel=async(uid,value,{signal}={})=>{
  if(signal?.aborted)return false;const old=stream.detailedModels.get(uid);
  if(old&&old!==value){old.active=false;old.group.visible=false;}
  if(value){value.active=true;value.group.visible=true;stream.detailedModels.set(uid,value);}else stream.detailedModels.delete(uid);
  return true;
 };
}
function withGLTFExtensions(compressed,used,required=[],images=null){
 const glb=gunzipSync(compressed),jsonLength=glb.readUInt32LE(12),json=JSON.parse(glb.toString('utf8',20,20+jsonLength));
 json.extensionsUsed=used;if(required.length)json.extensionsRequired=required;if(images)json.images=images;
 const jsonText=JSON.stringify(json),jsonChunk=Buffer.from(jsonText+' '.repeat((4-Buffer.byteLength(jsonText)%4)%4)),binaryAt=20+jsonLength,binaryLength=glb.readUInt32LE(binaryAt),binary=glb.subarray(binaryAt+8,binaryAt+8+binaryLength);
 const output=Buffer.alloc(12+8+jsonChunk.length+8+binary.length);output.writeUInt32LE(0x46546c67,0);output.writeUInt32LE(2,4);output.writeUInt32LE(output.length,8);output.writeUInt32LE(jsonChunk.length,12);output.writeUInt32LE(0x4e4f534a,16);jsonChunk.copy(output,20);
 const next=binaryAt+(jsonChunk.length-jsonLength);output.writeUInt32LE(binary.length,next);output.writeUInt32LE(0x004e4942,next+4);binary.copy(output,next+8);return output;
}

test('verified native GLB keeps indexed buffers, source transforms/material provenance and shared city night uniforms',async t=>{
 const f=fixture();t.after(()=>f.stream.cache.close());const meta=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];assert.equal(new URL(meta.assetURL).searchParams.get('v'),f.meta.sha256);const r=await loadOfficialModel(meta,f.building,f.stream.lighting,{fetcher:async()=>new Response(f.compressed)});t.after(()=>disposeOfficialModel(r));
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
test('progressive detail keeps visible grace and restores its fallback when warm retention is disabled',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});assert.equal(await layer.loadCatalogue('http://localhost/catalogue.json'),true);
 const c=camera();assert.deepEqual(layer.plan(c,{viewportHeight:800,force:true}),[f.meta.uid]);await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);
 assert.equal(f.stream.cache.entries.get('0_0').buildings.group.children.length,0);assert.equal(f.stream.maximumRoof(5,5,1),12);assert.equal(f.stream.getLoadedBuilding(f.meta.uid).modelId,f.meta.modelId);
 entry.group.updateMatrixWorld(true);const ray=new THREE.Raycaster(new THREE.Vector3(5,30,5),new THREE.Vector3(0,-1,0)),hit=ray.intersectObjects(f.stream.pickMeshes(ray.ray))[0];assert.ok(hit);assert.equal(f.stream.featureAt(hit).uid,f.meta.uid);assert.equal(f.stream.featureAt(hit).topHeightHKPD,10);
 f.stream.buildings.visible=false;assert.equal(f.stream.pickMeshes(ray.ray).length,0);f.stream.buildings.visible=true;
 let disposed=0;entry.meshes[0].geometry.addEventListener('dispose',()=>disposed++);c.position.set(5,10,5000);c.lookAt(5,7,5);layer.plan(c,{force:true});
 assert.equal(f.stream.detailedModels.get(f.meta.uid),entry);assert.equal(f.stream.maximumRoof(5,5,1),12);assert.equal(disposed,0);assert.equal(layer.stats.cached,1);
 c.lookAt(5,10,6000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);assert.equal(disposed,1);assert.equal(layer.stats.cached,0);
});
test('failed model download uses Retry and only activates detail after successful verification',async t=>{
 const f=fixture();let failed=true;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?(failed?new Response('',{status:503}):new Response(f.compressed)):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await assert.rejects(layer.cache.waitFor([f.meta.uid]),/503/);assert.equal(f.stream.detailedModels.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
 while(layer.cache.running.size)await tick();failed=false;await layer.retry();await layer.cache.waitFor([f.meta.uid]);assert.equal(f.stream.maximumRoof(5,5,1),12);assert.equal(layer.stats.errors.length,0);
});
test('camera travel cancels a pending source request; late completion cannot replace the fallback',async t=>{
 const f=fixture();let release;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Promise(resolve=>{release=resolve;}):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});while(!release)await tick();c.position.set(50000,500,50000);c.lookAt(50000,0,40000);layer.plan(c,{force:true});release(new Response(f.compressed));while(layer.cache.running.size)await tick();assert.equal(f.stream.detailedModels.size,0);assert.equal(layer.cache.entries.size,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
});
test('background gate defers new detail while keeping selected and resident models available',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();
 assert.deepEqual(layer.plan(c,{allowNewLoads:false,force:true}),[]);assert.equal(layer.cache.running.size,0);
 assert.deepEqual(layer.plan(c,{allowNewLoads:false,selectedUid:f.meta.uid,force:true}),[f.meta.uid]);await layer.cache.waitFor([f.meta.uid]);
 assert.deepEqual(layer.plan(c,{allowNewLoads:false,force:true}),[f.meta.uid]);assert.equal(f.stream.detailedModels.get(f.meta.uid)?.active,true);
});
test('interaction pause preserves an in-flight source instead of downloading it again',async t=>{
 const f=fixture();let release,first=true;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)&&first?(first=false,new Promise(resolve=>{release=resolve;})):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});while(!release)await tick();
 layer.setLoadingPaused(true);assert.equal(layer.cache.paused,true);release(new Response(f.compressed));await tick();assert.equal(layer.cache.entries.size,0);
 layer.setLoadingPaused(false);await layer.cache.waitFor([f.meta.uid]);assert.equal(f.stream.detailedModels.get(f.meta.uid)?.active,true);
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
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);let disposed=0;entry.meshes[0].geometry.addEventListener('dispose',()=>disposed++);
 const restore=f.stream.refreshBuildings.bind(f.stream);let fail=true;t.mock.method(f.stream,'refreshBuildings',async()=>{if(fail)throw new Error('fixture bake failure');return restore();});c.position.set(50000,500,50000);c.lookAt(60000,500,50000);layer.plan(c,{force:true});await Promise.allSettled([...layer.retiring.values()]);
 assert.equal(disposed,0);assert.equal(f.stream.detailedModels.get(f.meta.uid),entry);assert.ok(layer.stats.residentBytes>0);assert.deepEqual(layer.stats.errors,['restore:'+f.meta.uid]);
 fail=false;await layer.retry();assert.equal(disposed,1);assert.equal(f.stream.detailedModels.size,0);assert.equal(layer.stats.residentBytes,0);assert.equal(layer.stats.errors.length,0);assert.equal(f.stream.maximumRoof(5,5,1),10);
});
test('pre-existing baked government models and source infrastructure take precedence over optional compact detail',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');await f.stream.suppressInfrastructureBuildings([f.meta.uid]);assert.deepEqual(layer.plan(camera(),{force:true}),[]);
 await f.stream.suppressInfrastructureBuildings([]);f.stream.cache.entries.get('0_0').data.buildings[0].modelGeometry={position:[0,0,0]};assert.deepEqual(layer.plan(camera(),{force:true}),[]);
});
test('turning away briefly retains nearby decoded detail without another model or material bake',async t=>{
 const f=fixture();let downloads=0;t.mock.method(globalThis,'fetch',async url=>{if(url==='tile')return response(f.data);if(modelRequest(url)){downloads++;return new Response(f.compressed);}return response(f.catalogue);});await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid),mesh=entry.meshes[0],fallback=f.stream.cache.entries.get('0_0').buildings.group;
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

test('catalogue accepts an explicit retained basic-form support flag',()=>{
 const f=fixture(),meta={...f.meta,retainsBasicForm:true};
 assert.equal(prepareModelCatalogue({...f.catalogue,models:[meta]},'http://localhost/catalogue.json')[0].retainsBasicForm,true);
 assert.throws(()=>prepareModelCatalogue({...f.catalogue,models:[{...meta,retainsBasicForm:'yes'}]},'http://localhost/catalogue.json'),/basic-form retention/);
});

test('bounded vertical placement aligns an unchanged source roof to current LandsD TopHeight',async t=>{
 const f=fixture(),offset=3,sourceWorldBounds=f.meta.worldBounds;
 const meta={...f.meta,worldBounds:[[0,5,0],[10,15,10]],sourceWorldBounds,verticalPlacementOffsetHKPD:offset,verticalPlacementBasis:'current-recorded-top-height',recordedTopHeight:15};
 const building={...f.building,height:13,topHeightHKPD:15};
 const prepared=prepareModelCatalogue({...f.catalogue,models:[meta]},'http://localhost/catalogue.json')[0];
 const result=await loadOfficialModel(prepared,building,f.stream.lighting,{fetcher:async()=>new Response(f.compressed)});t.after(()=>disposeOfficialModel(result));
 assert.deepEqual(result.group.position.toArray(),[-834500,3,816500]);
 assert.equal(result.bounds.min.y,5);assert.equal(result.bounds.max.y,15);
 assert.equal(Math.max(...Array.from(result.record.modelGeometry.position).filter((_,i)=>i%3===1)),15);
 assert.equal(result.record.modelSource.verticalPlacementOffsetHKPD,3);
 assert.deepEqual(result.record.modelSource.sourceWorldBounds,sourceWorldBounds);
 for(const edit of [
  {verticalPlacementOffsetHKPD:21},
  {verticalPlacementOffsetHKPD:3},
  {verticalPlacementOffsetHKPD:3,sourceWorldBounds,verticalPlacementBasis:'manual'},
  {verticalPlacementOffsetHKPD:3,sourceWorldBounds,verticalPlacementBasis:'current-recorded-top-height'},
 ]){
  const candidate={...f.meta,...edit};
  assert.throws(()=>prepareModelCatalogue({...f.catalogue,models:[candidate]},'http://localhost/catalogue.json'),/vertical placement/);
 }
});

test('a retained basic form stays rendered under an active government shell',async t=>{
 const f=fixture();f.catalogue.models[0]={...f.meta,retainsBasicForm:true};
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await layer.cache.waitFor([f.meta.uid]);
 assert.equal(f.stream.detailedModels.get(f.meta.uid)?.active,true);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);assert.equal(f.stream.getLoadedBuilding(f.meta.uid).modelId,f.meta.modelId);
});

test('real source-tile replacement activates a tower only after its native support and retires tower first',async t=>{
 const f=fixture(),supportUid='landsd/2:0';f.meta.supportDependencies=[{uid:supportUid,state:'candidate'}];
 f.catalogue.models.push({...f.meta,uid:supportUid,objectId:2,buildingCSUID:'two',modelId:'B0002',supportDependencies:[]});f.catalogue.counts.packedModels=2;
 f.data.buildings.push({...f.building,uid:supportUid,id:'landsd/2',objectId:2,buildingCSUID:'two'});
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const events=[],replace=f.stream.setDetailedModel.bind(f.stream);t.mock.method(f.stream,'setDetailedModel',async(uid,value,options)=>{
  if(uid===f.meta.uid&&value)assert.equal(f.stream.detailedModels.get(supportUid)?.active,true);
  if(uid===supportUid&&!value)assert.equal(f.stream.detailedModels.has(f.meta.uid),false);
  const result=await replace(uid,value,options);events.push((value?'add:':'remove:')+uid);return result;
 });
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');
 const c=camera();assert.deepEqual(layer.plan(c,{force:true,selectedUid:f.meta.uid}),[supportUid,f.meta.uid]);await layer.cache.waitFor([f.meta.uid]);assert.equal(f.stream.detailedModels.size,2);
 c.position.set(50000,500,50000);c.lookAt(60000,500,50000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);assert.equal(f.stream.detailedModels.size,0);
 assert.deepEqual(events,['add:'+supportUid,'add:'+f.meta.uid,'remove:'+f.meta.uid,'remove:'+supportUid]);
});


test('an active government assembly hides its bundled fallback forms and restores them on eviction',async t=>{
 const f=fixture(),bundledUid='landsd/2:0';f.catalogue.models[0].suppressesBuildingUids=[bundledUid];
 f.data.buildings.push({...f.building,uid:bundledUid,id:'landsd/2',objectId:2,buildingCSUID:'two',rings:[[[20,0],[30,0],[30,10],[20,10],[20,0]]],centre:[25,5]});
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');
 assert.ok(f.stream.collision(25,5,2,11,1));const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);
 assert.equal(f.stream.collision(25,5,2,11,1),null);assert.equal(f.stream.cache.entries.get('0_0').detailSuppressions.has(bundledUid),true);
 c.position.set(50000,500,50000);c.lookAt(60000,500,50000);layer.plan(c,{force:true});await Promise.all([...layer.retiring.values()]);assert.ok(f.stream.collision(25,5,2,11,1));
});

test('warm reversal and viewport changes reuse decoded source; grace expiry restores fallback',async t=>{
 const f=fixture();let requests=0;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?(requests++,new Response(f.compressed)):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true,now:0});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);
 c.lookAt(5,10,1000);layer.plan(c,{force:true,now:200,viewportWidth:844,viewportHeight:390});assert.equal(layer.cache.entries.get(f.meta.uid),entry);assert.ok(f.stream.collision(5,5,2,13,1));
 c.lookAt(5,7,5);layer.plan(c,{force:true,now:400,viewportWidth:3840,viewportHeight:2160});assert.equal(requests,1);assert.equal(layer.cache.entries.get(f.meta.uid),entry);
 c.lookAt(5,10,1000);layer.plan(c,{force:true,now:500});layer.plan(c,{now:11000});await Promise.all([...layer.retiring.values()]);assert.equal(layer.cache.entries.size,0);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);
});

test('in-view demotion keeps native shell visible until fallback is ready, then reuses warm decode',async t=>{
 const f=fixture();let requests=0;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?(requests++,new Response(f.compressed)):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true,now:0});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);
 let complete,started=false;const replace=f.stream.setDetailedModel.bind(f.stream);t.mock.method(f.stream,'setDetailedModel',async(uid,value,options)=>{if(!value&&!started){started=true;await new Promise(r=>{complete=r;});}return replace(uid,value,options);});
 c.position.set(5,10,5000);c.lookAt(5,7,5);layer.plan(c,{force:true,now:200});layer.plan(c,{force:true,now:2300});while(!complete)await tick();
 assert.equal(entry.group.visible,true);assert.equal(entry.active,true);assert.equal(f.stream.cache.entries.get('0_0').buildings.group.children.length,0);
 complete();await Promise.all([...layer.activating.values()]);assert.equal(entry.active,false);assert.equal(layer.cache.entries.get(f.meta.uid),entry);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);
 c.position.copy(camera().position);c.lookAt(5,7,5);layer.plan(c,{force:true,now:2500});await Promise.all([...layer.activating.values()]);assert.equal(entry.active,true);assert.equal(requests,1);
});

test('a hidden/zero canvas pauses admission without flushing resident models',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([f.meta.uid]);const entry=layer.cache.entries.get(f.meta.uid);layer.plan(c,{viewportWidth:0,viewportHeight:800,force:true});assert.equal(layer.cache.paused,true);assert.equal(layer.cache.entries.get(f.meta.uid),entry);
});
function drawBudgetFixture(t){
 const f=fixture(),base=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0],detailedModels=new Map();
 const stream={lighting:f.stream.lighting,detailedModels,getLoadedBuilding:uid=>({...f.building,uid}),setDetailedModel:async(uid,entry)=>{const old=detailedModels.get(uid);if(old){old.active=false;old.group.visible=false;}if(entry){entry.active=true;entry.group.visible=true;detailedModels.set(uid,entry);}else detailedModels.delete(uid);return true;}};
 const layer=new OfficialModelLayer({stream,profile:'desktop',loadAsset:async meta=>({entry:meta,record:{...f.building,uid:meta.uid},group:new THREE.Group(),meshes:[],active:false,budget:{...modelBudget(meta),drawCalls:80}})});
 for(let i=1;i<=3;i++)layer.models.set(`landsd/${i}:0`,{...base,uid:`landsd/${i}:0`});t.after(async()=>{await layer.dispose();f.stream.cache.close();});return layer;
}
test('lower profile replans decoded draw costs and restores excess resident fallbacks',async t=>{
 const layer=drawBudgetFixture(t);layer.plan(camera(),{force:true});await layer.cache.waitFor([...layer.models.keys()]);assert.equal(layer.stats.drawCalls,240);
 layer.setProfile('mobile');await Promise.all([...layer.retiring.values()]);assert.equal(layer.cache.entries.size,1);assert.equal(layer.stats.drawCalls,80);assert.ok(layer.stats.drawCalls<=layer.limits.drawCalls);assert.equal(layer.stats.errors.length,0);
});
test('selected unknown-cost detail displaces wanted residents without a sticky budget error',async t=>{
 const layer=drawBudgetFixture(t);layer.setProfile('mobile');const fresh=layer.models.get('landsd/3:0');layer.models.delete(fresh.uid);const c=camera();layer.plan(c,{force:true});while(layer.cache.running.size)await tick();
 assert.equal(layer.cache.entries.size,1);assert.equal(layer.stats.errors.length,0);const selected='landsd/3:0';layer.models.set(selected,fresh);assert.equal(layer.drawCosts.has(selected),false);
 layer.plan(c,{selectedUid:selected,force:true});await layer.cache.waitFor([selected]);assert.equal(layer.cache.entries.has(selected),true);assert.equal(layer.stats.drawCalls,80);assert.equal(layer.stats.errors.length,0);
});
test('an indivisible oversized detail stays on fallback without sticky errors or repeated decodes',async t=>{
 const layer=drawBudgetFixture(t),load=layer.loadAsset;let decodes=0;layer.loadAsset=async(...args)=>{decodes++;const entry=await load(...args);entry.budget.drawCalls=300;return entry;};layer.models=new Map([[...layer.models][0]]);layer.setProfile('mobile');const c=camera(),selected=[...layer.models.keys()][0];
 layer.plan(c,{selectedUid:selected,force:true});while(layer.cache.running.size)await tick();
 for(let i=0;i<10;i++)layer.plan(c,{selectedUid:selected,force:true});await tick();assert.equal(decodes,1);assert.equal(layer.cache.entries.size,0);assert.equal(layer.stats.errors.length,0);assert.match(layer.supportHolds.get(selected),/draw-call budget/);
});

test('Base mode starts no model downloads and cancels pending shared byte-cache work',async t=>{
 const f=fixture();let detailRequests=0;t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?(detailRequests++,new Response(f.compressed)):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.setQuality('base');await layer.loadCatalogue('http://localhost/catalogue.json');
 assert.deepEqual(layer.plan(camera(),{force:true}),[]);await tick();assert.equal(detailRequests,0);assert.equal(layer.stats.quality,'base');
});
test('switching to Base aborts an active detail transfer without closing the shared cache',async t=>{
 const f=fixture();let modelSignal,started;const start=new Promise(resolve=>started=resolve);
 t.mock.method(globalThis,'fetch',async(url,{signal}={})=>url==='tile'?response(f.data):modelRequest(url)?(modelSignal=signal,started(),new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')),{once:true}))):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await start;
 layer.setQuality('base');assert.equal(modelSignal.aborted,true);
 for(let i=0;i<30&&layer.cache.running.size;i++)await tick();
 assert.equal(layer.cache.running.size,0);assert.equal(layer.byteCache.closed,false);assert.equal(layer.byteCache.stats.pending,0);assert.equal(layer.cache.entries.size,0);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);
});
test('an approved self-contained variant loads lazily and records source provenance',async t=>{
 const f=fixture();f.catalogue.optimisedVariants=[await variantDescriptor(f)];t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await layer.cache.waitFor([f.meta.uid]);
 const entry=layer.cache.entries.get(f.meta.uid);assert.equal(entry.entry.variantId,repeat('b'));assert.equal(entry.record.modelSource.sourceSha256,f.meta.sha256);assert.equal(entry.record.modelSource.sourceMetadataSha256,await sourceMetadataHash(f.meta,f.catalogue));assert.equal(layer.failedVariants.size,0);
});
test('a stale optional descriptor is ignored while the native catalogue remains usable',async t=>{
 const f=fixture(),variant=await variantDescriptor(f);variant.sourceMetadataSha256=repeat('f');f.catalogue.optimisedVariants=[variant];
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const calls=[],layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{calls.push(meta);return fakeEntry(meta,building);}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});
 assert.equal(await layer.loadCatalogue('http://localhost/catalogue.json'),true);layer.plan(camera(),{force:true});await layer.cache.waitFor([f.meta.uid]);
 assert.equal(layer.catalogueErrors.size,0);assert.deepEqual(layer.models.get(f.meta.uid).variants,[]);assert.equal(calls.length,1);assert.equal(calls[0].variantId,undefined);
});
test('a failed variant GLB falls back to the native entry after one decode failure',async t=>{
 const f=fixture(),badBytes=gzipSync(Buffer.from('not a glb')),variant=await variantDescriptor(f,{bytes:badBytes,glbBytes:Buffer.byteLength('not a glb')});f.catalogue.optimisedVariants=[variant];
 t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):modelRequest(url)?new Response(new URL(url).pathname.includes('/variants/')?badBytes:f.compressed):response(f.catalogue));await sourceReady(f);
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');layer.plan(camera(),{force:true});await layer.cache.waitFor([f.meta.uid]);
 const entry=layer.cache.entries.get(f.meta.uid);assert.equal(entry.entry.variantId,undefined);assert.equal(entry.record.modelSource.variantId,null);assert.equal(layer.failedVariants.get(variant.variantId),'Invalid compact GLB');assert.equal(layer.byteCache.stats.requests,2);
});
test('variant GLBs allow only declared codecs and mesh quantisation',async t=>{
 const f=fixture(),source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];
 const decode=async(used,codec,required=[],images=false)=>{
  const glb=withGLTFExtensions(f.compressed,used,required,images?[{bufferView:0,mimeType:'image/png'}]:null),compressed=gzipSync(glb),sha256=createHash('sha256').update(compressed).digest('hex');
  const entry={...source,variantId:repeat('f'),sourceSha256:source.sha256,sourceMetadataSha256:repeat('a'),tier:'balanced',codec,sha256,bytes:compressed.length,glbBytes:glb.length};
  return loadOfficialModel(entry,f.building,f.stream.lighting,{fetcher:async()=>new Response(compressed)});
 };
 await assert.rejects(decode([],'meshopt'),/missing its declared codec extension/);
 await assert.rejects(decode(['EXT_meshopt_compression','KHR_materials_unlit'],'meshopt'),/unsupported glTF extension/);
 await assert.rejects(decode(['KHR_draco_mesh_compression'],'none'),/unsupported glTF extension/);
 await assert.rejects(decode([],'none',[],true),/Variants must be self-contained/);
 const meshopt=await decode(['EXT_meshopt_compression'],'meshopt',['EXT_meshopt_compression']);t.after(()=>disposeOfficialModel(meshopt));assert.equal(meshopt.record.modelSource.codec,'meshopt');
 const quantized=await decode(['KHR_mesh_quantization'],'none');t.after(()=>disposeOfficialModel(quantized));assert.equal(quantized.record.modelSource.codec,'none');
});
test('if variant and native loading both fail, the surveyed base form remains installed',async t=>{
 const f=fixture();f.catalogue.optimisedVariants=[await variantDescriptor(f)];t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);
 fakeStreamingSwaps(f.stream);const calls=[];
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta)=>{calls.push(meta);throw new Error(meta.variantId?'variant decode failed':'native decode failed');}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});await layer.loadCatalogue('http://localhost/catalogue.json');const source=layer.models.get(f.meta.uid);
 layer.plan(camera(),{force:true});await assert.rejects(layer.cache.waitFor([source.uid]),/native decode failed/);
 assert.deepEqual(calls.map(entry=>entry.variantId??'native'),[repeat('b'),'native']);assert.equal(f.stream.detailedModels.size,0);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);assert.equal(layer.failedVariants.get(repeat('b')),'variant decode failed');
});
test('same-UID quality swaps keep old entry until replacement is ready in both directions',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let release,gate=false;
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{if(gate)await new Promise(resolve=>release=resolve);return fakeEntry(meta,building);}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([source.uid]);const native=layer.cache.entries.get(source.uid);source.variants=[{...source,variantId:repeat('e'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000}];
 let releases=0;const originalRelease=layer.release.bind(layer);layer.release=entry=>{if(entry===native)releases++;return originalRelease(entry);};gate=true;layer.setQuality('balanced');
 for(let i=0;i<30&&!release;i++)await tick();assert.equal(layer.cache.entries.get(source.uid),native);assert.equal(f.stream.detailedModels.get(source.uid),native);
 release();for(let i=0;i<30&&layer.cache.entries.get(source.uid)?.entry.variantId!==repeat('e');i++)await tick();
 const variant=layer.cache.entries.get(source.uid);assert.equal(variant.entry.variantId,repeat('e'));assert.equal(f.stream.detailedModels.get(source.uid),variant);assert.equal(releases,0);
 release=null;layer.setQuality('lightweight');for(let i=0;i<30&&!release;i++)await tick();assert.equal(layer.cache.entries.get(source.uid),variant);assert.equal(f.stream.detailedModels.get(source.uid),variant);
 release();for(let i=0;i<30&&layer.cache.entries.get(source.uid)?.entry.variantId;i++)await tick();
 assert.equal(layer.cache.entries.get(source.uid).entry.variantId,undefined);assert.equal(f.stream.detailedModels.get(source.uid),layer.cache.entries.get(source.uid));
});
test('a stale quality replacement cannot install after switching to Base',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let release;
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{if(meta.variantId)await new Promise(resolve=>release=resolve);return fakeEntry(meta,building);}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([source.uid]);source.variants=[{...source,variantId:repeat('e'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000}];layer.setQuality('balanced');
 for(let i=0;i<30&&!release;i++)await tick();assert.ok(release);layer.setQuality('base');await Promise.all([...layer.retiring.values()]);release();
 for(let i=0;i<30&&layer.cache.running.size;i++)await tick();assert.equal(layer.cache.entries.size,0);assert.equal(f.stream.detailedModels.has(source.uid),false);assert.equal(layer.cache.errors.size,0);
});
test('peak-budget deferral retains the resident asset without marking the variant corrupt',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let loads=0;
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{loads++;return fakeEntry(meta,building);}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 const c=camera();layer.plan(c,{force:true});await layer.cache.waitFor([source.uid]);const old=layer.cache.entries.get(source.uid);source.variants=[{...source,variantId:repeat('e'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000}];
 const cost=modelBudget(source);layer.limits={...layer.limits,geometryBytes:Math.floor(cost.geometryBytes*1.5),residentBytes:Math.floor(cost.residentBytes*1.5),triangles:Math.floor(cost.triangles*1.5)};layer.setQuality('balanced');
 for(let i=0;i<30&&layer.cache.running.size;i++)await tick();assert.equal(layer.cache.entries.get(source.uid),old);assert.equal(f.stream.detailedModels.get(source.uid),old);assert.equal(loads,1);assert.equal(layer.failedVariants.size,0);assert.match(layer.cache.errors.get(source.uid).message,/peak device budget/);
});
test('an individually oversized desired variant retains its resident detail without decoding',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let loads=0;
 const layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{loads++;return fakeEntry(meta,building);}});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 layer.plan(camera(),{force:true});await layer.cache.waitFor([source.uid]);const old=layer.cache.entries.get(source.uid);
 source.variants=[{...source,variantId:repeat('f'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000,decodedGeometryBytes:old.budget.geometryBytes+1,indexedVertices:source.indexedVertices+1,triangles:source.triangles+1}];
 layer.limits={...layer.limits,geometryBytes:old.budget.geometryBytes,residentBytes:old.budget.residentBytes,triangles:old.budget.triangles};layer.setQuality('balanced');
 for(let i=0;i<30&&layer.cache.running.size;i++)await tick();assert.equal(layer.cache.entries.get(source.uid),old);assert.equal(f.stream.detailedModels.get(source.uid),old);assert.equal(loads,1);assert.equal(layer.failedVariants.size,0);assert.match(layer.cache.errors.get(source.uid).message,/peak device budget/);
});
test('cleared first-load budget deferral retries an unchanged wanted model',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);fakeStreamingSwaps(f.stream);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let layer,attempts=0,blocker;
 layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{
  attempts++;const entry=fakeEntry(meta,building);
  if(attempts===1){blocker=fakeEntry(meta,building);layer.retiring.set(blocker,Promise.resolve());}
  return entry;
 }});
 t.after(async()=>{if(blocker){layer.retiring.delete(blocker);disposeOfficialModel(blocker);}await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 const cost=modelBudget(source);layer.limits={...layer.limits,geometryBytes:Math.floor(cost.geometryBytes*1.5),residentBytes:Math.floor(cost.residentBytes*1.5),triangles:Math.floor(cost.triangles*1.5)};
 const c=camera(),wanted=layer.plan(c,{force:true});while(layer.cache.running.size)await tick();
 assert.deepEqual(layer.cache.wanted,wanted);assert.equal(layer.cache.entries.has(source.uid),false);assert.match(layer.cache.errors.get(source.uid).message,/device budget/);assert.equal(attempts,1);
 layer.retiring.delete(blocker);disposeOfficialModel(blocker);blocker=null;assert.deepEqual(layer.plan(c,{force:true}),wanted);
 for(let i=0;i<30&&!layer.cache.entries.has(source.uid);i++)await tick();
 assert.equal(layer.cache.entries.has(source.uid),true);assert.equal(layer.cache.errors.size,0);assert.equal(attempts,2);
});
test('cancellation at replacement install completion restores the base form',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let layer,triggered=false,committed;
 f.stream.onChange=()=>{
  const detail=f.stream.detailedModels.get(source.uid);
  if(!triggered&&layer&&detail?.active&&detail.entry?.variantId){triggered=true;committed=detail;layer.setQuality('base');}
 };
 layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>fakeEntry(meta,building)});t.after(async()=>{await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 layer.plan(camera(),{force:true});await layer.cache.waitFor([source.uid]);source.variants=[{...source,variantId:repeat('e'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000}];layer.setQuality('balanced');
 for(let i=0;i<60&&(!triggered||layer.cache.running.size||layer.retiring.size);i++)await tick();await Promise.allSettled([...layer.retiring.values()]);
 assert.equal(triggered,true);assert.equal(layer.quality,'base');assert.equal(layer.cache.entries.size,0);assert.equal(f.stream.detailedModels.has(source.uid),false);assert.ok(f.stream.cache.entries.get('0_0').buildings.group.children.length);assert.equal(committed.group.parent,null);assert.equal(layer.cache.errors.size,0);
});
test('failed cancellation restoration retains live geometry until Retry restores base',async t=>{
 const f=fixture();t.mock.method(globalThis,'fetch',async url=>url==='tile'?response(f.data):response(f.catalogue));await sourceReady(f);
 const source=prepareModelCatalogue(f.catalogue,'http://localhost/catalogue.json')[0];let layer,triggered=false,committed,failRestore=true;
 const install=f.stream.setDetailedModel.bind(f.stream);
 f.stream.setDetailedModel=(uid,entry,options)=>{if(triggered&&!entry&&failRestore)throw new Error('Fallback blocked');return install(uid,entry,options);};
 f.stream.onChange=()=>{const detail=f.stream.detailedModels.get(source.uid);if(!triggered&&layer&&detail?.active&&detail.entry?.variantId){triggered=true;committed=detail;layer.setQuality('base');}};
 layer=new OfficialModelLayer({stream:f.stream,warmMs:0,loadAsset:async(meta,building)=>{
  const entry=fakeEntry(meta,building),geometry=new THREE.BufferGeometry(),material=new THREE.MeshBasicMaterial();let disposals=0;
  const dispose=geometry.dispose.bind(geometry);geometry.dispose=()=>{disposals++;dispose();};entry.group.add(new THREE.Mesh(geometry,material));entry.disposals=()=>disposals;return entry;
 }});t.after(async()=>{failRestore=false;await layer.dispose();f.stream.cache.close();});layer.models.set(source.uid,source);
 layer.plan(camera(),{force:true});await layer.cache.waitFor([source.uid]);source.variants=[{...source,variantId:repeat('e'),tier:'balanced',codec:'none',minPixels:0,maxPixels:1000000}];layer.setQuality('balanced');
 for(let i=0;i<60&&(!triggered||layer.cache.running.size||layer.retiring.size);i++)await tick();await Promise.allSettled([...layer.retiring.values()]);
 assert.equal(f.stream.detailedModels.get(source.uid),committed);assert.equal(committed.disposals(),0);assert.ok(layer.releaseFailures.has(committed));
 failRestore=false;await layer.retry();assert.equal(f.stream.detailedModels.has(source.uid),false);assert.equal(layer.releaseFailures.size,0);assert.equal(committed.disposals(),1);
});
