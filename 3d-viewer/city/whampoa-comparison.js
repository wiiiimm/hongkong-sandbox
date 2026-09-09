import {createComparisonGallery} from './comparison-gallery.js';
import * as T from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';
import {GLTFLoader} from '../vendor/GLTFLoader.js';
const base='city/data/whampoa-light-trial/',manifest=await fetch(base+'manifest.json').then(r=>r.json()),data=await fetch(base+'basic.json').then(r=>r.json()),loader=new GLTFLoader(),views=[],nf=n=>n.toLocaleString('en-HK'),kb=n=>(n/1024).toFixed(1)+' KiB';let syncing=false,selected='ship',overview=false,spinning=false,lastFrame=0,flying=false,flightTime=0,tourStops=[];
const neutral=new T.MeshStandardMaterial({color:0xc3c9b7,roughness:.85,metalness:0,flatShading:true,side:T.DoubleSide});
const facade=neutral.clone();facade.onBeforeCompile=s=>{s.vertexShader='varying vec3 trialPos;varying vec3 trialNormal;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntrialPos=position;trialNormal=normal;');s.fragmentShader='varying vec3 trialPos;varying vec3 trialNormal;\n'+s.fragmentShader;s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
if(abs(trialNormal.y)<0.5){float u=abs(trialNormal.x)>abs(trialNormal.z)?trialPos.z:trialPos.x;vec2 cell=fract(vec2(u/2.7,trialPos.y/3.05));float windowMask=step(.16,cell.x)*step(cell.x,.75)*step(.24,cell.y)*step(cell.y,.79);float band=step(.93,cell.y);diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.23,.34,.33),windowMask*.85);diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.84,.83,.75),band*.65);}`);};facade.customProgramCacheKey=()=> 'trial-facade-v1';
for(const id of ['basic','light','high']){const host=document.getElementById(id),scene=new T.Scene();scene.background=new T.Color(0xe8eee1);const camera=new T.PerspectiveCamera(36,1,.1,4000),renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.shadowMap.enabled=true;host.append(renderer.domElement);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=20;controls.maxDistance=5000;controls.maxPolarAngle=Math.PI*.48;scene.add(new T.HemisphereLight(0xffffff,0x596b50,2));const sun=new T.DirectionalLight(0xfff5de,3);sun.position.set(-120,210,110);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-300,right:300,top:300,bottom:-300,near:1,far:700});sun.shadow.bias=-.001;scene.add(sun);const ground=new T.Mesh(new T.PlaneGeometry(5000,5000),new T.MeshStandardMaterial({color:0xdce5d3,roughness:1}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);const v={id,host,scene,camera,renderer,controls,ground,model:null};views.push(v);controls.addEventListener('change',()=>{if(syncing)return;syncing=true;for(const w of views)if(w!==v){w.camera.position.copy(camera.position);w.controls.target.copy(controls.target);w.controls.update();}syncing=false;render();});new ResizeObserver(()=>{const r=host.getBoundingClientRect();if(!r.width||!r.height)return;renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();if(views[0]?.bounds)reset();else render();}).observe(host);}
function render(){if(window.__trial){window.__trial.camera=views[0]?.camera.position.toArray();window.__trial.cameras=views.map(v=>v.camera.position.toArray());window.__trial.flying=flying;window.__trial.flightTime=flightTime;}for(const v of views){v.renderer.render(v.scene,v.camera);for(const label of v.labels||[]){const point=label.point.clone().project(v.camera);label.element.style.left=((point.x+1)*50)+'%';label.element.style.top=((1-point.y)*50)+'%';label.element.hidden=point.z>1||point.z< -1;}}}
function basicModel(rows,light=false){const group=new T.Group();for(const b of rows){const shape=new T.Shape(b.rings[0].map(([x,z])=>new T.Vector2(x,-z)));for(const ring of b.rings.slice(1))shape.holes.push(new T.Path(ring.map(([x,z])=>new T.Vector2(x,-z))));const g=new T.ExtrudeGeometry(shape,{depth:b.height,bevelEnabled:false,steps:1,curveSegments:1});g.rotateX(-Math.PI/2);g.translate(0,b.base,0);const mesh=new T.Mesh(g,light?facade:neutral);mesh.castShadow=mesh.receiveShadow=true;mesh.userData.uid=b.uid;group.add(mesh);}return group;}
async function nativeModel(models,prefix,translation){const group=new T.Group();for(const m of models){const response=await fetch(prefix+m.asset);if(!response.ok)throw Error('Model unavailable: '+m.uid);const raw=await response.arrayBuffer(),buffer=await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();const gltf=await loader.parseAsync(buffer,'');gltf.scene.position.add(new T.Vector3(...translation));gltf.scene.traverse(o=>{if(o.isMesh){o.material=neutral;o.castShadow=o.receiveShadow=true;o.userData.uid=m.uid;o.userData.nativeGeometry=true;}});group.add(gltf.scene);}group.userData.cachedNative=true;return group;}
function count(group){let n=0;group?.traverse(o=>{if(o.isMesh)n+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});return n;}
const referenceModels={};for(const [id,r]of Object.entries(manifest.references))referenceModels[id]={light:r.light?await nativeModel(r.light,base,r.rootTranslation):null,high:await nativeModel(r.high,r.prefix,r.rootTranslation)};
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
 if(overview&&flightTime>0){flyFrame();return;}
 applyPose(fittedPose(views[0].bounds,orbitDirection instanceof T.Vector3?orbitDirection:new T.Vector3(.15,1,1.7)));
}
function setFly(value){
 flying=value;lastFrame=0;
 const button=document.getElementById('flythrough');button.setAttribute('aria-pressed',String(value));button.textContent=value?'Pause fly-through':flightTime?'Resume fly-through':'Start fly-through';
 if(window.__trial)window.__trial.flying=value;
}
function flyFrame(){
 if(!tourStops.length)return;
 const step=12,index=Math.floor(flightTime/step)%tourStops.length,phase=flightTime%step,stop=tourStops[index];
 const direction=t=>new T.Vector3(Math.sin(t),.65,Math.cos(t));
 let pose;
 if(phase<8)pose=fittedPose(stop.bounds,direction(-.8+phase/8*1.6));
 else {const next=tourStops[(index+1)%tourStops.length],a=fittedPose(stop.bounds,direction(.8)),b=fittedPose(next.bounds,direction(-.8)),t=(phase-8)/4,u=t*t*(3-2*t);pose={position:a.position.lerp(b.position,u),target:a.target.lerp(b.target,u)};pose.position.y+=Math.sin(Math.PI*t)*Math.max(stop.bounds.getSize(new T.Vector3()).y,next.bounds.getSize(new T.Vector3()).y,80)*.7;}
 const status=document.getElementById('flight-status'),text=(phase<8?'Exploring ': 'Flying from ')+stop.name;if(status.textContent!==text)status.textContent=text;
 applyPose(pose);
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
 const entries=(overview?manifest.groups:manifest.groups.filter(g=>g.id===id)).map(assembly);
 const columns=overview?entries.length:1,rows=Math.ceil(entries.length/columns),cellX=Math.max(...entries.map(e=>e.size.x))+90,cellZ=Math.max(...entries.map(e=>e.size.z))+100;
 for(const v of views){if(v.model){v.scene.remove(v.model);v.model.traverse(o=>{if(o.isMesh&&!o.userData.nativeGeometry)o.geometry.dispose();});}for(const l of v.labels||[])l.element.remove();v.labels=[];v.host.querySelector('.placeholder')?.remove();v.model=new T.Group();v.scene.add(v.model);}
 tourStops=[];entries.forEach((entry,index)=>{const stopBounds=new T.Box3();const x=overview?((index%columns)-(columns-1)/2)*cellX:0,z=overview?(Math.floor(index/columns)-(rows-1)/2)*cellZ:0;entry.models.forEach((model,i)=>{const v=views[i];if(model){model.position.add(new T.Vector3(x,0,z));v.model.add(model);stopBounds.union(new T.Box3().setFromObject(model));}if(overview){const element=document.createElement('span');element.className='model-label';element.textContent=String(index+1)+(model?'':' · pending');element.title=entry.group.name;v.host.append(element);v.labels.push({element,point:new T.Vector3(x,entry.size.y+12,z)});}else if(!model){const el=document.createElement('div');el.className='placeholder';el.textContent='High-detail pass pending';v.host.append(el);}});tourStops.push({name:entry.group.name,bounds:stopBounds});});
 const bounds=new T.Box3();for(const v of views)bounds.union(new T.Box3().setFromObject(v.model));for(const v of views)v.bounds=bounds;
 const sourceForms=entries.reduce((n,e)=>n+e.rows.length,0),references=entries.map(e=>manifest.references[e.group.id]).filter(Boolean),highForms=references.reduce((n,r)=>n+r.high.length,0),bytes=key=>references.reduce((n,r)=>n+(r[key]||[]).reduce((t,m)=>t+m.bytes,0),0),counts=views.map(v=>count(v.model));
 document.getElementById('basic-stats').textContent=`${nf(sourceForms)} source forms · ${nf(counts[0])} triangles`;
 const reducedGroups=entries.filter(e=>referenceModels[e.group.id]?.light).length;
 const lightPayload=reducedGroups===0?'existing footprint geometry · shared façade shader':`${kb(bytes('light'))} compressed mesh${reducedGroups<entries.length?' + procedural façades':''}`;
 document.getElementById('light-stats').textContent=`${nf(counts[1])} triangles · ${lightPayload}`;
 document.getElementById('high-stats').textContent=highForms?`${nf(highForms)} source forms · ${nf(counts[2])} triangles · ${kb(bytes('high'))} compressed`:'High-detail pass pending';
 document.getElementById('light-description').textContent='Reduced native meshes or shared procedural façades';document.getElementById('high-description').textContent='Existing government geometry where available';
 document.getElementById('summary').textContent=overview?`${entries.length} locations · three levels of detail · one shared scale`:`${entries[0].group.name} · three levels of detail`;
 document.getElementById('qualification').textContent='Identical scale and camera across all three views. Light variants are comparison studies. Site 12 high detail includes the shared podium, absent from its original nine-tower basic/light trial.'+(overview?' Models are arranged in a study grid, not their geographical positions.':'');
 document.getElementById('location-legend')?.remove();if(overview){const legend=document.createElement('ol');legend.id='location-legend';legend.setAttribute('aria-label','Overview location key');for(const entry of entries){const li=document.createElement('li');li.textContent=entry.group.name;legend.append(li);}document.getElementById('views').after(legend);}document.getElementById('location').disabled=overview;document.getElementById('overview').setAttribute('aria-pressed',String(overview));document.getElementById('overview').textContent=overview?'Show one location':'Show all locations';document.body.classList.toggle('overview',overview);
 window.__trial={ready:true,id,overview,spinning,counts,uids:entries.flatMap(e=>e.group.uids),highUids:references.flatMap(r=>r.high.map(m=>m.uid)),highPending:!highForms,locations:entries.map(e=>e.group.id)};reset();
}
const select=document.getElementById('location');for(const group of manifest.groups){const option=document.createElement('option');option.value=group.id;option.textContent=group.name;select.append(option);}
select.addEventListener('change',e=>{setFly(false);flightTime=0;show(e.target.value);});document.getElementById('overview').onclick=()=>{setFly(false);flightTime=0;overview=!overview;show(selected);};
function setSpin(value){spinning=value;window.__trial.spinning=value;const button=document.getElementById('spin');button.setAttribute('aria-pressed',String(value));button.textContent=value?'Pause spin':'Start spin';lastFrame=0;}
document.getElementById('spin').onclick=()=>{flightTime=0;setFly(false);document.getElementById('flight-status').textContent='';setSpin(!spinning);};
document.getElementById('flythrough').onclick=()=>{if(flying){setFly(false);return;}setSpin(false);if(!overview){overview=true;show(selected);}setFly(true);flyFrame();};
for(const v of views)v.controls.addEventListener('start',()=>{setSpin(false);setFly(false);});
function animate(now){if(gallery?.active){lastFrame=now;requestAnimationFrame(animate);return;}if(flying&&lastFrame){flightTime+=Math.min((now-lastFrame)/1000,.1);flyFrame();}else if(spinning&&lastFrame){const dt=Math.min((now-lastFrame)/1000,.1),v=views[0],offset=v.camera.position.clone().sub(v.controls.target);offset.applyAxisAngle(new T.Vector3(0,1,0),dt*.12);if(overview)reset(offset.normalize());else{v.camera.position.copy(v.controls.target).add(offset);v.controls.update();}}lastFrame=now;requestAnimationFrame(animate);}requestAnimationFrame(animate);
document.getElementById('presentation').onclick=e=>{const on=document.body.classList.toggle('presentation');e.target.setAttribute('aria-pressed',String(on));e.target.textContent=on?'Exit video view':'Video view';reset();};
window.__trialOrbitTest=angle=>{const offset=views[0].camera.position.clone().sub(views[0].controls.target).normalize().applyAxisAngle(new T.Vector3(0,1,0),angle);reset(offset);return views.map(v=>{const result=[];for(const x of [v.bounds.min.x,v.bounds.max.x])for(const y of [v.bounds.min.y,v.bounds.max.y])for(const z of [v.bounds.min.z,v.bounds.max.z])result.push(new T.Vector3(x,y,z).project(v.camera).toArray());return result;});};document.getElementById('reset').onclick=()=>{flightTime=0;setFly(false);setSpin(false);document.getElementById('flight-status').textContent='';reset();};
window.__trialFlightTest=time=>{flightTime=time;flyFrame();return {cameras:views.map(v=>v.camera.position.toArray()),targets:views.map(v=>v.controls.target.toArray()),status:document.getElementById('flight-status').textContent};};document.getElementById('wire').onchange=e=>{neutral.wireframe=facade.wireframe=e.target.checked;render();gallery?.render();};show(new URLSearchParams(location.search).get('site')||manifest.groups[0].id);select.value=selected;

let gallery=null;
document.getElementById('gallery-toggle').onclick=()=>{setFly(false);setSpin(false);if(!gallery)gallery=createComparisonGallery(manifest.groups,assembly);gallery.setActive(!gallery.active);const button=document.getElementById('gallery-toggle');button.textContent=gallery.active?'Return to tour':'Gallery view';button.setAttribute('aria-pressed',String(gallery.active));};
