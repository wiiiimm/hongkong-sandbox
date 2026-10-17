import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
import {createRequire} from 'node:module';import {mkdir,writeFile} from 'node:fs/promises';import assert from 'node:assert/strict';
const require=createRequire(new URL('../../../3d-viewer/city/package.json',import.meta.url)),{chromium}=require('playwright'),out=new URL('../../../docs/astra-city/comparison-gallery/portrait/',import.meta.url);await mkdir(out,{recursive:true});const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']}),report={errors:[],views:[]};
try{for(const width of [1440,390]){const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'no-preference',hasTouch:width<700});page.on('pageerror',e=>report.errors.push(e.message));await page.goto('http://127.0.0.1:4176/modelling-effort-comparison.html');await page.waitForFunction(()=>window.__trial?.ready);
 assert.deepEqual(await page.evaluate(()=>window.__trial.loadErrors),[]);
 await page.selectOption('#location','ifc');
 const initial=await page.locator('#basic').boundingBox();assert.equal(initial.height,640);assert(initial.height>initial.width);
 for(const height of ['320','900','1200','640']){
  await page.locator('#location-size').fill(height);await page.locator('#location-size').dispatchEvent('input');
  await page.waitForFunction(h=>[...document.querySelectorAll('#views .viewport')].every(n=>n.clientHeight===h),Number(height));
  assert.equal(await page.locator('#location-size-value').innerText(),height+' px');
 }
 await page.locator('#location-size').focus();await page.keyboard.press('ArrowRight');
 await page.waitForFunction(()=>document.querySelector('#basic').clientHeight===660);
 await page.selectOption('#location','hsbc');assert.equal((await page.locator('#basic').boundingBox()).height,660);
 await page.click('#presentation');assert.equal((await page.locator('#basic').boundingBox()).height,660);await page.click('#presentation');
 await page.locator('#location-size').fill('640');await page.locator('#location-size').dispatchEvent('input');
 await page.waitForTimeout(150);
 const cameras=await page.evaluate(()=>window.__trial.cameras);assert(cameras.every(c=>JSON.stringify(c)===JSON.stringify(cameras[0])));
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:new URL('portrait-'+width+'.png',out).pathname,fullPage:true});
assert.equal(await page.locator('#overview,#flythrough').count(),0);await page.click('#gallery-toggle');await page.waitForFunction(()=>window.__gallery?.active&&window.__gallery.drawn>0);assert.equal(await page.locator('.gallery-cell').count(),21);assert.equal(await page.locator('.gallery-canvas').count(),1);assert.equal(await page.evaluate(()=>window.__gallery.playing),false);
 assert.equal(await page.locator('#location-size-control').isVisible(),false);
 const cell=page.locator('.gallery-cell').first(),beforeHover=await cell.boundingBox();await cell.hover();await page.waitForTimeout(250);
 assert.deepEqual(await cell.boundingBox(),beforeHover);assert.equal(await page.locator('.is-hovered').count(),0);
 assert.equal(await cell.evaluate(n=>getComputedStyle(n).transform),'none');

 await page.mouse.move(0,0);
 for(const size of ['100','280']){await page.locator('#gallery-size').fill(size);await page.locator('#gallery-size').dispatchEvent('input');await page.waitForTimeout(100);const h=await page.locator('.gallery-cell').first().evaluate(n=>n.getBoundingClientRect().height);assert.equal(h,Number(size));}
 await page.selectOption('#gallery-motion','fly');
 const opening=await page.evaluate(()=>window.__galleryFlightTest(0)),close=await page.evaluate(()=>window.__galleryFlightTest(6.4));
 const distance=s=>Math.hypot(...s.camera.map((v,i)=>v-s.target[i]));
 assert(opening.every((s,i)=>s.shot==='Approach'&&distance(s)>distance(close[i])*1.5));
 const loop=await page.evaluate(()=>window.__galleryFlightTest(32));assert.deepEqual(loop,opening);
 const samples=[];for(const time of [0,7,14,21,28,32]){const states=await page.evaluate(t=>window.__galleryFlightTest(t),time);assert(states.every(s=>!s.inside&&s.camera.every(Number.isFinite)));samples.push(states[0]);}assert.equal(new Set(samples.map(s=>s.shot)).size,5);assert(Math.max(...samples.map(s=>s.camera[1]))-Math.min(...samples.map(s=>s.camera[1]))>10);assert(new Set(samples.map(s=>s.target[1])).size>2);
 await page.evaluate(()=>window.__galleryFlightTest(7));await page.click('#gallery-play');await page.waitForTimeout(400);await page.click('#gallery-play');await page.waitForTimeout(100);const paused=await page.evaluate(()=>window.__gallery.locations.map(r=>r.camera));await page.waitForTimeout(300);assert.deepEqual(await page.evaluate(()=>window.__gallery.locations.map(r=>r.camera)),paused);await page.locator('#gallery-speed').fill('2');await page.locator('#gallery-speed').dispatchEvent('input');await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>window.__gallery.speed),2);await page.screenshot({path:new URL('cinematic-'+width+'.png',out).pathname});
 for(let i=0;i<3;i++){await page.locator('#gallery-toggle').scrollIntoViewIfNeeded();await page.click('#gallery-toggle');assert.equal(await page.locator('.gallery-canvas').count(),0);assert.equal(await page.evaluate(()=>window.__gallery.active),false);await page.setViewportSize({width,height:1000+i*10});await page.waitForTimeout(100);assert.equal(await page.locator('.gallery-canvas').count(),0);assert(await page.locator('#views').isVisible());assert(await page.locator('#location-size-control').isVisible());assert.equal((await page.locator('#basic').boundingBox()).height,640);await page.selectOption('#location','hsbc');assert.equal(await page.evaluate(()=>window.__trial.id),'hsbc');await page.screenshot({path:new URL('exit-'+width+'.png',out).pathname});await page.click('#gallery-toggle');await page.waitForFunction(()=>window.__gallery.active);assert.equal(await page.locator('.gallery-canvas').count(),1);}
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);report.views.push({width,cells:21,sharedRenderers:1,exitCycles:3,noCanvasAfterExit:true,sizeHeights:[100,280],locationHeights:[320,900,1200,640],keyboardHeight:660,defaultPortrait:true,noHoverEnlargement:true,locationHeightRestored:true,pauseStable:true,cinematicSamples:samples});await page.close();}assert.deepEqual(report.errors,[]);}finally{await browser.close();await writeFile(new URL('verification.json',out),JSON.stringify(report,null,2)+'\n');}console.log('Passed portrait location height, keyboard control, gallery hover removal, exit, size and cinematic checks.');
