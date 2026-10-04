import {streamingMetrics as metrics} from './streaming-metrics.js';
/** Bounded compressed source cache. A camera change cannot cancel a shared download. */
export class ModelByteCache {
 constructor({maxBytes=32*1024*1024,maxEntries=96,maxPending=8}={}){Object.assign(this,{maxBytes,maxEntries,maxPending});this.entries=new Map();this.pending=new Map();this.queue=[];this.bytes=0;this.running=0;this.closed=false;this.hits=0;this.requests=0;}
 key(entry){return entry.assetURL+'|'+entry.sha256;}
 delete(entry){const key=this.key(entry),old=this.entries.get(key);if(old){this.bytes-=old.byteLength;this.entries.delete(key);}}
 get(entry,{fetcher=fetch}={}){
  if(this.closed)return Promise.reject(new DOMException('Closed','AbortError'));
  const key=this.key(entry),hit=this.entries.get(key);if(hit){this.hits++;metrics.count('modelSourceCacheHits');this.entries.delete(key);this.entries.set(key,hit);return Promise.resolve(hit);}
  if(this.pending.has(key)){this.hits++;metrics.count('modelSourceCacheHits');return this.pending.get(key).promise;}
  if(!Number.isSafeInteger(entry.bytes)||entry.bytes<=0)return Promise.reject(new Error('Invalid model source byte count'));
  if(this.pending.size>=this.maxPending)return Promise.reject(new Error('Compressed source queue is full; Retry when settled'));
  if(entry.bytes>this.maxBytes)return Promise.reject(new Error('Model source exceeds compressed cache budget'));
  let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;}),controller=new AbortController();
  this.pending.set(key,{promise,controller});this.queue.push({entry,key,fetcher,resolve,reject,controller});this.pump();return promise;
 }
 pump(){
  if(this.closed)return;
  while(this.running<1&&this.queue.length){
   const job=this.queue.shift();this.running++;
   // Reserve enough room for the bounded response before starting a transfer.
   while(this.entries.size&&(this.bytes+job.entry.bytes>this.maxBytes||this.entries.size>=this.maxEntries)){const key=this.entries.keys().next().value;this.bytes-=this.entries.get(key).byteLength;this.entries.delete(key);}
   this.requests++;metrics.count('modelRequests');
   const finish=()=>{this.running--;this.pending.delete(job.key);this.pump();};
   this.read(job).then(bytes=>{if(!this.closed){this.entries.set(job.key,bytes);this.bytes+=bytes.byteLength;}finish();job.resolve(bytes);},error=>{finish();job.reject(error);});
  }
 }
 async read({entry,fetcher,controller}){
  const response=await fetcher(entry.assetURL,{signal:controller.signal,cache:'force-cache'});if(!response.ok)throw new Error('Official model HTTP '+response.status);
  const reader=response.body.getReader(),bytes=new Uint8Array(entry.bytes);let at=0;
  try{for(;;){const {value,done}=await reader.read();if(done)break;if(at+value.byteLength>bytes.byteLength)throw new Error('Model response exceeds declared byte count');bytes.set(value,at);at+=value.byteLength;}}
  catch(error){await reader.cancel().catch(()=>{});throw error;}finally{reader.releaseLock();}
  if(at!==entry.bytes)throw new Error('Model response byte count mismatch');return bytes;
 }
 close(){this.closed=true;for(const job of this.queue)job.reject(new DOMException('Closed','AbortError'));this.queue=[];for(const {controller} of this.pending.values())controller.abort();this.pending.clear();this.entries.clear();this.bytes=0;}
 get stats(){return {bytes:this.bytes,entries:this.entries.size,pending:this.pending.size,running:this.running,hits:this.hits,requests:this.requests,maxBytes:this.maxBytes,maxEntries:this.maxEntries};}
}
/** Yield between indivisible stages; fallback bakes have their own bounded worker queue. */
export function yieldModelWork(signal){
 if(signal?.aborted)return Promise.reject(new DOMException('Aborted','AbortError'));
 if(typeof requestAnimationFrame!=='function')return Promise.resolve();
 return new Promise((resolve,reject)=>{
  let frame,timer,settled=false;
  const done=()=>{if(settled)return;settled=true;clearTimeout(timer);cancelAnimationFrame(frame);signal?.removeEventListener('abort',done);signal?.aborted?reject(new DOMException('Aborted','AbortError')):resolve();};
  signal?.addEventListener('abort',done,{once:true});timer=setTimeout(done,50);frame=requestAnimationFrame(()=>{clearTimeout(timer);timer=setTimeout(done,0);});
 });
}
