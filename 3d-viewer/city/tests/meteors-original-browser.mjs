// Original HKS-85 UI smoke after extraction to the shared implementation.
// Uses only the original viewer's existing ?debug hooks and normal controls.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const output=fileURLToPath(new URL('../../../docs/astra-city/meteors/original-browser/',import.meta.url));await mkdir(output,{recursive:true});
const remaining=process.argv.includes('--remaining');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,locale:'en-GB'}),report={scope:remaining?'remaining control checks':'full original smoke',startedAt:new Date().toISOString(),browser:await browser.version(),errors:[],diagnostics:[]};
page.on('pageerror',error=>report.errors.push(error.message));page.on('console',message=>{if(message.type()==='error')(/WebGL|Shader|GL_INVALID/i.test(message.text())?report.errors:report.diagnostics).push(message.text());});
const input=async(id,value)=>page.locator('#'+id).evaluate((el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));},value);
const pool=()=>page.evaluate(()=>({total:window.__meteors().length,active:window.__meteors().filter(m=>m.active).length,visible:window.__meteors().filter(m=>m.line.visible&&m.line.material.opacity>0).length,fade:window.__sky.starFade,groups:window.__three().scene.children.filter(g=>g.name==='Shooting stars').length}));
try{
 const url=new URL(process.env.ORIGINAL_URL||'http://127.0.0.1:4176/index.html');for(const [k,v]of Object.entries({debug:'1',locale:'en',su:'1',sl:'0',sd:'2026-09-06',sm:'1260',sh:'1',shr:'18',sp:'0',cl:'0',ra:'0',fo:'0',wv:'0',lv:'0'}))url.searchParams.set(k,v);
 await page.goto(url.href);await page.waitForFunction(()=>window.__hkLoaded&&window.__meteors?.().length===14&&window.__three?.().terrain?.geometry?.attributes?.position?.count>100,null,{timeout:120000});
 await page.locator('#dockgear').click();
 if(!remaining){
 assert.equal(await page.locator('#shootstars').isChecked(),true);assert.equal(await page.locator('#meteorrate').inputValue(),'18');assert.equal(await page.locator('#meteorratev').textContent(),'calm');
 for(const [value,label]of [[0,'off'],[18,'calm'],[50,'romantic'],[100,'apocalypse']]){await input('meteorrate',value);assert.equal(await page.locator('#meteorratev').textContent(),label);}
 await page.locator('#stargazebtn').click();await page.waitForFunction(()=>document.body.classList.contains('stargazing')&&window.__sky.starFade>=.55);await page.waitForFunction(()=>window.__meteors().filter(m=>m.active).length>=3,null,{timeout:12000});report.storm=await pool();assert.equal(report.storm.total,14);assert.equal(report.storm.groups,1);
 await page.locator('#meteorrate').scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>{const camera=window.__three().camera;return window.__meteors().some(m=>{if(!m.active||m.line.material.opacity<.4)return false;const v=m.A.clone().fromBufferAttribute(m.line.geometry.attributes.position,0);m.line.localToWorld(v);v.project(camera);return v.x>-.4&&v.x<.8&&Math.abs(v.y)<.8&&v.z>0&&v.z<1;});},null,{timeout:18000});
 await page.screenshot({path:output+'original-apocalypse-1440x1000.png'});
 await page.locator('#shootstars').uncheck();await page.waitForFunction(()=>window.__meteors().every(m=>!m.active&&!m.line.visible));assert.equal(await page.locator('#meteorrate').isDisabled(),true);report.off=await pool();
 await page.waitForFunction(()=>new URL(location.href).searchParams.get('sh')==='0'&&new URL(location.href).searchParams.get('shr')==='100',null,{timeout:5000});report.sharedLink={sh:'0',shr:'100'};
 await page.locator('#shootstars').check();await page.waitForFunction(()=>window.__meteors().filter(m=>m.active).length>=3,null,{timeout:12000});
 await page.locator('#stargazebtn').click();await page.waitForFunction(()=>!document.body.classList.contains('stargazing'));
 }else{await input('meteorrate',100);}
 await page.locator('#skymode').selectOption('off');await page.waitForFunction(()=>window.__meteors().every(m=>!m.active));assert.equal(await page.locator('#shootstars').isDisabled(),true);assert.equal(await page.locator('#meteorrate').isDisabled(),true);
 report.skyOff=await pool();
 await page.locator('#skymode').selectOption('fixed');await input('skytime',720);await page.waitForFunction(()=>window.__sky.starFade<.55&&window.__meteors().every(m=>!m.active),null,{timeout:10000});report.day=await pool();assert.equal(await page.locator('#shootstars').isDisabled(),false);assert.equal(await page.locator('#meteorrate').isDisabled(),false);
 await page.locator('#langbtn').click();await page.waitForFunction(()=>document.querySelector('#meteorratev').textContent==='末日');report.translatedLabel='末日';
 assert.deepEqual(report.errors,[]);report.result='passed';report.checks=remaining?['sky-off hides trails and disables controls','daylight hides trails but permits controls','Traditional Chinese rate label retained']:['default enabled/rate18 and original 0–100 labels','one 14-trail shared pool','on-screen original Stargaze meteor draw','toggle immediately clears pool and disables rate','sh/shr shared-link state retained','sky-off hides trails and disables controls','daylight hides trails but permits controls','Traditional Chinese rate label retained'];
}catch(error){report.result='failed';report.failure=error.stack;throw error;}finally{report.finishedAt=new Date().toISOString();await writeFile(output+(remaining?'remaining-verification.json':'verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));await browser.close();}
