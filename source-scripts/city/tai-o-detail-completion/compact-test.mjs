/** Verify staged gzip GLB with the app's actual vendored GLTFLoader; no GPU. */
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {GLTFLoader} from '../../../3d-viewer/vendor/GLTFLoader.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const batch='compact';

const here=new URL('./',import.meta.url),doc=new URL('../../../docs/astra-city/tai-o-detail-completion/',here);
const catalogue=JSON.parse(await readFile(new URL(`${batch}/catalogue.json`,here),'utf8'));
const evidence=JSON.parse(await readFile(new URL('staged-additions.json',doc),'utf8'));
const selection=JSON.parse(gunzipSync(await readFile(new URL('../tai-o-models/building-selection.json.gz',here))));
const selected=new Map(selection.buildings.map(b=>[b.uid,b]));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
let totalTriangles=0;const results=[];
const allCatalogue=catalogue;
assert.equal(allCatalogue.models.length,catalogue.counts.catalogueModels);
assert.equal(catalogue.models.length,catalogue.counts.packedModels);
for(const entry of allCatalogue.models){
 const source=selected.get(entry.uid);assert(source);assert.equal(entry.buildingCSUID,source.buildingCSUID);assert.equal(entry.objectId,source.objectId);
 assert.equal(entry.recordedBaseHeight,source.baseHeightHKPD??null);assert.equal(entry.recordedTopHeight,source.topHeightHKPD??null);
 if(!entry.asset)continue;
 const proof=evidence.assets.find(e=>e.uid===entry.uid);assert(proof);
 const compressed=await readFile(new URL(`${batch}/${entry.asset}`,here));assert.equal(hash(compressed),entry.sha256);
 const raw=gunzipSync(compressed);assert.equal(raw.byteLength,entry.glbBytes);assert.equal(hash(raw),proof.glbSha256);
 const t=performance.now();const parsed=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'');
 parsed.scene.position.set(...catalogue.rootTranslation);parsed.scene.updateMatrixWorld(true);
 const meshes=[];parsed.scene.traverse(o=>{if(o.isMesh)meshes.push(o)});assert.equal(meshes.length,proof.primitives.length);
 let triangles=0,bytes=0;
 for(let i=0;i<meshes.length;i++){
  const geometry=meshes[i].geometry,indices=geometry.index.array;triangles+=indices.length/3;bytes+=indices.byteLength;
  const names={POSITION:'position',NORMAL:'normal',COLOR_0:'color'};
  for(const [key,expected] of Object.entries(proof.primitives[i].expandedAttributeSha256)){
   const attribute=geometry.attributes[names[key]];assert(attribute,key);bytes+=attribute.array.byteLength;
   const expanded=new attribute.array.constructor(indices.length*attribute.itemSize);
   for(let v=0;v<indices.length;v++)expanded.set(attribute.array.subarray(indices[v]*attribute.itemSize,(indices[v]+1)*attribute.itemSize),v*attribute.itemSize);
   assert.equal(hash(Buffer.from(expanded.buffer)),expected,`${entry.uid} ${key}: original expanded float bits`);
  }
 }
 assert.equal(triangles,entry.triangles);assert.equal(bytes,entry.decodedGeometryBytes);totalTriangles+=triangles;
 const bounds=new THREE.Box3().setFromObject(parsed.scene,true),actual=[bounds.min.toArray(),bounds.max.toArray()];
 const maxBoundsError=Math.max(...actual.flat().map((v,i)=>Math.abs(v-entry.worldBounds.flat()[i])));assert(maxBoundsError<1e-7,`${entry.uid}: source transform bounds`);
 const sourceGltf=JSON.parse(await readFile(new URL(`../../../${proof.sourceEntry}`,here),'utf8'));
 assert.deepEqual(parsed.parser.json.nodes,sourceGltf.nodes);assert.deepEqual(parsed.parser.json.materials,sourceGltf.materials);
 results.push({uid:entry.uid,modelId:entry.modelId,triangles,compressedBytes:compressed.byteLength,decodedGeometryBytes:bytes,maxBoundsError,parseAndVerificationMs:performance.now()-t});
 for(const mesh of meshes){mesh.geometry.dispose();for(const material of Array.isArray(mesh.material)?mesh.material:[mesh.material])material.dispose()}
}
assert.equal(results.length,catalogue.counts.packedModels);assert.equal(totalTriangles,catalogue.counts.packedTriangles);
const report={catalogueSha256:hash(await readFile(new URL(`${batch}/catalogue.json`,here))),checks:['All catalogue UID/CSUID/OBJECTID and recorded source heights match retained selection','Gzip and decoded GLB hashes match','Actual app GLTFLoader parses each packed asset','Expanded position/normal/colour bits reproduce the original source in triangle order','Native node/material metadata is unchanged','City-translated bounds agree within 0.0000001 m','Decoded byte and triangle counts match catalogue'],models:results,limits:['CPU decoder validation; no claim of GPU frame rate or architectural/terrain acceptance.']};
await writeFile(new URL(`${batch}-verification.json`,doc),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({models:results.length,triangles:totalTriangles,checks:report.checks.length}));
