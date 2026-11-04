/** Capture exact rendered BASIC part prisms with full production position parity. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {describeBuilding,createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3],sha=b=>createHash('sha256').update(b).digest('hex'),input=JSON.parse(readFileSync(new URL(inputPath,root)));
for(const [p,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const rows=[];
for(const row of input.rows){
 const states={};
 for(const state of ['before','after']){
  const b={...row.building,...(state==='after'?{foundationBase:row.foundationBase}:{})};assert(!b.modelGeometry);
  const description=describeBuilding(b),parts=[],combined=[];
  for(const part of description.parts){
   const path=ring=>{const r=ring.length>1&&ring[0][0]===ring.at(-1)[0]&&ring[0][1]===ring.at(-1)[1]?ring.slice(0,-1):ring;return r.map(([x,z])=>new THREE.Vector2(x,-z));};
   const shape=new THREE.Shape(path(part.rings[0]));for(const hole of part.rings.slice(1))shape.holes.push(new THREE.Path(path(hole)));
   const geometry=new THREE.ExtrudeGeometry(shape,{depth:part.top-part.bottom,bevelEnabled:false,steps:1,curveSegments:1});geometry.rotateX(-Math.PI/2);geometry.translate(0,part.bottom,0);
   const position=Array.from(geometry.attributes.position.array);combined.push(...position);const ys=position.filter((_,i)=>i%3===1),bottom=Math.min(...ys),top=Math.max(...ys),caps=[];
   for(let i=0;i<position.length;i+=9){const face=[position.slice(i,i+3),position.slice(i+3,i+6),position.slice(i+6,i+9)];if(face.every(p=>p[1]===top)){const [a,b,c]=face;if((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])!==0)caps.push(face);}}
   assert(caps.length>0&&bottom<top);parts.push({kind:part.kind,bottom,top,caps,position,index:Array.from({length:position.length/3},(_,i)=>i)});geometry.dispose();
  }
  const actual=createBuildingGeometry(b);assert(!actual.index);assert.deepEqual(new Float32Array(combined),actual.attributes.position.array,'Reconstructed parts differ from actual production geometry');
  states[state]={parts,fullProductionPositionParity:true,productionPositionSHA256:sha(Buffer.from(actual.attributes.position.array.buffer,actual.attributes.position.array.byteOffset,actual.attributes.position.array.byteLength))};actual.dispose();
 }
 rows.push({uid:row.building.uid,...states});
}
assert(verifyModuleClosure(closure,root));for(const [p,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
writeFileSync(new URL(outputPath,root),JSON.stringify({rows,inputHashes:{...input.inputHashes,...closure.inputHashes},completeRecursiveProductionModuleClosure:closure,sourceGeometryChanges:0,installationApproved:false}));
