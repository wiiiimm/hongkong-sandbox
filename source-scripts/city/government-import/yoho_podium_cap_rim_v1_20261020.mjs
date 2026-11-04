/** Attribute every canonical podium low-rim contact failure; no waivers. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const [input,output]=process.argv.slice(2),data=JSON.parse(gunzipSync(readFileSync(input))),geo=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)}),surface=supportSurface(geo(data.ground)),rows=[];
for(const [mode,t]of Object.entries(data.worlds)){
 const g=geo(t),q=createSourceFaceQuery(g);let bottom=Infinity;for(const f of t)for(const p of f)bottom=Math.min(bottom,p[1]);
 const rim=lowRimSamples(g,bottom),proof=measureSupport(rim,surface),failed=proof.failed.map(x=>({...x,incidentFaces:q(x.position).map(f=>f.faceIndex)}));
 rows.push({mode,bottom,proof:{...proof,failed},allFailuresOnKnownBottomCap:failed.length>0&&failed.every(x=>x.reason==='support-above-rim'&&x.incidentFaces.some(i=>i===18215||i===18216)),installationApproved:false});
}
writeFileSync(output,JSON.stringify({rows,installationApproved:false}));console.log(JSON.stringify(rows.map(r=>({mode:r.mode,samples:r.proof.samples,contacts:r.proof.contacts,missing:r.proof.missing,failed:r.proof.failed.length,allFailuresOnKnownBottomCap:r.allFailuresOnKnownBottomCap}))));
