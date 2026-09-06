import * as THREE from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';
import {makeTerrainSampler,BuildingIndex,smoothStep} from './geo.js';
import {makeTerrain,makeWater,makeBuildings,makeRoads,makeNature,makeFerries,extrudeBuilding} from './world.js';
import {Navigation} from './navigation.js';
const $=id=>document.getElementById(id),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const PLACES={
 central:{title:'Central',zh:'中環',subtitle:'22.282° N · 114.160° E',description:'Where the mountains meet the metropolis.',target:[0,110,420],offset:[1900,1560,-2050],spawn:[0,575]},
 wanchai:{title:'Wan Chai',zh:'灣仔',subtitle:'22.279° N · 114.173° E',description:'A thousand stories between the streets.',target:[1390,90,680],offset:[1500,1150,-1500],spawn:[1390,920]},
 kowloon:{title:'Kowloon',zh:'九龍',subtitle:'22.295° N · 114.169° E',description:'Across the water, another world awaits.',target:[750,90,-1020],offset:[-1600,1300,2000],spawn:[998,-853]},
 lantau:{title:'Lantau Island',zh:'大嶼山',subtitle:'22.267° N · 113.942° E',description:'The quieter side. Terrain beyond the city district.',target:[-22440,300,2273],offset:[7400,5700,7200],spawn:[-22440,2273]},
};
let place='central',scene,camera,renderer,controls,nav,sampler,index,buildings,terrain,water,nature,roads,city,ferries,sun,ambient,selection,tween,frameCount=0,lastHud=0,startTime=0;
let toastTimer,worldTime=15,mapBackdrop,mapStamp,selectedIndex=-1;
const labelEntries=[],temp=new THREE.Vector3(),raycaster=new THREE.Raycaster();
function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),4400);}
function transition(position,target,duration=1.6){tween={from:camera.position.clone(),to:new THREE.Vector3(...position),targetFrom:controls.target.clone(),targetTo:new THREE.Vector3(...target),elapsed:0,duration:reduced?.001:duration};}
function goPlace(key,animate=true){
 place=key;const p=PLACES[key];if(nav.mode!=='orbit')nav.setMode('orbit',p.spawn);
 $('place-title').replaceChildren(document.createTextNode(`${p.title} `));const zh=document.createElement('span');zh.textContent=p.zh;$('place-title').append(zh);$('place-subtitle').textContent=p.subtitle;$('place-description').textContent=p.description;
 document.querySelectorAll('[data-place]').forEach(b=>{b.classList.toggle('active',b.dataset.place===key);b.setAttribute('aria-pressed',b.dataset.place===key);});
 const pos=p.target.map((x,i)=>x+p.offset[i]);
 if(animate)transition(pos,p.target);else{camera.position.set(...pos);controls.target.set(...p.target);controls.update();}
 if(key==='lantau')toast('Lantau terrain is ready to explore. Building coverage begins around Victoria Harbour.');
 $('map-location').textContent=key==='lantau'?'LANTAU ISLAND':'VICTORIA HARBOUR';$('map-scale').textContent=key==='lantau'?'10 km ━':'1 km ━';
 clearTimeout(toastTimer);if(key!=='lantau')$('toast').classList.remove('show');closeSelection();if(innerWidth<=760)$('explorer').classList.remove('open');
 history.replaceState(null,'',`${location.pathname}?district=${key}`);
}
function onMode(mode){
 tween=null;camera.fov=mode==='orbit'?44:mode==='walk'?60:52;camera.updateProjectionMatrix();document.body.classList.toggle('exploring-person',mode!=='orbit');
 document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode);});
 $('journey').hidden=mode==='orbit';$('journey-mode').textContent=mode==='walk'?'ON FOOT':'IN THE AIR';
 $('control-hint').innerHTML=mode==='orbit'?'Drag to orbit <i>·</i> Scroll to get closer <i>·</i> Click a building to discover':mode==='walk'?'WASD move <i>·</i> Drag to look <i>·</i> Shift run <i>·</i> C camera <i>·</i> Esc explore':'W / S climb & descend <i>·</i> A / D turn <i>·</i> Shift boost <i>·</i> C camera <i>·</i> Esc explore';
 $('touch-controls').hidden=mode==='orbit'||!matchMedia('(pointer: coarse)').matches;
 if(mode!=='orbit')closeSelection();
 const shadowExtent=mode==='walk'?80:mode==='fly'?900:2200;
 Object.assign(sun.shadow.camera,{left:-shadowExtent,right:shadowExtent,top:shadowExtent,bottom:-shadowExtent});sun.shadow.camera.updateProjectionMatrix();sun.shadow.normalBias=mode==='walk'?.06:1.2;
}
function setTime(value){
 worldTime=value;const night=smoothStep(17.6,20,value),gold=Math.sin(smoothStep(15,20,value)*Math.PI);
 const bg=new THREE.Color('#d9e3d5').lerp(new THREE.Color('#d6c4a2'),gold*.48).lerp(new THREE.Color('#142b35'),night);
 scene.background=bg;scene.fog.color.copy(bg);
 sun.color.set('#fff7df').lerp(new THREE.Color('#ffc080'),gold*.72);sun.intensity=3.0*(1-night)+.24;
 ambient.intensity=1.9*(1-night)+.62;ambient.color.set('#e8f0e6').lerp(new THREE.Color('#95b9d8'),night);ambient.groundColor.set('#6c806a').lerp(new THREE.Color('#20392f'),night);
 buildings.night.value=night;water.material.color.set('#71a8a0').lerp(new THREE.Color('#173e4a'),night);water.material.roughness=.38+night*.4;water.material.metalness=.25-night*.15;water.material.emissive.set('#25434c');water.material.emissiveIntensity=night*.4;
 renderer.toneMappingExposure=1.05*(1-night)+.95*night;
 document.body.classList.toggle('night',night>.5);$('time-output').textContent=`${Math.floor(value).toString().padStart(2,'0')}:${Math.round(value%1*60).toString().padStart(2,'0')}`;
}
function closeSelection(){selectedIndex=-1;$('building-card').hidden=true;if(selection){scene.remove(selection);selection.geometry.dispose();selection.material.dispose();selection=null;}}
function selectBuilding(i,focus=false){
 const b=city.buildings[i];if(!b)return;closeSelection();selectedIndex=i;
 const geo=extrudeBuilding(b);selection=new THREE.LineSegments(new THREE.EdgesGeometry(geo,25),new THREE.LineBasicMaterial({color:'#e8ae4f',transparent:true,opacity:.95,depthTest:false}));geo.dispose();selection.renderOrder=10;scene.add(selection);
 $('building-name').textContent=b.name||'A Hong Kong building';$('building-zh').textContent=b.zh||`${b.kind.replaceAll('_',' ')} · OpenStreetMap footprint`;
 $('building-height').textContent=`${b.height} m`;$('building-levels').textContent=b.levels??'—';
 $('building-source').textContent=b.heightSource==='tagged'?'Height tagged in OpenStreetMap. Simplified massing; façade details are illustrative.':b.heightSource==='levels'?'Estimated height from mapped floor count × 3.2 m. Not a surveyed measurement.':'Height is an illustrative fallback. This footprint has no mapped height or floor count.';
 $('building-osm').href=`https://www.openstreetmap.org/${b.id}`;$('building-card').hidden=false;
 if(focus){if(nav.mode!=='orbit')nav.setMode('orbit',b.centre);const radius=Math.max(100,b.height*2.1);transition([b.centre[0]+radius*.75,b.base+b.height+radius*.5,b.centre[1]-radius],[b.centre[0],b.base+b.height*.45,b.centre[1]],1.2);}
}
function makeLabels(){
 const add=(text,pos,kind='landmark')=>{const el=document.createElement('div');el.className=`map-label ${kind}`;el.textContent=text;$('labels').append(el);labelEntries.push({el,pos:new THREE.Vector3(...pos),kind});};
 for(const [text,needle] of [['IFC','Two International Finance Centre'],['Jardine House','Jardine House'],['HSBC','HSBC Main Building'],['Bank of China','Bank of China Tower'],['Central Plaza','Central Plaza'],['ICC','International Commerce Centre']]){
  const b=city.buildings.filter(b=>b.name===needle).sort((a,b)=>b.height-a.height)[0];if(b)add(text,[b.centre[0],b.base+b.height+28,b.centre[1]]);
 }
 add('Victoria Harbour · 維多利亞港',[600,4,-260],'harbour');
 for(const p of Object.values(PLACES))if(p.title!=='Lantau Island')add(p.zh,[p.target[0],110,p.target[2]+300],'district-name');
}
function updateLabels(){
 const w=innerWidth,h=innerHeight,occupied=[];
 for(const {el,pos,kind} of labelEntries){
  temp.copy(pos).project(camera);const distance=camera.position.distanceTo(pos),x=(temp.x*.5+.5)*w,y=(-temp.y*.5+.5)*h;
  const off=nav.mode!=='orbit'||distance>10000||distance<120||temp.z>1||temp.z<0||x<16||x>w-16||y<84||y>h-100||(x<330&&w>760)||(kind==='harbour'&&distance<800);
  const overlap=occupied.some(([xx,yy])=>Math.abs(xx-x)<100&&Math.abs(yy-y)<35);
  el.style.opacity=off||overlap?'0':'1';if(!off&&!overlap){el.style.left=`${x}px`;el.style.top=`${y}px`;occupied.push([x,y]);}
 }
}
function mapCoords(x,z){const b=place==='lantau'?[-36500,-13500,11000,10500]:[-3600,-2600,3600,2900];return[(x-b[0])/(b[2]-b[0])*440,(z-b[1])/(b[3]-b[1])*280];}
function drawMinimap(){
 const canvas=$('minimap'),ctx=canvas.getContext('2d');
 const stamp=place+String(worldTime>19);if(stamp!==mapStamp){
 ctx.fillStyle=worldTime>19?'#1d4645':'#9fbeb2';ctx.fillRect(0,0,440,280);
 // The miniature uses the actual terrain's zero-elevation mask, not a sketched coast.
 const data=terrain.userData.data,g=data.meta.georef;
 ctx.fillStyle=worldTime>19?'#66816c':'#dce3c9';
 const step=place==='lantau'?4:1;
 const a=mapCoords(0,0),b=mapCoords(g.aE*step,Math.abs(g.aN)*step),sx=b[0]-a[0]+.5,sy=b[1]-a[1]+.5;
 for(let r=0;r<data.h;r+=step)for(let c=0;c<data.w;c+=step){if(data.elev[r*data.w+c]<=.1)continue;const [x,y]=mapCoords(g.bE+c*g.aE-834500,816500-(g.bN+r*g.aN));if(x<-sx||y<-sy||x>440||y>280)continue;ctx.fillRect(x,y,sx,sy);}
 if(place!=='lantau'){
  ctx.strokeStyle=worldTime>19?'#8b9e82':'#b1bda3';ctx.lineWidth=.65;ctx.beginPath();
  for(const r of city.roads){if(!['primary','secondary','tertiary','trunk'].includes(r.kind))continue;r.path.forEach(([x,z],i)=>{const p=mapCoords(x,z);i?ctx.lineTo(...p):ctx.moveTo(...p);});}ctx.stroke();
  ctx.fillStyle=worldTime>19?'#b1b88d':'#829b7a';for(const b of city.buildings){if(b.height<25)continue;const [x,y]=mapCoords(...b.centre);ctx.fillRect(x,y,1.4,1.4);}
 }
 mapBackdrop=ctx.getImageData(0,0,440,280);mapStamp=stamp;
 }else ctx.putImageData(mapBackdrop,0,0);
 const p=nav.mode==='orbit'?controls.target:nav.position,[x,y]=mapCoords(p.x,p.z);ctx.save();ctx.translate(x,y);ctx.fillStyle='#385b45';ctx.strokeStyle='#f7fae8';ctx.lineWidth=2.5;
 ctx.beginPath();ctx.arc(0,0,7,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.rotate(nav.mode==='orbit'?Math.atan2(camera.position.x-p.x,-(camera.position.z-p.z)):nav.heading);ctx.beginPath();ctx.moveTo(0,-18);ctx.lineTo(-5,-9);ctx.lineTo(5,-9);ctx.closePath();ctx.fill();ctx.restore();
}
function bindUI(){
 document.querySelectorAll('[data-place]').forEach(b=>b.addEventListener('click',()=>goPlace(b.dataset.place)));
 document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>nav.setMode(b.dataset.mode,PLACES[place].spawn)));
 const layers={'buildings':buildings.group,'roads':roads,'trees':nature.group};
 for(const key of ['buildings','roads','trees','labels'])$(`layer-${key}`).addEventListener('change',e=>{if(key==='labels')$('labels').hidden=!e.target.checked;else layers[key].visible=e.target.checked;if(key==='buildings'&&!e.target.checked)closeSelection();$('layer-count').textContent=`${document.querySelectorAll('.layers input:checked').length} LAYERS`;});
 $('time').addEventListener('input',e=>setTime(Number(e.target.value)));
 $('reset-view').addEventListener('click',()=>goPlace(place));
 $('top-view').addEventListener('click',()=>{if(nav.mode!=='orbit')nav.setMode('orbit',PLACES[place].spawn);const p=controls.target;transition([p.x,p.y+(place==='lantau'?18000:3300),p.z+.1],[p.x,p.y,p.z],1.3);});
 $('north-view').addEventListener('click',()=>{if(nav.mode!=='orbit')return;const p=controls.target,d=camera.position.distanceTo(p);transition([p.x,p.y+d*.72,p.z+d*.7],[p.x,p.y,p.z]);});
 $('postcard').addEventListener('click',()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download=`hong-kong-astra-${place}-${renderer.domElement.width}x${renderer.domElement.height}.png`;a.href=renderer.domElement.toDataURL('image/png');a.click();toast(`Postcard saved · ${renderer.domElement.width} × ${renderer.domElement.height} pixels`);});
 $('about-open').addEventListener('click',()=>{$('about').showModal();nav.clearInput();});$('about-close').addEventListener('click',()=>$('about').close());$('about').addEventListener('click',e=>{if(e.target===$('about')){const r=$('about').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('about').close();}});
 $('selection-close').addEventListener('click',closeSelection);$('panel-toggle').addEventListener('click',()=>$('explorer').classList.toggle('open'));
 $('search').addEventListener('input',()=>{
  const q=$('search').value.trim().toLocaleLowerCase(),results=$('search-results');results.replaceChildren();results.hidden=!q;if(!q)return;
  const matches=city.buildings.map((b,i)=>[b,i]).filter(([b])=>b.name.toLocaleLowerCase().includes(q)||b.zh.includes(q)).sort((a,b)=>b[0].height-a[0].height).filter(([b],i,all)=>all.findIndex(([a])=>(a.parent||a.id)===(b.parent||b.id))===i).slice(0,8);
  if(!matches.length){const p=document.createElement('p');p.className='source-note';p.textContent='No building found in this first district.';results.append(p);}
  for(const [b,i] of matches){const button=document.createElement('button');button.textContent=b.name||b.zh;button.addEventListener('click',()=>{selectBuilding(i,true);results.hidden=true;$('search').blur();if(innerWidth<=760)$('explorer').classList.remove('open');});results.append(button);}
 });
 let pointerStart;
 renderer.domElement.addEventListener('pointerdown',e=>{pointerStart={x:e.clientX,y:e.clientY};});
 renderer.domElement.addEventListener('pointerup',e=>{if(nav.mode!=='orbit'||!pointerStart||Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5)return;if(!buildings.group.visible)return;
  raycaster.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);const hit=raycaster.intersectObjects(buildings.group.children)[0];if(hit)selectBuilding(Math.round(hit.object.geometry.attributes.feature.getX(hit.face.a)));else closeSelection();
 });
 controls.addEventListener('start',()=>{tween=null;});
 addEventListener('keydown',e=>{
  if(e.code==='Escape'){if($('about').open)return;if(document.activeElement===$('search')){$('search-results').hidden=true;$('search').blur();return;}if(nav.mode!=='orbit')nav.setMode('orbit',PLACES[place].spawn);else closeSelection();return;}
  if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable||$('about').open||e.repeat)return;
  if(e.code==='Slash'){e.preventDefault();$('explorer').classList.add('open');$('search').focus();}
  const m={Digit1:'orbit',Digit2:'walk',Digit3:'fly'}[e.code];if(m)nav.setMode(m,PLACES[place].spawn);
 });
 addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.5:1.75));renderer.setSize(innerWidth,innerHeight);});
}
async function loadJSON(path){const r=await fetch(path);if(!r.ok)throw new Error(`${path}: HTTP ${r.status}`);return r.json();}
async function init(){
 renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,logarithmicDepthBuffer:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.5:1.75));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 $('viewport').append(renderer.domElement);renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','3D city: drag to orbit, scroll to zoom, click a building for details');
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();toast('Graphics paused. Reload the page to restore the city.');});
 scene=new THREE.Scene();scene.background=new THREE.Color('#d9e3d5');scene.fog=new THREE.Fog('#d9e3d5',8000,36000);
 camera=new THREE.PerspectiveCamera(44,innerWidth/innerHeight,.5,100000);
 controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.minDistance=12;controls.maxDistance=65000;controls.maxPolarAngle=Math.PI*.475;controls.screenSpacePanning=false;
 ambient=new THREE.HemisphereLight('#e8f0e6','#6c806a',1.9);scene.add(ambient);
 sun=new THREE.DirectionalLight('#fff7df',3);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-2200,right:2200,top:2200,bottom:-2200,near:10,far:12000});sun.shadow.bias=-.00007;sun.shadow.normalBias=1.2;sun.shadow.radius=2;scene.add(sun,sun.target);
 [city,terrain]=await Promise.all([loadJSON('city/data/central.json'),loadJSON('city/data/terrain.json')]);
 $('loading-detail').textContent=`Placing ${city.buildings.length.toLocaleString('en-HK')} building forms on the map…`;
 sampler=makeTerrainSampler(terrain);index=new BuildingIndex(city.buildings);
 const terrainData=terrain;terrain=makeTerrain(terrainData);terrain.userData.data=terrainData;scene.add(terrain);
 water=makeWater();scene.add(water.mesh);
 await new Promise(r=>setTimeout(r,50));buildings=await makeBuildings(city.buildings);scene.add(buildings.group);
 $('loading-detail').textContent='Tracing the streets and planting the parks…';await new Promise(r=>setTimeout(r,20));
 roads=makeRoads(city.roads,sampler);scene.add(roads);nature=makeNature(city.parks,terrainData,sampler,index);scene.add(nature.group);ferries=makeFerries();scene.add(ferries.group);
 nav=new Navigation({camera,controls,scene,canvas:renderer.domElement,sampler,index,toast,onMode});
 bindUI();makeLabels();setTime(15);const initial=new URLSearchParams(location.search).get('district');goPlace(Object.hasOwn(PLACES,initial)?initial:'central',false);
 $('data-summary').textContent=`${city.buildings.length.toLocaleString('en-HK')} building forms · OSM`;$('snapshot-date').textContent=city.meta.snapshot.slice(0,10);
 // Read-only diagnostics for reproducible browser verification and performance inspection.
 window.__city={get ready(){return true;},get state(){return {mode:nav.mode,position:nav.position.toArray(),camera:camera.position.toArray(),distance:nav.distance,speed:nav.speed,firstPerson:nav.firstPerson,time:worldTime,place,selectedIndex,layers:{buildings:buildings.group.visible,roads:roads.visible,trees:nature.group.visible,labels:!$('labels').hidden},render:{calls:renderer.info.render.calls,triangles:renderer.info.render.triangles},counts:city.meta.counts,trees:nature.count,actorHeight:new THREE.Box3().setFromObject(nav.walker).getSize(new THREE.Vector3()).y,collision:!!index.collision(nav.position.x,nav.position.z,nav.position.y,nav.position.y+1.8,.5)};}};
 startTime=performance.now();requestAnimationFrame(animate);
 $('loading').style.opacity='0';setTimeout(()=>$('loading').hidden=true,750);
}
let lastTime=0;
function animate(now){
 requestAnimationFrame(animate);const dt=Math.min((now-(lastTime||now))/1000,.05);lastTime=now;
 const paused=document.hidden||$('about').open;
 if(tween&&!paused){tween.elapsed+=dt;const u=Math.min(1,tween.elapsed/tween.duration),v=u*u*(3-2*u);camera.position.lerpVectors(tween.from,tween.to,v);controls.target.lerpVectors(tween.targetFrom,tween.targetTo,v);if(u===1)tween=null;}
 if(nav.mode==='orbit'){controls.update();const ground=sampler.height(camera.position.x,camera.position.z);if(camera.position.y<ground+2)camera.position.y=ground+2;}else if(!paused)nav.update(dt);
 const focus=nav.mode==='orbit'?controls.target:nav.position;sun.target.position.set(focus.x,0,focus.z);sun.position.set(focus.x+Math.cos((worldTime-6)/12*Math.PI)*3300,Math.max(600,Math.sin((worldTime-6)/12*Math.PI)*4400),focus.z+1800);
 if(!reduced&&!paused){water.time.value+=dt;ferries.update((now-startTime)/1000);}
 frameCount++;
 if(now-lastHud>250){
  updateLabels();drawMinimap();
  if(nav.mode==='walk'){$('journey-value').textContent=`${Math.round(nav.distance)} m`;$('journey-detail').textContent=nav.firstPerson?'First person':'Taking the scenic route';}
  if(nav.mode==='fly'){$('journey-value').textContent=`${Math.round(nav.position.y)} m`;$('journey-detail').textContent=`${Math.round(nav.speed*3.6)} km/h · ${nav.firstPerson?'Pilot’s eye':'Chase camera'}`;}
  lastHud=now;
 }
 renderer.render(scene,camera);
}
init().catch(error=>{console.error('City failed to load',error);$('loading-detail').textContent=`The city could not load. ${error.message}. Reload to try again.`;$('loading').querySelector('.loading-line').hidden=true;});
