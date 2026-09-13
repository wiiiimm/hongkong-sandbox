/** Decode only the five reviewed contact models with the app's original loader. */
import {readFile} from 'node:fs/promises';
import {gunzipSync} from 'node:zlib';
import {GLTFLoader} from '../../../3d-viewer/vendor/GLTFLoader.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const here=new URL('./',import.meta.url),doc=new URL('../../../docs/astra-city/central-completion/',here);
export async function loadContactModels(){
 const contacts=JSON.parse(await readFile(new URL('route-preflight.json',doc))).routes.flatMap(r=>r.stagedBlockerBuildings),uids=new Set(contacts.map(c=>c.uid)),models=new Map(),meshStats=[];
 for(const batch of ['compact','compact-followup']){
  const catalogue=JSON.parse(await readFile(new URL(`${batch}/catalogue.json`,here)));
  for(const spec of catalogue.models.filter(m=>uids.has(m.uid))){
   const raw=gunzipSync(await readFile(new URL(`${batch}/${spec.asset}`,here))),parsed=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'');parsed.scene.position.set(...catalogue.rootTranslation);parsed.scene.updateMatrixWorld(true);
   const positions=[],indices=[];parsed.scene.traverse(mesh=>{
    if(!mesh.isMesh)return;const position=mesh.geometry.attributes.position,offset=positions.length/3,v=new THREE.Vector3();
    for(let i=0;i<position.count;i++){v.fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);positions.push(v.x,v.y,v.z)}
    if(mesh.geometry.index)for(const i of mesh.geometry.index.array)indices.push(offset+i);else for(let i=0;i<position.count;i++)indices.push(offset+i);
    mesh.geometry.dispose();for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material])m.dispose();
   });
   models.set(spec.uid,{position:Float64Array.from(positions),index:Uint32Array.from(indices),bounds:spec.worldBounds});meshStats.push({uid:spec.uid,modelId:spec.modelId,triangles:indices.length/3});
  }
 }
 return{models,meshStats};
}
export function nearModel(model,x,z,radius){const [lo,hi]=model.bounds;return x+radius>=lo[0]&&x-radius<=hi[0]&&z+radius>=lo[2]&&z-radius<=hi[2]}
