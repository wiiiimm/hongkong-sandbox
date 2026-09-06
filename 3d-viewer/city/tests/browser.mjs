import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const base=process.env.CITY_URL||'http://127.0.0.1:4176/city.html';
// tests/ -> city/ -> 3d-viewer/ -> repository root
const evidence=fileURLToPath(new URL('../../../docs/astra-city/',import.meta.url));
await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const page=await context.newPage(),errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(new URL(base).origin)&&r.status()>=400)failed.push(`${r.status()} ${r.url()}`);});
const state=()=>page.evaluate(()=>window.__city.state);
const ready=async()=>{await page.waitForFunction(()=>window.__city?.ready,{timeout:60000});await page.locator('#loading').waitFor({state:'hidden'});};
try{
 await page.goto(base);await ready();
 assert.equal((await state()).mode,'orbit');assert.ok((await state()).counts.buildings>9000);
 await page.screenshot({path:evidence+'central-desktop-1440x1000.png'});
 for(const name of ['buildings','roads','trees','labels']){
  await page.locator('#layer-'+name).uncheck();assert.equal((await state()).layers[name],false);
  await page.locator('#layer-'+name).check();assert.equal((await state()).layers[name],true);
 }
 await page.locator('#search').fill('Bank of China Tower');await page.locator('#search-results button').first().click();
 await page.waitForFunction(()=>window.__city.state.selectedIndex>=0);assert.match(await page.locator('#building-name').textContent(),/Bank of China/);
 assert.match(await page.locator('#building-source').textContent(),/tagged|Estimated/);await page.locator('#selection-close').click();
 await page.locator('#search').fill('no-such-building-xyz');assert.match(await page.locator('#search-results').textContent(),/No building/);await page.locator('#search').fill('');
 await page.locator('[data-place="central"]').click();
 await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.actorHeight>1&&window.__city.state.actorHeight<3);
 assert.equal((await state()).collision,false);
 await page.keyboard.down('w');await page.waitForFunction(()=>window.__city.state.distance>1.5,{timeout:10000});await page.keyboard.up('w');
 assert.equal((await state()).collision,false);await page.keyboard.press('c');assert.equal((await state()).firstPerson,true);await page.keyboard.press('c');
 await page.waitForFunction(()=>Math.abs(window.__city.state.camera[1]-window.__city.state.position[1])<5);
 await page.waitForTimeout(1000);await page.screenshot({path:evidence+'central-walk-1440x1000.png'});
 await page.keyboard.press('Escape');assert.equal((await state()).mode,'orbit');
 await page.locator('[data-mode="fly"]').click();const flight=await state();
 await page.keyboard.down('w');await page.waitForFunction(y=>window.__city.state.position[1]>y+5,flight.position[1],{timeout:10000});await page.keyboard.up('w');
 assert.equal((await state()).collision,false);await page.keyboard.down('Shift');await page.waitForFunction(()=>window.__city.state.speed>70);await page.keyboard.up('Shift');
 await page.waitForTimeout(1000);await page.screenshot({path:evidence+'central-flight-1440x1000.png'});
 await page.locator('#about-open').click();const paused=await state();await page.waitForTimeout(400);assert.deepEqual((await state()).position,paused.position);await page.locator('#about-close').click();
 await page.keyboard.press('Escape');await page.locator('[data-place="central"]').click();
 await page.locator('#time').fill('20');assert.equal((await state()).time,20);assert.ok(await page.locator('body').evaluate(el=>el.classList.contains('night')));
 await page.waitForTimeout(1800);await page.screenshot({path:evidence+'central-night-1440x1000.png'});
 const downloadPromise=page.waitForEvent('download');await page.locator('#postcard').click();const download=await downloadPromise;const path=evidence+'central-postcard-1440x1000.png';await download.saveAs(path);const png=await readFile(path);assert.equal(png.readUInt32BE(16),1440);assert.equal(png.readUInt32BE(20),1000);
 await page.locator('[data-place="lantau"]').click();assert.equal((await state()).place,'lantau');await page.waitForTimeout(1800);assert.ok((await state()).camera[0]<-10000);
 await page.locator('[data-place="wanchai"]').click();assert.equal((await state()).place,'wanchai');
 await page.locator('[data-place="kowloon"]').click();assert.equal((await state()).place,'kowloon');
 await page.locator('#time').fill('15');await page.locator('[data-place="central"]').click();
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(1800);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:evidence+'central-mobile-390x844.png'});
 await page.locator('#panel-toggle').click();assert.ok(await page.locator('#explorer').isVisible());await page.locator('[data-place="wanchai"]').click();assert.equal(await page.locator('#explorer').isVisible(),false);
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={result:'passed',checks:['city load','four independent layer toggles','named building-part search and height provenance','empty search','walk movement and building clearance','actor size','first-person camera','flight climb and boost','pause while help is open','night lighting','native-size PNG export','Lantau and neighbourhood navigation','mobile layout and panel'],state:await state(),pageErrors:errors,failedRequests:failed};
 await writeFile(evidence+'verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
