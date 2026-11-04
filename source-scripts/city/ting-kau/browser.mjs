/** Real-city before/after acceptance. Run only after reserving the shared GPU slot. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const root=new URL('../../../',import.meta.url),phase=process.argv[2],resume=process.argv.includes('--resume-flight');
assert.ok(['before','after'].includes(phase),'Usage: node source-scripts/city/ting-kau/browser.mjs before|after');
const require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const output=new URL(`docs/astra-city/ting-kau/browser/${phase}/`,root);await mkdir(output,{recursive:true});
const read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const hash=async p=>createHash('sha256').update(await readFile(new URL(p,root))).digest('hex');
const packages=await Promise.all(['tsing-ma','ting-kau'].map(region=>read(`source-scripts/city/${region}/bridges-${region}.json`)));
const cables=await Promise.all(['tsing-ma','ting-kau'].map(region=>read(`source-scripts/city/${region}/cables-${region}.json`)));
const expected={models:packages.flatMap(p=>p.models.map(m=>({id:m.id,region:p.region,triangles:m.modelGeometry.triangles,worldBounds:m.worldBounds,buildingUids:m.suppressesBuildingUids,proxies:m.suppresses}))),clips:packages.flatMap(p=>p.proxyClips||[]),cables:cables.map(p=>({id:p.id,region:p.region,triangles:p.counts.illustrativeTriangles}))};
const report={phase,started:new Date().toISOString(),commit:execFileSync('git',['rev-parse','HEAD'],{cwd:root}).toString().trim(),manifestSha256:await hash('3d-viewer/city/data/manifest.json'),terrainSha256:await hash('3d-viewer/city/data/terrain.json'),checks:[],views:[],errors:[],failures:[]};
if(resume){assert.equal(phase,'after');const checkpoint=JSON.parse(await readFile(new URL('checkpoint.json',output),'utf8'));assert.equal(checkpoint.manifestSha256,report.manifestSha256,'Source manifest changed; cannot reuse checkpoint');const resumedAt=report.started;Object.assign(report,checkpoint,{resumedAt,resumedFrom:'Validated source, picking, ground and suppression checkpoint; remaining navigation/mobile checks in a fresh browser.'});}
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
async function verifyRegionRendering(region){
 const rows=await page.evaluate(ids=>{const layer=window.__bridgeCluster.bridgeLayer,counts=new Map();for(const g of layer.cache.values())for(const mesh of g.userData.deckMeshes)for(const feature of mesh.geometry.attributes.bridgeFeature.array){const id=layer.features[feature].id;if(ids.includes(id))counts.set(id,(counts.get(id)||0)+1);}return ids.map(id=>({id,triangles:(counts.get(id)||0)/3}));},expected.models.filter(m=>m.region===region).map(m=>m.id));
 for(const row of rows)assert.equal(row.triangles,expected.models.find(m=>m.id===row.id).triangles,'Every source component must render once in its region: '+row.id);
 (report.regionalRendering??=[]).push({region,models:rows});
}
async function measure(){await page.emulateMedia({reducedMotion:'no-preference'});return page.evaluate(async()=>{const frames=[];let last;for(let i=0;i<180;i++){const now=await new Promise(requestAnimationFrame);if(i>20)frames.push(now-last);last=now;}frames.sort((a,b)=>a-b);return {frames:frames.length,medianFrameMs:frames[Math.floor(frames.length*.5)],p95FrameMs:frames[Math.floor(frames.length*.95)],render:window.__city.state.render};});}
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__bridgeCluster",{get:()=>({stream,camera,controls,sampler,renderer,THREE,nav,bridgeLayer,terrain,water,environment,cableLayer:typeof cableLayer===\"undefined\"?null:cableLayer})});\n'});});
 await page.goto(process.env.CITY_URL||'http://127.0.0.1:4176/city.html?district=mawan');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 await tab('weather');await page.locator('#weather-mode').selectOption('manual');
 for(const id of ['weather-rain','weather-clouds','weather-fog','weather-wind','weather-waves','weather-snow'])await page.locator('#'+id).evaluate(e=>{e.value='0';e.dispatchEvent(new Event('input',{bubbles:true}));});
 await page.locator('#atmospheric-haze').evaluate(e=>{e.value='35';e.dispatchEvent(new Event('input',{bubbles:true}));});
 await tab('time');await page.locator('#sky-date').fill('2026-09-07');await page.locator('#sky-date').dispatchEvent('change');await tab('weather');
 await page.locator('#tide-level').evaluate(e=>{e.value='.3';e.dispatchEvent(new Event('input',{bubbles:true}));});await closePanel();
 report.initial=await page.evaluate(()=>window.__city.state);
 if(!resume){await frame('tsing-ma-day-1440x1000',[-9140,520,-5840],[-8950,85,-7040]);
 await frame('tsing-ma-under-span-1440x1000',[-9000,22,-6840],[-9000,46,-7100]);
 await frame('tsing-ma-foundation-island-1440x1000',[-9820,195,-6600],[-9485,8,-6860]);
 await frame('ting-kau-day-1440x1000',[-7080,435,-8480],[-8250,95,-8480]);
 await frame('ting-kau-under-span-1440x1000',[-8040,20,-8550],[-8370,50,-8500]);
 await frame('ting-kau-foundation-island-1440x1000',[-8000,140,-8640],[-8230,7,-8485]);
 }
 if(phase==='after'){
  if(!resume){report.sourceIntegration=await page.evaluate(expected=>{
   const {bridgeLayer:layer,cableLayer,stream}=window.__bridgeCluster;if(!cableLayer)throw Error('Illustrative cable adapter not integrated');
   const rendered=new Map();for(const g of layer.cache.values())for(const m of g.userData.deckMeshes)for(const i of m.geometry.attributes.bridgeFeature.array){const id=layer.features[i].id;rendered.set(id,(rendered.get(id)||0)+1);}
   const models=expected.models.map(w=>{const m=layer.records.get(w.id);if(!m)throw Error('Missing source model '+w.id);return {id:w.id,triangles:m.modelGeometry.position.length/9,renderedTriangles:(rendered.get(w.id)||0)/3,worldBounds:m.worldBounds,walkable:m.walkable,walkTriangles:m.walkTriangleIndices.length,buildingUids:m.suppressesBuildingUids.map(uid=>({uid,layer:layer.suppressedBuildingUids.has(uid),stream:stream.infrastructureBuildingUids.has(uid)})),proxies:m.suppresses.map(id=>({id,layer:layer.suppressedIds.has(id),roads:stream.bridgeRoadIds.has(id)}))};});
   const clips=expected.clips.map(w=>({id:w.id,layer:layer.proxyClips.get(w.id),stream:stream.infrastructureRoadClips.get(w.id),fullySuppressed:stream.bridgeRoadIds.has(w.id)}));
   const estimated=expected.cables.map(w=>{const m=cableLayer.records.get(w.id);return {id:w.id,exists:!!m,visible:cableLayer.pickMeshes().some(mesh=>mesh.userData.cableId===w.id),triangles:m?.illustrativeTriangles,sourceTriangles:m?.sourceTriangles,estimatedGeometry:m?.estimatedGeometry,walkable:m?.walkable};});
   return {models,clips,cables:estimated,bridgeStats:layer.stats,cableStats:cableLayer.stats,cableErrors:[...cableLayer.errors]};
  },expected);
  assert.equal(report.sourceIntegration.models.length,7);
  for(const [i,m]of report.sourceIntegration.models.entries()){const e=expected.models[i];assert.equal(m.triangles,e.triangles);assert.ok(m.renderedTriangles===0||m.renderedTriangles===e.triangles,'Source geometry must never duplicate: '+m.id);assert.deepEqual(m.worldBounds,e.worldBounds);assert.equal(m.walkable,false);assert.equal(m.walkTriangles,0);assert.ok(m.buildingUids.every(r=>r.layer&&r.stream));assert.ok(m.proxies.every(r=>r.layer&&r.roads));}
  for(const [i,c]of report.sourceIntegration.clips.entries()){assert.deepEqual(c.layer.keepPaths,expected.clips[i].keepPaths);assert.deepEqual(c.stream.keepPaths,expected.clips[i].keepPaths);assert.equal(c.fullySuppressed,false);}
  for(const [i,c]of report.sourceIntegration.cables.entries()){assert.equal(c.exists,true);assert.equal(c.visible,true);assert.equal(c.triangles,expected.cables[i].triangles);assert.equal(c.sourceTriangles,0);assert.equal(c.estimatedGeometry,true);assert.equal(c.walkable,false);}
  report.checks.push('Seven original models render once; seven tower footprint UIDs and 21 fully covered OSM proxies suppressed; two original Tsing Yi tails retained; both cable packets remain separately labelled estimates');
  report.sourcePicking=[];await frame(null,[-9140,520,-5840],[-8950,85,-7040]);await verifyRegionRendering('tsing-ma');report.sourcePicking.push(await clickGeometry('landsd-infrastructure/I254702348107063C0'));
  report.cablePicking=[await clickGeometry(expected.cables[0].id,true)];await frame(null,[-7080,435,-8480],[-8250,95,-8480]);await verifyRegionRendering('ting-kau');report.sourcePicking.push(await clickGeometry('landsd-infrastructure/I259872443407063C0'));report.cablePicking.push(await clickGeometry(expected.cables[1].id,true));
  report.checks.push('Actual mouse clicks pick both source bridges and both illustrative cable layers with distinct source cards');
  report.ground=await page.evaluate(()=>{
   const {sampler,terrain,THREE,nav,bridgeLayer}=window.__bridgeCluster;terrain.updateMatrixWorld(true);
   const marine=[[-9250,-6940],[-9000,-7010],[-8750,-7090],[-8500,-7160],[-8250,-7240],[-8350.76,-8704.7],[-8300.76,-8604.7],[-8190.76,-8374.7],[-8150.76,-8294.7]].map(([x,z])=>{const ray=new THREE.Raycaster(new THREE.Vector3(x,400,z),new THREE.Vector3(0,-1,0)),hit=ray.intersectObject(terrain,true)[0];return {world:[x,z],mappedWater:sampler.mappedWater(x,z),sampledGround:sampler.height(x,z),renderedTerrainY:hit?.point.y,underSpanCollision:!!nav.collides(x,z,0,55,.55),walkFloors:nav.groundHeights(x,z)};});
   const foundations=[[-9500,-6860],[-8427.765,-8887.478],[-8229.83,-8485.528],[-8019.633,-8059.256]].map(([x,z])=>({world:[x,z],mappedWater:sampler.mappedWater(x,z),ground:sampler.height(x,z)}));
   const formerSpikes=[[-9407.5,-6862.5,2.17],[-8262.5,-8497.5,7.12],[-8042.5,-8042.5,6.4]].map(([x,z,expected])=>{const ray=new THREE.Raycaster(new THREE.Vector3(x,200,z),new THREE.Vector3(0,-1,0));const hit=ray.intersectObject(terrain,true)[0];return {world:[x,z],expectedHKPD:expected,sampled:sampler.height(x,z),rendered:hit?.point.y,mappedWater:sampler.mappedWater(x,z)};});
   return {marine,foundations,formerSpikes,deckContact:nav.collides(-9000,-7010,76,78,.55)?.id||null,aboveDeckContact:!!nav.collides(-9000,-7010,80,82,.55),sourceFloors:bridgeLayer.surfaces.heights(-9000,-7010)};
  });
  for(const m of report.ground.marine){assert.equal(m.mappedWater,true);assert.equal(m.sampledGround,-4);assert.ok(Math.abs(m.renderedTerrainY+4)<.01,'Visible terrain must agree with mapped water');assert.equal(m.underSpanCollision,false);assert.deepEqual(m.walkFloors,[]);}
  for(const s of report.ground.formerSpikes){assert.equal(s.mappedWater,false);assert.ok(Math.abs(s.sampled-s.expectedHKPD)<.011);assert.ok(Math.abs(s.rendered-s.expectedHKPD)<.011,'Former foundation spike must be absent from actual terrain mesh');}
  for(const f of report.ground.foundations){assert.equal(f.mappedWater,false);assert.ok(f.ground>0);}
  assert.ok(report.ground.deckContact?.startsWith('landsd-infrastructure/'));assert.equal(report.ground.aboveDeckContact,false);assert.deepEqual(report.ground.sourceFloors,[]);
  report.checks.push('Nine actual rendered terrain rays reach the −4 m illustrative bed under both spans; all four sampled foundations remain land; source deck collision works without granting walking access');
  report.buildingSuppression=[];
  for(const region of ['tsing-ma','ting-kau']){
   if(region==='tsing-ma')await frame(null,[-9140,520,-5840],[-8950,85,-7040]);else await frame(null,[-7080,435,-8480],[-8250,95,-8480]);
   const uids=expected.models.filter(m=>m.region===region).flatMap(m=>m.buildingUids);
   const rows=await page.evaluate(uids=>{const {stream}=window.__bridgeCluster;return uids.map(uid=>{const entry=[...stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!entry)throw Error('Tower source record not loaded: '+uid);const index=entry.data.buildings.findIndex(b=>b.uid===uid);return {uid,sourceRecordRetained:true,excluded:entry.exclusions.has(uid),renderedVertices:entry.buildings.group.children.reduce((n,m)=>n+Array.from(m.geometry.attributes.feature.array).filter(i=>i===index).length,0)};});},uids);
   for(const r of rows){assert.equal(r.excluded,true);assert.equal(r.renderedVertices,0);}report.buildingSuppression.push(...rows);
  }
  await frame(null,[-9140,520,-5840],[-8950,85,-7040]);await tab('places');await page.locator('#layer-bridges').uncheck();await closePanel();assert.equal(await page.evaluate(()=>window.__bridgeCluster.bridgeLayer.pickMeshes().length+window.__bridgeCluster.cableLayer.pickMeshes().length),0);await capture('bridge-layer-hidden-1440x1000');await tab('places');await page.locator('#layer-bridges').check();await closePanel();
  await writeFile(new URL('checkpoint.json',output),JSON.stringify(report,null,2)+'\n');}
  await frame(null,[-9140,520,-5840],[-8950,85,-7040]);
  await page.locator('[data-mode="fly"]').click();
  await page.waitForFunction(()=>window.__city.state.mode==='fly'&&!window.__city.state.pendingModeRequest,null,{timeout:90000});
  await page.evaluate(async()=>{const {nav,stream}=window.__bridgeCluster;await nav.setAircraft('prop');nav.position.set(-9000,35,-6920);nav.heading=0;nav.pitch=0;nav.speed=62;nav.keys.clear();await Promise.race([stream.arrive(-9000,-6920,3200),new Promise((_,reject)=>setTimeout(()=>reject(Error('Flight test arrival timed out')),45000))]);nav.position.set(-9000,35,-6920);nav.heading=0;nav.pitch=0;nav.speed=62;nav.keys.clear();});
  report.flight=await page.evaluate(async()=>{const d=window.__bridgeCluster,start=d.nav.position.toArray(),samples=[];for(let i=0;i<160;i++){await new Promise(requestAnimationFrame);if(i%10===0)samples.push({position:d.nav.position.toArray(),collision:!!d.nav.collides(d.nav.position.x,d.nav.position.z,d.nav.position.y-d.nav.aircraftEnvelope.bottom,d.nav.position.y+d.nav.aircraftEnvelope.top,d.nav.aircraftEnvelope.radius)});}return {start,end:d.nav.position.toArray(),samples,aircraft:window.__city.state.aircraft};});
  report.flight.modeEntry='Real Fly button from the far-panned bridge camera; then an explicit under-span test position with normal frame-driven navigation. Pending mode arrival must complete without orbit replanning starvation.';assert.ok(report.flight.start[2]>-6950,'Flight evidence starts before the source span');assert.ok(report.flight.samples.some(s=>s.position[2]>-7000)&&report.flight.samples.some(s=>s.position[2]<-7020),'Recorded frames bracket the source-span crossing');assert.ok(report.flight.end[2]<-7040,'Flight must actually cross below Tsing Ma');assert.ok(report.flight.samples.every(s=>s.position[1]<50&&!s.collision));await capture('flight-under-source-span-1440x1000');await page.locator('[data-mode="orbit"]').click();report.checks.push('Real running navigation flies the light aircraft continuously beneath Tsing Ma without a false-land climb or bridge collision');
 }
 await frame('tsing-ma-night-1440x1000',[-9140,520,-5840],[-8950,85,-7040],'22:00');await frame('ting-kau-night-1440x1000',[-7080,435,-8480],[-8250,95,-8480],'22:00');
 report.desktopPerformance=await measure();await page.setViewportSize({width:390,height:844});await frame('ting-kau-mobile-390x844',[-6450,660,-8460],[-8250,95,-8480]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.setViewportSize({width:320,height:844});await frame('tsing-ma-mobile-320x844',[-9100,1050,-4800],[-8950,85,-7040]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);report.mobilePerformance=await measure();
 report.checks.push('Matched day/night source views, foundation and under-span views, 390/320 mobile layouts, recorded frame times');
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.failures,[]);report.result='passed';await rm(new URL('failure.png',output),{force:true});console.log(JSON.stringify({phase,result:report.result,checks:report.checks,views:report.views.length,desktop:report.desktopPerformance,mobile:report.mobilePerformance},null,2));
}catch(error){report.result='failed';report.error=error.stack;await page.screenshot({path:new URL('failure.png',output).pathname}).catch(()=>{});throw error;}
finally{report.finished=new Date().toISOString();await writeFile(new URL('verification.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
