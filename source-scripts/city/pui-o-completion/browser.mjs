/** Bounded acceptance in the existing city app. Run only after coordinated publication/GPU release. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const require=createRequire(new URL('../../../3d-viewer/city/package.json',import.meta.url)),{chromium}=require('playwright');
const root=new URL('../../../',import.meta.url),out=new URL('docs/astra-city/pui-o-completion/browser/',root);
const read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const hash=async p=>createHash('sha256').update(await readFile(new URL(p,root))).digest('hex');
const catalogueURL='city/data/official-models/pui-o/catalogue.json',manifest=await read('3d-viewer/city/data/manifest.json');
// Fail before Chrome or evidence writes when the staged package is not yet live.
assert.ok(manifest.officialModelCatalogues?.includes(catalogueURL),'Publish the staged Pui O catalogue before running this acceptance script');
assert.equal(await hash('3d-viewer/'+catalogueURL),await hash('source-scripts/city/pui-o-completion/compact/catalogue.json'));
assert.equal(await hash('3d-viewer/city/data/terrain-pui-o.json'),await hash('source-scripts/city/pui-o-completion/terrain-pui-o.json'));
const catalogue=await read('3d-viewer/'+catalogueURL),metas=catalogue.models;
assert.equal(metas.length,681);
const tile=await read('3d-viewer/city/data/tiles/-10_2.json'),buildings=new Map(tile.buildings.map(b=>[b.uid,b]));
const representatives=[['west-village','landsd/135520:0'],['middle-village','landsd/77541:0'],['east-village','landsd/77602:0']].map(([view,uid])=>({view,...metas.find(m=>m.uid===uid)}));
for(const m of representatives)assert.ok(m.modelId&&buildings.has(m.uid));
const route=await read('docs/astra-city/pui-o-completion/route.json');
const report={result:'running',startedUTC:new Date().toISOString(),commit:execFileSync('git',['rev-parse','HEAD'],{cwd:root}).toString().trim(),url:process.env.CITY_URL||'http://127.0.0.1:4176/city.html',manifestSha256:await hash('3d-viewer/city/data/manifest.json'),catalogueSha256:await hash('3d-viewer/'+catalogueURL),terrainSha256:await hash('3d-viewer/city/data/terrain-pui-o.json'),expectedModels:681,views:[],sourceModels:[],arrivals:[],errors:[],dataFailures:[],limits:['Three representative compact models are checked visually; all 681 already have independent source/CPU loader checks.','The short beach walk is an actual held-key browser check. The separate 555 m forward/reverse CPU Navigation replay is not represented as a full browser walk.','Wetland inundation, the inland shared-road connection and full section 10.7 acceptance remain under review.']};
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
report.browser=await browser.version();let currentPage;
const save=()=>writeFile(new URL('verification.json',out),JSON.stringify(report,null,2)+'\n');
const snap=(page,name)=>page.screenshot({path:new URL(name+'.png',out).pathname});
async function open(width=1440,failedModel=null){
 const page=await browser.newPage({viewport:{width,height:width===390?844:1000},deviceScaleFactor:1,reducedMotion:'reduce',hasTouch:width===390});currentPage=page;
 page.on('pageerror',error=>report.errors.push(error.message));
 page.on('console',message=>{if(/THREE.WebGLProgram|GL_INVALID|shader error/i.test(message.text()))report.errors.push(message.text());});
 page.on('response',response=>{if(response.url().includes('/city/data/')&&response.status()>=400)report.dataFailures.push({url:response.url(),status:response.status()});});
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__puiOReview",{get:()=>({officialModels,stream,camera,controls,renderer,sampler,THREE,nav,terrain,water,environment,visitBuilding,closeSelection,controlSheet})});\n'});});
 let fail=!!failedModel;const aborted=[];
 if(failedModel)await page.route(`**/${failedModel.modelId}.glb.gz`,async r=>{if(fail){aborted.push(r.request().url());await r.abort('failed');}else await r.continue();});
 const started=performance.now();await page.goto(report.url+(report.url.includes('?')?'&':'?')+'district=puio');
 await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden'});
 await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:90000});
 await page.waitForFunction(ids=>ids.every(uid=>window.__puiOReview.officialModels.models.has(uid)),metas.map(m=>m.uid),{timeout:90000});
 assert.equal((await page.evaluate(()=>window.__city.state)).counts.buildings,346115);
 return {page,startupMs:performance.now()-started,aborted,recover:()=>{fail=false;}};
}
async function settle(page){
 await page.waitForFunction(()=>{const s=window.__city.state;return !s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending&&!s.models.pending&&!s.models.retiring;},null,{timeout:120000});
}
async function tab(page,name){if(!(await page.evaluate(()=>window.__city.state.controls.expanded)))await page.locator('#panel-toggle').click();await page.locator('#tab-'+name).click();}
async function time(page,value){await tab(page,'time');await page.locator('#time').fill(value);await page.evaluate(()=>window.__puiOReview.controlSheet.close({restoreFocus:false}));await page.waitForTimeout(120);}
async function frame(page,name,eye,target,value='15:00'){
 await time(page,value);await page.evaluate(({eye,target})=>{const {camera,controls,closeSelection}=window.__puiOReview;closeSelection();camera.position.fromArray(eye);controls.target.fromArray(target);controls.update();camera.updateMatrixWorld(true);},{eye,target});
 await page.waitForTimeout(300);await settle(page);await snap(page,name);report.views.push({name,eye,target,time:value,state:await page.evaluate(()=>window.__city.state)});
}
async function focus(page,meta,{allowFailure=false}={}){
 const source=buildings.get(meta.uid);await page.evaluate(b=>window.__puiOReview.visitBuilding(b),{uid:source.uid,tile:source.tile,centre:source.centre,base:source.base,height:source.height});
 await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
 await page.waitForFunction(({uid,failed})=>failed?window.__puiOReview.officialModels.cache.errors.has(uid):window.__puiOReview.stream.detailedModels.get(uid)?.active,{uid:meta.uid,failed:allowFailure},{timeout:120000});
 const [a,b]=meta.worldBounds,centre=a.map((v,i)=>(v+b[i])/2),distance=Math.max(36,(b[0]-a[0])*1.8,(b[2]-a[2])*1.8);
 await page.evaluate(({centre,top,distance})=>{const {camera,controls,controlSheet}=window.__puiOReview;camera.position.set(centre[0]+distance*.7,top+distance*.75,centre[2]+distance);controls.target.fromArray(centre);controls.update();camera.updateMatrixWorld(true);controlSheet.close({restoreFocus:false});},{centre,top:b[1],distance});
 await page.waitForTimeout(300);await settle(page);
}
async function sourceProof(page,meta){
 const proof=await page.evaluate(uid=>{
  const {stream,officialModels,renderer}=window.__puiOReview,e=stream.detailedModels.get(uid),g=e.record.modelGeometry,p=g.position,order=g.index;let contact;
  for(let i=0;i<order.length;i+=3){const ids=[order[i],order[i+1],order[i+2]],q=[0,1,2].map(a=>ids.reduce((s,id)=>s+p[id*3+a],0)/3);if(stream.collision(q[0],q[2],q[1]-.05,q[1]+.05,.05)?.uid===uid){contact=q;break;}}
  const materials=[...new Set(e.meshes.flatMap(m=>[].concat(m.material)))],compiled=materials.filter(m=>renderer.properties.get(m).uniforms?.uCityNight===stream.lighting.night).length;
  return {uid,modelId:e.record.modelId,active:e.active,visible:e.group.visible,worldBounds:[e.bounds.min.toArray(),e.bounds.max.toArray()],recordedBase:e.record.baseHeightHKPD??null,recordedTop:e.record.topHeightHKPD??null,triangles:e.entry.triangles,contact,aboveRoofCollision:contact?stream.collision(contact[0],contact[2],e.bounds.max.y+1,e.bounds.max.y+2,.05)?.uid??null:null,compiledNightMaterials:compiled,sourceMaterialCount:materials.length,stats:officialModels.stats};
 },meta.uid);
 assert.equal(proof.modelId,meta.modelId);assert.equal(proof.active,true);assert.equal(proof.visible,true);proof.maximumPlacementErrorMetres=Math.max(...proof.worldBounds.flat().map((v,i)=>Math.abs(v-meta.worldBounds.flat()[i])));assert.ok(proof.maximumPlacementErrorMetres<.002);assert.equal(proof.recordedBase,meta.recordedBaseHeight);assert.equal(proof.recordedTop,meta.recordedTopHeight);assert.ok(proof.contact);assert.equal(proof.aboveRoofCollision,null);assert.ok(proof.compiledNightMaterials>0);return proof;
}
async function pick(page,meta,{fallback=false}={}){
 await page.evaluate(()=>window.__puiOReview.closeSelection());
 const point=await page.evaluate(({uid,fallback})=>{
  const {stream,camera,THREE,renderer}=window.__puiOReview,detail=stream.detailedModels.get(uid),r=stream.getLoadedBuilding(uid),candidates=[];
  const addTriangles=(mesh,featureIndex)=>{const p=mesh.geometry.attributes.position,index=mesh.geometry.index,feature=mesh.geometry.attributes.feature,n=index?.count??p.count,step=featureIndex===undefined?Math.max(3,Math.floor(n/120/3)*3):3;
   mesh.updateMatrixWorld(true);for(let i=0;i+2<n;i+=step){const ids=[0,1,2].map(k=>index?index.getX(i+k):i+k);if(featureIndex!==undefined&&Math.round(feature.getX(ids[0]))!==featureIndex)continue;const q=new THREE.Vector3();for(const id of ids)q.add(new THREE.Vector3().fromBufferAttribute(p,id));candidates.push(q.divideScalar(3).applyMatrix4(mesh.matrixWorld));}
  };
  if(detail?.active&&!fallback){for(const mesh of detail.meshes)addTriangles(mesh);}
  else{const tile=stream.cache.entries.get(r.tile),featureIndex=tile.data.buildings.findIndex(b=>b.uid===uid);for(const mesh of tile.buildings.group.children)addTriangles(mesh,featureIndex);}
  const ray=new THREE.Raycaster();for(const p of candidates.sort((a,b)=>b.y-a.y)){const v=p.clone().project(camera);if(Math.abs(v.x)>.82||Math.abs(v.y)>.72||v.z>1)continue;const x=(v.x+1)*innerWidth/2,y=(1-v.y)*innerHeight/2;if(document.elementFromPoint(x,y)!==renderer.domElement)continue;ray.setFromCamera(new THREE.Vector2(v.x,v.y),camera);const hit=ray.intersectObjects(stream.pickMeshes(ray.ray),false)[0];if(hit&&stream.featureAt(hit)?.uid===uid)return {x,y};}return null;
 },{uid:meta.uid,fallback});assert.ok(point,'Unobscured source '+(fallback?'fallback':'model')+' ray for '+meta.uid);
 await page.mouse.click(point.x,point.y);await page.waitForFunction(uid=>window.__city.state.selectedId===uid,meta.uid,{timeout:10000});
 assert.equal(await page.locator('#building-height-label').textContent(),fallback?'HEIGHT':'OUTLINE HEIGHT');const source=await page.locator('#building-source').innerText();if(fallback)assert.doesNotMatch(source,/Official Lands Department non-textured/);else assert.match(source,/Official Lands Department non-textured/);
 return {uid:meta.uid,point,source,href:await page.locator('#building-osm').getAttribute('href')};
}
const measure=page=>page.evaluate(async()=>{const samples=[];let last;for(let i=0;i<140;i++){const now=await new Promise(requestAnimationFrame);if(i>20)samples.push(now-last);last=now;}samples.sort((a,b)=>a-b);return {samples:samples.length,medianFrameMs:samples[Math.floor(samples.length*.5)],p95FrameMs:samples[Math.floor(samples.length*.95)],render:window.__city.state.render,models:window.__city.state.models};});
function budgets(stats){assert.ok(stats.cached<=stats.limits.count);assert.ok(stats.geometryBytes<=stats.limits.geometryBytes);assert.ok(stats.residentBytes<=stats.limits.residentBytes);assert.ok(stats.triangles<=stats.limits.triangles);}
async function arrival(page,id){
 await tab(page,'places');await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="'+id+'"]').click();await settle(page);assert.equal((await page.evaluate(()=>window.__city.state)).place,id);
 await page.evaluate(()=>window.__puiOReview.controlSheet.close({restoreFocus:false}));await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:90000});const start=await page.evaluate(()=>window.__city.state);assert.equal(start.collision,false);
 const proof={id,position:start.position,collision:start.collision,movementReady:start.movementReady};
 if(id==='puiobeach'){
  // Follow the next source vertex in the already verified beach footway, not an invented inland shortcut.
  const next=route.centreline.filter(p=>p[0]>start.position[0]+5).sort((a,b)=>Math.hypot(a[0]-start.position[0],a[1]-start.position[2])-Math.hypot(b[0]-start.position[0],b[1]-start.position[2]))[0];assert.ok(next);
  await page.evaluate(p=>{const n=window.__puiOReview.nav;n.heading=Math.atan2(p[0]-n.position.x,-(p[1]-n.position.z));},next);
  await page.keyboard.down('w');try{await page.waitForFunction(d=>window.__city.state.distance>d+3,start.distance,{timeout:6000});}finally{await page.keyboard.up('w');}
  const end=await page.evaluate(()=>window.__city.state);proof.walkedMetres=end.distance-start.distance;proof.end=end.position;proof.endCollision=end.collision;proof.sourceWayId=107501760;assert.equal(end.collision,false);await snap(page,'beach-short-walk-1440x1000');
 }
 report.arrivals.push(proof);await page.locator('[data-mode="orbit"]').click();
}
try{
 const desktop=await open();report.startupMs=desktop.startupMs;const page=desktop.page;
 await page.locator('#section-grid-toggle').click();await page.waitForFunction(()=>window.__city.state.sections.total===132&&!window.__city.state.sections.pending,null,{timeout:90000});
 await tab(page,'places');await page.locator('#section-select').selectOption('10.7');report.sectionReadiness={state:await page.evaluate(()=>window.__city.state.sections),issueLink:await page.locator('#section-issues a').filter({hasText:'HKS-171'}).getAttribute('href')};assert.deepEqual(report.sectionReadiness.state.counts,{ready:0,close:0,reviewing:12,base:120});assert.equal(report.sectionReadiness.state.selected,'10.7');assert.equal(report.sectionReadiness.issueLink,'https://linear.app/stealth-company/issue/HKS-171');await page.locator('#section-grid-toggle').click();assert.equal(await page.evaluate(()=>window.__city.state.sections.enabled),false);
 await frame(page,'village-overview-day-1440x1000',[-18580,175,5100],[-18780,12,4840]);
 await frame(page,'village-overview-night-1440x1000',[-18580,175,5100],[-18780,12,4840],'22:00');report.desktopPerformance=await measure(page);budgets(report.desktopPerformance.models);
 for(const meta of representatives){await time(page,'15:00');await focus(page,meta);const proof=await sourceProof(page,meta);proof.pick=await pick(page,meta);proof.view=meta.view;report.sourceModels.push(proof);await snap(page,meta.view+'-source-1440x1000');}
 await time(page,'22:00');await focus(page,representatives[1]);const night=await sourceProof(page,representatives[1]);assert.ok((await page.evaluate(()=>window.__city.state.lighting.night))>.5);report.nightModel=night;await pick(page,representatives[1]);await snap(page,'village-model-night-1440x1000');
 await frame(page,'beach-day-1440x1000',[-18450,200,5620],[-18760,5,5370]);
 report.beachPlacement=await page.evaluate(points=>{const s=window.__puiOReview.sampler;return points.map(([x,z])=>({world:[x,z],ground:s.height(x,z),raw:s.raw(x,z),mappedWater:s.mappedWater(x,z)}));},route.centreline);
 for(const id of ['puio','puiobeach'])await arrival(page,id);
 await page.locator('[data-mode="fly"]').click();await page.waitForFunction(()=>window.__city.state.mode==='fly'&&window.__city.state.movementReady,null,{timeout:90000});const flightStart=await page.evaluate(()=>window.__city.state.position);await page.waitForTimeout(1500);const flightEnd=await page.evaluate(()=>window.__city.state);report.flight={start:flightStart,end:flightEnd.position,distanceMetres:Math.hypot(flightEnd.position[0]-flightStart[0],flightEnd.position[2]-flightStart[2]),collision:flightEnd.collision};assert.ok(report.flight.distanceMetres>20);assert.equal(report.flight.collision,false);await snap(page,'pui-o-flight-1440x1000');await page.locator('[data-mode="orbit"]').click();await page.waitForFunction(()=>window.__city.state.mode==='orbit'&&!window.__city.state.loadingTravel,null,{timeout:10000});report.flight.returnedToOrbit=true;await page.close();
 const mobile=await open(390);await time(mobile.page,'22:00');await focus(mobile.page,representatives[1]);report.mobile={width:390,height:844,startupMs:mobile.startupMs,model:await sourceProof(mobile.page,representatives[1]),pick:await pick(mobile.page,representatives[1])};assert.equal(report.mobile.model.stats.profile,'mobile');budgets(report.mobile.model.stats);await snap(mobile.page,'village-mobile-source-night-390x844');await mobile.page.evaluate(()=>window.__puiOReview.closeSelection());await frame(mobile.page,'village-mobile-clean-day-390x844',[-18580,130,4920],[-18730,10,4800]);await frame(mobile.page,'village-mobile-clean-night-390x844',[-18580,130,4920],[-18730,10,4800],'22:00');report.mobile.performance=await measure(mobile.page);await tab(mobile.page,'time');assert.equal(await mobile.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await snap(mobile.page,'time-controls-mobile-390x844');await mobile.page.close();
 const meta=representatives[1],failed=await open(1440,meta);await time(failed.page,'15:00');await focus(failed.page,meta,{allowFailure:true});
 report.failureFallback=await failed.page.evaluate(uid=>{const {stream,officialModels}=window.__puiOReview;return {uid,modelActive:!!stream.detailedModels.get(uid)?.active,fallbackHasModel:!!stream.getLoadedBuilding(uid)?.modelGeometry,errorRecorded:officialModels.cache.errors.has(uid)};},meta.uid);assert.equal(report.failureFallback.modelActive,false);assert.equal(report.failureFallback.fallbackHasModel,false);assert.equal(report.failureFallback.errorRecorded,true);assert.ok(failed.aborted.length);report.failureFallback.abortedRequests=failed.aborted;report.failureFallback.pick=await pick(failed.page,meta,{fallback:true});await snap(failed.page,'failed-model-visible-fallback-1440x1000');
 failed.recover();await failed.page.locator('#stream-retry').click();await failed.page.waitForFunction(uid=>window.__puiOReview.stream.detailedModels.get(uid)?.active,meta.uid,{timeout:120000});await focus(failed.page,meta);report.failureFallback.recovery=await sourceProof(failed.page,meta);report.failureFallback.recoveredPick=await pick(failed.page,meta);await snap(failed.page,'failed-model-recovered-1440x1000');await failed.page.close();
 assert.deepEqual(report.errors,[]);assert.deepEqual(report.dataFailures,[]);report.result='passed';console.log(JSON.stringify({result:report.result,views:report.views.length,models:report.sourceModels.length,arrivals:report.arrivals.length,desktop:report.desktopPerformance,mobile:report.mobile.performance},null,2));
}catch(error){report.result='failed';report.failure=error.stack;if(currentPage&&!currentPage.isClosed())await snap(currentPage,'failure').catch(()=>{});throw error;}
finally{report.finishedUTC=new Date().toISOString();await save();await browser.close();}
