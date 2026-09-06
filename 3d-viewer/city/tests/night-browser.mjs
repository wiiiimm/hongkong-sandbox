import {chromium} from 'playwright';
import {formatHour} from '../lighting.js';
import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const evidence=fileURLToPath(new URL('../../../docs/astra-city/night-cycle/',import.meta.url));await mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1}),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
const state=()=>page.evaluate(()=>window.__city.state);
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&s.stream.pending===0;},null,{timeout:90000});
async function time(h){await page.locator('#time').fill(formatHour(h));await page.waitForTimeout(400);}
async function pixels(){return page.evaluate(async()=>{
 const canvas=document.querySelector('#viewport canvas'),image=new Image();image.src=canvas.toDataURL();await image.decode();
 const copy=document.createElement('canvas');copy.width=canvas.width;copy.height=canvas.height;const ctx=copy.getContext('2d');ctx.drawImage(image,0,0);const data=ctx.getImageData(0,0,copy.width,copy.height).data;
 let total=0,warm=0,lit=0,visible=0;for(let i=0;i<data.length;i+=4){const r=data[i],g=data[i+1],b=data[i+2];total+=r*.2126+g*.7152+b*.0722;if(r>105&&r>g*1.13&&g>b*1.15)warm++;if(r*.2126+g*.7152+b*.0722>100)lit++;if(r+g+b>45)visible++;}
 return {luminance:total/(data.length/4),warmPixels:warm,litPixels:lit,visibleFraction:visible/(data.length/4)};
});}
try{
 await page.goto((process.env.CITY_URL||'http://127.0.0.1:4176/city.html')+'?district=kowloon');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:60000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 // Stop ambient animation, then compare the same geometry and camera through the night.
 await page.emulateMedia({reducedMotion:'reduce'});
 const samples={};for(const h of [20,0,2,4,6,12]){await time(h);samples[h]={...await pixels(),lighting:(await state()).lighting};await page.screenshot({path:evidence+`kowloon-${String(h).padStart(2,'0')}00-1440x1000.png`});}
 assert.deepEqual(errors,[]);
 assert.ok(samples[20].litPixels>samples[0].litPixels);
 assert.ok(samples[0].litPixels>samples[2].litPixels);
 assert.ok(samples[2].litPixels>samples[4].litPixels);
 assert.ok(samples[4].litPixels>100,'some actual rendered windows / street lights remain on');
 assert.ok(samples[4].luminance<samples[0].luminance*.8);
 assert.ok(samples[4].visibleFraction>.4,'terrain / city remain navigable in moonlight');
 assert.ok(samples[6].luminance>samples[4].luminance);assert.ok(samples[12].luminance>samples[20].luminance);
 await page.locator('[data-hour="4"]').click();assert.equal((await state()).time,4);assert.equal(await page.locator('#time-output').textContent(),'04:00');assert.ok(await page.locator('body').evaluate(el=>el.classList.contains('night')));
 // Travel at the darkest time: new materials must inherit this clock's uniforms.
 await page.locator('[data-region="lantau"]').click();await page.locator('[data-place="lantau"]').click();await settle();assert.equal((await state()).time,4);assert.ok((await state()).stream.forms>100);await page.screenshot({path:evidence+'tung-chung-0400-1440x1000.png'});
 await page.locator('[data-mode="walk"]').click();await page.waitForFunction(()=>window.__city.state.mode==='walk'&&window.__city.state.movementReady);assert.equal((await state()).collision,false);
 await page.waitForFunction(()=>{const s=window.__city.state;return Math.hypot(...s.camera.map((v,i)=>v-s.position[i]))<12;},null,{timeout:20000});
 await page.keyboard.down('w');await page.waitForFunction(()=>window.__city.state.distance>1.5,null,{timeout:15000});await page.keyboard.up('w');assert.equal((await state()).collision,false);
 await page.screenshot({path:evidence+'tung-chung-walk-0400-1440x1000.png'});await page.keyboard.press('Escape');
 // Manual scrubbing pauses time lapse; crossing midnight must not turn day on.
 await time(23.75);await page.locator('#time-play').click();await page.waitForFunction(()=>window.__city.state.time<1,null,{timeout:15000});assert.equal((await state()).lighting.night,1);
 await page.locator('#about-open').click();const paused=(await state()).time;await page.waitForTimeout(450);assert.equal((await state()).time,paused);await page.locator('#about-close').click();await time(4);assert.equal((await state()).timeLapse,false);
 await page.setViewportSize({width:390,height:844});await page.locator('#panel-toggle').click();await page.locator('[data-hour="20"]').click();assert.equal((await state()).time,20);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:evidence+'night-controls-mobile-390x844.png'});
 await page.locator('[data-hour="4"]').click();const downloadPromise=page.waitForEvent('download');await page.locator('#postcard').click();const download=await downloadPromise;await download.saveAs(evidence+'night-postcard-390x844.png');const png=await readFile(evidence+'night-postcard-390x844.png');assert.equal(png.readUInt32BE(16),390);assert.equal(png.readUInt32BE(20),844);
 assert.deepEqual(errors,[]);
 const result={result:'passed',checks:['full 24-hour cycle','visible window counts fall through midnight to 4 am','4 am retains lit windows and legible surroundings','dawn and daylight return','new sections inherit 4 am lighting','walking at night','time lapse crosses midnight','help pauses time lapse','manual control pauses time lapse','mobile presets and layout','night PNG export'],samples,errors};
 await writeFile(evidence+'verification.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
