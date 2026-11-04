import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const dir=process.argv[2],d=JSON.parse(gunzipSync(readFileSync(dir+'/input.json.gz'))),rows=[];
const geometry=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)});
for(const [mode,world] of Object.entries(d.worlds))for(const [uid,tri]of Object.entries(world)){
 const target=geometry(tri),bottom=tri.reduce((b,t)=>Math.min(b,...t.map(v=>v[1])),Infinity),supportUids=uid==='landsd/322270:0'?['landsd/26195:0']:[];
 const supports=geometry([...d.terrain,...supportUids.flatMap(u=>world[u])]),proof=verifySupportInterface(target,bottom,supports),query=createSourceFaceQuery(target);
 const unresolved=proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)}));const reasons={};for(const f of unresolved)reasons[f.reason]=(reasons[f.reason]||0)+1;
 rows.push({uid,mode,bottom,supportUids,interface:proof,unresolved,reasons});console.log(JSON.stringify({uid,mode,passed:proof.passed,samples:proof.samples,unresolved:unresolved.length,reasons}));
}
writeFileSync(dir+'/checks.json.gz',gzipSync(JSON.stringify({rows,publication:false,modelGeometryChanges:0})));
