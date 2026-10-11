import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {makeNature} from '../world.js';
import {BuildingIndex,inPolygon} from '../geo.js';
import {disposeGroup} from '../streaming.js';
test('late surface masks remove overlapping trees and can be reapplied without corrupting placement',()=>{
 const terrain={w:3,h:3,elev:Array(9).fill(5),vegetation:Array(9).fill(0),meta:{georef:{bE:834500,bN:816500,aE:70,aN:-70}}};
 const park={rings:[[[0,0],[100,0],[100,100],[0,100],[0,0]]]};
 const nature=makeNature([park],terrain,{height:()=>5},new BuildingIndex([])),initial=nature.count;
 assert.ok(initial>10);const canopy=nature.group.children.find(o=>o.isInstancedMesh),original=canopy.instanceMatrix.array.slice();
 const pitch=[[[20,20],[80,20],[80,80],[20,80],[20,20]]];nature.applyMask((x,z)=>inPolygon(x,z,pitch));assert.ok(nature.count<initial);
 const matrix=new THREE.Matrix4();for(let i=0;i<canopy.count;i++){canopy.getMatrixAt(i,matrix);const p=new THREE.Vector3().setFromMatrixPosition(matrix);assert.equal(inPolygon(p.x,p.z,pitch),false);}
 nature.applyMask(()=>true);assert.equal(nature.count,0);assert.equal(canopy.count,0);
 nature.applyMask(()=>false);assert.equal(nature.count,initial);assert.deepEqual(canopy.instanceMatrix.array,original);disposeGroup(nature.group);
});
