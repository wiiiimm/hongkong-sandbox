/** Read-only staged model validation. No publication or source elevation changes. Node 24+. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,realpathSync} from 'node:fs';
import {resolve,dirname,relative,isAbsolute} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
const args=process.argv.slice(2),option=(key,fallback)=>args.includes(key)?args[args.indexOf(key)+1]:fallback;
const root=realpathSync(resolve(option('--root',fileURLToPath(new URL('../../../',import.meta.url)))));
const dbPath=resolve(option('--db',root+'/source-scripts/city/building-batch/local/buildings.sqlite'));
const folder=realpathSync(resolve(option('--candidates',root+'/source-scripts/city/building-batch/local/candidates')));
const output=resolve(option('--out',folder+'/validation.json'));
const safe=(base,p)=>{const path=realpathSync(resolve(base,p)),r=relative(realpathSync(base),path);assert(!r.startsWith('..')&&!isAbsolute(r),'Path escapes input root');return path;};
const hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
const read=(base,p)=>{const path=safe(base,p),bytes=readFileSync(path);hashes[path.startsWith(root+'/')?relative(root,path):relative(folder,path)]=hash(bytes);return JSON.parse(bytes);};
const imports=await Promise.all(['3d-viewer/vendor/three.module.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/geo.js','3d-viewer/city/world.js'].map(p=>import(pathToFileURL(resolve(root,p)))));
const [THREE,{prepareModelCatalogue,loadOfficialModel,disposeOfficialModel},{BuildingIndex,makeTerrainSampler,inPolygon},{makeTerrain}]=imports;
const db=new DatabaseSync(dbPath,{readOnly:true});db.exec('PRAGMA busy_timeout=30000');
const lookup=db.prepare('SELECT * FROM buildings WHERE uid=? AND active=1');
const tiles=new Map(),inputHash=db.prepare('SELECT sha256 FROM inputs WHERE path=?');
const getBuilding=uid=>{
 const row=lookup.get(uid);assert(row,'Active building missing');
 if(!tiles.has(row.input_path)){const path=safe(root+'/3d-viewer',row.input_path),raw=readFileSync(path);assert.equal(hash(raw),inputHash.get(row.input_path)?.sha256,'Live tile changed since inventory');hashes['3d-viewer/'+row.input_path]=hash(raw);tiles.set(row.input_path,new Map(JSON.parse(raw).buildings.map(b=>[b.uid,b])));}
 const building=tiles.get(row.input_path).get(uid);assert(building,'Building missing from current tile');assert.deepEqual(building.rings,JSON.parse(row.rings_json));return building;
};
const index=read(folder,'catalogue-index.json'),seen=new Set(),entries=[];
for(const name of index.catalogues){
 const cat=read(folder,name);for(const e of prepareModelCatalogue(cat,'http://staged.local/'+name)){assert(!seen.has(e.uid),'Duplicate model across catalogues');seen.add(e.uid);entries.push(e);}
}
assert.equal(entries.length,index.models);
const manifest=read(root,'3d-viewer/city/data/manifest.json'),terrainData=read(root,'3d-viewer/city/data/terrain.json');
terrainData.patches=manifest.terrainPatches.map(p=>read(root,'3d-viewer/'+p.url));
const sampler=makeTerrainSampler(terrainData),terrain=makeTerrain(terrainData);terrain.updateMatrixWorld(true);
const lighting={night:{value:1},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
const results=[],started=performance.now();let terrainRays=0,loaderAccepted=0;
try{
 for(const entry of entries){
  let model;const began=performance.now();
  try{
   const building=getBuilding(entry.uid),asset=readFileSync(safe(folder,entry.asset));
   model=await loadOfficialModel(entry,building,lighting,{fetcher:async()=>new Response(asset)});
   loaderAccepted++;
   assert(model.meshes.every(m=>m.userData.officialBuildingUid===entry.uid));
   // A real source triangle, not the footprint's artificial flat roof.
   const {position,index:indices}=model.record.modelGeometry;let roof=null;
   for(let i=0;i<indices.length;i+=3){
    const a=indices[i]*3,b=indices[i+1]*3,c=indices[i+2]*3;
    const nx=(position[b+1]-position[a+1])*(position[c+2]-position[a+2])-(position[b+2]-position[a+2])*(position[c+1]-position[a+1]);
    const ny=(position[b+2]-position[a+2])*(position[c]-position[a])-(position[b]-position[a])*(position[c+2]-position[a+2]);
    const nz=(position[b]-position[a])*(position[c+1]-position[a+1])-(position[b+1]-position[a+1])*(position[c]-position[a]);
    if(ny<=Math.hypot(nx,ny,nz)*.2)continue;
    const point=[0,1,2].map(axis=>(position[a+axis]+position[b+axis]+position[c+axis])/3);
    if(!roof||point[1]>roof[1])roof=point;
   }
   assert(roof,'No upward source surface');
   const ray=new THREE.Raycaster(new THREE.Vector3(roof[0],entry.worldBounds[1][1]+10,roof[2]),new THREE.Vector3(0,-1,0));
   const hits=ray.intersectObjects(model.meshes);assert(hits.length,'Source picking missed');assert.equal(hits[0].object.userData.officialBuildingUid,entry.uid);
   const collision=new BuildingIndex([model.record]);assert.equal(collision.collision(roof[0],roof[2],roof[1]-.05,roof[1]+.05,.1)?.uid,entry.uid,'Source surface collision missed');
   assert.equal(collision.collision(roof[0],roof[2],entry.worldBounds[1][1]+1,entry.worldBounds[1][1]+2,.1),null);
   const points=[];
   for(const ring of building.rings)for(let i=0;i<ring.length;i++){points.push(ring[i]);const b=ring[(i+1)%ring.length];points.push([(ring[i][0]+b[0])/2,(ring[i][1]+b[1])/2]);}
   const xs=building.rings[0].map(p=>p[0]),zs=building.rings[0].map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
   for(let x=0;x<5;x++)for(let z=0;z<5;z++){const p=[minX+(maxX-minX)*(x+.5)/5,minZ+(maxZ-minZ)*(z+.5)/5];if(inPolygon(...p,building.rings))points.push(p);}
   const ground=points.map(p=>sampler.height(...p));assert(ground.every(Number.isFinite));
   const roofGround=sampler.height(roof[0],roof[2]),minGround=Math.min(...ground),maxGround=Math.max(...ground);
   // Verify the sampler against the drawn mesh at one real roof position per candidate.
   ray.set(new THREE.Vector3(roof[0],3000,roof[2]),new THREE.Vector3(0,-1,0));
   const terrainHits=ray.intersectObject(terrain,true);assert.equal(terrainHits.length,1,'Expected one rendered terrain surface');assert(Math.abs(terrainHits[0].point.y-roofGround)<.004,'Sampler differs from rendered terrain');terrainRays++;
   const concerns=[];
   if(roofGround>roof[1]+.25)concerns.push('sampled-highest-roof-below-terrain');
   if(maxGround>entry.worldBounds[0][1]+2)concerns.push('sampled-terrain-above-model-bottom');
   if(minGround<entry.worldBounds[0][1]-2)concerns.push('sampled-ground-gap-below-model-bottom');
   results.push({uid:entry.uid,modelId:entry.modelId,outcome:'runtime-accepted-placement-unreviewed',triangles:entry.triangles,compressedBytes:entry.bytes,residentBudgetBytes:model.budget.residentBytes,
    terrain:{sampleCount:points.length,minGround,maxGround,roofGround,roof,sourceYBounds:[entry.worldBounds[0][1],entry.worldBounds[1][1]],resolutions:[...new Set(points.map(p=>sampler.resolutionAt(...p)))]},concerns,seconds:(performance.now()-began)/1000});
  }catch(error){results.push({uid:entry.uid,outcome:'validation-exception',loaderAccepted:Boolean(model?.record),error:String(error.message)});}
  finally{disposeOfficialModel(model);}
  if(results.length%500===0)console.error('Validated '+results.length+'/'+entries.length);
 }
}finally{db.close();terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});}
const exceptions=results.filter(r=>r.outcome==='validation-exception'),concerns={};for(const r of results)for(const c of r.concerns||[])concerns[c]=(concerns[c]||0)+1;
const report={schemaVersion:1,staged:true,published:false,models:entries.length,loaderAccepted,checksPassed:results.length-exceptions.length,exceptions:exceptions.length,terrainRays,seconds:(performance.now()-started)/1000,
 peakRSSBytes:process.resourceUsage().maxRSS*1024,compressedBytes:entries.reduce((n,e)=>n+e.bytes,0),concerns,hashes,results,
 limits:['CPU loader, source-surface picking/collision and sampled terrain screening; no GPU/browser performance or architecture acceptance.',
 'Terrain flags are diagnostics, not automatic rejection: piers, overhangs, slopes and elevated infrastructure need contextual review.',
 'Sampling is not an exhaustive foundation or roof test. Native source geometry stays unchanged. No viewer publication.']};
writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,hashes:undefined,results:undefined}));
if(exceptions.length)process.exitCode=1;
