import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
const state=()=>page.evaluate(()=>window.__city.state);
async function point(hour){await page.locator('#time-dial').scrollIntoViewIfNeeded();const b=await page.locator('#time-dial').boundingBox(),a=hour*Math.PI/12;return [b.x+b.width/2+Math.sin(a)*b.width*.38,b.y+b.height/2-Math.cos(a)*b.height*.38];}
try{
 await page.goto((process.env.CITY_URL||'http://127.0.0.1:4176/city.html')+'?district=kowloon');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:60000});await page.locator('#loading').waitFor({state:'hidden'});await page.locator('[data-panel=time]').click();
 for(let h=0;h<24;h++){await page.mouse.click(...await point(h));assert.equal((await state()).time,h);}
 await page.mouse.move(...await point(23));await page.mouse.down();for(const h of [23.5,0,.5,1]){await page.mouse.move(...await point(h));assert.equal((await state()).time,h);}await page.mouse.up();
 await page.locator('#time-play').click();await page.locator('#time-dial').press('Home');assert.equal((await state()).time,0);assert.equal((await state()).timeLapse,false);
 await page.locator('#time-dial').press('ArrowLeft');assert.equal((await state()).time,23.75);await page.locator('#time-dial').press('ArrowRight');assert.equal((await state()).time,0);
 await page.locator('#time-dial').press('PageUp');assert.equal((await state()).time,1);await page.locator('#time-dial').press('Shift+ArrowRight');assert.ok(Math.abs((await state()).time-65/60)<1e-9);
 await page.locator('#time').fill('23:59');assert.ok(Math.abs((await state()).time-(23+59/60))<1e-9);assert.equal(await page.locator('#time-dial').getAttribute('aria-valuenow'),'1439');
 await page.locator('#tab-weather').click();await page.locator('#light-shimmer').uncheck();assert.equal((await state()).lighting.shimmer,0);await page.locator('#light-shimmer').check();assert.equal((await state()).lighting.shimmer,1);
 await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>window.__city.state.lighting.shimmer===0);assert.equal((await state()).lighting.shimmer,0);assert.equal(await page.locator('#light-shimmer').isDisabled(),true);
 await page.emulateMedia({reducedMotion:'no-preference'});await page.waitForFunction(()=>window.__city.state.lighting.shimmer===1);assert.equal((await state()).lighting.shimmer,1);
 await page.setViewportSize({width:390,height:844});await page.locator('#panel-toggle').click();await page.locator('#tab-time').click();await page.touchscreen.tap(...await point(6));assert.equal((await state()).time,6);await page.touchscreen.tap(...await point(18));assert.equal((await state()).time,18);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.locator('#time-dial').screenshot({path:new URL('../../../docs/astra-city/night-cycle/clock-mobile.png',import.meta.url).pathname});
 const result={result:'passed',checks:['all 24 hours selected on circular dial','drag forwards through midnight','keyboard wraps both ways','five-minute keyboard step','manual clock pauses time lapse','exact 23:59 entry','accessible minute value','shimmer switch','dynamic reduced-motion setting','touch selection at 6 am and 6 pm','mobile layout'],errors};assert.deepEqual(errors,[]);
 await writeFile(new URL('../../../docs/astra-city/night-cycle/clock-verification.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close();}
