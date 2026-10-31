/** Preserve strict highest-surface results while inspecting original support layers. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {lowRimSamples,measureSupport,supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],hashes={};
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=createHash('sha256').update(raw).digest('hex');return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const input=read(dir+'input.json'),graph=read(input.graph),worlds=read(input.worlds),uids=Object.keys(worlds.original).sort(),tri=uids.flatMap(u=>worlds.original[u]);assert.equal(tri.length,13557);
const supportIds=graph.positiveContactReachableFromPodium.flatMap(i=>graph.components[i].globalFaces);
function geometry(ids){const position=ids.flatMap(i=>tri[i].flat());return {position,index:Array.from({length:position.length/3},(_,i)=>i)};}
const surface=supportSurface(geometry(supportIds)),rows=[];
for(const component of graph.unconnectedComponents){const body=graph.components[component],g=geometry(body.globalFaces);let bottom=Infinity;for(let i=1;i<g.position.length;i+=3)bottom=Math.min(bottom,g.position[i]);const rim=lowRimSamples(g,bottom),strict=measureSupport(rim,surface);const samples=rim.map(position=>{const hits=surface.intersectionDetails(position[0],position[2]).map(h=>{const [a,b,c]=h.vertices;const normalY=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]);return {...h,globalSourceFace:supportIds[h.faceIndex],gapM:position[1]-h.height,upward:normalY>0};});return {position,allOriginalHits:hits,contactLayers:hits.filter(h=>h.gapM>=-.1&&h.gapM<=1),upwardContactLayers:hits.filter(h=>h.upward&&h.gapM>=-.1&&h.gapM<=1)};});rows.push({component,uid:body.uid,faces:body.globalFaces.length,bottom,strict,samples});}
for(const p of ['source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/opus_component_layers_v1_20261017.mjs'])hashes[p]=createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex');
for(const [p,h]of Object.entries(hashes))assert.equal(createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex'),h);
const summary={rows:rows.map(r=>({component:r.component,faces:r.faces,bottom:r.bottom,samples:r.samples.length,strictHighestContacts:r.strict.contacts,anyContactLayer:r.samples.filter(x=>x.contactLayers.length).length,upwardContactLayer:r.samples.filter(x=>x.upwardContactLayers.length).length})),fullAcceptance:false,newlyInstalled:0};
writeFileSync(new URL(dir+'layers.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,qualification:'All lower layers retained separately; never overrides conservative highest-surface checks. No unsupported-source, identity, structural or publication decision.'})));writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
