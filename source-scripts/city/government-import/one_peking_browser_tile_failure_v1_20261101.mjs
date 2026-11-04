/** Three immutable scene controls; inspect exact BASIC tile error, no acceptance. */
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright'),hash=b=>createHash('sha256').update(b).digest('hex'),inputs={};
const read=async p=>{const raw=await readFile(new URL(p,root));inputs[p]=hash(raw);return JSON.parse(raw);};
const config=await read(process.argv[2]),out=process.argv[3],manifest=await read('3d-viewer/city/data/manifest.json'),cat=await read(config.stage+'catalogue.json'),terrain=config.terrain[0];
assert(config.viewerURL==='http://127.0.0.1:4177/city.html'&&config.terrain.length===1&&terrain.replaces);
const tile=await read('3d-viewer/city/data/tiles/0_-1.json'),form=tile.buildings.find(b=>b.uid==='landsd/211702:0');assert(form);await mkdir(new URL(out,root),{recursive:true});
for(const path of ['source-scripts/city/government-import/one_peking_browser_tile_failure_v1_20261101.mjs','3d-viewer/city/app.js','3d-viewer/city/streaming.js','3d-viewer/city/tile-cache.js']){const b=await readFile(new URL(path,root));inputs[path]=hash(b);}
const reports=[],browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{for(const name of ['baseline','terrain-only','terrain-and-sources']){
 const context=await browser.newContext({viewport:{width:1280,height:900}}),page=await context.newPage(),errors=[],tileHTTP=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',async r=>{if(r.url().includes('/city/data/tiles/0_-1.json')){const bytes=await r.body();tileHTTP.push({status:r.status(),sha256:hash(bytes),url:r.url()});}});
 await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__port",{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding})});window.__portOriginalRender=renderer.render.bind(renderer);renderer.render=()=>{};'});});
 if(name!=='baseline'){
  await page.route('**/'+terrain.destination,async route=>{const b=await readFile(new URL(terrain.source,root));assert.equal(hash(b),terrain.sha256);inputs[terrain.source]=hash(b);await route.fulfill({body:b});});
  await page.route('**/city/data/manifest.json',async route=>{const response=await route.fetch(),m=await response.json();assert.deepEqual(m,manifest);m.terrainPatches=m.terrainPatches.filter(t=>t.url!==terrain.replaces.url);m.terrainPatches.push({url:terrain.destination,resolution:terrain.resolution,area:terrain.area});if(name==='terrain-and-sources')m.officialModelCatalogues.push(config.catalogueURL);await route.fulfill({response,json:m});});
 }
 if(name==='terrain-and-sources'){
  await page.route('**/'+config.catalogueURL,r=>r.fulfill({json:cat}));const folder=config.catalogueURL.slice(0,config.catalogueURL.lastIndexOf('/')+1);
  for(const model of cat.models)await page.route('**/'+folder+model.asset+'*',async route=>{const path=config.stage+model.asset,b=await readFile(new URL(path,root));assert.equal(hash(b),model.sha256);inputs[path]=hash(b);await route.fulfill({body:b});});
 }
 let failure=null;
 try{
  await page.goto(config.viewerURL,{waitUntil:'domcontentloaded',timeout:120000});await page.waitForFunction(()=>!!window.__port?.stream&&!!window.__port?.officialModels,null,{timeout:120000});await page.evaluate(b=>window.__port.visitBuilding(b),form);
  await page.waitForFunction(uid=>window.__port.stream.cache.errors.has('0_-1')||window.__port.stream.detailedModels.get(uid)?.active,form.uid,{timeout:120000});
 }catch(e){failure=String(e.message);}
 const state=await page.evaluate(uid=>{const r=window.__port;if(!r?.stream)return {notReady:true};return {uid,selectedId:window.__city.state.selectedId,loadingTravel:window.__city.state.loadingTravel,travelling:window.__city.state.travelling,movementReady:window.__city.state.movementReady,basicLoaded:!!r.stream.getLoadedBuilding(uid),detailActive:!!r.stream.detailedModels.get(uid)?.active,sourceErrors:[...r.stream.cache.errors].map(([key,e])=>({key,name:e?.name,message:e?.message??String(e),stack:e?.stack,cause:e?.cause?String(e.cause):null})),modelErrors:[...r.officialModels.cache.errors].map(([key,e])=>({key,message:e?.message??String(e)})),sourceRunning:[...r.stream.cache.running.keys()]};},form.uid);
 reports.push({case:name,failure,errors,tileHTTP,state,installationApproved:false});console.log(JSON.stringify(reports.at(-1)));await context.close();
}}
finally{await browser.close();}
for(const [p,h]of Object.entries(inputs))assert.equal(hash(await readFile(new URL(p,root))),h,'Diagnostic input changed');
await writeFile(new URL(out+'diagnostic.json',root),JSON.stringify({cases:reports,inputHashes:inputs,publication:false,modelGeometryChanges:0,installationApproved:false},null,2)+'\n');
