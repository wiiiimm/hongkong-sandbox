/** Continuation support evidence; original meshes, no publication or AI calls. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {lowRimSamples,supportSurface,measureSupport,inspectSupportLayers} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),hash=b=>createHash('sha256').update(b).digest('hex'),inputHashes={};
const bytes=p=>{const b=readFileSync(new URL(p,root));inputHashes[p]=hash(b);return b;},read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(bytes(p)):bytes(p));
const base='docs/astra-city/government-import/government-xl-remaining-20260923/',packet=read(base+'sol-pilot-20261002/packet.json'),available=new Map();
for(const dir of ['government-xl-remaining-20260923','government-xl-remaining-held-20260923']){
 const prefix='source-scripts/city/government-import/local/'+dir+'/recovered/',cat=read(prefix+'catalogue.json');
 for(const e of cat.models)available.set(e.uid,{entry:{rootTranslation:cat.rootTranslation,...e},path:prefix+e.asset,state:'candidate'});
}
for(const p of [base+'beverly-hill-pair-terrain-diagnostic-20260928/selection.json.gz',base+'beverly-hill-pair-terrain-diagnostic-20260928/support-selection.json.gz'])for(const r of read(p).rows)available.set(r.uid,{...r.candidate,state:'candidate'});
const manifest=read('3d-viewer/city/data/manifest.json'),forms=new Map();
for(const t of manifest.tiles)for(const b of read('3d-viewer/'+t.url).buildings)forms.set(b.uid,b);
for(const url of manifest.officialModelCatalogues){const cat=read('3d-viewer/'+url),prefix='3d-viewer/'+url.slice(0,url.lastIndexOf('/')+1);for(const e of cat.models)available.set(e.uid,{entry:{rootTranslation:cat.rootTranslation,...e},path:prefix+e.asset,state:'installed'});}
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
async function geometry(uid,override){const source=override||available.get(uid);assert(source&&forms.has(uid),'Missing source '+uid);const raw=source.path.startsWith('/')?readFileSync(source.path):bytes(source.path);assert.equal(hash(raw),source.entry.sha256);const model=await loadOfficialModel({...source.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},forms.get(uid),lighting,{fetcher:async()=>new Response(raw)});try{return {source,g:model.record.modelGeometry};}finally{disposeOfficialModel(model);}}
const recoveredSupport=read('source-scripts/city/government-import/local/sol-continuation-20261003/support-runtime.json.gz').rows[0];
if(!available.has(recoveredSupport.uid))available.set(recoveredSupport.uid,{...recoveredSupport.candidate,state:'candidate'});
function componentSupport(g,bottom,surface){
 const count=g.index.length/3,parent=Array.from({length:count},(_,i)=>i),find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;},seen=new Map();
 for(let f=0;f<count;f++)for(let k=0;k<3;k++){const v=g.index[f*3+k],key=Array.from(g.position.slice(v*3,v*3+3)).map(n=>n.toFixed(4)).join(',');if(seen.has(key))parent[find(f)]=find(seen.get(key));else seen.set(key,f);}
 const groups=new Map();for(let f=0;f<count;f++){const id=find(f);if(!groups.has(id))groups.set(id,[]);groups.get(id).push(...g.index.slice(f*3,f*3+3));}
 return [...groups.values()].map(index=>{const rim=lowRimSamples({position:g.position,index},bottom);return {triangles:index.length/3,...measureSupport(rim,surface)};}).filter(r=>r.samples).map(({failed,...r})=>r).sort((a,b)=>b.samples-a.samples);
}
const pairs=[['landsd/104302:0','landsd/91827:0'],['landsd/255917:0','landsd/254491:0'],['landsd/255647:0','landsd/254491:0'],['landsd/255539:0','landsd/233218:0'],['landsd/273839:0','landsd/175935:0']],rows=[];
for(const [uid,supportUid] of pairs){assert(packet.uids.includes(uid));const tower=await geometry(uid),support=await geometry(supportUid),rim=lowRimSamples(tower.g,tower.source.entry.worldBounds[0][1]),surface=supportSurface(support.g),measured=measureSupport(rim,surface),layers=inspectSupportLayers(rim,surface);rows.push({uid,supportUid,sourceSHA256:tower.source.entry.sha256,supportSHA256:support.source.entry.sha256,supportState:support.source.state,...measured,layers,components:componentSupport(tower.g,tower.source.entry.worldBounds[0][1],surface)});}
for(const p of ['source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/sol-support-contact-20261003.mjs','3d-viewer/city/official-model-assets.js'])bytes(p);

function trianglesHash(g){const rows=[];for(let i=0;i<g.index.length;i+=3){const vs=[0,1,2].map(k=>Array.from(g.position.slice(g.index[i+k]*3,g.index[i+k]*3+3)));const rotations=[0,1,2].map(k=>JSON.stringify([...vs.slice(k),...vs.slice(0,k)]));rows.push(rotations.sort()[0]);}return hash(Buffer.from(rows.sort().join('\n')));}
const installedSupport=await geometry(recoveredSupport.uid),recoveredGeometry=await geometry(recoveredSupport.uid,{...recoveredSupport.candidate,state:'recovered-original'}),equivalence={uid:recoveredSupport.uid,installedSHA256:installedSupport.source.entry.sha256,recoveredSHA256:recoveredGeometry.source.entry.sha256,installedTrianglesSHA256:trianglesHash(installedSupport.g),recoveredTrianglesSHA256:trianglesHash(recoveredGeometry.g),scope:'Exact world-coordinate triangle equality including winding, independent of mesh packing and primitive order; no geometry edits.'};equivalence.equal=equivalence.installedTrianglesSHA256===equivalence.recoveredTrianglesSHA256;assert(equivalence.equal,'Recovered support differs from installed geometry');

const report={supportEquivalence:equivalence,method:'Every unique source vertex in the lowest 0.35m and low-rim edge samples at <=1m spacing tested against highest exact vertically intersected support triangle. Conservative sampled diagnostic, not complete surface/contact proof.',rows,inputHashes,aiCalls:0,modelGeometryChanges:0,publication:false};writeFileSync(new URL(base+'sol-continuation-20261003/support-contact.json',root),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(rows.map(({failed,layers,components,...r})=>({...r,componentsAtLowRim:components.length,componentsWithAnyContact:components.filter(c=>c.contacts>0).length,layerReasons:layers.rows.reduce((a,r)=>(a[r.classification]=(a[r.classification]||0)+1,a),{})})),null,2));
