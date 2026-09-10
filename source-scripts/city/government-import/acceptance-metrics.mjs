/** Direct-original import checks. No shape-benefit comparison, geometry edits or AI. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {MODEL_PROFILES} from '../../../3d-viewer/city/official-models.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root))),hash=b=>createHash('sha256').update(b).digest('hex');
const batch='government-200-20260911',doc=`docs/astra-city/government-import/${batch}/`,out=new URL(doc+'acceptance/',root);mkdirSync(out,{recursive:true});
const selected=JSON.parse(gunzipSync(readFileSync(new URL(doc+'selection.json.gz',root)))),previous=JSON.parse(gunzipSync(readFileSync(new URL(doc+'results.json.gz',root))));
const ids=new Set(previous.rows.filter(r=>r.state==='runtime-validated-awaiting-acceptance').map(r=>r.uid));
const rows=selected.rows.filter(r=>ids.has(r.uid));assert.equal(rows.length,61);
const inputs={},load=p=>{const raw=readFileSync(new URL(p,root));inputs[p]=hash(raw);return JSON.parse(raw);};
const manifest=load('3d-viewer/city/data/manifest.json'),data=load('3d-viewer/city/data/terrain.json');
data.patches=(manifest.terrainPatches||[]).map(p=>load('3d-viewer/'+p.url));
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);const sampler=makeTerrainSampler(data);
const grounds=new Map(rows.map(r=>[r.uid,[]])),identity=new THREE.Matrix4();
// Keep only actual drawn terrain triangles intersecting this bounded model group.
terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.equals(identity),'Unexpected drawn terrain transform');const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
 for(let i=0;i<n;i+=3){const a=idx?idx.getX(i):i,b=idx?idx.getX(i+1):i+1,c=idx?idx.getX(i+2):i+2,x=[p.getX(a),p.getX(b),p.getX(c)],z=[p.getZ(a),p.getZ(b),p.getZ(c)];const x0=Math.min(...x),x1=Math.max(...x),z0=Math.min(...z),z1=Math.max(...z);
  for(const r of rows){const [lo,hi]=r.candidate.entry.worldBounds;if(x1<lo[0]-1||x0>hi[0]+1||z1<lo[2]-1||z0>hi[2]+1)continue;grounds.get(r.uid).push(x[0],p.getY(a),z[0],x[1],p.getY(b),z[1],x[2],p.getY(c),z[2]);}
 }
});
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},results=[];
for(const r of rows){let model;
 try{const e=r.candidate.entry,raw=readFileSync(new URL(`source-scripts/city/government-import/local/${batch}/candidates/${e.asset}`,root));assert.equal(hash(raw),e.sha256);const source=load('3d-viewer/'+r.source.tile).buildings.find(b=>b.uid===r.uid);assert.deepEqual(source,r.source.building);
  model=await loadOfficialModel({...e,assetURL:'https://validation.invalid/model.glb.gz'},source,lighting,{fetcher:async()=>new Response(raw)});
  const g=grounds.get(r.uid),surface=nativeTerrainSurface({position:g,index:Array.from({length:g.length/3},(_,i)=>i)}),position=model.record.modelGeometry.position,index=model.record.modelGeometry.index;
  const bottom=e.worldBounds[0][1];let count=0,lowCount=0,minGap=Infinity,maxLowGap=-Infinity,minLowGap=Infinity,maxSamplerDelta=0,missing=0;
  const check=(x,y,z)=>{const drawn=surface.height(x,z);count++;if(drawn===null){missing++;return;}const gap=y-drawn;minGap=Math.min(minGap,gap);maxSamplerDelta=Math.max(maxSamplerDelta,Math.abs(sampler.height(x,z)-drawn));if(y<=bottom+.35){lowCount++;minLowGap=Math.min(minLowGap,gap);maxLowGap=Math.max(maxLowGap,gap);}};
  for(let i=0;i<position.length;i+=3)check(position[i],position[i+1],position[i+2]);
  // All triangle centres plus low-rim edges every <=1 m, without changing source geometry.
  for(let i=0;i<index.length;i+=3){const vertices=[0,1,2].map(k=>Array.from(position.slice(index[i+k]*3,index[i+k]*3+3)));check(...[0,1,2].map(k=>vertices.reduce((s,p)=>s+p[k],0)/3));
   for(let edge=0;edge<3;edge++){const a=vertices[edge],b=vertices[(edge+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(...a.map((v,k)=>v+(b[k]-v)*j/steps));}
  }
  results.push({uid:r.uid,sourceSHA256:e.sha256,checks:count,lowRimChecks:lowCount,minSurfaceGap:minGap,minLowGap,maxLowGap,maxSamplerDelta,missingTerrain:missing,terrainTriangles:surface.triangles,budget:model.budget,identity:{overlap:e.overlapOfSmallerFootprint,centroidDistance:e.footprintCentroidDistanceMetres},sourcePreserved:true});
 }catch(error){results.push({uid:r.uid,error:String(error.message)});}finally{disposeOfficialModel(model);}
}
const report={policy:'original-government-import-v1',inputHashes:inputs,profiles:MODEL_PROFILES,rows:results,aiCalls:0,geometryChanges:0,architectureReconstruction:false};
writeFileSync(new URL('metrics.json',out),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({models:results.length,errors:results.filter(r=>r.error).length,groundContact:results.filter(r=>!r.error&&!r.missingTerrain&&r.minSurfaceGap>=-.5&&r.minLowGap>=-.5&&r.maxLowGap<=1&&r.maxSamplerDelta<=.004).length}));
terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});
