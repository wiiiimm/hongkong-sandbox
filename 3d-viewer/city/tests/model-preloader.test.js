import test from 'node:test';
import assert from 'node:assert/strict';
import {ModelPreloader} from '../model-preloader.js';
const entry=(uid,x,bytes=4)=>({uid,assetURL:'https://example.test/'+uid,bytes,worldBounds:[[x,0,0],[x+1,1,1]],priority:'detail'});

test('preloads compressed models nearest first and reprioritises around a moving origin',async()=>{
 let origin=[0,0],release;const requested=[];
 const preloader=new ModelPreloader({getOrigin:()=>origin,fetcher:async url=>{requested.push(url.split('/').at(-1));if(requested.length===1)await new Promise(resolve=>{release=resolve;});return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('far',100),entry('near',5),entry('middle',40)]);const loading=preloader.start();
 while(!release)await new Promise(resolve=>setTimeout(resolve,0));assert.deepEqual(requested,['near']);origin=[110,0];release();await loading;
 assert.deepEqual(requested,['near','far','middle']);assert.equal(preloader.stats.complete,true);assert.equal(preloader.stats.done,3);assert.equal(preloader.stats.sessionBytes,12);
});

test('pause preserves an in-flight download and stops admission until resume',async()=>{
 let attempts=0,release;const preloader=new ModelPreloader({getOrigin:()=>[0,0],fetcher:async()=>{attempts++;if(attempts===1)await new Promise(resolve=>{release=resolve;});return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('one',0),entry('two',10)]);const loading=preloader.start();while(!release)await new Promise(resolve=>setTimeout(resolve,0));preloader.setPaused(true);release();
 await new Promise(resolve=>setTimeout(resolve,10));assert.equal(preloader.stats.done,1);assert.equal(attempts,1);preloader.setPaused(false);await loading;assert.equal(attempts,2);assert.equal(preloader.stats.done,2);
});

test('an immediate restart cannot be cancelled by the stopped run',async()=>{
 let attempts=0;const preloader=new ModelPreloader({getOrigin:()=>[0,0],fetcher:async(_url,{signal})=>{attempts++;if(attempts===1)await new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(signal.reason),{once:true}));return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('one',0)]);void preloader.start();while(!preloader.controller)await new Promise(resolve=>setTimeout(resolve,0));
 preloader.stop();await preloader.start();
 assert.equal(attempts,2);assert.equal(preloader.stats.active,false);assert.equal(preloader.stats.done,1);
});

test('demo sessions obey byte and model caps without decoding',async()=>{
 const p=new ModelPreloader({getOrigin:()=>[0,0],maxBytes:8,maxModels:2,fetcher:async()=>new Response(new Uint8Array(4))});p.setModels([entry('a',0),entry('b',10),entry('c',20)]);await p.start();assert.equal(p.stats.done,2);assert.equal(p.stats.budgetReached,true);assert.equal(p.stats.sessionBytes,8);
});
test('Stop cancels a shared-cache background transfer and immediate restart survives old settlement',async()=>{
 const {ModelByteCache}=await import('../model-byte-cache.js'),cache=new ModelByteCache();let attempts=0,firstSignal,finishOld;
 const preloader=new ModelPreloader({byteCache:cache,getOrigin:()=>[0,0],fetcher:async(_url,{signal})=>{attempts++;if(attempts===1){firstSignal=signal;await new Promise((resolve,reject)=>{finishOld=()=>reject(new DOMException('Aborted','AbortError'));});}return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('one',0)]);const old=preloader.start();while(!firstSignal)await new Promise(resolve=>setTimeout(resolve,0));preloader.stop();assert.equal(firstSignal.aborted,true);
 const restarted=preloader.start();await old;await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cache.pending.size,1);finishOld();await restarted;
 assert.equal(attempts,2);assert.equal(preloader.stats.done,1);assert.equal(preloader.stats.errors,0);assert.equal(cache.pending.size,0);cache.close();
});
