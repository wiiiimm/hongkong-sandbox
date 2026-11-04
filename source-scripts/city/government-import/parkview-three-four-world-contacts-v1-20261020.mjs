/** Exact original support sample accounting; no acceptance or geometry edits. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const path=process.argv[2],output=process.argv[3],raw=readFileSync(path),input=JSON.parse(gunzipSync(raw)),rows=[];
for(const r of input.rows){
 const proof=verifySupportInterface(r.source,Math.min(...r.source.position.filter((_,i)=>i%3===1)),r.support),query=createSourceFaceQuery(r.support);
 const mapped=proof.unresolved.map(p=>({...p,supportFacesAtOriginalPoint:query(p.position)}));
 const summary={uid:r.uid,mode:r.mode,samples:proof.samples,canonicalContacts:proof.strictContacts,canonicalResolvedWallContacts:proof.resolved.length,directOriginalFaceContacts:mapped.filter(p=>p.supportFacesAtOriginalPoint.length).length,stillUnresolved:mapped.filter(p=>!p.supportFacesAtOriginalPoint.length).length};
 rows.push({...summary,rawInterface:proof,mapped,sourceWorldSHA256:r.sourceWorldSHA256,supportWorldSHA256:r.supportWorldSHA256,installationApproved:false});console.log(JSON.stringify(summary));
}
const hashes={};for(const p of [path,'source-scripts/city/government-import/parkview-three-four-world-contacts-v1-20261020.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs'])hashes[p]=createHash('sha256').update(readFileSync(p)).digest('hex');
writeFileSync(output,gzipSync(JSON.stringify({rows,inputHashes:hashes,installationApproved:false,geometryChanges:0})));
