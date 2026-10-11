/** Bounded, opt-in CPU/wall-time observations; no synchronous GPU queries. */
export class StreamingMetrics {
 constructor({enabled=false,capacity=600}={}){this.enabled=enabled;this.capacity=capacity;this.samples=new Map();this.counters=new Map();this.observer=null;}
 record(name,value){if(!this.enabled||!Number.isFinite(value))return;let s=this.samples.get(name);if(!s){s={values:[],cursor:0,count:0,total:0,max:0};this.samples.set(name,s);}s.count++;s.total+=value;s.max=Math.max(s.max,value);s.values[s.cursor]=value;s.cursor=(s.cursor+1)%this.capacity;}
 count(name,n=1){if(this.enabled)this.counters.set(name,(this.counters.get(name)||0)+n);}
 start(){return this.enabled?performance.now():0;}
 end(name,start){if(this.enabled)this.record(name,performance.now()-start);}
 observe(){if(!this.enabled||!globalThis.PerformanceObserver)return;try{this.observer=new PerformanceObserver(list=>{for(const e of list.getEntries())this.record('longTaskMs',e.duration);});this.observer.observe({type:'longtask',buffered:false});}catch{/* Unsupported in some browsers. */}}
 reset(){this.samples.clear();this.counters.clear();}
 get snapshot(){return {enabled:this.enabled,capacity:this.capacity,counters:Object.fromEntries(this.counters),samples:Object.fromEntries([...this.samples].map(([name,s])=>{const v=[...s.values].sort((a,b)=>a-b);return [name,{count:s.count,retained:v.length,total:s.total,max:s.max,median:v[Math.floor((v.length-1)*.5)]??0,p95:v[Math.floor((v.length-1)*.95)]??0}];}))};}
 dispose(){this.observer?.disconnect();}
}
export const streamingMetrics=new StreamingMetrics({enabled:typeof location!=='undefined'&&new URLSearchParams(location.search).get('streamingMetrics')==='1'});
