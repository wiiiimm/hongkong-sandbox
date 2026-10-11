/** Actual source triangle support diagnostics. No membership inference or model edits. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),doc='docs/astra-city/government-import/government-200-20260911/',read=p=>{const b=readFileSync(new URL(p,root));return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);},hash=b=>createHash('sha256').update(b).digest('hex');
const sources=read('source-scripts/city/government-import/local/government-198-resolution-20260911/support/geometry-inputs.json'),previous=read(doc+'pending-context/results.json.gz'),geometry=new Map(read('source-scripts/city/government-import/local/government-200-20260911-pending-context-v1/geometry.json.gz').rows.map(r=>[r.uid,r])),surfaces=new Map(),errors=[];
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
for(const r of sources.rows){let model;try{const raw=readFileSync(r.candidate.path);assert.equal(hash(raw),r.candidate.entry.sha256);model=await loadOfficialModel({...r.candidate.entry,assetURL:'https://validation.invalid/model.glb.gz'},r.building,lighting,{fetcher:async()=>new Response(raw)});surfaces.set(r.uid,{sourceSHA256:r.candidate.entry.sha256,surface:nativeTerrainSurface({position:Array.from(model.record.modelGeometry.position),index:Array.from(model.record.modelGeometry.index)})});}catch(e){errors.push({uid:r.uid,error:e.message});}finally{disposeOfficialModel(model);}}
const rows=[];
for(const r of previous.rows){
 const g=geometry.get(r.uid),p=g.position;let bottom=Infinity;for(let i=1;i<p.length;i+=3)bottom=Math.min(bottom,p[i]);const low=[];for(let i=0;i<p.length;i+=3)if(p[i+1]<=bottom+.35)low.push(p.slice(i,i+3));
 const hints=r.overlappingFootprintHints.map(n=>{const src=surfaces.get(n.uid);if(!src)return{uid:n.uid,state:'native-support-unavailable'};let covered=0,contact=0,minGap=Infinity,maxGap=-Infinity;for(const [x,y,z] of low){const h=src.surface.height(x,z);if(h===null)continue;covered++;const gap=y-h;minGap=Math.min(minGap,gap);maxGap=Math.max(maxGap,gap);if(gap>=-.1&&gap<=.1)contact++;}return{uid:n.uid,sourceSHA256:src.sourceSHA256,state:'source-triangles-checked',lowRimSamples:low.length,covered,contactWithin01m:contact,gapRange:covered?[minGap,maxGap]:null,completeLowRimContact:covered===low.length&&contact===low.length};});
 rows.push({uid:r.uid,hints,supportAccepted:false,qualification:'Highest actual source triangle at each low-rim point, not footprint overlap. Even complete sampled contact does not establish source assembly membership or validate the companion model.'});
}
writeFileSync(new URL(doc+'resolution/support-triangle-checks.json',root),JSON.stringify({models:rows.length,sourceModelsLoaded:surfaces.size,sourceErrors:errors,rows,aiCalls:0,publication:false},null,2)+'\n');
console.log(JSON.stringify({models:rows.length,sourceModelsLoaded:surfaces.size,errors:errors.length,completeContactHints:rows.flatMap(r=>r.hints).filter(r=>r.completeLowRimContact).length}));
