import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {trianglePointIndex} from './triangle-point-index.mjs';

test('negative cell boundaries and tolerance-expanded bounds keep nearby faces',()=>{
 const g={position:[-8,0,-8,-8,2,-8,-8,0,-6],index:[0,1,2]},index=trianglePointIndex(g);
 assert.deepEqual(index.candidates([-8.0009,1,-7]),[0]);
 assert.deepEqual(index.candidates([-8.002,1,-7]),[]);
 assert.deepEqual(index.candidates([-8,3,-7]),[]);
});
test('oversized projected faces fall back to the large-face list',()=>{
 const g={position:[-100,0,-100,100,0,-100,-100,0,100],index:[0,1,2]},index=trianglePointIndex(g,{maxCells:1});
 assert.equal(index.largeFaces,1);assert.deepEqual(index.candidates([0,0,0]),[0]);
});
test('filtering retains original face indices and source ordering without mutation',()=>{
 const g={position:[0,0,0,1,0,0,0,1,0],index:[0,1,2,0,1,2,0,1,2]},before=structuredClone(g);
 assert.deepEqual(trianglePointIndex(g,{acceptFace:(_,i)=>i!==1}).candidates([0,0,0]),[0,2]);assert.deepEqual(g,before);
});
test('conservative index never excludes exact triangle contacts across a deterministic corpus',()=>{
 let seed=123456;const random=()=>((seed=(1664525*seed+1013904223)>>>0)/2**32),position=[],index=[];
 for(let f=0;f<100;f++){const x=random()*100-50,y=random()*10-5,z=random()*100-50;for(let k=0;k<3;k++){position.push(x+random()*4,y+random()*4,z+random()*4);index.push(index.length);}}
 const g={position,index},lookup=trianglePointIndex(g),tri=new THREE.Triangle(),p=new THREE.Vector3(),closest=new THREE.Vector3();
 for(let f=0;f<100;f++){
  [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(position,index[f*3+k]*3));
  for(const bary of [[1,0,0],[0,1,0],[0,0,1],[.2,.3,.5]]){
   p.copy(tri.a).multiplyScalar(bary[0]).addScaledVector(tri.b,bary[1]).addScaledVector(tri.c,bary[2]);p.x+=.0001;
   tri.closestPointToPoint(p,closest);assert(closest.distanceTo(p)<=.001);assert(lookup.candidates(p.toArray()).includes(f));
  }
 }
});
test('invalid index budgets and query coordinates fail explicitly',()=>{
 const g={position:[],index:[]};for(const options of [{cell:0},{tolerance:-1},{maxCells:0}])assert.throws(()=>trianglePointIndex(g,options));
 assert.throws(()=>trianglePointIndex(g).candidates([NaN,0,0]));
});
