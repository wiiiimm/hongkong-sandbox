// HKS-170 uses the same city UI/streaming/picking probes as the Mui Wo review.
import {chromium} from 'playwright';import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const phase=process.argv[2]||'after';assert.ok(['before','after'].includes(phase));
const output=fileURLToPath(new URL('../../../docs/astra-city/tai-o-models/browser/',import.meta.url));await mkdir(output,{recursive:true});
const raw=await readFile(new URL('../data/manifest.json',import.meta.url)),manifest=JSON.parse(raw);
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),report={phase,startedAt:new Date().toISOString(),manifestSha256:createHash('sha256').update(raw).digest('hex'),officialCoverage:manifest.officialCoverage,views:[],selections:[],errors:[],failed:[]};
page.on('pageerror',e=>report.errors.push(e.message));page.on('response',r=>{if(r.url().includes('/city/data/tiles/')&&r.status()>=400)report.failed.push({url:r.url(),status:r.status()});});
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending;},null,{timeout:120000});
const measure=()=>page.evaluate(async()=>{const frames=[];let prior=performance.now();for(let n=0;n<140;n++){await new Promise(requestAnimationFrame);const now=performance.now();if(n>=20)frames.push(now-prior);prior=now;}frames.sort((a,b)=>a-b);return {samples:frames.length,medianFrameMs:frames[60],p95FrameMs:frames[114],render:window.__city.state.render};});
const setTime=async t=>{await page.locator('[data-panel="time"]').click();await page.locator('#time').fill(t);await page.locator('[data-panel="places"]').click();await page.waitForTimeout(200);};
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__taiOReview",{get:()=>({stream,camera,controls,sampler,renderer,THREE})});\n'});});
 await page.goto('http://127.0.0.1:4176/city.html?district=taio');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 report.start=await page.evaluate(()=>window.__city.state);assert.equal(report.start.counts.buildings,346115);
 report.models=await page.evaluate(()=>[...window.__taiOReview.stream.cache.entries.values()].flatMap(e=>e.data.buildings).filter(b=>b.modelGeometry).length);assert.equal(report.models,phase==='after'?532:0);
 for(const frame of ['overview','village']){
  if(frame==='village')await page.evaluate(()=>{const {camera,controls}=window.__taiOReview;camera.position.set(-30805,180,3815);controls.target.set(-30625,5,3605);controls.update();camera.updateMatrixWorld();});
  for(const t of ['15:00','22:00']){await setTime(t);const view={frame,time:t,state:await page.evaluate(()=>window.__city.state),performance:await measure()};report.views.push(view);await page.screenshot({path:output+phase+'-'+frame+'-'+t.replace(':','')+'-1440x1000.png'});}
 }
 if(phase==='after'){
  await setTime('15:00');
  for(const tile of ['9-SW-23A','9-SW-23B']){
   const source=await page.evaluate(tile=>{
    const {stream,camera,controls,sampler,THREE}=window.__taiOReview,rows=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings),candidates=rows.filter(b=>b.modelGeometry?.sourceTile===tile&&b.structureType!=='Open-sided Structure').sort((a,b)=>Math.hypot(a.centre[0]+30625,a.centre[1]-3605)-Math.hypot(b.centre[0]+30625,b.centre[1]-3605));
    for(const b of candidates.slice(0,40)){
     const [low,high]=b.modelGeometry.worldBounds,[x,z]=b.centre,top=high[1],distance=Math.max(65,(high[0]-low[0])*1.7,(high[2]-low[2])*1.7);camera.position.set(x+distance,top+distance*.7,z+distance);controls.target.set(x,(low[1]+top)/2,z);controls.update();camera.updateMatrixWorld();
     const points=[b.centre,...b.rings[0].map(p=>[p[0]*.6+x*.4,p[1]*.6+z*.4])],ray=new THREE.Raycaster();
     for(const [px,pz] of points){const p=new THREE.Vector3(px,top,pz).project(camera);if(Math.abs(p.x)>.65||Math.abs(p.y)>.65)continue;ray.setFromCamera(new THREE.Vector2(p.x,p.y),camera);const hit=ray.intersectObjects(stream.pickMeshes(ray.ray),false)[0];if(!hit||stream.featureAt(hit)?.uid!==b.uid)continue;
      return {uid:b.uid,modelId:b.modelGeometry.modelId,sourceTile:tile,name:b.name,bounds:b.modelGeometry.worldBounds,sourceBase:b.baseHeightHKPD,sourceTop:b.topHeightHKPD,ground:sampler.height(x,z),blocked:!!stream.collision(px,pz,top-.15,top+.15,.2),click:{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2}};
     }
    }throw Error('No selectable source roof in '+tile);
   },tile);
   await page.waitForTimeout(200);await page.mouse.click(source.click.x,source.click.y);await page.waitForFunction(uid=>window.__city.state.selectedId===uid,source.uid);source.card=await page.locator('#building-card').innerText();source.href=await page.locator('#building-osm').getAttribute('href');assert.match(source.card,/Official Lands Department non-textured 3D roof geometry/);assert.equal(source.blocked,true);assert.equal(await page.locator('#building-height-label').textContent(),'OUTLINE HEIGHT');report.selections.push(source);await page.screenshot({path:output+phase+'-'+tile+'-source-card-1440x1000.png'});await page.locator('#selection-close').click();
  }
  await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="taio"]').click();await settle();await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady);const start=await page.evaluate(()=>window.__city.state);assert.equal(start.collision,false);let moved=false;
  for(const key of ['w','d','s','a']){await page.keyboard.down(key);try{await page.waitForFunction(d=>window.__city.state.distance>d+2,start.distance,{timeout:4500});moved=true;}catch{}finally{await page.keyboard.up(key);}if(moved)break;}
  const end=await page.evaluate(()=>window.__city.state);report.walk={start:start.position,end:end.position,distance:end.distance-start.distance,collision:end.collision};assert.ok(moved);assert.equal(end.collision,false);
 }
 if(phase==='after'){
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:4176/city.html?district=taio');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
  await page.locator('#panel-toggle').click();await setTime('15:00');await page.locator('#panel-toggle').click();
  report.mobile={viewport:{width:390,height:844},time:'15:00',state:await page.evaluate(()=>window.__city.state),performance:await measure()};
  await page.screenshot({path:output+'after-mobile-1500-390x844.png'});
 }
 report.result='passed';assert.deepEqual(report.errors,[]);assert.deepEqual(report.failed,[]);console.log(JSON.stringify({phase,result:report.result,models:report.models,views:report.views.map(v=>({frame:v.frame,time:v.time,performance:v.performance})),selections:report.selections.map(s=>({uid:s.uid,tile:s.sourceTile})),walk:report.walk},null,2));
}catch(error){report.result='failed';report.error=error.stack;await page.screenshot({path:output+phase+'-failure.png'}).catch(()=>{});throw error;}finally{report.finishedAt=new Date().toISOString();await writeFile(output+phase+'-verification.json',JSON.stringify(report,null,2)+'\n');await browser.close();}
