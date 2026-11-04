/** Diagnose mixed ground/podium support; do not grant acceptance or change assets. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const input=process.argv[2],output=process.argv[3],geometry=JSON.parse(gunzipSync(readFileSync(input))).rows,g=new Map(geometry.map(r=>[r.uid,r])),pod=g.get('landsd/254491:0'),rows=[];
for(const uid of ['landsd/256113:0','landsd/255917:0','landsd/255646:0']){
 const source=g.get(uid),position=source.drawnGroundGeometry.flat(Infinity),ground={position,index:Array.from({length:position.length/3},(_,i)=>i)},offset=ground.position.length/3;
 const support={position:ground.position.concat(pod.position),index:ground.index.concat(pod.index.map(i=>i+offset))};
 let bottom=Infinity;for(let i=1;i<source.position.length;i+=3)bottom=Math.min(bottom,source.position[i]);
 const proof=verifySupportInterface(source,bottom,support),groundQuery=createSourceFaceQuery(ground),podQuery=createSourceFaceQuery(pod);
 const mapped=proof.unresolved.map(p=>({...p,groundFaces:groundQuery(p.position),podiumFaces:podQuery(p.position)}));
 const summary={uid,samples:proof.samples,strictContacts:proof.strictContacts,resolvedWallContacts:proof.resolved.length,rawUnresolved:proof.unresolved.length,directOriginalFaceContacts:mapped.filter(p=>p.groundFaces.length||p.podiumFaces.length).length,stillUnresolved:mapped.filter(p=>!p.groundFaces.length&&!p.podiumFaces.length).length,groundTriangles:ground.index.length/3};
 rows.push({...summary,rawInterface:proof,mapped,sourceSHA256:source.sourceSHA256,installationApproved:false});console.log(JSON.stringify(summary));
}
const inputHashes={};for(const p of [input,'source-scripts/city/government-import/parkview-mixed-support-v1-20261020.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs'])inputHashes[p]=createHash('sha256').update(readFileSync(p)).digest('hex');
writeFileSync(output,gzipSync(JSON.stringify({rows,inputHashes,installationApproved:false,geometryChanges:0})));
