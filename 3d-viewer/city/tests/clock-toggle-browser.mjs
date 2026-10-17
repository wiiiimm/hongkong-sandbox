// HKS-190: use the real city clock and lighting, with native button interactions.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
const output=new URL('../../../docs/astra-city/clock-toggle/',import.meta.url);await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true});
const report={testedAt:new Date().toISOString(),checks:[],layouts:[],errors:[]};
page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});
const state=()=>page.evaluate(()=>window.__city.state),toggle=page.getByRole('switch',{name:'Live Hong Kong time'}),date=page.locator('#sky-date');
const tab=async name=>{if(!(await state()).controls.expanded)await page.locator('#panel-toggle').click();await page.locator('#tab-'+name).click();};
async function checkMode(live){assert.equal((await state()).environment.mode,live?'live':'manual');assert.equal(await toggle.getAttribute('aria-checked'),String(live));assert.equal(await date.isDisabled(),live);}
async function enableLive(){if((await state()).environment.mode!=='live')await toggle.click();await checkMode(true);}
try{
 await page.goto(process.env.CITY_URL||'http://127.0.0.1:4176/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready&&!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await tab('time');
 await checkMode(false);assert.equal(await toggle.evaluate(e=>e.tagName),'BUTTON');await date.fill('2026-12-31');await date.press('Tab');await page.locator('#time-play').click();await enableLive();assert.equal((await state()).timeLapse,false);assert.ok(Math.abs(Date.parse((await state()).environment.date)-Date.now())<3000);await toggle.press('Tab');assert.equal(await date.evaluate(e=>document.activeElement===e),false);
 await toggle.press('Space');await checkMode(false);const frozen=(await state()).environment.date;await page.waitForTimeout(1150);assert.equal((await state()).environment.date,frozen);await toggle.press('Enter');await checkMode(true);report.checks.push('Native click, Space and Enter switch Live/Manual; Live stops playback, follows current HKT and disables/skips the date; Manual holds time');
 for(const action of [()=>page.locator('#time').fill('22:00'),()=>page.locator('#time-dial').press('Home'),()=>page.locator('[data-hour="4"]').click(),()=>page.locator('#time-play').click()]){await enableLive();await action();await checkMode(false);if((await state()).timeLapse)await page.locator('#time-play').click();}
 await date.fill('2026-12-31');await date.press('Tab');assert.equal((await state()).environment.hkt.date,'2026-12-31');report.checks.push('Exact time, dial, presets and timelapse all restore Manual and re-enable date; manual date editing still works');
 assert.equal(await page.locator('#panel-time #light-shimmer').count(),0);await tab('weather');assert.equal(await page.locator('#panel-weather #light-shimmer').count(),1);await page.locator('#light-shimmer').uncheck();assert.equal((await state()).lighting.shimmer,0);await page.locator('#light-shimmer').check();assert.equal((await state()).lighting.shimmer,1);report.checks.push('Distant light shimmer lives in Weather and still controls the lighting uniform');
 for(const [width,height]of [[1440,1000],[390,844],[320,667]]){
  await page.setViewportSize({width,height});await tab('time');await enableLive();await date.scrollIntoViewIfNeeded();await page.waitForTimeout(260);
  const layout=await toggle.evaluate(e=>{const r=e.getBoundingClientRect(),c=document.getElementById('control-content');return {viewport:[innerWidth,innerHeight],button:{left:r.left,right:r.right,width:r.width,height:r.height},overflow:document.documentElement.scrollWidth>innerWidth||c.scrollWidth>c.clientWidth+1};});assert.equal(layout.overflow,false);assert.ok(layout.button.height>=44&&layout.button.left>=0&&layout.button.right<=width);report.layouts.push(layout);await page.screenshot({path:new URL(`live-${width}x${height}.png`,output).pathname});
  await toggle.tap();await checkMode(false);await toggle.tap();await checkMode(true);await tab('weather');await page.locator('#light-shimmer').scrollIntoViewIfNeeded();await page.screenshot({path:new URL(`weather-${width}x${height}.png`,output).pathname});
 }
 report.checks.push('Toggle accepts touch at 320, 390 and 1440 px with a 44 px target, no horizontal overflow and reachable Weather shimmer');assert.deepEqual(report.errors,[]);report.result='passed';console.log(JSON.stringify(report,null,2));
}catch(e){report.result='failed';report.error=e.stack;throw e;}finally{await writeFile(new URL('verification.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
