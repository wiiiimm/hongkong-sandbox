/** Complete unchanged original nine-source contact census, no gate waivers. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-miami-fourteen-original-current-diagnostic-20261009/';
const raw=readFileSync(new URL(base+'complete-fourteen-original-contact-inputs.json.gz',root)),inp=JSON.parse(gunzipSync(raw));
const hash=x=>createHash('sha256').update(x).digest('hex');
for(const r of [...inp.rows,inp.terrain])assert.equal(hash(Buffer.from(new Float64Array(r.position).buffer)),r.worldTriangleSHA256);
const terrain=supportSurface(inp.terrain),podium=inp.rows.find(r=>r.uid==='landsd/232089:0'),podiumSurface=supportSurface(podium),results=[];
for(const source of inp.rows){
 const bottom=source.worldBounds[0][1],rim=lowRimSamples(source,bottom),ground=measureSupport(rim,terrain),support=measureSupport(rim,podiumSurface);
 const independentPodiumInterfaces=inp.rows.filter(r=>['landsd/232089:0','landsd/259038:0','landsd/231147:0'].includes(r.uid)&&r.uid!==source.uid).map(r=>({uid:r.uid,interface:verifySupportInterface(source,bottom,r)}));
 const originalPodiumInterface=source.uid===podium.uid?null:verifySupportInterface(source,bottom,podium);
 const originalGroundInterface=verifySupportInterface(source,bottom,inp.terrain);
 const row={uid:source.uid,sourceSHA256:source.sourceSHA256,sourceWorldTriangleSHA256:source.worldTriangleSHA256,bottomHKPD:bottom,wholeGroundContact:ground,wholePodiumContact:source.uid===podium.uid?null:support,originalPodiumInterface,independentPodiumInterfaces,originalGroundInterface,physicalAccepted:false,installationApproved:false,geometryChanges:0};results.push(row);
 console.log(JSON.stringify({uid:source.uid,rim:rim.length,groundContacts:ground.contacts,groundFailures:ground.failed.length,podiumContacts:source.uid===podium.uid?null:support.contacts,podiumFailures:source.uid===podium.uid?null:support.failed.length,originalPodiumInterfacePassed:originalPodiumInterface?.passed,originalGroundInterfacePassed:originalGroundInterface.passed,groundWallIntersections:originalGroundInterface.wallIntersections,podiumInterfaces:independentPodiumInterfaces.map(r=>({uid:r.uid,passed:r.interface.passed,samples:r.interface.samples,strict:r.interface.strictContacts,unresolved:r.interface.unresolved.length}))}));
}
writeFileSync(new URL(base+'all-fourteen-original-ground-podium-contact.json.gz',root),gzipSync(JSON.stringify({rows:results,inputSHA256:hash(raw),terrainWorldTriangleSHA256:inp.terrain.worldTriangleSHA256,geometryChanges:0,physicalAccepted:false,installationApproved:false})));
