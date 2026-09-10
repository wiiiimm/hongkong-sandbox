import {createComparisonGallery} from './comparison-gallery.js?v=20260910-startup1';
import * as T from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';
import {GLTFLoader} from '../vendor/GLTFLoader.js';
async function readJSON(url){const response=await fetch(url,{cache:'no-cache'});if(!response.ok)throw new Error(`${url}: HTTP ${response.status}`);return response.json();}
const base='city/data/whampoa-light-trial/',manifest=await readJSON(base+'manifest.json'),data=await readJSON(base+'basic.json'),loader=new GLTFLoader(),views=[],nf=n=>n.toLocaleString('en-HK'),kb=n=>(n/1024).toFixed(1)+' KiB';let gallery=null,syncing=false,selected='ship',spinning=false,lastFrame=0;
const loadErrors=[];
const neutral=new T.MeshStandardMaterial({color:0xc3c9b7,roughness:.85,metalness:0,flatShading:true,side:T.DoubleSide});
const facade=neutral.clone();facade.onBeforeCompile=s=>{s.vertexShader='varying vec3 trialPos;varying vec3 trialNormal;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntrialPos=position;trialNormal=normal;');s.fragmentShader='varying vec3 trialPos;varying vec3 trialNormal;\n'+s.fragmentShader;s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
if(abs(trialNormal.y)<0.5){float u=abs(trialNormal.x)>abs(trialNormal.z)?trialPos.z:trialPos.x;vec2 cell=fract(vec2(u/2.7,trialPos.y/3.05));float windowMask=step(.16,cell.x)*step(cell.x,.75)*step(.24,cell.y)*step(cell.y,.79);float band=step(.93,cell.y);diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.23,.34,.33),windowMask*.85);diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.84,.83,.75),band*.65);}`);};facade.customProgramCacheKey=()=> 'trial-facade-v1';
for(const id of ['basic','light','high']){const host=document.getElementById(id),scene=new T.Scene();scene.background=new T.Color(0xe8eee1);const camera=new T.PerspectiveCamera(36,1,.1,4000),renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.shadowMap.enabled=true;host.append(renderer.domElement);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=20;controls.maxDistance=5000;controls.maxPolarAngle=Math.PI*.48;scene.add(new T.HemisphereLight(0xffffff,0x596b50,2));const sun=new T.DirectionalLight(0xfff5de,3);sun.position.set(-120,210,110);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-300,right:300,top:300,bottom:-300,near:1,far:700});sun.shadow.bias=-.001;scene.add(sun);const ground=new T.Mesh(new T.PlaneGeometry(5000,5000),new T.MeshStandardMaterial({color:0xdce5d3,roughness:1}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);const v={id,host,scene,camera,renderer,controls,ground,model:null};views.push(v);controls.addEventListener('change',()=>{if(syncing)return;syncing=true;for(const w of views)if(w!==v){w.camera.position.copy(camera.position);w.controls.target.copy(controls.target);w.controls.update();}syncing=false;render();});new ResizeObserver(()=>{const r=host.getBoundingClientRect();if(!r.width||!r.height)return;renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();if(views[0]?.bounds)reset();else render();}).observe(host);}
function render(){if(window.__trial){window.__trial.camera=views[0]?.camera.position.toArray();window.__trial.cameras=views.map(v=>v.camera.position.toArray());}for(const v of views){v.renderer.render(v.scene,v.camera);for(const label of v.labels||[]){const point=label.point.clone().project(v.camera);label.element.style.left=((point.x+1)*50)+'%';label.element.style.top=((1-point.y)*50)+'%';label.element.hidden=point.z>1||point.z< -1;}}}
function basicModel(rows,light=false){const group=new T.Group();for(const b of rows){const shape=new T.Shape(b.rings[0].map(([x,z])=>new T.Vector2(x,-z)));for(const ring of b.rings.slice(1))shape.holes.push(new T.Path(ring.map(([x,z])=>new T.Vector2(x,-z))));const g=new T.ExtrudeGeometry(shape,{depth:b.height,bevelEnabled:false,steps:1,curveSegments:1});g.rotateX(-Math.PI/2);g.translate(0,b.base,0);const mesh=new T.Mesh(g,light?facade:neutral);mesh.castShadow=mesh.receiveShadow=true;mesh.userData.uid=b.uid;group.add(mesh);}return group;}
async function nativeModel(models,prefix,translation){const group=new T.Group();for(const m of models){const response=await fetch(prefix+m.asset);if(!response.ok)throw Error('Model unavailable: '+m.uid+' (HTTP '+response.status+')');const raw=await response.arrayBuffer(),buffer=await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();const gltf=await loader.parseAsync(buffer,'');gltf.scene.position.add(new T.Vector3(...translation));gltf.scene.traverse(o=>{if(o.isMesh){o.material=neutral;o.castShadow=o.receiveShadow=true;o.userData.uid=m.uid;o.userData.nativeGeometry=true;}});group.add(gltf.scene);}group.userData.cachedNative=true;return group;}
function count(group){let n=0;group?.traverse(o=>{if(o.isMesh)n+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});return n;}
const referenceModels={};
for(const [id,r]of Object.entries(manifest.references)){
 referenceModels[id]={light:null,high:null};
 for(const kind of ['light','high']){
  if(!r[kind])continue;
  window.comparisonLoadStatus?.(`Loading ${manifest.groups.find(g=>g.id===id)?.name||id} · ${kind}…`);
  try{referenceModels[id][kind]=await nativeModel(r[kind],kind==='light'?base:r.prefix,r.rootTranslation);}
  catch(error){loadErrors.push({id,kind,message:error.message});console.warn('Comparison model load failed:',id,kind,error);}
 }
}
if(loadErrors.length)window.comparisonLoadStatus?.(`${loadErrors.length} model variant(s) could not load. Available models remain visible. ${loadErrors.map(e=>`${e.id} ${e.kind}: ${e.message}`).join('; ')}`,true);
function fittedPose(bounds,direction){
 const target=bounds.getCenter(new T.Vector3());direction=direction.clone().normalize();
 const right=new T.Vector3().crossVectors(new T.Vector3(0,1,0),direction).normalize(),up=new T.Vector3().crossVectors(direction,right),tanV=Math.tan(T.MathUtils.degToRad(18)),tanH=tanV*Math.min(...views.map(v=>v.camera.aspect));
 let distance=20;
 for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){const p=new T.Vector3(x,y,z).sub(target),depth=p.dot(direction);distance=Math.max(distance,depth+Math.abs(p.dot(right))*1.18/tanH,depth+Math.abs(p.dot(up))*1.18/tanV);}
 return {target,position:target.clone().addScaledVector(direction,distance)};
}
function applyPose(pose){
 syncing=true;for(const v of views){v.controls.target.copy(pose.target);v.camera.far=12000;v.camera.updateProjectionMatrix();v.controls.maxDistance=10000;v.camera.position.copy(pose.position);v.controls.update();}syncing=false;render();
}
function reset(orbitDirection=null){
 applyPose(fittedPose(views[0].bounds,orbitDirection instanceof T.Vector3?orbitDirection:new T.Vector3(.15,1,1.7)));
}
function assembly(group){
 const rows=data.buildings.filter(b=>group.uids.includes(b.uid)),native=referenceModels[group.id];
 const models=[basicModel(rows),native?.light?.clone(true)||basicModel(rows,true),native?.high?.clone(true)||null];
 const bounds=new T.Box3();for(const model of models)if(model)bounds.union(new T.Box3().setFromObject(model));
 const centre=bounds.getCenter(new T.Vector3());centre.y=bounds.min.y;
 for(const model of models)if(model)model.position.sub(centre);
 return {group,rows,models,size:bounds.getSize(new T.Vector3())};
}
function show(id){
 if(!manifest.groups.some(g=>g.id===id))id=manifest.groups[0].id;selected=id;
 const entries=manifest.groups.filter(g=>g.id===id).map(assembly);
 for(const v of views){if(v.model){v.scene.remove(v.model);v.model.traverse(o=>{if(o.isMesh&&!o.userData.nativeGeometry)o.geometry.dispose();});}for(const l of v.labels||[])l.element.remove();v.labels=[];v.host.querySelector('.placeholder')?.remove();v.model=new T.Group();v.scene.add(v.model);}
 for(const entry of entries)entry.models.forEach((model,i)=>{const v=views[i];if(model)v.model.add(model);else{const el=document.createElement('div');el.className='placeholder';el.textContent='High-detail model unavailable';v.host.append(el);}});

 const bounds=new T.Box3();for(const v of views)bounds.union(new T.Box3().setFromObject(v.model));for(const v of views)v.bounds=bounds;
 const sourceForms=entries.reduce((n,e)=>n+e.rows.length,0),references=entries.filter(e=>referenceModels[e.group.id]?.high).map(e=>manifest.references[e.group.id]).filter(Boolean),highForms=references.reduce((n,r)=>n+r.high.length,0),bytes=key=>entries.filter(e=>referenceModels[e.group.id]?.[key]).reduce((n,e)=>n+(manifest.references[e.group.id][key]||[]).reduce((t,m)=>t+m.bytes,0),0),counts=views.map(v=>count(v.model));
 document.getElementById('basic-stats').textContent=`${nf(sourceForms)} source forms · ${nf(counts[0])} triangles`;
 const reducedGroups=entries.filter(e=>referenceModels[e.group.id]?.light).length;
 const lightPayload=reducedGroups===0?'existing footprint geometry · shared façade shader':`${kb(bytes('light'))} compressed mesh${reducedGroups<entries.length?' + procedural façades':''}`;
 document.getElementById('light-stats').textContent=`${nf(counts[1])} triangles · ${lightPayload}`;
 document.getElementById('high-stats').textContent=highForms?`${nf(highForms)} source forms · ${nf(counts[2])} triangles · ${kb(bytes('high'))} compressed`:'High-detail model unavailable';
 document.getElementById('light-description').textContent='Reduced native meshes or shared procedural façades';document.getElementById('high-description').textContent='Existing government geometry where available';
 document.getElementById('summary').textContent=`${entries[0].group.name} · three levels of detail`;
 document.getElementById('qualification').textContent='Identical scale and camera across all three views. Light variants are comparison studies. Site 12 high detail includes the shared podium, absent from its original nine-tower basic/light trial.';

 window.__trial={ready:true,id,spinning,loadErrors,counts,uids:entries.flatMap(e=>e.group.uids),highUids:references.flatMap(r=>r.high.map(m=>m.uid)),highPending:!highForms,locations:entries.map(e=>e.group.id)};reset();
}
const select=document.getElementById('location');for(const group of manifest.groups){const option=document.createElement('option');option.value=group.id;option.textContent=group.name;select.append(option);}
select.addEventListener('change',e=>show(e.target.value));
function setSpin(value){spinning=value;window.__trial.spinning=value;const button=document.getElementById('spin');button.setAttribute('aria-pressed',String(value));button.textContent=value?'Pause spin':'Start spin';lastFrame=0;}
document.getElementById('spin').onclick=()=>setSpin(!spinning);
for(const v of views)v.controls.addEventListener('start',()=>setSpin(false));
function animate(now){if(gallery?.active){lastFrame=now;requestAnimationFrame(animate);return;}if(spinning&&lastFrame){const dt=Math.min((now-lastFrame)/1000,.1),v=views[0],offset=v.camera.position.clone().sub(v.controls.target);offset.applyAxisAngle(new T.Vector3(0,1,0),dt*.12);v.camera.position.copy(v.controls.target).add(offset);v.controls.update();}lastFrame=now;requestAnimationFrame(animate);}requestAnimationFrame(animate);
document.getElementById('presentation').onclick=e=>{const on=document.body.classList.toggle('presentation');e.target.setAttribute('aria-pressed',String(on));e.target.textContent=on?'Exit video view':'Video view';reset();};
document.getElementById('reset').onclick=()=>{setSpin(false);reset();};
document.getElementById('wire').onchange=e=>{neutral.wireframe=facade.wireframe=e.target.checked;render();gallery?.render();};show(new URLSearchParams(location.search).get('site')||manifest.groups[0].id);select.value=selected;

document.getElementById('gallery-toggle').onclick=()=>{setSpin(false);if(!gallery)gallery=createComparisonGallery(manifest.groups,assembly);gallery.setActive(!gallery.active);const button=document.getElementById('gallery-toggle');button.textContent=gallery.active?'Single location':'Gallery view';button.setAttribute('aria-pressed',String(gallery.active));};
