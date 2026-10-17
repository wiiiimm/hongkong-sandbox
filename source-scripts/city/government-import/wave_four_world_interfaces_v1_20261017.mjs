/** Re-run unchanged strict support sampling in all complete source worlds. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {createSourceFaceQuery} from './source-face-query.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),input=process.argv[2],out=process.argv[3];assert(input.startsWith('docs/')&&out.startsWith('docs/')&&!input.includes('..')&&!out.includes('..'));
const raw=readFileSync(new URL(input,root)),worlds=JSON.parse(gunzipSync(raw)),rows=[];
for(const [mode,world] of Object.entries(worlds)){
 const geometry=uid=>{const position=world[uid].flat(2);return {position,index:Array.from({length:position.length/3},(_,i)=>i)};},support=geometry('landsd/301560:0');
 for(const uid of Object.keys(world).filter(u=>u!=='landsd/301560:0')){
  const source=geometry(uid),bottom=world[uid].reduce((m,t)=>Math.min(m,...t.map(v=>v[1])),Infinity),proof=verifySupportInterface(source,bottom,support),query=createSourceFaceQuery(source);
  rows.push({mode,uid,proof,unresolved:proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)}))});
 }
}
const paths=[input,'source-scripts/city/government-import/wave_four_world_interfaces_v1_20261017.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs'];
const inputHashes=Object.fromEntries(paths.map(p=>[p,createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex')]));writeFileSync(new URL(out,root),JSON.stringify({rows,inputHashes,fullAcceptance:false})+'\n');console.log(rows.map(r=>({mode:r.mode,samples:r.proof.samples,unresolved:r.proof.unresolved.length})));
