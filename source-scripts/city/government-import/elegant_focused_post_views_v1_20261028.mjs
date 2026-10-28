// V13: identical V12 checks; allow an explicitly configured loopback test origin.
// V12: retain V11 checks and stage exact source-bound BASIC protections without editing installed catalogues.
/** Scripted source-port runtime acceptance; no AI image/model review. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
function normaliseSourceForms(data){const rows=Array.isArray(data)?data:Object.entries(data).map(([uid,r])=>{assert(r?.building?.uid===uid,'Source-form dictionary key mismatch');return r.building;});assert(rows.every(r=>r&&typeof r.uid==='string'));assert.equal(new Set(rows.map(r=>r.uid)).size,rows.length);return rows;}
const mode=process.argv[2]||'staged';assert(['staged','live','preflight'].includes(mode));
const config=await read(process.argv[3]||'source-scripts/city/government-import/accepted/government-198-resolution-20260911/browser-config.json'),catalogue=await read(config.stage+'catalogue.json'),forms=normaliseSourceForms(await read(config.stage+'source-forms.json')),url=config.catalogueURL,assetBase=url.slice(0,url.lastIndexOf('/')+1),out=new URL(config.doc,root);if(mode!=='preflight')await mkdir(out,{recursive:true});
// A diagnostic overlay may nominate only exact new-original / current-compound pairs.
const protections=config.basicFallbackProtections||[];
const {prepareBasicFallbackProtections}=await import('../../../3d-viewer/city/basic-fallback-protections.js');
prepareBasicFallbackProtections(protections);
if(protections.length){
 const manifest=await read('3d-viewer/city/data/manifest.json'),current=[];
 for(const url of manifest.officialModelCatalogues||[])current.push(...(await read('3d-viewer/'+url)).models);
 for(const protection of protections){
  const targets=catalogue.models.filter(m=>m.uid===protection.uid),owners=current.filter(m=>m.uid===protection.suppressorUid);
  assert.equal(targets.length,1);assert.equal(owners.length,1);
  assert.equal(targets[0].sha256,protection.sourceSHA256);assert.equal(targets[0].buildingCSUID,protection.buildingCSUID);
  assert.equal(owners[0].sha256,protection.suppressorSourceSHA256);
  assert(owners[0].suppressesBuildingUids?.includes(protection.uid));
 }
}
const browserModels=config.browserUids?catalogue.models.filter(model=>config.browserUids.includes(model.uid)):catalogue.models;assert(browserModels.length>0&&(!config.browserUids||browserModels.length===config.browserUids.length));
// Exercise a source's download/retry after its candidate dependencies are ready.
const testByUid=new Map(browserModels.map(m=>[m.uid,m])),testOrdered=[],testDone=new Set(),testVisiting=new Set();
function dependencyFirst(model){if(testDone.has(model.uid))return;assert(!testVisiting.has(model.uid),'Candidate support dependency cycle');testVisiting.add(model.uid);for(const d of model.supportDependencies||[])if(testByUid.has(d.uid))dependencyFirst(testByUid.get(d.uid));testVisiting.delete(model.uid);testDone.add(model.uid);testOrdered.push(model);}
// Retained owners may now depend on a candidate too. Exercise those
// deliberately failed candidate supports before unrelated new sources, so
// the unchanged retained-visibility checks run only after their retry.
for(const uid of config.dependencyFallbackRetainedUids||[]){const update=(config.catalogueReplacements||[]).find(r=>r.ownerUid===uid);assert(update&&update.afterEntry,'Reviewed retained support update required');for(const d of update.afterEntry.supportDependencies||[])if(['candidate','installed'].includes(d.state)&&testByUid.has(d.uid))dependencyFirst(testByUid.get(d.uid));}
for(const model of browserModels)dependencyFirst(model);browserModels.splice(0,browserModels.length,...testOrdered);
if(mode==='preflight'){const expected=process.argv[4]?normaliseSourceForms(await read(process.argv[4])):forms;const sorted=rows=>[...rows].sort((a,b)=>a.uid.localeCompare(b.uid));assert.deepEqual(sorted(forms),sorted(expected),'Prepared forms differ from the browser-tested buildings');for(const m of catalogue.models){const b=forms.find(b=>b.uid===m.uid);assert(b);assert.equal(b.objectId,m.objectId);assert.equal(b.buildingCSUID,m.buildingCSUID);}console.log(JSON.stringify({sourceFormAdapterPassed:true,models:catalogue.models.length,dependencyFirstOrder:browserModels.map(m=>m.uid)}));process.exit(0);}
// Required retained sources use their real current catalogues. Waiting for the
// unrelated serial background inventory is not a source activation check.
const candidateUids=new Set(catalogue.models.map(m=>m.uid)),requiredUids=new Set([...Object.values(config.nativeSupportUidsByModel||{}).flat(),...(config.additionalRetainedUids||[])].filter(uid=>!candidateUids.has(uid))),requiredCatalogues=[];
if(requiredUids.size){const manifest=await read('3d-viewer/city/data/manifest.json');for(const url of manifest.officialModelCatalogues||[]){const data=await read('3d-viewer/'+url),matches=data.models.filter(m=>requiredUids.has(m.uid));if(matches.length)requiredCatalogues.push({url,models:matches.map(m=>({uid:m.uid,sha256:m.sha256,worldBounds:m.worldBounds,triangles:m.triangles}))});}for(const uid of requiredUids)assert.equal(requiredCatalogues.flatMap(c=>c.models).filter(m=>m.uid===uid).length,1,'Unique current retained native catalogue required: '+uid);}
const retainedForms=[];
if(requiredUids.size){const manifest=await read('3d-viewer/city/data/manifest.json');for(const expected of requiredCatalogues.flatMap(c=>c.models)){const [a,b]=expected.worldBounds,x=(a[0]+b[0])/2,z=(a[2]+b[2])/2;const matches=[];for(const tile of manifest.tiles){const [left,top,right,bottom]=tile.bounds;if(x<left||x>right||z<top||z>bottom)continue;matches.push(...(await read('3d-viewer/'+tile.url)).buildings.filter(b=>b.uid===expected.uid));}assert.equal(matches.length,1,'Exact retained navigation form required');retainedForms.push(matches[0]);}}
const report={mode,views:[],retainedNativeOwnViews:[],errors:[],aiCalls:0,architectureReview:false,nativeHTTPObservationTimeoutMs:120000,actorObservationTimeoutMs:120000},browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
assert(Array.isArray(config.viewportWidths)&&config.viewportWidths.length===1&&[1280,390].includes(config.viewportWidths[0]));
try{for(const width of config.viewportWidths){
 const context=await browser.newContext({viewport:{width,height:900},hasTouch:width<700}),page=await context.newPage(),allowed=new Set(),cdp=await context.newCDPSession(page);await cdp.send('Network.clearBrowserCache');page.on('console',m=>{if(m.text().startsWith('ILLUMINATION_DIAGNOSTIC '))console.log(m.text());});page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(/THREE.WebGLProgram|GL_INVALID|shader error/i.test(m.text()))report.errors.push(m.text());});
 page.on('request',r=>{if(requiredCatalogues.some(c=>r.url().includes(c.url.slice(0,c.url.lastIndexOf('/')+1))&&r.url().includes('/assets/'))){report.nativeAssetRequests??=[];report.nativeAssetRequests.push({url:r.url(),event:'requested'});console.log(mode,width,'retained asset requested');}});page.on('response',r=>{if(requiredCatalogues.some(c=>r.url().includes(c.url.slice(0,c.url.lastIndexOf('/')+1))&&r.url().includes('/assets/'))){report.nativeAssetRequests??=[];report.nativeAssetRequests.push({url:r.url(),event:'response',status:r.status()});console.log(mode,width,'retained asset response',r.status());}});
 await page.route('**/city/app.js*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__port",{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});window.__portOriginalRender=renderer.render.bind(renderer);renderer.render=()=>{};'});});
 for(const required of requiredCatalogues)for(const expected of required.models){const data=await read('3d-viewer/'+required.url),entry=data.models.find(m=>m.uid===expected.uid),assetURL=required.url.slice(0,required.url.lastIndexOf('/')+1)+entry.asset;await page.route('**/'+assetURL+'*',async route=>{const response=await route.fetch({timeout:120000});assert.equal(response.status(),200,'Current native source HTTP failure');const body=await response.body();assert.equal(body.length,entry.bytes,'Current native response byte count differs');assert.equal((await import('node:crypto')).createHash('sha256').update(body).digest('hex'),expected.sha256,'Current native response SHA differs');await route.fulfill({response,body});});}
 if(mode==='staged'){
  await page.route('**/'+url,r=>r.fulfill({json:catalogue}));
  for(const t of config.terrain)await page.route('**/'+t.destination,async r=>r.fulfill({body:await readFile(new URL(t.source,root))}));
  for(const replacement of config.catalogueReplacements||[])await page.route('**/'+replacement.url,async r=>r.fulfill({body:await readFile(new URL(replacement.source,root))}));
  await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json(),replaced=new Set(config.terrain.flatMap(t=>(t.replacesMany??(t.replaces?[t.replaces]:[])).map(r=>r.url)));m.officialModelCatalogues.push(url);if(protections.length){m.basicFallbackProtections=[...(m.basicFallbackProtections||[]),...protections];prepareBasicFallbackProtections(m.basicFallbackProtections);}m.terrainPatches=m.terrainPatches.filter(t=>!replaced.has(t.url));m.terrainPatches.push(...config.terrain.map(t=>({url:t.destination,resolution:t.resolution,area:t.area})));await r.fulfill({response,json:m});});
 }
 const routedModels=mode==='staged'?catalogue.models:browserModels;
 for(const model of routedModels)await page.route('**/'+assetBase+model.asset+'*',async r=>width===390&&(!config.failureTestUids||config.failureTestUids.includes(model.uid))&&!allowed.has(model.uid)?r.fulfill({status:503,body:'Intentional fallback test'}):mode==='staged'?r.fulfill({body:await readFile(new URL(config.stage+model.asset,root))}):r.continue());
 if(mode==='staged')for(const update of config.estimatedBaseUpdates||[])await page.route('**/'+update.tile,async route=>{const response=await route.fetch(),raw=await response.body();assert.equal((await import('node:crypto')).createHash('sha256').update(raw).digest('hex'),update.tileSHA256);const data=JSON.parse(raw),b=data.buildings.find(b=>b.uid===update.uid);assert(b);assert.equal(b.base,update.previousBase);assert.equal(b.height,update.height);assert.equal(b.objectId,update.objectId);assert.equal(b.buildingCSUID,update.buildingCSUID);assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.heightSource,'estimated');assert(b.baseHeightHKPD==null&&b.topHeightHKPD==null&&!b.modelGeometry);b.base=update.base;await route.fulfill({response,json:data});});
 // Private diagnostic only: immutable surveyed/source fields and exact whole-tile binding.
 if(config.privateFoundationTileOverlays?.length){
  assert.equal(mode,'staged');assert.equal(config.diagnosticOnly,true);assert.equal(config.publication,false);
  const seen=new Set();
  for(const overlay of config.privateFoundationTileOverlays){
   assert(overlay.url.startsWith('city/data/tiles/')&&!overlay.url.includes('..'));
   const original=await read('3d-viewer/'+overlay.url),expected=structuredClone(original);
   for(const change of overlay.changes){
    assert(!seen.has(change.uid));seen.add(change.uid);
    const b=expected.buildings.find(b=>b.uid===change.uid);assert.deepEqual(b,change.before);
    assert(!b.modelGeometry&&b.foundationBase==null&&b.foundationPolicy==null);
    assert(Number.isFinite(change.foundationBase)&&change.foundationBase<b.base-.02);
    assert.equal(change.proposalApproved,false);
    assert(change.role==='surveyed-solid-podium'||change.role==='existing-estimated-open-canopy');
    if(change.role==='surveyed-solid-podium'){assert.equal(b.structureType,'Podium');assert.equal(b.kind,'yes');assert.equal(b.minimum,0);assert.equal(b.baseSource,'landsd');assert.equal(b.heightSource,'landsd');assert.equal(b.base,b.baseHeightHKPD);assert.equal(b.base+b.height,b.topHeightHKPD);}
    else{assert.equal(b.structureType,'Open-sided Structure');assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.heightSource,'estimated');assert(b.baseHeightHKPD==null&&b.topHeightHKPD==null);}
    b.foundationBase=change.foundationBase;
   }
   const bytes=await readFile(new URL(overlay.source,root));
   assert.equal((await import('node:crypto')).createHash('sha256').update(bytes).digest('hex'),overlay.afterSHA256);
   assert.deepEqual(JSON.parse(bytes),expected,'Private overlay changed fields beyond foundationBase');
   await page.route('**/'+overlay.url,async route=>{const response=await route.fetch(),raw=await response.body();assert.equal((await import('node:crypto')).createHash('sha256').update(raw).digest('hex'),overlay.beforeSHA256,'Current tile changed before private overlay');assert.deepEqual(JSON.parse(raw),original);await route.fulfill({response,body:bytes});});
  }
  assert.equal(seen.size,3,'This diagnostic binds exactly three proposed BASIC foundations');
  report.privateFoundationTileOverlays={uids:[...seen],diagnosticOnly:true,publication:false};
 }
 console.log(mode,width,'initialising');const startupAt=Date.now();report.startupObservationBudgetMs=300000;report.retainedTravelObservationBudgetMs=180000;
 page.on('requestfailed',r=>{report.failedRequests??=[];report.failedRequests.push({url:r.url(),error:r.failure()?.errorText});});
 const viewerURL=config.viewerURL||'http://127.0.0.1:4176/city.html';const viewer=new URL(viewerURL);assert(viewer.protocol==='http:'&&viewer.hostname==='127.0.0.1'&&viewer.pathname==='/city.html'&&!viewer.username&&!viewer.password&&!viewer.search&&!viewer.hash);await page.goto(viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:300000});await page.locator('#loading').waitFor({state:'hidden',timeout:300000});report.startupElapsedMs=Date.now()-startupAt;
 // Infrastructure wait only: all original model, collision, fallback and framing assertions remain unchanged.

 console.log(mode,width,'map ready');await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),url);
 for(const required of requiredCatalogues){assert(await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),required.url),'Required native catalogue failed: '+required.url);for(const expected of required.models){assert.equal(await page.evaluate(uid=>window.__port.officialModels.models.get(uid)?.sha256,expected.uid),expected.sha256,'Current retained source metadata changed');await page.evaluate(async uid=>{const layer=window.__port.officialModels;await layer.byteCache.get(layer.models.get(uid));},expected.uid);console.log(mode,width,expected.uid,'retained original bytes cached');}}
 await page.evaluate(()=>{const r=window.__port.renderer;window.__portDraw=window.__portOriginalRender.bind(r);r.render=()=>{};});
 await page.evaluate(()=>{window.__portSolidWitness=uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid);let fallbackFaces=0;for(const e of r.stream.cache.entries.values())for(const mesh of e.buildings.group.children){if(!e.buildings.group.visible||!mesh.visible)continue;const f=mesh.geometry.attributes.feature,idx=mesh.geometry.index;if(!f)continue;for(let i=0;i<(idx?.count??f.count);i+=3){const vertex=idx?idx.getX(i):i;if(e.data.buildings[Math.round(f.getX(vertex))]?.uid===uid)fallbackFaces++;}}return{sourceSHA256:r.officialModels.models.get(uid).sha256,originalTriangles:d?.record?.modelGeometry?.index?.length/3||0,meshVisibility:(d?.meshes||[]).map(m=>m.visible),wireframeFlags:(d?.meshes||[]).flatMap(m=>(Array.isArray(m.material)?m.material:[m.material]).map(a=>a.wireframe===true)),fallbackFaces};};});
 async function retainedEligibility(){const out={};for(const uid of requiredUids){let state=await page.evaluate(async uid=>{const r=window.__port,m=r.officialModels.models.get(uid),d=r.stream.detailedModels.get(uid),box=new r.THREE.Box3(new r.THREE.Vector3(...m.worldBounds[0]),new r.THREE.Vector3(...m.worldBounds[1])),matrix=new r.THREE.Matrix4().multiplyMatrices(r.camera.projectionMatrix,r.camera.matrixWorldInverse),frustum=new r.THREE.Frustum().setFromProjectionMatrix(matrix),{projectedBounds}=await import('/city/model-spatial-index.js'),limits=r.officialModels.limits;return{wanted:r.officialModels.cache.wanted.includes(uid),active:!!d?.active,visible:!!d?.group?.visible,sourceSHA256:m.sha256,camera:r.camera.position.toArray(),wholeOriginalBounds:m.worldBounds,frustumEligible:frustum.intersectsBox(box),originalBoundsDistance:box.distanceToPoint(r.camera.position),projectedPixels:projectedBounds(box,matrix,innerWidth,innerHeight).pixels,detailDistance:limits.detailDistance,landmarkDistance:limits.landmarkDistance,minimumPixels:limits.minPixels,residentPixelThreshold:limits.minPixels*(d?.active?.65:1),currentWanted:[...r.officialModels.cache.wanted],limits:{count:limits.count,geometryBytes:limits.geometryBytes,residentBytes:limits.residentBytes,triangles:limits.triangles,drawCalls:limits.drawCalls}};},uid);if(state.wanted){await page.waitForFunction(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid);return !r.officialModels.cache.wanted.includes(uid)||(d?.active&&d.group.visible);},uid,{timeout:120000});state=await page.evaluate(({uid,state})=>{const r=window.__port,d=r.stream.detailedModels.get(uid);return{...state,active:!!d?.active,visible:!!d?.group?.visible,wanted:r.officialModels.cache.wanted.includes(uid),currentWanted:[...r.officialModels.cache.wanted]};},{uid,state});assert(!state.wanted||(state.active&&state.visible),'Currently wanted retained actor must remain active/visible');}const expected=requiredCatalogues.flatMap(c=>c.models).find(m=>m.uid===uid);assert.equal(state.sourceSHA256,expected.sha256);out[uid]=state;}return out;}

 report.postDiagnostics=[];
 for(const uid of ['landsd/99061:0','landsd/336456:0']){
  const owners=uid==='landsd/99061:0'?['landsd/236170:0']:['landsd/255231:0','landsd/257493:0'];
  for(const owner of owners){await page.evaluate(b=>window.__port.visitBuilding(b),forms.find(b=>b.uid===owner));await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});await page.waitForFunction(uid=>window.__port.stream.detailedModels.get(uid)?.active,owner,{timeout:120000});}
  const change=config.privateFoundationTileOverlays.flatMap(o=>o.changes).find(c=>c.uid===uid);assert(change);
  await page.evaluate(b=>window.__port.visitBuilding(b),change.before);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
  await page.waitForFunction(uid=>{const b=window.__port.stream.getLoadedBuilding(uid);return b&&!b.hidden&&Number.isFinite(b.foundationBase);},uid,{timeout:120000});
  const count=await page.evaluate(async uid=>{const {describeBuilding}=await import('/city/building-geometry.js');return describeBuilding(window.__port.stream.getLoadedBuilding(uid)).parts.filter(p=>p.kind==='post').length;},uid);
  assert.equal(count,uid==='landsd/99061:0'?2:4);
  for(let postIndex=0;postIndex<count;postIndex++){
   const result=await page.evaluate(async({uid,postIndex})=>{
    const r=window.__port,T=r.THREE,{describeBuilding}=await import('/city/building-geometry.js'),b=r.stream.getLoadedBuilding(uid),post=describeBuilding(b).parts.filter(p=>p.kind==='post')[postIndex];
    const [x0,z0,x1,z1]=post.bounds,bounds=new T.Box3(new T.Vector3(x0,b.foundationBase,z0),new T.Vector3(x1,b.base,z1)),center=bounds.getCenter(new T.Vector3());
    r.controls.enableDamping=false;r.scene.updateMatrixWorld(true);
    const points=[];for(const y of [.2,.5,.8])for(const x of [x0,(x0+x1)/2,x1])for(const z of [z0,(z0+z1)/2,z1])points.push(new T.Vector3(x,b.foundationBase+(b.base-b.foundationBase)*y,z));
    function firstHit(origin,direction){const ray=new T.Raycaster(origin,direction),hits=ray.intersectObjects(r.stream.pickMeshes(ray.ray),false),hit=hits.find(h=>h.object.visible!==false),ground=ray.intersectObject(r.terrain,true)[0];if(ground&&(!hit||ground.distance<hit.distance-.001))return{uid:'terrain',point:ground.point.toArray()};return hit?{uid:r.stream.featureAt(hit)?.uid??hit.object.userData.officialBuildingUid??null,point:hit.point.toArray()}:null;}
    const candidates=[];
    for(const elevation of [.05,.15,.35,.7])for(let step=0;step<24;step++){
     const a=step*Math.PI/12,dir=new T.Vector3(Math.sin(a),elevation,Math.cos(a)).normalize(),right=new T.Vector3().crossVectors(new T.Vector3(0,1,0),dir).normalize(),up=new T.Vector3().crossVectors(dir,right),tv=Math.tan(T.MathUtils.degToRad(r.camera.fov/2)),th=tv*r.camera.aspect;let distance=0;
     for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){const o=new T.Vector3(x,y,z).sub(center);distance=Math.max(distance,o.dot(dir)+Math.abs(o.dot(right))/th,o.dot(dir)+Math.abs(o.dot(up))/tv);}distance=Math.max(1.2,distance*1.3);
     const position=center.clone().addScaledVector(dir,distance),cameraCollision=r.stream.collision(position.x,position.z,position.y-.1,position.y+.1,.1)?.uid??null,ground=r.sampler.height(position.x,position.z),hits=points.map(q=>firstHit(position,q.clone().sub(position).normalize())),visible=hits.filter(h=>h?.uid===uid&&h.point[1]<b.base-.01).length,blockers={};for(const h of hits){const k=h?.uid??'no-hit';blockers[k]=(blockers[k]??0)+1;}
     candidates.push({azimuthDegrees:step*15,elevation,distance,position:position.toArray(),target:center.toArray(),cameraCollision,ground,aboveGround:position.y>ground+.1,visibleLowerSamples:visible,totalSamples:points.length,blockers});
    }
    const ranked=candidates.filter(c=>!c.cameraCollision&&c.aboveGround).sort((a,b)=>b.visibleLowerSamples-a.visibleLowerSamples||a.distance-b.distance);
    return{uid,postIndex,post,base:b.base,foundationBase:b.foundationBase,candidates,best:ranked[0]??null};
   },{uid,postIndex});
   if(result.best){
    await page.evaluate(best=>{const r=window.__port;r.camera.position.fromArray(best.position);r.controls.target.fromArray(best.target);r.controls.update();r.camera.updateMatrixWorld(true);},result.best);
    for(const time of ['15:00','22:00']){await page.evaluate(t=>{const e=document.getElementById('time');e.value=t;e.dispatchEvent(new Event('input',{bubbles:true}));},time);await page.waitForTimeout(1000);
     const state=await page.evaluate(({uid,owners})=>{const r=window.__port;r.closeSelection();document.getElementById('building-card').hidden=true;r.controlSheet?.close({restoreFocus:false});r.camera.updateMatrixWorld(true);window.__portDraw(r.scene,r.camera);return{canvasPNG:r.renderer.domElement.toDataURL('image/png'),selectionClosed:!window.__city.state.selectedId,sourceOwners:owners.map(u=>({uid:u,active:!!r.stream.detailedModels.get(u)?.active,sha256:r.officialModels.models.get(u)?.sha256})),basicHidden:r.stream.getLoadedBuilding(uid)?.hidden,activeContext:[...r.stream.detailedModels].filter(([u,d])=>d.active&&d.group.visible).map(([u,d])=>({uid:u,sha256:r.officialModels.models.get(u)?.sha256}))};},{uid,owners});
     const file=`post-${uid.replaceAll('/','-').replaceAll(':','-')}-${postIndex}-${width}-${time.replace(':','')}.png`;await writeFile(new URL(file,out),Buffer.from(state.canvasPNG.split(',')[1],'base64'));delete state.canvasPNG;result.exports??=[];result.exports.push({time,file,...state});
    }
   }
   report.postDiagnostics.push(result);console.log('POST_DIAGNOSTIC',uid,postIndex,JSON.stringify({best:result.best}));
  }
 }
 report.diagnosticOnly=true;report.visualReviewApproved=false;report.installationApproved=false;await context.close();
 }assert.deepEqual(report.errors,[]);report.passed=true;}catch(error){report.errors.push(error.message);throw error;}finally{await browser.close();await writeFile(new URL(mode+'-browser.json',out),JSON.stringify(report,null,2)+'\n');}
