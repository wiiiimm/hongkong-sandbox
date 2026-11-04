/** Validate diagnostic grid facets against the actual, unchanged geo.js grid branch. */
import {readFileSync,writeFileSync}from'node:fs';
import{createHash}from'node:crypto';
import assert from'node:assert/strict';
import{makeTerrainSampler,terrainVertexHeight}from'../../../3d-viewer/city/geo.js';
const[patchPath,contractPath,outPath]=process.argv.slice(2);assert(patchPath&&contractPath&&outPath);
const patch=JSON.parse(readFileSync(patchPath)),contract=JSON.parse(readFileSync(contractPath)),g=patch.meta.georef,w=patch.w,h=patch.h;
assert.equal(patch.nativeMesh.source.numericalCoverageGap.policy,'parent-grid-fallback');
const gridData={...patch};delete gridData.nativeMesh;const sampler=makeTerrainSampler(gridData),vertices=[];
for(let r=0;r<h;r++)for(let c=0;c<w;c++)vertices.push([g.bE+c*g.aE-834500,terrainVertexHeight(patch,r*w+c),816500-g.bN-r*g.aN]);
let checks=0,maxError=0;const grid=[];
for(let r=0;r<h-1;r++)for(let c=0;c<w-1;c++){const i=r*w+c;for(const ids of[[i,i+1,i+w],[i+w+1,i+w,i+1]]){const tri=ids.map(i=>vertices[i]);grid.push(tri);for(const weights of[[1,0,0],[0,1,0],[0,0,1],[1/3,1/3,1/3]]){const p=[0,1,2].map(k=>weights.reduce((s,q,j)=>s+q*tri[j][k],0)),error=Math.abs(sampler.height(p[0],p[2])-p[1]);assert(Number.isFinite(error));maxError=Math.max(maxError,error);checks++;}}}
assert(maxError<1e-8,'Diagnostic grid differs from current renderer grid branch');
const[lo,hi]=contract.completeSourceFourWorldBounds,selected=grid.filter(t=>[0,2].every(k=>Math.max(...t.map(p=>p[k]))>=lo[k]&&Math.min(...t.map(p=>p[k]))<=hi[k]));
const array=new Float64Array(selected.flat(2)),sha=createHash('sha256').update(Buffer.from(array.buffer)).digest('hex');
assert.equal(sha,contract.virtualFallbackSHA256);assert.equal(selected.length,contract.virtualFallbackTriangles);
writeFileSync(outPath,JSON.stringify({passed:true,gridTriangles:grid.length,selectedTriangles:selected.length,samplerChecks:checks,maximumSamplerErrorM:maxError,virtualFallbackSHA256:sha,sourceGeometryChanges:0,terrainGeometryChanges:0,qualification:'The exact diagnostic grid used in the clearance proof has the current renderer diagonal and vertex heights. All grid vertices/triangle centroids match unchanged geo.js; the full selected Float64 array hash equals the clearance input. No terrain is published or changed.'}));
