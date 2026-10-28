/** Attribute existing strict samples to complete source/ground support facets. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
const read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(p)):readFileSync(p));
const [inputPath,summaryPath,contactPath,outputPath]=process.argv.slice(2);
const input=read(inputPath),summary=read(summaryPath),prior=read(contactPath),rows=[];
const digest=a=>createHash('sha256').update(Buffer.from(new Float64Array(a).buffer)).digest('hex');
for(const r of input.rows){
 assert(r.source.index.every((v,i)=>v===i)&&r.support.index.every((v,i)=>v===i));
 assert.equal(digest(r.source.position),r.sourceWorldSHA256);assert.equal(digest(r.support.position),r.supportWorldSHA256);
 const old=prior.rows.find(p=>p.uid===r.uid&&p.mode===r.mode);assert(old);
 const rim=lowRimSamples(r.source,r.sourceMinimumY),surface=supportSurface(r.support),proof=measureSupport(rim,surface);
 assert.deepEqual(proof,old.rawInterface.strictLowRim,'Strict witness generation or measurements changed');
 const roster=summary.supportRosters[r.uid];assert(roster.length);
 let offset=0;for(const part of roster){assert.equal(part.sourceFaceRange[0],offset);offset=part.sourceFaceRange[1];assert(offset>part.sourceFaceRange[0]);assert.notEqual(part.uid,r.uid);}
 assert.equal(offset,r.support.index.length/3);
 const provider=i=>{const part=roster.find(p=>i>=p.sourceFaceRange[0]&&i<p.sourceFaceRange[1]);assert(part);return {kind:part.kind||'other-original',uid:part.uid??null,supportFace:i,localFace:i-part.sourceFaceRange[0]};};
 const strict=[];
 for(const position of rim){
  const hits=surface.intersectionDetails(position[0],position[2]);if(!hits.length)continue;
  const height=hits.at(-1).height,gap=position[1]-height;
  if(gap<proof.minimumGap||gap>proof.maximumGap)continue;
  const top=hits.filter(h=>h.height===height);assert(top.length);
  strict.push({position,supportHeight:height,gap,providers:top.map(h=>({...provider(h.faceIndex),barycentric:h.barycentric}))});
 }
 assert.equal(strict.length,old.canonicalContacts);
 rows.push({uid:r.uid,mode:r.mode,sourceWorldSHA256:r.sourceWorldSHA256,supportWorldSHA256:r.supportWorldSHA256,strictSamples:strict,structuralRootAccepted:false});
 console.log(JSON.stringify({uid:r.uid,mode:r.mode,strictSamples:strict.length}));
}
const hashes={};for(const p of [inputPath,summaryPath,contactPath,'source-scripts/city/government-import/current_support_provenance_v1_20261028.mjs','source-scripts/city/government-import/support-contact.mjs'])hashes[p]=createHash('sha256').update(readFileSync(p)).digest('hex');
writeFileSync(outputPath,gzipSync(JSON.stringify({rows,inputHashes:hashes,geometryChanges:0,structuralRootsAccepted:false,installationApproved:false})));
