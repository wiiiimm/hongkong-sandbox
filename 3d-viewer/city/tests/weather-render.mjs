import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
try{
 const base=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');
 await page.route('**/weather-fixture.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><title>Weather verification</title>'}));await page.goto(base.origin+'/weather-fixture.html');
 const result=await page.evaluate(async()=>{
  const THREE=await import('/vendor/three.module.js'),{createWeather,weatherAtmosphere}=await import('/city/weather.js');
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(58,1.5,.2,100000),renderer=new THREE.WebGLRenderer({logarithmicDepthBuffer:true});renderer.setSize(600,400);renderer.toneMapping=THREE.ACESFilmicToneMapping;scene.background=new THREE.Color('#6e91a4');scene.fog=new THREE.FogExp2('#a2b8c0',.00006);
  camera.position.set(0,100,300);camera.lookAt(0,550,-4000);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(12000,12000),new THREE.MeshBasicMaterial({color:'#66735c'}));ground.rotation.x=-Math.PI/2;scene.add(ground);
  const tower=new THREE.Mesh(new THREE.BoxGeometry(120,600,120),new THREE.MeshBasicMaterial({color:'#bcafa0'}));tower.position.set(0,300,-900);scene.add(tower);
  const weather=createWeather({scene,camera}),target=new THREE.WebGLRenderTarget(600,400);
  const render=()=>{renderer.setRenderTarget(target);renderer.render(scene,camera);const out=new Uint8Array(600*400*4);renderer.readRenderTargetPixels(target,0,0,600,400,out);return out;};
  const difference=(a,b)=>{let count=0,sum=0;for(let i=0;i<a.length;i++)if(i%4!==3){const d=Math.abs(a[i]-b[i]);count+=d>0;sum+=d;}return {count,mean:sum/(a.length*.75)};};
  weather.setManual({rain:0,clouds:0,snow:0});weather.update(0);const clear=render();
  weather.setManual({clouds:1});weather.update(0);const cloudy=render();
  weather.setManual({rain:1});weather.update(.1);const rainA=render();for(let i=0;i<10;i++)weather.update(.1);const rainB=render();
  weather.setManual({rain:0,snow:1});weather.update(.1);const snowA=render();for(let i=0;i<10;i++)weather.update(.1);const snowB=render();
  weather.update(.1,{reducedMotion:true});const reducedA=render(),elapsed=weather.state.elapsed;for(let i=0;i<10;i++)weather.update(.1,{reducedMotion:true});const reducedB=render();
  const particles=scene.getObjectByName('City weather').children.filter(o=>/rain|snow/.test(o.name)).map(o=>o.visible);
  const atmosphere=weather.update(0,{suspended:true}),suspended=scene.getObjectByName('City weather').visible;
  const programCount=renderer.info.programs.length;weather.dispose();const disposed=!scene.getObjectByName('City weather');
  const result={clouds:difference(clear,cloudy),rain:difference(rainA,rainB),snow:difference(snowA,snowB),reduced:difference(reducedA,reducedB),elapsed,particles,suspended,atmosphere,disposed,programCount};
  ground.geometry.dispose();ground.material.dispose();tower.geometry.dispose();tower.material.dispose();target.dispose();renderer.dispose();return result;
 });
 assert.ok(result.clouds.count>1000,'clouds render visibly');assert.ok(result.rain.count>100,'rain moves');assert.ok(result.snow.count>20,'snow moves');assert.equal(result.reduced.count,0,'reduced motion freezes all weather animation');assert.deepEqual(result.particles,[false,false]);assert.equal(result.suspended,false);assert.equal(result.atmosphere.cloudCover,0);assert.equal(result.disposed,true);assert.deepEqual(errors,[]);
 console.log(JSON.stringify({...result,result:'passed',errors},null,2));
}finally{await browser.close();}
