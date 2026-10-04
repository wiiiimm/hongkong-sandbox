import test from 'node:test';
import assert from 'node:assert/strict';
import {ModelByteCache} from '../model-byte-cache.js';
const meta=i=>({assetURL:'https://test/'+i,sha256:String(i),bytes:4});
test('source downloads deduplicate, reuse on reversal and evict within finite byte/count caps',async()=>{
 const cache=new ModelByteCache({maxBytes:8,maxEntries:2});let requests=0;const fetcher=async()=>{requests++;return new Response(new Uint8Array(4));};
 const [a,b]=await Promise.all([cache.get(meta(1),{fetcher}),cache.get(meta(1),{fetcher})]);assert.equal(a,b);assert.equal(requests,1);
 await cache.get(meta(2),{fetcher});await cache.get(meta(1),{fetcher});await cache.get(meta(3),{fetcher});assert.equal(cache.stats.bytes,8);assert.equal(cache.stats.entries,2);assert.equal(requests,3);assert.equal(cache.stats.running,0);
 await cache.get(meta(1),{fetcher});assert.equal(requests,3);cache.close();assert.equal(cache.stats.bytes,0);
});
test('oversized and failed sources are bounded and retryable',async()=>{
 const cache=new ModelByteCache({maxBytes:8});await assert.rejects(cache.get({...meta(1),bytes:9}),/budget/);
 await assert.rejects(cache.get(meta(1),{fetcher:async()=>new Response(new Uint8Array(5))}),/exceeds/);await new Promise(r=>setTimeout(r,0));
 assert.equal((await cache.get(meta(1),{fetcher:async()=>new Response(new Uint8Array(4))})).length,4);cache.close();
});
test('cancelling background-only reads releases the transfer and queued work without cancelling foreground subscribers',async()=>{
 const cache=new ModelByteCache();let release,networkSignal;
 const fetcher=(_url,{signal})=>new Promise((resolve,reject)=>{networkSignal=signal;release=()=>resolve(new Response(new Uint8Array(4)));signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')),{once:true});});
 const stop=new AbortController(),background=cache.get(meta(1),{fetcher,signal:stop.signal});
 const next=cache.get(meta(2),{fetcher:async()=>new Response(new Uint8Array(4))});stop.abort();await assert.rejects(background,{name:'AbortError'});assert.equal(networkSignal.aborted,true);await next;
 const stopShared=new AbortController(),shared=cache.get(meta(3),{fetcher,signal:stopShared.signal}),foreground=cache.get(meta(3),{fetcher});
 stopShared.abort();await assert.rejects(shared,{name:'AbortError'});assert.equal(networkSignal.aborted,false);release();assert.equal((await foreground).length,4);
 const active=cache.get(meta(4),{fetcher}),stopQueued=new AbortController(),queued=cache.get(meta(5),{fetcher,signal:stopQueued.signal});stopQueued.abort();await assert.rejects(queued,{name:'AbortError'});assert.equal(cache.queue.length,0);release();await active;cache.close();
});
