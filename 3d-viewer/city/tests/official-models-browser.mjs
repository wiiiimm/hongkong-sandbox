// Actual app acceptance. Uses the existing browser review hook pattern only for
// camera framing/inspection; source picking, clock and Retry use real UI controls.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=new URL('../../../',import.meta.url),out=fileURLToPath(new URL('../../../docs/astra-city/central-completion/browser/',import.meta.url));
await mkdir(out,{recursive:true});
const metas=(await Promise.all(['compact','compact-followup','compact-corridor'].map(async batch=>JSON.parse(await readFile(new URL(`source-scripts/city/central-completion/${batch}/catalogue.json`,root),'utf8')).models))).flat();
assert.equal(metas.length,37);
const manifest=JSON.parse(await readFile(new URL('../data/manifest.json',import.meta.url),'utf8')),tiles=new Map(),visitors=new Map(),sourceRecords=new Map();
for(const m of metas){for(const tile of manifest.tiles){const b=tile.bounds,a=m.worldBounds;if(b[0]>a[1][0]||b[2]<a[0][0]||b[1]>a[1][2]||b[3]<a[0][2])continue;if(!tiles.has(tile.id))tiles.set(tile.id,JSON.parse(await readFile(new URL(`../data/tiles/${tile.id}.json`,import.meta.url),'utf8')));const r=tiles.get(tile.id).buildings.find(b=>b.uid===m.uid);if(r){sourceRecords.set(m.uid,r);visitors.set(m.uid,{uid:r.uid,tile:r.tile,centre:r.centre,base:r.base,height:r.height,name:r.name});break;}}assert.ok(visitors.has(m.uid),m.uid);}
const {inPolygon}=await import('../geo.js');
const placement=new Map(metas.map(m=>{const b=sourceRecords.get(m.uid),point=b.centre,below=[...tiles.values()].flatMap(t=>t.buildings).filter(r=>r.uid!==b.uid&&r.base<=m.worldBounds[0][1]&&r.base+r.height>=m.worldBounds[0][1]-.8&&inPolygon(point[0],point[1],r.rings));return [m.uid,{footprintCentre:point,sourceBottomHKPD:m.worldBounds[0][1],recordedBaseHKPD:b.baseHeightHKPD??null,foundationBase:b.foundationBase??null,retainedSupportingForms:below.map(r=>({uid:r.uid,name:r.name,structureType:r.structureType,base:r.base,top:r.base+r.height})),note:'Centre sampling is a placement diagnostic, not proof of a surveyed ground contact. Native model geometry and recorded source heights are unchanged.'}];}));
const previous=process.argv.includes('--resume')?JSON.parse(await readFile(out+'verification.json','utf8')):null;if(previous)await writeFile(out+'first-pass.json',JSON.stringify(previous,null,2)+'\n');
const report={result:'running',startedUTC:new Date().toISOString(),url:process.env.CITY_URL||'http://127.0.0.1:4176/city.html',visits:[],mobile:[],errors:[]};
if(previous){report.visits=previous.visits;report.priorRun={startedUTC:previous.startedUTC,startupMs:previous.startupMs,failure:previous.failure,note:'Completed source-model checks retained; camera visibility search extended for a podium obscured from the first fixed angle.'};}
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});report.browser=await browser.version();
const save=()=>writeFile(out+(process.argv.includes('--exports')?'exports-verification.json':'verification.json'),JSON.stringify(report,null,2)+'\n');
const snap=(page,name)=>page.screenshot({path:out+name+'.png'});
async function pageFor(width=1440,failedModel=null){
 const page=await browser.newPage({viewport:{width,height:width<=760?844:1000},deviceScaleFactor:1,reducedMotion:'reduce',hasTouch:width<=760});
 page.on('pageerror',e=>report.errors.push(e.message));page.on('console',e=>{if((e.type()==='error'||/THREE.WebGLProgram|GL_INVALID|shader error/i.test(e.text()))&&!e.text().includes('net::ERR_FAILED'))report.errors.push(e.text());});
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__modelReview",{get:()=>({officialModels,stream,camera,controls,renderer,scene,sampler,THREE,visitBuilding,closeSelection,controlSheet})});\n'});});
 let fail=!!failedModel;if(failedModel)await page.route(`**/${failedModel.modelId}.glb.gz`,async route=>fail?route.abort('failed'):route.continue());
 const started=performance.now();await page.goto(report.url+'?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden'});await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:90000});
 await page.waitForFunction(ids=>ids.every(id=>window.__modelReview.officialModels.models.has(id)),metas.map(m=>m.uid),{timeout:90000});
 return {page,startupMs:performance.now()-started,recover:()=>{fail=false;}};
}
async function time(page,value){if(!await page.locator('#explorer').evaluate(e=>e.classList.contains('open')))await page.locator('#panel-toggle').click();await page.locator('#tab-time').click();await page.locator('#time').fill(value);await page.evaluate(()=>window.__modelReview.controlSheet.close({restoreFocus:false}));await page.waitForTimeout(120);}
async function visit(page,meta,{allowFailure=false}={}){
 const start=performance.now();await page.evaluate(row=>window.__modelReview.visitBuilding(row),visitors.get(meta.uid));await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
 if(allowFailure){await page.waitForFunction(uid=>window.__modelReview.officialModels.cache.errors.has(uid),meta.uid,{timeout:90000});return;}
 await page.waitForFunction(uid=>window.__modelReview.stream.detailedModels.get(uid)?.active,meta.uid,{timeout:120000});
 await page.evaluate(uid=>{
  const {stream,camera,controls,controlSheet}=window.__modelReview,e=stream.detailedModels.get(uid),b=e.bounds,centre=b.getCenter(camera.position.clone()),size=b.getSize(camera.position.clone());
  const distance=Math.max(35,Math.max(size.x,size.z)*1.1,size.y*.7);camera.position.set(centre.x+distance*.65,b.max.y+distance*.7,centre.z+distance);controls.target.set(centre.x,centre.y,centre.z);controls.update();camera.updateMatrixWorld(true);controlSheet.close({restoreFocus:false});
 },meta.uid);await page.waitForTimeout(200);
 const proof=await page.evaluate(async uid=>{
  const {stream,officialModels,renderer,THREE,sampler}=window.__modelReview,e=stream.detailedModels.get(uid),p=e.record.modelGeometry.position,order=e.record.modelGeometry.index;
  const {modelSurfaceCollision}=await import('/city/model-collision.js');let contact;
  for(let i=0;i<order.length;i+=3){const ids=[order[i],order[i+1],order[i+2]],q=[0,1,2].map(a=>ids.reduce((sum,id)=>sum+p[id*3+a],0)/3);if(modelSurfaceCollision(e.record.modelGeometry,q[0],q[2],q[1]-.05,q[1]+.05,.05)){contact=q;break;}}
  const materials=[...new Set(e.meshes.flatMap(m=>[].concat(m.material)))],compiled=materials.filter(m=>renderer.properties.get(m).uniforms?.uCityNight===stream.lighting.night).length;
  const centre=e.record.centre;const low=[];for(let i=0;i<p.length;i+=3)if(p[i+1]<=e.bounds.min.y+1)low.push(p[i+1]-sampler.height(p[i],p[i+2]));low.sort((a,b)=>a-b);
  return {groundAtFootprintCentre:sampler.height(centre[0],centre[1]),groundResolution:sampler.resolutionAt(centre[0],centre[1]),lowSourceVertices:{withinMetresOfMinimum:1,count:low.length,minTerrainDifference:low[0],medianTerrainDifference:low[Math.floor(low.length/2)],maxTerrainDifference:low.at(-1)},uid,modelId:e.record.modelId,active:e.active,visible:e.group.visible,triangles:e.entry.triangles,geometryBytes:e.entry.decodedGeometryBytes,worldBounds:[e.bounds.min.toArray(),e.bounds.max.toArray()],recordedBase:e.record.baseHeightHKPD,recordedTop:e.record.topHeightHKPD,indexed:e.meshes.every(m=>!!m.geometry.index),compiledNightMaterials:compiled,sourceMaterialCount:materials.length,activity:e.record.activity,contact,roof:stream.maximumRoof(e.bounds.getCenter(new THREE.Vector3()).x,e.bounds.getCenter(new THREE.Vector3()).z,2),aboveRoofCollision:modelSurfaceCollision(e.record.modelGeometry,e.bounds.min.x,e.bounds.min.z,e.bounds.max.y+.1,e.bounds.max.y+2,.1),stats:officialModels.stats};
 },meta.uid);
 assert.equal(proof.modelId,meta.modelId);assert.equal(proof.recordedBase??null,meta.recordedBaseHeight);assert.equal(proof.recordedTop??null,meta.recordedTopHeight);assert.equal(proof.indexed,true);assert.ok(proof.contact);assert.equal(proof.aboveRoofCollision,false);assert.ok(proof.roof>=meta.worldBounds[1][1]-.001);assert.ok(proof.compiledNightMaterials>0,meta.label+' shared night shader compiled');proof.placement=placement.get(meta.uid);proof.readyMs=performance.now()-start;return proof;
}
async function pick(page,uid){
 await page.evaluate(()=>window.__modelReview.closeSelection());
 const findPoint=()=>page.evaluate(uid=>{
  const {stream,camera,THREE,renderer}=window.__modelReview,e=stream.detailedModels.get(uid),ray=new THREE.Raycaster(),v=new THREE.Vector3(),candidates=[e.bounds.getCenter(new THREE.Vector3())];
  e.group.updateMatrixWorld(true);
  for(const mesh of e.meshes){const p=mesh.geometry.attributes.position,index=mesh.geometry.index;for(let i=0;i<index.count;i+=Math.max(3,Math.floor(index.count/300/3)*3)){if(i+2>=index.count)break;const q=new THREE.Vector3();for(let k=0;k<3;k++)q.add(new THREE.Vector3().fromBufferAttribute(p,index.getX(i+k)));candidates.push(q.divideScalar(3).applyMatrix4(mesh.matrixWorld));}}
  for(const p of candidates){v.copy(p).project(camera);if(Math.abs(v.x)>.82||Math.abs(v.y)>.75||v.z>1)continue;const x=(v.x+1)*innerWidth/2,y=(1-v.y)*innerHeight/2;if(document.elementFromPoint(x,y)!==renderer.domElement)continue;ray.setFromCamera(new THREE.Vector2(v.x,v.y),camera);const hit=ray.intersectObjects(stream.pickMeshes(ray.ray),false)[0];if(hit&&stream.featureAt(hit)?.uid===uid)return {x,y};}
  return null;
 },uid);
 let point=await findPoint();for(let angle=0;!point&&angle<8;angle++){await page.evaluate(({uid,angle})=>{const {stream,camera,controls}=window.__modelReview,e=stream.detailedModels.get(uid),b=e.bounds,c=b.getCenter(camera.position.clone()),s=b.getSize(camera.position.clone()),d=Math.max(35,s.x*1.5,s.z*1.5,s.y*.8),a=angle*Math.PI/4;camera.position.set(c.x+Math.sin(a)*d,b.max.y+d*.7,c.z+Math.cos(a)*d);controls.target.copy(c);controls.update();camera.updateMatrixWorld(true);},{uid,angle});await page.waitForTimeout(120);point=await findPoint();}
 assert.ok(point,'An unobscured source-model click ray for '+uid);await page.mouse.click(point.x,point.y);await page.waitForFunction(uid=>window.__city.state.selectedId===uid,uid,{timeout:10000});assert.equal(await page.locator('#building-height-label').textContent(),'OUTLINE HEIGHT');const text=await page.locator('#building-source').innerText();assert.match(text,/Official Lands Department non-textured/);return {point,source:text,href:await page.locator('#building-osm').getAttribute('href')};
}
const measure=page=>page.evaluate(()=>new Promise(resolve=>{const values=[];let last;function frame(t){if(last!==undefined)values.push(t-last);last=t;if(values.length<120)requestAnimationFrame(frame);else{values.sort((a,b)=>a-b);resolve({median:values[60],p95:values[114]});}}requestAnimationFrame(frame);}));
const captured=new Set(['landsd/89275:0','landsd/123884:0','landsd/1307:0','landsd/98449:0','landsd/124803:0','landsd/145002:0','landsd/94583:0','landsd/161250:0','landsd/265525:0']);
try{
 if(process.argv.includes('--exports')){
  const frame=async(page,meta)=>{
   await visit(page,meta);await page.evaluate(uid=>{
    const {stream,camera,controls,closeSelection,THREE}=window.__modelReview,e=stream.detailedModels.get(uid),b=e.bounds,c=b.getCenter(new THREE.Vector3()),p=e.record.modelGeometry.position,index=e.record.modelGeometry.index,points=[],ray=new THREE.Raycaster(),tv=Math.tan(camera.getEffectiveFOV()*Math.PI/360),th=tv*camera.aspect;
    for(let i=0;i<index.length;i+=Math.max(3,Math.floor(index.length/24/3)*3)){if(i+2>=index.length)break;const q=new THREE.Vector3();for(let j=0;j<3;j++)q.add(new THREE.Vector3().fromArray(p,index[i+j]*3));points.push(q.divideScalar(3));}
    let best={score:-1,position:null};
    for(const elevation of [.8,2,5]){for(let turn=0;turn<8;turn++){
     const angle=Math.PI+turn*Math.PI/4,n=new THREE.Vector3(Math.sin(angle),elevation,Math.cos(angle)).normalize(),right=new THREE.Vector3(n.z,0,-n.x).normalize(),up=new THREE.Vector3().crossVectors(n,right).normalize();let distance=35;
     for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){const q=new THREE.Vector3(x,y,z).sub(c),depth=q.dot(n);distance=Math.max(distance,depth+Math.abs(q.dot(right))/(th*.78),depth+Math.abs(q.dot(up))/(tv*.60));}
     camera.position.copy(c).addScaledVector(n,distance);controls.target.copy(c);controls.update();camera.updateMatrixWorld(true);let score=0;
     for(const q of points){const v=q.clone().project(camera);ray.setFromCamera(new THREE.Vector2(v.x,v.y),camera);const hit=ray.intersectObjects(stream.pickMeshes(ray.ray),false)[0];if(hit&&stream.featureAt(hit)?.uid===uid)score++;}
     if(score>best.score)best={score,position:camera.position.clone()};if(score>=points.length*.75)break;
    }if(best.score>=points.length*.75)break;}
    camera.position.copy(best.position);controls.target.copy(c);controls.update();camera.updateMatrixWorld(true);closeSelection();

   },meta.uid);await page.waitForTimeout(750);
  };
  const desktop=await pageFor();
  for(const uid of ['landsd/89275:0','landsd/123884:0','landsd/161250:0','landsd/94583:0','landsd/265525:0','landsd/1307:0','landsd/124803:0']){const meta=metas.find(m=>m.uid===uid);await time(desktop.page,'15:00');await frame(desktop.page,meta);await snap(desktop.page,'clean-desktop-'+meta.modelId);if(uid==='landsd/89275:0'){await time(desktop.page,'21:00');await snap(desktop.page,'clean-desktop-hsbc-night');}}
  await desktop.page.close();
  for(const width of [390,320]){const mobile=await pageFor(width);await time(mobile.page,'21:00');for(const uid of ['landsd/89275:0','landsd/1307:0']){const meta=metas.find(m=>m.uid===uid);await frame(mobile.page,meta);await snap(mobile.page,`clean-mobile-${width}-${meta.modelId}-night`);}await mobile.page.close();}
  const meta=metas.find(m=>m.uid==='landsd/145002:0'),failure=await pageFor(1440,meta);await visit(failure.page,meta,{allowFailure:true});const selectedBefore=await failure.page.evaluate(()=>({uid:window.__city.state.selectedId,label:document.getElementById('building-height-label').textContent,source:document.getElementById('building-source').textContent}));assert.equal(selectedBefore.uid,meta.uid);assert.notEqual(selectedBefore.label,'OUTLINE HEIGHT');failure.recover();await failure.page.locator('#stream-retry').click();await failure.page.waitForFunction(uid=>window.__modelReview.stream.detailedModels.get(uid)?.active&&document.getElementById('building-height-label').textContent==='OUTLINE HEIGHT',meta.uid,{timeout:120000});const selectedAfter=await failure.page.evaluate(()=>({uid:window.__city.state.selectedId,label:document.getElementById('building-height-label').textContent,source:document.getElementById('building-source').textContent}));assert.equal(selectedAfter.uid,meta.uid);assert.match(selectedAfter.source,/Official Lands Department non-textured/);report.selectedCardUpgrade={selectedBefore,selectedAfter,withoutAnotherSelection:true};await snap(failure.page,'selected-card-auto-upgrade');await failure.page.close();assert.deepEqual(report.errors,[]);report.result='passed';report.finishedUTC=new Date().toISOString();
 }else{
 const desktop=await pageFor();report.startupMs=desktop.startupMs;await time(desktop.page,'15:00');
 for(const meta of metas){if(report.visits.some(r=>r.uid===meta.uid))continue;const proof=await visit(desktop.page,meta);proof.label=meta.label;proof.pick=await pick(desktop.page,meta.uid);report.visits.push(proof);if(captured.has(meta.uid))await snap(desktop.page,'desktop-'+meta.modelId);await save();console.log(JSON.stringify({uid:meta.uid,label:meta.label,cached:proof.stats.cached,readyMs:Math.round(proof.readyMs)}));}
 const hsbc=metas.find(m=>m.uid==='landsd/89275:0');await visit(desktop.page,hsbc);await time(desktop.page,'21:00');await pick(desktop.page,hsbc.uid);await snap(desktop.page,'desktop-hsbc-night');report.desktopNight=await desktop.page.evaluate(()=>({lighting:window.__city.state.lighting,models:window.__city.state.models}));report.desktopPerformance=await measure(desktop.page);assert.ok(report.desktopNight.lighting.night>.5);await desktop.page.close();
 for(const width of [390,320]){
  const mobile=await pageFor(width),row={width,startupMs:mobile.startupMs,models:[]};await time(mobile.page,'21:00');
  for(const uid of ['landsd/89275:0','landsd/123884:0','landsd/124803:0','landsd/1307:0']){const meta=metas.find(m=>m.uid===uid),proof=await visit(mobile.page,meta);proof.pick=await pick(mobile.page,uid);assert.equal(proof.stats.profile,'mobile');assert.ok(proof.stats.cached<=proof.stats.limits.count);assert.ok(proof.stats.geometryBytes<=proof.stats.limits.geometryBytes);assert.ok(proof.stats.residentBytes<=proof.stats.limits.residentBytes);assert.ok(proof.stats.triangles<=proof.stats.limits.triangles);row.models.push(proof);if(uid==='landsd/89275:0'||uid==='landsd/1307:0')await snap(mobile.page,`mobile-${width}-${meta.modelId}-night`);}
  row.performance=await measure(mobile.page);assert.equal(await mobile.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await mobile.page.locator('#panel-toggle').click();await snap(mobile.page,`mobile-${width}-controls`);report.mobile.push(row);await mobile.page.close();await save();
 }
 const failed=metas.find(m=>m.uid==='landsd/145002:0'),failure=await pageFor(1440,failed);await visit(failure.page,failed,{allowFailure:true});report.failureFallback=await failure.page.evaluate(uid=>{const {stream,officialModels}=window.__modelReview;return {modelActive:stream.detailedModels.has(uid),fallbackHasModel:!!stream.getLoadedBuilding(uid).modelGeometry,errors:officialModels.stats.errors};},failed.uid);assert.equal(report.failureFallback.modelActive,false);assert.equal(report.failureFallback.fallbackHasModel,false);failure.recover();await failure.page.locator('#stream-retry').click();await failure.page.waitForFunction(uid=>window.__modelReview.stream.detailedModels.get(uid)?.active,failed.uid,{timeout:120000});await visit(failure.page,failed);report.failureFallback.retry=await pick(failure.page,failed.uid);await snap(failure.page,'failed-download-recovered');await failure.page.close();
 assert.deepEqual(report.errors,[]);report.result='passed';report.finishedUTC=new Date().toISOString();
 }
}catch(error){report.result='failed';report.failure=error.stack;const pages=browser.contexts().flatMap(c=>c.pages());if(pages.length)await snap(pages.at(-1),'acceptance-failure');throw error;}
finally{await save();await browser.close();}
