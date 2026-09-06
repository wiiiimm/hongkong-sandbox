import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';
const base=process.env.CITY_URL||'http://127.0.0.1:4176/city.html';
const evidence=fileURLToPath(new URL('../../../docs/astra-city/islands/',import.meta.url));
await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
const page=await context.newPage(),errors=[],failed=[],visits=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('response',r=>{if(r.url().startsWith(new URL(base).origin)&&r.status()>=400)failed.push(`${r.status()} ${r.url()}`);});
const state=()=>page.evaluate(()=>window.__city.state);
const settled=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0;},null,{timeout:90000});
const priority=['muiwo','taio','cheungchau','pengchau','puio','cheungsha','tongfuk','shuihau','ngongping','tungchungvalley','lantau'];
try{
 await page.goto(base+'?district=muiwo');
 await page.waitForFunction(()=>window.__city?.ready,null,{timeout:90000});await page.locator('#loading').waitFor({state:'hidden'});await settled();
 await page.locator('[data-panel="sky"]').click();await page.locator('#time').fill('15:00');
 for(const id of priority){
  if((await state()).mode!=='orbit')await page.keyboard.press('Escape');
  await page.locator('[data-panel="places"]').click();
  await page.locator(`[data-region="${PLACES[id].region}"]`).click();
  await page.locator(`[data-place="${id}"]`).click();await settled();
  await page.waitForFunction(title=>document.getElementById('map-location').textContent===title,PLACES[id].title.toUpperCase());
  const orbit=await state();assert.equal(orbit.place,id);assert.equal(orbit.region,PLACES[id].region);
  assert.deepEqual(orbit.stream.errors,[]);assert.ok(orbit.stream.cached<=30);assert.ok(orbit.stream.wanted<=24);assert.ok(orbit.stream.forms>0);
  await page.screenshot({path:evidence+id+'-orbit-1440x1000.png'});
  await page.locator('[data-mode="walk"]').click();
  await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:60000});
  const entered=await state();assert.equal(entered.collision,false,`${id} arrival collision`);
  assert.ok(Math.hypot(entered.position[0]-PLACES[id].spawn[0],entered.position[2]-PLACES[id].spawn[1])<1,`${id} uses the configured public-path arrival`);
  await page.keyboard.down('w');
  try{await page.waitForFunction(distance=>window.__city.state.distance>distance+1.5,entered.distance,{timeout:20000});}finally{await page.keyboard.up('w');}
  const walked=await state();assert.equal(walked.collision,false,`${id} walking collision`);
  if(['muiwo','taio','cheungchau','pengchau'].includes(id)){
   await page.waitForFunction(()=>{const s=window.__city.state;return Math.hypot(...s.camera.map((v,i)=>v-s.position[i]))<12;},null,{timeout:30000});
   await page.screenshot({path:evidence+id+'-walk-1440x1000.png'});
  }
  visits.push({id,title:PLACES[id].title,region:PLACES[id].region,source:PLACES[id].source,configuredArrival:PLACES[id].spawn,actualArrival:entered.position,walkedMetres:walked.distance-entered.distance,collision:walked.collision,loadedForms:orbit.stream.forms,cache:orbit.stream.cached,render:orbit.render});
  console.log(id,'walked',(walked.distance-entered.distance).toFixed(2),'m;',orbit.stream.forms,'loaded forms');
 }
 await page.keyboard.press('Escape');await page.setViewportSize({width:390,height:844});
 await page.locator('#panel-toggle').click();await page.locator('[data-panel="places"]').click();
 await page.locator('[data-region="islands"]').click();await page.locator('[data-place="pengchau"]').click();await settled();
 assert.equal((await state()).place,'pengchau');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:evidence+'peng-chau-mobile-390x844.png'});
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={result:'passed',checks:['explicit destination selection for all 11 priority locations','arrival at configured public paths','clear building collision at entry','at least 1.5 m walking at every location','bounded streaming cache','no page errors or failed local requests','mobile island navigation without horizontal overflow'],limits:['Arrival and short-movement checks are not a detailed village, coastline or architecture review.','The existing terrain mesh is sampled at 70 m.','Mapped building completeness and height accuracy remain unverified.'],visits,errors,failed};
 await writeFile(evidence+'verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({result:result.result,visited:visits.length,errors,failed}));
}catch(error){console.error(JSON.stringify({errors,failed,visits},null,2));throw error;}finally{await browser.close();}
