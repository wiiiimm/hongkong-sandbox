import * as THREE from '../vendor/three.module.js';

// A bounded compositor effect: no duplicate meshes, render targets or geometry edits.
export class ModelReveal {
 constructor(canvas){this.canvas=canvas;this.items=[];this.point=new THREE.Vector3();}
 start(entry){
  if(!globalThis.CSS?.supports('backdrop-filter','blur(1px)')&&!globalThis.CSS?.supports('-webkit-backdrop-filter','blur(1px)'))return;
  if(this.items.length>=3)this.remove(this.items[0]);
  const element=document.createElement('div');element.className='model-reveal';element.setAttribute('aria-hidden','true');
  Object.assign(element.style,{position:'fixed',pointerEvents:'none',zIndex:'1',borderRadius:'24px',maskImage:'radial-gradient(ellipse, black 45%, transparent 72%)',webkitMaskImage:'radial-gradient(ellipse, black 45%, transparent 72%)'});
  document.body.append(element);this.items.push({entry,element,start:performance.now()});
 }
 remove(item){item.element.remove();this.items.splice(this.items.indexOf(item),1);}
 update(camera,now,{reduced=false,interacting=false}={}){
  if(!this.items.length)return;
  const rect=this.canvas.getBoundingClientRect();camera.updateMatrixWorld(true);
  for(const item of [...this.items]){
   const t=Math.max(0,(now-item.start)/650),{entry,element}=item;
   if(t>=1||reduced||interacting||!entry.active||!entry.group.visible){this.remove(item);continue;}
   let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity,clipped=false;
   for(let i=0;i<8;i++){
    this.point.set(i&1?entry.bounds.max.x:entry.bounds.min.x,i&2?entry.bounds.max.y:entry.bounds.min.y,i&4?entry.bounds.max.z:entry.bounds.min.z).project(camera);
    if(this.point.z < -1||this.point.z > 1){clipped=true;break;}
    const x=(this.point.x+1)*rect.width/2,y=(1-this.point.y)*rect.height/2;
    left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);
   }
   // Avoid expensive near-camera/full-screen blur and tiny distant flashes.
   if(clipped||right<0||bottom<0||left>rect.width||top>rect.height||right-left<12||bottom-top<12||(right-left)*(bottom-top)>rect.width*rect.height*.3){this.remove(item);continue;}
   const pad=18,blur=5*(1-t)*(1-t);
   Object.assign(element.style,{left:`${rect.left+left-pad}px`,top:`${rect.top+top-pad}px`,width:`${right-left+pad*2}px`,height:`${bottom-top+pad*2}px`,backdropFilter:`blur(${blur}px)`,webkitBackdropFilter:`blur(${blur}px)`,opacity:String(1-t*t)});
  }
 }
 dispose(){for(const item of [...this.items])this.remove(item);}
}
