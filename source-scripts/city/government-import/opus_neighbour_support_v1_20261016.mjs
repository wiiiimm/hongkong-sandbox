/** Exact captured BASIC neighbour versus unchanged Opus podium; diagnostic only. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {lowRimSamples,measureSupport,supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const input=read(dir+'input.json'),actor=read(input.actorsPath).rows.find(r=>r.uid==='landsd/319559:0'),rows=read(input.geometryPath).rows;
const podium=rows.find(r=>r.uid==='landsd/248432:0');assert(actor&&podium);
const bottom=Math.min(...actor.index.map(i=>actor.position[i*3+1]));
const result=measureSupport(lowRimSamples(actor,bottom),supportSurface(podium));
const summary={uid:actor.uid,supportUid:podium.uid,bottom,sourceFaces:podium.index.length/3,samples:result.samples,contacts:result.contacts,missing:result.missing,minGap:result.minGap,maxGap:result.maxGap,allSampledContactsPass:result.allSampledContactsPass,fullAcceptance:false};
writeFileSync(new URL(dir+'support.json',root),JSON.stringify(result));writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
