import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {makeTerrainSampler,ORIGIN} from '../geo.js';
import {makeTerrain} from '../world.js';
const meta=(cell)=>({georef:{aE:cell,bE:ORIGIN[0],aN:-cell,bN:ORIGIN[1]}});
test('fine terrain replaces coarse faces and walking samples the rendered fine triangles',()=>{
 const patch={w:3,h:3,elev:[2,2,2,2,12,2,2,2,2],vegetation:Array(9).fill(0),meta:meta(5),coarseCells:[0,0,1,1]};
 const coarse={w:2,h:2,elev:[2,2,2,2],vegetation:Array(4).fill(0),meta:meta(10),patches:[patch]};
 const sampler=makeTerrainSampler(coarse),terrain=makeTerrain(coarse);
 assert.equal(terrain.children[0].geometry.index.count,0);assert.equal(terrain.children[1].geometry.index.count,24);
 assert.equal(sampler.height(5,5),12);assert.equal(sampler.height(2.5,2.5),2);assert.equal(sampler.height(7.5,7.5),2);assert.equal(sampler.resolutionAt(5,5),5);
 terrain.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
});
test('retained fine Mui Wo DTM joins every coarse boundary sample without a vertical seam',()=>{
 const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url)));const coarse=read('../data/terrain.json'),patch=read('../data/terrain-mui-wo.json'),sample=makeTerrainSampler(coarse),fine=makeTerrainSampler(patch),g=patch.meta.georef;
 for(let k=0;k<patch.w;k++)for(const [c,r] of [[k,0],[k,patch.h-1],[0,k],[patch.w-1,k]]){
  const x=g.bE+c*g.aE-ORIGIN[0],z=ORIGIN[1]-(g.bN+r*g.aN);assert.ok(Math.abs(sample.raw(x,z)-fine.raw(x,z))<.006);
 }
 assert.equal(patch.meta.source.nativeCellSize,5);assert.match(patch.meta.source.sha256,/^[a-f0-9]{64}$/);
});
