/** Normal-scene native candidate review, before/after, desktop and mobile. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8')),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const path='source-scripts/city/cultural-model-review/candidates/',catalogue=await read(path+'catalogue.json'),models=new Map(catalogue.models.map(m=>[m.uid,m]));
const groups=[{id:'mplus-pavilion',uids:['landsd/168596:0']},{id:'xiqu-centre',uids:['landsd/205817:0']},{id:'mplus',uids:['landsd/279530:0','landsd/310908:0']},{id:'palace-museum',uids:['landsd/283788:0']}];
const buildings=new Map(),manifest=await read('3d-viewer/city/data/manifest.json');for(const tile of manifest.tiles)for(const b of(await read('3d-viewer/'+tile.url)).buildings)if(models.has(b.uid))buildings.set(b.uid,b);
const output=new URL('docs/astra-city/cultural-model-review/browser/',root);await mkdir(output,{recursive:true});
const report={started:new Date().toISOString(),verticalScale:1,staged:true,published:false,errors:[],views:[],runtimeHashes:{},limits:['Unmodified native candidate geometry; browser-only catalogue injection uses the intended landmark priority for the reviewed named group.','All surrounding city objects remain visible. Location caption/minimap/labels are hidden only to avoid covering review framing.','Desktop and emulated mobile Chrome check loading/rendering; no claim of real-device Safari or sustained mobile thermal performance.','Correct geometry and lighting response are separate from source-authentic materials, LED media facades and interiors.']};
for(const p of ['3d-viewer/city/app.js','3d-viewer/city/official-models.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/data/manifest.json'])report.runtimeHashes[p]=createHash('sha256').update(await readFile(new URL(p,root))).digest('hex');
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const mobile of process.env.CULTURAL_FOUNDATIONS_ONLY? [false]:[false,true]){
  const page=await browser.newPage({viewport:mobile?{width:390,height:844}:{width:1280,height:900},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});
  let inject=false;const url='city/data/official-models/cultural-review/catalogue.json';
  page.on('pageerror',e=>report.errors.push(e.message));
  await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__review",{get:()=>({scene,officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});'});});
  await page.route('**/'+url,r=>r.fulfill({json:{...catalogue,models:catalogue.models.map(m=>({...m,priority:'landmark'}))}}));
  for(const m of models.values())await page.route('**/'+url.slice(0,url.lastIndexOf('/')+1)+m.asset,async r=>{const bytes=await readFile(new URL(path+m.asset,root));assert.equal(createHash('sha256').update(bytes).digest('hex'),m.sha256);await r.fulfill({body:bytes,contentType:'application/gzip'});});
  await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),data=await response.json();if(inject)data.officialModelCatalogues=[...data.officialModelCatalogues,url];await r.fulfill({response,json:data});});
  for(const phase of mobile||process.env.CULTURAL_FOUNDATIONS_ONLY?['after']:['before','after']){
   inject=phase==='after';await page.goto((process.env.CITY_BASE_URL||'http://127.0.0.1:4176')+'/city.html?district=westkowloon');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});
   await page.addStyleTag({content:'#location-title,.minimap,#labels{display:none!important}'});
   for(const g of groups){
    await page.evaluate(b=>window.__review.visitBuilding(b),buildings.get(g.uids[0]));await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
    const ms=g.uids.map(uid=>models.get(uid)),bounds=[[0,1,2].map(i=>Math.min(...ms.map(m=>m.worldBounds[0][i]))),[0,1,2].map(i=>Math.max(...ms.map(m=>m.worldBounds[1][i])))];
    for(const direction of process.env.CULTURAL_FOUNDATIONS_ONLY?['foundation']:phase==='before'||mobile?['southwest']:['southwest','northeast']){
     const framing=await page.evaluate(({bounds,direction})=>{const r=window.__review,[a,b]=bounds,c=a.map((v,i)=>(v+b[i])/2),radius=new r.THREE.Vector3(...a).distanceTo(new r.THREE.Vector3(...b))/2,halfV=r.THREE.MathUtils.degToRad(r.camera.getEffectiveFOV()/2),halfH=Math.atan(Math.tan(halfV)*r.camera.aspect),distance=radius/Math.sin(Math.min(halfV,halfH)) *1.22,sign=direction==='northeast'?-1:1,offset=new r.THREE.Vector3(-.65*sign,direction==='foundation'?.12:.65,1*sign).normalize().multiplyScalar(distance);if(direction==='foundation')c[1]=a[1]+Math.min(5,(b[1]-a[1])*.2);r.closeSelection();r.controlSheet.close({restoreFocus:false});r.camera.position.set(c[0]+offset.x,Math.max(c[1]+offset.y,r.sampler.height(c[0]+offset.x,c[2]+offset.z)+10),c[2]+offset.z);r.controls.target.fromArray(c);r.controls.update();r.camera.updateMatrixWorld(true);return{camera:r.camera.position.toArray(),target:c};},{bounds,direction});
     await page.waitForTimeout(800);await page.waitForFunction(()=>window.__review.officialModels.stats.pending===0&&window.__city.state.stream.pending===0,null,{timeout:90000});
     if(inject)await page.waitForFunction(uids=>uids.every(uid=>window.__review.stream.detailedModels.get(uid)?.active),g.uids,{timeout:60000});
     const times=phase==='before'||direction==='northeast'||direction==='foundation'?['15:00']:['15:00','22:00'];
     for(const time of times){
      await page.evaluate(time=>{const input=document.getElementById('time');input.value=time;input.dispatchEvent(new Event('input',{bubbles:true}));},time);await page.waitForTimeout(650);
      const evidence=await page.evaluate(({uids,bounds})=>{const r=window.__review,[a,b]=bounds,box=new r.THREE.Box3(new r.THREE.Vector3(...a),new r.THREE.Vector3(...b)),corners=[];for(const x of[a[0],b[0]])for(const y of[a[1],b[1]])for(const z of[a[2],b[2]])corners.push(new r.THREE.Vector3(x,y,z).project(r.camera).toArray());const activeUIDs=uids.filter(uid=>r.stream.detailedModels.get(uid)?.active),picking=[];for(const uid of activeUIDs){const d=r.stream.detailedModels.get(uid),p=d.record.modelGeometry.position,idx=d.record.modelGeometry.index;let roof=null;for(let i=0;i<idx.length;i+=3){const q=[0,1,2].map(axis=>(p[idx[i]*3+axis]+p[idx[i+1]*3+axis]+p[idx[i+2]*3+axis])/3);if(!roof||q[1]>roof[1])roof=q;}const ray=new r.THREE.Raycaster(new r.THREE.Vector3(roof[0],b[1]+20,roof[2]),new r.THREE.Vector3(0,-1,0));const hit=ray.intersectObjects(d.meshes)[0];picking.push({uid,hitUid:hit?.object.userData.officialBuildingUid??null});}const occupancy=r.stream.collision(r.camera.position.x,r.camera.position.z,r.camera.position.y-.2,r.camera.position.y+.2,.2)?.uid||null;return{activeUIDs,picking,cameraCollision:occupancy,boxInsideView:corners.every(p=>Math.abs(p[0])<.92&&Math.abs(p[1])<.92&&p[2]>-1&&p[2]<1),corners,cache:r.officialModels.stats,lighting:window.__city.state.lighting,time:window.__city.state.time,render:window.__city.state.render,uiOverflow:document.documentElement.scrollWidth>innerWidth};},{uids:g.uids,bounds});
      assert(!evidence.cameraCollision);if(direction!=='foundation')assert(evidence.boxInsideView);assert(!evidence.uiOverflow);if(inject){assert.deepEqual(evidence.activeUIDs,g.uids);assert(evidence.picking.every(p=>p.uid===p.hitUid));}else assert.equal(evidence.activeUIDs.length,0);
      const file=`${g.id}-${mobile?'mobile':'desktop'}-${phase}-${direction}-${time.replace(':','')}.jpg`;await page.screenshot({path:new URL(file,output).pathname,type:'jpeg',quality:85});report.views.push({id:g.id,uids:g.uids,phase,mobile,direction,time,...framing,...evidence,file,sha256:createHash('sha256').update(await readFile(new URL(file,output))).digest('hex')});console.log(file,evidence.activeUIDs.length,'active');await writeFile(new URL(process.env.CULTURAL_FOUNDATIONS_ONLY?'foundations.json':'report.json',output),JSON.stringify(report,null,2)+'\n');
     }
    }
   }
  }
  await page.close();
 }
}finally{report.finished=new Date().toISOString();await writeFile(new URL(process.env.CULTURAL_FOUNDATIONS_ONLY?'foundations.json':'report.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
assert.equal(report.errors.length,0);console.log(JSON.stringify({views:report.views.length,errors:report.errors.length}));
