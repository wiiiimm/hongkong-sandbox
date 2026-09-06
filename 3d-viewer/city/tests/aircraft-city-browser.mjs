import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {AIRCRAFT} from '../aircraft.js';

const evidence=new URL('../../../docs/astra-city/aircraft/',import.meta.url);await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true}),errors=[],checks=[],aircraft=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
const url=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');url.searchParams.set('district','kowloon');
const state=p=>p.evaluate(()=>window.__city.state);
const ready=async p=>{await p.goto(url.href);await p.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await p.locator('#loading').waitFor({state:'hidden'});await p.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});};
const fly=async p=>{await p.locator('[data-mode="fly"]').click();await p.waitForFunction(()=>window.__city.state.mode==='fly'&&window.__city.state.movementReady,null,{timeout:120000});await p.waitForTimeout(1200);};
const loaded=(p,id)=>p.waitForFunction(id=>window.__city.state.aircraft.id===id&&window.__city.state.aircraft.status==='ready',id,{timeout:45000});
const screenshot=(p,name)=>p.screenshot({path:new URL(name,evidence).pathname});
const overlap=(a,b)=>a&&b&&Math.min(a.x+a.width,b.x+b.width)>Math.max(a.x,b.x)+1&&Math.min(a.y+a.height,b.y+b.height)>Math.max(a.y,b.y)+1;
const visibleRect=async(p,selector)=>{const e=p.locator(selector);return await e.isVisible()?e.boundingBox():null;};
try{
 await ready(page);await fly(page);assert.equal(await page.locator('#aircraft-model option').count(),7);
 for(const definition of AIRCRAFT){
  await page.locator('#aircraft-model').selectOption(definition.id);await loaded(page,definition.id);await page.waitForTimeout(550);
  const s=await state(page),status=await page.locator('#aircraft-status').textContent();
  assert.equal(s.mode,'fly');assert.equal(await page.locator('#aircraft-model option:checked').textContent(),definition.label);assert.equal(s.aircraft.dimensions.length,definition.length);assert.equal(s.aircraft.dimensions.wingspan,definition.wingspan);
  assert.ok(s.aircraft.drawMeshes>0);assert.match(status,new RegExp(definition.length.toFixed(1).replace('.','\\.')+' m long'));assert.match(status,new RegExp(definition.wingspan.toFixed(1).replace('.','\\.')+' m wingspan'));
  if(definition.approximate)assert.match(status,/Approx\./);if(definition.kind==='ufo')assert.match(status,/fictional/);
  assert.equal(await page.locator('#aircraft-retry').isVisible(),false);
  await screenshot(page,`city-${definition.id}-1440x1000.png`);aircraft.push({...s.aircraft,uiStatus:status,camera:s.camera,position:s.position});
 }
 checks.push('all seven city selector choices load with correct labels and calibrated dimensions');
 await page.locator('#viewport canvas').focus();const start=(await state(page)).position[1];await page.keyboard.down('KeyW');await page.waitForFunction(y=>window.__city.state.position[1]>y+8,start,{timeout:15000});await page.keyboard.up('KeyW');
 await page.keyboard.press('KeyC');await page.waitForFunction(()=>window.__city.state.firstPerson);await page.waitForTimeout(450);await screenshot(page,'city-pilots-eye-1440x1000.png');await page.keyboard.press('KeyC');assert.equal((await state(page)).firstPerson,false);checks.push('climb and pilots-eye/chase camera controls work in the city');
 await page.locator('[data-mode="orbit"]').click();assert.equal(await page.locator('#flight-controls').isVisible(),false);assert.equal((await state(page)).aircraft.id,'ufo');await fly(page);assert.equal((await state(page)).aircraft.id,'ufo');checks.push('aircraft choice persists across Explore and Fly transitions');
 // Keep the older model request pending until the latest choice has loaded.
 let release,arrived;const gate=new Promise(resolve=>release=resolve),entered=new Promise(resolve=>arrived=resolve);
 await page.route('**/plane-747.glb',async route=>{arrived();await gate;await route.continue();});
 await page.locator('#aircraft-model').selectOption('cx747');await entered;await page.locator('#aircraft-model').selectOption('prop');await loaded(page,'prop');const lateResponse=page.waitForResponse(response=>response.url().endsWith('/plane-747.glb'));release();await(await lateResponse).finished();await page.waitForTimeout(600);
 assert.equal((await state(page)).aircraft.id,'prop');assert.equal(await page.locator('#aircraft-model').inputValue(),'prop');await page.unroute('**/plane-747.glb');checks.push('a late model response cannot replace the latest aircraft selection');
 await page.locator('#panel-toggle').click();await page.locator('#tab-sky').click();await page.locator('#time').fill('00:00');await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>window.__city.state.lighting.shimmer===0&&window.__city.state.lighting.night>.99);await page.locator('#panel-toggle').click();await page.waitForTimeout(250);await screenshot(page,'city-midnight-reduced-motion-1440x1000.png');checks.push('midnight flight and reduced-motion settings integrate without graphics errors');
 // A fresh tab makes the deliberate network failure independent of earlier model caching.
 const retryPage=await browser.newPage({viewport:{width:1440,height:1000}}),retryErrors=[],failedRequests=[];
 retryPage.on('pageerror',e=>retryErrors.push(e.message));retryPage.on('console',message=>{if(message.type()==='error'&&!message.location().url.endsWith('/plane-a350.glb'))retryErrors.push(message.text());});retryPage.on('requestfailed',r=>failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 await retryPage.route('**/plane-a350.glb',r=>r.abort('failed'));await ready(retryPage);await fly(retryPage);await retryPage.locator('#aircraft-model').selectOption('a350');
 await retryPage.waitForFunction(()=>window.__city.state.aircraft.id==='a350'&&window.__city.state.aircraft.status==='fallback');assert.equal(await retryPage.locator('#aircraft-retry').isVisible(),true);assert.match(await retryPage.locator('#aircraft-status').textContent(),/Detailed aircraft unavailable/);assert.equal((await state(retryPage)).mode,'fly');await retryPage.waitForTimeout(1200);await screenshot(retryPage,'city-model-fallback-1440x1000.png');
 await retryPage.unroute('**/plane-a350.glb');await retryPage.locator('#aircraft-retry').click();await loaded(retryPage,'a350');assert.equal(await retryPage.locator('#aircraft-retry').isVisible(),false);assert.ok(failedRequests.some(r=>r.url.endsWith('/plane-a350.glb')));assert.deepEqual(retryErrors,[]);await retryPage.waitForTimeout(1200);await screenshot(retryPage,'city-model-retry-1440x1000.png');await retryPage.close();checks.push('model request failure retains flight fallback and actual Retry loads the detailed aircraft');
 await page.bringToFront();
 for(const width of [390,320]){
  await page.setViewportSize({width,height:844});await page.locator('#aircraft-model').selectOption('cx777');await loaded(page,'cx777');await page.waitForTimeout(350);
  const flight=await visibleRect(page,'#flight-controls');assert.ok(flight&&flight.x>=0&&flight.x+flight.width<=width);
  for(const selector of ['#journey','.view-tools','.mode-dock','#touch-controls'])assert.ok(!overlap(flight,await visibleRect(page,selector)),`Aircraft selector overlaps ${selector} at ${width}px`);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  const touchContrast=await page.locator('#touch-controls button').first().evaluate(element=>{const style=getComputedStyle(element),rgb=value=>value.match(/[\d.]+/g).slice(0,3).map(Number),luminance=value=>rgb(value).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0),a=luminance(style.color),b=luminance(style.backgroundColor);return(Math.max(a,b)+.05)/(Math.min(a,b)+.05);});assert.ok(touchContrast>=3,'night movement icons remain legible');await screenshot(page,`city-mobile-${width}x844.png`);
  await page.locator('#panel-toggle').click();await page.locator('#tab-weather').click();await screenshot(page,`city-mobile-settings-${width}x844.png`);
  assert.ok(!overlap(await visibleRect(page,'#flight-controls'),await visibleRect(page,'#explorer')),`Aircraft selector overlaps the open settings panel at ${width}px`);assert.equal(await page.locator('#touch-controls').isVisible(),false,'movement buttons cannot obscure open settings');assert.ok(!overlap(await visibleRect(page,'#control-hint'),await visibleRect(page,'#explorer')),'movement hint cannot obscure the weather controls');
  await page.locator('#tab-sky').click();assert.equal(await page.locator('#panel-sky').isVisible(),true);await page.locator('#panel-toggle').click();checks.push(`mobile aircraft/settings layout at ${width}px has no overlaps or overflow`);
 }
 assert.deepEqual(errors,[]);const result={result:'passed',testedAt:new Date().toISOString(),url:url.href,browser:await browser.version(),viewports:[{width:1440,height:1000},{width:390,height:844},{width:320,height:844}],checks,aircraft,failedRequests,errors,retryErrors};await writeFile(new URL('city-verification.json',evidence),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}catch(error){console.error(JSON.stringify({completedChecks:checks,errors,aircraft:aircraft.map(a=>a.id)},null,2));throw error;}finally{await browser.close();}
