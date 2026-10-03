// HKS-167: actual city streaming, source-model picking, collision and local timing.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const output=fileURLToPath(new URL('../../../docs/astra-city/mui-wo-buildings/extension/browser/',import.meta.url));await mkdir(output,{recursive:true});
const baseline=JSON.parse(await readFile(new URL('../../../docs/astra-city/landsd-territory/browser/verification.json',import.meta.url))).visits.find(v=>v.id==='muiwo');
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),report={startedAt:new Date().toISOString(),baselineCommit:'ff68cf1',baseline,visits:[],errors:[],failures:[]};
page.on('pageerror',e=>report.errors.push(e.message));page.on('response',r=>{if(r.url().includes('/city/data/tiles/')&&r.status()>=400)report.failures.push({url:r.url(),status:r.status()});});
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending;},null,{timeout:180000});
const state=()=>page.evaluate(()=>window.__city.state);
const measure=()=>page.evaluate(async()=>{const samples=[];let prior=performance.now();for(let n=0;n<200;n++){await new Promise(requestAnimationFrame);const now=performance.now();if(n>=20)samples.push(now-prior);prior=now;}samples.sort((a,b)=>a-b);return {samples:samples.length,medianFrameMs:samples[90],p95FrameMs:samples[171],render:window.__city.state.render};});
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__modelReview",{get:()=>({stream,camera,controls,sampler,renderer,bridgeLayer,THREE})});\n'});});
 const started=performance.now();await page.goto('http://127.0.0.1:4176/city.html?district=muiwo');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden'});await settle();report.settledMs=performance.now()-started;
 await page.locator('[data-panel="time"]').click();await page.locator('#time').fill('15:00');await page.locator('[data-panel="places"]').click();
 report.waterMask=await page.evaluate(()=>({bayRaw:window.__modelReview.sampler.raw(-16000,2350)}));assert.ok(report.waterMask.bayRaw<=0,'Silvermine Bay remains water after source TIN blending');
 report.overview=await state();assert.deepEqual(report.overview.camera,baseline.overview.camera,'Same camera as the verified ff68cf1 Mui Wo baseline');assert.deepEqual(report.overview.counts.buildings,346115);
 await page.screenshot({path:output+'muiwo-overview-1440x1000.png'});report.performance=await measure();
 report.geometry=await page.evaluate(()=>{const {stream}=window.__modelReview,rows=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings),models=rows.filter(b=>b.modelGeometry);return {loadedTiles:stream.stats.loaded,cached:stream.stats.cached,loadedModels:new Set(models.map(b=>b.uid)).size,modelTriangles:models.reduce((n,b)=>n+b.modelGeometry.position.length/9,0),modelsPerSourceTile:Object.fromEntries([...new Set(models.map(b=>b.modelGeometry.sourceTile||'10-SW-12C'))].map(tile=>[tile,models.filter(b=>(b.modelGeometry.sourceTile||'10-SW-12C')===tile).length]))};});assert.equal(report.geometry.loadedModels,1327);
 const locations=[['waterfront',[-16540,2297],'10-SW-17B'],['wang-tong',[-16779,1694],'10-SW-12D'],['tai-tei-tong',[-17440,2185],'10-SW-17A'],['luk-tei-tong',[-17356,2710],'10-SW-17C'],['southern-villages',[-17000,2880],'10-SW-17D'],['ferry-pier',[-16224,2460],'10-SW-18A']];
 for(const [id,centre,tile] of locations){
  const visit={id,centre,tile};report.visits.push(visit);
  visit.source=await page.evaluate(({centre,tile})=>{
   const {stream,camera,controls,sampler,THREE}=window.__modelReview,all=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings),candidates=all.filter(b=>b.modelGeometry?.sourceTile===tile&&!['Open-sided Structure'].includes(b.structureType)).sort((a,b)=>Math.hypot(a.centre[0]-centre[0],a.centre[1]-centre[1])-Math.hypot(b.centre[0]-centre[0],b.centre[1]-centre[1]));
   for(const b of candidates.slice(0,30)){
    const bounds=b.modelGeometry.worldBounds,[x,z]=b.centre,top=bounds[1][1],span=Math.max(bounds[1][0]-bounds[0][0],bounds[1][2]-bounds[0][2],20),distance=Math.max(75,span*1.8);
    camera.position.set(x+distance,top+distance*.6,z+distance);controls.target.set(x,(top+bounds[0][1])/2,z);controls.update();camera.updateMatrixWorld();
    const ray=new THREE.Raycaster(),points=[b.centre,...b.rings[0].map(p=>[p[0]*.6+x*.4,p[1]*.6+z*.4])];
    for(const [px,pz] of points){const p=new THREE.Vector3(px,top,pz).project(camera);if(Math.abs(p.x)>.65||Math.abs(p.y)>.65)continue;ray.setFromCamera(new THREE.Vector2(p.x,p.y),camera);const hit=ray.intersectObjects(stream.pickMeshes(ray.ray),false)[0];if(!hit||stream.featureAt(hit)?.uid!==b.uid)continue;
     return {uid:b.uid,id:b.id,name:b.name,buildingCSUID:b.buildingCSUID,modelId:b.modelGeometry.modelId,modelBounds:bounds,outlineBase:b.baseHeightHKPD,outlineTop:b.topHeightHKPD,ground:sampler.height(x,z),centre:b.centre,sourceTile:b.modelGeometry.sourceTile,triangles:b.modelGeometry.position.length/9,blocked:!!stream.collision(px,pz,top-.15,top+.15,.2),click:{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2}};
    }
   }throw Error('No selectable detailed model in '+tile);
  },{centre,tile});
  await page.waitForTimeout(250);await page.mouse.click(visit.source.click.x,visit.source.click.y);await page.waitForFunction(uid=>window.__city.state.selectedId===uid,visit.source.uid,{timeout:15000});
  visit.card=await page.locator('#building-card').innerText();visit.href=await page.locator('#building-osm').getAttribute('href');assert.match(visit.card,/Official Lands Department non-textured 3D roof geometry/);assert.equal(await page.locator('#building-height-label').textContent(),'OUTLINE HEIGHT');assert.equal(visit.source.blocked,true);assert.equal(new URL(visit.href).hostname,'portal.csdi.gov.hk');
  await page.screenshot({path:output+id+'-source-card-1440x1000.png'});visit.performance=await measure();visit.result='passed';await page.locator('#selection-close').click();
 }
 // Real user flow: return to the existing public arrival, then walk with collisions.
 await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="muiwo"]').click();await settle();await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:90000});const start=await state();assert.equal(start.collision,false);let moved=false;
 for(const key of ['w','d','s','a']){await page.keyboard.down(key);try{await page.waitForFunction(d=>window.__city.state.distance>d+2,start.distance,{timeout:4500});moved=true;}catch{}finally{await page.keyboard.up(key);}if(moved)break;}
 report.walk={start:start.position,end:(await state()).position,distance:(await state()).distance-start.distance,collision:(await state()).collision};assert.ok(moved);assert.equal(report.walk.collision,false);await page.keyboard.press('Escape');
 report.result='passed';assert.deepEqual(report.errors,[]);assert.deepEqual(report.failures,[]);console.log(JSON.stringify({result:report.result,geometry:report.geometry,performance:report.performance,visits:report.visits.map(v=>({id:v.id,uid:v.source.uid,result:v.result})),walk:report.walk},null,2));
}catch(error){report.result='failed';report.error=error.stack;await page.screenshot({path:output+'failure-1440x1000.png'}).catch(()=>{});throw error;}finally{report.finishedAt=new Date().toISOString();await writeFile(output+'verification.json',JSON.stringify(report,null,2)+'\n');await browser.close();}
