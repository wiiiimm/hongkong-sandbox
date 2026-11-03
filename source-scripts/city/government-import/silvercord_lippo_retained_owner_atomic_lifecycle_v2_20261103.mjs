/** Private software diagnostic: exact original assets, no model/publication approval. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {bindProductionSourceBoundTileRoutes} from './qualified_source_bound_tile_routes_v1_20261029.mjs';
import {originalGroupFallbackChecks as sourceBoundFallbackChecks} from './original_foundation_group_lifecycle_checks_v1_20261102.mjs';
import {verifyDesktopCase} from './original_atomic_desktop_case_reuse_v1_20261103.mjs';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const config=await read(process.argv[2]),out=new URL(process.argv[3]+'/',root),catalogue=await read(config.stage+'catalogue.json'),rawForms=await read(config.stage+'source-forms.json'),forms=Array.isArray(rawForms)?rawForms:Object.values(rawForms).map(r=>r.building),uids=catalogue.models.map(m=>m.uid).sort();
assert(config.diagnosticOnly&&config.publication===false&&uids.length>1);assert(catalogue.models.every(m=>JSON.stringify([...m.activationGroup].sort())===JSON.stringify(uids)));
await mkdir(out,{recursive:true});
const report={diagnosticOnly:true,physicalAcceptance:false,installationApproved:false,publication:false,cases:[],pageErrors:[],performanceAcceptance:false};
const reuse=config.reuseSuccessfulAtomic;
assert(reuse);
const readPinned=async ref=>{const raw=await readFile(new URL(ref.path,root));assert.equal(createHash('sha256').update(raw).digest('hex'),ref.sha256);return raw;};
const priorConfig=JSON.parse(await readPinned(reuse.config)),currentConfig=structuredClone(config);delete currentConfig.reuseSuccessfulAtomic;assert.deepEqual(currentConfig,priorConfig);
const previous=JSON.parse(await readPinned(reuse.report));
report.cases.push(verifyDesktopCase(previous,catalogue,config.catalogueReplacements[0].afterEntry));
for(const image of reuse.images)await writeFile(new URL(image.filename,out),await readPinned(image));
report.reusedDesktopCases=[{report:reuse.report,config:reuse.config,images:reuse.images,qualification:'One completed desktop case only; the failed overall run is not accepted. Exact sources, owner, production configuration and geometry hashes match.'}];
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const width of [390])for(const failedUid of uids){
  const name=width+'-'+(failedUid?.replaceAll('/','-').replaceAll(':','-')||'success'),context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage();let denied=failedUid;
  page.on('pageerror',e=>report.pageErrors.push({case:name,message:e.message}));
  await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+`\nObject.defineProperty(window,'__port',{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,THREE,visitBuilding,closeSelection})});window.__groupAudit={uids:${JSON.stringify(uids)},frames:0,transitions:[],violations:[]};window.__groupDraw=renderer.render.bind(renderer);renderer.render=()=>{const r=window.__port,a=window.__groupAudit;if(!r.stream?.detailedModels)return;a.frames++;const active=a.uids.filter(uid=>r.stream.detailedModels.get(uid)?.active);const key=active.join('|');if(a.last!==key){a.last=key;a.transitions.push({frame:a.frames,active});}if(active.length&&active.length!==a.uids.length&&a.violations.length<10)a.violations.push({kind:'partial-native-group',active});if(active.length===a.uids.length){for(const e of r.stream.cache.entries.values())for(const b of e.data.buildings)if(a.uids.includes(b.uid)&&e.models?.get(b.uid)!==r.stream.detailedModels.get(b.uid)&&a.violations.length<10)a.violations.push({kind:'stale-fallback-collision-map',uid:b.uid});}};`});});
  const url=config.catalogueURL,assetBase=url.slice(0,url.lastIndexOf('/')+1);
  // No source-bound continuation is proposed. Verify actual production modules
  // over HTTP without invoking the separate four-proposal Sha Tin route.
  assert.deepEqual(config.privateSourceBoundTileOverlays,[]);assert(Object.keys(config.productionGeometryInputHashes).length>0);
  for(const [url,expected]of Object.entries(config.productionGeometryInputHashes)){
   assert(url.startsWith('city/')&&!url.includes('..'));const bytes=await readFile(new URL('3d-viewer/'+url,root));assert.equal(createHash('sha256').update(bytes).digest('hex'),expected);
   const response=await page.request.get(new URL(url,new URL(config.viewerURL).origin+'/').href);assert(response.ok());assert.equal(createHash('sha256').update(await response.body()).digest('hex'),expected);
  }
  report.actualProductionGeometryHTTPVerified=true;report.moduleSubstitution=false;
  await (await import('./private_foundation_tile_routes_v1_20261102.mjs')).bindPrivateFoundationTileRoutes(page,config,'staged');
  for(const overlay of config.availabilityOverlays||[]){
   const contents=await read(overlay.source),before=await read('3d-viewer/'+overlay.url),expected=structuredClone(before),entry=expected.models.find(m=>m.uid===overlay.uid);
   assert(entry);entry.activationGroup=uids;assert.deepEqual(contents,expected);
   assert.equal(overlay.url.slice(0,overlay.url.lastIndexOf('/')),overlay.destination.slice(0,overlay.destination.lastIndexOf('/')));
   for(const alias of [overlay.url,overlay.destination])await page.route('**/'+alias,r=>r.fulfill({json:contents}));
   const model=contents.models.find(m=>m.uid===overlay.uid),bytes=await readFile(new URL('3d-viewer/'+overlay.url.slice(0,overlay.url.lastIndexOf('/')+1)+model.asset,root));
   assert.equal(createHash('sha256').update(bytes).digest('hex'),model.sha256);
   await page.route('**/'+overlay.url.slice(0,overlay.url.lastIndexOf('/')+1)+model.asset+'*',r=>model.uid===denied?r.fulfill({status:503,body:'Intentional existing peer failure'}):r.fulfill({body:bytes}));
  }
  assert.equal(config.catalogueReplacements.length,1);
  for(const update of config.catalogueReplacements){
   const oldRaw=await readFile(new URL('3d-viewer/'+update.url,root)),afterRaw=await readFile(new URL(update.source,root));
   assert.equal(createHash('sha256').update(oldRaw).digest('hex'),update.beforeSHA256);assert.equal(createHash('sha256').update(afterRaw).digest('hex'),update.sha256);
   const before=JSON.parse(oldRaw),after=JSON.parse(afterRaw),expected=structuredClone(before),owner=expected.models.find(m=>m.uid===update.ownerUid);
   assert.deepEqual(update.changedFields,['supportDependencies']);assert.deepEqual(owner,update.beforeEntry);owner.supportDependencies=update.afterEntry.supportDependencies;assert.deepEqual(owner,update.afterEntry);assert.deepEqual(expected,after);
   assert(owner.supportDependencies.every(d=>uids.includes(d.uid)&&d.state==='installed'&&catalogue.models.find(m=>m.uid===d.uid).sha256===d.sha256));
   await page.route('**/'+update.url,route=>route.fulfill({body:afterRaw}));
  }
  async function retainedOwnerPhase(active){
   const expected=config.catalogueReplacements[0].afterEntry,uid=expected.uid;
   if(active)await page.evaluate(uid=>{const r=window.__port;r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},uid);
   await page.waitForFunction(({uid,active})=>!!window.__port.stream.detailedModels.get(uid)?.active===active,{uid,active},{timeout:120000});
   const state=await page.evaluate(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid),e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)throw new Error('Missing retained owner tile');const at=e.data.buildings.findIndex(b=>b.uid===uid),i=e.index.buildings.findIndex(b=>b.uid===uid);let faces=0;for(const mesh of e.buildings.group.children){const f=mesh.geometry?.attributes.feature;if(f)for(const v of f.array)if(v===at)faces++;}return {uid,active:!!d?.active,sourceSHA256:r.officialModels.models.get(uid).sha256,originalTriangles:d?.record?.modelGeometry?.index?.length/3||0,basicFaces:faces,collisionKinds:i<0?[]:e.index.volumes[i].map(v=>v.kind)};},uid);
   assert.equal(state.sourceSHA256,expected.sha256);assert.equal(state.active,active);assert.equal(state.basicFaces>0,!active);assert.equal(state.collisionKinds.includes('model-surface'),active);if(active)assert.equal(state.originalTriangles,expected.triangles);
   return state;
  }
  await page.route('**/'+url,r=>r.fulfill({json:catalogue}));
  for(const model of catalogue.models){const bytes=await readFile(new URL(config.stage+model.asset,root));assert.equal(bytes.length,model.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),model.sha256);await page.route('**/'+assetBase+model.asset+'*',r=>model.uid===denied?r.fulfill({status:503,body:'Intentional group peer failure'}):r.fulfill({body:bytes}));}
  for(const t of config.terrain)await page.route('**/'+t.destination,async r=>r.fulfill({body:await readFile(new URL(t.source,root))}));
  await page.route('**/city/data/manifest.json',async route=>{const response=await route.fetch(),m=await response.json(),replaced=new Set(config.terrain.flatMap(t=>(t.replacesMany??(t.replaces?[t.replaces]:[])).map(r=>r.url)));for(const overlay of config.availabilityOverlays||[]){assert.equal(m.officialModelCatalogues.filter(u=>u===overlay.url).length,1);m.officialModelCatalogues=m.officialModelCatalogues.map(u=>u===overlay.url?overlay.destination:u);}m.officialModelCatalogues.push(url);m.terrainPatches=m.terrainPatches.filter(t=>!replaced.has(t.url));m.terrainPatches.push(...config.terrain.map(t=>({url:t.destination,resolution:t.resolution,area:t.area})));await route.fulfill({response,json:m});});
  console.log(name,'initialising');await page.goto(config.viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:300000});
  assert(await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),url));
  // Explicitly load the exact current owner metadata before observing fallback.
  // Readiness was already established this way by the success-view harness.
  for(const update of config.catalogueReplacements){
   assert(await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),update.url));
   const actual=await page.evaluate(uid=>{const m=window.__port.officialModels.models.get(uid);return {sha256:m?.sha256,supportDependencies:m?.supportDependencies};},update.ownerUid);
   assert.equal(actual.sha256,update.ownerSHA256);assert.deepEqual(actual.supportDependencies,update.afterEntry.supportDependencies);
  }

  const form=forms.find(b=>b.uid===uids[0]);assert(form);await page.evaluate(form=>window.__port.visitBuilding(form),form);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
  await page.evaluate(bounds=>{const r=window.__port,lo=bounds[0],hi=bounds[1],centre=new r.THREE.Vector3(...lo).add(new r.THREE.Vector3(...hi)).multiplyScalar(.5),radius=new r.THREE.Vector3(...hi).distanceTo(new r.THREE.Vector3(...lo))/2,half=Math.min(r.THREE.MathUtils.degToRad(r.camera.fov/2),Math.atan(Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2))*r.camera.aspect)),distance=radius/Math.sin(half)*1.15;r.controls.enableDamping=false;r.camera.position.copy(centre).addScaledVector(new r.THREE.Vector3(-1,1.6,1).normalize(),distance);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);},[0,1].map(side=>[0,1,2].map(axis=>(side?Math.max:Math.min)(...catalogue.models.map(m=>m.worldBounds[side][axis])))));
  await page.waitForFunction(()=>{const c=window.__port.stream.cache;return !c.running.size&&c.wanted.every(id=>c.entries.has(id));},null,{timeout:300000});
  await page.evaluate(uid=>{const r=window.__port;r.officialModels.setLoadingPaused(false);r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},uids[0]);
  const result={name,width,failedUid,failureKeptAllBasics:false};
  if(failedUid){
   await page.waitForFunction(({uids,failedUid})=>{const r=window.__port;return r.officialModels.cache.errors.has(failedUid)&&uids.every(uid=>!r.stream.detailedModels.get(uid)?.active);},{uids,failedUid},{timeout:120000});
   result.failureKeptAllBasics=await page.evaluate(uids=>{const r=window.__port;return uids.every(uid=>{const e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)return false;const i=e.data.buildings.findIndex(b=>b.uid===uid);return e.buildings.group.children.some(m=>{const f=m.geometry?.attributes.feature;return f&&Array.from(f.array).includes(i);});});},uids);assert(result.failureKeptAllBasics);
   result.failedFallback=await sourceBoundFallbackChecks(page,false,catalogue,config);
   result.retainedOwnerFailedFallback=await retainedOwnerPhase(false);
   await page.evaluate(()=>{const r=window.__port;window.__groupDraw(r.scene,r.camera);});await page.locator('canvas').first().screenshot({path:new URL(name+'-failed-basic.png',out).pathname});
   denied=null;await page.evaluate(()=>window.__port.officialModels.retry());
  }
  await page.waitForFunction(uids=>uids.every(uid=>window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});
  result.sources=await page.evaluate(uids=>uids.map(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid);return{uid,sha256:r.officialModels.models.get(uid).sha256,triangles:d.record.modelGeometry.index.length/3,active:d.active};}),uids);
  result.activeFallback=await sourceBoundFallbackChecks(page,true,catalogue,config);
  result.retainedOwnerActive=await retainedOwnerPhase(true);
  for(const source of result.sources){const model=catalogue.models.find(m=>m.uid===source.uid);assert.equal(source.sha256,model.sha256);assert.equal(source.triangles,model.triangles);}
  await page.evaluate(()=>window.__port.officialModels.setQuality('base'));await page.waitForFunction(uids=>uids.every(uid=>!window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});result.baseOnlyRestoredCompleteGroup=true;
  result.baseFallback=await sourceBoundFallbackChecks(page,false,catalogue,config);
  result.retainedOwnerBaseFallback=await retainedOwnerPhase(false);
  await page.evaluate(()=>{const r=window.__port;window.__groupDraw(r.scene,r.camera);});await page.locator('canvas').first().screenshot({path:new URL(name+'-base-only.png',out).pathname});
  await page.evaluate(uid=>{const r=window.__port;r.officialModels.setQuality('auto');r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},uids[0]);await page.waitForFunction(uids=>uids.every(uid=>window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});
  await page.evaluate(()=>{const r=window.__port;window.__groupDraw(r.scene,r.camera);});await page.locator('canvas').first().screenshot({path:new URL(name+'.png',out).pathname});
  result.recoveredFallback=await sourceBoundFallbackChecks(page,true,catalogue,config);
  result.retainedOwnerRecovered=await retainedOwnerPhase(true);
  await page.evaluate(()=>{const r=window.__port;r.closeSelection();r.officialModels.warmMs=0;r.camera.position.set(50000,1000,50000);r.controls.target.set(60000,1000,50000);r.controls.update();r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:null,force:true,allowNewLoads:true});});await page.waitForFunction(uids=>uids.every(uid=>!window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});result.completeGroupEvicted=true;result.testWarmRetentionDisabledForEviction=true;
  result.evictedFallback=await sourceBoundFallbackChecks(page,false,catalogue,config);
  result.retainedOwnerEvictedFallback=await retainedOwnerPhase(false);
  result.audit=await page.evaluate(()=>window.__groupAudit);assert(result.audit.frames>0);assert.deepEqual(result.audit.violations,[]);assert(result.audit.transitions.some(r=>r.active.length===uids.length));assert.equal(result.audit.transitions.at(-1).active.length,0);
  report.cases.push(result);await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await context.close();console.log(name,'passed');
 }
 assert.deepEqual(report.pageErrors,[]);report.passed=true;
}catch(error){report.error=error.stack;throw error;}finally{await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await browser.close();}
