const distanceSquared=(entry,[x,z])=>{
 const bounds=entry.worldBounds,cx=(bounds[0][0]+bounds[1][0])/2,cz=(bounds[0][2]+bounds[1][2])/2;
 return (cx-x)**2+(cz-z)**2;
};

/** Warms the browser HTTP cache in geographic order without decoding models. */
export class ModelPreloader{
 constructor({getOrigin,getDirection=()=>null,fetcher=fetch,onChange=()=>{},byteCache=null,maxBytes=32*1024*1024,maxModels=96}){
  Object.assign(this,{getOrigin,getDirection,fetcher,onChange,byteCache,maxBytes,maxModels});this.sessionBytes=0;this.sessionModels=0;this.budgetReached=false;this.models=new Map();this.done=new Set();this.errors=new Map();this.active=false;this.paused=false;this.controller=null;this.promise=null;this.bytesDone=0;this.runToken=0;
 }
 setModels(models){this.models=new Map(models.map(entry=>[entry.uid,entry]));this.notify();}
 notify(){this.onChange(this.stats);}
 next(){
  const origin=this.getOrigin(),direction=this.getDirection();let best=null,bestDistance=Infinity;
  for(const entry of this.models.values()){
   if(this.done.has(entry.uid)||this.errors.has(entry.uid))continue;
   if(this.sessionModels>=this.maxModels||this.sessionBytes+entry.bytes>this.maxBytes){this.budgetReached=true;continue;}
   let distance=distanceSquared(entry,origin);if(direction){const b=entry.worldBounds,dx=(b[0][0]+b[1][0])/2-origin[0],dz=(b[0][2]+b[1][2])/2-origin[1],ahead=(dx*direction[0]+dz*direction[1])/Math.max(1,Math.hypot(dx,dz));distance*=1-.35*Math.max(0,ahead);}
   if(distance<bestDistance||(distance===bestDistance&&entry.priority==='landmark'&&best?.priority!=='landmark')){best=entry;bestDistance=distance;}
  }
  return best;
 }
 async start(){
  if(this.active)return this.promise;this.active=true;this.sessionBytes=0;this.sessionModels=0;this.budgetReached=false;this.errors.clear();this.notify();
  const token=++this.runToken;
  this.promise=this.run(token).finally(()=>{if(this.runToken===token){this.active=false;this.controller=null;this.notify();}});return this.promise;
 }
 stop(){if(!this.active)return;this.active=false;this.runToken++;this.controller?.abort();this.notify();}
 setPaused(paused){
  if(this.paused===paused)return;this.paused=paused;this.notify();
 }
 async waitUntilReady(token){while(this.active&&this.runToken===token&&this.paused)await new Promise(resolve=>setTimeout(resolve,100));}
 async run(token){
  while(this.active&&this.runToken===token){
   await this.waitUntilReady(token);if(!this.active||this.runToken!==token)break;
   const entry=this.next();if(!entry)break;
   const controller=new AbortController();this.controller=controller;
   try{
    let bytes;if(this.byteCache)bytes=await this.byteCache.get(entry,{fetcher:this.fetcher,signal:controller.signal});else{
    const response=await this.fetcher(entry.assetURL,{signal:controller.signal,cache:'force-cache'});
    if(!response.ok)throw new Error('HTTP '+response.status);
    bytes=await response.arrayBuffer();}if(bytes.byteLength!==entry.bytes)throw new Error('Unexpected byte count');
    if(this.runToken!==token)break;this.done.add(entry.uid);this.bytesDone+=entry.bytes;this.sessionBytes+=entry.bytes;this.sessionModels++;
   }catch(error){
    if(!controller.signal.aborted)this.errors.set(entry.uid,error.message);
   }finally{if(this.controller===controller)this.controller=null;this.notify();}
  }
 }
 retry(){this.errors.clear();return this.start();}
 get stats(){
  const models=[...this.models.values()],totalBytes=models.reduce((sum,entry)=>sum+entry.bytes,0);
  return {active:this.active,paused:this.paused,done:this.done.size,total:models.length,bytesDone:this.bytesDone,totalBytes,errors:this.errors.size,budgetReached:this.budgetReached,sessionBytes:this.sessionBytes,maxBytes:this.maxBytes,maxModels:this.maxModels,complete:!!models.length&&this.done.size+this.errors.size===models.length};
 }
}
