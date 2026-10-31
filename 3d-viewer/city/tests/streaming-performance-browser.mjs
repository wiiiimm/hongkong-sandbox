// Reproducible cloud/emulation correctness + stage timing, never device FPS certification.
import {chromium} from 'playwright';
import {writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const label=process.argv[2]||'after',out=new URL(`../../../docs/astra-city/mobile-model-streaming/evidence/${label}.json`,import.meta.url);
const report={label,environment:'Linux cloud Chromium / SwiftShader; viewport emulation, not physical-device acceptance',started:new Date().toISOString(),runs:[]};
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-webgl','--ignore-gpu-blocklist','--enable-unsafe-swiftshader']});report.browser=await browser.version();
try{
 for(const [width,height] of [[390,844],[1440,900]]){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'}),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/__livereload',r=>r.abort());
  await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:await response.text()+'\nwindow.__streamReview={officialModels,stream,camera,controls,renderer,nav,visitBuilding,ensureBackgroundData};\n'});});
  const start=Date.now();await page.goto((process.env.CITY_URL||'http://127.0.0.1:8777/city.html')+'?district=central&streamingMetrics=1');
  await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});
  console.log(label,width,'app ready');
  await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling&&!window.__city.state.stream.pending,null,{timeout:90000}).catch(async error=>{report.failure={message:error.message,state:await page.evaluate(()=>window.__city.state),metrics:await page.evaluate(()=>window.__city.metrics.snapshot),errors};throw error;});
  const run={width,height,startupMs:Date.now()-start,errors,phases:[]};report.runs.push(run);console.log(label,width,'base ready');
  await page.evaluate(()=>window.__streamReview.ensureBackgroundData());
  const uid=await page.evaluate(()=>{const {stream}=window.__streamReview;return ['landsd/89275:0','landsd/123884:0'].find(uid=>stream.getLoadedBuilding(uid));});assert.ok(uid);
  await page.evaluate(uid=>window.__streamReview.visitBuilding(window.__streamReview.stream.getLoadedBuilding(uid)),uid);
  await page.waitForFunction(uid=>window.__streamReview.stream.detailedModels.get(uid)?.active,uid,{timeout:120000});
  await page.waitForTimeout(1500);
  const runPhase=async(name,action)=>{await page.evaluate(()=>window.__city.metrics.reset());await action();run.phases.push({name,...await page.evaluate(()=>({metrics:window.__city.metrics.snapshot,models:window.__city.state.models,render:window.__city.state.render}))});};
  await runPhase('stable',()=>page.waitForTimeout(4000));
  for(const name of ['cold-reversal','warm-reversal'])await runPhase(name,()=>page.evaluate(async()=>{
   const {camera,controls}=window.__streamReview,origin=camera.position.clone(),target=controls.target.clone(),offset=origin.clone().sub(target);
   for(const a of [0,.65,1.3,.65,0,-.65,0]){camera.position.copy(target).add(offset.clone().applyAxisAngle({x:0,y:1,z:0},a));controls.update();await new Promise(r=>setTimeout(r,450));}
   camera.position.copy(origin);controls.target.copy(target);controls.update();
  }));
  await runPhase('resize',async()=>{for(const [w,h] of [[844,390],[600,800],[1920,1080],[width,height]]){await page.setViewportSize({width:w,height:h});await page.waitForTimeout(400);}});
  run.final=await page.evaluate(()=>window.__city.state);assert.equal(errors.length,0);await context.close();
  await mkdir(new URL('.',out),{recursive:true});await writeFile(out,JSON.stringify(report,null,2)+'\n');console.log(label,width,'complete');
 }
}finally{await browser.close();await mkdir(new URL('.',out),{recursive:true});await writeFile(out,JSON.stringify(report,null,2)+'\n');}
