// CPU integration against retained source packages; no WebGL or data publication.
// node 3d-viewer/city/tests/infrastructure-staged.mjs [package.json ...]
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {BridgeLayer} from '../bridges.js';
const paths=process.argv.slice(2);
if(!paths.length)paths.push('source-scripts/city/tsing-ma/bridges-tsing-ma.json','source-scripts/city/mui-wo-completion/bridges-mui-wo.json');
const mapped=JSON.parse(readFileSync(new URL('../data/bridges.json',import.meta.url))),packages=new Map(paths.map(path=>[path,JSON.parse(readFileSync(path))]));
const digest=data=>createHash('sha256').update(JSON.stringify(data)).digest('hex');
const before=new Map([...packages].map(([path,data])=>[path,digest(data)])),originalFetch=globalThis.fetch,results=[];
globalThis.fetch=async url=>({ok:true,json:async()=>url==='mapped'?mapped:packages.get(url)});
try{
 for(const order of ['official-first','mapped-first']){
  const layer=new BridgeLayer({scene:new THREE.Scene(),sampler:{height:()=>2}});
  try{
   if(order==='mapped-first')assert.equal(await layer.load('mapped'),true);
   for(const path of paths)assert.equal(await layer.load(path),true,`${path}: ${JSON.stringify([...layer.errors])}`);
   if(order==='official-first')assert.equal(await layer.load('mapped'),true,JSON.stringify([...layer.errors]));
   const expectedModels=[...packages.values()].reduce((sum,p)=>sum+p.models.length,0),expectedClips=[...packages.values()].reduce((sum,p)=>sum+p.proxyClips.length,0);
   assert.equal(layer.stats.sourceModels,expectedModels);assert.equal(layer.proxyClips.size,expectedClips);assert.equal(layer.stats.pendingProxyClips,0);
   for(const data of packages.values())for(const model of data.models){assert.ok(layer.records.has(model.id));for(const uid of model.suppressesBuildingUids||[])assert.ok(layer.suppressedBuildingUids.has(uid));}
   const views=[];
   for(const data of packages.values()){
    const b=data.models[0].worldBounds,x=(b[0][0]+b[1][0])/2,z=(b[0][2]+b[1][2])/2;layer.plan(x,z,2200);
    assert.ok(layer.stats.tiles<=24);for(const mesh of layer.pickMeshes())assert.ok(mesh.geometry.attributes.position.array.every(Number.isFinite));
    views.push({region:data.region,cached:layer.stats.tiles,meshes:layer.pickMeshes().length});
   }
   results.push({order,stats:layer.stats,views});
  }finally{layer.dispose();assert.equal(layer.cache.size,0);assert.equal(layer.suppressedBuildingUids.size,0);}
 }
 for(const [path,data] of packages)assert.equal(digest(data),before.get(path),'Source package was mutated');
 console.log(JSON.stringify({verifiedUTC:new Date().toISOString(),gpu:false,sourcePackages:[...before].map(([path,sha256])=>({path,parsedContentSHA256:sha256})),results},null,2));
}finally{globalThis.fetch=originalFetch;}
