import * as THREE from '../vendor/three.module.js';
import {GLTFLoader} from '../vendor/GLTFLoader.js';
import {AircraftModel,aircraftById} from './aircraft.js';
const clamp=THREE.MathUtils.clamp;
const FORWARD=new THREE.Vector3(),RIGHT=new THREE.Vector3(),TARGET=new THREE.Vector3(),EYE=new THREE.Vector3();
// Keep the whole craft inside the narrower horizontal field of view on portrait screens.
// Account for both span and fuselage length when the player looks around the aircraft.
export function aircraftChaseDistance(definition,camera,lookYaw=0){
 const baseline=Math.max(48,Math.max(definition.length,definition.wingspan)*1.55);
 const tangent=Math.tan(THREE.MathUtils.degToRad(camera.getEffectiveFOV())*.5)*Math.max(.1,camera.aspect);
 const c=Math.abs(Math.cos(lookYaw)),s=Math.abs(Math.sin(lookYaw));
 const halfWidth=(definition.wingspan*c+definition.length*s)*.5;
 const halfDepth=(definition.length*c+definition.wingspan*s)*.5;
 return Math.max(baseline,halfWidth/(tangent*.84)+halfDepth);
}
// Tide gates use the resting level; short wave chop must not toggle foot access.
export function waterAllowsStep(ground,waterLevel,previousGround=Infinity){
 if(!Number.isFinite(ground)||!Number.isFinite(waterLevel))return false;
 return ground+.2>=waterLevel||(previousGround+.2<waterLevel&&ground>=previousGround-1e-6);
}
const MOVE_KEYS=new Set(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight','Space']);
export class Navigation {
 constructor({camera,controls,scene,canvas,sampler,index,toast,onMode,waterLevel=()=>.3,waterSurface=waterLevel}){
  Object.assign(this,{camera,controls,scene,canvas,sampler,index,toast,onMode,waterLevel,waterSurface});
  this.mode='orbit';this.keys=new Set();this.position=new THREE.Vector3();this.heading=0;this.pitch=0;this.lookPitch=.12;this.lookYaw=0;this.speed=62;this.distance=0;this.firstPerson=false;this.drag=null;this.lastContact=-10;this.time=0;
  this.walker=new THREE.Group();this.plane=new THREE.Group();scene.add(this.walker,this.plane);this.walker.visible=this.plane.visible=false;
  this.aircraft=new AircraftModel({target:this.plane});
  this.makeActors();
  addEventListener('keydown',e=>{if(e.defaultPrevented||(e.code==='Space'&&e.target.closest?.('button,a'))||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable||document.querySelector('dialog[open]'))return;if(MOVE_KEYS.has(e.code)&&this.mode!=='orbit'){e.preventDefault();this.keys.add(e.code);}if(e.code==='KeyC'&&this.mode!=='orbit'&&!e.repeat)this.firstPerson=!this.firstPerson;});
  addEventListener('keyup',e=>this.keys.delete(e.code));addEventListener('blur',()=>this.clearInput());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)this.clearInput();});
  canvas.addEventListener('pointerdown',e=>{if(this.mode==='orbit'||e.button!==0)return;this.drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!this.drag||e.pointerId!==this.drag.id)return;const dx=e.clientX-this.drag.x,dy=e.clientY-this.drag.y;this.drag.x=e.clientX;this.drag.y=e.clientY;if(this.mode==='walk'){this.heading+=dx*.004;this.lookPitch=clamp(this.lookPitch+dy*.004,-.9,.85);}else{this.lookYaw+=dx*.004;this.lookPitch=clamp(this.lookPitch+dy*.004,-.8,.8);}});
  const release=e=>{if(this.drag?.id===e.pointerId)this.drag=null;};canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);canvas.addEventListener('lostpointercapture',release);
  document.querySelectorAll('[data-key]').forEach(button=>{button.addEventListener('pointerdown',e=>{e.preventDefault();button.setPointerCapture(e.pointerId);this.keys.add(button.dataset.key);});for(const event of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(event,()=>this.keys.delete(button.dataset.key));});
 }
 clearInput(){this.keys.clear();this.drag=null;}
 makeActors(){
  const body=new THREE.Mesh(new THREE.CapsuleGeometry(.23,.85,4,8),new THREE.MeshStandardMaterial({color:'#ba684a'}));body.position.y=.95;this.walker.add(body);
  const head=new THREE.Mesh(new THREE.SphereGeometry(.2,10,8),new THREE.MeshStandardMaterial({color:'#dbc9a0'}));head.position.y=1.64;this.walker.add(head);
  const loader=new GLTFLoader();
  const attach=(url,target,height,width,rotation=0)=>loader.load(url,gltf=>{
   const model=gltf.scene;model.updateMatrixWorld(true);
   const wrapper=new THREE.Group();wrapper.rotation.y=rotation;wrapper.add(model);wrapper.updateMatrixWorld(true);
   const box=new THREE.Box3().setFromObject(wrapper),size=box.getSize(new THREE.Vector3()),centre=box.getCenter(new THREE.Vector3());
   const scale=height?height/Math.max(.01,size.y):width/Math.max(.01,size.x,size.z);
   wrapper.scale.setScalar(scale);wrapper.position.set(-centre.x*scale,height?-box.min.y*scale:-centre.y*scale,-centre.z*scale);
   for(const child of [...target.children]){target.remove(child);child.traverse(m=>{m.geometry?.dispose();if(m.material)for(const mat of [].concat(m.material))mat.dispose();});}
   target.add(wrapper);model.traverse(m=>{if(m.isMesh){m.castShadow=true;m.receiveShadow=true;}if(m.isSkinnedMesh)m.frustumCulled=false;});
   if(height&&gltf.animations.length){
    this.mixer=new THREE.AnimationMixer(model);this.actions={};
    for(const name of ['Idle','Walk','Run']){const clip=gltf.animations.find(c=>c.name.endsWith('|'+name)||c.name===name);if(clip)this.actions[name]=this.mixer.clipAction(clip);}
   }

  },undefined,()=>{}); // Bundled primitive fallback still makes navigation fully usable.
  attach('data/models/hiker-adventurer.glb',this.walker,1.8,null,Math.PI);
  this.setAircraft('prop');
 }
 get aircraftState(){return this.aircraft.state;}
 setAircraftLighting(settings){this.aircraft.setLighting(settings);}
 get aircraftEnvelope(){const d=aircraftById(this.aircraft.id),height=this.aircraft.state.dimensions?.height||d.length*.25;return {extent:Math.max(d.length,d.wingspan),radius:Math.max(6,d.wingspan*.5,d.length*.46),bottom:Math.max(3,height*.35),top:Math.max(3,height*.75)};}
 async setAircraft(id){
  const pending=this.aircraft.setAircraft(id);
  // A larger replacement must not start with its wings inside an adjacent tower.
  const clear=()=>{if(this.mode!=='fly')return;const e=this.aircraftEnvelope;this.position.y=Math.max(this.position.y,this.index.maximumRoof(this.position.x,this.position.z,e.radius)+e.bottom+25);};
  clear();const loaded=await pending;clear();return loaded;
 }
 safeGround(x,z){
  const valid=(px,pz)=>this.sampler.contains(px,pz)&&this.sampler.raw(px,pz)>.5&&waterAllowsStep(this.sampler.height(px,pz),this.waterLevel())&&!this.index.collision(px,pz,this.sampler.height(px,pz),this.sampler.height(px,pz)+1.8,.65);
  if(valid(x,z))return new THREE.Vector3(x,this.sampler.height(x,z),z);
  for(let r=3;r<300;r+=3)for(let i=0;i<24;i++){const px=x+Math.cos(i*Math.PI/12)*r,pz=z+Math.sin(i*Math.PI/12)*r;if(valid(px,pz))return new THREE.Vector3(px,this.sampler.height(px,pz),pz);}
  return null;
 }
 setMode(mode,spawn){
  this.clearInput();this.lookYaw=0;this.lookPitch=.12;this.firstPerson=false;
  if(mode==='walk'){
    const safe=this.safeGround(spawn[0],spawn[1]);if(!safe){this.toast('No clear ground here. Choose another neighbourhood.');return false;}
    this.position.copy(safe);this.heading=0;this.distance=0;
  }else if(mode==='fly'){
    this.position.set(spawn[0]+600,Math.max(500,this.sampler.height(...spawn)+300),spawn[1]-1000);this.heading=Math.PI+.15;this.lookPitch=.65;this.pitch=0;this.speed=62;
    // Clear any tall structures near the starting point.
    this.position.y=Math.max(this.position.y,this.index.maximumRoof(this.position.x,this.position.z,this.aircraftEnvelope.radius)+100);
  }else if(this.mode!=='orbit'){
    this.controls.target.copy(this.position);this.camera.position.copy(this.position).add(new THREE.Vector3(260,230,320));this.controls.update();
  }
  this.mode=mode;this.controls.enabled=mode==='orbit';this.walker.visible=mode==='walk';this.plane.visible=mode==='fly';this.onMode(mode);return true;
 }
 update(dt){
  if(this.mode==='orbit')return;this.time+=dt;
  const pressed=(...keys)=>keys.some(k=>this.keys.has(k));
  if(this.mode==='walk'){
   const f=Number(pressed('KeyW','ArrowUp'))-Number(pressed('KeyS','ArrowDown')),s=Number(pressed('KeyD'))-Number(pressed('KeyA'));
   this.heading+=(Number(pressed('ArrowRight'))-Number(pressed('ArrowLeft')))*dt*1.5;
   const speed=pressed('ShiftLeft','ShiftRight')?8:3.9,n=Math.hypot(f,s)||1;
   const dx=(Math.sin(this.heading)*f+Math.cos(this.heading)*s)/n*speed*dt,dz=(-Math.cos(this.heading)*f+Math.sin(this.heading)*s)/n*speed*dt;
   const step=(x,z)=>{if(!this.sampler.contains(x,z)||this.sampler.raw(x,z)<=.5)return false;const y=this.sampler.height(x,z),d=Math.hypot(x-this.position.x,z-this.position.z);return waterAllowsStep(y,this.waterLevel(),this.position.y)&&Math.abs(y-this.position.y)<Math.max(.1,d*.95)&&!this.index.collision(x,z,y,y+1.8,.55);};
   // Small swept steps stop thin walls being skipped, even after a slow frame.
   const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.35));
   for(let i=0;i<steps;i++){
    const before=this.position.clone();if(step(this.position.x+dx/steps,this.position.z))this.position.x+=dx/steps;if(step(this.position.x,this.position.z+dz/steps))this.position.z+=dz/steps;
    this.position.y=this.sampler.height(this.position.x,this.position.z);this.distance+=Math.hypot(this.position.x-before.x,this.position.z-before.z);
   }
   if(this.mixer){
    const name=(f||s)?(speed>4?'Run':'Walk'):'Idle',action=this.actions[name]||this.actions.Idle;
    if(action&&action!==this.currentAction){this.currentAction?.fadeOut(.2);action.reset().fadeIn(.2).play();this.currentAction=action;}
    this.mixer.update(dt);
   }
   this.walker.position.copy(this.position);this.walker.rotation.y=-this.heading;this.walker.visible=!this.firstPerson;
   FORWARD.set(Math.sin(this.heading),0,-Math.cos(this.heading));
   TARGET.copy(this.position).addScaledVector(FORWARD,this.firstPerson?8:1.2);TARGET.y+=(this.firstPerson?1.6:1.3)-this.lookPitch*(this.firstPerson?8:5);
   EYE.copy(this.position);if(this.firstPerson)EYE.y+=1.68;else{EYE.addScaledVector(FORWARD,-7);EYE.y+=3.2;EYE.y=Math.max(EYE.y,this.sampler.height(EYE.x,EYE.z)+1);}
  }else{
   this.aircraft.update(dt);const envelope=this.aircraftEnvelope;
   const climb=Number(pressed('KeyW','ArrowUp'))-Number(pressed('KeyS','ArrowDown')),turn=Number(pressed('KeyD','ArrowRight'))-Number(pressed('KeyA','ArrowLeft'));
   this.heading+=turn*dt*.6;this.pitch=THREE.MathUtils.damp(this.pitch,climb*.48,2.5,dt);this.speed=THREE.MathUtils.damp(this.speed,pressed('ShiftLeft','ShiftRight')?125:62,1,dt);
   FORWARD.set(Math.sin(this.heading)*Math.cos(this.pitch),Math.sin(this.pitch),-Math.cos(this.heading)*Math.cos(this.pitch));
   const steps=Math.ceil(this.speed*dt/2);
   for(let i=0;i<steps;i++){
    const next=this.position.clone().addScaledVector(FORWARD,this.speed*dt/steps);
    if(!this.sampler.contains(next.x,next.z)){this.heading+=Math.PI;this.toast('Turning back towards Hong Kong.');break;}
    next.y=clamp(next.y,Math.max(this.sampler.height(next.x,next.z),this.waterLevel())+Math.max(18,envelope.bottom+8),2400);
    const hit=this.index.collision(next.x,next.z,next.y-envelope.bottom,next.y+envelope.top,envelope.radius);
    if(hit){this.position.y=Math.max(this.position.y,hit.base+hit.height+envelope.bottom+25);this.pitch=.35;if(this.time-this.lastContact>3){this.toast('Building ahead — climbing to clear the roof.');this.lastContact=this.time;}break;}
    this.position.copy(next);
   }
   this.plane.position.copy(this.position);this.plane.rotation.set(this.pitch,-this.heading,-turn*.35,'YXZ');this.plane.visible=!this.firstPerson;
   const angle=this.heading+this.lookYaw;
   RIGHT.set(Math.sin(angle),0,-Math.cos(angle));
   const d=aircraftById(this.aircraft.id),lookDistance=Math.max(80,envelope.extent*1.7);
   EYE.copy(this.position).addScaledVector(RIGHT,this.firstPerson?d.length*.42:-aircraftChaseDistance(d,this.camera,this.lookYaw));EYE.y+=this.firstPerson?Math.max(1.5,d.length*.035):Math.max(13,envelope.extent*.37);
   TARGET.copy(this.position).addScaledVector(RIGHT,lookDistance);TARGET.y+=this.pitch*lookDistance-this.lookPitch*Math.max(45,envelope.extent*.65);
  }
  if(this.mode==='walk'&&!this.firstPerson){
   const head=this.position.clone().add(new THREE.Vector3(0,1.65,0)),boom=EYE.clone().sub(head),length=boom.length();
   for(let d=.5;d<=length;d+=.3){const p=head.clone().addScaledVector(boom,d/length);if(this.index.collision(p.x,p.z,p.y-.2,p.y+.2,.2)||p.y<this.sampler.height(p.x,p.z)+.25){EYE.copy(head).addScaledVector(boom,Math.max(0,d-.4)/length);break;}}
  }
  EYE.y=Math.max(EYE.y,this.waterSurface()+.25);
  this.camera.position.lerp(EYE,1-Math.exp(-dt*(this.firstPerson?25:7)));this.camera.position.y=Math.max(this.camera.position.y,this.waterSurface()+.25);this.camera.lookAt(TARGET);
 }
}
