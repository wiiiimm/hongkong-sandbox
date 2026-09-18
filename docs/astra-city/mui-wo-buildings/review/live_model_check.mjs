import {chromium} from '../../../../3d-viewer/city/node_modules/playwright/index.mjs';
import {readFile,writeFile} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import assert from 'node:assert/strict';
const here=path.dirname(fileURLToPath(import.meta.url));const baked=JSON.parse(await readFile(path.join(here,'model-sample/model-geometries.json'))).byBuildingUid;
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),errors=[],failed=[],tiles=new Map(),pendingResponses=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/city/data/tiles/')){if(r.status()>=400)failed.push(r.status()+' '+r.url());else pendingResponses.push(r.json().then(d=>tiles.set(r.url(),d)));}});
const settled=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0;},null,{timeout:90000});
try{
 await page.goto('http://127.0.0.1:4176/city.html?district=muiwo');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:90000});await page.locator('#loading').waitFor({state:'hidden'});await settled();
 await page.locator('[data-panel="sky"]').click();await page.locator('#time').fill('15:00');await page.screenshot({path:path.join(here,'mui-wo-live-official-overview-1600x1000.png')});
 const visits=[];
 for(const [search,filename] of [['Pak Ngan Heung Public Toilet','pak-ngan-heung-public-toilet-live'],['YICK YUEN','pak-ngan-heung-yick-yuen-live']]){
  await page.locator('[data-panel="places"]').click();await page.locator('#search').fill(search);await page.locator('#search-results button').first().waitFor();await page.locator('#search-results button').first().click();await settled();await page.locator('#building-card').waitFor({state:'visible'});
  const state=await page.evaluate(()=>window.__city.state);assert.ok(baked[state.selectedId],state.selectedId+' must be a verified model match');assert.deepEqual(state.stream.errors,[]);
  const card=await page.locator('#building-card').innerText(),sourceLink=await page.locator('#building-osm').getAttribute('href');assert.match(card,/Official Lands Department non-textured 3D roof geometry/);
  await page.screenshot({path:path.join(here,filename+'-1600x1000.png')});
  const performance=await page.evaluate(async()=>{const frames=[];let last=performance.now();for(let n=0;n<90;n++)await new Promise(resolve=>requestAnimationFrame(t=>{frames.push(t-last);last=t;resolve();}));frames.sort((a,b)=>a-b);return {sampledFrames:frames.length,medianFrameMs:frames[Math.floor(frames.length/2)],p90FrameMs:frames[Math.floor(frames.length*.9)],meanFrameMs:frames.reduce((a,b)=>a+b,0)/frames.length};});
  visits.push({search,state,sourceLink,card,performance});
 }
 await Promise.all(pendingResponses);const models=[...tiles.values()].flatMap(t=>t.buildings).filter(b=>b.modelGeometry);
 assert.equal(new Set(models.map(b=>b.uid)).size,275);assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={result:'passed',url:page.url(),checkedAt:new Date().toISOString(),loadedTileResponses:tiles.size,loadedVerifiedModelCount:new Set(models.map(b=>b.uid)).size,loadedModelTriangles:models.reduce((n,b)=>n+b.modelGeometry.position.length/9,0),visits,errors,failed,limits:['Headless Chrome timing is local evidence, not a mobile frame-rate guarantee.','This verifies live tile geometry, selection and representative appearance; it does not validate every building footprint or pedestrian route.']};
 await writeFile(path.join(here,'live-model-check.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,visits:visits.map(v=>({search:v.search,id:v.state.selectedId,render:v.state.render,stream:v.state.stream,performance:v.performance}))},null,2));
}finally{await browser.close();}
