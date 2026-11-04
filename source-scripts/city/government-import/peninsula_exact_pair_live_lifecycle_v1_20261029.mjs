/** Actual installed HTTP lifecycle diagnostic; no catalogue/terrain substitution. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const config=await read(process.argv[2]),out=new URL(process.argv[3]+'/',root),catalogue=await read(config.stage+'catalogue.json'),rawForms=await read(config.stage+'source-forms.json'),forms=Array.isArray(rawForms)?rawForms:Object.values(rawForms).map(r=>r.building),uids=catalogue.models.map(m=>m.uid).sort();
const owner=catalogue.models.find(m=>m.uid==='landsd/270876:0');assert(owner&&config.expectedCanopyUid==='way/709674357:0');assert.equal(owner.sha256,'3a40860e5302240d814f907d2f1edabc4b3c7becab1c90d37f406d2a4ce631f2');
assert(config.liveInstalled===true&&config.diagnosticOnly&&config.publication===false&&uids.length>1);assert(catalogue.models.every(m=>JSON.stringify([...m.activationGroup].sort())===JSON.stringify(uids)));
await mkdir(out,{recursive:true});
const report={diagnosticOnly:true,liveInstalledHTTP:true,catalogueAndTerrainSubstitution:false,physicalAcceptance:false,installationApproved:false,publication:false,cases:[],pageErrors:[],performanceAcceptance:false};
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const width of [1280,390])for(const failedUid of width===390?uids:[null]){
  const name=width+'-'+(failedUid?.replaceAll('/','-').replaceAll(':','-')||'success'),context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage();let denied=failedUid;
  page.on('pageerror',e=>report.pageErrors.push({case:name,message:e.message}));
  await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+`\nObject.defineProperty(window,'__port',{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,THREE,visitBuilding,closeSelection})});window.__groupAudit={uids:${JSON.stringify(uids)},frames:0,transitions:[],violations:[]};window.__groupDraw=renderer.render.bind(renderer);renderer.render=()=>{const r=window.__port,a=window.__groupAudit;if(!r.stream?.detailedModels)return;a.frames++;const active=a.uids.filter(uid=>r.stream.detailedModels.get(uid)?.active);const key=active.join('|');if(a.last!==key){a.last=key;a.transitions.push({frame:a.frames,active});}if(active.length&&active.length!==a.uids.length&&a.violations.length<10)a.violations.push({kind:'partial-native-group',active});if(active.length===a.uids.length){for(const e of r.stream.cache.entries.values())for(const b of e.data.buildings)if(a.uids.includes(b.uid)&&e.models?.get(b.uid)!==r.stream.detailedModels.get(b.uid)&&a.violations.length<10)a.violations.push({kind:'stale-fallback-collision-map',uid:b.uid});}};`});});
  const url=config.catalogueURL,assetBase=url.slice(0,url.lastIndexOf('/')+1);
  const origin=new URL(config.viewerURL).origin;
  const manifestResponse=await page.request.get(origin+'/city/data/manifest.json');assert(manifestResponse.ok());const installedManifest=await manifestResponse.json();assert.deepEqual(installedManifest,await read('3d-viewer/city/data/manifest.json'));assert.equal(installedManifest.officialModelCatalogues.filter(u=>u===url).length,1);
  const catResponse=await page.request.get(origin+'/'+url);assert(catResponse.ok());assert.deepEqual(await catResponse.json(),catalogue);
  for(const terrain of config.terrain){assert.equal(installedManifest.terrainPatches.filter(t=>t.url===terrain.destination).length,1);assert(!installedManifest.terrainPatches.some(t=>t.url===terrain.replaces.url));const response=await page.request.get(origin+'/'+terrain.destination);assert(response.ok());assert.equal(createHash('sha256').update(await response.body()).digest('hex'),terrain.sha256);}
  for(const model of catalogue.models){const bytes=await readFile(new URL(config.stage+model.asset,root));assert.equal(bytes.length,model.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),model.sha256);const response=await page.request.get(origin+'/'+assetBase+model.asset);assert(response.ok());assert.equal(createHash('sha256').update(await response.body()).digest('hex'),model.sha256);await page.route('**/'+assetBase+model.asset+'*',r=>model.uid===denied?r.fulfill({status:503,body:'Intentional installed group peer failure'}):r.continue());}
  console.log(name,'initialising');await page.goto(config.viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:300000});
  assert(await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),url));
  const form=forms.find(b=>b.uid===uids[0]);assert(form);await page.evaluate(form=>window.__port.visitBuilding(form),form);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
  await page.evaluate(bounds=>{const r=window.__port,lo=bounds[0],hi=bounds[1],centre=new r.THREE.Vector3(...lo).add(new r.THREE.Vector3(...hi)).multiplyScalar(.5),radius=new r.THREE.Vector3(...hi).distanceTo(new r.THREE.Vector3(...lo))/2,half=Math.min(r.THREE.MathUtils.degToRad(r.camera.fov/2),Math.atan(Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2))*r.camera.aspect)),distance=radius/Math.sin(half)*1.15;r.controls.enableDamping=false;r.camera.position.copy(centre).addScaledVector(new r.THREE.Vector3(-1,1.6,1).normalize(),distance);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);},[0,1].map(side=>[0,1,2].map(axis=>(side?Math.max:Math.min)(...catalogue.models.map(m=>m.worldBounds[side][axis])))));
  await page.waitForFunction(()=>{const c=window.__port.stream.cache;return !c.running.size&&c.wanted.every(id=>c.entries.has(id));},null,{timeout:300000});
  await page.evaluate(uid=>{const r=window.__port;r.officialModels.setLoadingPaused(false);r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},uids[0]);
  const result={name,width,failedUid,failureKeptAllBasics:false};
  async function canopyState(active,phase){
   const args={ownerUid:owner.uid,canopyUid:config.expectedCanopyUid,active};
   await page.waitForFunction(({ownerUid,canopyUid,active})=>{
    const r=window.__port,e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===canopyUid));if(!e)return false;
    const i=e.data.buildings.findIndex(b=>b.uid===canopyUid);
    const visible=(e.buildings?.group?.children||[]).some(m=>{const f=m.geometry?.attributes.feature;return f&&Array.from(f.array).includes(i);});
    return Boolean(r.stream.detailedModels.get(ownerUid)?.active)===active&&visible===!active;
   },args,{timeout:120000});
   result.canopyLifecycle??=[];result.canopyLifecycle.push({phase,ownerActive:active,basicCanopyVisible:!active});
  }
  if(failedUid){
   await page.waitForFunction(({uids,failedUid})=>{const r=window.__port;return r.officialModels.cache.errors.has(failedUid)&&uids.every(uid=>!r.stream.detailedModels.get(uid)?.active);},{uids,failedUid},{timeout:120000});
   result.failureKeptAllBasics=await page.evaluate(uids=>{const r=window.__port;return uids.every(uid=>{const e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)return false;const i=e.data.buildings.findIndex(b=>b.uid===uid);return e.buildings.group.children.some(m=>{const f=m.geometry?.attributes.feature;return f&&Array.from(f.array).includes(i);});});},uids);assert(result.failureKeptAllBasics);
   await canopyState(false,'failed-download');
   denied=null;await page.evaluate(()=>window.__port.officialModels.retry());
  }
  await page.waitForFunction(uids=>uids.every(uid=>window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});
  await canopyState(true,'original-active');
  result.sources=await page.evaluate(uids=>uids.map(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid);return{uid,sha256:r.officialModels.models.get(uid).sha256,triangles:d.record.modelGeometry.index.length/3,active:d.active};}),uids);
  for(const source of result.sources){const model=catalogue.models.find(m=>m.uid===source.uid);assert.equal(source.sha256,model.sha256);assert.equal(source.triangles,model.triangles);}
  await page.evaluate(()=>window.__port.officialModels.setQuality('base'));await page.waitForFunction(uids=>uids.every(uid=>!window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});result.baseOnlyRestoredCompleteGroup=true;await canopyState(false,'base-only');
  await page.evaluate(uid=>{const r=window.__port;r.officialModels.setQuality('auto');r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},uids[0]);await page.waitForFunction(uids=>uids.every(uid=>window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});
  await canopyState(true,'auto-restored');
  await page.evaluate(()=>{const r=window.__port;window.__groupDraw(r.scene,r.camera);});await page.locator('canvas').first().screenshot({path:new URL(name+'.png',out).pathname});
  await page.evaluate(()=>{const r=window.__port;r.closeSelection();r.officialModels.warmMs=0;r.camera.position.set(50000,1000,50000);r.controls.target.set(60000,1000,50000);r.controls.update();r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:null,force:true,allowNewLoads:true});});await page.waitForFunction(uids=>uids.every(uid=>!window.__port.stream.detailedModels.get(uid)?.active),uids,{timeout:120000});result.completeGroupEvicted=true;result.testWarmRetentionDisabledForEviction=true;
  await page.evaluate(form=>{const r=window.__port;r.officialModels.setQuality('base');r.visitBuilding(form);},form);
  await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
  await canopyState(false,'evicted-return-base-only');
  result.audit=await page.evaluate(()=>window.__groupAudit);assert(result.audit.frames>0);assert.deepEqual(result.audit.violations,[]);assert(result.audit.transitions.some(r=>r.active.length===uids.length));assert.equal(result.audit.transitions.at(-1).active.length,0);
  report.cases.push(result);await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await context.close();console.log(name,'passed');
 }
 assert.deepEqual(report.pageErrors,[]);report.passed=true;
}catch(error){report.error=error.stack;throw error;}finally{await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await browser.close();}
