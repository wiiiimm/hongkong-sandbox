import {streamingMetrics as metrics} from './streaming-metrics.js';
// Two CPU workers, at most 32 queued tile/fallback jobs. Input records are cloned,
// never transferred: source arrays remain authoritative for picking/collision.
const queue=[],workers=new Set();let running=0;
export function bakeBuildingBuffers(features,signal){
 if(signal?.aborted)return Promise.reject(new DOMException('Aborted','AbortError'));
 if(queue.length>=32)return Promise.reject(new Error('Building bake queue full; retry after streaming settles'));
 return new Promise((resolve,reject)=>{const job={features,signal,resolve,reject,queuedAt:metrics.start()};queue.push(job);pump();});
}
function pump(){
 while(running<2&&queue.length){
  const job=queue.shift();if(job.signal?.aborted){job.reject(new DOMException('Aborted','AbortError'));continue;}
  let worker;try{worker=new Worker(new URL('./building-bake-worker.js',import.meta.url),{type:'module'});}catch(error){job.reject(error);continue;}workers.add(worker);running++;metrics.end('fallbackQueueMs',job.queuedAt);
  let done=false;
  const finish=(error,value)=>{if(done)return;done=true;worker.terminate();workers.delete(worker);running--;job.signal?.removeEventListener('abort',cancel);error?job.reject(error):job.resolve(value);pump();};
  const cancel=()=>finish(new DOMException('Aborted','AbortError'));
  worker.onmessage=e=>{metrics.record('fallbackWorkerMs',e.data.workMs);e.data.error?finish(new Error(e.data.error)):finish(null,e.data);};
  worker.onerror=e=>finish(new Error(e.message||'Building worker failed'));
  job.signal?.addEventListener('abort',cancel,{once:true});try{worker.postMessage(job.features);}catch(error){finish(error);}
 }
}
