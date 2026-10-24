import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(new URL('../../../3d-viewer/city/package.json',import.meta.url)),{chromium}=require('playwright');
const oldScript=execFileSync('git',['show','897a6fcb:3d-viewer/city/whampoa-comparison.js'],{encoding:'utf8'});
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const report={};
try{
 // Reproduce the previous UI/entry-script mismatch, then prove the new URL avoids it.
 const old=await browser.newPage(),errors=[];old.on('pageerror',e=>errors.push(e.message));
 await old.route('**/whampoa-comparison.js*',r=>r.fulfill({contentType:'text/javascript',body:oldScript}));
 await old.goto('http://127.0.0.1:4176/modelling-effort-comparison.html');
 await old.waitForFunction(()=>document.querySelector('#load-status')?.getAttribute('role')==='alert');
 report.oldScriptMismatch=await old.locator('#load-message').innerText();assert.match(report.oldScriptMismatch,/null|undefined/);await old.close();
 const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));let staleHits=0;
 await page.route('**/city/whampoa-comparison.js',r=>{staleHits++;return r.fulfill({contentType:'text/javascript',body:oldScript});});
 await page.goto('http://127.0.0.1:4176/modelling-effort-comparison.html');await page.waitForFunction(()=>window.__trial?.ready);
 assert.equal(staleHits,0);assert.equal(await page.locator('#load-status').isVisible(),false);report.versionedStartup=true;await page.close();
 const fail=await browser.newPage();fail.on('pageerror',e=>errors.push(e.message));
 await fail.route('**/*.glb.gz',r=>r.fulfill({status:503,body:'Temporary failure'}));
 await fail.goto('http://127.0.0.1:4176/modelling-effort-comparison.html');await fail.waitForFunction(()=>window.__trial?.ready);
 assert((await fail.evaluate(()=>window.__trial.counts[0]))>0);assert((await fail.evaluate(()=>window.__trial.loadErrors.length))>0);
 assert(await fail.locator('#load-retry').isVisible());await fail.click('#gallery-toggle');await fail.waitForFunction(()=>window.__gallery?.drawn>0);
 report.failedDownloadsPreserveBaselineAndGallery=true;
 await fail.unroute('**/*.glb.gz');await fail.click('#gallery-toggle');await fail.click('#load-retry');await fail.waitForFunction(()=>window.__trial?.ready&&window.__trial.loadErrors.length===0);
 report.retryRecoversModels=true;await fail.close();
 const fatal=await browser.newPage();await fatal.route('**/manifest.json',r=>r.fulfill({status:503,body:'Unavailable'}));await fatal.goto('http://127.0.0.1:4176/modelling-effort-comparison.html');await fatal.waitForFunction(()=>document.querySelector('#load-status')?.getAttribute('role')==='alert');assert.match(await fatal.locator('#load-message').innerText(),/HTTP 503/);report.manifestFailureVisible=true;await fatal.close();
 assert.deepEqual(errors,[]);report.pageErrors=errors;
}finally{await browser.close();await writeFile(new URL('../../../docs/astra-city/comparison-gallery/fixes/startup-verification.json',import.meta.url),JSON.stringify(report,null,2)+'\n');}
console.log(report);
