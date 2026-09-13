import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';
const base=process.env.CITY_URL||'http://127.0.0.1:4176/city.html';
const evidence=fileURLToPath(new URL('../../../docs/astra-city/',import.meta.url));await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const page=await context.newPage(),errors=[],failed=[],visits=[];let expectedFailure=false;
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(new URL(base).origin)&&r.status()>=400&&!expectedFailure)failed.push(`${r.status()} ${r.url()}`);});
const state=()=>page.evaluate(()=>window.__city.state);
const settled=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0;},null,{timeout:90000});
async function visit(id){
 await page.locator('[data-panel=places]').click();
 await page.locator(`[data-region="${PLACES[id].region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await settled();
 const s=await state();assert.equal(s.place,id);assert.deepEqual(s.stream.errors,[]);assert.ok(s.stream.cached<=30);assert.ok(s.stream.wanted<=24);assert.ok(s.stream.forms>20);
 if(id==='mongkok')assert.ok(s.stream.forms>5000,'cross-harbour arrival keeps the destination blocks loaded');
 visits.push({place:id,loadedForms:s.stream.forms,cached:s.stream.cached,triangles:s.render.triangles});
}
try{
 await page.goto(base);await page.waitForFunction(()=>window.__city?.ready,null,{timeout:60000});await page.locator('#loading').waitFor({state:'hidden'});await settled();
 assert.equal((await state()).mode,'orbit');assert.ok((await state()).counts.buildings>40000);
 await page.screenshot({path:evidence+'central-desktop-1440x1000.png'});
 for(const name of ['buildings','roads','trees','labels']){await page.locator('#layer-'+name).uncheck();assert.equal((await state()).layers[name],false);await page.locator('#layer-'+name).check();assert.equal((await state()).layers[name],true);}
 await page.locator('#search').fill('Bank of China Tower');await page.locator('#search-results button').first().click();await page.waitForFunction(()=>window.__city.state.selectedId!==null);assert.match(await page.locator('#building-name').textContent(),/Bank of China/);assert.match(await page.locator('#building-source').textContent(),/tagged|Estimated/);await page.locator('#selection-close').click();
 await page.locator('#search').fill('no-such-building-xyz');await page.waitForFunction(()=>document.getElementById('search-results').textContent.includes('No building'));await page.locator('#search').fill('');
 await visit('central');await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady);
 assert.ok((await state()).actorHeight>1&&(await state()).actorHeight<3);assert.equal((await state()).collision,false);
 await page.keyboard.down('w');await page.waitForFunction(()=>window.__city.state.distance>1.5,null,{timeout:15000});await page.keyboard.up('w');assert.equal((await state()).collision,false);
 await page.keyboard.press('c');assert.equal((await state()).firstPerson,true);await page.keyboard.press('c');await page.waitForTimeout(1000);await page.screenshot({path:evidence+'central-walk-1440x1000.png'});
 await page.keyboard.press('Escape');await page.locator('[data-mode="fly"]').click();await page.locator('[role=menuitemradio][aria-checked=true]').click();await page.waitForFunction(()=>window.__city.state.mode==='fly'&&window.__city.state.movementReady);const flight=await state();
 await page.keyboard.down('w');await page.waitForFunction(y=>window.__city.state.position[1]>y+5,flight.position[1],{timeout:15000});await page.keyboard.up('w');assert.equal((await state()).collision,false);
 await page.keyboard.down('Shift');await page.waitForFunction(()=>window.__city.state.speed>70);await page.keyboard.up('Shift');await page.waitForTimeout(1000);await page.screenshot({path:evidence+'central-flight-1440x1000.png'});
 await page.locator('#about-open').click();const paused=await state();await page.waitForTimeout(400);assert.deepEqual((await state()).position,paused.position);assert.match(await page.locator('#about').textContent(),/stargazing.*live Hong Kong time.*live HKO observations.*manual weather/);await page.locator('#about-close').click();await page.keyboard.press('Escape');
 await visit('central');await page.locator('[data-panel=sky]').click();await page.locator('#time').fill('20:00');assert.equal((await state()).time,20);await page.screenshot({path:evidence+'central-night-1440x1000.png'});
 const downloadPromise=page.waitForEvent('download');await page.locator('#postcard').click();const download=await downloadPromise;const path=evidence+'central-postcard-1440x1000.png';await download.saveAs(path);const png=await readFile(path);assert.equal(png.readUInt32BE(16),1440);assert.equal(png.readUInt32BE(20),1000);
 // Search must find and load a building in a region never visited this session.
 await page.locator('#search').fill('One Citygate');await page.locator('#search-results button').first().click();await page.waitForFunction(()=>window.__city.state.selectedId!==null);assert.equal(await page.locator('#building-name').textContent(),'One Citygate');assert.equal((await state()).time,20);assert.ok((await state()).tiles.includes('-12_-1'));await page.locator('#selection-close').click();await page.locator('#search').fill('');
 await page.locator('[data-panel=sky]').click();await page.locator('#time').fill('15:00');await visit('lantau');await page.screenshot({path:evidence+'tung-chung-desktop-1440x1000.png'});
 await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady);assert.equal((await state()).collision,false);await page.keyboard.press('Escape');
 for(const id of ['mongkok','northpoint','chaiwan','aberdeen','stanley','discoverybay','muiwo']){await visit(id);if(['mongkok','muiwo'].includes(id))await page.screenshot({path:evidence+id+'-desktop-1440x1000.png'});}
 // Simulate a failed collision tile: the original game remains available and a retry recovers it.
 expectedFailure=true;await page.route('**/tiles/-16_1.json',r=>r.fulfill({status:503,body:'Temporary test outage'}));await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="taio"]').click();await page.waitForFunction(()=>window.__city.state.stream.errors.includes('-16_1'));
 await page.locator('[data-mode="walk"]').click();assert.equal((await state()).mode,'orbit');assert.ok(await page.locator('#stream-retry').isVisible());await page.unroute('**/tiles/-16_1.json');expectedFailure=false;await page.locator('#stream-retry').click();await settled();assert.deepEqual((await state()).stream.errors,[]);await page.screenshot({path:evidence+'tai-o-desktop-1440x1000.png'});
 // A rapid destination change must not let a stale arrival overwrite the final choice.
 await page.locator('[data-place="lantau"]').click();await page.locator('[data-region="island"]').click();await page.locator('[data-place="central"]').click();await page.locator('[data-region="kowloon"]').click();await page.locator('[data-place="mongkok"]').click();await settled();assert.equal((await state()).place,'mongkok');assert.ok((await state()).stream.cached<=30);
 await visit('central');await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:evidence+'central-mobile-390x844.png'});
 await page.locator('#panel-toggle').click();assert.ok(await page.locator('#explorer').isVisible());await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="muiwo"]').click();await settled();assert.equal(await page.locator('#explorer').isVisible(),false);await page.screenshot({path:evidence+'muiwo-mobile-390x844.png'});
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={result:'passed',checks:['city load','four independent layer toggles','named building-part search and height provenance','empty search','walk movement and clearance','actor dimensions','first-person camera','flight climb and boost','paused help','original stargazing and weather notice','night lighting','native-size PNG export','global search loads an unvisited region','walking in Tung Chung','expanded destination visits','bounded 30-section cache','tile failure blocks entry and explicit retry recovers','rapid destination changes','mobile regional navigation'],visits,state:await state(),pageErrors:errors,unexpectedFailedRequests:failed};
 await writeFile(evidence+'verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
