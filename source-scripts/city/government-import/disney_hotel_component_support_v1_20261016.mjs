/** Check the complete low component against the rest of its unchanged source. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {supportSurface,lowRimSamples,inspectSupportLayers} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const input=read(dir+'input.json'),context=read(input.contextPath),g=read(input.geometryPath).rows[0],selected=new Set(context.faceIds),inside=[],outside=[];
for(let i=0;i<g.index.length;i+=3)(selected.has(i/3)?inside:outside).push(...g.index.slice(i,i+3));
assert.equal(inside.length/3,74);assert.equal(outside.length/3,15425-74);
const bottom=context.summary.bounds[0][1],rim=lowRimSamples({position:g.position,index:inside},bottom),surface=supportSurface({position:g.position,index:outside});
const layers=inspectSupportLayers(rim,surface),rows=rim.map(position=>({position,hits:surface.intersectionDetails(position[0],position[2]).map(h=>({...h,sourceFace:Math.floor(outside[h.faceIndex*3]/3),gapM:position[1]-h.height}))}));
// Map the support-local triangle index back to the original source triangle index.
const outsideIds=Array.from({length:g.index.length/3},(_,i)=>i).filter(i=>!selected.has(i));
for(const r of rows)for(const h of r.hits)h.sourceFace=outsideIds[h.faceIndex];
const summary={sourceFaces:15425,componentFaces:74,otherSourceFaces:outside.length/3,rimSamples:rim.length,strictContacts:layers.conservative.contacts,missing:layers.conservative.missing,anyLayerContacts:rows.filter(r=>r.hits.some(h=>h.gapM>=-.1&&h.gapM<=1)).length,fullAcceptance:false};
writeFileSync(new URL(dir+'support-context.json.gz',root),gzipSync(JSON.stringify({summary,layers,rows})));writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
