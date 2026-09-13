/** Read-only isolated foundation review using the existing staged-plan routing.
 * Unrelated building groups hidden; native model groups cloned unchanged. Terrain remains visible.
 * Diagnostic screenshots do not demonstrate ordinary scene visibility or interaction performance.
 */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
const require=createRequire(new URL('../../../3d-viewer/city/package.json',import.meta.url)),{chromium}=require('playwright');
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const config=await read(process.env.DIAG_CONFIG||'source-scripts/city/architecture-batch/browser-config.json'),plan=await read(config.plan),context=await read('source-scripts/city/architecture-batch/placement-context.json');
const wanted=process.env.DIAG_UIDS?process.env.DIAG_UIDS.split(','):context.browserFoundationChecks;
const models=(await Promise.all(plan.areas.map(a=>read(a.catalogue)))).flatMap(c=>c.models),manifest=await read('3d-viewer/city/data/manifest.json'),buildings=new Map();
for(const t of manifest.tiles)for(const b of (await read('3d-viewer/'+t.url)).buildings)if(wanted.includes(b.uid))buildings.set(b.uid,b);
const out=new URL(process.env.DIAG_OUT||'docs/astra-city/architecture-batch/diagnostic-browser/',root);await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']}),page=await browser.newPage({viewport:{width:1280,height:900}}),report={diagnostic:true,views:[],errors:[],limits:['Unrelated buildings hidden only in this diagnostic browser; terrain, model geometry and native heights are unchanged.','Two opposite diagonal foundation views; not exhaustive facade inspection or mobile validation.']};
try{
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__diagnostic",{get:()=>({scene,officialModels,stream,camera,controls,renderer,sampler,THREE,terrain,visitBuilding,closeSelection,controlSheet})});\n'});});
 for(const a of plan.areas){const cat=await read(a.catalogue),base=new URL(a.catalogue,root);await page.route('**/'+a.destination,r=>r.fulfill({json:cat}));for(const m of cat.models)await page.route('**/'+a.destination.slice(0,a.destination.lastIndexOf('/')+1)+m.asset,async r=>r.fulfill({body:await readFile(new URL(m.asset,base)),contentType:'application/gzip'}));}
 for(const r of config.terrainReplacements||[])await page.route('**/'+r.url,async route=>route.fulfill({body:await readFile(new URL(r.path,root)),contentType:'application/json'}));
 await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),m=await response.json();m.officialModelCatalogues=[...new Set([...m.officialModelCatalogues,...plan.areas.map(a=>a.destination)])];await r.fulfill({response,json:m});});
 await page.goto('http://127.0.0.1:4176/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});
 for(const uid of wanted){
  const m=models.find(m=>m.uid===uid),b=buildings.get(uid);if(!m||!b)throw Error('Missing candidate '+uid);
  await page.evaluate(b=>window.__diagnostic.visitBuilding(b),b);await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});await page.waitForFunction(uid=>window.__diagnostic.stream.detailedModels.get(uid)?.active,uid,{timeout:120000});await page.waitForFunction(()=>window.__city.state.stream.pending===0&&window.__diagnostic.officialModels.stats.pending===0,null,{timeout:120000});
  const supports=(context.rows.find(r=>r.uid===uid)?.nearbyParts||[]).filter(n=>n.targetCoverageFraction>.1).map(n=>n.uid);
  for(const sign of [1,-1]){
   const detail=await page.evaluate(({uid,bounds,supports,sign})=>{const r=window.__diagnostic;if(window.__diagGroup)window.__diagGroup.removeFromParent();const group=new r.THREE.Group();window.__diagGroup=group;r.scene.add(group);const included=[];for(const id of [uid,...supports]){const d=r.stream.detailedModels.get(id);if(d?.active){d.group.updateMatrixWorld(true);const clone=d.group.clone(true);clone.applyMatrix4(d.group.parent.matrixWorld);clone.visible=true;group.add(clone);included.push(id);}}r.stream.buildings.visible=false;r.closeSelection();r.controlSheet.close({restoreFocus:false});const input=document.getElementById('time');input.value='15:00';input.dispatchEvent(new Event('input',{bubbles:true}));const [a,b]=bounds,c=[(a[0]+b[0])/2,(a[2]+b[2])/2],span=Math.max(b[0]-a[0],b[2]-a[2]),height=b[1]-a[1],dist=Math.max(23,span*1.3),targetY=a[1]+Math.min(4,height*.3);r.camera.position.set(c[0]+sign*dist*.8,targetY+Math.max(8,height*.18),c[1]+sign*dist);r.controls.target.set(c[0],targetY,c[1]);r.controls.update();r.camera.updateMatrixWorld(true);let label=document.getElementById('diagnostic-label');if(!label){label=document.createElement('div');label.id='diagnostic-label';Object.assign(label.style,{position:'fixed',top:'78px',left:'22px',zIndex:9999,background:'#fff',color:'#183a32',padding:'12px',font:'13px monospace'});document.body.append(label);}label.textContent='DIAGNOSTIC · '+uid+' · unrelated buildings hidden · native geometry + terrain';return{included,missingSupports:supports.filter(s=>!included.includes(s)),camera:r.camera.position.toArray(),target:r.controls.target.toArray(),groundAtCentre:r.sampler.height(...c)};},{uid,bounds:m.worldBounds,supports,sign});
   await page.waitForTimeout(500);const file=uid.replace(/\W/g,'-')+(sign===1?'-se':'-nw')+'.png';await page.screenshot({path:new URL(file,out).pathname});report.views.push({uid,file,...detail});
  }
  console.log(uid,'diagnostic captured');
 }
}finally{await writeFile(new URL('report.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
