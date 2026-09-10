/** Focused production-dialog test. The 3D renderer is excluded; see live-dialog.png for full-page smoke evidence. */
import {createRequire} from 'node:module';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browserExecutable} from '../../../source-scripts/city/landmark-preflight/browser-runtime.mjs';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const out=new URL('../../../docs/astra-city/enhancement-screening/',import.meta.url);
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
  assert.equal(await page.locator('.progress-tier').count(),4);
  const state=await page.evaluate(()=>({total:document.querySelector('#progress-total').textContent,ready:document.querySelector('#progress-enhanced').textContent,overflow:document.documentElement.scrollWidth>innerWidth,dialogOverflow:document.querySelector('#building-progress').scrollWidth>document.querySelector('#building-progress').clientWidth,bars:[...document.querySelectorAll('.progress-tier meter')].map(m=>({value:m.value,max:m.max,label:m.getAttribute('aria-valuetext')}))}));
  assert(!state.overflow&&!state.dialogOverflow);assert.equal(state.bars.reduce((n,b)=>n+b.value,0),stats.totalForms);
  assert(state.bars.every(b=>b.label&&b.max===stats.totalForms));
  await page.screenshot({path:new URL(name+'.png',out).pathname});
  await page.locator('#building-progress summary').click();assert(await page.getByText('Changes to a screened building', {exact:false}).isVisible());
  await page.keyboard.press('Escape');assert.equal(await page.locator('#building-progress').evaluate(d=>d.open),false);
  report.views.push({name,...state});await page.close();
 }
 for(const scenario of ['unavailable','stale','empty','mixed','invalid']){
  const data=scenario==='unavailable'?null:scenario==='stale'?{...stats,manifestDigest:'stale'}:scenario==='empty'?{...stats,totalForms:0,breakdown:{enhanced:0,goodToGo:0,enhancementRequired:0,unassessed:0}}:scenario==='mixed'?{...stats,totalForms:100,breakdown:{enhanced:20,goodToGo:50,enhancementRequired:10,unassessed:20}}:{...stats,totalForms:1};
  const page=await pageFor({width:390,height:844},data);
  if(scenario==='empty'){assert.equal(await page.locator('#progress-percent').textContent(),'Not available');assert(await page.locator('#progress-meter').isHidden());}
  else if(scenario==='mixed'){assert.equal(await page.locator('#progress-percent').textContent(),'70.00%');assert.equal(await page.locator('#progress-enhanced').textContent(),'70');assert.equal(await page.locator('#progress-bar-goodToGo').evaluate(e=>e.value),50);}
  else assert(await page.locator('#progress-values').isHidden());
  report.checks.push(scenario);await page.close();
 }
 assert.deepEqual(report.errors,[]);console.log(JSON.stringify(report));
}finally{await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
