/** Clean actual Base-only canvas exports for each private procedural fallback. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
import {bindPrivateSourceBoundRoutes} from './private_source_bound_browser_routes_v1_20261029.mjs';
import {sourceBoundFallbackChecks} from './source_bound_basic_lifecycle_checks_v1_20261029.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const config=await read(process.argv[2]),out=new URL(process.argv[3]+'/',root),catalogue=await read(config.stage+'catalogue.json');
assert(config.diagnosticOnly&&config.publication===false&&config.viewerURL==='http://127.0.0.1:4177/city.html');
const changes=config.privateSourceBoundTileOverlays.flatMap(o=>o.changes);assert.equal(changes.length,4);
await mkdir(out,{recursive:true});const report={diagnosticOnly:true,physicalAcceptance:false,installationApproved:false,publication:false,pageErrors:[],views:[],cases:[]};
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const width of [1280,390]){
  const context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push({width,message:e.message}));
  await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+"\nObject.defineProperty(window,'__port',{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,THREE,visitBuilding,closeSelection})});"});});
  await bindPrivateSourceBoundRoutes(page,config,root,'staged',report);
  await page.route('**/'+config.catalogueURL,r=>r.fulfill({json:catalogue}));
  const assetBase=config.catalogueURL.slice(0,config.catalogueURL.lastIndexOf('/')+1);
  for(const model of catalogue.models){const bytes=await readFile(new URL(config.stage+model.asset,root));assert.equal(bytes.length,model.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),model.sha256);await page.route('**/'+assetBase+model.asset+'*',r=>r.fulfill({body:bytes}));}
  for(const t of config.terrain)await page.route('**/'+t.destination,async r=>r.fulfill({body:await readFile(new URL(t.source,root))}));
  await page.route('**/city/data/manifest.json',async route=>{const response=await route.fetch(),m=await response.json();assert(!m.officialModelCatalogues.includes(config.catalogueURL));m.officialModelCatalogues.push(config.catalogueURL);m.terrainPatches.push(...config.terrain.map(t=>({url:t.destination,resolution:t.resolution,area:t.area})));await route.fulfill({response,json:m});});
  await page.goto(config.viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:300000});assert(await page.evaluate(url=>window.__port.officialModels.loadCatalogue(url),config.catalogueURL));
  await page.evaluate(()=>window.__port.officialModels.setQuality('base'));
  // A common initial visit loads the exact tile set used by every group fallback.
  await page.evaluate(b=>window.__port.visitBuilding(b),changes.find(c=>c.role==='source-bound-basic-continuation').before);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
  await page.waitForFunction(()=>{const c=window.__port.stream.cache;return !c.running.size&&!c.reloads.size&&!c.reloading.size&&c.wanted.every(id=>c.entries.has(id));},null,{timeout:300000});
  report.cases.push({width,contract:await sourceBoundFallbackChecks(page,false,catalogue,config)});
  for(const change of changes){
   await page.evaluate(b=>window.__port.visitBuilding(b),change.before);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
   const observation=await page.evaluate(async change=>{
    const r=window.__port,b=r.stream.getLoadedBuilding(change.uid);if(!b)throw new Error('Fallback form absent');
    const {describeBuilding}=await import('/city/building-geometry.js'),description=describeBuilding(b),rings=b.rings.flat(),lo=[Math.min(...rings.map(p=>p[0])),Math.min(...description.parts.map(p=>p.bottom)),Math.min(...rings.map(p=>p[1]))],hi=[Math.max(...rings.map(p=>p[0])),Math.max(...description.parts.map(p=>p.top)),Math.max(...rings.map(p=>p[1]))],c=new r.THREE.Vector3(...lo).add(new r.THREE.Vector3(...hi)).multiplyScalar(.5),direction=new r.THREE.Vector3(1,.65,-1).normalize(),right=new r.THREE.Vector3().crossVectors(new r.THREE.Vector3(0,1,0),direction).normalize(),up=new r.THREE.Vector3().crossVectors(direction,right),tanV=Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2)),tanH=tanV*r.camera.aspect;let distance=0;
    for(const x of[lo[0],hi[0]])for(const y of[lo[1],hi[1]])for(const z of[lo[2],hi[2]]){const p=new r.THREE.Vector3(x,y,z).sub(c);distance=Math.max(distance,p.dot(direction)+Math.abs(p.dot(right))/tanH,p.dot(direction)+Math.abs(p.dot(up))/tanV);}
    r.controls.enableDamping=false;r.camera.position.copy(c).addScaledVector(direction,distance*1.12);r.controls.target.copy(c);r.controls.update();r.camera.updateMatrixWorld(true);const time=document.getElementById('time');time.value='15:00';time.dispatchEvent(new Event('input',{bubbles:true}));
    for(const x of[lo[0],hi[0]])for(const y of[lo[1],hi[1]])for(const z of[lo[2],hi[2]]){const p=new r.THREE.Vector3(x,y,z).project(r.camera);if(Math.abs(p.x)>1||Math.abs(p.y)>1||Math.abs(p.z)>1)throw new Error('Fallback bounds not framed');}
    await new Promise(requestAnimationFrame);r.renderer.render(r.scene,r.camera);return {uid:b.uid,quality:r.officialModels.quality,active:!!r.stream.detailedModels.get(b.uid)?.active,lo,hi,canvas:r.renderer.domElement.toDataURL('image/png')};
   },change);
   assert.equal(observation.quality,'base');assert.equal(observation.active,false);const file=width+'-'+change.uid.replaceAll('/','-').replaceAll(':','-')+'-base-only.png';await writeFile(new URL(file,out),Buffer.from(observation.canvas.split(',')[1],'base64'));delete observation.canvas;report.views.push({width,file,...observation});await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));console.log(width,change.uid,'captured');
  }
  await context.close();
 }
 assert.deepEqual(report.pageErrors,[]);assert.equal(report.views.length,8);report.passed=true;
}catch(error){report.error=error.stack;throw error;}finally{await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await browser.close();}
