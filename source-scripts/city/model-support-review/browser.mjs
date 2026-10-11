/** Actual streamed native tower/podium failure, retry and retirement proof. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const out=new URL('docs/astra-city/model-support-review/',root);await mkdir(out,{recursive:true});
const tower='landsd/136500:0',podium='landsd/114461:0',manifest=await read('3d-viewer/city/data/manifest.json'),models=new Map();
for(const url of manifest.officialModelCatalogues)for(const model of(await read('3d-viewer/'+url)).models)models.set(model.uid,{...model,url});
assert(models.get(tower).supportDependencies.some(d=>d.uid===podium));
let record;for(const tile of manifest.tiles){const b=models.get(tower).worldBounds;if(tile.bounds[0]>b[1][0]||tile.bounds[2]<b[0][0]||tile.bounds[1]>b[1][2]||tile.bounds[3]<b[0][2])continue;record=(await read('3d-viewer/'+tile.url)).buildings.find(b=>b.uid===tower);if(record)break;}assert(record);
const files=['3d-viewer/city/official-models.js','3d-viewer/city/model-support.js','3d-viewer/city/streaming.js','3d-viewer/city/data/manifest.json'];
const hash=async p=>createHash('sha256').update(await readFile(new URL(p,root))).digest('hex');
const report={started:new Date().toISOString(),tower,podium,views:[],errors:[],runtimeHashes:Object.fromEntries(await Promise.all(files.map(async p=>[p,await hash(p)]))),productionPublished:false};
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const mobile of [false,true]){
  const page=await browser.newPage({viewport:mobile?{width:390,height:844}:{width:1280,height:900},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:1});let fail=true;
  page.on('pageerror',error=>report.errors.push(error.message));
  await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__supportReview",{get:()=>({officialModels,stream,camera,controls,THREE,visitBuilding,closeSelection,controlSheet})});'});});
  const assetURL=models.get(podium).url.replace(/[^/]+$/,models.get(podium).asset);
  await page.route('**/'+assetURL,route=>fail?route.fulfill({status:503,body:'Expected support failure for private review'}):route.continue());
  await page.goto('http://127.0.0.1:4176/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});
  await page.evaluate(({tower,podium})=>{
   const r=window.__supportReview,replace=r.stream.setDetailedModel.bind(r.stream);window.__supportEvents=[];
   r.stream.setDetailedModel=async(uid,value,options)=>{
    if([tower,podium].includes(uid))window.__supportEvents.push({uid,action:value?'attach-start':'retire-start',towerActive:!!r.stream.detailedModels.get(tower)?.active,podiumActive:!!r.stream.detailedModels.get(podium)?.active});
    return replace(uid,value,options);
   };
  },{tower,podium});
  await page.evaluate(b=>window.__supportReview.visitBuilding(b),record);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
  await page.evaluate(({bounds,tower})=>{const r=window.__supportReview,a=new r.THREE.Vector3(...bounds[0]),b=new r.THREE.Vector3(...bounds[1]),centre=a.clone().add(b).multiplyScalar(.5),radius=a.distanceTo(b)/2,angle=Math.min(r.THREE.MathUtils.degToRad(r.camera.getEffectiveFOV()/2),Math.atan(Math.tan(r.THREE.MathUtils.degToRad(r.camera.getEffectiveFOV()/2))*r.camera.aspect)),distance=radius/Math.sin(angle)*1.25;r.closeSelection();r.controlSheet.close({restoreFocus:false});r.camera.position.copy(centre).addScaledVector(new r.THREE.Vector3(.7,.65,1).normalize(),distance);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);r.officialModels.plan(r.camera,{selectedUid:tower,force:true});},{bounds:models.get(tower).worldBounds,tower});
  await page.waitForFunction(podium=>window.__supportReview.officialModels.cache.errors.has(podium),podium,{timeout:90000});
  const failed=await page.evaluate(({tower,podium})=>{const r=window.__supportReview;return {towerActive:!!r.stream.detailedModels.get(tower)?.active,podiumActive:!!r.stream.detailedModels.get(podium)?.active,towerFallback:!!r.stream.getLoadedBuilding(tower)&&!r.stream.getLoadedBuilding(tower).modelGeometry,errors:[...r.officialModels.cache.errors.keys()]};},{tower,podium});
  assert(!failed.towerActive&&!failed.podiumActive&&failed.towerFallback);
  fail=false;await page.evaluate(()=>window.__supportReview.officialModels.retry());await page.waitForFunction(({tower,podium})=>{const r=window.__supportReview;return r.stream.detailedModels.get(tower)?.active&&r.stream.detailedModels.get(podium)?.active;},{tower,podium},{timeout:90000});
  await page.addStyleTag({content:'#location-title,.minimap,#labels{display:none!important}'});await page.waitForTimeout(600);
  const active=await page.evaluate(({tower,podium})=>{const r=window.__supportReview;return {models:[tower,podium].map(uid=>({uid,active:r.stream.detailedModels.get(uid)?.active,visible:r.stream.detailedModels.get(uid)?.group.visible})),stats:r.officialModels.stats,uiOverflow:document.documentElement.scrollWidth>innerWidth,events:window.__supportEvents};},{tower,podium});
  assert(active.models.every(m=>m.active&&m.visible));assert(!active.uiOverflow);for(const key of ['geometryBytes','residentBytes','triangles'])assert(active.stats[key]<=active.stats.limits[key]);
  assert(active.events.filter(e=>e.uid===tower&&e.action==='attach-start').every(e=>e.podiumActive));
  const file=(mobile?'mobile':'desktop')+'-native-support-after-retry.jpg';await page.screenshot({path:new URL(file,out).pathname,type:'jpeg',quality:85});
  await page.evaluate(()=>{const r=window.__supportReview;r.camera.position.set(50000,500,50000);r.controls.target.set(50000,0,49000);r.controls.update();r.camera.updateMatrixWorld(true);r.officialModels.plan(r.camera,{force:true});});
  await page.waitForFunction(({tower,podium})=>{const r=window.__supportReview;return !r.stream.detailedModels.has(tower)&&!r.stream.detailedModels.has(podium)&&r.officialModels.retiring.size===0;},{tower,podium},{timeout:90000});
  const retirement=await page.evaluate(()=>window.__supportEvents);assert(retirement.filter(e=>e.uid===podium&&e.action==='retire-start').every(e=>!e.towerActive));
  report.views.push({mobile,failed,active,retirement,file,sha256:await hash('docs/astra-city/model-support-review/'+file)});await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');console.log(mobile?'mobile passed':'desktop passed');await page.close();
 }
}finally{report.finished=new Date().toISOString();report.finalRuntimeHashes=Object.fromEntries(await Promise.all(files.map(async p=>[p,await hash(p)])));await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
assert.equal(report.errors.length,0);
