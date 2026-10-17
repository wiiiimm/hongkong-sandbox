/** Diagnostic only: full original triangle clearance against current drawn terrain.
 * Does not bypass the runtime loader for acceptance and grants no identity credit.
 */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),[inputPath,outPath,geometryPath]=process.argv.slice(2);
assert(inputPath&&outPath&&geometryPath&&!existsSync(new URL(outPath,root))&&!existsSync(new URL(geometryPath,root)),'Fresh named outputs required');
const hash=raw=>createHash('sha256').update(raw).digest('hex'),inputs={};
const load=(p,gzip=false)=>{const raw=readFileSync(new URL(p,root));inputs[p]=hash(raw);return JSON.parse(gzip?gunzipSync(raw):raw);};
const original=load(inputPath,true),rows=original.rows;assert(rows.length>0&&rows.length<=20);
const manifest=load('3d-viewer/city/data/manifest.json');assert.equal(inputs['3d-viewer/city/data/manifest.json'],original.manifestSHA256);
const data=load('3d-viewer/city/data/terrain.json');
data.patches=(manifest.terrainPatches||[]).map(p=>load('3d-viewer/'+p.url));
for(const p of ['source-scripts/city/government-import/original-source-clearance-diagnostic.mjs','3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js','3d-viewer/city/native-terrain.js'])inputs[p]=hash(readFileSync(new URL(p,root)));
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);const sampler=makeTerrainSampler(data),identity=new THREE.Matrix4();
const ground=new Map(rows.map(r=>[r.uid,[]]));
terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.equals(identity));const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
 for(let i=0;i<n;i+=3){const vertices=[0,1,2].map(k=>{const j=idx?idx.getX(i+k):i+k;return[p.getX(j),p.getY(j),p.getZ(j)];});const xs=vertices.map(p=>p[0]),zs=vertices.map(p=>p[2]);
  for(const row of rows){const [lo,hi]=row.worldBounds;if(Math.max(...xs)<lo[0]-1||Math.min(...xs)>hi[0]+1||Math.max(...zs)<lo[2]-1||Math.min(...zs)>hi[2]+1)continue;ground.get(row.uid).push(...vertices.flat());}
 }
});
const results=[],geometry=[];
for(const row of rows){assert(Array.isArray(row.triangles)&&row.triangles.length);const points=row.triangles.flat(2);assert(points.every(Number.isFinite));
 const encoded=Buffer.alloc(points.length*8);points.forEach((p,i)=>encoded.writeDoubleLE(p,i*8));assert.equal(hash(encoded),row.worldTrianglesSHA256);
 const g=ground.get(row.uid),surface=nativeTerrainSurface({position:g,index:Array.from({length:g.length/3},(_,i)=>i)}),bottom=row.worldBounds[0][1];
 let checks=0,lowRimChecks=0,minSurfaceGap=Infinity,minLowGap=Infinity,maxLowGap=-Infinity,maxSamplerDelta=0,missingTerrain=0;
 const failures=[];
 const check=(x,y,z,kind)=>{checks++;const drawn=surface.height(x,z);if(drawn===null){missingTerrain++;return;}const gap=y-drawn,delta=Math.abs(sampler.height(x,z)-drawn);minSurfaceGap=Math.min(minSurfaceGap,gap);maxSamplerDelta=Math.max(maxSamplerDelta,delta);if(y<=bottom+.35){lowRimChecks++;minLowGap=Math.min(minLowGap,gap);maxLowGap=Math.max(maxLowGap,gap);}if(gap<-.5||y<=bottom+.35&&gap>1)failures.push({point:[x,y,z],gap,kind});};
 for(const t of row.triangles){for(const p of t)check(...p,'vertex');check(...[0,1,2].map(a=>t.reduce((s,p)=>s+p[a],0)/3),'centre');for(let i=0;i<3;i++){const a=t[i],b=t[(i+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(...a.map((v,k)=>v+(b[k]-v)*j/steps),'low-edge');}}
 const result={uid:row.uid,sourceSHA256:row.sourceSHA256,checks,lowRimChecks,minSurfaceGap,minLowGap,maxLowGap,maxSamplerDelta,missingTerrain,failedSamples:failures.length,groundContactPassed:!missingTerrain&&minSurfaceGap>=-.5&&minLowGap>=-.5&&maxLowGap<=1&&maxSamplerDelta<=.004,identityAccepted:false,runtimeLoaderAccepted:false,installationApproved:false};
 results.push(result);geometry.push({uid:row.uid,sourceSHA256:row.sourceSHA256,worldTrianglesSHA256:row.worldTrianglesSHA256,drawnGroundGeometry:g,failedSamples:failures});console.log(JSON.stringify(result));
}
const report={inputHashes:inputs,rows:results,publication:false,sourceGeometryChanges:0,qualification:'Full original clearance diagnostic only. Original triangle positions are checked against pinned current rendered terrain. Vertex checks repeat shared original vertices; counts are not directly comparable to indexed loader metrics. The loader and all identity/runtime/foundation/neighbour/publication gates still require a separate passing route.'};
for(const path of[outPath,geometryPath])mkdirSync(new URL('.',new URL(path,root)),{recursive:true});
writeFileSync(new URL(outPath,root),JSON.stringify(report,null,2)+'\n');writeFileSync(new URL(geometryPath,root),gzipSync(JSON.stringify({inputHashes:inputs,rows:geometry})));
terrain.traverse(o=>{o.geometry?.dispose();for(const m of[].concat(o.material||[]))m.dispose();});
