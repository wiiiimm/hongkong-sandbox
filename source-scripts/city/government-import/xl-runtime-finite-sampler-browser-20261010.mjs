const {chromium}=await import(process.env.CITY_PLAYWRIGHT_MODULE||'playwright');
import assert from 'node:assert/strict';
import fs from 'node:fs';
const batch='government-runtime-finite-sampler-integration-20261010',out='docs/astra-city/government-import/'+batch;
assert(!fs.existsSync(out));fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/opt/google/chrome/chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[],failed=[];
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith('http://127.0.0.1:4176')&&r.status()>=400)failed.push({url:r.url(),status:r.status()});});
try{
 await page.goto('http://127.0.0.1:4176/city.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__city?.ready,null,{timeout:90000});
 const moduleResult=await page.evaluate(async()=>{
  const {nativeTerrainSurface}=await import('/city/native-terrain.js?v=20261010-finite1');
  const {withinFiniteTriangleProjection}=await import('/city/exact-finite-triangle-projection.js');
  const tri=[[0,4,0],[1,4,0],[0,4,1]], surface=nativeTerrainSurface({position:tri.flat(),index:[0,1,2]});
  return {inside:surface.height(.25,.25),outside:surface.height(-Number.EPSILON,.25),closedBoundary:surface.height(0,.25),exactInside:withinFiniteTriangleProjection([0,0],[1,0],[0,1],[.25,.25]),exactOutside:withinFiniteTriangleProjection([0,0],[1,0],[0,1],[-Number.EPSILON,.25])};
 });
 assert.equal(moduleResult.inside,4);assert.equal(moduleResult.closedBoundary,4);assert.equal(moduleResult.outside,null);assert.equal(moduleResult.exactInside,true);assert.equal(moduleResult.exactOutside,false);
 const desktop=await page.evaluate(()=>({ready:window.__city.ready,mode:window.__city.state.mode,render:window.__city.state.render}));
 await page.setViewportSize({width:390,height:844});
 await page.waitForFunction(()=>window.innerWidth===390);
 const mobile=await page.evaluate(()=>({ready:window.__city.ready,width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth}));assert.equal(mobile.overflow,false);
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
 const result={passed:true,moduleResult,desktop,mobile,pageErrors:errors,failedLocalRequests:failed,checks:['actual city module chain boots','production finite sampler imports in browser','inside height and closed boundary preserved','outside point rejected without tolerance','desktop and mobile viewport'],sourceGeometryChanges:0,installationCredit:false};
 fs.writeFileSync(out+'/browser.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close();}
