// HKS-170: inspect the actual rendered channel/bridge geometry and game Navigation.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
const geometryOnly=process.argv.includes('--geometry-only');
const output=new URL('../../../docs/astra-city/tai-o-completion/browser/',import.meta.url);await mkdir(output,{recursive:true});
const route=JSON.parse(await readFile(new URL('../../../docs/astra-city/tai-o-completion/route.json',import.meta.url)));
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true,reducedMotion:'reduce'});
const report={testedAt:new Date().toISOString(),views:[],checks:[],errors:[],failures:[]};
page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});page.on('response',r=>{if(r.url().includes('/city/data/')&&r.status()>=400)report.failures.push(r.url());});
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending;},null,{timeout:120000});
const tab=async name=>{if(!(await page.evaluate(()=>window.__city.state.controls.expanded)))await page.locator('#panel-toggle').click();await page.locator('#tab-'+name).click();};
async function frame(name,eye,target,time){
 await tab('time');await page.locator('#time').fill(time);await page.locator('#panel-toggle').click();
 await page.evaluate(({eye,target})=>{const {camera,controls}=window.__taiOCompletion;camera.position.fromArray(eye);controls.target.fromArray(target);controls.update();camera.updateMatrixWorld();},{eye,target});await page.waitForTimeout(800);
 const stats=await page.evaluate(async()=>{const frames=[];let before;for(let i=0;i<140;i++){const now=await new Promise(requestAnimationFrame);if(i>20)frames.push(now-before);before=now;}frames.sort((a,b)=>a-b);return {medianFrameMs:frames[Math.floor(frames.length*.5)],p95FrameMs:frames[Math.floor(frames.length*.95)],state:window.__city.state};});report.views.push({name,time,...stats});await page.screenshot({path:new URL(name+'.png',output).pathname});
}
try{
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__taiOCompletion",{get:()=>({stream,camera,controls,sampler,renderer,THREE,nav,bridgeLayer,terrain,water,environment})});\n'});});
 await page.goto('http://127.0.0.1:4176/city.html?district=taiopromenade');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 const sources=await page.evaluate(()=>{const {bridgeLayer,sampler,stream}=window.__taiOCompletion;return {stats:bridgeLayer.stats,models:[...bridgeLayer.surfaces.models.values()].map(m=>({id:m.id,triangles:m.modelGeometry.triangles,public:m.walkable})),renderedIds:[...bridgeLayer.cache.values()].flatMap(g=>g.userData.deckMeshes).flatMap(m=>[...new Set(m.geometry.attributes.bridgeFeature.array)].map(i=>bridgeLayer.features[i].id)),mappedWater:sampler.mappedWater(-30677,3677),raw:sampler.raw(-30677,3677),renderedHeight:sampler.height(-30677,3677),buildingModels:[...stream.cache.entries.values()].flatMap(e=>e.data.buildings).filter(b=>b.modelGeometry).length};});report.sources=sources;assert.equal(sources.stats.sourceModels,5);assert.equal(sources.stats.publicDecks,2);assert.equal(sources.stats.publicApproaches,2);assert.equal(sources.mappedWater,true);assert.equal(sources.renderedHeight,-4);assert.equal(sources.buildingModels,532);assert.equal(sources.renderedIds.filter(id=>id.startsWith('landsd-infrastructure/')).length,5);assert.equal(sources.renderedIds.includes('way/507688251'),false);assert.equal(sources.renderedIds.includes('way/244106712'),false);report.checks.push('Five original source infrastructure meshes render once; public deck faces enabled only for two verified bridges; mapped channel cuts reach water without removing buildings');
 await frame('comparison-village-1440x1000',[-30805,180,3815],[-30625,5,3605],'15:00');await frame('channels-day-1440x1000',[-30900,205,3830],[-30570,5,3590],'15:00');await frame('channels-night-1440x1000',[-30900,205,3830],[-30570,5,3590],'22:00');await frame('tai-chung-bridge-1440x1000',[-30625,50,3720],[-30672,4,3674],'15:00');
 const picking=await page.evaluate(()=>{const {bridgeLayer,camera,THREE,stream}=window.__taiOCompletion,model=[...bridgeLayer.surfaces.models.values()].find(m=>m.routeProxyId==='way/507688251'),p=model.modelGeometry.position;for(const t of model.walkTriangleIndices){const i=t*9,q=new THREE.Vector3((p[i]+p[i+3]+p[i+6])/3,(p[i+1]+p[i+4]+p[i+7])/3,(p[i+2]+p[i+5]+p[i+8])/3).project(camera),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2(q.x,q.y),camera);const hit=ray.intersectObjects([...bridgeLayer.pickMeshes(),...stream.pickMeshes(ray.ray)])[0];if(hit&&bridgeLayer.featureAt(hit)?.id===model.id)return {id:model.id,click:[(q.x+1)*innerWidth/2,(1-q.y)*innerHeight/2]};}throw Error('Source deck cannot be picked');});await page.mouse.click(...picking.click);assert.equal(await page.locator('#building-height-label').textContent(),'DECK · HKPD');report.picking={...picking,card:await page.locator('#building-card').innerText()};await page.screenshot({path:new URL('bridge-source-card-1440x1000.png',output).pathname});await page.locator('#selection-close').click();report.checks.push('Rendered source bridge remains selectable with public access and HKPD provenance');
 report.approaches=[];
 const approachNames=await page.evaluate(()=>[...window.__taiOCompletion.bridgeLayer.records.values()].filter(r=>r.estimatedPublicApproach).map(r=>r.name));
 for(const name of approachNames){
  await tab('places');await page.locator('#search').fill(name);await page.locator('#search-results button').filter({hasText:name}).click();await settle();
  await page.locator('#building-card').waitFor({state:'visible'});assert.equal(await page.locator('#building-height-label').textContent(),'ESTIMATED · HKPD');
  const card=await page.locator('#building-card').innerText();assert.match(card,/estimated|illustrative/i);assert.doesNotMatch(card,/undefined|NaN/);
  assert.equal(await page.evaluate(()=>window.__city.state.camera.every(Number.isFinite)),true);report.approaches.push({name,card});await page.screenshot({path:new URL('approach-'+report.approaches.length+'-1440x1000.png',output).pathname});await page.locator('#selection-close').click();
 }
 report.checks.push('Both estimated public approaches are searchable and show their estimated profile and width without invalid camera/card values');
 if(!geometryOnly&&route.walkCentreline){
  report.walk=await page.evaluate(async points=>{
   const {nav,stream,sampler}=window.__taiOCompletion;await stream.arrive(points[0][0],points[0][1],3200);
   if(!nav.setMode('walk',points[0]))throw Error('No route start');
   const start=nav.position.toArray(),failures=[],stops=[];nav.keys.add('KeyW');
   for(let i=1;i<points.length;i++){
    const [x,z]=points[i];let attempts=0,prior=Infinity,stuck=0;
    while(Math.hypot(x-nav.position.x,z-nav.position.z)>.035){const dx=x-nav.position.x,dz=z-nav.position.z,d=Math.hypot(dx,dz);nav.heading=Math.atan2(dx,-dz);nav.update(Math.min(.025,d/3.9));if(Math.abs(prior-d)<1e-5)stuck++;else stuck=0;prior=d;if(++attempts>10000||stuck>5){failures.push({i,target:[x,z],position:nav.position.toArray(),raw:sampler.raw(x,z),ground:sampler.height(x,z)});break;}}
    if(failures.length)break;if(i%100===0)stops.push(nav.position.toArray());
   }
   nav.keys.clear();return {start,end:nav.position.toArray(),distance:nav.distance,failures,stops,points:points.length,collision:!!nav.collides(nav.position.x,nav.position.z,nav.position.y,nav.position.y+1.8,.55,true)};
  },route.walkCentreline);assert.deepEqual(report.walk.failures,[]);assert.ok(report.walk.distance>600);assert.equal(report.walk.collision,false);await page.screenshot({path:new URL('continuous-walk-finish-1440x1000.png',output).pathname});report.checks.push('Actual app Navigation.update continuously traverses the reviewed public route, with existing collisions and tides; only initial spawn, no intermediate teleport');
 }else if(!geometryOnly)throw Error('Reviewed continuous walking route is not ready');
 await page.locator('[data-mode="orbit"]').click();await page.setViewportSize({width:390,height:844});await frame('channels-mobile-390x844',[-30920,320,3940],[-30585,5,3610],'15:00');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(report.errors,[]);assert.deepEqual(report.failures,[]);report.result='passed';console.log(JSON.stringify({result:report.result,checks:report.checks,views:report.views.map(v=>({name:v.name,medianFrameMs:v.medianFrameMs,p95FrameMs:v.p95FrameMs})),walk:report.walk,errors:report.errors},null,2));
}catch(e){report.result='failed';report.error=e.stack;await page.screenshot({path:new URL('failure.png',output).pathname}).catch(()=>{});throw e;}finally{await writeFile(new URL(geometryOnly?'geometry-verification.json':'verification.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
