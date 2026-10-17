import {normaliseHour,formatHour} from './lighting.js';
export function hourAtPoint(x,y){return normaliseHour(Math.atan2(x,-y)*12/Math.PI);}
export function hourFromInput(value){
 const m=/^(\d{2}):(\d{2})$/.exec(value);if(!m||+m[1]>23||+m[2]>59)return null;
 return +m[1]+m[2]/60;
}
export function updateClockDial(dial,hour,phase){
 const angle=normaliseHour(hour)*Math.PI/12,x=Math.sin(angle),y=-Math.cos(angle);
 for(const [selector,attrs] of [['.clock-hand',{x1:80+x*43,y1:80+y*43,x2:80+x*59,y2:80+y*59}],['.clock-thumb',{cx:80+x*59,cy:80+y*59}]])
  for(const [k,v] of Object.entries(attrs))dial.querySelector(selector).setAttribute(k,v);
 dial.setAttribute('aria-valuenow',String(Math.round(normaliseHour(hour)*60)%1440));
 dial.setAttribute('aria-valuetext',`${formatHour(hour)} · ${phase}`);
}
export function bindClockDial(dial,{getHour,onChange}){
 const ticks=dial.querySelector('.clock-ticks');
 for(let h=0;h<24;h++){
  const angle=h*Math.PI/12,line=document.createElementNS('http://www.w3.org/2000/svg','line'),r=h%6===0?46:51;
  for(const [k,v] of Object.entries({x1:80+Math.sin(angle)*r,y1:80-Math.cos(angle)*r,x2:80+Math.sin(angle)*55,y2:80-Math.cos(angle)*55}))line.setAttribute(k,v);
  ticks.append(line);
 }
 let pointer=null;
 const select=e=>{const b=dial.getBoundingClientRect(),x=e.clientX-b.x-b.width/2,y=e.clientY-b.y-b.height/2;if(Math.hypot(x,y)<b.width*.16)return;onChange(normaliseHour(Math.round(hourAtPoint(x,y)*12)/12));};
 dial.addEventListener('pointerdown',e=>{if(e.button!==0||pointer!==null)return;e.preventDefault();dial.focus({preventScroll:true});pointer=e.pointerId;dial.setPointerCapture(pointer);select(e);});
 dial.addEventListener('pointermove',e=>{if(e.pointerId===pointer)select(e);});
 dial.addEventListener('pointerup',e=>{if(e.pointerId===pointer){select(e);dial.releasePointerCapture(pointer);pointer=null;}});
 for(const event of ['pointercancel','lostpointercapture'])dial.addEventListener(event,()=>pointer=null);
 dial.addEventListener('keydown',e=>{
  const step=e.shiftKey?1/12:.25,delta={ArrowRight:step,ArrowUp:step,ArrowLeft:-step,ArrowDown:-step,PageUp:1,PageDown:-1}[e.key];
  if(delta===undefined&&!['Home','End'].includes(e.key))return;
  e.preventDefault();e.stopPropagation();onChange(e.key==='Home'?0:e.key==='End'?23.75:normaliseHour(getHour()+delta));
 });
}
