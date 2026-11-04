/** Attribute every remaining sample to exact source faces and other original actors. No acceptance. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {createSourceFaceQuery} from './source-face-query.mjs';
import {supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],out=process.argv[3];
assert(base.startsWith('docs/')&&out.startsWith('docs/')&&!base.includes('..')&&!out.includes('..'));
const read=p=>JSON.parse(gunzipSync(readFileSync(new URL(p,root)))),rows=[];
for(const mode of ['original','literal','left','balanced']){
 const input=read(`${base}/${mode}/input.json.gz`),prior=read(`${base}/${mode}/support.json.gz`);
 const queries=new Map(input.rows.map(r=>[r.uid,createSourceFaceQuery(r)]));
 const surfaces=new Map(input.rows.map(r=>[r.uid,supportSurface(r)]));
 for(const r of prior.rows){
  const samples=r.proof.unresolved.map(f=>{
   const faces=queries.get(r.uid)(f.position);assert(faces.length);
   const actorHits=[...surfaces].filter(([uid])=>uid!==r.uid).map(([uid,s])=>({uid,hits:s.intersectionDetails(f.position[0],f.position[2]).map(h=>({...h,gap:f.position[1]-h.height}))})).filter(a=>a.hits.length);
   const candidates=actorHits.flatMap(a=>a.hits.filter(h=>h.gap>=-.1&&h.gap<=1).map(h=>({uid:a.uid,...h})));
   return {...f,sourceFaces:faces,otherOriginalActorHits:actorHits,additionalWithinStrictInterval:candidates};
  });
  rows.push({mode,uid:r.uid,strictContacts:r.proof.strictContacts,samples:r.proof.samples,unresolved:samples});
 }
}
writeFileSync(new URL(out,root),gzipSync(JSON.stringify({rows,fullAcceptance:false,qualification:'Exact historical complete assembly geometry only. Candidate contacts are not approval, ownership, or an acyclic runtime support dependency.'})));
for(const r of rows)console.log(JSON.stringify({mode:r.mode,uid:r.uid,unresolved:r.unresolved.length,otherActorContactCandidates:r.unresolved.filter(x=>x.additionalWithinStrictInterval.length).length,reasons:Object.fromEntries([...new Set(r.unresolved.map(x=>x.reason))].map(k=>[k,r.unresolved.filter(x=>x.reason===k).length]))}));
