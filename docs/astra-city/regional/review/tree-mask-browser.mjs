import {chromium} from '../../../../3d-viewer/city/node_modules/playwright/index.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=new URL('../../../../',import.meta.url),payload=JSON.parse(await readFile(new URL('3d-viewer/city/data/regional/urban.json',base),'utf8'));
const pitches=payload.surfaces.filter(s=>s.kind==='pitch'&&s.rings[0].some(([x,z])=>x>2600&&x<3400&&z>0&&z<1200));
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
let release;const gate=new Promise(resolve=>release=resolve);
try{
 // A getter appended only to this test's script response exposes existing matrices.
 // No production file or city behaviour is changed by the instrumentation.
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__regionalReview",{get(){return {stream,regionalDetail};}});\n'});});
 await page.route('**/city/data/regional/urban.json',async route=>{await gate;await route.continue();});
 const count=()=>page.evaluate(async pitches=>{const {inPolygon}=await import('/city/geo.js');let treesInPark=0,insidePitch=0;const tiles=[];for(const [id,e] of window.__regionalReview.stream.cache.entries){const parks=e.data.parks.filter(p=>p.name==='Victoria Park');if(!parks.length)continue;tiles.push(id);const mesh=e.nature.group.children.find(o=>o.isInstancedMesh),a=mesh.instanceMatrix.array;for(let i=0;i<mesh.count;i++){const x=a[i*16+12],z=a[i*16+14];if(!parks.some(p=>inPolygon(x,z,p.rings)))continue;treesInPark++;if(pitches.some(p=>inPolygon(x,z,p.rings)))insidePitch++;}}return {treesInPark,insidePitch,tiles};},pitches);
 await page.goto('http://127.0.0.1:4176/city.html?district=section-02-4');await page.waitForFunction(()=>window.__city?.ready&&window.__regionalReview?.stream.cache.entries.has('1_0')&&window.__regionalReview?.stream.cache.entries.has('2_0'),null,{timeout:19000});const before=await count();assert.ok(before.insidePitch>0,'delayed urban response must leave existing generated trees to test remasking');release();
 await page.waitForFunction(()=>{const s=window.__city.state;return s.regional.packages===3&&s.regional.pending===0&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0;},null,{timeout:60000});await page.locator('#loading').waitFor({state:'hidden'});const after=await count();assert.equal(after.insidePitch,0);assert.ok(after.treesInPark>0,'ordinary park trees should remain');
 await page.locator('#tab-sky').click();await page.locator('#time').fill('15:00');await page.locator('#tab-places').click();await page.waitForTimeout(200);await page.screenshot({path:new URL('victoria-park-masked-1440x1000.png',import.meta.url).pathname});
 // Travel far enough to evict the park tiles, then verify newly generated trees.
 for(const [region,id] of [['ntwest','tinshuiwai'],['nteast','shatin']]){await page.locator(`[data-region="${region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling&&window.__city.state.stream.pending===0,null,{timeout:90000});}assert.equal(await page.evaluate(()=>window.__regionalReview.stream.cache.entries.has('1_0')),false);
 await page.locator('[data-region="island"]').click();await page.locator('[data-place="section-02-4"]').click();await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling&&window.__city.state.stream.pending===0,null,{timeout:90000});const reloaded=await count();assert.equal(reloaded.insidePitch,0);
 await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.waitForTimeout(200);await page.screenshot({path:new URL('victoria-park-masked-mobile-390x844.png',import.meta.url).pathname});
 assert.deepEqual(errors,[]);const result={result:'passed',beforeUrbanResponse:before,afterUrbanResponse:after,afterEvictionAndReload:reloaded,errors};await writeFile(new URL('tree-mask-browser.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{release();await browser.close();}
