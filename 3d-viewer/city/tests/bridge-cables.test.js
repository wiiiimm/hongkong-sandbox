import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../../vendor/three.module.js';
import {BridgeCables,CABLE_SOURCE_PARENTS} from '../bridge-cables.js';
const packet=region=>JSON.parse(fs.readFileSync(new URL(`../../../source-scripts/city/${region}/cables-${region}.json`,import.meta.url)));
const all=Object.values(CABLE_SOURCE_PARENTS).flat();
const response=data=>({ok:true,json:async()=>structuredClone(data)});
const at=(layer,parents=all)=>layer.plan(-8700,-7900,3000,parents);
test('both real packets retain separate illustrative identities and require every original parent',async()=>{
 const scene=new THREE.Scene(),layer=new BridgeCables({scene,fetchImpl:async url=>response(packet(url))});
 await layer.load('tsing-ma');await layer.load('ting-kau');assert.equal(layer.stats.sourceTriangles,0);assert.equal(layer.stats.illustrativeTriangles,10536);assert.equal(layer.pickMeshes().length,0);
 at(layer,CABLE_SOURCE_PARENTS['tsing-ma'].slice(1));assert.equal(layer.pickMeshes().length,0);at(layer,CABLE_SOURCE_PARENTS['ting-kau']);assert.equal(layer.pickMeshes().length,1);at(layer);assert.equal(layer.pickMeshes().length,2);
 for(const r of layer.records.values()){assert.equal(r.walkable,false);assert.equal(r.estimatedGeometry,true);assert.equal(r.sourceTriangles,0);assert.match(r.accessNote,/No walking/);const g=layer.geometryFor(r);assert.equal(g.attributes.position.count/3,r.illustrativeTriangles);assert.deepEqual([...g.attributes.position.array],Array.from(new Float32Array(r.modelGeometry.position)));assert.equal(g.attributes.cityWindows,undefined);g.dispose();}
 at(layer,[]);assert.equal(layer.pickMeshes().length,0);layer.dispose();assert.equal(scene.children.length,0);
});
test('parent-first loading, duplicate URL deduplication, range and layer toggles preserve picking',async()=>{
 let calls=0;const layer=new BridgeCables({fetchImpl:async()=>{calls++;return response(packet('ting-kau'));}});at(layer);
 const a=layer.load('cables'),b=layer.load('cables');assert.equal(a,b);assert.equal(await a,true);assert.equal(calls,1);assert.equal(await layer.load('cables'),true);assert.equal(calls,1);
 const mesh=layer.pickMeshes()[0],r=layer.featureAt({object:mesh});assert.equal(r.region,'ting-kau');assert.equal(layer.featureAt({object:new THREE.Mesh()}),undefined);
 layer.group.visible=false;assert.equal(layer.pickMeshes().length,0);assert.equal(layer.featureAt({object:mesh}),undefined);layer.group.visible=true;at(layer);assert.equal(layer.pickMeshes().length,1);layer.plan(20000,20000,100,all);assert.equal(layer.pickMeshes().length,0);layer.dispose();
});
test('invalid or failed cable data cannot replace existing geometry and Retry recovers independently',async()=>{
 let broken=true;const layer=new BridgeCables({fetchImpl:async url=>{if(url==='good')return response(packet('tsing-ma'));const d=packet('ting-kau');if(broken)d.counts.originalSourceModels=1;return response(d);}});at(layer);await layer.load('good');const existing=layer.pickMeshes()[0];assert.equal(await layer.load('retry'),false);assert.equal(layer.records.size,1);assert.deepEqual(layer.stats.errors,['retry']);assert.equal(layer.pickMeshes()[0],existing);
 broken=false;assert.equal(await layer.retry(),true);assert.equal(layer.records.size,2);assert.deepEqual(layer.stats.errors,[]);assert.equal(layer.pickMeshes()[0],existing);layer.dispose();
});
test('malformed geometry, bounds, floor claims and duplicate region fail atomically',async()=>{
 const mutations=[d=>d.modelGeometry.position[0]=NaN,d=>d.modelGeometry.normal.pop(),d=>d.modelGeometry.worldBounds[0][0]+=200,d=>d.walkable=true,d=>d.modelGeometry.colour[0]=2,d=>d.counts.illustrativeTriangles--];
 for(const mutate of mutations){const d=packet('ting-kau');mutate(d);const layer=new BridgeCables({fetchImpl:async()=>response(d)});assert.equal(await layer.load('bad'),false);assert.equal(layer.group.children.length,0);layer.dispose();}
 let changed=false;const layer=new BridgeCables({fetchImpl:async()=>{const d=packet('ting-kau');if(changed)d.id+='-duplicate';return response(d);}});await layer.load('one');const old=[...layer.meshes.values()][0];changed=true;assert.equal(await layer.load('two'),false);assert.equal(layer.group.children.length,1);assert.equal([...layer.meshes.values()][0],old);layer.dispose();
});
test('disposal releases visible GPU resources once and prevents late completion',async()=>{
 const layer=new BridgeCables({fetchImpl:async()=>response(packet('ting-kau'))});await layer.load('ready');const mesh=[...layer.meshes.values()][0];let geometryDisposals=0,materialDisposals=0;mesh.geometry.addEventListener('dispose',()=>geometryDisposals++);mesh.material.addEventListener('dispose',()=>materialDisposals++);layer.dispose();layer.dispose();assert.equal(geometryDisposals,1);assert.equal(materialDisposals,1);
 let release,signal;const delayed=new BridgeCables({fetchImpl:async(_,options)=>{signal=options.signal;await new Promise(resolve=>release=resolve);return response(packet('ting-kau'));}});const pending=delayed.load('late');await Promise.resolve();delayed.dispose();assert.equal(signal.aborted,true);release();assert.equal(await pending,false);assert.equal(delayed.group.children.length,0);assert.equal(delayed.stats.pending,0);assert.deepEqual(delayed.stats.errors,[]);
});

test('native browser fetch keeps its global receiver instead of the layer instance',async()=>{
 const layer=new BridgeCables({fetchImpl:function(){assert.equal(this,globalThis);return Promise.resolve(response(packet('ting-kau')));}});
 assert.equal(await layer.load('browser-receiver'),true);assert.equal(layer.records.size,1);layer.dispose();
});
