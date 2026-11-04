/** UNEXECUTED read-only current terrain union; no constructor or model load. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3],hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
assert(inputPath?.startsWith('docs/astra-city/government-import/')&&outputPath?.startsWith('docs/astra-city/government-import/')&&!existsSync(new URL(outputPath,root)));
function bytes(p,expected){const url=new URL(p,root);assert(url.pathname.startsWith(root.pathname));const raw=readFileSync(url);if(expected!==undefined)assert.equal(sha(raw),expected);hashes[p]=sha(raw);return raw;}
const worldURL=new URL('3d-viewer/city/world.js',root),closure=snapshotModuleClosure(worldURL,root);
Object.assign(hashes,closure.inputHashes);
for(const p of ['source-scripts/city/government-import/xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-union-v1.mjs','source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs'])bytes(p);
const input=JSON.parse(gunzipSync(bytes(inputPath)));
assert.equal(input.currentManifest.sha256,'2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540');
const manifest=JSON.parse(bytes(input.currentManifest.path,input.currentManifest.sha256));
for(const pin of input.evidenceRefs)bytes(pin.path,pin.sha256);
assert.deepEqual(input.currentCatalogueRefs.map(p=>p.path),manifest.officialModelCatalogues.map(p=>'3d-viewer/'+p));
assert.deepEqual(input.currentTileRefs.map(p=>p.path),manifest.tiles.map(t=>'3d-viewer/'+t.url));
for(const pin of [...input.currentCatalogueRefs,...input.currentTileRefs])bytes(pin.path,pin.sha256);
const data=JSON.parse(bytes('3d-viewer/city/data/terrain.json'));
data.patches=manifest.terrainPatches.map(p=>JSON.parse(bytes('3d-viewer/'+p.url)));
const {makeTerrain}=await import(worldURL.href),THREE=await import(new URL('3d-viewer/vendor/three.module.js',root).href);
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);
const bounds=input.completeCaptureBounds;assert(bounds.length===4&&bounds.every(Number.isFinite)&&bounds[0]<bounds[2]&&bounds[1]<bounds[3]);
const ground=[],layers=[],identity=new THREE.Matrix4();let layerID=0;
function attribute(a){return a?{count:a.count,itemSize:a.itemSize,arrayType:a.array.constructor.name,sha256:sha(Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength))}:null;}
try{terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.equals(identity),'Unexpected current terrain transform');
 const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
 assert(n%3===0&&p.itemSize===3);const selected=[];
 for(let i=0;i<n;i+=3){const a=idx?idx.getX(i):i,b=idx?idx.getX(i+1):i+1,c=idx?idx.getX(i+2):i+2;
  const x=[p.getX(a),p.getX(b),p.getX(c)],z=[p.getZ(a),p.getZ(b),p.getZ(c)];
  const outside=Math.max(...x)<bounds[0]||Math.min(...x)>bounds[2]||Math.max(...z)<bounds[1]||Math.min(...z)>bounds[3];
  if(outside)continue;
  const values=[x[0],p.getY(a),z[0],x[1],p.getY(b),z[1],x[2],p.getY(c),z[2]];assert(values.every(Number.isFinite));
  const unionFacetID=ground.length/9;for(const value of values)ground.push(value);
  selected.push({unionFacetID,originalDrawnLayerFacetID:i/3,originalDrawnVertexIndices:[a,b,c]});
 }
 layers.push({layerID:layerID++,name:mesh.name,matrixWorldFloat64:Array.from(mesh.matrixWorld.elements),
  completeDrawnTriangles:n/3,completePOSITION:attribute(p),completeIndex:attribute(idx),completeNormal:attribute(mesh.geometry.attributes.normal),completeColor:attribute(mesh.geometry.attributes.color),
  selectedFacets:selected,strictlyClosedBoxSeparatedFacets:n/3-selected.length});
});}finally{terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});}
assert(ground.length>0&&ground.length%9===0);
assert(verifyModuleClosure(closure,root));for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);
const worldBytes=Buffer.from(new Float64Array(ground).buffer);
writeFileSync(new URL(outputPath,root),gzipSync(JSON.stringify({completeCaptureBounds:bounds,drawnGroundGeometry:ground,
 completeCapturedDrawnTriangles:ground.length/9,completeCapturedFloat64WorldSHA256:sha(worldBytes),layers,inputHashes:hashes,
 completeRecursiveWorldModuleClosure:closure,startEndAllInputsVerified:true,everyCurrentTerrainLayerTraversed:true,
 omittedFacetsStrictlyOutsideCompleteCaptureBounds:true,terrainConstruction:false,currentAcceptance:false,nativeReacceptance:false})));
console.log(JSON.stringify({completeCapturedDrawnTriangles:ground.length/9,completeTraversedLayers:layers.length,currentAcceptance:false}));
