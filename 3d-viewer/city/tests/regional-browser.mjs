import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';
const base=process.env.CITY_URL||'http://127.0.0.1:4176/city.html';
const evidence=fileURLToPath(new URL('../../../docs/astra-city/regional/browser/',import.meta.url));
await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),page=await context.newPage(),errors=[],visits=[];
page.on('pageerror',e=>errors.push(e.message));
const state=()=>page.evaluate(()=>window.__city.state);
const settled=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0&&s.regional.pending===0;},null,{timeout:90000});
const choose=async id=>{
 if((await state()).mode!=='orbit')await page.keyboard.press('Escape');
 await page.locator('[data-panel="places"]').click();await page.locator(`[data-region="${PLACES[id].region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await settled();
};
const sections=['01.1','02.1','03.2','04.6','05.1','06.1','07.4','08.3','09.3','10.6','10.10','10.12','10.13','11.1','12.4','13.2','14.1','15.4','16.1','17.1','18.1'];
const capture=new Set(['01.1','05.1','07.4','10.6','10.10','10.12','10.13','13.2','17.1']);
try{
 await page.goto(base+'?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:90000});await page.locator('#loading').waitFor({state:'hidden'});await settled();
 assert.equal((await state()).regional.packages,3);assert.deepEqual((await state()).regional.errors,[]);assert.ok((await state()).regional.surfaces>1000);
 await page.locator('[data-panel="time"]').click();await page.locator('#time').fill('15:00');
 for(const section of sections){
  const found=Object.entries(PLACES).find(([,p])=>p.sectionId===section&&!p.aerialOnly);assert.ok(found,'Walking visit for section '+section);const [id,p]=found;
  await choose(id);const orbit=await state();assert.equal(orbit.place,id);assert.ok(orbit.regional.tiles<=24);assert.ok(orbit.regional.visibleSurfaces>=0);assert.deepEqual(orbit.stream.errors,[]);
  if(capture.has(section))await page.screenshot({path:evidence+section+'-day-1440x1000.png'});
  await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:60000});
  const entered=await state();assert.equal(entered.collision,false,id);assert.ok(Math.hypot(entered.position[0]-p.spawn[0],entered.position[2]-p.spawn[1])<1);
  let walked=false;
  for(const key of ['w','d','s','a']){
   await page.keyboard.down(key);try{await page.waitForFunction(d=>window.__city.state.distance>d+2,entered.distance,{timeout:4500});walked=true;}catch{}finally{await page.keyboard.up(key);}if(walked)break;
  }
  const after=await state();assert.ok(walked,'At least 2 m movement at '+id);assert.equal(after.collision,false);
  visits.push({id,section,title:p.title,visibleSurfaces:orbit.regional.visibleSurfaces,detailTiles:orbit.regional.tiles,render:orbit.render,arrival:entered.position,walked:after.distance-entered.distance});console.log(section,p.title,orbit.regional.visibleSurfaces,'surfaces');
 }
 await page.keyboard.press('Escape');await page.locator('[data-panel="places"]').click();
 await page.locator('#layer-surfaces').uncheck();assert.equal((await state()).layers.surfaces,false);await page.locator('#layer-surfaces').check();assert.equal((await state()).layers.surfaces,true);
 const aerial=Object.entries(PLACES).find(([,p])=>p.aerialOnly);assert.ok(aerial);await choose(aerial[0]);assert.equal(await page.locator('[data-mode="walk"]').isDisabled(),true);
 await page.keyboard.press('2');assert.equal((await state()).mode,'orbit');await page.locator('[data-mode="fly"]').click();await page.waitForFunction(()=>window.__city.state.mode==='fly',null,{timeout:60000});
 const village=Object.entries(PLACES).find(([,p])=>p.sectionId==='10.6'&&!p.aerialOnly)[0];await choose(village);
 await page.locator('[data-panel="time"]').click();await page.locator('#time').fill('22:00');await page.waitForFunction(()=>window.__city.state.time===22);await page.screenshot({path:evidence+'mui-wo-22-1440x1000.png'});
 await page.locator('#time').fill('04:00');await page.waitForFunction(()=>window.__city.state.time===4);await page.screenshot({path:evidence+'mui-wo-04-1440x1000.png'});
 await page.locator('[data-panel="places"]').click();await page.locator('#search').fill('梅窩');await page.waitForFunction(()=>document.querySelector('#search-results button')?.textContent.includes('梅窩'));
 assert.ok(await page.locator('#search-results button').count()>0);await page.keyboard.press('Escape');
 await page.setViewportSize({width:390,height:844});await page.locator('#panel-toggle').click();await page.locator('#search').fill('10.12');await page.waitForFunction(()=>document.querySelector('#search-results button')?.textContent.includes('坪洲'));
 await page.locator('#search-results button').first().click();await settled();assert.equal(PLACES[(await state()).place].sectionId,'10.12');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:evidence+'peng-chau-mobile-390x844.png'});
 let fail=true;await page.route('**/city/data/regional/urban.json',route=>fail?route.fulfill({status:503,body:'deliberate verification failure'}):route.continue());
 await page.goto(base+'?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:90000});await page.locator('#loading').waitFor({state:'hidden'});await settled();
 assert.equal((await state()).regional.errors.length,1);assert.equal((await state()).mode,'orbit');fail=false;await page.locator('#stream-retry').click();await page.waitForFunction(()=>window.__city.state.regional.packages===3&&window.__city.state.regional.errors.length===0,null,{timeout:60000});
 assert.deepEqual(errors,[]);
 const result={result:'passed',visits,checks:['all three regional packages loaded','21 representative sections across all 18 districts','2 m movement at each verified arrival','bounded regional geometry','detail-layer visibility','aerial-only walking guard and flight','22:00 and 04:00 appearance','bilingual/section search','mobile Peng Chau','regional fetch failure and Retry without losing city'],limits:['Short movement checks are not complete walking-route or architectural acceptance.'],errors};
 await writeFile(evidence+'verification.json',JSON.stringify(result,null,2)+'\n');console.log('regional browser passed');
}catch(error){console.error(JSON.stringify({errors,visits},null,2));throw error;}finally{await browser.close();}
