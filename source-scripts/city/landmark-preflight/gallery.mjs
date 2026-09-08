/** Mechanical normal-scene gallery. Reuses the existing staged review routes and
 * navigation API; no terrain/model edits, no automatic architectural acceptance.
 * Run only after final source snapshot stabilises. */
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const require=createRequire(new URL('../../../3d-viewer/city/package.json',import.meta.url)),{chromium}=require('playwright');
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const summary=await read('docs/astra-city/landmark-preflight/report.json'),pin=await read('source-scripts/city/landmark-preflight/snapshot.json');
assert.equal(summary.snapshotId,pin.id);
const base=`source-scripts/city/landmark-preflight/snapshots/${pin.id}/`;
for(const [name,info]of Object.entries(pin.files))assert.equal(createHash('sha256').update(await readFile(new URL(base+name,root))).digest('hex'),info.sha256,name);
for(const [path,digest]of Object.entries(pin.cpuValidationInputHashes))if(path.startsWith('3d-viewer/'))assert.equal(createHash('sha256').update(await readFile(new URL(path,root))).digest('hex'),digest,'Live reviewed terrain/source changed: '+path);
if(pin.files['app.js'])assert.equal(createHash('sha256').update(await readFile(new URL('3d-viewer/city/app.js',root))).digest('hex'),pin.files['app.js'].sha256,'Runtime changed');
const catalogue=await read(base+'catalogue.json'),models=new Map(catalogue.models.map(m=>[m.uid,m]));
const published=await read(base+'published-models.json'),contextModels=new Map([...published.models,...catalogue.models].map(m=>[m.uid,m]));
const manifest=await read('3d-viewer/city/data/manifest.json'),buildings=new Map();
for(const tile of manifest.tiles)for(const b of(await read('3d-viewer/'+tile.url)).buildings)if(models.has(b.uid))buildings.set(b.uid,b);
const groups=summary.landmarks.filter(g=>g.members.some(uid=>models.has(uid)));
const requested=process.env.GALLERY_IDS?.split(',');const selected=groups.filter(g=>!requested||requested.includes(g.id));
const out=new URL(`docs/astra-city/landmark-preflight/gallery/${pin.id}/`,root);await mkdir(out,{recursive:true});
const report={snapshotId:pin.id,kind:'automated-evidence-unreviewed',started:new Date().toISOString(),landmarks:[],errors:[],limits:['Normal scene screenshots are evidence awaiting human/agent review, not acceptance.','Models are injected from the pinned candidate snapshot; live assets and terrain remain unchanged.','Only selected source members are framed; identity and full component membership remain unresolved where flagged.','No collision/walking/mobile/GPU performance acceptance is performed by this gallery.']};
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1280,height:900}});
const catalogueURL='city/data/official-models/preflight-gallery-'+pin.id+'/catalogue.json';
const union=entries=>[[0,1,2].map(i=>Math.min(...entries.map(m=>m.worldBounds[0][i]))),[0,1,2].map(i=>Math.max(...entries.map(m=>m.worldBounds[1][i])))];
try{
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/city/app.js',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text())+'\nObject.defineProperty(window,"__gallery",{get:()=>({officialModels,stream,camera,controls,renderer,sampler,THREE,visitBuilding,closeSelection,controlSheet})});\n'});});
 await page.route('**/'+catalogueURL,r=>r.fulfill({json:catalogue}));
 for(const m of models.values())await page.route('**/'+catalogueURL.slice(0,catalogueURL.lastIndexOf('/')+1)+m.asset,async r=>r.fulfill({body:await readFile(new URL(base+'assets/'+m.asset,root)),contentType:'application/gzip'}));
 await page.route('**/city/data/manifest.json',async r=>{const response=await r.fetch(),data=await response.json();data.officialModelCatalogues=[...data.officialModelCatalogues,catalogueURL];await r.fulfill({response,json:data});});
 await page.goto('http://127.0.0.1:4176/city.html?district=central');await page.waitForFunction(()=>window.__city?.ready,null,{timeout:180000});await page.locator('#loading').waitFor({state:'hidden',timeout:180000});
 for(const g of selected){
  const row={id:g.id,name:g.name,identityState:g.identityState,publicationApproved:false,views:[]};report.landmarks.push(row);
  try{
   const staged=g.members.filter(uid=>models.has(uid)).map(uid=>models.get(uid)),assembly=g.members.filter(uid=>contextModels.has(uid)).map(uid=>contextModels.get(uid));
   const focus=staged.toSorted((a,b)=>(b.worldBounds[1][1]-b.worldBounds[0][1])-(a.worldBounds[1][1]-a.worldBounds[0][1]))[0],bounds=union(assembly);
   row.focusUid=focus.uid;row.stagedUIDs=staged.map(m=>m.uid);row.assemblyBounds=bounds;row.missingNativeGeometryUIDs=g.members.filter(uid=>!contextModels.has(uid));
   if(Math.max(bounds[1][0]-bounds[0][0],bounds[1][2]-bounds[0][2])>4000){row.result='held-geographic-span-over-4km';continue;}
   assert(buildings.has(focus.uid),'Source feature unavailable');await page.evaluate(b=>window.__gallery.visitBuilding(b),buildings.get(focus.uid));
   await page.waitForFunction(()=>!window.__city.state.loadingTravel&&!window.__city.state.travelling,null,{timeout:120000});await page.waitForFunction(uid=>window.__gallery.stream.detailedModels.get(uid)?.active,focus.uid,{timeout:60000});
   for(const view of ['overview','closeup']){
    const detail=await page.evaluate(({bounds,label,view,uids})=>{const r=window.__gallery;r.closeSelection();r.controlSheet.close({restoreFocus:false});const input=document.getElementById('time');input.value='15:00';input.dispatchEvent(new Event('input',{bubbles:true}));const[a,b]=bounds,c=a.map((v,i)=>(v+b[i])/2),span=Math.max(b[0]-a[0],b[2]-a[2]),height=b[1]-a[1],dist=Math.max(30,span*(view==='overview'?1.6:1.2),height*1.3),x=c[0]-dist*.7,z=c[2]-dist;let y=Math.max(b[1]+dist*.35,r.sampler.height(x,z)+15);for(let step=2;step<=10;step++){const t=step/10;y=Math.max(y,(r.sampler.height(c[0]+(x-c[0])*t,c[2]+(z-c[2])*t)+5-c[1]*(1-t))/t);}r.camera.position.set(x,y,z);r.controls.target.fromArray(c);r.controls.update();r.camera.updateMatrixWorld(true);let el=document.getElementById('gallery-label');if(!el){el=document.createElement('div');el.id='gallery-label';Object.assign(el.style,{position:'fixed',top:'78px',left:'20px',zIndex:9999,background:'#fff',color:'#183a32',padding:'10px',font:'13px monospace',maxWidth:'75vw'});document.body.append(el);}el.textContent='STAGED EVIDENCE · '+label+' · '+view+' · unreviewed';return{camera:r.camera.position.toArray(),target:r.controls.target.toArray()};},{bounds:view==='overview'?bounds:focus.worldBounds,label:g.name,view,uids:row.stagedUIDs});
    await page.waitForTimeout(650);const file=g.id+'-'+view+'.png';await page.screenshot({path:new URL(file,out).pathname});
    const loaded=await page.evaluate(uids=>({activeUIDs:uids.filter(uid=>window.__gallery.stream.detailedModels.get(uid)?.active),cache:window.__gallery.officialModels.stats}),row.stagedUIDs);
    row.views.push({file,...detail,...loaded});
   }
   row.result='captured-unreviewed';console.log(g.id,row.result);
  }catch(error){row.result='capture-failed';row.error=String(error.stack);console.log(g.id,row.result,error.message);}
  await writeFile(new URL('report.json',out),JSON.stringify(report,null,2)+'\n');
 }
}finally{report.finished=new Date().toISOString();await writeFile(new URL('report.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
await writeFile(new URL('docs/astra-city/landmark-preflight/gallery-summary.json',root),JSON.stringify(report,null,2)+'\n');
const rows=report.landmarks.map(g=>`<section><h2>${g.name.replaceAll('&','&amp;').replaceAll('<','&lt;')}</h2><p>${g.result}</p>${g.views.map(v=>`<a href="${v.file}"><img src="${v.file}" loading="lazy" width="480"></a>`).join('')}</section>`).join('');
await writeFile(new URL('index.html',out),`<!doctype html><meta charset="utf-8"><title>Unreviewed landmark evidence</title><style>body{font:16px system-ui;background:#edf0e7;color:#183a32;padding:24px}section{margin:28px 0}img{max-width:48%;height:auto;margin:4px}</style><h1>Staged landmark evidence — unreviewed</h1><p>Snapshot ${pin.id}. No publication or architecture acceptance.</p>${rows}`);
console.log(JSON.stringify({snapshotId:pin.id,captured:report.landmarks.filter(g=>g.result==='captured-unreviewed').length,failed:report.landmarks.filter(g=>g.result==='capture-failed').length}));
