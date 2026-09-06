// Bounded asynchronous asset lifecycle; deliberately independent of Three.js.
export class TileCache {
  constructor({load,dispose,limit=30,concurrency=2,onChange=()=>{}}){
    Object.assign(this,{load,dispose,limit,concurrency,onChange});
    this.entries=new Map();this.running=new Map();this.errors=new Map();this.wanted=[];this.listeners=new Set();this.closed=false;
  }
  notify(){this.onChange();for(const fn of [...this.listeners])fn();}
  plan(ids){
    if(this.closed)return;
    this.wanted=[...new Set(ids)].slice(0,this.limit);
    for(const [id,c] of this.running)if(!this.wanted.includes(id))c.abort();
    this.evict();this.notify();this.pump();
  }
  evict(){
    for(const [id,value] of this.entries){
      if(this.entries.size<=this.limit-this.running.size)break;
      if(!this.wanted.includes(id)){this.entries.delete(id);this.dispose(value);}
    }
  }
  pump(){
    if(this.closed)return;
    for(const id of this.wanted){
      if(this.running.size>=this.concurrency)break;
      if(this.entries.has(id)||this.running.has(id)||this.errors.has(id))continue;
      const controller=new AbortController();this.running.set(id,controller);this.evict();
      Promise.resolve().then(()=>this.load(id,controller.signal)).then(value=>{
        if(this.closed||controller.signal.aborted||!this.wanted.includes(id))this.dispose(value);
        else{this.entries.delete(id);this.entries.set(id,value);}
      }).catch(error=>{
        if(!controller.signal.aborted&&!this.closed)this.errors.set(id,error);
      }).finally(()=>{this.running.delete(id);this.evict();this.notify();this.pump();});
    }
  }
  ready(ids){return ids.every(id=>this.entries.has(id));}
  waitFor(ids){
    return new Promise((resolve,reject)=>{
      const check=()=>{
        const error=ids.map(id=>this.errors.get(id)).find(Boolean);
        const cancelled=this.closed||ids.some(id=>!this.wanted.includes(id));
        if(error||cancelled||this.ready(ids)){
          this.listeners.delete(check);
          if(error)reject(error);else if(cancelled)reject(new DOMException('District changed','AbortError'));else resolve();
        }
      };
      this.listeners.add(check);check();
    });
  }
  retry(){for(const id of this.wanted)this.errors.delete(id);this.notify();this.pump();}
  close(){this.closed=true;for(const c of this.running.values())c.abort();for(const value of this.entries.values())this.dispose(value);this.entries.clear();this.notify();}
}
export function distanceToBounds(x,z,b){return Math.hypot(Math.max(b[0]-x,0,x-b[2]),Math.max(b[1]-z,0,z-b[3]));}
export function nearbyTiles(tiles,x,z,radius,limit=24){
 return tiles.map(t=>[t,distanceToBounds(x,z,t.bounds)])
  .filter(([,d])=>d<=radius).sort((a,b)=>a[1]-b[1]||Math.hypot(a[0].centre[0]-x,a[0].centre[1]-z)-Math.hypot(b[0].centre[0]-x,b[0].centre[1]-z))
  .slice(0,limit).map(([t])=>t.id);
}
