/** HKS-214: inspect previously inactive candidates individually, with normal LOD.
 * No live manifest, priority, terrain, identity or publication changes. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url), read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const prior=await read('docs/astra-city/landmark-preflight/gallery-summary.json'),pin=await read('source-scripts/city/landmark-preflight/snapshot.json');
assert.equal(prior.snapshotId,pin.id);
const base=`source-scripts/city/landmark-preflight/snapshots/${pin.id}/`,catalogue=await read(base+'catalogue.json');
assert.equal(createHash('sha256').update(await readFile(new URL(base+'catalogue.json',root))).digest('hex'),pin.files['catalogue.json'].sha256);
const models=new Map(catalogue.models.map(m=>[m.uid,m])),missing=prior.landmarks.flatMap(g=>g.stagedUIDs.filter(uid=>!g.views.some(v=>v.activeUIDs.includes(uid))).map(uid=>({group:g,model:models.get(uid)})));
const buildings=new Map(),manifest=await read('3d-viewer/city/data/manifest.json');
for(const tile of manifest.tiles)for(const b of(await read('3d-viewer/'+tile.url)).buildings)if(missing.some(x=>x.model.uid===b.uid))buildings.set(b.uid,b);
const output=new URL('docs/astra-city/landmark-visibility/',root);await mkdir(output,{recursive:true});
const report={issue:'HKS-214',snapshotId:pin.id,gitHead:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),started:new Date().toISOString(),runtimeHashes:{},limits:['Candidate-only review routes; production assets and priorities unchanged.','Active model membership proves loading, not architectural accuracy or complete visibility.','Source component identity and placement remain unapproved.'],parts:[],errors:[]};
for(const path of ['3d-viewer/city/app.js','3d-viewer/city/official-models.js','3d-viewer/city/official-model-assets.js'])report.runtimeHashes[path]=createHash('sha256').update(await readFile(new URL(path,root))).digest('hex');
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1280,height:900}}),catalogueURL=`city/data/official-models/visibility-${pin.id}/catalogue.json`;
const inspect=async uid=>page.evaluate(uid=>{const r=window.__visibility,m=r.officialModels.models.get(uid);if(!m)return{uid,missingCatalogue:true};const box=new r.THREE.Box3(new r.THREE.Vector3(...m.worldBounds[0]),new r.THREE.Vector3(...m.worldBounds[1])),eye=r.camera.position,extent=box.getSize(new r.THREE.Vector3()),distance=box.distanceToPoint(eye),projected=Math.max(extent.x,extent.y,extent.z)*900/(2*Math.tan(r.THREE.MathUtils.degToRad(r.camera.getEffectiveFOV())/2)*Math.max(1,box.getCenter(new r.THREE.Vector3()).distanceTo(eye))),resident=r.officialModels.cache.entries.has(uid),range=(m.priority==='landmark'?r.officialModels.limits.landmarkDistance:r.officialModels.limits.detailDistance)*(resident?1.2:1),matrix=new r.THREE.Matrix4().multiplyMatrices(r.camera.projectionMatrix,r.camera.matrixWorldInverse),visible=new r.THREE.Frustum().setFromProjectionMatrix(matrix).intersectsBox(box),b=r.stream.getLoadedBuilding(uid),entry=r.stream.detailedModels.get(uid);return{uid,camera:eye.toArray(),target:r.controls.target.toArray(),priority:m.priority,distance,range,projectedPixels:projected,minPixels:r.officialModels.limits.minPixels,frustumVisible:visible,sourceLoaded:!!b,sourceAlreadyHasGeometry:!!b?.modelGeometry,resident,active:!!entry?.active,wanted:r.officialModels.cache.wanted.includes(uid),cache:r.officialModels.stats};},uid);
const settle=async()=>{await page.waitForTimeout(750);await page.waitForFunction(()=>window.__visibility.officialModels.stats.pending===0&&window.__city.state.stream.pending===0,null,{timeout:60000});await page.waitForTimeout(500);};
try{
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__visibility",{get:()=>({officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});'});});
 await page.route('**/'+catalogueURL,r=>r.fulfill({json:catalogue}));
 for(const m of models.values())await page.route('**/'+catalogueURL.slice(0,catalogueURL.lastIndexOf('/')+1)+m.asset,async r=>{const bytes=await readFile(new URL(base+'assets/'+m.asset,root));assert.equal(createHash('sha256').update(bytes).digest('hex'),m.sha256);await r.fulfill({body:bytes,contentType:'application/gzip'});});
 await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),data=await response.json();data.officialModelCatalogues=[...data.officialModelCatalogues,catalogueURL];await r.fulfill({response,json:data});});
 await page.goto((process.env.CITY_BASE_URL||'http://127.0.0.1:4176')+'/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});
 for(const {group:g,model:m}of missing){
  const row={landmark:g.id,name:g.name,uid:m.uid,sourceLabel:m.label,modelId:m.modelId,sourceSHA256:m.sha256,bounds:m.worldBounds,publicationApproved:false,originalViews:[]};report.parts.push(row);
  await page.evaluate(b=>window.__visibility.visitBuilding(b),buildings.get(m.uid));await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
  for(const v of g.views){await page.evaluate(v=>{const r=window.__visibility;r.closeSelection();r.controlSheet.close({restoreFocus:false});r.camera.position.fromArray(v.camera);r.controls.target.fromArray(v.target);r.controls.update();r.camera.updateMatrixWorld(true);},v);await settle();row.originalViews.push({file:v.file,...await inspect(m.uid)});}
  await page.evaluate(bounds=>{const r=window.__visibility,[a,b]=bounds,c=a.map((v,i)=>(v+b[i])/2),span=Math.max(b[0]-a[0],b[2]-a[2]),height=b[1]-a[1],distance=Math.max(20,span*.9,height*.65),x=c[0]-distance*.7,z=c[2]-distance,y=Math.max(b[1]+distance*.4,r.sampler.height(x,z)+10);r.camera.position.set(x,y,z);r.controls.target.fromArray(c);r.controls.update();r.camera.updateMatrixWorld(true);const time=document.getElementById('time');time.value='15:00';time.dispatchEvent(new Event('input',{bubbles:true}));},m.worldBounds);
  await settle();row.closeup=await inspect(m.uid);const file=m.uid.replaceAll('/','-').replaceAll(':','-')+'.jpg';await page.screenshot({path:new URL(file,output).pathname,type:'jpeg',quality:85});row.closeup.file=file;row.closeup.sha256=createHash('sha256').update(await readFile(new URL(file,output))).digest('hex');
  console.log(JSON.stringify({uid:m.uid,active:row.closeup.active,old:row.originalViews.map(x=>({distance:x.distance,pixels:x.projectedPixels,sourceLoaded:x.sourceLoaded,wanted:x.wanted,active:x.active})),close:row.closeup.cache.errors}));
  await writeFile(new URL('report.json',output),JSON.stringify(report,null,2)+'\n');
 }
}finally{report.finished=new Date().toISOString();report.counts={candidates:report.parts.length,activeInCloseup:report.parts.filter(p=>p.closeup?.active).length,errors:report.errors.length};await writeFile(new URL('report.json',output),JSON.stringify(report,null,2)+'\n');await browser.close();}
assert.equal(report.errors.length,0);assert.equal(report.counts.activeInCloseup,missing.length,'Some candidates remain inactive; inspect report rather than raising budgets.');
