import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const dir=process.argv[2],data=JSON.parse(gunzipSync(readFileSync(dir+'/geometry-inputs.json.gz')));
const supports=data.rows.filter(r=>!data.towerUIDs.includes(r.uid));
const combined={position:[],index:[]};
for(const s of supports){const offset=combined.position.length/3;for(const p of s.position)combined.position.push(p);for(const i of s.index)combined.index.push(i+offset);}
const rows=[];
for(const s of data.rows.filter(r=>data.towerUIDs.includes(r.uid))){
 const proof=verifySupportInterface(s,s.bottom,combined),query=createSourceFaceQuery(s);
 const unresolved=proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)}));
 const reasons={};for(const f of unresolved)reasons[f.reason]=(reasons[f.reason]||0)+1;
 rows.push({uid:s.uid,sourceSHA256:s.sourceSHA256,interface:proof,unresolved,reasons,installationApproved:false});
 console.log(JSON.stringify({uid:s.uid,passed:proof.passed,samples:proof.samples,contacts:proof.strictContacts,wallIntersections:proof.wallIntersections,reasons}));
}
writeFileSync(dir+'/support-checks.json.gz',gzipSync(JSON.stringify({rows,supports:supports.map(s=>({uid:s.uid,sha256:s.sourceSHA256})),modelGeometryChanges:0,publication:false,qualification:'Canonical interface rules on exact decoded original geometry. Diagnostic only; production renderer, identity, terrain and foundation acceptance still required.'})));
