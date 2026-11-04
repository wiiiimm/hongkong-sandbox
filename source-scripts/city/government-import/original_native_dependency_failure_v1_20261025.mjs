/** Supplemental native dependency failure/recovery test; no publication. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root))),sha=b=>createHash('sha256').update(b).digest('hex');
const [inputPath,outPath]=process.argv.slice(2),input=await read(inputPath),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
for(const r of input.evidenceRefs)assert.equal(sha(await readFile(new URL(r.path,root))),r.sha256,r.path);
const catalogue=await read(input.stage+'catalogue.json'),source=catalogue.models.find(m=>m.uid===input.uid),parent=input.parent.entry;
assert.equal(catalogue.models.length,1);assert(source&&source.sha256===input.sourceSHA256);
assert.deepEqual(source.supportDependencies,[{uid:parent.uid,state:'installed',buildingCSUID:parent.buildingCSUID,sha256:parent.sha256}]);
assert.equal(source.publicationApproved,false);assert.equal(parent.uid,input.parent.uid);
const url=new URL(input.viewerURL);assert(url.protocol==='http:'&&url.hostname==='127.0.0.1'&&url.pathname==='/city.html'&&!url.search&&!url.hash&&!url.username&&!url.password);
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist']});
const report={uid:source.uid,parentUid:parent.uid,sourceSHA256:source.sha256,parentSHA256:parent.sha256,width:390,errors:[],deniedParentRequests:0,successfulParentRequests:0,sourceGeometryChanges:0,installationApproved:false,publication:false};
try{
 const context=await browser.newContext({viewport:{width:390,height:900},hasTouch:true}),page=await context.newPage(),cdp=await context.newCDPSession(page);await cdp.send('Network.clearBrowserCache');let allowParent=false;
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/city/app.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__port",{get:()=>({scene,officialModels,stream,camera,controls,renderer,visitBuilding})});window.__portOriginalRender=renderer.render.bind(renderer);renderer.render=()=>{};'});});
 await page.route('**/city/data/manifest.json',async route=>{const response=await route.fetch(),m=await response.json();assert(!m.officialModelCatalogues.includes(input.catalogueURL));m.officialModelCatalogues.push(input.catalogueURL);await route.fulfill({response,json:m});});
 await page.route('**/'+input.catalogueURL,route=>route.fulfill({json:catalogue}));
 const sourceAsset=input.catalogueURL.slice(0,input.catalogueURL.lastIndexOf('/')+1)+source.asset;
 await page.route('**/'+sourceAsset+'*',async route=>{const body=await readFile(new URL(input.stage+source.asset,root));assert.equal(sha(body),source.sha256);await route.fulfill({body});});
 await page.route('**/'+input.parent.assetURL+'*',async route=>{
  if(!allowParent){report.deniedParentRequests++;await route.fulfill({status:503,body:'Intentional native dependency test'});return;}
  const response=await route.fetch({timeout:120000}),body=await response.body();assert.equal(response.status(),200);assert.equal(body.length,parent.bytes);assert.equal(sha(body),parent.sha256);report.successfulParentRequests++;await route.fulfill({response,body});
 });
 await page.goto(input.viewerURL);await page.waitForFunction(()=>window.__city?.ready&&window.__port?.stream,null,{timeout:300000});await page.locator('#loading').waitFor({state:'hidden',timeout:300000});
 await page.evaluate(async ({catalogueURL,parentCatalogue})=>{const r=window.__port;await r.officialModels.loadCatalogue(catalogueURL);await r.officialModels.loadCatalogue(parentCatalogue);const unpause=r.officialModels.setLoadingPaused.bind(r.officialModels);unpause(false);r.officialModels.setLoadingPaused=p=>{if(!p)unpause(false);};},{catalogueURL:input.catalogueURL,parentCatalogue:input.parent.catalogueURL});
 await page.evaluate(form=>window.__port.visitBuilding(form),input.form);
 await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:180000});
 await page.evaluate(uid=>{const r=window.__port;r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,allowNewLoads:true,force:true});},source.uid);
 await page.waitForFunction(({uid,parentUid})=>{const r=window.__port,b=r.stream.getLoadedBuilding(uid),e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(f=>f.uid===uid));if(!r.officialModels.cache.errors.has(parentUid)||!b||b.hidden||!e||e.detailSuppressions?.has(uid)||e.buildings.group.visible===false||r.stream.detailedModels.get(uid)?.active)return false;const i=e.data.buildings.findIndex(f=>f.uid===uid);return e.buildings.group.children.some(m=>m.visible!==false&&m.geometry?.attributes.feature&&Array.from(m.geometry.attributes.feature.array).includes(i));},{uid:source.uid,parentUid:parent.uid},{timeout:120000});
 report.failed=await page.evaluate(({uid,parentUid})=>{const r=window.__port,b=r.stream.getLoadedBuilding(uid),e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(f=>f.uid===uid)),i=e.data.buildings.findIndex(f=>f.uid===uid);return {uid,parentUid,sourceSHA256:r.officialModels.models.get(uid).sha256,parentSHA256:r.officialModels.models.get(parentUid).sha256,parentFailed:r.officialModels.cache.errors.has(parentUid),active:!!r.stream.detailedModels.get(uid)?.active,parentActive:!!r.stream.detailedModels.get(parentUid)?.active,basicLoaded:!!b,basicHidden:!!b.hidden,detailSuppressed:!!e.detailSuppressions?.has(uid),basicGroupVisible:e.buildings.group.visible===true,ownFeaturePresent:e.buildings.group.children.some(m=>m.visible!==false&&m.geometry?.attributes.feature&&Array.from(m.geometry.attributes.feature.array).includes(i)),dependencies:r.officialModels.models.get(uid).supportDependencies};},{uid:source.uid,parentUid:parent.uid});
 assert(report.deniedParentRequests>0&&report.failed.parentFailed&&!report.failed.active&&!report.failed.parentActive&&report.failed.basicLoaded&&!report.failed.basicHidden&&!report.failed.detailSuppressed&&report.failed.basicGroupVisible&&report.failed.ownFeaturePresent);
 assert.equal(report.failed.sourceSHA256,source.sha256);assert.equal(report.failed.parentSHA256,parent.sha256);assert.deepEqual(report.failed.dependencies,source.supportDependencies);
 allowParent=true;await page.locator('#stream-retry').click();
 await page.evaluate(uid=>{const r=window.__port;r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,allowNewLoads:true,force:true});},source.uid);
 await page.waitForFunction(({uid,parentUid})=>{const r=window.__port;return r.stream.detailedModels.get(uid)?.active&&r.stream.detailedModels.get(parentUid)?.active;},{uid:source.uid,parentUid:parent.uid},{timeout:180000});
 report.recovered=await page.evaluate(({uid,parentUid})=>{const r=window.__port;return [uid,parentUid].map(uid=>({uid,active:!!r.stream.detailedModels.get(uid)?.active,visible:!!r.stream.detailedModels.get(uid)?.group?.visible,sourceSHA256:r.officialModels.models.get(uid).sha256,triangles:r.stream.detailedModels.get(uid)?.record?.modelGeometry?.index?.length/3}));},{uid:source.uid,parentUid:parent.uid});
 assert(report.successfulParentRequests>0);assert(report.recovered.every(m=>m.active&&m.visible));assert.deepEqual(report.recovered.map(m=>m.sourceSHA256),[source.sha256,parent.sha256]);assert.deepEqual(report.recovered.map(m=>m.triangles),[source.triangles,parent.triangles]);assert.deepEqual(report.errors,[]);report.passed=true;await context.close();
}catch(error){report.passed=false;report.failure={message:error.message,stack:error.stack};process.exitCode=1;}finally{await browser.close();for(const r of input.evidenceRefs)assert.equal(sha(await readFile(new URL(r.path,root))),r.sha256,r.path);await mkdir(new URL('.',new URL(outPath,root)),{recursive:true});await writeFile(new URL(outPath,root),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({passed:report.passed,denied:report.deniedParentRequests,recovered:report.successfulParentRequests}));
