import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {geometryGLB} from './export_render_mesh.mjs';
import {parseGLB,encodeExact,verifyExact} from './codec.mjs';

test('render export retains Float32 corner order, normals, UV and window mask exactly',async()=>{
  const g=new THREE.BufferGeometry();
  const attrs={position:[3,[1.125,2,3,4,5,6,7,8,9]],normal:[3,[0,1,0,0,0,1,1,0,0]],uv:[2,[0,0,1,0,0,1]],cityWindows:[1,[0,1,0]]};
  const semantics={position:'POSITION',normal:'NORMAL',uv:'TEXCOORD_0',cityWindows:'_CITY_WINDOWS'};
  for(const [name,[size,values]]of Object.entries(attrs))g.setAttribute(name,new THREE.Float32BufferAttribute(values,size));
  const glb=geometryGLB(g,'fixture'),parsed=parseGLB(glb);
  for(const [name]of Object.entries(attrs)){
    const a=parsed.json.accessors[parsed.json.meshes[0].primitives[0].attributes[semantics[name]]];
    const v=parsed.json.bufferViews[a.bufferView],expected=g.getAttribute(name).array;
    assert.deepEqual(parsed.bin.subarray(v.byteOffset,v.byteOffset+v.byteLength),Buffer.from(expected.buffer));
  }
  assert.deepEqual(parsed.json.nodes,[{mesh:0,name:'fixture'}]);
  const encoded=await encodeExact(glb);await verifyExact(glb,encoded.glb);
  assert.deepEqual(geometryGLB(g,'fixture'),glb,'deterministic container');
  g.attributes.position.array[0]=NaN;
  assert.throws(()=>geometryGLB(g,'fixture'),/finite/);
});
