import test from 'node:test';
import assert from 'node:assert/strict';
import {ModelPreloader} from '../model-preloader.js';
const entry=(uid,x,bytes=4)=>({uid,assetURL:'https://example.test/'+uid,bytes,worldBounds:[[x,0,0],[x+1,1,1]],priority:'detail'});

test('preloads compressed models nearest first and reprioritises around a moving origin',async()=>{
 let origin=[0,0],release;const requested=[];
 const preloader=new ModelPreloader({getOrigin:()=>origin,fetcher:async url=>{requested.push(url.split('/').at(-1));if(requested.length===1)await new Promise(resolve=>{release=resolve;});return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('far',100),entry('near',5),entry('middle',40)]);const loading=preloader.start();
 while(!release)await new Promise(resolve=>setTimeout(resolve,0));assert.deepEqual(requested,['near']);origin=[110,0];release();await loading;
 assert.deepEqual(requested,['near','far','middle']);assert.deepEqual(preloader.stats,{active:false,paused:false,done:3,total:3,bytesDone:12,totalBytes:12,errors:0,complete:true});
});

test('pause aborts background work and resume retries it',async()=>{
 let attempts=0;const preloader=new ModelPreloader({getOrigin:()=>[0,0],fetcher:async(_url,{signal})=>{attempts++;if(attempts===1)await new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(signal.reason),{once:true}));return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('one',0)]);const loading=preloader.start();while(!preloader.controller)await new Promise(resolve=>setTimeout(resolve,0));preloader.setPaused(true);
 await new Promise(resolve=>setTimeout(resolve,0));assert.equal(preloader.stats.done,0);preloader.setPaused(false);await loading;assert.equal(attempts,2);assert.equal(preloader.stats.done,1);
});

test('an immediate restart cannot be cancelled by the stopped run',async()=>{
 let attempts=0;const preloader=new ModelPreloader({getOrigin:()=>[0,0],fetcher:async(_url,{signal})=>{attempts++;if(attempts===1)await new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(signal.reason),{once:true}));return new Response(new Uint8Array(4));}});
 preloader.setModels([entry('one',0)]);void preloader.start();while(!preloader.controller)await new Promise(resolve=>setTimeout(resolve,0));
 preloader.stop();await preloader.start();
 assert.equal(attempts,2);assert.equal(preloader.stats.active,false);assert.equal(preloader.stats.done,1);
});
