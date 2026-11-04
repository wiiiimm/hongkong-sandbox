/** Full indexed-mesh terrain regression check for already-installed neighbours. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {dirname,resolve,relative} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {gunzipSync} from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {levels} from '../assembly-support-review/triangles.mjs';
import {nativeNeighbourAccepted} from './native-neighbour-policy.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const doc=process.argv[2];
assert(doc,'Usage: node check-native-neighbours.mjs <document-folder/>');
const hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
const read=p=>{const raw=readFileSync(resolve(root,p));hashes[p]=hash(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};

const manifest=read('3d-viewer/city/data/manifest.json'),base=read('3d-viewer/city/data/terrain.json');
base.patches=[];
const installed=[];
for(const row of manifest.terrainPatches||[])installed.push({entry:row,data:read('3d-viewer/'+row.url)});
base.patches=installed.map(row=>row.data);
const before=makeTerrainSampler(base),variant=structuredClone(base),inputs=read(doc+'neighbour-inputs.json.gz'),replaced=new Set(inputs.patches.flatMap(row=>row.replaces?[row.replaces.url]:[]));
variant.patches=installed.filter(row=>!replaced.has(row.entry.url)).map(row=>structuredClone(row.data));
for(const row of inputs.patches){
 const raw=readFileSync(resolve(root,row.path));
 assert.equal(hash(raw),row.sha256);
 hashes[row.path]=row.sha256;
 variant.patches.push(JSON.parse(raw));
}
const after=makeTerrainSampler(variant),standard=read(doc+'neighbour-checks.json');
const blocked=new Set(standard.rows.filter(row=>row.existingNative&&row.reasons.length).map(row=>row.uid));
for(const row of inputs.patches)for(const uid of row.replaces?.retainedUids||[])blocked.add(uid);
const buildings=new Map(inputs.rows.map(row=>[row.building.uid,row.building])),entries=new Map(),available=new Map();
for(const url of manifest.officialModelCatalogues){
 const path='3d-viewer/'+url,cat=read(path),folder=dirname(path);
 for(const entry of prepareModelCatalogue(cat,pathToFileURL(resolve(root,path)).href)){
  available.set(entry.uid,{entry,path:resolve(root,folder,entry.asset)});
 }
}
const dependencies=new Set();
for(const uid of blocked)for(const dependency of available.get(uid)?.entry.supportDependencies||[]){
 const support=available.get(dependency.uid)?.entry;
 assert(dependency.state==='installed'&&support&&support.buildingCSUID===dependency.csuid,'Pinned installed native dependency unavailable');
 dependencies.add(dependency.uid);
}
for(const [uid,value] of available){
 const sameParent=[...blocked].some(other=>buildings.get(other)?.parent&&buildings.get(other).parent===buildings.get(uid)?.parent);
 if(blocked.has(uid)||sameParent||dependencies.has(uid))entries.set(uid,value);
}
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},geometry=new Map();
for(const [uid,{entry,path}] of entries){
 const raw=readFileSync(path),assetPath=relative(root,path);
 hashes[assetPath]=hash(raw);assert.equal(hashes[assetPath],entry.sha256);
 const model=await loadOfficialModel(entry,buildings.get(uid),lighting,{fetcher:async()=>new Response(raw)}),g=model.record.modelGeometry,triangles=[];
 for(let i=0;i<g.index.length;i+=3){
  const ids=[g.index[i],g.index[i+1],g.index[i+2]],p=ids.map(v=>[g.position[v*3],g.position[v*3+1],g.position[v*3+2]]);
  const det=(p[1][0]-p[0][0])*(p[2][2]-p[0][2])-(p[1][2]-p[0][2])*(p[2][0]-p[0][0]);
  if(Math.abs(det)>1e-9)triangles.push({ax:p[0][0],az:p[0][2],ay:p[0][1],bx:p[1][0],bz:p[1][2],by:p[1][1],cx:p[2][0],cz:p[2][2],cy:p[2][1],det,minX:Math.min(...p.map(v=>v[0])),maxX:Math.max(...p.map(v=>v[0])),minZ:Math.min(...p.map(v=>v[2])),maxZ:Math.max(...p.map(v=>v[2]))});
 }
 geometry.set(uid,{entry,position:g.position,index:g.index,triangles});disposeOfficialModel(model);
}
// Diagnostic only: compare every actually rendered terrain triangle intersecting
// the complete installed source bounding box. Exact Float32 equality grants no publication.
function drawnTriangles(data,bounds){
 const terrain=makeTerrain(data),out=[];terrain.updateMatrixWorld(true);
 terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.equals(new THREE.Matrix4()));
  const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
  for(let i=0;i<n;i+=3){const ps=[0,1,2].map(k=>{const v=idx?idx.getX(i+k):i+k;return[p.getX(v),p.getY(v),p.getZ(v)];});
   if(Math.max(...ps.map(v=>v[0]))<bounds[0][0]-1||Math.min(...ps.map(v=>v[0]))>bounds[1][0]+1||Math.max(...ps.map(v=>v[2]))<bounds[0][2]-1||Math.min(...ps.map(v=>v[2]))>bounds[1][2]+1)continue;
   out.push(JSON.stringify(ps.sort((a,b)=>a[0]-b[0]||a[1]-b[1]||a[2]-b[2])));
  }
 });
 terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});return out.sort();
}
const proof=read(doc+'retained-basic-support-proof.json');
assert(proof.uid==='landsd/34255:0'&&proof.supportUid==='landsd/264935:0'&&proof.basicSourceUnchanged===true);
assert(inputs.candidateIds.length===1&&['landsd/31718:0','landsd/34249:0'].includes(inputs.candidateIds[0]));
for(const [path,sha] of Object.entries(proof.inputHashes)){const raw=readFileSync(resolve(root,path));assert.equal(hash(raw),sha);hashes[path]=sha;}
const basic=buildings.get(proof.supportUid);assert(basic&&basic.buildingCSUID===proof.supportCSUID&&!available.has(proof.supportUid));
const basicGeometry=createBuildingGeometry(basic),basicPosition=basicGeometry.attributes.position,basicTriangles=[];
for(let i=0;i<basicPosition.count;i+=3){const ps=[0,1,2].map(k=>[basicPosition.getX(i+k),basicPosition.getY(i+k),basicPosition.getZ(i+k)]),[a,b,c]=ps;
 const det=(b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2]);if(Math.abs(det)<=1e-9)continue;
 basicTriangles.push({ax:a[0],ay:a[1],az:a[2],bx:b[0],by:b[1],bz:b[2],cx:c[0],cy:c[1],cz:c[2],det,minX:Math.min(...ps.map(p=>p[0])),maxX:Math.max(...ps.map(p=>p[0])),minZ:Math.min(...ps.map(p=>p[2])),maxZ:Math.max(...ps.map(p=>p[2]))});
}
basicGeometry.dispose();
for(const path of ['source-scripts/city/government-import/check-on-ning-retained-basic-neighbours.mjs','3d-viewer/city/building-geometry.js','source-scripts/city/government-import/native-neighbour-policy.mjs'])hashes[path]=hash(readFileSync(resolve(root,path)));
const rows=[],resolved=[];
for(const uid of blocked){
 const g=geometry.get(uid);
 if(!g){rows.push({uid,passed:false,reason:'installed-native-asset-unavailable'});continue;}
 const oldGap=[],newGap=[];
 for(let i=0;i<g.position.length;i+=3){const x=g.position[i],y=g.position[i+1],z=g.position[i+2];oldGap.push(y-before.height(x,z));newGap.push(y-after.height(x,z));}
 let oldBuried=0,newBuried=0,oldUpward=0,newUpward=0,newlyBuried=0,newlyUpward=0;
 for(let i=0;i<g.index.length;i+=3){
  const ids=[g.index[i],g.index[i+1],g.index[i+2]],a=new THREE.Vector3().fromArray(g.position,ids[0]*3),b=new THREE.Vector3().fromArray(g.position,ids[1]*3),c=new THREE.Vector3().fromArray(g.position,ids[2]*3),up=new THREE.Triangle(a,b,c).getNormal(new THREE.Vector3()).y>.15;
  const was=ids.every(v=>oldGap[v]<-.25),now=ids.every(v=>newGap[v]<-.25);
  oldBuried+=was;newBuried+=now;oldUpward+=was&&up;newUpward+=now&&up;newlyBuried+=now&&!was;newlyUpward+=now&&!was&&up;
 }
 const low=g.entry.worldBounds[0][1],rim=[];
 for(let i=0;i<g.position.length;i+=3)if(g.position[i+1]<=low+.35)rim.push([g.position[i],g.position[i+1],g.position[i+2]]);
 const pinned=new Set((g.entry.supportDependencies||[]).filter(d=>d.state==='installed').map(d=>d.uid));
 const supports=[...geometry.entries()].filter(([other,h])=>other!==uid&&
  (buildings.get(uid)?.parent&&buildings.get(other)?.parent===buildings.get(uid).parent||pinned.has(other))&&h.entry.worldBounds[0][1]<low);
 let supported=0;
 for(const [x,y,z] of rim)if(supports.some(([,h])=>{const ys=levels(h,x,z);return ys.length>0&&y<=ys.at(-1)+.5;}))supported++;
 let basicSupported=0;
 if(uid===proof.uid){assert.equal(g.entry.sha256,proof.towerSHA256);for(const [x,y,z] of rim){const ys=levels({triangles:basicTriangles},x,z);if(ys.length&&Math.abs(y-ys.at(-1))<=.5)basicSupported++;}}
 const terrainRelevant=newGap.reduce((value,item)=>Math.min(value,item),Infinity)<=2,nativeSupportFraction=rim.length?supported/rim.length:0;
 const exactDrawnTerrainDiagnostic=uid===proof.uid?{before:drawnTriangles(base,g.entry.worldBounds),after:drawnTriangles(variant,g.entry.worldBounds)}:null;
 const unchangedTerrain=exactDrawnTerrainDiagnostic&&exactDrawnTerrainDiagnostic.before.length>0&&JSON.stringify(exactDrawnTerrainDiagnostic.before)===JSON.stringify(exactDrawnTerrainDiagnostic.after);
 const basicSupportFraction=unchangedTerrain&&rim.length?basicSupported/rim.length:0;
 const supportFraction=Math.max(nativeSupportFraction,basicSupportFraction);
 const passed=nativeNeighbourAccepted({newlyBuried,newlyUpward,terrainRelevant,supportFraction});
 const row={uid,passed,retainedBasicSupport:uid===proof.uid?{uid:proof.supportUid,csuid:proof.supportCSUID,samples:rim.length,strictContacts:basicSupported,unchangedDrawnTerrain:unchangedTerrain,beforeTriangles:exactDrawnTerrainDiagnostic.before.length,afterTriangles:exactDrawnTerrainDiagnostic.after.length,beforeSHA256:hash(Buffer.from(JSON.stringify(exactDrawnTerrainDiagnostic.before))),afterSHA256:hash(Buffer.from(JSON.stringify(exactDrawnTerrainDiagnostic.after))),legacyProofSHA256:hash(readFileSync(resolve(root,doc+'retained-basic-support-proof.json')))}:null,vertices:g.position.length/3,triangles:g.index.length/3,terrain:{minimumGapBefore:oldGap.reduce((value,item)=>Math.min(value,item),Infinity),minimumGapAfter:newGap.reduce((value,item)=>Math.min(value,item),Infinity),maximumBurialIncrease:oldGap.reduce((value,item,i)=>Math.max(value,item-newGap[i]),-Infinity),whollyBuriedBefore:oldBuried,whollyBuriedAfter:newBuried,upwardWhollyBuriedBefore:oldUpward,upwardWhollyBuriedAfter:newUpward,newlyWhollyBuried:newlyBuried,newlyUpwardWhollyBuried:newlyUpward},support:{sameParentNativeUids:supports.filter(([u])=>buildings.get(uid)?.parent&&buildings.get(u)?.parent===buildings.get(uid).parent).map(([u])=>u),pinnedNativeUids:supports.filter(([u])=>pinned.has(u)).map(([u])=>u),lowRimSamples:rim.length,supportedLowRim:supported,nativeSupportFraction,basicSupportFraction,supportFraction},policy:'All runtime-loaded indexed vertices and triangles use the exact before/after viewer terrain samplers. No newly wholly buried triangle is allowed. A terrain-distant component requires >=50% native low-rim support. For exact previously approved Block 1 only, its unchanged rendered basic podium is rebound through current Neon/source/installed/browser receipts and exact unchanged rendered terrain; source clearance remains 0.5 m.'};
 rows.push(row);if(passed)resolved.push(uid);
}
const result={rows,resolved:resolved.sort(),blocked:[...blocked].sort(),inputHashes:hashes,aiCalls:0,modelGeometryChanges:0,publication:false};
writeFileSync(resolve(root,doc+'native-neighbour-checks.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({blocked:blocked.size,resolved:resolved.length,rows:rows.map(r=>({uid:r.uid,passed:r.passed,newlyBuried:r.terrain?.newlyWhollyBuried,support:r.support?.supportFraction}))}));
