import * as THREE from '../vendor/three.module.js';
import {GLTFLoader} from '../vendor/GLTFLoader.js';
import {facadeMaterial} from './world.js';
import {buildingLighting} from './lighting.js';
import {describeBuilding} from './building-geometry.js';
const HASH=/^[a-f0-9]{64}$/;
const positive=n=>Number.isSafeInteger(n)&&n>0;
const abort=()=>new DOMException('Aborted','AbortError');
const SHA256_K=new Uint32Array([0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]);
const rotate=(x,n)=>(x>>>n)|(x<<(32-n));
/** Keeps model integrity checks available on LAN/Tailscale HTTP preview origins. */
export async function sha256Hex(bytes,subtle=globalThis.crypto?.subtle){
 if(subtle){const digest=await subtle.digest('SHA-256',bytes);return [...new Uint8Array(digest)].map(v=>v.toString(16).padStart(2,'0')).join('');}
 const bitLength=bytes.length*8,total=Math.ceil((bytes.length+9)/64)*64,padded=new Uint8Array(total),view=new DataView(padded.buffer),w=new Uint32Array(64);padded.set(bytes);padded[bytes.length]=0x80;view.setUint32(total-8,Math.floor(bitLength/0x100000000));view.setUint32(total-4,bitLength>>>0);
 const h=new Uint32Array([0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]);
 for(let offset=0;offset<total;offset+=64){
  for(let i=0;i<16;i++)w[i]=view.getUint32(offset+i*4);for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2],s0=rotate(a,7)^rotate(a,18)^(a>>>3),s1=rotate(b,17)^rotate(b,19)^(b>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;}
  let [a,b,c,d,e,f,g,q]=h;
  for(let i=0;i<64;i++){const s1=rotate(e,6)^rotate(e,11)^rotate(e,25),choice=(e&f)^(~e&g),t1=(q+s1+choice+SHA256_K[i]+w[i])>>>0,s0=rotate(a,2)^rotate(a,13)^rotate(a,22),majority=(a&b)^(a&c)^(b&c),t2=(s0+majority)>>>0;q=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
  h[0]=(h[0]+a)>>>0;h[1]=(h[1]+b)>>>0;h[2]=(h[2]+c)>>>0;h[3]=(h[3]+d)>>>0;h[4]=(h[4]+e)>>>0;h[5]=(h[5]+f)>>>0;h[6]=(h[6]+g)>>>0;h[7]=(h[7]+q)>>>0;
 }
 return [...h].map(v=>v.toString(16).padStart(8,'0')).join('');
}
export function prepareModelCatalogue(data,url){
 if(data?.schemaVersion!==1||!['official-model-catalogue','staged-official-model-catalogue'].includes(data.kind)||data.crs!=='EPSG:2326'||data.verticalDatum!=='Hong Kong Principal Datum'||JSON.stringify(data.rootTranslation)!=='[-834500,0,816500]'||!Array.isArray(data.models)||!data.models.length||data.models.length>2048||data.counts?.packedModels!==data.models.length)throw new Error('Invalid compact model catalogue');
 const seen=new Set();return data.models.map(r=>{
  const b=r.worldBounds;
  if(typeof r.uid!=='string'||!/^landsd\/\d+:\d+$/.test(r.uid)||seen.has(r.uid)||String(r.objectId)!==r.uid.split('/')[1].split(':')[0]||typeof r.buildingCSUID!=='string'||!r.buildingCSUID||typeof r.modelId!=='string'||!r.modelId||typeof r.sourceTile!=='string'||typeof r.asset!=='string'||!r.asset.endsWith('.glb.gz')||r.encoding!=='gzip'||!HASH.test(r.sha256)||![r.bytes,r.glbBytes,r.decodedGeometryBytes,r.triangles,r.indexedVertices].every(positive)||r.bytes>32*1024*1024||r.glbBytes>128*1024*1024||!Array.isArray(b)||b.length!==2||!b.every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite))||b[0].some((v,i)=>v>=b[1][i]))throw new Error('Invalid compact model entry '+r?.uid);
  const suppressions=r.suppressesBuildingUids??[];
  if(!Array.isArray(suppressions)||suppressions.length>64||new Set(suppressions).size!==suppressions.length||suppressions.some(uid=>!/^landsd\/\d+:\d+$/.test(uid)||uid===r.uid))throw new Error('Invalid model assembly suppression '+r?.uid);
  seen.add(r.uid);const assetURL=new URL(r.asset,url).href;
  if(new URL(assetURL).origin!==new URL(url).origin)throw new Error('Model assets must share catalogue origin');
  return {...r,assetURL,catalogueURL:url,rootTranslation:data.rootTranslation,coordinatePolicy:data.coordinatePolicy,datasetId:data.datasetId};
 });
}
export function modelBudget(entry){
 // Source CPU buffers + their GPU copy, exact Float64 collision coordinates,
 // Uint32 collision indices, triangle bounds and a per-face spatial-index reserve.
 const collisionBytes=entry.indexedVertices*24+entry.triangles*(12+48+64);
 return {geometryBytes:entry.decodedGeometryBytes,residentBytes:entry.decodedGeometryBytes*2+collisionBytes+65536,triangles:entry.triangles};
}
export function disposeOfficialModel(value){
 if(!value)return;value.group?.removeFromParent();const geometries=new Set(),materials=new Set();
 value.group?.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)for(const m of [].concat(o.material))materials.add(m);});
 for(const g of geometries)g.dispose();for(const m of materials)m.dispose();
}
async function boundedBytes(stream,expected,signal){
 const reader=stream.getReader(),chunks=[];let length=0;
 try{for(;;){if(signal?.aborted)throw abort();const {value,done}=await reader.read();if(done)break;length+=value.length;if(length>expected)throw new Error('Model response exceeds declared byte count');chunks.push(value);}}
 catch(error){await reader.cancel().catch(()=>{});throw error;}finally{reader.releaseLock();}
 if(length!==expected)throw new Error('Model response byte count mismatch');
 const bytes=new Uint8Array(length);let at=0;for(const chunk of chunks){bytes.set(chunk,at);at+=chunk.length;}return bytes;
}
function nativeGLB(bytes){
 const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 if(bytes.length<20||view.getUint32(0,true)!==0x46546c67||view.getUint32(4,true)!==2||view.getUint32(8,true)!==bytes.length||view.getUint32(16,true)!==0x4e4f534a)throw new Error('Invalid compact GLB');
 const length=view.getUint32(12,true);if(length>bytes.length-20)throw new Error('Invalid compact GLB JSON');
 const json=JSON.parse(new TextDecoder().decode(bytes.subarray(20,20+length)));
 if(json.buffers?.some(b=>b.uri)||json.images?.length||json.extensionsRequired?.length)throw new Error('Compact models must be self-contained and require no additional decoders');
 return json;
}
/** Decodes exact native source geometry. It does not change source node transforms. */
export async function loadOfficialModel(entry,building,lighting,{signal,fetcher=fetch,loader=new GLTFLoader()}={}){
 if(!building||building.uid!==entry.uid||building.objectId!==entry.objectId||building.buildingCSUID!==entry.buildingCSUID||(building.baseHeightHKPD??null)!==entry.recordedBaseHeight||(building.topHeightHKPD??null)!==entry.recordedTopHeight)throw new Error('Model does not match the loaded official building source');
 if(signal?.aborted)throw abort();const response=await fetcher(entry.assetURL,{signal});if(!response.ok)throw new Error('Official model HTTP '+response.status);
 const compressed=await boundedBytes(response.body,entry.bytes,signal);
 if(await sha256Hex(compressed)!==entry.sha256)throw new Error('Official model SHA-256 mismatch');
 const bytes=await boundedBytes(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')),entry.glbBytes,signal),source=nativeGLB(bytes);
 if(signal?.aborted)throw abort();const gltf=await loader.parseAsync(bytes.buffer,'');let result={group:gltf.scene};
 try{
  if(signal?.aborted)throw abort();const group=gltf.scene;group.position.set(...entry.rootTranslation);group.updateMatrixWorld(true);
  const meshes=[];group.traverse(o=>{if(o.isMesh)meshes.push(o);});if(!meshes.length)throw new Error('Empty official model');
  let vertices=0,triangles=0,geometryBytes=0;
  for(const mesh of meshes){
   const g=mesh.geometry,p=g.attributes.position,n=g.attributes.normal,c=g.attributes.color,index=g.index;
   if(!p||p.itemSize!==3||!n||n.count!==p.count||!c||c.count!==p.count||!index||index.count%3||[p,n,c].some(a=>!a.array.every(Number.isFinite))||!index.array.every(i=>Number.isInteger(i)&&i>=0&&i<p.count))throw new Error('Invalid official model attributes');
   vertices+=p.count;triangles+=index.count/3;geometryBytes+=index.array.byteLength+Object.values(g.attributes).reduce((sum,a)=>sum+a.array.byteLength,0);
  }
  if(vertices!==entry.indexedVertices||triangles!==entry.triangles||geometryBytes!==entry.decodedGeometryBytes)throw new Error('Official model geometry count mismatch');
  const bounds=new THREE.Box3().setFromObject(group,true),flat=[...bounds.min.toArray(),...bounds.max.toArray()];
  if(flat.some((v,i)=>Math.abs(v-entry.worldBounds.flat()[i])>.002))throw new Error('Official model source placement mismatch');
  const position=new Float64Array(vertices*3),index=new Uint32Array(triangles*3),point=new THREE.Vector3();let vertexOffset=0,indexOffset=0;
  for(const mesh of meshes){
   const p=mesh.geometry.attributes.position,indices=mesh.geometry.index.array;
   for(let i=0;i<p.count;i++){point.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);position.set(point.toArray(),(vertexOffset+i)*3);}
   for(let i=0;i<indices.length;i++)index[indexOffset+i]=indices[i]+vertexOffset;
   vertexOffset+=p.count;indexOffset+=indices.length;
  }
  const record={...building,modelId:entry.modelId,modelGeometry:{position,index,triangles,worldBounds:entry.worldBounds},modelSource:{datasetId:entry.datasetId,modelId:entry.modelId,sourceTile:entry.sourceTile,sourceTileRevision:entry.sourceTileRevision,sha256:entry.sha256,catalogueURL:entry.catalogueURL,coordinatePolicy:entry.coordinatePolicy,originalMaterials:source.materials,originalNodes:source.nodes}};
  if(describeBuilding(record).modelStatus!=='usable')throw new Error('Official model does not fit its matched footprint');
  const style=buildingLighting(record),night=facadeMaterial('#ffffff',lighting),attachNight=night.onBeforeCompile,materialMap=new Map();night.dispose();
  for(const mesh of meshes){
   mesh.userData.officialBuildingUid=record.uid;mesh.castShadow=mesh.receiveShadow=true;
   const decorate=original=>{
    if(materialMap.has(original))return materialMap.get(original);
    const material=original.clone();material.onBeforeCompile=shader=>{
     attachNight(shader);
     // Per-building constants avoid expanding compact source geometry with
     // repeated facade attributes. The exact shared city window shader is reused.
     shader.uniforms.cityLight={value:new THREE.Vector4(style.seed,style.profile,style.base,style.retailTop)};
     shader.uniforms.cityWindows={value:record.structureType==='Open-sided Structure'||entry.proceduralWindows===false?0:1};
     shader.vertexShader=shader.vertexShader.replace('attribute vec4 cityLight;','uniform vec4 cityLight;').replace('attribute float cityWindows;','uniform float cityWindows;');
    };
    material.customProgramCacheKey=()=> 'official-city-facade-v1';materialMap.set(original,material);return material;
   };
   mesh.material=Array.isArray(mesh.material)?mesh.material.map(decorate):decorate(mesh.material);
  }
  for(const original of materialMap.keys())original.dispose();
  result={group,record,meshes,bounds,entry,budget:modelBudget(entry),active:false};group.visible=false;return result;
 }catch(error){disposeOfficialModel(result);throw error;}
}
