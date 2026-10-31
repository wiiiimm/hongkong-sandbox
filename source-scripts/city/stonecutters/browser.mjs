/** Real-city before/after acceptance. Run only after reserving the shared GPU slot. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const root=new URL('../../../',import.meta.url),phase=process.argv[2];
assert.ok(['before','after'].includes(phase),'Usage: node source-scripts/city/stonecutters/browser.mjs before|after');
const require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const output=new URL(`docs/astra-city/stonecutters/browser/${phase}/`,root);await mkdir(output,{recursive:true});
const read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const hash=async p=>createHash('sha256').update(await readFile(new URL(p,root))).digest('hex');
const source=phase==='after'?await read('3d-viewer/city/data/bridges-stonecutters.json'):null;
const expected=source?{models:source.models.map(m=>({id:m.id,triangles:m.modelGeometry.triangles,worldBounds:m.worldBounds,buildingUids:m.suppressesBuildingUids,proxies:m.suppresses})),clips:source.proxyClips||[]}:null;
const report={phase,started:new Date().toISOString(),commit:execFileSync('git',['rev-parse','HEAD'],{cwd:root}).toString().trim(),manifestSha256:await hash('3d-viewer/city/data/manifest.json'),terrainSha256:await hash('3d-viewer/city/data/terrain.json'),checks:[],views:[],errors:[],failures:[]};
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
page.on('pageerror',e=>report.errors.push(e.message));page.on('response',r=>{if(r.url().includes('/city/data/')&&r.status()>=400)report.failures.push({url:r.url(),status:r.status()});});
page.on('console',m=>{if(m.type()==='error'&&/shader|webgl|gl_invalid/i.test(m.text()))report.errors.push(m.text());});
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state,d=window.__bridgeCluster;return s&&d&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending&&!d.cableLayer?.stats.pending&&![...d.stream.cache.entries.values()].some(e=>e.infrastructureUpdate);},null,{timeout:120000});
async function tab(name){if(!await page.evaluate(()=>window.__city.state.controls.expanded))await page.locator('#panel-toggle').click();await page.locator('#tab-'+name).click();}
async function closePanel(){if(await page.evaluate(()=>window.__city.state.controls.expanded))await page.locator('#panel-toggle').click();}
async function capture(name){await page.screenshot({path:new URL(name+'.png',output).pathname});report.views.push({name,state:await page.evaluate(()=>window.__city.state)});}
async function frame(name,eye,target,hour='15:00'){
 await tab('time');await page.locator('#time').fill(hour);await closePanel();
 await page.evaluate(async({eye,target})=>{const d=window.__bridgeCluster;if(d.nav.mode!=='orbit')d.nav.setMode('orbit',[target[0],target[2]]);d.camera.position.fromArray(eye);d.controls.target.fromArray(target);d.controls.update();d.camera.updateMatrixWorld();d.bridgeLayer.plan(target[0],target[2],3000,d.camera.position);await d.stream.arrive(target[0],target[2],3200);},{eye,target});
 await settle();await page.waitForTimeout(350);if(name)await capture(name);
}
async function clickGeometry(id,illustrative=false){
 const point=await page.evaluate(({id,illustrative})=>{
  const {camera,THREE,bridgeLayer,stream,cableLayer}=window.__bridgeCluster,layer=illustrative?cableLayer:bridgeLayer,m=layer.records.get(id);if(!m)throw Error('Missing selectable geometry '+id);
  const p=m.modelGeometry.position,ray=new THREE.Raycaster(),stride=Math.max(1,Math.floor(p.length/9/1400));let attempts=0;
  for(let t=0;t<p.length/9;t+=stride){const i=t*9,v=new THREE.Vector3((p[i]+p[i+3]+p[i+6])/3,(p[i+1]+p[i+4]+p[i+7])/3,(p[i+2]+p[i+5]+p[i+8])/3).project(camera);if(v.z<0||v.z>1||Math.abs(v.x)>.8||Math.abs(v.y)>.75)continue;
   const x=Math.round((v.x+1)*innerWidth/2),y=Math.round((1-v.y)*innerHeight/2),element=document.elementFromPoint(x,y);if(element?.tagName!=='CANVAS')continue;
   ray.setFromCamera(new THREE.Vector2(x/innerWidth*2-1,1-y/innerHeight*2),camera);const hit=ray.intersectObjects([...bridgeLayer.pickMeshes(),...(cableLayer?.pickMeshes()||[]),...stream.pickMeshes(ray.ray)],false)[0];attempts++;if(hit&&layer.featureAt(hit)?.id===id)return {id,click:[x,y],attempts};
  }throw Error('No unobscured real city click ray for '+id+' after '+attempts+' candidates');
 },{id,illustrative});
 await page.mouse.click(...point.click);await page.waitForFunction(id=>window.__city.state.selectedId===id,id,{timeout:5000});assert.equal(await page.locator('#building-card').isVisible(),true);
 const card=await page.locator('#building-card').innerText();assert.doesNotMatch(card,/undefined|NaN/);
 if(illustrative){assert.match(card,/illustrative|estimated/i);assert.doesNotMatch(await page.locator('#building-levels-label').innerText(),/^SOURCE TRIANGLES$/);}
 else{assert.equal(await page.locator('#building-height-label').innerText(),'MODEL · HKPD');assert.match(card,/Lands Department/);assert.match(card,/pedestrian access|walking access|No public|Motorway/i);}
 await capture((illustrative?'illustrative-cable-card-':'original-source-card-')+id.split('/').at(-1));await page.locator('#selection-close').click();return {...point,card};
}
async function measure(){await page.emulateMedia({reducedMotion:'no-preference'});return page.evaluate(async()=>{const frames=[];let last;for(let i=0;i<180;i++){const now=await new Promise(requestAnimationFrame);if(i>20)frames.push(now-last);last=now;}frames.sort((a,b)=>a-b);return {frames:frames.length,medianFrameMs:frames[Math.floor(frames.length*.5)],p95FrameMs:frames[Math.floor(frames.length*.95)],render:window.__city.state.render};});}
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__bridgeCluster",{get:()=>({stream,camera,controls,sampler,renderer,THREE,nav,bridgeLayer,terrain,water,environment,cableLayer:typeof cableLayer===\"undefined\"?null:cableLayer})});\n'});});
 await page.goto(process.env.CITY_URL||'http://127.0.0.1:4176/city.html?district=tsingyi');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 await tab('weather');await page.locator('#weather-mode').selectOption('manual');
 for(const id of ['weather-rain','weather-clouds','weather-fog','weather-wind','weather-waves','weather-snow'])await page.locator('#'+id).evaluate(e=>{e.value='0';e.dispatchEvent(new Event('input',{bubbles:true}));});
 await page.locator('#atmospheric-haze').evaluate(e=>{e.value='35';e.dispatchEvent(new Event('input',{bubbles:true}));});
 await tab('time');await page.locator('#sky-date').fill('2026-09-07');await page.locator('#sky-date').dispatchEvent('change');await tab('weather');
 await page.locator('#tide-level').evaluate(e=>{e.value='.3';e.dispatchEvent(new Event('input',{bubbles:true}));});await closePanel();
 report.initial=await page.evaluate(()=>window.__city.state);
 await frame('stonecutters-day-1440x1000',[-3320,660,-3030],[-4200,100,-4210]);
 await frame('stonecutters-northwest-landing-1440x1000',[-5150,300,-4180],[-4670,60,-4600]);
 await frame('stonecutters-southeast-landing-1440x1000',[-3320,280,-4130],[-3720,60,-3810]);
 await frame('stonecutters-under-span-1440x1000',[-3950,24,-4490],[-4200,65,-4210]);
 report.ground=await page.evaluate(()=>{const {sampler,terrain,THREE}=window.__bridgeCluster;terrain.updateMatrixWorld(true);return Array.from({length:11},(_,i)=>{const x=-4670+i*95,z=-4600+i*79,hit=new THREE.Raycaster(new THREE.Vector3(x,400,z),new THREE.Vector3(0,-1,0)).intersectObject(terrain,true)[0];return {world:[x,z],sampled:sampler.height(x,z),rendered:hit?.point.y,mappedWater:sampler.mappedWater(x,z)};});});
 report.groundBasis='Retained OSM motorway centreline context, not surveyed pier or shoreline samples; baseline diagnostic only.';

 if(phase==='after'){
  await frame(null,[-3320,660,-3030],[-4200,100,-4210]);
  report.sourceIntegration=await page.evaluate(expected=>{
   const {bridgeLayer:layer,stream,cableLayer}=window.__bridgeCluster,rendered=new Map();
   for(const g of layer.cache.values())for(const m of g.userData.deckMeshes)for(const i of m.geometry.attributes.bridgeFeature.array){const id=layer.features[i].id;rendered.set(id,(rendered.get(id)||0)+1);}
   return {models:expected.models.map(e=>{const m=layer.records.get(e.id);if(!m)throw Error('Missing original model '+e.id);return {id:m.id,triangles:m.modelGeometry.position.length/9,renderedTriangles:(rendered.get(m.id)||0)/3,worldBounds:m.worldBounds,walkable:m.walkable,walkTriangles:m.walkTriangleIndices.length,proxies:m.suppresses.map(id=>({id,layer:layer.suppressedIds.has(id),roads:stream.bridgeRoadIds.has(id)})),buildingUids:m.suppressesBuildingUids.map(uid=>{const entry=[...stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid)),index=entry?.data.buildings.findIndex(b=>b.uid===uid);return {uid,sourceRetained:!!entry,layer:layer.suppressedBuildingUids.has(uid),stream:stream.infrastructureBuildingUids.has(uid),renderedVertices:entry?.buildings.group.children.reduce((n,m)=>n+Array.from(m.geometry.attributes.feature.array).filter(i=>i===index).length,0)};})};}),clips:expected.clips.map(c=>({id:c.id,layer:layer.proxyClips.get(c.id),stream:stream.infrastructureRoadClips.get(c.id),fullySuppressed:stream.bridgeRoadIds.has(c.id)})),cables:[...cableLayer.records.values()].filter(r=>r.region==='stonecutters').map(r=>({id:r.id,sourceTriangles:r.sourceTriangles,triangles:r.illustrativeTriangles,estimatedGeometry:r.estimatedGeometry,visible:cableLayer.pickMeshes().some(m=>m.userData.cableId===r.id)}))};
  },expected);
  assert.ok(report.sourceIntegration.models.length>=3,'Original deck and two separate towers required');
  for(const [i,m]of report.sourceIntegration.models.entries()){const e=expected.models[i];assert.equal(m.triangles,e.triangles);assert.equal(m.renderedTriangles,e.triangles,'Source renders exactly once: '+m.id);assert.deepEqual(m.worldBounds,e.worldBounds);assert.equal(m.walkable,false);assert.equal(m.walkTriangles,0);assert.ok(m.proxies.every(p=>p.layer&&p.roads));assert.ok(m.buildingUids.every(b=>b.sourceRetained&&b.layer&&b.stream&&b.renderedVertices===0));}
  for(const [i,c]of report.sourceIntegration.clips.entries()){assert.deepEqual(c.layer.keepPaths,expected.clips[i].keepPaths);assert.deepEqual(c.stream.keepPaths,expected.clips[i].keepPaths);assert.equal(c.fullySuppressed,false);}
  for(const c of report.sourceIntegration.cables){assert.equal(c.sourceTriangles,0);assert.equal(c.estimatedGeometry,true);assert.equal(c.visible,true);}
  report.sourcePicking=[];
  for(const m of expected.models)report.sourcePicking.push(await clickGeometry(m.id));
  report.cablePicking=[];for(const c of report.sourceIntegration.cables)report.cablePicking.push(await clickGeometry(c.id,true));
  report.checks.push('Each original source model renders once, exact source identities replace proxies, retained source records remain, actual mouse picking shows source cards, and cables are separately labelled');
  for(const g of report.ground.slice(2,8)){assert.equal(g.mappedWater,true);assert.equal(g.sampled,-4);assert.ok(Math.abs(g.rendered+4)<.01);}
  report.foundations=await page.evaluate(()=>{const {sampler,terrain,THREE}=window.__bridgeCluster;return [[-4634.028,-4573.747],[-3849.81,-3924.645]].map(([x,z])=>{const hit=new THREE.Raycaster(new THREE.Vector3(x,400,z),new THREE.Vector3(0,-1,0)).intersectObject(terrain,true)[0];return {world:[x,z],mappedWater:sampler.mappedWater(x,z),sampled:sampler.height(x,z),rendered:hit?.point.y};});});
  for(const f of report.foundations){assert.equal(f.mappedWater,false);assert.ok(f.rendered>0&&f.rendered<12);assert.ok(Math.abs(f.rendered-f.sampled)<.02);}
  report.checks.push('Six actual terrain rays under the central span reach the illustrative submerged bed; both original tower centres remain on low port land');
  await page.locator('[data-mode="fly"]').click();await page.waitForFunction(()=>window.__city.state.mode==='fly'&&!window.__city.state.pendingModeRequest,null,{timeout:90000});
  await page.evaluate(async()=>{const {nav,stream}=window.__bridgeCluster;await nav.setAircraft('prop');await stream.arrive(-4241.9,-4249.2,3200);nav.position.set(-4165.5,35,-4341.6);nav.heading=Math.atan2(-.637,-.77);nav.pitch=0;nav.speed=62;nav.keys.clear();});
  report.flight=await page.evaluate(async()=>{const {nav}=window.__bridgeCluster,start=nav.position.toArray(),samples=[];for(let i=0;i<220;i++){await new Promise(requestAnimationFrame);if(i%5===0)samples.push({position:nav.position.toArray(),collision:!!nav.collides(nav.position.x,nav.position.z,nav.position.y-nav.aircraftEnvelope.bottom,nav.position.y+nav.aircraftEnvelope.top,nav.aircraftEnvelope.radius)});}return {start,end:nav.position.toArray(),samples};});
  const along=p=>(p[0]+4241.9)*(-.637)+(p[2]+4249.2)*.77;
  assert.ok(along(report.flight.start)<-90);assert.ok(along(report.flight.end)>60,'Actual flight must cross the span');assert.ok(report.flight.samples.every(s=>!s.collision&&s.position[1]<50));
  await capture('stonecutters-flight-under-span-1440x1000');await page.locator('[data-mode="orbit"]').click();report.checks.push('Real Fly-button entry and frame-driven flight cross below the bridge without terrain climb or collision');
 }
 await frame('stonecutters-night-1440x1000',[-3320,660,-3030],[-4200,100,-4210],'22:00');
 report.desktopPerformance=await measure();
 await page.setViewportSize({width:390,height:844});await frame('stonecutters-mobile-390x844',[-2940,980,-2510],[-4200,100,-4210]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.setViewportSize({width:320,height:844});await frame('stonecutters-mobile-320x844',[-2940,980,-2510],[-4200,100,-4210]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 report.mobilePerformance=await measure();report.checks.push('Baseline day, night, both landings, under-span and mobile views; sampled/rendered centreline terrain and frame times recorded. No reconstruction acceptance claimed.');
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.failures,[]);report.result='passed';await rm(new URL('failure.png',output),{force:true});console.log(JSON.stringify({phase,result:report.result,checks:report.checks,views:report.views.length,desktop:report.desktopPerformance,mobile:report.mobilePerformance},null,2));
}catch(error){report.result='failed';report.error=error.stack;await page.screenshot({path:new URL('failure.png',output).pathname}).catch(()=>{});throw error;}
finally{report.finished=new Date().toISOString();await writeFile(new URL('verification.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
