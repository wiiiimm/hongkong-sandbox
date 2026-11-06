/** Export the existing renderer's mesh, without authoring or replacing geometry. */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, mkdirSync, existsSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync} from 'node:zlib';
import {createInterface} from 'node:readline';
import {makeGLB, sha} from './codec.mjs';

export function geometryGLB(geometry, uid) {
  assert.ok(!geometry.index, 'renderer must supply its actual non-indexed corners');
  const semantics={position:'POSITION',normal:'NORMAL',uv:'TEXCOORD_0',cityWindows:'_CITY_WINDOWS'};
  const views=[],accessors=[],pieces=[],attributes={};let offset=0;
  const count=geometry.getAttribute('position').count;
  assert.ok(count>0 && count%3===0, 'non-empty triangle mesh');
  for(const [name, attribute] of Object.entries(geometry.attributes)) {
    assert.ok(semantics[name], `unsupported renderer attribute: ${name}`);
    assert.ok(attribute.array instanceof Float32Array && !attribute.normalized);
    assert.equal(attribute.count,count);
    const values=attribute.array;
    for(const value of values)assert.ok(Number.isFinite(value),'finite render attributes');
    const bytes=Buffer.alloc(values.length*4);
    values.forEach((value,i)=>bytes.writeFloatLE(value,i*4));
    const view=views.length;views.push({buffer:0,byteOffset:offset,byteLength:bytes.length,target:34962});
    pieces.push(bytes);offset+=bytes.length;
    const accessor={bufferView:view,componentType:5126,count,type:['','SCALAR','VEC2','VEC3','VEC4'][attribute.itemSize]};
    assert.ok(accessor.type);
    if(name==='position') {
      accessor.min=[Infinity,Infinity,Infinity];accessor.max=[-Infinity,-Infinity,-Infinity];
      values.forEach((v,i)=>{const k=i%3;accessor.min[k]=Math.min(accessor.min[k],v);accessor.max[k]=Math.max(accessor.max[k],v);});
    }
    attributes[semantics[name]]=accessors.length;accessors.push(accessor);
  }
  return makeGLB({asset:{version:'2.0',generator:'Astra existing-render-mesh export v1'},
    buffers:[{byteLength:offset}],bufferViews:views,accessors,
    meshes:[{primitives:[{attributes,mode:4}]}],nodes:[{mesh:0,name:uid}],scenes:[{nodes:[0]}],scene:0},Buffer.concat(pieces));
}

if(process.argv[1] && resolve(process.argv[1])===resolve(new URL(import.meta.url).pathname)) {
  const root=resolve(process.argv[2]);
  const {createBuildingGeometry,describeBuilding}=await import(pathToFileURL(resolve(root,'3d-viewer/city/building-geometry.js')));
  let tilePath, tileHash, buildings;
  for await(const line of createInterface({input:process.stdin})) {
    try {
      const request=JSON.parse(line), path=resolve(root,request.tile);
      assert.ok(path.startsWith(root+'/'));
      if(path!==tilePath) {
        const bytes=readFileSync(path);tileHash=sha(bytes);tilePath=path;
        const rows=JSON.parse(bytes).buildings;
        buildings=new Map(rows.map(b=>[b.uid,b]));assert.equal(buildings.size,rows.length,'unique tile UIDs');
      }
      assert.equal(tileHash,request.tileSha256);
      const building=buildings.get(request.uid);assert.ok(building);
      const description=describeBuilding(building);
      if(request.kind==='embedded-render-v1')assert.equal(description.modelStatus,'usable','embedded model must pass the actual renderer');
      else {assert.equal(request.kind,'base-render-v1');assert.ok(!building.modelGeometry);}
      const geometry=createBuildingGeometry(building),glb=geometryGLB(geometry,request.uid);
      const output=gzipSync(glb,{level:9,mtime:0}),hash=sha(output),out=resolve(request.directory,hash+'.glb.gz');
      mkdirSync(dirname(out),{recursive:true});
      if(existsSync(out))assert.equal(sha(readFileSync(out)),hash);else writeFileSync(out,output,{flag:'wx'});
      assert.equal(sha(readFileSync(out)),hash);
      const attributes=Object.fromEntries(Object.entries(geometry.attributes).map(([key,a])=>[key,
        {itemSize:a.itemSize,count:a.count,sha256:sha(Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength))}]));
      process.stdout.write(JSON.stringify({ok:true,path:out,sha256:hash,bytes:output.length,
        triangles:geometry.attributes.position.count/3,attributes,modelStatus:description.modelStatus,
        buildingJsonSha256:sha(Buffer.from(JSON.stringify(building)))})+'\n');
      geometry.dispose();
    }catch(error){process.stdout.write(JSON.stringify({ok:false,error:error.message})+'\n');}
  }
}
