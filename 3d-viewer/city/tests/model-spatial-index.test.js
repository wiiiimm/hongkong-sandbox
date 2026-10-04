import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {ModelSpatialIndex,projectedBounds} from '../model-spatial-index.js';
import {canvasDimensions} from '../canvas-viewport.js';
test('projects clipped horizontal and vertical bounds through actual CSS canvas and near plane',()=>{
 const c=new THREE.PerspectiveCamera(60,2,.5,1000);c.updateMatrixWorld(true);const m=new THREE.Matrix4().multiplyMatrices(c.projectionMatrix,c.matrixWorldInverse),box=new THREE.Box3(new THREE.Vector3(-5,-1,-10),new THREE.Vector3(5,1,-9));
 const a=projectedBounds(box,m,800,400),b=projectedBounds(box,m,400,400);assert.ok(a.width>a.height);assert.equal(a.width,b.width*2);assert.equal(a.height,b.height);
 const cross=projectedBounds(new THREE.Box3(new THREE.Vector3(-1,-1,-1),new THREE.Vector3(1,1,1)),m,800,400);assert.equal(cross.coverage,1);
});
test('spatial query caps work and excludes distant invisible catalogue regions',()=>{
 const models=new Map(Array.from({length:10000},(_,i)=>[String(i),{uid:String(i),worldBounds:[[i*30-50,0,-100],[i*30-40,10,-90]]}]));const index=new ModelSpatialIndex(models),c=new THREE.PerspectiveCamera(60,1,.5,1000);c.updateMatrixWorld(true);const f=new THREE.Frustum().setFromProjectionMatrix(c.projectionMatrix);
 const q=index.query(f,c.position,{maxCandidates:32,maxNodes:64});assert.ok(q.rows.length<=32);assert.ok(q.visited<=64);assert.ok(q.rows.length>0);assert.ok(q.rows.every(r=>f.intersectsBox(r.box)));
});
test('all canvas sizes have finite pixel cost with fractional DPR independent of CSS importance',()=>{
 for(const [w,h,dpr] of [[390,844,3],[844,390,3],[600,800,1.25],[1440,900,2],[3840,2160,2],[5120,1440,1.5]]){const v=canvasDimensions(w,h,dpr);assert.equal(v.width,w);assert.equal(v.height,h);assert.ok(v.bufferWidth*v.bufferHeight<=4000000);assert.ok(v.pixelRatio<=1.5);}
 assert.equal(canvasDimensions(0,900,2).active,false);
 assert.equal(canvasDimensions(3840,2160,2,{maxDpr:1.75,maxPixels:32000000}).pixelRatio,1.75);
});
