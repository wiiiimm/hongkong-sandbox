/** Diagnose source-authored support intersections; never modifies geometry or approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url);
const base='docs/astra-city/government-import/government-xl-remaining-forty-assembly-support-v1-20261021/';
const inputs=JSON.parse(readFileSync(new URL(base+'support-inputs.json',root)));
const checks=JSON.parse(gunzipSync(readFileSync(new URL(base+'support-checks.json.gz',root))));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const rows=[];
for(const prior of checks.rows.filter(r=>['landsd/198440:0','landsd/314698:0','landsd/278458:0'].includes(r.uid))){
 const source=inputs.sources.find(r=>r.uid===prior.supportUid);
 const raw=readFileSync(new URL(source.candidate.path,root));
 const model=await loadOfficialModel({...source.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},source.source.building,lighting,{fetcher:async()=>new Response(raw)});
 try{
  const query=createSourceFaceQuery(model.record.modelGeometry);
  const contacts=prior.unresolved.map(sample=>{
   const deckPosition=[sample.position[0],sample.position[1]-sample.gap,sample.position[2]];
   const supportFaces=query(deckPosition);assert(supportFaces.length,'Expected actual support face at reported deck');
   return {...sample,deckPosition,supportFaces};
  });
  rows.push({uid:prior.uid,supportUid:prior.supportUid,sourceSHA256:prior.sourceSHA256,supportSHA256:prior.supportSHA256,contacts});
 }finally{disposeOfficialModel(model);}
}
writeFileSync(new URL(process.argv[2],root),JSON.stringify({rows,installationApproved:false,physicalInterpretationAccepted:false,rawFailuresPreserved:true,sourceGeometryChanges:0},null,2)+'\n');
