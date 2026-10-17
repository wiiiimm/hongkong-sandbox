import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {CityStreaming} from '../streaming.js';
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));
const profile={profile:4,source:'research',retailTop:7};
function fixture(activityTiles=true){
 const building={uid:'landsd/1:0',id:'landsd/1',tile:'0_0',kind:'yes',base:2,height:12,minimum:0,rings:[[[0,0],[10,0],[10,10],[0,10],[0,0]]],centre:[5,5]},data={id:'0_0',buildings:[building],roads:[],parks:[]};
 const manifest={activityTiles,tileSize:2000,tiles:[{id:'0_0',url:'city/data/tiles/0_0.json',bounds:[0,0,2000,2000],centre:[1000,1000]}]};
 const terrain={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta:{georef:{bE:834500,bN:816500,aE:70,aN:-70}}};
 const stream=new CityStreaming({manifest,terrain,sampler:{height:()=>2},scene:new THREE.Scene(),activity:{buildings:{[building.uid]:profile}}});
 return {stream,data,sidecar:{buildings:{[building.uid]:profile}}};
}
const ok=data=>({ok:true,json:async()=>structuredClone(data)});
const bakedProfile=entry=>entry.buildings.group.children[0].geometry.attributes.cityLight.getY(0);

test('geometry and activity load concurrently with the same signal before facade profiles are baked',async t=>{
 const {stream,data,sidecar}=fixture(),requests=[];t.after(()=>stream.cache.close());
 t.mock.method(globalThis,'fetch',(url,{signal})=>new Promise(resolve=>requests.push({url,signal,resolve})));
 stream.cache.plan(['0_0']);await tick();assert.equal(requests.length,2);assert.equal(requests[0].signal,requests[1].signal);assert.deepEqual(requests.map(r=>r.url),['city/data/tiles/0_0.json','city/data/activity/0_0.json']);
 requests[0].resolve(ok(data));await tick();assert.equal(stream.cache.ready(['0_0']),false);assert.equal(stream.cache.entries.size,0);
 requests[1].resolve(ok(sidecar));await stream.cache.waitFor(['0_0']);const entry=stream.cache.entries.get('0_0');assert.deepEqual(entry.data.buildings[0].activity,profile);assert.equal(bakedProfile(entry),4);
});

test('failed activity blocks tile readiness and the normal cache Retry restores both data and windows',async t=>{
 const {stream,data,sidecar}=fixture();let failure=true;const requests=[];t.after(()=>stream.cache.close());
 t.mock.method(globalThis,'fetch',async url=>{requests.push(url);return url.includes('/activity/')?(failure?{ok:false,status:503}:ok(sidecar)):ok(data);});
 stream.cache.plan(['0_0']);await assert.rejects(stream.cache.waitFor(['0_0']),/City activity 0_0: HTTP 503/);assert.equal(stream.cache.ready(['0_0']),false);assert.equal(stream.cache.entries.size,0);
 while(stream.cache.running.size)await tick();failure=false;stream.cache.retry();await stream.cache.waitFor(['0_0']);assert.equal(stream.cache.errors.size,0);assert.equal(bakedProfile(stream.cache.entries.get('0_0')),4);assert.equal(requests.filter(url=>url.includes('/activity/')).length,2);assert.equal(requests.filter(url=>url.includes('/tiles/')).length,2);
});

test('cancelled travel aborts geometry and activity together and ignores their late completion',async t=>{
 const {stream,data,sidecar}=fixture(),requests=[];t.after(()=>stream.cache.close());
 t.mock.method(globalThis,'fetch',(url,{signal})=>new Promise(resolve=>requests.push({url,signal,resolve})));
 stream.cache.plan(['0_0']);await tick();const arrival=assert.rejects(stream.cache.waitFor(['0_0']),{name:'AbortError'});stream.cache.plan([]);await arrival;assert.ok(requests.every(r=>r.signal.aborted));
 for(const r of requests)r.resolve(ok(r.url.includes('/activity/')?sidecar:data));while(stream.cache.running.size)await tick();assert.equal(stream.cache.entries.size,0);assert.equal(stream.cache.errors.size,0);assert.equal(stream.buildings.children.length,0);
});

test('legacy manifests fetch geometry only and retain global activity profiles',async t=>{
 const {stream,data}=fixture(false),requests=[];t.after(()=>stream.cache.close());t.mock.method(globalThis,'fetch',async url=>{requests.push(url);return ok(data);});
 stream.cache.plan(['0_0']);await stream.cache.waitFor(['0_0']);assert.deepEqual(requests,['city/data/tiles/0_0.json']);assert.equal(bakedProfile(stream.cache.entries.get('0_0')),4);
});

test('malformed, incomplete or invalid per-building profiles cannot silently render mixed-use windows',async t=>{
 const cases=[['array',{buildings:[]}],['missing UID',{buildings:{}}],['non-integer profile',{buildings:{'landsd/1:0':{...profile,profile:1.5}}}],['out-of-range profile',{buildings:{'landsd/1:0':{...profile,profile:5}}}],['missing retail height',{buildings:{'landsd/1:0':{profile:2}}}],['negative retail height',{buildings:{'landsd/1:0':{...profile,retailTop:-1}}}],['non-finite retail height',{buildings:{'landsd/1:0':{...profile,retailTop:Infinity}}}]];
 for(const [name,sidecar] of cases)await t.test(name,async t=>{
  const {stream,data}=fixture();t.after(()=>stream.cache.close());t.mock.method(globalThis,'fetch',async url=>ok(url.includes('/activity/')?sidecar:data));
  stream.cache.plan(['0_0']);await assert.rejects(stream.cache.waitFor(['0_0']),/Invalid city activity 0_0/);assert.equal(stream.cache.entries.size,0);
 });
});

test('legacy unclassified buildings still use the existing fallback profile',async t=>{
 const {stream,data}=fixture(false);stream.activity={buildings:{}};t.after(()=>stream.cache.close());t.mock.method(globalThis,'fetch',async()=>ok(data));
 stream.cache.plan(['0_0']);await stream.cache.waitFor(['0_0']);assert.equal(stream.cache.entries.get('0_0').data.buildings[0].activity,undefined);assert.equal(bakedProfile(stream.cache.entries.get('0_0')),3);
});
