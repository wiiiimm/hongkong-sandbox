import * as THREE from '../vendor/three.module.js';
import {OrbitControls} from '../vendor/OrbitControls.js';
import {makeTerrainSampler,smoothStep} from './geo.js';
import {makeTerrain,makeWater,makeFerries,extrudeBuilding} from './world.js';
import {Navigation} from './navigation.js';
import {CityStreaming} from './streaming.js';
import {PLACES,REGIONS,closestPlace} from './places.js';
const $=id=>document.getElementById(id),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let place='central',region='island',scene,camera,renderer,controls,nav,sampler,stream,terrain,water,manifest,ferries,sun,ambient,selection,tween;
let catalogue=[],overview={},cataloguePromise,travel=0,modeRequest=0,selectedId=null,selectedIndex=-1,loadingTravel=false,lastHud=0,lastStream=0,startTime=0;
let toastTimer,worldTime=15,mapBackdrop,mapStamp,mapBounds=[-3600,-2600,3600,2900];
const labelEntries=[],temp=new THREE.Vector3(),raycaster=new THREE.Raycaster();
function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),4400);}
function transition(position,target,duration=1.6){tween={from:camera.position.clone(),to:new THREE.Vector3(...position),targetFrom:controls.target.clone(),targetTo:new THREE.Vector3(...target),elapsed:0,duration:reduced?.001:duration};}
function regionUI(key){
 region=key;document.querySelectorAll('[data-region]').forEach(b=>{b.classList.toggle('active',b.dataset.region===key);b.setAttribute('aria-pressed',b.dataset.region===key);});
 document.querySelectorAll('[data-place]').forEach(b=>b.hidden=PLACES[b.dataset.place].region!==key);
 $('chapter-label').textContent=`${String(Object.keys(REGIONS).indexOf(key)+1).padStart(2,'0')} — ${REGIONS[key].title.toUpperCase()}`;
}
function updatePlace(key){
 place=key;const p=PLACES[key];regionUI(p.region);$('place-title').replaceChildren(document.createTextNode(`${p.title} `));const zh=document.createElement('span');zh.textContent=p.zh;$('place-title').append(zh);
 $('place-subtitle').textContent=REGIONS[p.region].title.toUpperCase()+' · '+REGIONS[p.region].zh;$('place-description').textContent=p.description;
 document.querySelectorAll('[data-place]').forEach(b=>{b.classList.toggle('active',b.dataset.place===key);b.setAttribute('aria-pressed',b.dataset.place===key);});
 history.replaceState(null,'',`${location.pathname}?district=${key}`);if(innerWidth<=760)$('explorer').classList.remove('open');
}
async function goPlace(key,animate=true){
 const token=++travel;++modeRequest;loadingTravel=true;const p=PLACES[key];if(nav.mode!=='orbit')nav.setMode('orbit',p.spawn);
 updatePlace(key);closeSelection();const pos=p.target.map((x,i)=>x+p.offset[i]);
 if(animate)transition(pos,p.target);else{camera.position.set(...pos);controls.target.set(...p.target);controls.update();}
 updateStreamStatus();
 try{await stream.arrive(p.target[0],p.target[2],key==='lantaupeaks'?6000:3200);if(token!==travel)return;}
 catch(error){if(token===travel&&error.name!=='AbortError')toast('This area could not finish loading. Use Retry to try again.');}
 finally{if(token===travel){loadingTravel=false;updateStreamStatus();}}
}
async function chooseMode(mode){
 if(mode==='orbit'){++modeRequest;nav.setMode(mode,PLACES[place].spawn);return;}
 const token=++modeRequest,p=PLACES[place],origin=mode==='fly'?[p.spawn[0]+600,p.spawn[1]-1000]:p.spawn;
 try{await stream.arrive(...origin,3200);if(token===modeRequest)nav.setMode(mode,p.spawn);}
 catch(error){if(error.name!=='AbortError')toast('Movement is waiting for this area. Retry the city download.');}
}
function onMode(mode){
 tween=null;camera.fov=mode==='orbit'?44:mode==='walk'?60:52;camera.updateProjectionMatrix();document.body.classList.toggle('exploring-person',mode!=='orbit');
 document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode);});
 $('journey').hidden=mode==='orbit';$('journey-mode').textContent=mode==='walk'?'ON FOOT':'IN THE AIR';
 $('control-hint').innerHTML=mode==='orbit'?'Drag to orbit <i>·</i> Scroll to get closer <i>·</i> Click a building to discover':mode==='walk'?'WASD move <i>·</i> Drag to look <i>·</i> Shift run <i>·</i> C camera <i>·</i> Esc explore':'W / S climb & descend <i>·</i> A / D turn <i>·</i> Shift boost <i>·</i> C camera <i>·</i> Esc explore';
 $('touch-controls').hidden=mode==='orbit'||!matchMedia('(pointer: coarse)').matches;if(mode!=='orbit')closeSelection();
 const extent=mode==='walk'?80:mode==='fly'?900:2200;Object.assign(sun.shadow.camera,{left:-extent,right:extent,top:extent,bottom:-extent});sun.shadow.camera.updateProjectionMatrix();sun.shadow.normalBias=mode==='walk'?.06:1.2;
}
function setTime(value){
 worldTime=value;const night=smoothStep(17.6,20,value),gold=Math.sin(smoothStep(15,20,value)*Math.PI);
 const bg=new THREE.Color('#d9e3d5').lerp(new THREE.Color('#d6c4a2'),gold*.48).lerp(new THREE.Color('#142b35'),night);scene.background=bg;scene.fog.color.copy(bg);
 sun.color.set('#fff7df').lerp(new THREE.Color('#ffc080'),gold*.72);sun.intensity=3*(1-night)+.24;
 ambient.intensity=1.9*(1-night)+.62;ambient.color.set('#e8f0e6').lerp(new THREE.Color('#95b9d8'),night);ambient.groundColor.set('#6c806a').lerp(new THREE.Color('#20392f'),night);
 stream.night.value=night;water.material.color.set('#71a8a0').lerp(new THREE.Color('#173e4a'),night);water.material.roughness=.38+night*.4;water.material.metalness=.25-night*.15;water.material.emissive.set('#25434c');water.material.emissiveIntensity=night*.4;
 renderer.toneMappingExposure=1.05*(1-night)+.95*night;document.body.classList.toggle('night',night>.5);$('time-output').textContent=`${Math.floor(value).toString().padStart(2,'0')}:${Math.round(value%1*60).toString().padStart(2,'0')}`;
}
function closeSelection(){selectedId=null;selectedIndex=-1;$('building-card').hidden=true;if(selection){scene.remove(selection);selection.geometry.dispose();selection.material.dispose();selection=null;}}
function selectBuilding(b){
 if(!b)return;closeSelection();selectedId=b.uid;selectedIndex=0;
 const geo=extrudeBuilding(b);selection=new THREE.LineSegments(new THREE.EdgesGeometry(geo,25),new THREE.LineBasicMaterial({color:'#e8ae4f',transparent:true,opacity:.95,depthTest:false}));geo.dispose();selection.renderOrder=10;scene.add(selection);
 $('building-name').textContent=b.name||'A Hong Kong building';$('building-zh').textContent=b.zh||`${b.kind.replaceAll('_',' ')} · OpenStreetMap footprint`;$('building-height').textContent=`${b.height} m`;$('building-levels').textContent=b.levels??'—';
 $('building-source').textContent=b.heightSource==='tagged'?'Height tagged in OpenStreetMap. Simplified massing; façade details are illustrative.':b.heightSource==='levels'?'Estimated height from mapped floor count × 3.2 m. Not a surveyed measurement.':'Height is an illustrative fallback. This footprint has no mapped height or floor count.';
 $('building-osm').href=`https://www.openstreetmap.org/${b.id}`;$('building-card').hidden=false;
}
async function visitBuilding(b){
 const token=++travel;++modeRequest;loadingTravel=true;if(nav.mode!=='orbit')nav.setMode('orbit',b.centre);updatePlace(closestPlace(...b.centre));closeSelection();
 const radius=Math.max(100,b.height*2.1);transition([b.centre[0]+radius*.75,b.base+b.height+radius*.5,b.centre[1]-radius],[b.centre[0],b.base+b.height*.45,b.centre[1]],1.2);
 try{const full=await stream.getBuilding(b.tile,b.uid);if(token===travel){selectBuilding(full);stream.plan(...b.centre,3200);}}
 catch(error){if(error.name!=='AbortError')toast('This building could not load. Retry the city download.');}
 finally{if(token===travel){loadingTravel=false;updateStreamStatus();}}
}
function makeLabels(){
 for(const {el} of labelEntries)el.remove();labelEntries.length=0;
 const add=(text,pos,kind='landmark')=>{const el=document.createElement('div');el.className=`map-label ${kind}`;el.textContent=text;$('labels').append(el);labelEntries.push({el,pos:new THREE.Vector3(...pos),kind});};
 for(const [text,needle] of [['IFC','Two International Finance Centre'],['Jardine House','Jardine House'],['HSBC','HSBC Main Building'],['Bank of China','Bank of China Tower'],['Central Plaza','Central Plaza'],['ICC','International Commerce Centre'],['Langham Place','Langham Place'],['Citygate','One Citygate']]){
  const b=catalogue.filter(b=>b.name===needle).sort((a,b)=>b.height-a.height)[0];if(b)add(text,[b.centre[0],b.base+b.height+28,b.centre[1]]);
 }
 add('Victoria Harbour · 維多利亞港',[600,4,-260],'harbour');
 for(const p of Object.values(PLACES))if(p!==PLACES.lantaupeaks)add(p.zh,[p.target[0],sampler.height(p.target[0],p.target[2])+70,p.target[2]+150],'district-name');
}
function updateLabels(){
 const w=innerWidth,h=innerHeight,occupied=[];
 for(const {el,pos,kind} of labelEntries){
  temp.copy(pos).project(camera);const distance=camera.position.distanceTo(pos),x=(temp.x*.5+.5)*w,y=(-temp.y*.5+.5)*h;
  const off=nav.mode!=='orbit'||distance>6500||distance<120||temp.z>1||temp.z<0||x<16||x>w-16||y<84||y>h-100||(x<330&&w>760)||(kind==='harbour'&&distance<800);
  const overlap=occupied.some(([xx,yy])=>Math.abs(xx-x)<100&&Math.abs(yy-y)<35);el.style.opacity=off||overlap?'0':'1';if(!off&&!overlap){el.style.left=`${x}px`;el.style.top=`${y}px`;occupied.push([x,y]);}
 }
}
function mapCoords(x,z){return[(x-mapBounds[0])/(mapBounds[2]-mapBounds[0])*440,(z-mapBounds[1])/(mapBounds[3]-mapBounds[1])*280];}
function drawMinimap(){
 const canvas=$('minimap'),ctx=canvas.getContext('2d'),focus=nav.mode==='orbit'?controls.target:nav.position;
 const span=place==='lantaupeaks'&&nav.mode==='orbit'?22000:6400,cx=Math.round(focus.x/1000)*1000,cz=Math.round(focus.z/1000)*1000;mapBounds=[cx-span/2,cz-span*.32,cx+span/2,cz+span*.32];
 const stamp=[cx,cz,span,worldTime>19,Object.keys(overview).length].join('|');
 if(stamp!==mapStamp){
  ctx.fillStyle=worldTime>19?'#1d4645':'#9fbeb2';ctx.fillRect(0,0,440,280);const data=terrain.userData.data,g=data.meta.georef;ctx.fillStyle=worldTime>19?'#66816c':'#dce3c9';
  const step=span>10000?3:1,a=mapCoords(0,0),b=mapCoords(g.aE*step,Math.abs(g.aN)*step),sx=b[0]-a[0]+.5,sy=b[1]-a[1]+.5;
  for(let r=0;r<data.h;r+=step)for(let c=0;c<data.w;c+=step){if(data.elev[r*data.w+c]<=.1)continue;const [x,y]=mapCoords(g.bE+c*g.aE-834500,816500-(g.bN+r*g.aN));if(x<-sx||y<-sy||x>440||y>280)continue;ctx.fillRect(x,y,sx,sy);}
  ctx.fillStyle=worldTime>19?'#b1b88d':'#829b7a';for(const points of Object.values(overview))for(const [px,pz] of points){const [x,y]=mapCoords(px,pz);if(x>=0&&x<=440&&y>=0&&y<=280)ctx.fillRect(x,y,1.4,1.4);}
  mapBackdrop=ctx.getImageData(0,0,440,280);mapStamp=stamp;
 }else ctx.putImageData(mapBackdrop,0,0);
 const [x,y]=mapCoords(focus.x,focus.z);ctx.save();ctx.translate(x,y);ctx.fillStyle='#385b45';ctx.strokeStyle='#f7fae8';ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(0,0,7,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.rotate(nav.mode==='orbit'?Math.atan2(camera.position.x-focus.x,-(camera.position.z-focus.z)):nav.heading);ctx.beginPath();ctx.moveTo(0,-18);ctx.lineTo(-5,-9);ctx.lineTo(5,-9);ctx.closePath();ctx.fill();ctx.restore();
 $('map-location').textContent=PLACES[closestPlace(focus.x,focus.z)].title.toUpperCase();$('map-scale').textContent=span>10000?'5 km ━':'1 km ━';
}
function updateStreamStatus(){
 if(!stream)return;const s=stream.stats,bar=$('stream-status');bar.hidden=!s.pending&&!s.errors.length&&!loadingTravel;
 $('stream-message').textContent=s.errors.length?'Some city sections could not load':loadingTravel?`Arriving in ${PLACES[place].title}…`:`Unfolding the neighbourhood · ${s.loaded}/${s.wanted}`;
 $('stream-retry').hidden=!s.errors.length;$('data-summary').textContent=`${manifest.counts.buildings.toLocaleString('en-HK')} building forms · OSM`;
}
async function getCatalogue(){
 if(!cataloguePromise)cataloguePromise=loadJSON(manifest.catalogue).then(data=>{catalogue=data;makeLabels();return data;}).catch(error=>{cataloguePromise=null;throw error;});return cataloguePromise;
}
async function search(){
 const q=$('search').value.trim().toLocaleLowerCase(),results=$('search-results');results.replaceChildren();results.hidden=!q;if(!q)return;
 const note=text=>{const p=document.createElement('p');p.className='source-note';p.textContent=text;results.replaceChildren(p);};
 if(!catalogue.length)note('Looking across Hong Kong…');
 try{await getCatalogue();}catch{note('Search could not load. Type again to retry.');return;}
 if($('search').value.trim().toLocaleLowerCase()!==q)return;results.replaceChildren();
 const seen=new Set(),matches=catalogue.filter(b=>b.name.toLocaleLowerCase().includes(q)||b.zh.includes(q)).sort((a,b)=>b.height-a.height).filter(b=>{const id=b.parent||b.id;if(seen.has(id))return false;seen.add(id);return true;}).slice(0,8);
 if(!matches.length)note('No building found in the mapped areas.');
 for(const b of matches){const button=document.createElement('button');button.textContent=b.name||b.zh;const small=document.createElement('small');small.textContent=PLACES[closestPlace(...b.centre)].title;button.append(small);button.addEventListener('click',()=>{visitBuilding(b);results.hidden=true;$('search').blur();});results.append(button);}
}
function bindUI(){
 const districts=$('district-list');for(const [key,p] of Object.entries(PLACES)){
  const b=document.createElement('button');b.className='district';b.dataset.place=key;const symbol=document.createElement('span');symbol.className='district-symbol';symbol.textContent=p.zh[0];const names=document.createElement('span');const title=document.createElement('b');title.textContent=p.title;const subtitle=document.createElement('small');subtitle.textContent=p.zh;names.append(title,subtitle);const arrow=document.createElement('span');arrow.className='arrow';arrow.textContent='↗';b.append(symbol,names,arrow);b.addEventListener('click',()=>goPlace(key));districts.append(b);
 }
 document.querySelectorAll('[data-region]').forEach(b=>b.addEventListener('click',()=>regionUI(b.dataset.region)));
 document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>chooseMode(b.dataset.mode)));
 const layers={buildings:stream.buildings,roads:stream.roads,trees:stream.trees};
 for(const key of ['buildings','roads','trees','labels'])$(`layer-${key}`).addEventListener('change',e=>{if(key==='labels')$('labels').hidden=!e.target.checked;else layers[key].visible=e.target.checked;if(key==='buildings'&&!e.target.checked)closeSelection();$('layer-count').textContent=`${document.querySelectorAll('.layers input:checked').length} LAYERS`;});
 $('time').addEventListener('input',e=>setTime(Number(e.target.value)));$('stream-retry').addEventListener('click',()=>stream.cache.retry());
 $('reset-view').addEventListener('click',()=>goPlace(place));$('top-view').addEventListener('click',()=>{if(nav.mode!=='orbit')nav.setMode('orbit',PLACES[place].spawn);const p=controls.target;transition([p.x,p.y+(place==='lantaupeaks'?18000:3300),p.z+.1],[p.x,p.y,p.z],1.3);});
 $('north-view').addEventListener('click',()=>{if(nav.mode!=='orbit')return;const p=controls.target,d=camera.position.distanceTo(p);transition([p.x,p.y+d*.72,p.z+d*.7],[p.x,p.y,p.z]);});
 $('postcard').addEventListener('click',()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download=`hong-kong-astra-${place}-${renderer.domElement.width}x${renderer.domElement.height}.png`;a.href=renderer.domElement.toDataURL('image/png');a.click();toast(`Postcard saved · ${renderer.domElement.width} × ${renderer.domElement.height} pixels`);});
 $('about-open').addEventListener('click',()=>{$('about').showModal();nav.clearInput();});$('about-close').addEventListener('click',()=>$('about').close());$('about').addEventListener('click',e=>{if(e.target===$('about')){const r=$('about').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('about').close();}});
 $('selection-close').addEventListener('click',closeSelection);$('panel-toggle').addEventListener('click',()=>$('explorer').classList.toggle('open'));$('search').addEventListener('input',search);
 let pointerStart;renderer.domElement.addEventListener('pointerdown',e=>{pointerStart={x:e.clientX,y:e.clientY};});
 renderer.domElement.addEventListener('pointerup',e=>{if(nav.mode!=='orbit'||!pointerStart||Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5||!stream.buildings.visible)return;
  raycaster.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);const meshes=stream.buildings.children.filter(g=>g.visible).flatMap(g=>g.children);const hit=raycaster.intersectObjects(meshes)[0];if(hit)selectBuilding(stream.featureAt(hit));else closeSelection();
 });
 controls.addEventListener('start',()=>{tween=null;++travel;loadingTravel=false;});
 addEventListener('keydown',e=>{
  if(e.code==='Escape'){if($('about').open)return;if(document.activeElement===$('search')){$('search-results').hidden=true;$('search').blur();return;}if(nav.mode!=='orbit')chooseMode('orbit');else closeSelection();return;}
  if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable||$('about').open||e.repeat)return;
  if(e.code==='Slash'){e.preventDefault();$('explorer').classList.add('open');$('search').focus();}const m={Digit1:'orbit',Digit2:'walk',Digit3:'fly'}[e.code];if(m)chooseMode(m);
 });
 addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.5:1.75));renderer.setSize(innerWidth,innerHeight);});
}
async function loadJSON(path){const r=await fetch(path);if(!r.ok)throw new Error(`${path}: HTTP ${r.status}`);return r.json();}
async function init(){
 renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,logarithmicDepthBuffer:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.5:1.75));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 $('viewport').append(renderer.domElement);renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','3D city: drag to orbit, scroll to zoom, click a building for details');renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();toast('Graphics paused. Reload the page to restore the city.');});
 scene=new THREE.Scene();scene.background=new THREE.Color('#d9e3d5');scene.fog=new THREE.Fog('#d9e3d5',8000,36000);camera=new THREE.PerspectiveCamera(44,innerWidth/innerHeight,.5,100000);
 controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.minDistance=12;controls.maxDistance=65000;controls.maxPolarAngle=Math.PI*.475;controls.screenSpacePanning=false;
 ambient=new THREE.HemisphereLight('#e8f0e6','#6c806a',1.9);scene.add(ambient);sun=new THREE.DirectionalLight('#fff7df',3);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-2200,right:2200,top:2200,bottom:-2200,near:10,far:12000});sun.shadow.bias=-.00007;sun.shadow.normalBias=1.2;sun.shadow.radius=2;scene.add(sun,sun.target);
 const [m,data]=await Promise.all([loadJSON('city/data/manifest.json'),loadJSON('city/data/terrain.json')]);manifest=m;sampler=makeTerrainSampler(data);terrain=makeTerrain(data);terrain.userData.data=data;scene.add(terrain);water=makeWater();scene.add(water.mesh);
 stream=new CityStreaming({manifest,terrain:data,sampler,scene,onChange:updateStreamStatus});ferries=makeFerries();scene.add(ferries.group);
 nav=new Navigation({camera,controls,scene,canvas:renderer.domElement,sampler,index:stream,toast,onMode});bindUI();setTime(15);makeLabels();
 $('snapshot-date').textContent=manifest.snapshot.slice(0,10);$('loading').style.opacity='0';setTimeout(()=>$('loading').hidden=true,750);
 window.__city={get ready(){return true;},get state(){return {mode:nav.mode,position:nav.position.toArray(),camera:camera.position.toArray(),distance:nav.distance,speed:nav.speed,firstPerson:nav.firstPerson,time:worldTime,place,region,selectedId,selectedIndex,loadingTravel,travelling:!!tween,stream:stream.stats,layers:{buildings:stream.buildings.visible,roads:stream.roads.visible,trees:stream.trees.visible,labels:!$('labels').hidden},render:{calls:renderer.info.render.calls,triangles:renderer.info.render.triangles},counts:manifest.counts,trees:stream.stats.trees,actorHeight:new THREE.Box3().setFromObject(nav.walker).getSize(new THREE.Vector3()).y,collision:!!stream.collision(nav.position.x,nav.position.z,nav.position.y,nav.position.y+1.8,.5),movementReady:stream.readyAt(nav.position.x,nav.position.z,350),tiles:[...stream.cache.entries.keys()]};}};
 startTime=performance.now();requestAnimationFrame(animate);const initial=new URLSearchParams(location.search).get('district');goPlace(Object.hasOwn(PLACES,initial)?initial:'central',false);
 // Search and overview data arrive independently; neither blocks movement or terrain.
 getCatalogue().catch(()=>{});loadJSON(manifest.overview).then(data=>{overview=data;}).catch(()=>{});
}
let lastTime=0;
function animate(now){
 requestAnimationFrame(animate);const dt=Math.min((now-(lastTime||now))/1000,.05);lastTime=now;const paused=document.hidden||$('about').open;
 if(tween&&!paused){tween.elapsed+=dt;const u=Math.min(1,tween.elapsed/tween.duration),v=u*u*(3-2*u);camera.position.lerpVectors(tween.from,tween.to,v);controls.target.lerpVectors(tween.targetFrom,tween.targetTo,v);if(u===1)tween=null;}
 const focus=nav.mode==='orbit'?controls.target:nav.position;
 if(now-lastStream>600&&!loadingTravel){stream.plan(focus.x,focus.z,nav.mode==='orbit'?Math.min(6000,Math.max(2600,camera.position.distanceTo(focus))):3200);lastStream=now;}
 if(nav.mode==='orbit'){controls.update();const ground=sampler.height(camera.position.x,camera.position.z);if(camera.position.y<ground+2)camera.position.y=ground+2;}else if(!paused&&stream.readyAt(nav.position.x,nav.position.z,350))nav.update(dt);
 sun.target.position.set(focus.x,0,focus.z);sun.position.set(focus.x+Math.cos((worldTime-6)/12*Math.PI)*3300,Math.max(600,Math.sin((worldTime-6)/12*Math.PI)*4400),focus.z+1800);
 if(!reduced&&!paused){water.time.value+=dt;ferries.update((now-startTime)/1000);}
 if(now-lastHud>300){updateLabels();drawMinimap();updateStreamStatus();
  if(nav.mode==='walk'){$('journey-value').textContent=`${Math.round(nav.distance)} m`;$('journey-detail').textContent=stream.readyAt(nav.position.x,nav.position.z,350)?nav.firstPerson?'First person':'Taking the scenic route':'Waiting for the neighbourhood…';}
  if(nav.mode==='fly'){$('journey-value').textContent=`${Math.round(nav.position.y)} m`;$('journey-detail').textContent=stream.readyAt(nav.position.x,nav.position.z,350)?`${Math.round(nav.speed*3.6)} km/h · ${nav.firstPerson?'Pilot’s eye':'Chase camera'}`:'Waiting for the neighbourhood…';}lastHud=now;
 }renderer.render(scene,camera);
}
init().catch(error=>{console.error('City failed to load',error);$('loading-detail').textContent=`The city could not load. ${error.message}. Reload to try again.`;$('loading').querySelector('.loading-line').hidden=true;});
