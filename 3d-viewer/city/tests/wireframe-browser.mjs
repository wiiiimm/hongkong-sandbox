/** HKS-210 independent actual-browser acceptance; inspection is never mocked. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const out=new URL('../../../docs/astra-city/wireframe/',import.meta.url);await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const report={result:'running',views:[],errors:[],limits:['Mobile viewport emulation runs in desktop Chrome; physical-phone thermal and frame performance are unverified.','Water, roads, vegetation, actors, labels and regional surface overlays remain in their normal styles and are explicitly excluded in the UI.']};let page;
async function ready(){await page.waitForFunction(()=>window.__city?.ready&&!window.__city.state.loadingTravel&&!window.__city.state.travelling&&window.__city.state.stream.pending===0&&window.__city.state.models.pending===0,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});}
async function open(width,place){page=await browser.newPage({viewport:{width,height:width<760?844:1000},deviceScaleFactor:1});page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(/THREE.WebGLProgram|GL_INVALID|shader error/i.test(m.text()))report.errors.push(m.text());});await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__wireReview",{get:()=>({meshInspection,renderer,scene,stream,terrain,bridgeLayer,cableLayer,controls,camera,controlSheet,goPlace,visitBuilding,closeSelection,nav,THREE})});\n'});});await page.goto('http://127.0.0.1:4176/city.html?district='+place);await ready();}
async function panel(){await page.evaluate(()=>window.__wireReview.controlSheet.open('places'));await page.locator('#mesh-inspection').evaluate(e=>e.open=true);}
async function mode(value){await panel();await page.locator('input[name="mesh-mode"][value="'+value+'"]').check();await page.waitForFunction(value=>window.__city.state.inspection.mode===value,value);await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));await page.waitForTimeout(200);}
async function proof(){return page.evaluate(()=>{
 const r=window.__wireReview,c=r.meshInspection;let wrong=0,buffers=0,alphaWrong=0,casts=0,verifiedTriangles=0;
 for(const rec of c.records.values()){
  const selected=c.mode!=='solid'&&c.targets[rec.target]&&rec.candidates?.length;
  if(selected){
   const o=rec.overlay,source=rec.mesh.geometry;
   if(!o||o.userData.inspectionSourceGeometry!==source||o.parent!==rec.mesh){wrong++;continue;}
   for(const res of rec.resources)if(![].concat(rec.mesh.material).includes(res.skin)||res.skin.opacity!==res.original.opacity||res.skin.depthWrite!==res.original.depthWrite)alphaWrong++;
   if(c.mode==='wireframe'&&c.regionUniforms.opacity.value!==0)alphaWrong++;
   if(o.isInstancedMesh){buffers+=o.instanceMatrix.array.byteLength;const a=new r.THREE.Matrix4(),b=new r.THREE.Matrix4();for(let i=0;i<o.count;i++){o.getMatrixAt(i,a);rec.mesh.getMatrixAt(o.userData.inspectionInstances[i],b);if(!a.equals(b))wrong++;}}
   else{
    const g=o.geometry,v=g.userData.inspectionSourceVertices,offsets=g.userData.inspectionSourceOffsets,p=g.attributes.position,q=source.attributes.position;
    if(!v||!offsets){wrong++;continue;}
    for(let i=0;i<v.length;i++)if(p.getX(i)!==q.getX(v[i])||p.getY(i)!==q.getY(v[i])||p.getZ(i)!==q.getZ(v[i]))wrong++;
    for(let i=0;i<offsets.length;i++)for(let j=0;j<3;j++)if(v[g.index.getX(i*3+j)]!==(source.index?source.index.getX(offsets[i]+j):offsets[i]+j))wrong++;
    verifiedTriangles+=offsets.length;
   }
   if(rec.mesh.castShadow)casts++;
  }else if(rec.overlay||rec.mesh.material!==rec.original)wrong++;
 }
 if(c.state.scope.triangles>c.state.scope.budget)wrong++;
 return{inspection:c.state,wrong,alphaWrong,verifiedTriangles,borrowedInstanceBytes:buffers,shadowCastingSources:casts,render:window.__city.state.render,memory:{...r.renderer.info.memory},mode:window.__city.state.mode,models:window.__city.state.models,bridges:window.__city.state.bridges};
});}
async function measure(){return page.evaluate(async()=>{let last;const times=[];for(let i=0;i<75;i++){const n=await new Promise(requestAnimationFrame);if(i>10)times.push(n-last);last=n;}times.sort((a,b)=>a-b);return{median:times[Math.floor(times.length*.5)],p95:times[Math.floor(times.length*.95)]};});}
async function capture(name){await page.waitForTimeout(900);await page.screenshot({path:new URL(name+'.png',out).pathname});const p=await proof();assert.equal(p.wrong,0);assert.equal(p.alphaWrong,0);const frame=await measure();report.views.push({name,...p,frame});console.log(name,JSON.stringify({inspection:p.inspection,render:p.render,frame}));await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');}
try{
 await open(1440,'central');assert.equal((await proof()).inspection.mode,'solid');
 await capture('central-solid');await mode('overlay');await panel();await page.locator('#mesh-opacity').fill('35');await page.locator('#mesh-opacity').dispatchEvent('input');await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));assert.equal((await proof()).inspection.opacity,35);await capture('central-overlay');
 await mode('wireframe');await capture('central-wireframe');await panel();assert.equal(await page.locator('#mesh-opacity').isDisabled(),true);await page.locator('#mesh-terrain').uncheck();await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));assert.equal((await proof()).inspection.targets.terrain,false);await capture('central-structures');await panel();await page.locator('#mesh-terrain').check();await page.locator('#mesh-structures').uncheck();await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));await capture('central-terrain');await panel();await page.locator('#mesh-structures').check();await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));
 // Load a detailed replacement while inspection is active, then test source picking/collision.
 const cfa=JSON.parse(await readFile(new URL('../data/tiles/0_0.json',import.meta.url),'utf8')).buildings.find(b=>b.uid==='landsd/184076:0');assert.ok(cfa);
 await page.evaluate(b=>window.__wireReview.visitBuilding(b),cfa);await ready();await page.waitForFunction(()=>window.__wireReview.stream.detailedModels.get('landsd/184076:0')?.active,null,{timeout:120000});await page.evaluate(()=>{const r=window.__wireReview;r.closeSelection();r.controls.target.set(66,24,718);r.camera.position.set(145,92,827);r.controls.update();});await capture('detailed-court-wireframe');
 const detailed=await page.evaluate(()=>{const r=window.__wireReview,e=r.stream.detailedModels.get('landsd/184076:0'),p=e.record.modelGeometry.position,ids=e.record.modelGeometry.index;let contact=null;for(let i=0;i<ids.length;i+=3){const q=[0,1,2].map(k=>(p[ids[i]*3+k]+p[ids[i+1]*3+k]+p[ids[i+2]*3+k])/3);if(r.stream.collision(q[0],q[2],q[1]-.05,q[1]+.05,.05)?.uid===e.record.uid){contact=q;break;}}const ray=new r.THREE.Raycaster(new r.THREE.Vector3(66,3000,718),new r.THREE.Vector3(0,-1,0));return{contact,pick:r.stream.featureAt(ray.intersectObjects(r.stream.pickMeshes(ray.ray))[0])?.uid,active:e.active};});assert.ok(detailed.contact);assert.equal(detailed.pick,'landsd/184076:0');report.detailed=detailed;
 await panel();await page.evaluate(()=>{const t=document.getElementById('time');t.value='22:00';t.dispatchEvent(new Event('input',{bubbles:true}));window.__wireReview.controlSheet.close({restoreFocus:false});});await capture('detailed-court-night-wireframe');await mode('solid');await capture('detailed-court-night-restored');await page.evaluate(()=>{const t=document.getElementById('time');t.value='15:00';t.dispatchEvent(new Event('input',{bubbles:true}));});await mode('wireframe');
 // Travel with wireframe already active: new detailed meshes must join the mode.
 await page.evaluate(()=>window.__wireReview.goPlace('muiwo',false));await ready();await capture('muiwo-streamed-wireframe');assert.ok((await proof()).inspection.meshes.structures>0);
 await mode('solid');assert.equal((await proof()).inspection.overlays,0);assert.equal((await proof()).inspection.materialPairs,0);await capture('muiwo-restored');
 // Repeated toggles must release every derived material/instance buffer.
 for(let i=0;i<8;i++){await mode('wireframe');await mode('solid');const p=await proof();assert.equal(p.inspection.overlays,0);assert.equal(p.inspection.materialPairs,0);assert.equal(p.wrong,0);}
 await page.evaluate(()=>window.__wireReview.goPlace('nt-lantau-link-view',false));await ready();await mode('wireframe');await capture('bridge-wireframe');assert.ok((await proof()).bridges.sourceModels>0);await mode('solid');await capture('bridge-restored');await page.close();
 await open(390,'central');await panel();await page.locator('input[name="mesh-mode"][value="overlay"]').check();await page.locator('#mesh-opacity').focus();await page.keyboard.press('ArrowLeft');assert.equal((await proof()).inspection.opacity,60);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:new URL('mobile-controls.png',out).pathname});await page.evaluate(()=>window.__wireReview.controlSheet.close({restoreFocus:false}));await mode('wireframe');await capture('mobile-wireframe');assert.equal((await proof()).models.profile,'mobile');await mode('solid');await capture('mobile-restored');await page.close();assert.deepEqual(report.errors,[]);report.result='passed';
}catch(e){report.result='failed';report.failure=e.stack;if(page&&!page.isClosed())await page.screenshot({path:new URL('failure.png',out).pathname}).catch(()=>{});throw e;}finally{await writeFile(new URL('browser.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
