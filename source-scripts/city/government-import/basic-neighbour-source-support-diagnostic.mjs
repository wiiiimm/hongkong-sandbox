/** Probe retained basic neighbours against original podium surfaces; no acceptance. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {supportSurface,measureSupport} from './support-contact.mjs';
import {inPolygon} from '../../../3d-viewer/city/geo.js';
const root=new URL('../../../',import.meta.url),[base,geometryPath,out]=process.argv.slice(2),hashes={},sha=r=>createHash('sha256').update(r).digest('hex');
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
assert(geometryPath?.startsWith('source-scripts/city/government-import/local/government-xl-')&&!geometryPath.includes('..'));
assert(out?.startsWith('source-scripts/city/government-import/local/government-xl-')&&!out.includes('..')&&!existsSync(new URL(out,root)));
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const geometry=read(geometryPath),inputs=read(base+'neighbour-inputs.json.gz'),checks=read(base+'neighbour-checks.json'),selection=read(base+'selection.json.gz');
assert.equal(geometry.rows.length,1);const source=geometry.rows[0],selected=selection.rows.find(r=>r.uid===source.uid);assert(selected);assert.equal(source.sourceSHA256,selected.sourceSHA256);
assert.equal(sha(readFileSync(new URL(selected.candidate.path,root))),source.sourceSHA256);hashes[selected.candidate.path]=source.sourceSHA256;
for(const [path,pinned] of Object.entries(inputs.inputHashes))assert.equal(sha(readFileSync(new URL(path,root))),pinned);
const surface=supportSurface(source),rows=[];
for(const check of checks.rows.filter(r=>!r.existingNative&&!r.candidate&&r.reasons.length)){
 const b=inputs.rows.find(r=>r.building.uid===check.uid).building,points=new Map(),baseHeight=b.base+(b.minimum||0),add=([x,z])=>points.set([x,z].map(v=>v.toFixed(5)).join(','),[x,baseHeight,z]);
 for(const ring of b.rings)for(let k=0;k<ring.length;k++){
  const a=ring[k],c=ring[(k+1)%ring.length];add(a);const n=Math.ceil(Math.hypot(a[0]-c[0],a[1]-c[1]));for(let j=1;j<n;j++)add(a.map((v,i)=>v+(c[i]-v)*j/n));
 }
 const xs=b.rings[0].map(v=>v[0]),zs=b.rings[0].map(v=>v[1]);for(let x=Math.min(...xs)+.5;x<Math.max(...xs);x++)for(let z=Math.min(...zs)+.5;z<Math.max(...zs);z++)if(inPolygon(x,z,b.rings))add([x,z]);
 const proof=measureSupport([...points.values()],surface);rows.push({uid:b.uid,name:b.name,sourceParent:b.parent,podiumParent:selected.source.building.parent,sameParent:b.parent===selected.source.building.parent,baseHeightHKPD:baseHeight,originalTerrainRegression:check,proof});console.log(JSON.stringify({uid:b.uid,samples:proof.samples,contacts:proof.contacts,missing:proof.missing,minGap:proof.minGap,maxGap:proof.maxGap}));
}
for(const path of ['source-scripts/city/government-import/basic-neighbour-source-support-diagnostic.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/geo.js'])hashes[path]=sha(readFileSync(new URL(path,root)));
for(const [path,pinned] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pinned);
mkdirSync(new URL('.',new URL(out,root)),{recursive:true});writeFileSync(new URL(out,root),JSON.stringify({uid:source.uid,sourceSHA256:source.sourceSHA256,rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,qualification:'Every footprint vertex, <=1m boundary samples and 1m interior samples at unchanged basic floor elevation against highest original source triangles. A positive sampled interface does not prove complete floor coverage or foundation; raw neighbour guards remain. No acceptance or geometry edits.'},null,2)+'\n');
