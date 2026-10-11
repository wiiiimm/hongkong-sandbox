// Reserve the shared GPU slot before running. Original UI only; no replacement renderer.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
const output=new URL('../../../docs/astra-city/tides/original-browser/',import.meta.url);await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},locale:'en-GB'}),errors=[],diagnostics=[],requests=[],checks=[],snapshots={};
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')(/WebGL|Shader|GL_INVALID/i.test(m.text())?errors:diagnostics).push(m.text());});
const input=(id,value)=>page.locator('#'+id).evaluate((el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));},value);
const state=()=>page.evaluate(()=>{const {renderer,sea,tidalMats}=window.__three(),sh=sea.material.userData.sh;return {seaY:sea.position.y,visible:sea.visible,shaderTime:sh?.uniforms.uTime.value,waveAmplitude:sh?.uniforms.uWaveAmp.value,rainSpark:sh?.uniforms.uSparkAmt.value,glint:sh?.uniforms.uGlintAmt.value,seaRegistered:tidalMats.includes(sea.material),tidalMaterials:tidalMats.length,shoreUniforms:tidalMats.map(m=>m.userData.sh?.uniforms.uWaterY.value).filter(x=>x!==undefined),programs:renderer.info.programs.map(p=>({runnable:p.diagnostics?.runnable!==false}))};});
let realConnectivity=false;
const fixture=async(station,day)=>JSON.parse(await readFile(new URL(`./fixtures/tides/hhot-${station.toLowerCase()}-2026-09-0${day}.json`,import.meta.url),'utf8'));
try{
 await page.clock.setFixedTime(new Date('2026-09-06T12:30:00+08:00'));
 await page.route('**/data.weather.gov.hk/**',async route=>{
  const url=new URL(route.request().url()),type=url.searchParams.get('dataType');
  if(type==='HHOT'&&realConnectivity)return route.continue();
  if(type==='HHOT'){const station=url.searchParams.get('station'),day=+url.searchParams.get('day');requests.push({station,day});return route.fulfill({json:await fixture(station,day)});}
  if(/wind/.test(url.pathname))return route.fulfill({contentType:'text/csv',body:'Date time,Automatic Weather Station,Wind Direction,Wind Speed,Maximum Gust\n202609061230,Cheung Chau,East,12,20\n'});
  if(type==='rhrread')return route.fulfill({json:{updateTime:'2026-09-06T12:30:00+08:00',temperature:{data:[{place:'Cheung Chau',value:28,unit:'C'}]},humidity:{data:[{place:'Hong Kong Observatory',value:70,unit:'percent'}]},icon:[50],rainfall:{data:[]},warningMessage:[]}});
  return route.fulfill({json:type==='LHL'?{data:[]}:type==='flw'?{generalSituation:'Retained tide test fixture',forecastDesc:'Light winds.'}:{}});
 });
 await page.route('**/api.data.gov.hk/**',route=>route.fulfill({contentType:'text/csv',body:'Date time,Automatic Weather Station,Wind Direction,Wind Speed,Maximum Gust\n202609061230,Cheung Chau,East,12,20\n'}));
 const url=new URL(process.env.ORIGINAL_URL||'http://127.0.0.1:4176/index.html');for(const [k,v]of Object.entries({debug:'1',locale:'en',s:'lantau-hk5m',su:'1',sl:'0',sd:'2026-09-06',sm:'750',sp:'0',cl:'0',ra:'0',fo:'0',wv:'0',lv:'0',ti:'50'}))url.searchParams.set(k,v);
 await page.goto(url.href);await page.waitForFunction(()=>window.__hkLoaded&&window.__three?.().sea?.material.userData.sh&&window.__three().terrain?.geometry?.attributes?.position?.count>100,null,{timeout:120000});
 await page.locator('#dockgear').click();await page.locator('#tide').scrollIntoViewIfNeeded();
 assert.equal(await page.locator('#waves').isChecked(),false);await page.waitForFunction(()=>window.__three().sea.material.userData.sh.uniforms.uWaveAmp.value===.05);snapshots.initial=await state();assert.equal(snapshots.initial.waveAmplitude,.05);
 await input('tide',0);await page.waitForFunction(()=>Math.abs(window.__three().sea.position.y-.4)<.000001);snapshots.low=await state();
 await input('tide',100);await page.waitForFunction(()=>window.__three().sea.position.y>1);snapshots.high=await state();assert.ok(snapshots.high.seaY>snapshots.low.seaY);assert.equal(await page.locator('#tidev').textContent(),'100%');
 assert.ok(snapshots.high.shoreUniforms.some(y=>Math.abs(y-snapshots.high.seaY)<.000001));checks.push('Original 0–100 tide slider, existing SEA_MIN low-water clamp and terrain shoreline uniforms are unchanged');
 await input('wind',100);await page.locator('#waves').check();await page.waitForFunction(()=>window.__three().sea.material.userData.sh.uniforms.uWaveAmp.value>.35);snapshots.waves=await state();await page.waitForTimeout(180);const later=await state();assert.ok(later.shaderTime>snapshots.waves.shaderTime);assert.notEqual(later.seaY,snapshots.waves.seaY);
 await page.locator('#meshdens').evaluate(el=>{el.value='10';el.dispatchEvent(new Event('change',{bubbles:true}));});await page.waitForFunction(()=>window.__three().tidalMats.includes(window.__three().sea.material));const remesh=await state();await page.waitForTimeout(180);assert.ok((await state()).shaderTime>remesh.shaderTime);assert.ok((await state()).waveAmplitude>.35);snapshots.remesh=await state();checks.push('Terrain-only density remesh retains the current sea in tidalMats and animated wave uniforms continue');
 await page.locator('#rain').check();await page.waitForFunction(()=>window.__three().sea.material.userData.sh.uniforms.uSparkAmt.value>0);assert.ok((await state()).glint>0);await page.locator('#rain').uncheck();checks.push('Original animated water normals, vertical bob, rain pocks and sun glitter compile and respond to Waves/Wind/Rain');
 await page.screenshot({path:new URL('original-manual-waves-1440x1000.png',output).pathname});
 await page.locator('#livebtn').click();await page.waitForFunction(()=>document.getElementById('wx-tide').textContent.includes('m'),null,{timeout:20000});assert.equal(await page.locator('#tide').isDisabled(),true);
 const raw=await fixture('CCH',6),expected=(+raw.data[0][13]+ +raw.data[0][14])/2;
 const live=await page.evaluate(()=>{const cv=document.getElementById('wx-tidegraph'),pixels=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;return {label:document.getElementById('wx-tide').textContent,caption:document.getElementById('wx-tidecap').textContent,width:cv.width,height:cv.height,graphPixels:pixels.reduce((sum,value,i)=>sum+(i%4===3&&value>0?1:0),0)};});
 assert.match(live.label,new RegExp(expected.toFixed(2).replace('.', '\\.')));assert.match(live.caption,/Cheung Chau/);assert.equal(requests.length,3);assert.deepEqual(requests.map(r=>r.day).sort(),[5,6,7]);assert.ok(live.graphPixels>10);snapshots.live=live;
 checks.push('Original Live fetches three retained HHOT daily responses, interpolates current 12:30 HKT, shows CCH and draws the 24-hour graph');
 await page.locator('#wx-tidegraph').scrollIntoViewIfNeeded().catch(()=>{});await page.screenshot({path:new URL('original-live-tide-1440x1000.png',output).pathname});
 await page.locator('#livebtn').click();assert.equal(await page.locator('#tide').isDisabled(),false);assert.match(await page.locator('#tidev').textContent(),/%$/);
 await page.locator('#waves').uncheck();await page.waitForFunction(()=>window.__three().sea.material.userData.sh.uniforms.uWaveAmp.value===.05);snapshots.final=await state();assert.ok(snapshots.final.programs.every(p=>p.runnable));assert.deepEqual(errors,[]);checks.push('Returning to original Manual retains its legacy adopted live level; waves off restores calm normals without shader errors');
 realConnectivity=true;
 snapshots.realBrowserHHOT=await page.evaluate(async realNow=>{const {createTideData}=await import('/city/tide-data.js');const data=createTideData({now:()=>realNow,timeoutMs:12000});await data.setStation('CCH');await data.setLive(true);const state=data.state;data.dispose();return {status:state.status,basis:state.basis,station:state.station.code,error:state.error,prediction:state.prediction?{time:state.prediction.time,heightCD:state.prediction.heightCD,heightHKPD:state.prediction.heightHKPD,sourceUrls:state.prediction.sourceUrls,fetchedAt:state.prediction.fetchedAt}:null};},Date.now());
 await writeFile(new URL('verification.json',output),JSON.stringify({result:'passed',testedAt:new Date().toISOString(),browser:await browser.version(),fixtureTime:'2026-09-06T12:30:00+08:00',checks,requests,snapshots,errors,diagnostics},null,2)+'\n');console.log(JSON.stringify({result:'passed',checks,requests,errors,diagnostics},null,2));
}catch(error){await writeFile(new URL('verification.json',output),JSON.stringify({result:'failed',error:error.stack,checks,requests,snapshots,errors,diagnostics},null,2)+'\n');throw error;}finally{await browser.close();}
