/** Read-only installed-source camera supplement; no asset/terrain substitution. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const config=await read(process.argv[2]),out=new URL(config.doc,root),manifest=await read('3d-viewer/city/data/manifest.json');
assert(config.publication===false&&config.geometryEdits===0&&config.uids.length>0&&config.uids.length<=8);
const entries=[],forms=[];
for(const url of manifest.officialModelCatalogues){const cat=await read('3d-viewer/'+url);for(const m of cat.models)if(config.uids.includes(m.uid))entries.push({url,model:m});}
assert.equal(entries.length,config.uids.length);
for(const {model} of entries){const [a,b]=model.worldBounds,x=(a[0]+b[0])/2,z=(a[2]+b[2])/2,matches=[];for(const tile of manifest.tiles){const [l,t,r,bt]=tile.bounds;if(x>=l&&x<=r&&z>=t&&z<=bt)matches.push(...(await read('3d-viewer/'+tile.url)).buildings.filter(v=>v.uid===model.uid));}assert.equal(matches.length,1);forms.push(matches[0]);}
await mkdir(out,{recursive:true});const report={passed:false,publication:false,geometryEdits:0,performanceAcceptance:false,manifestSHA256:createHash('sha256').update(await readFile(new URL('3d-viewer/city/data/manifest.json',root))).digest('hex'),views:[],errors:[]};
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__cameraProbe",{get:()=>({scene,officialModels,stream,camera,controls,renderer,THREE,visitBuilding,closeSelection,controlSheet})});window.__cameraDraw=renderer.render.bind(renderer);renderer.render=()=>{};'});});
  await page.goto(config.viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__cameraProbe?.stream,null,{timeout:300000});
  for(const {url,model} of entries){
   assert.equal(model.sha256,config.sourceSHA256ByUid[model.uid]);assert(await page.evaluate(url=>window.__cameraProbe.officialModels.loadCatalogue(url),url));
   await page.evaluate(form=>window.__cameraProbe.visitBuilding(form),forms.find(f=>f.uid===model.uid));await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
   await page.evaluate(uid=>{const r=window.__cameraProbe;r.officialModels.setLoadingPaused(false);r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,force:true,allowNewLoads:true});},model.uid);
   await page.waitForFunction(uid=>!!window.__cameraProbe.stream.detailedModels.get(uid)?.active,model.uid,{timeout:120000});
   const cameraChoice=await page.evaluate(({uid,bounds})=>{
    const r=window.__cameraProbe,T=r.THREE,d=r.stream.detailedModels.get(uid),targetMeshes=new Set(d.meshes),visible=o=>{for(let p=o;p;p=p.parent)if(!p.visible)return false;return true;},sceneMeshes=[];
    r.scene.updateMatrixWorld(true);r.scene.traverse(o=>{if(o.isMesh&&visible(o))sceneMeshes.push(o);});
    r.controls.enableDamping=false;r.controls.update();r.closeSelection();r.controlSheet?.close({restoreFocus:false});document.getElementById('building-card').hidden=true;
    const [a,b]=bounds,centre=new T.Vector3(...a).add(new T.Vector3(...b)).multiplyScalar(.5),radius=new T.Vector3(...a).distanceTo(new T.Vector3(...b))/2,half=Math.min(T.MathUtils.degToRad(r.camera.fov/2),Math.atan(Math.tan(T.MathUtils.degToRad(r.camera.fov/2))*r.camera.aspect)),distance=radius/Math.sin(half)*1.1,options=[];
    for(const factor of [1,1.7,2.7])for(const direction of [[.01,1,0],[0,1,.01],[.35,1,.35],[-.35,1,.35],[.35,1,-.35],[-.35,1,-.35]]){
     const position=centre.clone().addScaledVector(new T.Vector3(...direction).normalize(),distance*factor);
     const range=modelRange();if(new T.Box3(new T.Vector3(...a),new T.Vector3(...b)).distanceToPoint(position)>range)continue;
     r.camera.position.copy(position);r.controls.target.copy(centre);r.controls.update();r.camera.updateMatrixWorld(true);
     let fullyFramed=true;for(const x of [a[0],b[0]])for(const y of [a[1],b[1]])for(const z of [a[2],b[2]]){const p=new T.Vector3(x,y,z).project(r.camera);if(Math.abs(p.x)>1||Math.abs(p.y)>1||Math.abs(p.z)>1)fullyFramed=false;}if(!fullyFramed)continue;
     let isolated=0,unobstructed=0;const ray=new T.Raycaster();
     for(let y=-.8;y<=.801;y+=.16)for(let x=-.8;x<=.801;x+=.16){ray.setFromCamera(new T.Vector2(x,y),r.camera);const own=ray.intersectObjects(d.meshes,false);if(!own.length)continue;isolated++;const first=ray.intersectObjects(sceneMeshes,false)[0];if(first&&targetMeshes.has(first.object))unobstructed++;}
     if(unobstructed>=4)options.push({camera:r.camera.position.toArray(),target:centre.toArray(),direction,factor,fullyFramed,isolated,unobstructed,ratio:isolated?unobstructed/isolated:0});
    }
    function modelRange(){const m=r.officialModels.models.get(uid);return m.priority==='landmark'?r.officialModels.limits.landmarkDistance:r.officialModels.limits.detailDistance;}
    options.sort((a,b)=>b.ratio-a.ratio||b.unobstructed-a.unobstructed);const choice=options[0];if(!choice||choice.unobstructed<4)throw new Error('No usable target-surface camera: '+uid);
    r.camera.position.fromArray(choice.camera);r.controls.target.fromArray(choice.target);r.controls.update();r.camera.updateMatrixWorld(true);return{choice,options};
   },{uid:model.uid,bounds:model.worldBounds});
   for(const time of ['15:00','22:00']){
    await page.evaluate(t=>{const e=document.getElementById('time');e.value=t;e.dispatchEvent(new Event('input',{bubbles:true}));},time);await page.waitForTimeout(1500);
    const state=await page.evaluate(({uid,choice})=>{const r=window.__cameraProbe;r.controls.enableDamping=false;r.controls.update();r.camera.position.fromArray(choice.camera);r.controls.target.fromArray(choice.target);r.controls.update();r.camera.updateMatrixWorld(true);window.__cameraDraw(r.scene,r.camera);const d=r.stream.detailedModels.get(uid),position=r.camera.position.toArray(),target=r.controls.target.toArray();if(position.some((v,i)=>Math.abs(v-choice.camera[i])>1e-6)||target.some((v,i)=>Math.abs(v-choice.target[i])>1e-6))throw new Error('Capture camera drifted');const [a,b]=r.officialModels.models.get(uid).worldBounds;let fullyFramed=true;for(const x of [a[0],b[0]])for(const y of [a[1],b[1]])for(const z of [a[2],b[2]]){const p=new r.THREE.Vector3(x,y,z).project(r.camera);if(Math.abs(p.x)>1||Math.abs(p.y)>1||Math.abs(p.z)>1)fullyFramed=false;}return{fullyFramed,active:!!d?.active,visible:!!d?.group?.visible,sourceSHA256:r.officialModels.models.get(uid).sha256,originalTriangles:d?.record?.modelGeometry?.index?.length/3,camera:position,target,canvas:r.renderer.domElement.toDataURL('image/png')};},{uid:model.uid,choice:cameraChoice.choice});
    assert(state.active&&state.visible&&state.fullyFramed);assert.equal(state.sourceSHA256,model.sha256);assert.equal(state.originalTriangles,model.triangles);
    const file=`retained-${model.uid.replaceAll('/','-').replaceAll(':','-')}-${width}-${time.replace(':','')}.png`;await writeFile(new URL(file,out),Buffer.from(state.canvas.split(',')[1],'base64'));delete state.canvas;report.views.push({uid:model.uid,width,time,file,cameraChoice,...state});console.log(file);
   }
  }
  await context.close();
 }
 assert.deepEqual(report.errors,[]);report.passed=true;
}catch(error){report.error=error.stack;throw error;}finally{await writeFile(new URL('report.json',out),JSON.stringify(report,null,2));await browser.close();}
