/** Full original component low-rim replay against all other unchanged source faces. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-miami-original-roof-attachment-20261009/';
const bytes=readFileSync(new URL(base+'complete-original-component-support-inputs.json.gz',root)),input=JSON.parse(gunzipSync(bytes)),rows=[];
for(const r of input.rows){const source=input.sources.find(s=>s.uid===r.uid),ids=new Set(r.originalFaceIds),supportOriginalFaceIds=Array.from({length:source.index.length/3},(_,i)=>i).filter(i=>!ids.has(i));
 const geometry=faces=>{const position=faces.flatMap(i=>source.position.slice(i*9,i*9+9));return {position,index:Array.from({length:position.length/3},(_,i)=>i)};};
 const result=verifySupportInterface(geometry(r.originalFaceIds),r.bottomHKPD,geometry(supportOriginalFaceIds));rows.push({uid:r.uid,component:r.component,sourceSHA256:r.sourceSHA256,sourceWorldTriangleSHA256:r.sourceWorldTriangleSHA256,originalFaceIds:r.originalFaceIds,supportOriginalFaceIds,originalWholeSourceRoofInterface:result,physicalAccepted:false,sourceGeometryChanges:0});}
writeFileSync(new URL(base+'complete-original-component-roof-support.json.gz',root),gzipSync(JSON.stringify({rows,inputSHA256:createHash('sha256').update(bytes).digest('hex'),physicalAccepted:false,sourceGeometryChanges:0})));
for(const uid of new Set(rows.map(r=>r.uid))){const parts=rows.filter(r=>r.uid===uid);console.log(JSON.stringify({uid,components:parts.length,ordinaryOriginalRoofInterfacePassed:parts.filter(r=>r.originalWholeSourceRoofInterface.passed).length,stillUnresolved:parts.filter(r=>!r.originalWholeSourceRoofInterface.passed).length}));}
