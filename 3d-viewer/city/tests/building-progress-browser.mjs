/** Production dialog scenarios plus a real City startup smoke check. */
import {createRequire} from 'node:module';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browserExecutable} from '../../../source-scripts/city/landmark-preflight/browser-runtime.mjs';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const out=new URL('../../../docs/astra-city/building-progress-government/',import.meta.url);
const root=new URL('../../../',import.meta.url);
await mkdir(out,{recursive:true});
const stats=JSON.parse(await readFile(new URL('3d-viewer/city/data/building-progress.json',root)));
const browser=await chromium.launch({executablePath:browserExecutable(chromium),headless:true,args:['--no-sandbox']});
const report={scope:'Actual city HTML/CSS and progress module; 3D startup excluded',views:[],checks:[],errors:[]};
async function pageFor(viewport,data=stats){
 const page=await browser.newPage({viewport});page.on('pageerror',e=>report.errors.push(e.message));
 // Load the actual dialog module and map manifest without waiting for unrelated terrain/model streaming.
 await page.route('**/city/app.js*',route=>route.fulfill({contentType:'text/javascript',body:`
 import {bindBuildingProgress} from './building-progress.js';
 const manifest=await (await fetch('city/data/manifest.json')).json();
 document.getElementById('loading').hidden=true;
 await bindBuildingProgress(manifest);`}));
 await page.route('**/city/data/building-progress.json',route=>route.fulfill(data===null?{status:503,body:''}:{contentType:'application/json',body:JSON.stringify(data)}));
 await page.goto('http://127.0.0.1:4176/city.html');
 await page.waitForFunction(()=>document.querySelector('#progress-chip').textContent!=='…');
 await page.locator('#progress-open').click();return page;
}
try{
 for(const [name,width,height] of [['desktop',1280,900],['mobile',390,844],['narrow',320,740]]){
  const page=await pageFor({width,height});await page.locator('#progress-values').waitFor({state:'visible'});
  assert.equal(await page.locator('.progress-tier:visible').count(),3);
  const state=await page.evaluate(()=>({total:document.querySelector('#progress-total').textContent,enhanced:document.querySelector('#progress-enhanced').textContent,available:document.querySelector('#progress-available').textContent,remaining:document.querySelector('#progress-remaining').textContent,percent:document.querySelector('#progress-percent').textContent,chip:document.querySelector('#progress-chip').textContent,chipTotal:document.querySelector('#progress-chip-total').textContent,meter:{value:document.querySelector('#progress-meter').value,max:document.querySelector('#progress-meter').max},overflow:document.documentElement.scrollWidth>innerWidth,dialogOverflow:document.querySelector('#building-progress').scrollWidth>document.querySelector('#building-progress').clientWidth,bars:[...document.querySelectorAll('.progress-tier meter')].map(m=>({value:m.value,max:m.max,label:m.getAttribute('aria-valuetext')}))}));
  assert(!state.overflow&&!state.dialogOverflow);assert.equal(state.bars.reduce((n,b)=>n+b.value,0),stats.totalForms);
  assert(state.bars.every(b=>b.label&&b.max===stats.totalForms));
  assert.equal(state.meter.value,stats.government.ready);assert.equal(state.meter.max,stats.government.available);assert.equal(state.enhanced,stats.breakdown.enhanced.toLocaleString('en-HK'));
  assert.equal(state.available,stats.government.available.toLocaleString('en-HK'));assert.equal(state.remaining,stats.government.remaining.toLocaleString('en-HK'));
  assert.equal(await page.locator('#progress-outside').isVisible(),stats.government.enhancedOutside>0);
  await page.screenshot({path:new URL(name+'.png',out).pathname});
  await page.locator('#building-progress summary').click();assert(await page.getByText('Changed source identities', {exact:false}).isVisible());
  await page.keyboard.press('Escape');assert.equal(await page.locator('#building-progress').evaluate(d=>d.open),false);
  await page.screenshot({path:new URL(name+'-header.png',out).pathname});
  report.views.push({name,...state});await page.close();
 }
 for(const scenario of ['unavailable','stale','empty','mixed','invalid','no-source','bad-source-count']){
  const empty={totalForms:0,breakdown:{enhanced:0,goodToGo:0,enhancementRequired:0,unassessed:0},government:{available:0,enhanced:0,goodToGo:0,ready:0,remaining:0,noMatchedSource:0,enhancedOutside:0,goodToGoOutside:0}};
  const mixed={totalForms:100,breakdown:{enhanced:20,goodToGo:10,enhancementRequired:10,unassessed:60},government:{available:50,enhanced:15,goodToGo:5,ready:20,remaining:30,noMatchedSource:50,enhancedOutside:5,goodToGoOutside:5}};
  const data=scenario==='unavailable'?null:scenario==='stale'?{...stats,manifestDigest:'stale'}:scenario==='empty'?{...stats,...empty}:scenario==='mixed'?{...stats,...mixed}:scenario==='no-source'?{...stats,...empty,totalForms:10,breakdown:{...empty.breakdown,unassessed:10},government:{...empty.government,noMatchedSource:10}}:scenario==='bad-source-count'?{...stats,government:{...stats.government,remaining:1}}:{...stats,totalForms:1};
  const page=await pageFor({width:390,height:844},data);
  if(scenario==='empty'||scenario==='no-source'){assert.equal(await page.locator('#progress-percent').textContent(),'Not available');assert(await page.locator('#progress-meter').isHidden());}
  else if(scenario==='mixed'){assert.equal(await page.locator('#progress-percent').textContent(),'40.00% done');assert.equal(await page.locator('#progress-enhanced').textContent(),'20');assert.equal(await page.locator('#progress-bar-goodToGo').evaluate(e=>e.value),10);assert.equal(await page.locator('#progress-meter').evaluate(e=>e.max),50);}
  else assert(await page.locator('#progress-values').isHidden());
  report.checks.push(scenario);await page.close();
 }
 // The unmodified City entry point must also bind the counter beside the running renderer.
 const live=await browser.newPage({viewport:{width:1280,height:900}}),liveErrors=[];
 live.on('pageerror',e=>liveErrors.push(e.message));
 await live.goto('http://127.0.0.1:4176/city.html',{waitUntil:'domcontentloaded'});
 await live.waitForFunction(()=>document.querySelector('#progress-chip')?.textContent.includes('enhanced'),{},{timeout:60000});
 await live.locator('#loading').waitFor({state:'hidden',timeout:60000});
 await live.locator('#progress-open').click();
 assert.equal(await live.locator('#progress-total').textContent(),stats.totalForms.toLocaleString('en-HK'));
 await live.screenshot({path:new URL('live-dialog.png',out).pathname});
 report.live={scope:'Unmodified City startup, renderer and progress dialog',errors:liveErrors,chip:await live.locator('#progress-chip').textContent()};
 assert.deepEqual(liveErrors,[]);await live.close();
 assert.deepEqual(report.errors,[]);console.log(JSON.stringify(report));
}finally{await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
