import {test} from 'node:test';
import assert from 'node:assert/strict';
import {installSourcePixelWitness} from './source_pixel_visibility_witness_v1_20261027.mjs';

for(const [name,visible,throws]of [['visible target',true,false],['occluded target',false,false],['render failure restores scene',false,true]])test(name,()=>{
 const materials=[{side:1},{side:2}],meshes=materials.map(material=>({isMesh:true,material})),background={original:true},disposed=[];
 let draws=0;
 class Material{constructor(options){Object.assign(this,options);}dispose(){disposed.push(this);}}
 const gl={drawingBufferWidth:2,drawingBufferHeight:1,RGBA:1,UNSIGNED_BYTE:2,readPixels(x,y,w,h,format,type,pixels){pixels.set(visible?[255,0,255,255,0,0,0,255]:[0,0,0,255,0,0,0,255]);}};
 globalThis.window={__port:{THREE:{Color:class{},MeshBasicMaterial:Material},scene:{background,traverse(fn){meshes.forEach(fn);}},stream:{detailedModels:new Map([['source',{active:true,meshes:[meshes[0]]}]])},renderer:{getContext(){return gl;}}},__portDraw(){draws++;if(throws&&draws===1)throw Error('diagnostic draw failed');}};
 try{
  installSourcePixelWitness();
  if(throws)assert.throws(()=>window.__portSourceVisibility('source'),/diagnostic draw failed/);
  else assert.equal(window.__portSourceVisibility('source').visiblePixels,visible?1:0);
  assert.equal(window.__port.scene.background,background);
  assert.equal(meshes[0].material,materials[0]);assert.equal(meshes[1].material,materials[1]);
  assert.equal(disposed.length,2);assert.equal(draws,2);
 }finally{delete globalThis.window;}
});
