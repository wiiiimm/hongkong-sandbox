// Bounded territory regression using the established regional/Mui Wo browser patterns.
// Camera framing exposes existing app objects only in this test response; travel,
// selection, layer changes, clock changes and movement use the actual city UI.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';
const output=fileURLToPath(new URL('../../../docs/astra-city/landsd-territory/browser/',import.meta.url));
await mkdir(output,{recursive:true});
const ids=['central','kowloon','taio','pengchau','cheungchau','shatin','yuenlong','muiwo'];
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),page=await context.newPage();
const report={startedAt:new Date().toISOString(),browser:await browser.version(),viewport:{width:1440,height:1000},visits:[],errors:[],failures:[],method:'One fresh browser context; existing city UI and rendered geometry. Local development server; read-only app getter for geometry probes and camera framing. Per-view 180 requestAnimationFrame intervals after a 20-frame warm-up. Not a production-network or cross-device benchmark.'};
const pending=new Map(),finished=[],cdp=await context.newCDPSession(page);
await cdp.send('Network.enable');
cdp.on('Network.requestWillBeSent',event=>pending.set(event.requestId,{url:event.request.url,started:event.timestamp}));
cdp.on('Network.responseReceived',event=>{const r=pending.get(event.requestId);if(r)Object.assign(r,{status:event.response.status,cache:event.response.fromDiskCache||event.response.fromServiceWorker||false,contentLength:Number(event.response.headers['Content-Length']||event.response.headers['content-length']||0)});});
cdp.on('Network.loadingFinished',event=>{const r=pending.get(event.requestId);if(r){finished.push({...r,encodedDataLength:event.encodedDataLength,durationMs:(event.timestamp-r.started)*1000});pending.delete(event.requestId);}});
page.on('pageerror',error=>report.errors.push(error.message));
page.on('console',message=>{if(message.type()==='error')report.errors.push(message.text());});
const state=()=>page.evaluate(()=>window.__city.state);
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending;},null,{timeout:180000});
const save=()=>writeFile(output+'verification.json',JSON.stringify(report,null,2)+'\n');
const capture=name=>page.screenshot({path:output+name+'.png'});
const tab=async name=>{if(!await page.locator('#explorer').isVisible())await page.locator('#panel-toggle').click();await page.locator(`[data-panel="${name}"]`).click();};
const choose=async id=>{if((await state()).mode!=='orbit')await page.keyboard.press('Escape');await tab('places');await page.locator(`[data-region="${PLACES[id].region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await settle();assert.equal((await state()).place,id);};
const time=async value=>{await tab('time');await page.locator('#time').fill(value);await page.waitForFunction(h=>window.__city.state.time===h,Number(value.slice(0,2))+Number(value.slice(3))/60);await tab('places');await page.waitForTimeout(250);};
const network=from=>{const rows=finished.slice(from).filter(r=>r.url.startsWith('http://127.0.0.1:')||r.url.startsWith('http://localhost:'));return {requests:rows.length,encodedTransferBytes:rows.reduce((n,r)=>n+r.encodedDataLength,0),declaredBodyBytes:rows.reduce((n,r)=>n+r.contentLength,0),activityRequests:rows.filter(r=>/\/city\/data\/activity\//.test(r.url)).length,activityTransferBytes:rows.filter(r=>/\/city\/data\/activity\//.test(r.url)).reduce((n,r)=>n+r.encodedDataLength,0),cityTileRequests:rows.filter(r=>/\/city\/data\/tiles\//.test(r.url)).length,cityTileTransferBytes:rows.filter(r=>/\/city\/data\/tiles\//.test(r.url)).reduce((n,r)=>n+r.encodedDataLength,0)};};
const measure=()=>page.evaluate(async()=>{const frames=[];let previous=performance.now();for(let i=0;i<200;i++){await new Promise(requestAnimationFrame);const now=performance.now();if(i>=20)frames.push(now-previous);previous=now;}frames.sort((a,b)=>a-b);return {samples:frames.length,medianFrameMs:frames[Math.floor(frames.length*.5)],p95FrameMs:frames[Math.floor(frames.length*.95)],render:window.__city.state.render};});
const pixels=()=>page.evaluate(async()=>{const source=document.querySelector('#viewport canvas'),image=new Image();image.src=source.toDataURL();await image.decode();const canvas=document.createElement('canvas');canvas.width=source.width;canvas.height=source.height;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);const data=ctx.getImageData(0,0,canvas.width,canvas.height).data;let lit=0,total=0;for(let i=0;i<data.length;i+=4){const luminance=data[i]*.2126+data[i+1]*.7152+data[i+2]*.0722;total+=luminance;if(luminance>100)lit++;}return {litPixels:lit,meanLuminance:total/(data.length/4)};});
const frameSource=id=>page.evaluate(id=>{
 const {stream,camera,controls,sampler,bridgeLayer,THREE}=window.__territoryReview,place=window.__territoryReview.places[id];
 const all=[...stream.cache.entries.values()].filter(e=>e.buildings.group.visible).flatMap(e=>e.data.buildings);
 const candidates=all.filter(b=>b.id.startsWith('landsd/')&&b.heightSource==='landsd'&&b.height>3&&b.structureType==='Tower'&&b.base+b.height>sampler.height(...b.centre)+3).sort((a,b)=>Math.hypot(a.centre[0]-place.spawn[0],a.centre[1]-place.spawn[1])-Math.hypot(b.centre[0]-place.spawn[0],b.centre[1]-place.spawn[1]));
 if(id==='muiwo'){const market=all.find(b=>b.uid==='landsd/174478:0');if(market)candidates.unshift(market);}
 for(const b of candidates.slice(0,20)){
  const [x,z]=b.centre,top=b.base+b.height,xs=b.rings[0].map(p=>p[0]),zs=b.rings[0].map(p=>p[1]),span=Math.max(Math.max(...xs)-Math.min(...xs),Math.max(...zs)-Math.min(...zs),30),distance=Math.max(65,span*1.8);
  camera.position.set(x+distance,top+distance*.55,z+distance);controls.target.set(x,top-Math.min(b.height*.45,distance*.5),z);controls.update();camera.updateMatrixWorld();
  const ray=new THREE.Raycaster(),points=[b.centre,...b.rings[0].slice(0,-1).map(p=>[p[0]*.7+x*.3,p[1]*.7+z*.3])];
  for(const [px,pz] of points){const p=new THREE.Vector3(px,top,pz).project(camera);if(Math.abs(p.x)>.7||Math.abs(p.y)>.7)continue;ray.setFromCamera(new THREE.Vector2(p.x,p.y),camera);const buildingMeshes=stream.pickMeshes(ray.ray),bridgeMeshes=bridgeLayer.pickMeshes(),hit=ray.intersectObjects([...buildingMeshes,...bridgeMeshes],false)[0];if(!hit||bridgeMeshes.includes(hit.object)||stream.featureAt(hit)?.uid!==b.uid)continue;
   return {uid:b.uid,id:b.id,objectId:b.objectId,buildingCSUID:b.buildingCSUID,name:b.name,structureType:b.structureType,base:b.base,height:b.height,heightSource:b.heightSource,baseHeightHKPD:b.baseHeightHKPD,topHeightHKPD:b.topHeightHKPD,sourceUrl:b.sourceUrl,modelGeometry:!!b.modelGeometry,ground:sampler.height(x,z),centre:b.centre,click:{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2},volumeBlocked:!!stream.collision(px,pz,top-.15,top+.15,.2)};
  }
 }
 throw Error('No selectable recorded official roof near '+id);
},id);
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__territoryReview",{get:()=>({stream,camera,controls,sampler,scene,renderer,bridgeLayer,THREE,places:PLACES})});\n'});});
 const started=performance.now();await page.goto((process.env.CITY_URL||'http://127.0.0.1:4176/city.html')+'?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});report.readyMs=performance.now()-started;await page.locator('#loading').waitFor({state:'hidden'});await settle();
 report.startup={settledMs:performance.now()-started,network:network(0),state:await state()};report.graphics=await page.evaluate(()=>{const gl=window.__territoryReview.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return {renderer:gl.getParameter(ext?ext.UNMASKED_RENDERER_WEBGL:gl.RENDERER),vendor:gl.getParameter(ext?ext.UNMASKED_VENDOR_WEBGL:gl.VENDOR),drawingBuffer:[gl.drawingBufferWidth,gl.drawingBufferHeight]};});assert.ok(report.startup.state.counts.buildings>=342223,'Merged official territory coverage');assert.ok(report.startup.network.activityRequests>0,'Per-tile activity requested');assert.equal(finished.some(r=>new URL(r.url).pathname==='/city/data/activity.json'),false,'Global activity does not block startup');await time('15:00');
 for(const id of ids){
  const visit={id,title:PLACES[id].title},networkFrom=finished.length,started=performance.now();report.visits.push(visit);
  try{
   if(id!=='central')await choose(id);await time('15:00');const s=await state();visit.arrivalMs=performance.now()-started;visit.overview={stream:s.stream,regional:s.regional,bridges:s.bridges,render:s.render,camera:s.camera};
   assert.deepEqual(s.stream.errors,[]);assert.deepEqual(s.regional.errors,[]);assert.deepEqual(s.bridges.errors,[]);assert.ok(s.stream.cached<=30);assert.ok(s.regional.tiles<=24);assert.ok(s.bridges.tiles<=24);assert.ok(s.stream.forms>50);assert.ok(s.render.triangles>1000);
   visit.loaded=await page.evaluate(()=>{const {stream}=window.__territoryReview,rows=[...stream.cache.entries.values()].filter(e=>e.buildings.group.visible).flatMap(e=>e.data.buildings);return {official:rows.filter(b=>b.id.startsWith('landsd/')).length,sourceModels:rows.filter(b=>b.modelGeometry).length,types:Object.fromEntries([...new Set(rows.map(b=>b.structureType).filter(Boolean))].map(t=>[t,rows.filter(b=>b.structureType===t).length]))};});assert.ok(visit.loaded.official>20);
   await capture(id+'-overview-1440x1000');visit.performance=await measure();
   visit.source=await frameSource(id);await page.waitForTimeout(400);await page.mouse.click(visit.source.click.x,visit.source.click.y);await page.waitForFunction(uid=>window.__city.state.selectedId===uid,visit.source.uid,{timeout:10000});
   visit.source.card=await page.locator('#building-card').innerText();visit.source.href=await page.locator('#building-osm').getAttribute('href');const url=new URL(visit.source.href);assert.equal(url.hostname,'portal.csdi.gov.hk');assert.equal(Number(url.searchParams.get('objectIds')),visit.source.objectId);if(visit.source.heightSource==='landsd')assert.match(visit.source.card,/Hong Kong Principal Datum/);else assert.match(visit.source.card,/fallback|estimated/i);assert.equal(await page.locator('#building-height-label').textContent(),visit.source.modelGeometry?'OUTLINE HEIGHT':'HEIGHT');assert.equal(visit.source.volumeBlocked,true);
   if(['central','taio','muiwo'].includes(id))await capture(id+'-source-card-1440x1000');
   if(id==='central'||id==='muiwo'){const response=await page.request.get(visit.source.href,{timeout:45000});assert.ok(response.ok());const data=await response.json();assert.equal(data.features?.[0]?.attributes?.OBJECTID,visit.source.objectId);visit.source.governmentLookup={status:response.status(),objectId:data.features[0].attributes.OBJECTID,base:data.features[0].attributes.BaseHeight,top:data.features[0].attributes.TopHeight};assert.equal(data.features[0].attributes.BaseHeight,visit.source.baseHeightHKPD);assert.equal(data.features[0].attributes.TopHeight,visit.source.topHeightHKPD);}
   await page.locator('#selection-close').click();
   if(id==='central'){
    await page.locator('#layer-buildings').uncheck();assert.equal((await state()).layers.buildings,false);const pickCount=await page.evaluate(()=>{const {stream,camera,THREE}=window.__territoryReview,ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2(0,0),camera);return stream.pickMeshes(ray.ray).length;});assert.equal(pickCount,0);await page.mouse.click(visit.source.click.x,visit.source.click.y);assert.notEqual((await state()).selectedId,visit.source.uid);await page.locator('#layer-buildings').check();assert.equal((await state()).layers.buildings,true);visit.layerPicking='passed';
   }
   if(id==='kowloon'){
    visit.night={};for(const hour of ['21:00','04:00']){await time(hour);visit.night[hour]={pixels:await pixels(),lighting:(await state()).lighting};await capture(id+'-'+hour.replace(':','')+'-1440x1000');}
    assert.ok(visit.night['21:00'].pixels.litPixels>visit.night['04:00'].pixels.litPixels);assert.ok(visit.night['04:00'].pixels.litPixels>100);assert.ok(visit.night['04:00'].lighting.uniformActivity.every(n=>n>0));assert.equal(visit.night['04:00'].lighting.shimmer,0);await time('15:00');
   }
   await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:90000});const enter=await state();visit.walk={arrival:enter.position,collision:enter.collision,expectedSpawn:PLACES[id].spawn};assert.equal(enter.collision,false,'Clear official-building arrival at '+id);assert.ok(Math.hypot(enter.position[0]-PLACES[id].spawn[0],enter.position[2]-PLACES[id].spawn[1])<1);
   let moved=false;for(const key of ['w','d','s','a']){await page.keyboard.down(key);try{await page.waitForFunction(distance=>window.__city.state.distance>distance+2,enter.distance,{timeout:4500});moved=true;}catch{}finally{await page.keyboard.up(key);}if(moved)break;}
   const after=await state();visit.walk.distance=after.distance-enter.distance;visit.walk.end=after.position;assert.ok(moved,'At least 2 m collision-aware walking at '+id);assert.equal(after.collision,false);await page.keyboard.press('Escape');visit.result='passed';
  }catch(error){visit.result='failed';visit.failure=error.stack;report.failures.push({id,message:error.message});await capture(id+'-failure').catch(()=>{});console.error(id,error.message);}
  visit.network=network(networkFrom);await save();console.log(JSON.stringify({id,result:visit.result,forms:visit.overview?.stream.forms,official:visit.loaded?.official,performance:visit.performance,arrivalMs:visit.arrivalMs}));
 }
 await choose('pengchau');await page.setViewportSize({width:390,height:844});await page.waitForFunction(()=>document.querySelector('#viewport canvas').clientWidth===innerWidth);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await capture('peng-chau-mobile-390x844');await tab('places');await capture('peng-chau-mobile-panel-390x844');report.mobile='passed';
 report.network=network(0);report.finishedAt=new Date().toISOString();report.result=report.failures.length||report.errors.length?'failed':'passed';assert.deepEqual(report.errors,[]);assert.deepEqual(report.failures,[]);
}catch(error){report.result='failed';report.failure=error.stack;throw error;}finally{await save();await writeFile(output+'requests.json',JSON.stringify(finished,null,2)+'\n');await browser.close();}
