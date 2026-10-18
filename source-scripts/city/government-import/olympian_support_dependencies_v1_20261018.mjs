import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {lowRimSamples,supportSurface} from './support-contact.mjs';
const dir=process.argv[2],input=JSON.parse(gunzipSync(readFileSync(dir+'/inputs.json.gz'))),providers=['landsd/265851:0','landsd/239351:0','landsd/72277:0'],rows=[];
const geo=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)});
for(const [mode,w] of Object.entries(input.worlds)){
 const surfaces=providers.map(uid=>({uid,surface:supportSurface(geo(w[uid]))}));
 const contacts=p=>surfaces.filter(s=>s.surface.intersections(p[0],p[2]).some(y=>p[1]-y>=-.1&&p[1]-y<=1)).map(s=>s.uid);
 for(const uid of input.targets){
  const t=w[uid],bottom=Math.min(...t.flat().map(p=>p[1])),rim=lowRimSamples(geo(t),bottom),paths=input.towerPaths.filter(x=>x.mode===mode&&x.uid===uid).map(x=>({position:x.position,contact:x.contact}));
  const park=input.parkContacts.find(x=>x.mode===mode&&x.uid===uid);
  for(const d of park?.details||[])if(d.path?.endpointPassed)paths.push({position:d.position,contact:d.path.original.witness.contact.point});
  const checks=[];
  for(const p of rim){let supportedBy=contacts(p),via='original-rim',endpoint=null;
   if(!supportedBy.length){const path=paths.find(x=>Math.hypot(...x.position.map((v,k)=>v-p[k]))<=.001);assert(path,uid+' '+mode+' missing accepted path');endpoint=path.contact;supportedBy=contacts(endpoint);via='previously-reviewed-original-face-path';}
   assert(supportedBy.length,uid+' '+mode+' no endpoint provider');checks.push({position:p,supportedBy,via,endpoint});
  }
  rows.push({uid,mode,checks});
 }
}
const dependencies={};for(const uid of input.targets){const checks=rows.filter(r=>r.uid===uid).flatMap(r=>r.checks);let chosen=null;for(let n=1;n<=3&&!chosen;n++)for(let mask=1;mask<8;mask++){const subset=providers.filter((_,i)=>mask&(1<<i));if(subset.length!==n)continue;if(checks.every(c=>c.supportedBy.some(u=>subset.includes(u)))){chosen=subset;break;}}assert(chosen);dependencies[uid]=chosen;}
writeFileSync(dir+'/provider-checks.json.gz',gzipSync(JSON.stringify({rows,dependencies,modelGeometryChanges:0})));console.log(JSON.stringify(dependencies));
