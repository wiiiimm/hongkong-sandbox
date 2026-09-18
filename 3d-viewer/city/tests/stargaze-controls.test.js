import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {StargazeControls} from '../stargaze-controls.js';

test('secondary touches and their capture events cannot replace or cancel the active sky drag',()=>{
 class Canvas extends EventTarget{clientWidth=800;clientHeight=600;focus(){}setPointerCapture(){}}
 const canvas=new Canvas(),camera=new THREE.PerspectiveCamera(),controls={target:new THREE.Vector3(),update(){},enabled:true};
 let picks=0;const sky=new StargazeControls({camera,controls,canvas,onPick:()=>picks++});sky.enter(new THREE.Vector3(0,30,0));
 const send=(type,id,x=100,y=100)=>{const event=new Event(type);Object.assign(event,{pointerId:id,button:0,clientX:x,clientY:y});canvas.dispatchEvent(event);};
 send('pointerdown',11);send('pointerdown',12);assert.equal(sky.drag.id,11);
 send('pointermove',12,180);assert.equal(sky.yaw,0);
 send('lostpointercapture',12);assert.equal(sky.drag.id,11);
 send('pointercancel',12);assert.equal(sky.drag.id,11);
 send('pointermove',11,120);assert.ok(sky.yaw<0);
 send('pointerup',12);assert.equal(sky.drag.id,11);assert.equal(picks,0);
 send('pointercancel',11);assert.equal(sky.drag,null);
 send('pointerdown',13);send('pointerup',13);assert.equal(picks,1);assert.equal(sky.drag,null);
});
