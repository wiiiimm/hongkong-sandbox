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
