/** Real City loading, native picking/collision, lighting and fallback checks; no architectural scoring. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const mode=process.argv[2]||'staged',folder='source-scripts/city/government-import/accepted/government-200-20260911/',catalogue=await read(folder+'catalogue.json'),forms=await read(folder+'source-forms.json'),url='city/data/official-models/government-20260911/catalogue.json',out=new URL('docs/astra-city/government-import/government-200-20260911/acceptance/',root);await mkdir(out,{recursive:true});
const report={mode,views:[],errors:[],aiCalls:0,architectureReview:false},browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{for(const model of catalogue.models)for(const width of [1280,390]){
 const building=forms.find(b=>b.uid===model.uid),page=await browser.newPage({viewport:{width,height:900},hasTouch:width<700});page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(/THREE.WebGLProgram|GL_INVALID|shader error/i.test(m.text()))report.errors.push(m.text());});
 await page.route('**/city/app.js*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__port",{get:()=>({scene,officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});'});});
 let fail=width===390;
 if(mode==='staged'){
  await page.route('**/'+url,r=>r.fulfill({json:catalogue}));
  await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json();m.officialModelCatalogues.push(url);await r.fulfill({response,json:m});});
  for(const m of catalogue.models)await page.route('**/city/data/official-models/government-20260911/'+m.asset,async r=>m.uid===model.uid&&fail?r.fulfill({status:503,body:'Test unavailable'}):r.fulfill({body:await readFile(new URL(folder+m.asset,root))}));
 }else await page.route('**/government-20260911/'+model.asset,r=>fail?r.fulfill({status:503,body:'Test unavailable'}):r.continue());
 await page.goto('http://127.0.0.1:4176/city.html');await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden',timeout:120000});
 await page.evaluate(()=>{const r=window.__port.renderer;window.__portDraw=r.render.bind(r);r.render=()=>{};});
 await page.evaluate(b=>window.__port.visitBuilding(b),building);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:90000});
 await page.evaluate(bounds=>{const r=window.__port,[a,b]=bounds,c=a.map((v,i)=>(v+b[i])/2),radius=new r.THREE.Vector3(...a).distanceTo(new r.THREE.Vector3(...b))/2,half=Math.min(r.THREE.MathUtils.degToRad(r.camera.fov/2),Math.atan(Math.tan(r.THREE.MathUtils.degToRad(r.camera.fov/2))*r.camera.aspect)),d=radius/Math.sin(half)*1.3;r.closeSelection();r.controlSheet?.close({restoreFocus:false});r.camera.position.set(c[0]+d*.5,c[1]+d*.5,c[2]+d*.707);r.controls.target.fromArray(c);r.controls.update();},model.worldBounds);
 if(fail){await page.waitForFunction(uid=>window.__port.officialModels.cache.errors.has(uid),model.uid,{timeout:60000});assert.equal(await page.evaluate(uid=>!!window.__port.stream.detailedModels.get(uid)?.active,model.uid),false);report.views.push({uid:model.uid,width,phase:'failed-download',fallbackRetained:true});fail=false;await page.locator('#stream-retry').click();}
 await page.waitForFunction(uid=>window.__port.stream.detailedModels.get(uid)?.active,model.uid,{timeout:60000});
 for(const time of ['15:00','22:00']){
  await page.evaluate(t=>{const e=document.getElementById('time');e.value=t;e.dispatchEvent(new Event('input',{bubbles:true}));},time);await page.waitForTimeout(500);await page.evaluate(()=>{const r=window.__port;window.__portDraw(r.scene,r.camera);});
  const state=await page.evaluate(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid),p=d.record.modelGeometry.position,idx=d.record.modelGeometry.index;let roof=null;
   for(let i=0;i<idx.length;i+=3){const a=new r.THREE.Vector3(...p.slice(idx[i]*3,idx[i]*3+3)),b=new r.THREE.Vector3(...p.slice(idx[i+1]*3,idx[i+1]*3+3)),c=new r.THREE.Vector3(...p.slice(idx[i+2]*3,idx[i+2]*3+3)),normal=b.clone().sub(a).cross(c.clone().sub(a));if(normal.y<=normal.length()*.2)continue;const q=a.add(b).add(c).divideScalar(3);if(!roof||q.y>roof.y)roof=q;}
   const ray=new r.THREE.Raycaster(new r.THREE.Vector3(roof.x,roof.y+10,roof.z),new r.THREE.Vector3(0,-1,0));
   const frustum=new r.THREE.Frustum().setFromProjectionMatrix(new r.THREE.Matrix4().multiplyMatrices(r.camera.projectionMatrix,r.camera.matrixWorldInverse));
   return{active:!!d.active,pick:ray.intersectObjects(d.meshes)[0]?.object.userData.officialBuildingUid,collision:r.stream.collision(roof.x,roof.z,roof.y-.05,roof.y+.05,.05)?.uid,visible:frustum.intersectsBox(new r.THREE.Box3().setFromObject(d.group)),drawnTriangles:r.renderer.info.render.triangles,overflow:document.documentElement.scrollWidth>innerWidth};
  },model.uid);
  assert(state.active&&state.visible&&state.drawnTriangles>0&&!state.overflow);assert.equal(state.pick,model.uid);assert.equal(state.collision,model.uid);
  const file=`${mode}-${model.uid.replaceAll('/','-').replaceAll(':','-')}-${width}-${time.replace(':','')}.png`;await page.screenshot({path:new URL(file,out).pathname});report.views.push({uid:model.uid,width,time,file,...state});console.log(file);
 }
 await page.close();
}assert.deepEqual(report.errors,[]);report.passed=true;}finally{await browser.close();await writeFile(new URL(mode+'-browser.json',out),JSON.stringify(report,null,2)+'\n');}
