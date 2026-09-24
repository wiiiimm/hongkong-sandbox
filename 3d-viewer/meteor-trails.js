// Extracted from main.js HKS-85 (5777bc9): the original reusable meteor pool,
// blue-white trail colours, spherical arcs, lifetimes, fade and rate mapping.
// Both the original viewer and City use this implementation. No meteor catalogue
// or observed shower rate is implied: Calm/Romantic/Apocalypse are visual settings.
import * as THREE from './vendor/three.module.js';
export const METEOR_N=20,METEOR_POOL=14;
export const METEOR_DEFAULTS=Object.freeze({enabled:true,rate:.18});
const clampRate=rate=>Math.max(0,Math.min(1,rate));
export const meteorGap=rate=>30*Math.pow(.004,clampRate(rate));
export const meteorCap=rate=>Math.max(1,Math.round(METEOR_POOL*Math.pow(clampRate(rate),1.3)));
export function meteorRateLabel(rate){return rate<=0?'Off':rate<.42?'Calm':rate<.82?'Romantic':'Apocalypse';}

/** Bounded shared effect. `step` takes absolute effect-clock seconds, not a date.
 * parent may be a scene or group; meteor positions are local horizontal axes:
 * east +x, up +y, north -z. `radius` uses the viewer's world units.
 */
export function createMeteorTrails({parent,random=Math.random,enabled=true,rate=.18,fog=true}={}){
 const group=new THREE.Group();group.name='Shooting stars';parent?.add(group);
 const point=new THREE.Vector3(),tangent=new THREE.Vector3();
 let settings={enabled:!!enabled,rate:Number.isFinite(rate)?clampRate(rate):METEOR_DEFAULTS.rate},next=null,disposed=false,spawned=0;
 function makeMeteor(){
  const pos=new Float32Array(METEOR_N*3),col=new Float32Array(METEOR_N*3);
  for(let j=0;j<METEOR_N;j++){
   const w=Math.pow(1-j/(METEOR_N-1),1.6);
   col[j*3]=(.75+.25*w)*w;col[j*3+1]=(.85+.15*w)*w;col[j*3+2]=w;
  }
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));geometry.setAttribute('color',new THREE.BufferAttribute(col,3));
  const line=new THREE.Line(geometry,new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog}));
  line.visible=false;line.frustumCulled=false;group.add(line);
  return {line,t0:0,dur:1,active:false,A:new THREE.Vector3(),B:new THREE.Vector3()};
 }
 const pool=Array.from({length:METEOR_POOL},makeMeteor);
 function hide(){for(const mo of pool){mo.active=false;mo.line.visible=false;mo.line.material.opacity=0;}next=null;}
 function spawn(mo,time){
  const az=random()*Math.PI*2,alt=(20+45*random())*Math.PI/180;
  mo.A.set(Math.sin(az)*Math.cos(alt),Math.sin(alt),-Math.cos(az)*Math.cos(alt));
  tangent.set(random()-.5,random()-.5,random()-.5);
  tangent.addScaledVector(mo.A,-tangent.dot(mo.A)).normalize();
  if(tangent.y>.15)tangent.multiplyScalar(-1);
  mo.B.copy(mo.A).addScaledVector(tangent,.18+.22*random()).normalize();
  mo.t0=time;mo.dur=.7+.6*random();mo.active=true;mo.line.visible=true;
  // A reused trail must not flash its previous arc during the birth frame.
  mo.line.material.opacity=0;spawned++;
 }
 function setOptions(options={}){
  if(disposed)return;
  if(options.enabled!==undefined)settings.enabled=!!options.enabled;
  if(Number.isFinite(options.rate)&&clampRate(options.rate)!==settings.rate){settings.rate=clampRate(options.rate);next=null;}
  if(!settings.enabled||settings.rate===0)hide();
 }
 function step(time,{starFade=0,radius=1}={}){
  if(disposed)return;
  if(!Number.isFinite(time)||!Number.isFinite(radius)||radius<=0||!Number.isFinite(starFade)||starFade<.55||!settings.enabled||settings.rate<=0){hide();return;}
  let live=0;
  for(const mo of pool){
   if(!mo.active)continue;
   const p=(time-mo.t0)/mo.dur;
   if(p>1.4||p<0){mo.active=false;mo.line.visible=false;mo.line.material.opacity=0;continue;}
   live++;const array=mo.line.geometry.attributes.position.array;
   for(let j=0;j<METEOR_N;j++){
    const pj=Math.max(0,Math.min(1,p-.35*j/(METEOR_N-1)));
    point.copy(mo.A).lerp(mo.B,pj).normalize().multiplyScalar(radius);
    array[j*3]=point.x;array[j*3+1]=point.y;array[j*3+2]=point.z;
   }
   mo.line.geometry.attributes.position.needsUpdate=true;
   mo.line.material.opacity=.85*Math.min(1,p*5)*Math.max(0,1-Math.max(0,p-1)/.4);
  }
  const gap=meteorGap(settings.rate),cap=meteorCap(settings.rate);
  if(next===null)next=time+random()*gap;
  let guard=0;
  while(time>=next&&guard++<METEOR_POOL){
   if(live<cap){const free=pool.find(m=>!m.active);if(free){spawn(free,time);live++;}}
   next+=gap*(.4+1.2*random());
  }
 }
 return {group,pool,step,setOptions,hide,reschedule(){if(!disposed)next=null;},
  get state(){return {...settings,rateLabel:meteorRateLabel(settings.rate),gapSeconds:meteorGap(settings.rate),concurrencyLimit:meteorCap(settings.rate),active:pool.filter(m=>m.active).length,visibleTrails:pool.filter(m=>m.line.visible&&m.line.material.opacity>0).length,poolSize:pool.length,spawned,disposed};},
  dispose(){if(disposed)return;disposed=true;hide();group.removeFromParent();for(const mo of pool){mo.line.geometry.dispose();mo.line.material.dispose();}}
 };
}
