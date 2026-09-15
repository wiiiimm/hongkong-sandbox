import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const evidence=new URL('../../../docs/astra-city/weather-effects/',import.meta.url);await fs.mkdir(evidence,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:800,height:600}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
try{
 const base=new URL(process.env.CITY_URL||'http://127.0.0.1:4176/city.html');
 await page.route('**/storm-fixture.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><html><head><meta charset="utf-8"><title>Original storm adaptation · verification</title><style>body{margin:0;background:#0e1720;color:#e6edf1;font:15px system-ui}header{padding:14px}button{font:inherit;padding:9px 14px;margin:0 8px 10px 0}canvas{display:block}small{display:block;color:#a6bbc6;margin-top:6px}</style></head><body><header>Weather restoration · bounded render fixture<small>Original forked lightning + original synthesised weather sound</small></header><button id="sound">Enable weather sound</button><button id="strike">Manual strike</button></body></html>'}));
 await page.goto(base.origin+'/storm-fixture.html');
 await page.evaluate(async()=>{
  const NativeAudioContext=window.AudioContext;window.audioContexts=[];
  // Test-only analyser taps the original master output without changing synthesis.
  window.AudioContext=class extends NativeAudioContext{
   constructor(){super();this.testAnalyser=this.createAnalyser();this.testAnalyser.fftSize=2048;this.testGains=0;window.audioContexts.push(this);}
   createGain(){const node=super.createGain();if(this.testGains++===0){const connect=node.connect.bind(node);node.connect=target=>{if(target===this.destination){connect(this.testAnalyser);return this.testAnalyser.connect(target);}return connect(target);};}return node;}
  };
  const THREE=await import('/vendor/three.module.js'),{createWeatherEffects}=await import('/city/weather-effects.js');window.originalAudio=await import('/audio.js');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#283846');scene.fog=new THREE.FogExp2('#283846',.000025);
  const camera=new THREE.PerspectiveCamera(58,800/440,.2,100000);camera.position.set(0,180,300);camera.lookAt(0,500,-850);
  const renderer=new THREE.WebGLRenderer({logarithmicDepthBuffer:true,antialias:true});renderer.setSize(800,440);renderer.toneMapping=THREE.ACESFilmicToneMapping;document.body.append(renderer.domElement);
  const ambient=new THREE.HemisphereLight('#c4dfec','#617453',.45);scene.add(ambient);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(10000,10000),new THREE.MeshStandardMaterial({color:'#354d43',roughness:1}));ground.rotation.x=-Math.PI/2;scene.add(ground);
  for(let i=0;i<9;i++){const tower=new THREE.Mesh(new THREE.BoxGeometry(80,120+i*20,80),new THREE.MeshStandardMaterial({color:i%2?'#9caaa8':'#758798'}));tower.position.set((i-4)*155,(120+i*20)/2,-850+(i%2)*190);scene.add(tower);}
  let seed=6,first=true;const random=()=>{if(first){first=false;return .35;}return ((seed=Math.imul(seed,1664525)+1013904223)>>>0)/4294967296;};
  const fx=createWeatherEffects({scene,camera,terrainHeight:()=>0,random});window.fixture={fx,scene,camera,renderer,ambient};
  window.settings={rain:1,wind:.65,waves:.6,fog:0};
  window.step=(dt,options={})=>{const light=fx.update(dt,{settings:window.settings,...options});ambient.intensity=.45+light.ambientBoost;renderer.render(scene,camera);return light;};
  window.pixels=()=>{const target=new THREE.WebGLRenderTarget(800,440);renderer.setRenderTarget(target);renderer.render(scene,camera);const bytes=new Uint8Array(800*440*4);renderer.readRenderTargetPixels(target,0,0,800,440,bytes);renderer.setRenderTarget(null);target.dispose();return bytes;};
  window.difference=(a,b)=>{let changed=0,total=0;for(let i=0;i<a.length;i++)if(i%4!==3){const delta=Math.abs(a[i]-b[i]);changed+=delta>0;total+=delta;}return {changed,mean:total/(a.length*.75)};};
  document.getElementById('sound').onclick=async e=>{window.soundResult=await fx.setSound(!fx.state.sound.enabled,e);document.getElementById('sound').textContent=fx.state.sound.enabled?'Mute weather sound':'Enable weather sound';};
  document.getElementById('strike').onclick=()=>{fx.setManual({lightning:true,thunderRate:1});window.step(0);window.triggerResult=fx.triggerStrike();window.step(.001);};
  window.step(0);window.baseline=window.pixels();window.baselineCalls=renderer.info.render.calls;
 });
 const locked=await page.evaluate(async()=>{await fixture.fx.setSound(true);return {contexts:audioContexts.length,state:fixture.fx.state.sound};});assert.equal(locked.contexts,0);assert.equal(locked.state.status,'gesture-required');
 await page.screenshot({path:new URL('storm-before-800x600.png',evidence).pathname});
 await page.click('#sound');await page.waitForFunction(()=>window.soundResult?.status==='playing');
 await page.waitForFunction(()=>{const ctx=audioContexts[0];if(!ctx||ctx.currentTime<.1)return false;const data=new Float32Array(ctx.testAnalyser.fftSize);ctx.testAnalyser.getFloatTimeDomainData(data);return Math.sqrt(data.reduce((sum,n)=>sum+n*n,0)/data.length)>.0001;},{},{timeout:8000});
 const sound=await page.evaluate(()=>{const ctx=audioContexts[0],data=new Float32Array(ctx.testAnalyser.fftSize);ctx.testAnalyser.getFloatTimeDomainData(data);return {state:fixture.fx.state.sound,context:ctx.state,rms:Math.sqrt(data.reduce((sum,n)=>sum+n*n,0)/data.length),contexts:audioContexts.length,currentTime:ctx.currentTime,gainCount:ctx.testGains};});
 assert.equal(sound.context,'running');assert.equal(sound.contexts,1);assert.ok(sound.rms>.0001,'original ambience produces actual nonzero audio output');
 await page.click('#strike');
 const strike=await page.evaluate(()=>({triggered:triggerResult,state:fixture.fx.state,source:originalAudio.getAudioState(),difference:difference(baseline,pixels()),calls:fixture.renderer.info.render.calls,baselineCalls,vertices:fixture.scene.getObjectByName('Forked lightning').geometry.attributes.position.count,programs:fixture.renderer.info.programs.map(p=>p.diagnostics?.runnable!==false)}));
 assert.equal(strike.triggered,true);assert.equal(strike.source.activeThunderSources,2);assert.ok(strike.difference.changed>1000);assert.ok(strike.vertices>=28&&strike.vertices<350);assert.ok(strike.programs.every(Boolean));
 await page.screenshot({path:new URL('storm-strike-800x600.png',evidence).pathname});
 const reduced=await page.evaluate(()=>{const light=step(.01,{reducedMotion:true});return {light,difference:difference(baseline,pixels()),bolt:fixture.scene.getObjectByName('Forked lightning').visible};});assert.equal(reduced.light.ambientBoost,0);assert.equal(reduced.bolt,false);assert.equal(reduced.difference.changed,0);
 const live=await page.evaluate(()=>{step(.01,{mode:'live'});return {state:fixture.fx.state,triggered:fixture.fx.triggerStrike(),audio:originalAudio.getAudioState()};});assert.equal(live.state.manual.lightning,true);assert.equal(live.triggered,false);assert.equal(live.audio.activeThunderSources,0);assert.equal(live.state.sound.audible,true);
 const paused=await page.evaluate(async()=>{step(.01,{paused:true});await new Promise(r=>setTimeout(r,30));return {state:fixture.fx.state.sound,audio:originalAudio.getAudioState()};});assert.equal(paused.audio.contextState,'suspended');assert.equal(paused.state.audible,false);
 await page.evaluate(()=>step(.01));await page.waitForFunction(()=>fixture.fx.state.sound.audible);
 // CDP lifecycle exercises the real document.visibilitychange path.
 const cdp=await page.context().newCDPSession(page);await cdp.send('Page.setWebLifecycleState',{state:'frozen'});await cdp.send('Page.setWebLifecycleState',{state:'active'});
 await page.click('#sound');await page.waitForFunction(()=>window.soundResult?.status==='muted');assert.equal(await page.evaluate(()=>originalAudio.getAudioState().contextState),'suspended');
 const disposed=await page.evaluate(async()=>{const ctx=audioContexts[0];await fixture.fx.dispose();fixture.renderer.dispose();return {context:ctx.state,stormPresent:!!fixture.scene.getObjectByName('City storm · manual simulation'),state:fixture.fx.state.sound};});assert.equal(disposed.context,'closed');assert.equal(disposed.stormPresent,false);assert.deepEqual(errors,[]);
 const result={result:'passed',locked,sound,strike,reduced,live:{...live,state:{...live.state,lastStrike:live.state.lastStrike}},paused,disposed,errors,notes:['Headless Chrome: real Web Audio output measured through a test-only analyser; no sound samples or replacement synthesis.','Fixture uses WebGLRenderer logarithmicDepthBuffer=true and camera far=100000.','Visibility/mute/disposal race coverage is in focused Node tests; this fixture checks real suspend/resume and context closure.']};
 await fs.writeFile(new URL('browser-verification.json',evidence),JSON.stringify(result,null,2));console.log(JSON.stringify({result:result.result,rms:sound.rms,lightningPixelDifference:strike.difference,extraDrawCalls:strike.calls-strike.baselineCalls,vertices:strike.vertices,reducedMotionPixelDifference:reduced.difference,errors},null,2));
}finally{await browser.close();}
