import {chromium} from 'playwright';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const phase=process.argv[2]||'after',output=fileURLToPath(new URL('../../../docs/astra-city/mui-wo-buildings/browser/',import.meta.url));await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']}),page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',e=>{if(e.type()==='error')errors.push(e.text());});
const report={phase,errors};
const settle=()=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.bridges.pending&&!s.regional.pending;},null,{timeout:120000});
try{
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__buildingReview",{get:()=>({stream,camera,controls,sampler,scene,renderer,THREE})});\n'});});
 await page.goto('http://127.0.0.1:4176/city.html?district=muiwo');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle();
 await page.locator('#tab-time').click();await page.locator('#time').fill('15:00');await page.locator('#tab-places').click();await page.waitForTimeout(600);
 report.overview=await page.evaluate(()=>window.__city.state);await page.screenshot({path:output+phase+'-mui-wo-overview-1440x1000.png'});
 report.market=await page.evaluate(()=>{
  const {stream,camera,controls,sampler,THREE}=window.__buildingReview,b=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings).find(b=>b.uid==='landsd/174478:0');if(!b)throw Error('Cooked food market missing');
  const [x,z]=b.centre,top=b.base+b.height;camera.position.set(x+42,top+14,z+46);controls.target.set(x,top-2,z);controls.update();camera.updateMatrixWorld();
  const meshes=stream.buildings.children.filter(g=>g.visible).flatMap(g=>g.children),ray=new THREE.Raycaster(),points=[b.centre,...b.rings[0].slice(0,-1).map(p=>[p[0]*.75+x*.25,p[1]*.75+z*.25])];let click;
  for(const [px,pz] of points){const projected=new THREE.Vector3(px,top,pz).project(camera);ray.setFromCamera(new THREE.Vector2(projected.x,projected.y),camera);const hit=ray.intersectObjects(meshes,false)[0];if(hit&&stream.featureAt(hit)?.uid===b.uid){click={x:(projected.x+1)*innerWidth/2,y:(1-projected.y)*innerHeight/2};break;}}
  return {uid:b.uid,name:b.name,base:b.base,top,sourceBase:b.baseHeightHKPD,sourceTop:b.topHeightHKPD,click,ground:sampler.height(x,z),centre:b.centre};
 });
 await page.waitForTimeout(1000);await settle();await page.screenshot({path:output+phase+'-market-day-1440x1000.png'});
 report.perf=await page.evaluate(async()=>{const frames=[];let previous=performance.now();for(let i=0;i<90;i++){await new Promise(requestAnimationFrame);const now=performance.now();frames.push(now-previous);previous=now;}frames.sort((a,b)=>a-b);return {medianFrameMs:frames[45],p95FrameMs:frames[85],render:window.__city.state.render,stream:window.__city.state.stream};});
 assert.ok(report.market.click,'source roof can be selected through actual ray');await page.mouse.click(report.market.click.x,report.market.click.y);await page.waitForFunction(()=>window.__city.state.selectedId==='landsd/174478:0');
 report.card=await page.locator('#building-card').innerText();await page.screenshot({path:output+phase+'-market-source-card-1440x1000.png'});await page.locator('#selection-close').click();
 await page.locator('#tab-time').click();await page.locator('#time').fill('21:00');await page.locator('#tab-places').click();await page.waitForTimeout(600);await page.screenshot({path:output+phase+'-market-night-1440x1000.png'});
 if(phase==='after'){
  report.geometry=await page.evaluate(async()=>{
   const {describeBuilding,collisionVolumes}=await import('/city/building-geometry.js'),{BuildingIndex,inPolygon}=await import('/city/geo.js'),{stream,THREE}=window.__buildingReview;
   const roofs=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings).filter(b=>b.structureType==='Open-sided Structure'),b=roofs.find(b=>b.uid==='landsd/174478:0'),description=describeBuilding(b),index=new BuildingIndex([b]);
   let air=null;
   for(let x=Math.min(...b.rings[0].map(p=>p[0]));x<=Math.max(...b.rings[0].map(p=>p[0]));x+=1)for(let z=Math.min(...b.rings[0].map(p=>p[1]));z<=Math.max(...b.rings[0].map(p=>p[1]));z+=1){
    if(inPolygon(x,z,b.rings)&&!index.collision(x,z,b.base+.15,b.base+1.95,.45)){air=[x,z];break;}
   }
   const post=collisionVolumes(b).find(p=>p.kind==='post'),px=(post.bounds[0]+post.bounds[2])/2,pz=(post.bounds[1]+post.bounds[3])/2;
   return {roofs:roofs.length,posts:roofs.reduce((n,b)=>n+describeBuilding(b).illustrativeSupports,0),marketPosts:description.illustrativeSupports,air,postBlocked:!!index.collision(px,pz,b.base+.15,b.base+1.95,.2),roofBlocked:!!index.collision(...[air[0],air[1],b.base+b.height-.1,b.base+b.height+.1,.1])};
  });
  assert.ok(report.geometry.roofs>=200);assert.ok(report.geometry.air);assert.equal(report.geometry.postBlocked,true);assert.equal(report.geometry.roofBlocked,true);
  await page.locator('#tab-time').click();await page.locator('#time').fill('15:00');await page.locator('#tab-places').click();
  report.isolatedRoof=await page.evaluate(async()=>{
   const {stream,camera,controls,sampler}=window.__buildingReview,{describeBuilding}=await import('/city/building-geometry.js');
   const b=[...stream.cache.entries.values()].flatMap(e=>e.data.buildings).find(b=>b.uid==='landsd/316300:0'),d=describeBuilding(b),[x,z]=b.centre,top=d.parts.find(p=>p.kind==='roof')?.top||b.base+b.height;
   camera.position.set(x+38,top+5,z+43);controls.target.set(x,top-4,z);controls.update();camera.updateMatrixWorld();return {uid:b.uid,base:b.base,height:b.height,modelStatus:d.modelStatus,roofTop:top,posts:d.illustrativeSupports,ground:sampler.height(x,z)};
  });
  await page.waitForTimeout(1000);await settle();await page.screenshot({path:output+'after-open-sided-316300-day-1440x1000.png'});
  await page.locator('#tab-time').click();await page.locator('#time').fill('21:00');await page.locator('#tab-places').click();await page.waitForTimeout(500);await page.screenshot({path:output+'after-open-sided-316300-night-1440x1000.png'});
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(500);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:output+'after-market-mobile-390x844.png'});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(report.overview.stream.errors,[]);report.result='passed';
}catch(e){report.result='failed';report.failure=e.stack;throw e;}finally{await writeFile(output+phase+'-verification.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));await browser.close();}
