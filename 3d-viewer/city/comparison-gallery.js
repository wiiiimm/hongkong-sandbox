import * as T from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';

// One renderer draws visible DOM cells with scissors; no per-cell WebGL contexts.
export function createComparisonGallery(groups, assemble) {
 const host=document.createElement('section');host.id='comparison-gallery';host.hidden=true;
 host.innerHTML=`<div class="gallery-toolbar"><button id="gallery-play" aria-pressed="false">Play all</button><label>Motion <select id="gallery-motion"><option value="orbit">Orbit</option><option value="fly" selected>Drone fly-through</option></select></label><label>Speed <input id="gallery-speed" type="range" min="0.25" max="3" step="0.25" value="1"><output id="gallery-speed-value">1×</output></label><label>View size <input id="gallery-size" type="range" min="90" max="420" step="10" value="150"><output id="gallery-size-value">150 px</output></label><span>Each location is framed separately; its three versions stay in sync.</span></div><div class="gallery-head"><span>Location</span><span>Basic</span><span>Light</span><span>High</span></div><div class="gallery-rows"></div>`;
 document.getElementById('views').after(host);
 const renderer=new T.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.domElement.className='gallery-canvas';renderer.domElement.hidden=true;
 const rows=[];let active=false,playing=false,speed=1,motion='fly',last=0,dirty=true,elapsed=0,syncing=false;
 const play=host.querySelector('#gallery-play');
 const hoverCapable=matchMedia('(hover: hover) and (pointer: fine)');
 let hoveredCell=null,hoverUntil=0;
 function setHovered(cell){hoveredCell?.classList.remove('is-hovered');hoveredCell=cell;cell?.classList.add('is-hovered');hoverUntil=performance.now()+240;dirty=true;}
 function setPlaying(value){playing=value;last=0;play.textContent=value?'Pause all':'Play all';play.setAttribute('aria-pressed',String(value));}
 for(const [i,group]of groups.entries()){
  const assembly=assemble(group),row=document.createElement('article');row.className='gallery-row';const name=document.createElement('h3');name.textContent=group.name;row.append(name);host.querySelector('.gallery-rows').append(row);
  const bounds=new T.Box3();for(const model of assembly.models)if(model)bounds.union(new T.Box3().setFromObject(model));
  const target=bounds.getCenter(new T.Vector3()),camera=new T.PerspectiveCamera(36,1,.1,12000),entry={id:group.id,camera,bounds,target,cells:[],angle:i*.41,phase:i*.41};rows.push(entry);
  for(let variant=0;variant<3;variant++){
   const cell=document.createElement('div');cell.className='gallery-cell';cell.setAttribute('aria-label',group.name+' — '+['Basic','Light','High'][variant]);row.append(cell);
   cell.addEventListener('pointerenter',()=>{if(hoverCapable.matches)setHovered(cell);});
   cell.addEventListener('pointerleave',()=>{if(hoveredCell===cell)setHovered(null);});
   const scene=new T.Scene();scene.background=new T.Color(0xe8eee1);scene.add(new T.HemisphereLight(0xffffff,0x596b50,2));const sun=new T.DirectionalLight(0xfff5de,3);sun.position.set(-120,210,110);scene.add(sun);
   const floor=new T.Mesh(new T.PlaneGeometry(4000,4000),new T.MeshStandardMaterial({color:0xdce5d3,roughness:1}));floor.rotation.x=-Math.PI/2;scene.add(floor);if(assembly.models[variant])scene.add(assembly.models[variant]);else cell.textContent='Pending';
   const controls=new OrbitControls(camera,cell);controls.enableDamping=false;controls.minDistance=5;controls.maxDistance=5000;controls.target.copy(target);controls.maxPolarAngle=Math.PI*.48;
   controls.addEventListener('start',()=>setPlaying(false));controls.addEventListener('change',()=>{if(syncing)return;syncing=true;for(const c of entry.cells)c.controls.target.copy(controls.target);syncing=false;dirty=true;});entry.cells.push({cell,scene,controls,variant});
  }
 }
 function fit(row){
  const rect=row.cells[0].cell.getBoundingClientRect();if(!rect.width||!rect.height)return;
  const camera=row.camera;camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();
  const size=row.bounds.getSize(new T.Vector3());let theta=row.angle,tilt=.7,zoom=1,target=row.target.clone(),shot='Orbit';
  if(motion==='fly'){
   // A continuous 32-second drone approach, close facade rise, roof pass and reveal.
   // Close shots deliberately crop the model; only the reveal fits the full assembly.
   // Every location starts wide together; angular offsets vary the approach direction.
   // All three variants share the same camera throughout the tour.
   const keys=[[-1.15,.5,1.6,.5],[-.3,.08,.32,.32],[.65,.32,.36,.78],[2.1,1.3,.45,.84],[4.25,.5,1.35,.45],[Math.PI*2-1.15,.5,1.6,.5]];
   const phase=((elapsed/32)%1)*5,index=Math.floor(phase),u=phase-index,t=u*u*(3-2*u),a=keys[index],b=keys[index+1],mix=k=>a[k]+(b[k]-a[k])*t;
   theta=mix(0)+row.phase;tilt=mix(1);zoom=mix(2);target.y=row.bounds.min.y+size.y*mix(3);shot=['Approach','Facade rise','Rooftop pass','Wide reveal','Return'][index];
  }
  const direction=new T.Vector3(Math.sin(theta),tilt,Math.cos(theta)).normalize(),right=new T.Vector3().crossVectors(new T.Vector3(0,1,0),direction).normalize(),up=new T.Vector3().crossVectors(direction,right),tanV=Math.tan(Math.PI/10),tanH=tanV*camera.aspect;let distance=10;
  for(const x of [row.bounds.min.x,row.bounds.max.x])for(const y of [row.bounds.min.y,row.bounds.max.y])for(const z of [row.bounds.min.z,row.bounds.max.z]){const p=new T.Vector3(x,y,z).sub(target),depth=p.dot(direction);distance=Math.max(distance,depth+Math.abs(p.dot(right))*1.15/tanH,depth+Math.abs(p.dot(up))*1.15/tanV);}
  if(motion==='fly'){const span=Math.max(size.x,size.z,size.y*.65,15),blend=T.MathUtils.smoothstep(zoom,.6,1.35);distance=T.MathUtils.lerp(span*zoom,distance*zoom,blend);}else distance*=zoom;
  // Keep the camera outside the actual assembly bounds even on close passes.
  const clearance=Math.max(4,Math.min(size.x,size.z)*.08),safe=row.bounds.clone().expandByScalar(clearance);let position=target.clone().addScaledVector(direction,distance);
  if(safe.containsPoint(position)){
   let exit=Infinity;for(const axis of ['x','y','z'])if(Math.abs(direction[axis])>1e-6){const edge=direction[axis]>0?safe.max[axis]:safe.min[axis];exit=Math.min(exit,(edge-target[axis])/direction[axis]);}
   distance=Math.max(distance,exit+.1);position=target.clone().addScaledVector(direction,distance);
  }
  row.shot=shot;
  syncing=true;camera.position.copy(position);for(const c of row.cells)c.controls.target.copy(target);row.cells[0].controls.update();syncing=false;
 }
 function resize(){if(!active)return;renderer.setSize(innerWidth,innerHeight);for(const row of rows)fit(row);dirty=true;}
 function render(){
  renderer.setScissorTest(false);renderer.setClearColor(0,0);renderer.clear();renderer.setScissorTest(true);let drawn=0;
  const cells=rows.flatMap(row=>row.cells.map(c=>({...c,camera:row.camera})));
  // Draw the enlarged cell last so neighbouring viewports cannot paint over it.
  cells.sort((a,b)=>Number(a.cell===hoveredCell)-Number(b.cell===hoveredCell));
  for(const {cell,scene,camera}of cells){const r=cell.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||r.right<=0||r.left>=innerWidth)continue;const left=Math.max(0,r.left),bottom=Math.min(innerHeight,r.bottom),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top);renderer.setViewport(r.left,innerHeight-r.bottom,r.width,r.height);renderer.setScissor(left,innerHeight-bottom,right-left,bottom-top);renderer.render(scene,camera);drawn++;}
  window.__gallery={active,playing,speed,motion,drawn,locations:rows.map(r=>({id:r.id,camera:r.camera.position.toArray(),target:r.cells[0].controls.target.toArray(),variants:3,shot:r.shot})),rendererCount:1};
 }
 function frame(now){if(active){if(playing&&last){const dt=Math.min((now-last)/1000,.1)*speed;elapsed+=dt;for(const row of rows){row.angle+=dt*.18;fit(row);}dirty=true;}if(dirty||now<hoverUntil){render();dirty=false;}}last=now;requestAnimationFrame(frame);}requestAnimationFrame(frame);
 play.onclick=()=>{setPlaying(!playing);dirty=true;};host.querySelector('#gallery-motion').onchange=e=>{motion=e.target.value;elapsed=0;for(const row of rows)fit(row);dirty=true;};
 host.querySelector('#gallery-speed').oninput=e=>{speed=Number(e.target.value);host.querySelector('#gallery-speed-value').textContent=speed+'×';dirty=true;};
 const sizeInput=host.querySelector('#gallery-size');
 const initialSize=innerWidth<=700?150:Math.max(90,Math.min(150,Math.floor((innerHeight-220)/7/10)*10));
 sizeInput.value=initialSize;host.style.setProperty('--gallery-cell-height',initialSize+'px');host.querySelector('#gallery-size-value').textContent=initialSize+' px';
 sizeInput.oninput=()=>{host.style.setProperty('--gallery-cell-height',sizeInput.value+'px');host.querySelector('#gallery-size-value').textContent=sizeInput.value+' px';resize();};
 window.__galleryFlightTest=time=>{elapsed=time;for(const row of rows)fit(row);dirty=true;return rows.map(r=>({id:r.id,camera:r.camera.position.toArray(),target:r.cells[0].controls.target.toArray(),shot:r.shot,inside:r.bounds.containsPoint(r.camera.position)}));};
 const observer=new ResizeObserver(()=>{if(active)resize();});observer.observe(host);window.addEventListener('resize',resize);window.addEventListener('scroll',()=>{dirty=true;},{passive:true});
 return {setActive(value){
  active=value;host.hidden=!value;document.body.classList.toggle('gallery-active',value);
  if(value){document.body.append(renderer.domElement);renderer.domElement.hidden=false;resize();}
  else{setHovered(null);setPlaying(false);renderer.setScissorTest(false);renderer.setClearColor(0,0);renderer.clear();renderer.domElement.hidden=true;renderer.domElement.remove();}
  if(window.__gallery){window.__gallery.active=value;window.__gallery.playing=playing;window.__gallery.drawn=value?window.__gallery.drawn:0;}dirty=true;
 },render(){dirty=true;},get active(){return active;}};
}
