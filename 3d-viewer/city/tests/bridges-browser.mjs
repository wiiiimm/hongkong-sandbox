import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {PLACES} from '../places.js';

const output=fileURLToPath(new URL('../../../docs/astra-city/bridges/browser/',import.meta.url));
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':undefined),args:['--enable-webgl','--ignore-gpu-blocklist']});
const report={result:'running',browser:await browser.version(),url:process.env.CITY_URL||'http://127.0.0.1:4176/city.html',observations:[],errors:[]};
async function createPage(failBridge=false){
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce',hasTouch:true});
 page.on('pageerror',error=>report.errors.push(error.message));
 page.on('console',message=>{if(message.type()==='error'&&!message.text().includes('net::ERR_FAILED'))report.errors.push(message.text());});
 // Expose existing objects only in the served test response. Production files and
 // geometry are unchanged; camera framing and matrix inspection use this getter.
 await page.route('**/city/app.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__bridgeReview",{get:()=>({bridgeLayer,stream,camera,controls,sampler,scene,THREE})});\n'});});
 if(failBridge){let requests=0;await page.route('**/city/data/bridges.json',async route=>{requests++;if(requests===1)await route.abort('failed');else await route.continue();});}
 const url=new URL(report.url);url.searchParams.set('district','central');await page.goto(url.href);
 await page.waitForFunction(()=>window.__city?.ready,null,{timeout:120000});await page.locator('#loading').waitFor({state:'hidden'});await settle(page);
 await page.locator('#tab-time').click();await page.locator('#time').fill('15:00');await page.locator('#tab-places').click();
 return page;
}
const current=page=>page.evaluate(()=>window.__city.state);
const settle=page=>page.waitForFunction(()=>{const s=window.__city?.state;return s&&!s.loadingTravel&&!s.travelling&&!s.stream.pending&&!s.regional.pending&&!s.bridges.pending;},null,{timeout:90000});
const capture=async(page,name)=>{await page.waitForTimeout(200);await page.screenshot({path:output+name+'.png'});};
async function choose(page,id){if((await page.viewportSize()).width<=760&&!await page.locator('#explorer').evaluate(e=>e.classList.contains('open')))await page.locator('#panel-toggle').click();await page.locator('#tab-places').click();await page.locator(`[data-region="${PLACES[id].region}"]`).click();await page.locator(`[data-place="${id}"]`).click();await settle(page);}
async function frame(page,id){
 const result=await page.evaluate(id=>{
  const {bridgeLayer:layer,camera,controls,sampler,THREE,stream}=window.__bridgeReview,b=layer.records.get(id);if(!b)throw Error('Missing mapped span '+id);
  const points=b.deckPath.slice(1).map((p,i)=>p.map((v,k)=>(v+b.deckPath[i][k])/2)),centre=points[Math.floor(points.length/2)],distance=Math.max(44,Math.min(115,b.length*.8));
  const meshes=()=>[...stream.buildings.children.filter(g=>g.visible).flatMap(g=>g.children),...layer.pickMeshes()];
  const ray=new THREE.Raycaster(),v=new THREE.Vector3();let best;
  for(const height of [25,48,78])for(let i=0;i<12;i++){
   const angle=i*Math.PI/6,position=[centre[0]+Math.cos(angle)*distance,centre[1]+height,centre[2]+Math.sin(angle)*distance];
   position[1]=Math.max(position[1],sampler.height(position[0],position[2])+3);camera.position.set(...position);controls.target.set(...centre);controls.update();camera.updateMatrixWorld();layer.plan(centre[0],centre[2],3000,camera.position);
   const candidates=[];
   for(const p of points){v.set(...p).project(camera);if(Math.abs(v.x)>.6||Math.abs(v.y)>.6)continue;ray.setFromCamera(new THREE.Vector2(v.x,v.y),camera);const hit=ray.intersectObjects(meshes(),false)[0];if(hit&&layer.featureAt(hit)?.id===id)candidates.push({x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2});}
   if(candidates.length&&(!best||candidates.length>best.count)){best={position,target:centre,point:candidates[Math.floor(candidates.length/2)],count:candidates.length,height};}
  }
  if(!best)throw Error('No unobscured city click ray for '+id);
  camera.position.set(...best.position);controls.target.set(...best.target);controls.update();camera.updateMatrixWorld();layer.plan(centre[0],centre[2],3000,camera.position);
  return {...best,id,name:b.name||'Mapped footbridge',source:b.source,width:b.width,aboveGround:b.aboveGround,covered:b.covered,elevationBasis:b.elevationBasis,deckPath:b.deckPath};
 },id);
 await page.waitForTimeout(800);await settle(page);return result;
}
async function detail(page,id){
 return page.evaluate(id=>{
  const {bridgeLayer:layer}=window.__bridgeReview,index=layer.featureIndices.get(id),parts={deck:0,canopy:0,rails:0,railsVisible:false};let tileKey;
  for(const [key,g] of layer.cache)for(const mesh of g.children){const attr=mesh.geometry?.attributes.bridgeFeature;if(attr&&Array.from(attr.array).includes(index)){parts[mesh.userData.bridgePart]+=attr.count;tileKey=key;}}
  const rails=layer.cache.get(tileKey)?.userData.railMesh;parts.rails=rails?.count||0;parts.railsVisible=!!rails?.visible;return {...parts,tileKey,pickable:layer.pickMeshes().length,stats:layer.stats};
 },id);
}
async function clickDeck(page,id,point){await page.mouse.click(point.x,point.y);await page.waitForFunction(id=>window.__city.state.selectedId===id,id,{timeout:5000});assert.equal(await page.locator('#building-card').isVisible(),true);assert.match(await page.locator('#building-source').innerText(),/Estimated/);assert.match(await page.locator('#building-activity').innerText(),/Elevated walking.*require/);assert.equal(await page.locator('#building-osm').getAttribute('href'),'https://www.openstreetmap.org/'+id);}
async function searchBridge(page,text){await page.locator('#search').fill(text);await page.waitForFunction(()=>[...document.querySelectorAll('#search-results button')].some(e=>e.querySelector('small')?.textContent.includes('Footbridge')));const found=page.locator('#search-results button').filter({has:page.locator('small',{hasText:'Footbridge'})});assert.ok(await found.count()>=1);const named=found.filter({hasText:'Octopus Bridge'});await (await named.count()?named.first():found.first()).click();await settle(page);}
try{
 const page=await createPage();let state=await current(page);assert.equal(state.bridges.spans,12260);assert.equal(state.bridges.covered,3420);assert.deepEqual(state.bridges.errors,[]);
 for(const [place,id] of [['central','way/32511520'],['wanchai','way/40491206'],['tsuenwan','way/470688470'],['muiwo','way/701768072']]){
  await choose(page,place);const framing=await frame(page,id),render=await detail(page,id);assert.ok(render.deck>0);assert.equal(render.canopy>0,framing.covered);assert.equal(render.railsVisible,true);assert.ok(render.stats.tiles<=24);assert.ok(framing.aboveGround>0);await clickDeck(page,id,framing.point);await capture(page,place+'-deck-source-1440x1000');report.observations.push({place,framing,render,sourceText:await page.locator('#building-source').innerText()});
 }
 const before=await detail(page,'way/701768072');await page.locator('#layer-bridges').uncheck();state=await current(page);assert.equal(state.bridges.visibleSpans,0);assert.equal(await page.locator('#building-card').isVisible(),false);assert.equal((await detail(page,'way/701768072')).pickable,0);await capture(page,'mui-wo-layer-hidden-1440x1000');await page.locator('#layer-bridges').check();assert.equal((await current(page)).bridges.visibleSpans,before.stats.visibleSpans);
 const framing=await frame(page,'way/701768072');await page.evaluate(()=>{const {camera,controls,bridgeLayer}=window.__bridgeReview;camera.position.y=controls.target.y+3500;controls.update();bridgeLayer.plan(controls.target.x,controls.target.z,3000,camera.position);});await page.waitForTimeout(800);const far=await detail(page,'way/701768072');assert.equal(far.railsVisible,false);assert.ok(far.deck>0);await capture(page,'mui-wo-aerial-rails-lod-1440x1000');report.railLOD={near:before,far};
 await searchBridge(page,'Octopus Bridge');state=await current(page);assert.equal(await page.locator('#building-name').innerText(),'Octopus Bridge');assert.ok(state.selectedId?.startsWith('way/'));assert.equal(state.region,'nteast');assert.equal(state.mode,'orbit');await capture(page,'octopus-bridge-search-1440x1000');report.search={id:state.selectedId,source:await page.locator('#building-osm').getAttribute('href'),bridges:state.bridges};
 // Mobile named search traverses the actual panel, closes it on arrival, and
 // keeps the selected source card within the viewport.
 await page.setViewportSize({width:390,height:844});await page.locator('#selection-close').click();await page.locator('#panel-toggle').click();await searchBridge(page,'八爪魚');assert.equal(await page.locator('#explorer').evaluate(e=>e.classList.contains('open')),false);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await capture(page,'octopus-bridge-mobile-390x844');
 await page.setViewportSize({width:320,height:844});await page.waitForFunction(()=>document.querySelector('#viewport canvas').clientWidth===innerWidth);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await capture(page,'octopus-bridge-mobile-320x844');
 await page.close();
 const failed=await createPage(true);state=await current(failed);assert.equal(state.bridges.spans,0);assert.equal(state.bridges.errors.length,1);assert.equal(await failed.locator('#stream-retry').isVisible(),true);
 const roads=()=>failed.evaluate(()=>{const {stream}=window.__bridgeReview;return {suppressed:stream.bridgeRoadIds.size,tiles:[...stream.cache.entries].map(([id,e])=>({id,bridgeVertices:e.roads.children[2]?.geometry.attributes.position.count||0,roadCount:e.data.roads.filter(r=>r.bridge).length}))};});
 const fallback=await roads();assert.equal(fallback.suppressed,0);assert.ok(fallback.tiles.some(t=>t.bridgeVertices>0));await capture(failed,'failed-download-road-fallback-1440x1000');await failed.locator('#stream-retry').click();await settle(failed);state=await current(failed);assert.deepEqual(state.bridges.errors,[]);assert.equal(state.bridges.spans,12260);const restored=await roads();assert.ok(restored.suppressed>=12260);assert.ok(restored.tiles.some(t=>t.bridgeVertices<(fallback.tiles.find(f=>f.id===t.id)?.bridgeVertices||0)));await capture(failed,'retry-raised-decks-restored-1440x1000');report.retry={fallback,restored,bridges:state.bridges};await failed.close();
 assert.deepEqual(report.errors,[]);report.result='passed';report.checks=['four real city decks: source card, positive clearance and cover tags','near rails and high aerial rail LOD','layer visibility and picking exclusion','named bridge search in English and Traditional Chinese','regional replan cache remains at most 24 tiles','390/320 mobile search and no horizontal overflow','failed inventory retains old bridge road geometry; actual Retry loads decks and suppresses duplicates'];
}catch(error){report.result='failed';report.failure=error.stack;throw error;}finally{await writeFile(output+'verification.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({result:report.result,checks:report.checks,failure:report.failure,observations:report.observations.length,errors:report.errors},null,2));await browser.close();}
