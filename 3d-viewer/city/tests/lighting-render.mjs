import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
try{
 const base=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');
 await page.route('**/lighting-fixture.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><title>Building lighting verification</title>'}));await page.goto(base.origin+'/lighting-fixture.html');
 const result=await page.evaluate(async()=>{
  const THREE=await import('/vendor/three.module.js'),{makeBuildings}=await import('/city/world.js'),{cityLighting}=await import('/city/lighting.js');
  const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera(-195,195,130,-130,.1,10000),renderer=new THREE.WebGLRenderer();renderer.setSize(768,512);renderer.toneMapping=THREE.ACESFilmicToneMapping;
  scene.add(new THREE.AmbientLight('#c1d8e4',.1));
  const uniforms={night:{value:1},activity:{value:new Float32Array(4)},retail:{value:0},elapsed:{value:0},shimmer:{value:1}};
  const features=[0,1,4].map((profile,i)=>{const x=(i-1)*115;return {id:`way/${100+i}`,base:0,minimum:0,height:200,kind:'yes',rings:[[[x-36,-20],[x+36,-20],[x+36,20],[x-36,20],[x-36,-20]]],activity:{profile}};});
  scene.add((await makeBuildings(features,null,{lighting:uniforms})).group);
  const target=new THREE.WebGLRenderTarget(768,512),read=()=>{renderer.setRenderTarget(target);renderer.render(scene,camera);const data=new Uint8Array(768*512*4);renderer.readRenderTargetPixels(target,0,0,768,512,data);return data;};
  const setTime=h=>{const a=cityLighting(h).activity;uniforms.activity.value.set(a.slice(0,4));uniforms.retail.value=a[4];};
  const distance=d=>{camera.position.set(0,100,d);camera.lookAt(0,100,0);};
  const difference=(a,b)=>{let sum=0,changed=0,max=0;for(let i=0;i<a.length;i++)if(i%4!==3){const diff=Math.abs(a[i]-b[i]);sum+=diff;changed+=diff>0;max=Math.max(max,diff);}return {mean:sum/(a.length*.75),changed,max};};
  const regions=data=>[0,1,2].map(i=>{let sum=0,n=0;const mid=384+(i-1)*115/390*768;for(let y=60;y<450;y++)for(let x=Math.round(mid-60);x<mid+60;x++){const p=(y*768+x)*4;sum+=data[p]*.2126+data[p+1]*.7152+data[p+2]*.0722;n++;}return sum/n;});
  setTime(20);distance(300);uniforms.elapsed.value=0;const nearA=read();uniforms.elapsed.value=4;const nearB=read();
  distance(4000);uniforms.elapsed.value=0;const farA=read();uniforms.elapsed.value=4;const farB=read();
  uniforms.shimmer.value=0;uniforms.elapsed.value=0;const offA=read();uniforms.elapsed.value=4;const offB=read();
  distance(300);const samples={};for(const h of [18,20,21,22,23,0,4]){setTime(h);samples[h]=regions(read());}
  uniforms.night.value=0;uniforms.shimmer.value=1;distance(4000);uniforms.elapsed.value=0;const dayA=read();uniforms.elapsed.value=4;const dayB=read();
  const result={near:difference(nearA,nearB),far:difference(farA,farB),disabled:difference(offA,offB),day:difference(dayA,dayB),samples};
  target.dispose();renderer.dispose();return result;
 });
 assert.equal(result.near.changed,0,'nearby windows are steady');assert.ok(result.far.changed>100,'distant windows subtly vary');assert.ok(result.far.mean<2,'shimmer is restrained');assert.equal(result.disabled.changed,0);assert.equal(result.day.changed,0);
 assert.ok(result.samples[22][0]>result.samples[18][0]*1.15,'home windows brighten towards 10 pm');
 assert.ok(result.samples[22][0]>=result.samples[21][0]&&result.samples[23][0]<=result.samples[22][0],'homes peak at 10 pm then begin sleeping');
 assert.ok(result.samples[20][1]<result.samples[18][1],'offices leave from 6 pm');
 assert.ok(result.samples[22][1]<result.samples[20][1]*.5,'offices wind down through 8 pm');
 assert.ok(result.samples[22][2]<result.samples[21][2],'shops close progressively after 9 pm');
 assert.ok(result.samples[23][2]<result.samples[20][2]*.5,'most retail is dark by 11 pm');
 assert.ok(result.samples[0][2]<result.samples[23][2]&&result.samples[4][2]>0,'late shops and overnight lights survive');
 assert.deepEqual(errors,[]);result.result='passed';result.errors=errors;
 await writeFile(new URL('../../../docs/astra-city/night-cycle/render-verification.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
