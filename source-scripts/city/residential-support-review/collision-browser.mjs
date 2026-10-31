/** Installed native physics replay; only review instrumentation is injected. */
import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {browserExecutable} from '../landmark-preflight/browser-runtime.mjs';
const root=new URL('../../../',import.meta.url),require=createRequire(new URL('3d-viewer/city/package.json',root)),{chromium}=require('playwright');
const manifest=JSON.parse(await readFile(new URL('3d-viewer/city/data/manifest.json',root))),uid='landsd/268527:0',depotUid='landsd/324455:0';let building;
for(const t of manifest.tiles){const b=JSON.parse(await readFile(new URL('3d-viewer/'+t.url,root))).buildings.find(b=>b.uid===uid);if(b){building=b;break;}}
const report={issue:'HKS-214',uid,depotUid,errors:[],views:[],runtimeSHA256:{},limitations:['Browser mobile viewport is not physical handset CPU evidence.','Aircraft spawn/avoidance keeps its separate conservative maximum-roof envelope.']};
for(const f of ['geo.js','model-collision.js','building-geometry.js'])report.runtimeSHA256[f]=createHash('sha256').update(await readFile(new URL('3d-viewer/city/'+f,root))).digest('hex');
const browser=await chromium.launch({headless:true,executablePath:browserExecutable(chromium),args:['--enable-webgl','--ignore-gpu-blocklist']}),page=await browser.newPage({viewport:{width:1280,height:900}});
try{
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__physicsReview",{get:()=>({stream,camera,controls,visitBuilding,officialModels})});\n'});});
 await page.goto('http://127.0.0.1:4176/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});
 await page.evaluate(b=>window.__physicsReview.visitBuilding(b),building);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});
 await page.evaluate(()=>{const r=window.__physicsReview;r.camera.position.set(11240,85,-960);r.controls.target.set(11190,24,-1008);r.controls.update();});
 await page.waitForFunction(([u,d])=>window.__physicsReview.stream.detailedModels.get(u)?.active&&window.__physicsReview.stream.detailedModels.get(d)?.active,[uid,depotUid],{timeout:120000});
 for(const [label,viewport]of [['desktop',{width:1280,height:900}],['mobile-viewport',{width:390,height:844}]]){
  await page.setViewportSize(viewport);
  const result=await page.evaluate(async({uid,depotUid})=>{
   const {BuildingIndex}=await import('/city/geo.js'),{modelRoofHeight}=await import('/city/model-collision.js'),r=window.__physicsReview,target=r.stream.detailedModels.get(uid),depot=r.stream.detailedModels.get(depotUid),a=new BuildingIndex([target.record]),b=new BuildingIndex([depot.record]);
   const p=[11180.234375,29.109996795654297,-1012.8776041666666],query=i=>i.collision(p[0],p[2],p[1]-.05,p[1]+.05,.05)?.uid||null;
   const coldStart=performance.now(),own=query(a),other=query(b),coldMs=performance.now()-coldStart;
   const start=performance.now();for(let i=0;i<1000;i++){query(a);query(b);}const repeated2000QueriesMs=performance.now()-start;
   return{targetActive:target.active,depotActive:depot.active,point:p,target:own,depot:other,scene:query(r.stream),depotLocalRoof:modelRoofHeight(depot.record.modelGeometry,p[0],p[2]),depotGlobalTop:depot.bounds.max.y,coldTwoQueriesMs:coldMs,repeated2000QueriesMs,sourcePositionY:target.record.modelGeometry.position[target.record.modelGeometry.index[32*3]*3+1],supportHolds:r.officialModels.stats.supportHolds};
  },{uid,depotUid});
  report.views.push({label,viewport,...result});
  if(!result.targetActive||!result.depotActive||result.target!==uid||result.depot!==null||result.scene!==uid)throw Error('Installed native physics regression failed');
 }
 report.status=report.errors.length?'failed-page-errors':'passed';
}finally{await writeFile(new URL('docs/astra-city/residential-support-review/collision-browser.json',root),JSON.stringify(report,null,2)+'\n');await browser.close();}
console.log(JSON.stringify(report,null,2));if(report.status!=='passed')process.exitCode=1;
