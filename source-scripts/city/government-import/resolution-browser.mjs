/** Scripted source-port runtime acceptance; no AI image/model review. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const mode=process.argv[2]||'staged';assert(['staged','live'].includes(mode));
const config=await read(process.argv[3]||'source-scripts/city/government-import/accepted/government-198-resolution-20260911/browser-config.json'),catalogue=await read(config.stage+'catalogue.json'),forms=await read(config.stage+'source-forms.json'),url=config.catalogueURL,assetBase=url.slice(0,url.lastIndexOf('/')+1),out=new URL(config.doc,root);await mkdir(out,{recursive:true});
const browserModels=config.browserUids?catalogue.models.filter(model=>config.browserUids.includes(model.uid)):catalogue.models;assert(browserModels.length>0&&(!config.browserUids||browserModels.length===config.browserUids.length));
const report={mode,views:[],errors:[],aiCalls:0,architectureReview:false},browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{for(const width of [1280,390]){
 const page=await browser.newPage({viewport:{width,height:900},hasTouch:width<700}),allowed=new Set(),cdp=await page.context().newCDPSession(page);await cdp.send('Network.clearBrowserCache');page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(/THREE.WebGLProgram|GL_INVALID|shader error/i.test(m.text()))report.errors.push(m.text());});
 await page.route('**/city/app.js*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__port",{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});'});});
 if(mode==='staged'){
  await page.route('**/'+url,r=>r.fulfill({json:catalogue}));
  for(const t of config.terrain)await page.route('**/'+t.destination,async r=>r.fulfill({body:await readFile(new URL(t.source,root))}));
  for(const replacement of config.catalogueReplacements||[])await page.route('**/'+replacement.url,async r=>r.fulfill({body:await readFile(new URL(replacement.source,root))}));
  await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json();m.officialModelCatalogues.push(url);m.terrainPatches.push(...config.terrain.map(t=>({url:t.destination,resolution:t.resolution,area:t.area})));await r.fulfill({response,json:m});});
 }
 for(const model of browserModels)await page.route('**/'+assetBase+model.asset,async r=>width===390&&(!config.failureTestUids||config.failureTestUids.includes(model.uid))&&!allowed.has(model.uid)?r.fulfill({status:503,body:'Intentional fallback test'}):mode==='staged'?r.fulfill({body:await readFile(new URL(config.stage+model.asset,root))}):r.continue());
 await page.goto('http://127.0.0.1:4176/city.html');await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden',timeout:120000});
 await page.evaluate(()=>{const r=window.__port.renderer;window.__portDraw=r.render.bind(r);r.render=()=>{};});
 for(const model of browserModels){
  const building=forms.find(b=>b.uid===model.uid);
  await page.evaluate(b=>window.__port.visitBuilding(b),building);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:90000});
  await page.evaluate(({bounds,fitBox,priority})=>{const r=window.__port,[a,b]=bounds,c=a.map((v,i)=>(v+b[i])/2),radius=new r.THREE.Vector3(...a).distanceTo(new r.THREE.Vector3(...b))/2,half=Math.min(r.THREE.MathUtils.degToRad(r.camera.fov/2),Math.atan(Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2))*r.camera.aspect));let d=radius/Math.sin(half)*1.3;const direction=new r.THREE.Vector3(.5,.5,.707).normalize();
   if(fitBox){const right=new r.THREE.Vector3().crossVectors(new r.THREE.Vector3(0,1,0),direction).normalize(),up=new r.THREE.Vector3().crossVectors(direction,right),tanV=Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2)),tanH=tanV*r.camera.aspect;d=0;for(const x of [a[0],b[0]])for(const y of [a[1],b[1]])for(const z of [a[2],b[2]]){const o=new r.THREE.Vector3(x-c[0],y-c[1],z-c[2]);d=Math.max(d,o.dot(direction)+Math.abs(o.dot(right))/tanH,o.dot(direction)+Math.abs(o.dot(up))/tanV);}d*=1.04;}
   if(innerWidth>700){r.closeSelection();r.controlSheet?.close({restoreFocus:false});}r.camera.position.fromArray(c).addScaledVector(direction,d);r.controls.target.fromArray(c);r.controls.update();r.camera.updateMatrixWorld(true);if(fitBox){const distance=new r.THREE.Box3(new r.THREE.Vector3(...a),new r.THREE.Vector3(...b)).distanceToPoint(r.camera.position),range=priority==='landmark'?r.officialModels.limits.landmarkDistance:r.officialModels.limits.detailDistance;if(distance>range)throw new Error('Capture camera outside initial-load '+priority+' range: '+distance);}
  },{bounds:model.worldBounds,fitBox:!!config.fitBox,priority:model.priority});
  if(width===390&&(!config.failureTestUids||config.failureTestUids.includes(model.uid))){await page.waitForFunction(uid=>window.__port.officialModels.cache.errors.has(uid),model.uid,{timeout:60000});assert.equal(await page.evaluate(uid=>!!window.__port.stream.detailedModels.get(uid)?.active,model.uid),false);report.views.push({uid:model.uid,width,phase:'failed-download',fallbackRetained:true});allowed.add(model.uid);await page.locator('#stream-retry').click();}
  await page.waitForFunction(uid=>window.__port.stream.detailedModels.get(uid)?.active,model.uid,{timeout:60000});if(width===390)await page.evaluate(()=>{document.getElementById('building-card').hidden=true;window.__port.controlSheet?.close({restoreFocus:false});});
  for(const time of ['15:00','22:00']){
   await page.evaluate(t=>{const e=document.getElementById('time');e.value=t;e.dispatchEvent(new Event('input',{bubbles:true}));},time);await page.waitForTimeout(300);await page.evaluate(()=>{const r=window.__port;window.__portDraw(r.scene,r.camera);});
   const state=await page.evaluate(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid),p=d.record.modelGeometry.position,idx=d.record.modelGeometry.index;let roof=null;
    for(let i=0;i<idx.length;i+=3){const a=new r.THREE.Vector3(...p.slice(idx[i]*3,idx[i]*3+3)),b=new r.THREE.Vector3(...p.slice(idx[i+1]*3,idx[i+1]*3+3)),c=new r.THREE.Vector3(...p.slice(idx[i+2]*3,idx[i+2]*3+3)),normal=b.clone().sub(a).cross(c.clone().sub(a));if(normal.y<=normal.length()*.2)continue;const q=a.add(b).add(c).divideScalar(3);if(!roof||q.y>roof.y)roof=q;}
    const ray=new r.THREE.Raycaster(new r.THREE.Vector3(roof.x,roof.y+50,roof.z),new r.THREE.Vector3(0,-1,0));
    r.terrain.updateMatrixWorld(true);const ground=ray.intersectObject(r.terrain,true)[0]?.point.y;
    const frustum=new r.THREE.Frustum().setFromProjectionMatrix(new r.THREE.Matrix4().multiplyMatrices(r.camera.projectionMatrix,r.camera.matrixWorldInverse));
    const box=new r.THREE.Box3().setFromObject(d.group);let fullyFramed=true;for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const q=new r.THREE.Vector3(x,y,z).project(r.camera);if(Math.abs(q.x)>1||Math.abs(q.y)>1||Math.abs(q.z)>1)fullyFramed=false;}
    return{fullyFramed,active:!!d.active,pick:ray.intersectObjects(d.meshes)[0]?.object.userData.officialBuildingUid,collision:r.stream.collision(roof.x,roof.z,roof.y-.05,roof.y+.05,.05)?.uid,visible:frustum.intersectsBox(new r.THREE.Box3().setFromObject(d.group)),drawnTriangles:r.renderer.info.render.triangles,overflow:document.documentElement.scrollWidth>innerWidth,ground,groundSampler:r.sampler.height(roof.x,roof.z)};
   },model.uid);
   assert(state.active&&state.visible&&state.drawnTriangles>0&&!state.overflow);if(config.fitBox)assert(state.fullyFramed,'Whole source bounds must fit the viewport');assert.equal(state.pick,model.uid);assert.equal(state.collision,model.uid);assert(Number.isFinite(state.ground)&&Math.abs(state.ground-state.groundSampler)<=.004);
   const file=`${mode}-${model.uid.replaceAll('/','-').replaceAll(':','-')}-${width}-${time.replace(':','')}.png`;await page.screenshot({path:new URL(file,out).pathname});report.views.push({uid:model.uid,width,time,file,...state});console.log(file);
  }
 }
 await page.close();
}assert.deepEqual(report.errors,[]);report.passed=true;}catch(error){report.errors.push(error.message);throw error;}finally{await browser.close();await writeFile(new URL(mode+'-browser.json',out),JSON.stringify(report,null,2)+'\n');}
