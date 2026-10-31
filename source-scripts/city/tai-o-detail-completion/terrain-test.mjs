/** Actual sampler/mesh checks for staged Tai O children; no GPU or live publication. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {makeTerrainSampler,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const here=new URL('./',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,here))),sha=b=>createHash('sha256').update(b).digest('hex');
const bundle=read('./terrain-refinements.json'),parent=read('../../../3d-viewer/'+bundle.parentTerrainURL),base=read('../../../3d-viewer/city/data/terrain.json');
assert.equal(sha(readFileSync(new URL('../../../3d-viewer/'+bundle.parentTerrainURL,here))),bundle.parentSha256);
const before=makeTerrainSampler({...base,patches:[parent]}),after=makeTerrainSampler({...base,patches:[{...parent,patches:bundle.patches}]}),rows=[];let vertices=0,maxMeshError=0,maxSamplerError=0;
for(const patch of bundle.patches){
 const g=patch.meta.georef,mesh=makeTerrain(patch),p=mesh.geometry.attributes.position;
 assert.equal(p.count,patch.w*patch.h);
 for(let r=0;r<patch.h;r++)for(let c=0;c<patch.w;c++){
  const i=r*patch.w+c,x=g.bE+c*g.aE-834500,z=816500-g.bN-r*g.aN,expected=terrainVertexHeight(patch,i);
  assert(!before.mappedWater(x,z));assert(!after.mappedWater(x,z));
  const meshError=Math.abs(p.getY(i)-expected),samplerError=Math.abs(after.height(x,z)-expected);maxMeshError=Math.max(maxMeshError,meshError);maxSamplerError=Math.max(maxSamplerError,samplerError);
  assert(meshError<.00001);assert(samplerError<.000001);vertices++;
 }
 for(const [c,r] of [[-.5,-.5],[patch.w-.5,-.5],[-.5,patch.h-.5],[patch.w-.5,patch.h-.5]]){const x=g.bE+c-834500,z=816500-g.bN+r;assert(Math.abs(before.height(x,z)-after.height(x,z))<1e-9,'outside child unchanged');}
 rows.push({id:patch.id,vertices:p.count});mesh.geometry.dispose();mesh.material.dispose();
}
const proof=read('../../../docs/astra-city/tai-o-detail-completion/terrain-integration-candidate.json');assert.equal(proof.regressions.length,0);assert.equal(proof.rows.filter(r=>r.candidateNewModel).length,7);
for(const r of proof.rows.filter(r=>r.candidateNewModel))assert(!Object.values(r.afterFlags).some(Boolean),r.uid);
const estimates=read('./building-estimate-updates.json');assert.deepEqual(estimates.buildings.map(b=>b.uid).sort(),['landsd/14546:0','landsd/183353:0','landsd/309121:0']);
for(const b of estimates.buildings){assert.equal(b.sourceBaseHeightHKPD,null);assert.equal(b.sourceTopHeightHKPD,null);assert.equal(b.heightSource,'estimated');assert.equal(b.baseSource,'terrain-estimated');}
const report={stagedOnly:true,vertices,maxMeshErrorMetres:maxMeshError,maxSamplerErrorMetres:maxSamplerError,patches:rows,checks:['Actual makeTerrain child mesh agrees with source-derived grid vertices','Nested makeTerrainSampler agrees at all vertices including child/parent joins','No patch vertex intersects retained mapped hydro; outside child samples unchanged','All seven source models pass whole-footprint highest-roof and floating-base screens','Three explicit null-source estimated base updates are required'],limits:['Root must omit parent cells and render each child once using nested renderer support.','No GPU/browser or individual roof-face acceptance is claimed.']};
writeFileSync(new URL('../../../docs/astra-city/tai-o-detail-completion/terrain-runtime-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
