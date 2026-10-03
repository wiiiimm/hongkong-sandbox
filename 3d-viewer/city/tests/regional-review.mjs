import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';
const root=fileURLToPath(new URL('../../../docs/astra-city/regional/review/',import.meta.url));await mkdir(root,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce',hasTouch:true}),errors=[],observations=[];
page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
const current=()=>page.evaluate(()=>window.__city.state),settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0&&s.regional.pending===0;},null,{timeout:90000});
const capture=async(name)=>{await page.waitForTimeout(180);await page.screenshot({path:root+name+'.png'});};
const choose=async section=>{const [id,p]=Object.entries(PLACES).find(([,p])=>p.sectionId===section&&!p.aerialOnly);await page.locator('#tab-places').click();await page.locator(`[data-region="${p.region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await settle();return id;};
try{
 const url=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');url.searchParams.set('district','section-02-4');await page.goto(url.href);await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 await page.locator('#tab-time').click();await page.locator('#time').fill('15:00');await page.waitForFunction(()=>window.__city.state.time===15);
 for(const section of ['02.4','04.5','06.4','07.5','08.3','09.6']){
  const id=await choose(section),state=await current();assert.equal(state.place,id);assert.deepEqual(state.regional.errors,[]);assert.deepEqual(state.stream.errors,[]);assert.ok(state.regional.tiles<=24);assert.equal(state.regional.packages,3);
  await capture('urban-'+section+'-1440x1000');observations.push({section,id,regional:state.regional,render:state.render,camera:state.camera});
 }
 await choose('02.4');await page.locator('#layer-surfaces').uncheck();assert.equal((await current()).layers.surfaces,false);await capture('victoria-park-surfaces-hidden');await page.locator('#layer-surfaces').check();assert.equal((await current()).layers.surfaces,true);await capture('victoria-park-surfaces-visible');
 await page.setViewportSize({width:390,height:844});await page.locator('#panel-toggle').click();await page.locator('#search').fill('04.5');await page.waitForFunction(()=>document.querySelector('#search-results button')?.textContent.includes('Repulse Bay'));await page.locator('#search-results button').first().click();await settle();assert.equal((await current()).place,'section-04-5');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await capture('repulse-bay-mobile-390x844');
 await page.locator('#panel-toggle').click();await page.locator('#search').fill('南蓮');await page.waitForFunction(()=>document.querySelector('#search-results button')?.textContent.includes('南蓮'));await page.locator('#search-results button').first().click();await settle();assert.equal((await current()).place,'section-08-3');await capture('nan-lian-mobile-390x844');
 await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady,null,{timeout:60000});assert.equal((await current()).collision,false);await page.keyboard.press('Escape');
 const [aerialId,aerial]=Object.entries(PLACES).find(([,p])=>p.aerialOnly);await page.locator('#panel-toggle').click();await page.locator('#search').fill(aerial.title);await page.waitForFunction(title=>document.querySelector('#search-results button')?.textContent.includes(title),aerial.title);await page.locator('#search-results button').first().click();await settle();assert.equal((await current()).place,aerialId);assert.equal(await page.locator('[data-mode="walk"]').isDisabled(),true);await page.keyboard.press('2');assert.equal((await current()).mode,'orbit');
 assert.deepEqual(errors,[]);const result={result:'passed',url:url.href,browser:await browser.version(),observations,checks:['six urban regional render snapshots','local-detail visibility switch','section-number search on mobile','Traditional Chinese search on mobile','clear Nan Lian walking arrival','aerial-only keyboard and button guards','bounded detail geometry and zero graphics errors'],errors};await writeFile(root+'verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
