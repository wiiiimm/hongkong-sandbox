import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:800,height:600}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.route('**/reveal-check',r=>r.fulfill({contentType:'text/html',body:'<body style="margin:0;background:#a7c7d3"></body>'}));
await page.goto((process.env.CITY_BASE_URL||'http://127.0.0.1:4176')+'/reveal-check');
await page.evaluate(async()=>{
 const T=await import('/vendor/three.module.js'),{ModelReveal}=await import('/city/model-reveal.js?v=20260913-reveal1');
 const renderer=new T.WebGLRenderer();renderer.setSize(800,600);document.body.append(renderer.domElement);
 const scene=new T.Scene();scene.background=new T.Color('#a7c7d3');const camera=new T.PerspectiveCamera(45,800/600,.1,100);camera.position.set(6,5,12);camera.lookAt(0,1,0);
 const mesh=new T.Mesh(new T.BoxGeometry(2,4,2),new T.MeshNormalMaterial());mesh.position.y=1;scene.add(mesh);renderer.render(scene,camera);
 const entry={active:true,group:mesh,bounds:new T.Box3().setFromObject(mesh)},effect=new ModelReveal(renderer.domElement);window.check={effect,entry,camera};effect.start(entry);effect.update(camera,performance.now());
});
assert.equal(await page.locator('.model-reveal').count(),1);await page.screenshot({path:'/tmp/model-reveal-blur.png'});
await page.evaluate(()=>{const {effect,camera}=window.check;effect.update(camera,effect.items[0].start+700);});assert.equal(await page.locator('.model-reveal').count(),0);await page.screenshot({path:'/tmp/model-reveal-sharp.png'});
await page.evaluate(()=>{const {effect,entry,camera}=window.check;for(let i=0;i<5;i++)effect.start(entry);if(effect.items.length!==3)throw Error('unbounded effects');effect.update(camera,performance.now(),{reduced:true});});assert.equal(await page.locator('.model-reveal').count(),0);
await page.evaluate(()=>{const {effect,entry,camera}=window.check;effect.start(entry);effect.update(camera,performance.now(),{interacting:true});});assert.equal(await page.locator('.model-reveal').count(),0);assert.deepEqual(errors,[]);console.log('PASS: rendered blur, expiry, cap, reduced motion, interaction cleanup; no page errors');await browser.close();
