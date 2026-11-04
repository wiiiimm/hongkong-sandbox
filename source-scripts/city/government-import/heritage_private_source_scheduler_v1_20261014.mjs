/** Private fixture instance only: same unpause behavior as working Aqua browser. */
export function installPrivateSourceScheduler(r,timers=globalThis){
 const official=r.officialModels,original=official.setLoadingPaused,unpause=original.bind(official);let selected=null,timer=null,lastError=null;
 official.setLoadingPaused=paused=>{if(!paused)unpause(false);};
 function pump(){if(!selected)return;unpause(false);official.plan(r.camera,{viewportWidth:timers.innerWidth,viewportHeight:timers.innerHeight,selectedUid:selected,allowNewLoads:true,force:true});}
 return{start(uid){if(typeof uid!=='string'||!uid)throw Error('Exact requested UID required');if(timer!==null)timers.clearInterval(timer);selected=uid;pump();timer=timers.setInterval(()=>{try{pump();}catch(e){lastError=String(e?.stack??e);}},200);},get lastError(){return lastError;},stop(){if(timer!==null)timers.clearInterval(timer);timer=null;selected=null;official.setLoadingPaused=original;}};
}
