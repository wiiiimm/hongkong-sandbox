/** Original podium layer diagnostics only; canonical highest-surface checks remain. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {lowRimSamples,supportSurface,inspectSupportLayers} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
const path='source-scripts/city/government-import/local/government-xl-oi-sin-four-originals-physical-v1-20261017/runtime-geometry.json.gz';
const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);const data=JSON.parse(gunzipSync(raw));
const support=data.rows.find(r=>r.uid==='landsd/91128:0'),surface=supportSurface(support),rows=[];
for(const source of data.rows.filter(r=>r.uid!==support.uid)){
 const ys=source.position.filter((_,i)=>i%3===1);const bottom=ys.reduce((a,b)=>Math.min(a,b),Infinity);
 const proof=inspectSupportLayers(lowRimSamples(source,bottom),surface);rows.push({uid:source.uid,sourceSHA256:source.sourceSHA256,supportSHA256:support.sourceSHA256,proof});
}
for(const p of ['source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/oi_sin_original_support_layers_v1_20261017.mjs'])hashes[p]=sha(readFileSync(new URL(p,root)));
const out=new URL('docs/astra-city/government-import/government-xl-oi-sin-original-support-layers-v1-20261017/layers.json',root);mkdirSync(new URL('.',out),{recursive:true});writeFileSync(out,JSON.stringify({rows,inputHashes:hashes,installationApproved:false}));
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,failed:r.proof.rows.length,lowerContact:r.proof.rows.filter(p=>p.classification==='contact-layer-with-higher-overlap').length}))));
