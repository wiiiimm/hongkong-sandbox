import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {levels,nearest} from './triangles.mjs';
const face=(a,b,c)=>new THREE.Triangle(new THREE.Vector3(...a),new THREE.Vector3(...b),new THREE.Vector3(...c));
test('a shared box does not count as source triangle contact',()=>{
 const g={faces:[face([0,0,0],[10,0,0],[0,0,10])]};assert(nearest(g,new THREE.Vector3(9,0,9))>5);
});
test('lower wall rim can contact a real podium roof',()=>{
 const g={faces:[face([0,12,0],[10,12,0],[0,12,10])]};assert.equal(nearest(g,new THREE.Vector3(2,12,2)),0);assert.equal(nearest(g,new THREE.Vector3(2,15,2)),3);
});
test('vertical seam contact is found despite degenerate horizontal projection',()=>{
 const g={faces:[face([0,0,0],[0,10,0],[0,0,10])]};assert(nearest(g,new THREE.Vector3(.2,2,2))<.201);
});
test('open-bottom roof ray is a roof, not a foundation',()=>{
 const g={triangles:[{ax:0,az:0,bx:10,bz:0,cx:0,cz:10,ay:100,by:100,cy:100,det:100,minX:0,maxX:10,minZ:0,maxZ:10}]};assert.deepEqual(levels(g,2,2),[100]);assert.deepEqual(levels(g,9,9),[]);
});
