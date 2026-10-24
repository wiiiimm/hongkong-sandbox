/** Exact original companion versus unchanged Opus podium; diagnostic only. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {lowRimSamples,measureSupport,supportSurface,inspectSupportLayers} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const input=read(dir+'input.json'),actor=read(input.actorsPath),rows=read(input.geometryPath).rows;
const podium=rows.find(r=>r.uid==='landsd/248432:0');assert(actor&&podium);
const surface=supportSurface(podium),targets=[actor,rows.find(r=>r.uid==='landsd/322573:0')];assert(targets.every(Boolean));
const results=targets.map(g=>{let bottom=Infinity;for(const i of g.index)bottom=Math.min(bottom,g.position[i*3+1]);const rim=lowRimSamples(g,bottom),layers=inspectSupportLayers(rim,surface);return {uid:g.uid,bottom,layers};});
const summary={rows:results.map(r=>({uid:r.uid,bottom:r.bottom,samples:r.layers.conservative.samples,highestSurfaceContacts:r.layers.conservative.contacts,missing:r.layers.conservative.missing,lowerContactLayerSamples:r.layers.rows.filter(x=>x.contactHeights.length).length,failed:r.layers.rows.length})),fullAcceptance:false,sourceGeometryChanges:0};
writeFileSync(new URL(dir+'layers.json',root),JSON.stringify(results));writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
