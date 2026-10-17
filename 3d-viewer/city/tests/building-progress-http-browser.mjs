import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
const root=new URL('../../../',import.meta.url),out=new URL('docs/astra-city/building-progress-http-20261006/',root);
const stats=JSON.parse(await readFile(new URL('3d-viewer/city/data/building-progress.json',root)));
const origin=process.env.PROGRESS_HTTP_ORIGIN||'http://100.89.99.102:4176';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell',args:['--no-sandbox']});
const report={origin,updatedAt:stats.updatedAt,manifestDigest:stats.manifestDigest,cases:[],errors:[]};
await mkdir(out,{recursive:true});
try{
 for(const [mode,width] of [['available',1280],['available',390],['stale',390],['missing',390]]){
  const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
  const page=await context.newPage();page.on('pageerror',error=>report.errors.push(error.message));
  await page.route('**/city/app.js*',route=>route.fulfill({contentType:'text/javascript',body:`
   import {bindBuildingProgress} from './building-progress.js?v=20261006-progress-http1';
   const manifest=await (await fetch('city/data/manifest.json',{cache:'no-cache'})).json();
   await bindBuildingProgress(manifest);document.getElementById('loading').remove();window.__progressReady=true;
  `}));
  if(mode!=='available')await page.route('**/city/data/building-progress.json',route=>route.fulfill(mode==='missing'?{status:503,body:''}:{contentType:'application/json',body:JSON.stringify({...stats,manifestDigest:'0'.repeat(64)})}));
  await page.goto(origin+'/city.html');await page.waitForFunction(()=>window.__progressReady,null,{timeout:30000});
  const security=await page.evaluate(()=>({secureContext:isSecureContext,subtle:!!globalThis.crypto?.subtle}));
  assert.equal(security.secureContext,false,'Use an actual nonsecure HTTP/IP origin');assert.equal(security.subtle,false);
  await page.locator('#progress-open').click();
  const state=await page.evaluate(()=>({chipTotal:document.getElementById('progress-chip-total').textContent,chip:document.getElementById('progress-chip').textContent,
   total:document.getElementById('progress-total').textContent,government:document.getElementById('progress-enhanced').textContent,
   valuesHidden:document.getElementById('progress-values').hidden,status:document.getElementById('progress-status').textContent,
   overflow:document.documentElement.scrollWidth>innerWidth}));
  if(mode==='available'){
   assert.equal(state.chipTotal,stats.totalForms.toLocaleString('en-HK'));assert.equal(state.chip,stats.reviewedEnhancedForms.toLocaleString('en-HK'));
   assert.equal(state.total,state.chipTotal);assert.equal(state.government,stats.government.ready.toLocaleString('en-HK'));assert.equal(state.valuesHidden,false);assert.equal(state.overflow,false);
   await page.screenshot({path:new URL('available-'+width+'.png',out).pathname});
  }else{assert.equal(state.valuesHidden,true);assert.equal(state.chipTotal,'Updating');}
  report.cases.push({mode,width,...security,...state,passed:true});await context.close();
 }
 assert.deepEqual(report.errors,[]);report.passed=true;
}finally{await browser.close();await writeFile(new URL('result.json',out),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({passed:report.passed,cases:report.cases.length,errors:report.errors,total:stats.totalForms,enhanced:stats.reviewedEnhancedForms}));
