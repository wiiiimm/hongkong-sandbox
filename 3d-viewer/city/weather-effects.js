// HKS-169: adapts main.js HKS-13 forked channels and HKS-2 audio to city metres.
import * as THREE from '../vendor/three.module.js';
import {createWeatherAudio} from './weather-audio.js';
export const DEFAULT_STORM=Object.freeze({lightning:false,thunderRate:.4});
export const MIN_STRIKE_INTERVAL=4;
const clamp=x=>Math.max(0,Math.min(1,x));
export function normaliseStorm(values={},previous=DEFAULT_STORM){
 return {lightning:typeof values.lightning==='boolean'?values.lightning:previous.lightning,
  thunderRate:Number.isFinite(values.thunderRate)?clamp(values.thunderRate):previous.thunderRate};
}
// Original midpoint-displaced main channel, recursively dying side forks. The
// city's exact terrain endpoint replaces the original normalised scene's y=0.
export function lightningChannel({x,z,ground=0,top=Math.max(1100,ground+600),span=2000,random=Math.random}){
 const vertices=[];
 const jag=(x0,y0,z0,x1,y1,z1,steps,amp,depth)=>{
  let px=x0,py=y0,pz=z0;
  for(let i=1;i<=steps;i++){
   const t=i/steps,nx=x0+(x1-x0)*t+(random()*2-1)*amp*(1-t),ny=y0+(y1-y0)*t,nz=z0+(z1-z0)*t+(random()*2-1)*amp*(1-t);
   vertices.push(px,py,pz,nx,ny,nz);
   if(depth>0&&i>2&&i<steps-2&&random()<.28)jag(nx,ny,nz,nx+(random()*2-1)*span*.08,Math.max(ny-(top-ground)*(.1+random()*.2),ground),nz+(random()*2-1)*span*.08,4+(random()*3|0),amp*.6,depth-1);
   px=nx;py=ny;pz=nz;
  }
 };
 jag(x+(random()*2-1)*span*.05,top,z+(random()*2-1)*span*.05,x,ground,z,14,span*.02,2);
 return new Float32Array(vertices);
}
export function createWeatherEffects({scene,camera,terrainHeight=()=>0,random=Math.random,audioOptions,documentRef=globalThis.document}={}){
 const audio=createWeatherAudio({...audioOptions,documentRef}),group=new THREE.Group();group.name='City storm · manual simulation';
 const material=new THREE.LineBasicMaterial({color:0xeaf4ff,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog:true});
 const bolt=new THREE.LineSegments(new THREE.BufferGeometry(),material);bolt.name='Forked lightning';bolt.visible=false;bolt.frustumCulled=false;
 const glow=new THREE.PointLight(0xcfe0ff,0,2200,2);glow.name='Local lightning glow';glow.visible=false;group.add(bolt,glow);scene.add(group);
 let manual={...DEFAULT_STORM},mode='manual',paused=false,suspended=false,reducedMotion=false,disposed=false,active=false,flash=0,life=0,count=0,lastStrike=null,clock=0,lastAt=-Infinity,wait=MIN_STRIKE_INTERVAL;
 const direction=new THREE.Vector3();
 function clear(){flash=0;life=0;bolt.visible=false;glow.intensity=0;material.opacity=0;}
 function gate(){return !disposed&&mode==='manual'&&manual.lightning&&manual.thunderRate>0&&!paused&&!suspended&&!documentRef?.hidden;}
 function nextInterval(){return MIN_STRIKE_INTERVAL-Math.log(Math.max(.000001,1-random()))/(.04+.5*manual.thunderRate**2);}
 function strike(){
  if(!gate()||clock-lastAt<MIN_STRIKE_INTERVAL)return false;
  const close=random()<.6;count++;lastAt=clock;wait=nextInterval();
  lastStrike={number:count,elapsed:clock,close,source:'Manual storm simulation'};
  audio.thunder(close,close?1:.65);
  if(reducedMotion){clear();return true;}
  flash=close?1:.55;life=.28;
  if(close){
   camera.getWorldDirection(direction);direction.y=0;if(direction.lengthSq()<.001)direction.set(0,0,-1);direction.normalize();
   const distance=650+random()*900,lateral=(random()-.5)*distance;
   const x=camera.position.x+direction.x*distance-direction.z*lateral,z=camera.position.z+direction.z*distance+direction.x*lateral;
   const sampled=terrainHeight(x,z),ground=Number.isFinite(sampled)?sampled:0,top=Math.max(1100,ground+600);
   const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(lightningChannel({x,z,ground,top,random}),3));
   bolt.geometry.dispose();bolt.geometry=geometry;bolt.visible=true;material.opacity=1;glow.position.set(x,ground+(top-ground)*.25,z);lastStrike.position={x,y:ground,z};
  }else bolt.visible=false;
  return true;
 }
 const visibility=()=>{if(documentRef?.hidden){clear();glow.visible=false;active=false;audio.cancelThunder();wait=Math.max(wait,MIN_STRIKE_INTERVAL);}};documentRef?.addEventListener('visibilitychange',visibility);
 return {
  setManual(values){manual=normaliseStorm(values,manual);if(!manual.lightning||manual.thunderRate===0){clear();audio.cancelThunder();}wait=Math.max(wait,MIN_STRIKE_INTERVAL);return {...manual};},
  setSound:(on,event)=>audio.setEnabled(on,event),
  setMasterVolume:value=>audio.setMasterVolume(value),
  triggerStrike:()=>strike(),
  update(dt,options={}){
   if(disposed)return {ambientBoost:0,flash:0};
   mode=options.mode||'manual';paused=!!options.paused;suspended=!!options.suspended;reducedMotion=!!options.reducedMotion;
   audio.update(options.settings,{paused,suspended});
   active=gate();glow.visible=active&&!reducedMotion;
   if(!active){clear();audio.cancelThunder();wait=Math.max(wait,MIN_STRIKE_INTERVAL);return {ambientBoost:0,flash:0};}
   const delta=Math.max(0,Math.min(.25,Number.isFinite(dt)?dt:0));clock+=delta;wait-=delta;
   if(reducedMotion)clear();
   else if(life>0){life=Math.max(0,life-delta);const fade=life/.28;material.opacity=fade;flash=Math.max(0,flash-delta*4);glow.intensity=bolt.visible?60000*fade:0;if(life===0)clear();}
   if(wait<=0)strike();
   return {ambientBoost:reducedMotion?0:flash*.75,flash:reducedMotion?0:flash};
  },
  get state(){return {manual:{...manual},mode,active,visualSuppressed:reducedMotion||suspended||paused||!!documentRef?.hidden,flash,strikes:count,lastStrike:lastStrike?structuredClone(lastStrike):null,source:'Manual storm simulation',sound:audio.state};},
  async dispose(){if(disposed)return;disposed=true;clear();documentRef?.removeEventListener('visibilitychange',visibility);scene.remove(group);bolt.geometry.dispose();material.dispose();await audio.dispose();},
 };
}
