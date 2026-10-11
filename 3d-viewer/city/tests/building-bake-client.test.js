import test from 'node:test';
import assert from 'node:assert/strict';
import {bakeBuildingBuffers} from '../building-bake-client.js';
test('worker construction, clone and runtime failures do not strand the bounded queue',async t=>{
 let mode='construct',active=0,peak=0;
 class FakeWorker{
  constructor(){if(mode==='construct')throw new Error('construct');active++;peak=Math.max(peak,active);}
  terminate(){active--;}
  postMessage(){if(mode==='clone')throw new Error('clone');queueMicrotask(()=>mode==='runtime'?this.onerror({message:'runtime'}):this.onmessage({data:{meshes:[],totalVertices:0}}));}
 }
 const previous=globalThis.Worker;globalThis.Worker=FakeWorker;t.after(()=>{if(previous)globalThis.Worker=previous;else delete globalThis.Worker;});
 for(mode of ['construct','clone','runtime'])await assert.rejects(bakeBuildingBuffers([]),new RegExp(mode));
 mode='success';await Promise.all(Array.from({length:20},()=>bakeBuildingBuffers([])));assert.equal(active,0);assert.ok(peak<=2);
});
test('worker failures recover exact inline source forms while cancellation remains terminal',async t=>{
 const {makeBuildings}=await import('../world.js');let mode='construct';
 class FailedWorker{constructor(){if(mode==='construct')throw new Error('CSP');}terminate(){}postMessage(){if(mode==='clone')throw new Error('clone');queueMicrotask(()=>this.onerror({message:'module failed'}));}}
 const previous=globalThis.Worker;globalThis.Worker=FailedWorker;t.after(()=>{if(previous)globalThis.Worker=previous;else delete globalThis.Worker;});
 const features=[{id:'landsd/1',uid:'landsd/1:0',kind:'yes',base:2,height:8,minimum:0,rings:[[[0,0],[10,0],[10,10],[0,10],[0,0]]],centre:[5,5]}];
 const expected=await makeBuildings(features,null,{worker:false}),dispose=result=>{for(const mesh of result.group.children)mesh.geometry.dispose();for(const m of result.materials)m.dispose();};t.after(()=>dispose(expected));
 for(mode of ['construct','clone','runtime']){const actual=await makeBuildings(features,null,{worker:true});assert.equal(actual.totalVertices,expected.totalVertices);assert.equal(actual.group.children.length,expected.group.children.length);for(let i=0;i<actual.group.children.length;i++)for(const [key,a] of Object.entries(expected.group.children[i].geometry.attributes))assert.deepEqual(actual.group.children[i].geometry.attributes[key].array,a.array);dispose(actual);}
 const controller=new AbortController();controller.abort();await assert.rejects(makeBuildings(features,null,{worker:true,signal:controller.signal}),{name:'AbortError'});
});
