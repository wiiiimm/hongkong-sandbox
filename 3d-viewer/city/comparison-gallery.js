import * as T from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';

// One renderer draws visible DOM cells with scissors; no per-cell WebGL contexts.
export function createComparisonGallery(groups, assemble) {
 const host=document.createElement('section');host.id='comparison-gallery';host.hidden=true;
 host.innerHTML=`<div class="gallery-toolbar"><button id="gallery-play" aria-pressed="false">Play all</button><label>Motion <select id="gallery-motion"><option value="orbit">Orbit</option><option value="fly">Fly around</option></select></label><label>Speed <input id="gallery-speed" type="range" min="0.25" max="3" step="0.25" value="1"><output id="gallery-speed-value">1×</output></label><button id="gallery-density" aria-pressed="false">Roomy rows</button><span>Each location is framed separately; its three versions stay in sync.</span></div><div class="gallery-head"><span>Location</span><span>Basic</span><span>Light</span><span>High</span></div><div class="gallery-rows"></div>`;
 document.getElementById('views').after(host);
 const renderer=new T.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.domElement.className='gallery-canvas';renderer.domElement.hidden=true;document.body.append(renderer.domElement);
 const rows=[];let active=false,playing=false,speed=1,motion='orbit',last=0,dirty=true,elapsed=0,syncing=false;
 const play=host.querySelector('#gallery-play');
 function setPlaying(value){playing=value;last=0;play.textContent=value?'Pause all':'Play all';play.setAttribute('aria-pressed',String(value));}
 for(const [i,group]of groups.entries()){
  const assembly=assemble(group),row=document.createElement('article');row.className='gallery-row';const name=document.createElement('h3');name.textContent=group.name;row.append(name);host.querySelector('.gallery-rows').append(row);
  const bounds=new T.Box3();for(const model of assembly.models)if(model)bounds.union(new T.Box3().setFromObject(model));
  const target=bounds.getCenter(new T.Vector3()),camera=new T.PerspectiveCamera(36,1,.1,12000),entry={id:group.id,camera,bounds,target,cells:[],angle:i*.41,phase:i*.41};rows.push(entry);
  for(let variant=0;variant<3;variant++){
   const cell=document.createElement('div');cell.className='gallery-cell';cell.setAttribute('aria-label',group.name+' — '+['Basic','Light','High'][variant]);row.append(cell);
   const scene=new T.Scene();scene.background=new T.Color(0xe8eee1);scene.add(new T.HemisphereLight(0xffffff,0x596b50,2));const sun=new T.DirectionalLight(0xfff5de,3);sun.position.set(-120,210,110);scene.add(sun);
   const floor=new T.Mesh(new T.PlaneGeometry(4000,4000),new T.MeshStandardMaterial({color:0xdce5d3,roughness:1}));floor.rotation.x=-Math.PI/2;scene.add(floor);if(assembly.models[variant])scene.add(assembly.models[variant]);else cell.textContent='Pending';
   const controls=new OrbitControls(camera,cell);controls.enableDamping=false;controls.minDistance=5;controls.maxDistance=5000;controls.target.copy(target);controls.maxPolarAngle=Math.PI*.48;
   controls.addEventListener('start',()=>setPlaying(false));controls.addEventListener('change',()=>{if(syncing)return;syncing=true;for(const c of entry.cells)c.controls.target.copy(controls.target);syncing=false;dirty=true;});entry.cells.push({cell,scene,controls,variant});
  }
 }
 function fit(row){
  const rect=row.cells[0].cell.getBoundingClientRect();if(!rect.width||!rect.height)return;
  const camera=row.camera;camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();
  const theta=row.angle,tilt=motion==='fly'?.65+.18*Math.sin(elapsed*.3+row.phase):.7,direction=new T.Vector3(Math.sin(theta),tilt,Math.cos(theta)).normalize();
  const right=new T.Vector3().crossVectors(new T.Vector3(0,1,0),direction).normalize(),up=new T.Vector3().crossVectors(direction,right),tanV=Math.tan(Math.PI/10),tanH=tanV*camera.aspect;let distance=10;
  for(const x of [row.bounds.min.x,row.bounds.max.x])for(const y of [row.bounds.min.y,row.bounds.max.y])for(const z of [row.bounds.min.z,row.bounds.max.z]){const p=new T.Vector3(x,y,z).sub(row.target),depth=p.dot(direction);distance=Math.max(distance,depth+Math.abs(p.dot(right))*1.15/tanH,depth+Math.abs(p.dot(up))*1.15/tanV);}
  if(motion==='fly')distance*=1.05+.05*Math.sin(elapsed*.2+row.phase);
  syncing=true;camera.position.copy(row.target).addScaledVector(direction,distance);for(const c of row.cells)c.controls.target.copy(row.target);row.cells[0].controls.update();syncing=false;
 }
 function resize(){renderer.setSize(innerWidth,innerHeight);if(active)for(const row of rows)fit(row);dirty=true;}
 function render(){
  renderer.setScissorTest(false);renderer.setClearColor(0,0);renderer.clear();renderer.setScissorTest(true);let drawn=0;
  for(const row of rows)for(const {cell,scene}of row.cells){const r=cell.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||r.right<=0||r.left>=innerWidth)continue;const left=Math.max(0,r.left),bottom=Math.min(innerHeight,r.bottom),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top);renderer.setViewport(r.left,innerHeight-r.bottom,r.width,r.height);renderer.setScissor(left,innerHeight-bottom,right-left,bottom-top);renderer.render(scene,row.camera);drawn++;}
  window.__gallery={active,playing,speed,motion,drawn,locations:rows.map(r=>({id:r.id,camera:r.camera.position.toArray(),target:r.cells[0].controls.target.toArray(),variants:3})),rendererCount:1};
 }
 function frame(now){if(active){if(playing&&last){const dt=Math.min((now-last)/1000,.1)*speed;elapsed+=dt;for(const row of rows){row.angle+=dt*.18;fit(row);}dirty=true;}if(dirty){render();dirty=false;}}last=now;requestAnimationFrame(frame);}requestAnimationFrame(frame);
 play.onclick=()=>{setPlaying(!playing);dirty=true;};host.querySelector('#gallery-motion').onchange=e=>{motion=e.target.value;for(const row of rows)fit(row);dirty=true;};
 host.querySelector('#gallery-speed').oninput=e=>{speed=Number(e.target.value);host.querySelector('#gallery-speed-value').textContent=speed+'×';dirty=true;};
 host.querySelector('#gallery-density').onclick=e=>{const roomy=host.classList.toggle('roomy');e.target.textContent=roomy?'Fit all rows':'Roomy rows';e.target.setAttribute('aria-pressed',String(roomy));requestAnimationFrame(resize);};
 const observer=new ResizeObserver(()=>{if(active)resize();});observer.observe(host);window.addEventListener('resize',resize);window.addEventListener('scroll',()=>{dirty=true;},{passive:true});
 return {setActive(value){active=value;if(window.__gallery){window.__gallery.active=value;window.__gallery.playing=false;}host.hidden=!value;renderer.domElement.hidden=!value;document.body.classList.toggle('gallery-active',value);if(!value)setPlaying(false);else resize();dirty=true;},render(){dirty=true;},get active(){return active;}};
}
