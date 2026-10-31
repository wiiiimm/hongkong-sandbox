/** Private source-preserving inset into one exact installed native terrain surface. */
import{readFileSync,writeFileSync,mkdirSync}from'node:fs';import{gzipSync}from'node:zlib';import{createHash}from'node:crypto';import assert from'node:assert/strict';
import{makeTerrain}from'../../../3d-viewer/city/world.js';import{retainOutsideInset}from'./retained_terrain_inset_clip_v1.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outPath=process.argv[3],pins={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function load(path){assert(!path.includes('..'));const b=readFileSync(new URL(path,root));pins[path]=sha(b);return JSON.parse(b);}
assert(inputPath?.startsWith('docs/astra-city/government-import/')&&outPath?.startsWith('source-scripts/city/government-import/local/'));
const input=load(inputPath);for(const r of input.refs)assert.equal(sha(readFileSync(new URL(r.path,root))),r.sha256);
const old=load(input.parent.path),inset=load(input.inset.path);assert.equal(pins[input.parent.path],input.parent.sha256);assert.equal(pins[input.inset.path],input.inset.sha256);assert(old.nativeMesh&&!old.patches?.length&&inset.nativeMesh);
const terrain=makeTerrain(old);terrain.updateMatrixWorld(true);assert(terrain.isMesh);const p=terrain.geometry.attributes.position,idx=terrain.geometry.index;const faces=[],lineage=[];let originalFaces=0,unchanged=0;
for(let i=0;i<idx.count;i+=3){const f=[0,1,2].map(k=>{const j=idx.getX(i+k);return[p.getX(j),p.getY(j),p.getZ(j)];});const parts=retainOutsideInset(f,input.bounds,input.cut);if(parts.length===1&&parts[0]===f)unchanged++;for(const t of parts){faces.push(t);lineage.push({kind:'retained-current-source',originalFace:i/3,originalVertices:f});}originalFaces++;}
const q=inset.nativeMesh.position,n=inset.nativeMesh.index;let minimumInsetHeight=Infinity;
for(let i=0;i<n.length;i+=3){const f=[0,1,2].map(k=>q.slice(n[i+k]*3,n[i+k]*3+3));for(const[x,y,z]of f){assert(Number.isFinite(x)&&Number.isFinite(y)&&Number.isFinite(z));assert(x>=input.cut[0]-.002&&x<=input.cut[2]+.002&&z>=input.cut[1]-.002&&z<=input.cut[3]+.002);minimumInsetHeight=Math.min(minimumInsetHeight,y);}faces.push(f);lineage.push({kind:'verified-bounded-original-inset',insetFace:i/3});}
assert(minimumInsetHeight>=1.2,'New inset below unchanged native clamp');
const candidate=structuredClone(old);candidate.meta.targetUids=[...new Set([...old.meta.targetUids,...input.uids])].sort();candidate.nativeMesh.position=faces.flat(2);candidate.nativeMesh.index=Array.from({length:faces.length*3},(_,i)=>i);delete candidate.nativeMesh.sourceOverlap;
for(const key of['numericalCoverageGap','numericalProjectionOverlap'])delete candidate.nativeMesh.source[key];
const policy='Exact current rendered native surface retained outside explicit bounded original inset; all current source faces accounted for. Existing terrain grid/water/vegetation and original building geometry unchanged. Private proposal; all physical/current-neighbour/browser/publication checks remain mandatory.';
candidate.meta.source={...candidate.meta.source,policy,retainedNativeSurface:input.parent,boundedOriginalInset:input.inset};candidate.nativeMesh.source={...candidate.nativeMesh.source,policy,retainedNativeSurface:input.parent,boundedOriginalInset:input.inset};
for(const path of['source-scripts/city/government-import/selected_retained_native_inset_v1.mjs','source-scripts/city/government-import/retained_terrain_inset_clip_v1.mjs','source-scripts/city/government-import/clip_parent_terrain_triangle_v1.mjs','3d-viewer/city/world.js','3d-viewer/city/native-terrain.js','3d-viewer/city/native-terrain-depth.js','3d-viewer/city/geo.js'])pins[path]=sha(readFileSync(new URL(path,root)));
for(const[path,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(path,root))),h);
const out=new URL(outPath,root);mkdirSync(new URL('./',out),{recursive:true});writeFileSync(out,JSON.stringify(candidate));writeFileSync(new URL(input.lineage,root),gzipSync(JSON.stringify({originalFaces,unchangedFaces:unchanged,outputFaces:faces.length,insetFaces:n.length/3,minimumInsetHeight,lineage,inputHashes:pins,sourceGeometryChanges:0,installationApproved:false})));
terrain.geometry.dispose();terrain.material.dispose();console.log(JSON.stringify({originalFaces,unchangedFaces:unchanged,outputFaces:faces.length,minimumInsetHeight}));
