/** Private source-interface interpretation only. No terrain hooks or acceptance. */
import {readFile,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makePrivateInterfaceCatalogue} from './heritage_private_interface_catalogue_v1_20261014.mjs';
import {installPrivateSourceScheduler} from './heritage_private_source_scheduler_v1_20261014.mjs';
import {fitIndexedSourceBox} from './upton_private_indexed_source_framing_v1_20261014.mjs';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],sha=b=>createHash('sha256').update(b).digest('hex');
const closures=[snapshotModuleClosure(import.meta.url,root),snapshotModuleClosure(new URL('3d-viewer/city/app.js',root),root)];
if(process.argv.includes('--closure-only')){assert(!existsSync(new URL(doc,root)));await writeFile(new URL(doc,root),JSON.stringify(closures,null,2)+'\n');process.exit(0);}
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-')&&doc.endsWith('/')&&!doc.includes('..'));
const read=async p=>{const b=await readFile(new URL(p,root));return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);},input=await read(doc+'preview-input.json');
async function fence(){for(const q of input.executionRefs)assert.equal(sha(await readFile(new URL(q.path,root))),q.sha256,q.path);for(const c of closures)verifyModuleClosure(c,root);}
await fence();
const museum=await read(input.museumCapture.path),star=await read(input.starCapture.path),contacts=await read(input.savedOriginalContacts.path),basicContacts=await read(input.savedBASICContacts.path);
const expectedSources=[{...input.sources[0],position:museum.completeLiteralWorldPosition,index:museum.completeOriginalIndex},{...input.sources[1],position:star.completeLiteralWorldPosition,index:star.mesh.completeIndex}];
function indexed(row){const values=[];for(const i of row.index)values.push(...row.position.slice(i*3,i*3+3));return values;}
const expected=expectedSources.map(s=>({uid:s.uid,faces:s.faces,worldTriangleSHA256:sha(new Float64Array(indexed(s))),sourceSHA256:s.asset.sha256}));
const detailPoints=[...input.museumInterfaceFaceIDs.flatMap(f=>museum.completeOriginalIndex.slice(f*3,f*3+3).map(i=>museum.completeLiteralWorldPosition.slice(i*3,i*3+3))),...star.mesh.completeIndex.map(i=>star.completeLiteralWorldPosition.slice(i*3,i*3+3))];
const allPoints=expectedSources.flatMap(s=>s.index.map(i=>s.position.slice(i*3,i*3+3)));
const rational=s=>{const[a,b='1']=String(s).split('/');return Number(a)/Number(b);};
const originalLines=contacts.allFourViews.find(r=>r.arithmetic==='literal').pairs['Museum-vs-originalStar'].contacts.contacts.map(r=>({a:r.sourceFaceA,b:r.sourceFaceB,points:r.exactPoints.map(p=>p.map(rational))}));
const basicRows=basicContacts.fourViews;
assert(Array.isArray(basicRows)&&basicRows.length===4);
// The exact source-only packet is preserved verbatim; only these saved lines are
// converted for a canvas locator. They do not enter geometry/collision buffers.
const basicView=basicRows.find(r=>r.arithmetic==='literal');
const basicHits=basicView.fullFiniteSurfaceContacts.contacts;
assert(Array.isArray(basicHits)&&basicHits.length===14);
const basicLines=basicHits.map(r=>({a:r.sourceFaceA,b:r.sourceFaceB,points:r.exactPoints.map(p=>p.map(rational))}));
assert.equal(originalLines.length,8);
const require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
const report={sourceInterpretationOnly:true,sourceRoleAccepted:false,physicalAccepted:false,installationApproved:false,sourceGeometryChanges:0,terrainChanges:0,liveWrites:0,views:[],errors:[],scenarios:[]};
try{
 for(const scenario of ['current-BASIC','original-Star']){
  const context=await browser.newContext({viewport:{width:1600,height:1100}}),page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  report.loadingDiagnostics??=[];report.assetRequests??=[];
  page.on('requestfailed',q=>report.assetRequests.push({scenario,url:q.url(),failure:q.failure()}));
  page.on('response',q=>{if(q.status()>=400)report.assetRequests.push({scenario,url:q.url(),status:q.status()});});
  async function status(phase,uid){const row=await page.evaluate(({phase,uid})=>{const r=window.__heritageSource,b=r.stream.getLoadedBuilding(uid),m=r.officialModels.models.get(uid),d=r.stream.detailedModels.get(uid);return{phase,uid,modelKnown:!!m,modelSourceSHA256:m?.sha256,buildingLoaded:!!b,buildingTile:b?.tile,selected:window.__city.state.selectedId,state:window.__city.state,official:r.officialModels.stats,stream:r.stream.stats,catalogueErrors:[...r.officialModels.catalogueErrors.entries()],cacheError:r.officialModels.cache.errors.get(uid)?.stack??String(r.officialModels.cache.errors.get(uid)||''),wanted:r.officialModels.cache.wanted.slice(),detailedActive:!!d?.active,schedulerError:window.__heritageScheduler?.lastError??null};},{phase,uid});report.loadingDiagnostics.push({scenario,...row});return row;}
  const catalogue=makePrivateInterfaceCatalogue(input.sources,scenario),models=catalogue.models,url='city/data/private-source-review/'+input.batch+'/'+scenario+'/catalogue.json',base=url.slice(0,url.lastIndexOf('/')+1);
  await page.route('**/city/app.js*',async r=>{const response=await r.fetch(),text=await response.text();assert.equal(sha(Buffer.from(text)),input.executionRefs.find(q=>q.path==='3d-viewer/city/app.js').sha256);await r.fulfill({response,body:text+'\nObject.defineProperty(window,"__heritageSource",{get:()=>({scene,terrain,officialModels,stream,camera,controls,renderer,THREE,visitBuilding,controlSheet,environment,closeSelection})});window.__heritageRender=renderer.render.bind(renderer);renderer.render=()=>{};'});});
  await page.route('**/'+url,r=>r.fulfill({json:catalogue}));
  for(const m of models){const s=input.sources.find(s=>s.uid===m.uid),b=await readFile(new URL(s.asset.path,root));assert.equal(sha(b),m.sha256);await page.route('**/'+base+m.asset+'*',r=>r.fulfill({body:b}));}
  await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),text=await response.text();assert.equal(sha(Buffer.from(text)),input.currentManifest.sha256);const m=JSON.parse(text);assert(!m.officialModelCatalogues.includes(url));m.officialModelCatalogues.push(url);await r.fulfill({response,json:m});});
  await page.goto('http://127.0.0.1:4176/city.html');await page.waitForFunction(()=>window.__city?.ready&&window.__heritageSource?.stream,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden',timeout:120000});
  await page.evaluate(()=>window.__heritageSource.environment.setHour(12));const catalogueLoaded=await page.evaluate(url=>window.__heritageSource.officialModels.loadCatalogue(url),url);for(const m of models){const d=await status('after-catalogue-before-travel',m.uid);assert(catalogueLoaded&&d.modelKnown,'Private compact catalogue rejected: '+JSON.stringify(d.catalogueErrors));}
  for(const s of input.sources){await page.evaluate(async b=>window.__heritageSource.visitBuilding(b),s.currentForm);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:90000});}
  // Frame complete unchanged indexed sources before scheduling, so the tiny
  // neighbouring Star visit cannot leave the Museum outside the fixture camera.
  const loadingFit=fitIndexedSourceBox(allPoints,{fov:45,aspect:1600/1100,direction:[-1,.65,1],near:.5});
  await page.evaluate(({fit,installText})=>{const r=window.__heritageSource;r.closeSelection();r.controls.enableDamping=false;r.camera.fov=45;r.camera.near=.5;r.camera.updateProjectionMatrix();r.camera.position.fromArray(fit.camera);r.controls.target.fromArray(fit.target);r.controls.update();r.camera.updateMatrixWorld(true);window.__heritageScheduler=(0,eval)('('+installText+')')(r);},{fit:loadingFit,installText:installPrivateSourceScheduler.toString()});
  for(const m of models){
   await status('before-request',m.uid);
   await page.evaluate(uid=>window.__heritageScheduler.start(uid),m.uid);
   try{await page.waitForFunction(uid=>window.__heritageSource.stream.detailedModels.get(uid)?.active,m.uid,{timeout:90000});}
   catch(error){await status('timeout-or-loader-failure',m.uid);throw error;}
   await status('active',m.uid);
  }
  await page.evaluate(()=>window.__heritageScheduler.stop());
  const bindings=await page.evaluate(async({expected,scenario})=>{const r=window.__heritageSource,hash=async a=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',a.buffer.slice(a.byteOffset,a.byteOffset+a.byteLength)))].map(v=>v.toString(16).padStart(2,'0')).join(''),out=[];for(const s of expected.filter(s=>scenario==='original-Star'||s.uid==='landsd/165054:0')){const d=r.stream.detailedModels.get(s.uid);if(r.officialModels.models.get(s.uid)?.sha256!==s.sourceSHA256)throw Error('Source byte binding mismatch '+s.uid);if(!d?.active||!d.group.visible)throw Error('Original inactive '+s.uid);const g=d.record.modelGeometry,values=[];for(const i of g.index)values.push(...g.position.slice(i*3,i*3+3));const h=await hash(new Float64Array(values));if(h!==s.worldTriangleSHA256||g.index.length/3!==s.faces)throw Error('Literal source mismatch '+s.uid);const gpu=[];d.group.updateMatrixWorld(true);for(const m of d.meshes){const materials=Array.isArray(m.material)?m.material:[m.material];if(!m.visible||materials.some(a=>a.wireframe||a.opacity!==1))throw Error('Opaque original required');gpu.push({positionByteSHA256:await hash(m.geometry.attributes.position.array),matrixWorld:m.matrixWorld.elements.slice(),arrayType:m.geometry.attributes.position.array.constructor.name,vertices:m.geometry.attributes.position.count});}out.push({...s,actualGPU:gpu,noManualGPURecast:true});}const basic=r.stream.getLoadedBuilding('landsd/57455:0');if(!basic)throw Error('Star current form unloaded');let drawn=0;for(const e of r.stream.cache.entries.values())for(const mesh of e.buildings.group.children){if(!e.buildings.group.visible||!mesh.visible)continue;const f=mesh.geometry.attributes.feature,ix=mesh.geometry.index;if(!f)continue;for(let i=0;i<(ix?.count??f.count);i+=3){const v=ix?ix.getX(i):i;if(e.data.buildings[Math.round(f.getX(v))]?.uid==='landsd/57455:0')drawn++;}}if(scenario==='current-BASIC'&&(drawn!==24||r.stream.detailedModels.get('landsd/57455:0')?.active||basic.hidden))throw Error('Complete current BASIC24 must be drawn');if(scenario==='original-Star'&&drawn!==0)throw Error('Original comparison must replace only own BASIC');return{sources:out,currentBASICDrawnFaces:drawn,currentStarFormLoaded:true,privateOriginalStarNotIdentityOrInstallationApproval:scenario==='original-Star'};},{expected,scenario});
report.scenarios.push({scenario,...bindings});
  for(const v of [{id:'assembly',direction:[-1,.65,1],points:allPoints},{id:'corner-east',direction:[1,.7,1],points:detailPoints},{id:'corner-west',direction:[-1,.7,-1],points:detailPoints}]){
   const fit=fitIndexedSourceBox(v.points,{fov:45,aspect:1600/1100,direction:v.direction,near:.5});
   await page.evaluate(fit=>{const r=window.__heritageSource;document.getElementById('heritage-overlay')?.remove();r.closeSelection();r.controls.enableDamping=false;r.camera.fov=45;r.camera.near=.5;r.camera.updateProjectionMatrix();r.camera.position.fromArray(fit.camera);r.controls.target.fromArray(fit.target);r.controls.update();r.camera.updateMatrixWorld(true);document.getElementById('building-card').hidden=true;r.controlSheet?.close({restoreFocus:false});for(const p of fit.boundsCorners){const q=new r.THREE.Vector3(...p).project(r.camera);if(Math.abs(q.x)>.74||Math.abs(q.y)>.70||q.z< -1||q.z>1)throw Error('Source framing failed');}window.__heritageRender(r.scene,r.camera);},fit);
   const clean=doc+scenario+'-'+v.id+'-solid-1600x1100.png';await page.screenshot({path:new URL(clean,root).pathname});
   await page.evaluate(({lines,scenario})=>{const r=window.__heritageSource,c=document.createElement('canvas');c.id='heritage-overlay';c.width=innerWidth;c.height=innerHeight;Object.assign(c.style,{position:'fixed',inset:0,pointerEvents:'none',zIndex:9999});document.body.append(c);const ctx=c.getContext('2d');ctx.fillStyle='rgba(255,255,255,.95)';ctx.fillRect(8,8,innerWidth-16,60);ctx.fillStyle='#111';ctx.font='16px sans-serif';ctx.fillText('PRIVATE '+scenario+': full immutable Museum15140; independent Star remains separate.',18,30);ctx.fillText('Saved '+lines.length+' crossings, canvas locators ignore occlusion. No role/physical/installation approval.',18,53);ctx.lineWidth=3;ctx.strokeStyle='#e12e68';const project=p=>{const q=new r.THREE.Vector3(...p).project(r.camera);return[(q.x+1)*innerWidth/2,(1-q.y)*innerHeight/2,q.z];};for(const line of lines){const q=line.points.map(project);if(!q.every(p=>p[2]>=-1&&p[2]<=1))continue;ctx.beginPath();q.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.stroke();ctx.fillStyle='#a50035';ctx.fillText('M'+line.a+'/S'+line.b,q[0][0]+4,q[0][1]-4);}}, {scenario,lines:scenario==='current-BASIC'?basicLines:originalLines});
   const marked=doc+scenario+'-'+v.id+'-marked-1600x1100.png';await page.screenshot({path:new URL(marked,root).pathname});report.views.push({scenario,id:v.id,cleanSolidImage:clean,markedImage:marked,framing:fit,dimensions:[1600,1100],selectionClosed:true,canvasLocatorsNotDepthTested:true,noPickingCollisionOrAcceptanceCredit:true});
  }
  await context.close();await fence();
 }
 assert.equal(report.errors.length,0);assert.equal(report.views.length,6);
}finally{await browser.close();await writeFile(new URL(doc+'actual-private-interface-preview.json',root),JSON.stringify(report,null,2)+'\n');}
