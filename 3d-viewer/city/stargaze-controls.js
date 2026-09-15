import * as THREE from '../vendor/three.module.js';
const clamp=THREE.MathUtils.clamp;
// A camera-centred sky view; keep the city's ordinary orbit pose for the return trip.
export class StargazeControls {
 constructor({camera,controls,canvas,onPick}){
  Object.assign(this,{camera,controls,canvas,onPick});this.active=false;this.yaw=0;this.pitch=.55;this.drag=null;
  canvas.addEventListener('pointerdown',e=>{
   if(!this.active||e.button!==0||this.drag)return;canvas.focus({preventScroll:true});
   this.drag={id:e.pointerId,x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY};canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove',e=>{
   if(!this.active||this.drag?.id!==e.pointerId)return;
   this.yaw-=(e.clientX-this.drag.x)*.004;this.pitch=clamp(this.pitch+(e.clientY-this.drag.y)*.004,-.08,Math.PI*.49);
   this.drag.x=e.clientX;this.drag.y=e.clientY;this.update();
  });
  canvas.addEventListener('pointerup',e=>{
   if(this.drag?.id!==e.pointerId)return;
   if(Math.hypot(e.clientX-this.drag.startX,e.clientY-this.drag.startY)<5)this.onPick?.({x:e.clientX/canvas.clientWidth*2-1,y:1-e.clientY/canvas.clientHeight*2});
   this.drag=null;
  });
  for(const event of ['pointercancel','lostpointercapture'])canvas.addEventListener(event,e=>{if(this.drag?.id===e.pointerId)this.drag=null;});
  canvas.addEventListener('wheel',e=>{if(!this.active)return;e.preventDefault();camera.fov=clamp(camera.fov+e.deltaY*.025,25,95);camera.updateProjectionMatrix();},{passive:false});
  canvas.addEventListener('keydown',e=>{
   if(!this.active||document.querySelector('dialog[open]'))return;
   const d={ArrowLeft:[-.06,0],ArrowRight:[.06,0],ArrowUp:[0,.06],ArrowDown:[0,-.06]}[e.key];if(!d)return;
   e.preventDefault();e.stopPropagation();this.yaw+=d[0];this.pitch=clamp(this.pitch+d[1],-.08,Math.PI*.49);this.update();
  });
 }
 enter(position){
  if(this.active)return;
  this.saved={position:this.camera.position.clone(),target:this.controls.target.clone(),fov:this.camera.fov};
  this.active=true;this.controls.enabled=false;this.camera.position.copy(position);this.camera.fov=75;this.camera.updateProjectionMatrix();this.update();
 }
 exit(){
  if(!this.active)return;this.active=false;this.drag=null;
  this.camera.position.copy(this.saved.position);this.controls.target.copy(this.saved.target);this.camera.fov=this.saved.fov;this.camera.updateProjectionMatrix();this.controls.enabled=true;this.controls.update();
 }
 face(bearing){this.yaw=bearing*Math.PI/180;this.pitch=.55;this.update();}
 update(){
  if(!this.active)return;
  const direction=new THREE.Vector3(Math.sin(this.yaw)*Math.cos(this.pitch),Math.sin(this.pitch),-Math.cos(this.yaw)*Math.cos(this.pitch));
  this.camera.lookAt(this.camera.position.clone().add(direction));
 }
 get state(){return {active:this.active,bearing:(this.yaw*180/Math.PI%360+360)%360,altitude:this.pitch*180/Math.PI};}
}
