import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
import {classifyVerticalWallCrossings} from './vertical-wall-ground-crossing.mjs';
const root=new URL('../../../',import.meta.url),[modelPath,terrainPath,clearancePath,out]=process.argv.slice(2),hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={};
assert(out&&!existsSync(new URL(out,root)));
function read(p,gzip=false){const b=readFileSync(new URL(p,root));inputHashes[p]=hash(b);return JSON.parse(gzip?gunzipSync(b):b);}
const models=read(modelPath,true),terrains=read(terrainPath,true),clearance=read(clearancePath),rows=[];
for(const model of models.rows){const terrain=terrains.rows.find(r=>r.uid===model.uid),prior=clearance.rows.find(r=>r.uid===model.uid);assert(terrain&&prior);assert.equal(prior.sourceSHA256,model.sourceSHA256);assert.equal(prior.worldTrianglesSHA256,model.worldTrianglesSHA256);
 const encoded=Buffer.alloc(model.triangles.length*9*8);model.triangles.flat(2).forEach((v,i)=>encoded.writeDoubleLE(v,i*8));assert.equal(hash(encoded),model.worldTrianglesSHA256);
 const p=terrain.terrainTriangles.flat(2),surface=nativeTerrainSurface({position:p,index:Array.from({length:p.length/3},(_,i)=>i)});
 const diagnostic=classifyVerticalWallCrossings(model.triangles,prior.failedSamples,(x,z)=>surface.height(x,z));
 rows.push({uid:model.uid,sourceSHA256:model.sourceSHA256,worldTrianglesSHA256:model.worldTrianglesSHA256,rawOriginalClearance:{minSurfaceGap:prior.minSurfaceGap,minLowGap:prior.minLowGap,maxLowGap:prior.maxLowGap,missingTerrain:prior.missingTerrain,failedSamples:prior.failedSamples.length},diagnostic});
}
for(const p of ['source-scripts/city/government-import/run-vertical-wall-ground-crossing-diagnostic.mjs','source-scripts/city/government-import/vertical-wall-ground-crossing.mjs','source-scripts/city/government-import/test-vertical-wall-ground-crossing.mjs','3d-viewer/city/native-terrain.js'])inputHashes[p]=hash(readFileSync(new URL(p,root)));
mkdirSync(new URL('.',new URL(out,root)),{recursive:true});writeFileSync(new URL(out,root),JSON.stringify({inputHashes,rows,publication:false,newlyInstalled:0,acceptanceGranted:false},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,failedSamples:r.diagnostic.samples.length,allExactVerticalCrossings:r.diagnostic.allFailedSamplesAreExactVerticalWallCrossings,acceptanceGranted:false}))));
