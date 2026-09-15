/** Measure unchanged V City assembly contact using the production model loader. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {nearest} from '../assembly-support-review/triangles.mjs';

const root=new URL('../../../',import.meta.url);
const read=p=>JSON.parse(readFileSync(new URL(p,root)));
const hash=p=>createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex');
const base='source-scripts/city/government-import/accepted/government-xl-v-city-assembly-20260914/';
const out='docs/astra-city/government-import/government-xl-50-20260913/second-pass/third-pass/terrain-v-city/native-support-contact.json';
const supportUid='landsd/230643:0';
const groundUid='landsd/243886:0';
const catalogue=read(base+'catalogue.json');
const forms=read(base+'source-forms.json');
const records=new Map(forms.map(form=>[form.uid,form]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
const geometry=new Map();

for(const entry of prepareModelCatalogue(catalogue,'http://review.local/catalogue.json')){
 const bytes=readFileSync(new URL(base+entry.asset,root));
 const model=await loadOfficialModel(entry,records.get(entry.uid),lighting,{fetcher:async()=>new Response(bytes)});
 const {position,index}=model.record.modelGeometry,faces=[],rim=new Map();
 for(let i=0;i<index.length;i+=3){
  const face=new THREE.Triangle(...[index[i],index[i+1],index[i+2]].map(j=>new THREE.Vector3().fromArray(position,j*3)));
  if(face.getArea()>1e-12)faces.push(face);
 }
 for(let i=0;i<position.length;i+=3)if(position[i+1]<=entry.worldBounds[0][1]+.35){
  const value=[position[i],position[i+1],position[i+2]];
  rim.set(value.map(n=>n.toFixed(3)).join(','),value);
 }
 geometry.set(entry.uid,{entry,faces,rim:[...rim.values()]});
 disposeOfficialModel(model);
}

const support=geometry.get(supportUid),rows=[];
for(const [uid,item] of geometry){
 if(uid===supportUid||uid===groundUid)continue;
 const rim=item.rim.map(position=>({position,distance:nearest(support,new THREE.Vector3(...position))}));
 const distances=rim.map(row=>row.distance);
 rows.push({uid,sha256:item.entry.sha256,rimSamples:rim.length,contactsWithinHalfMetre:distances.filter(value=>value<=.5).length,contactsWithinOneMetre:distances.filter(value=>value<=1).length,minDistance:Math.min(...distances),maxDistance:Math.max(...distances),rim});
}
const report={issue:'HKS-203',supportUid,supportSHA256:support.entry.sha256,groundedIndependently:[groundUid],rows,inputHashes:{[base+'catalogue.json']:hash(base+'catalogue.json'),[base+'source-forms.json']:hash(base+'source-forms.json')},method:'Production native loader; unique component vertices within 0.35 m of each source minimum measured against exact non-degenerate triangles of the unchanged government V City podium. This records contact evidence without editing or simplifying either mesh.',aiCalls:0,modelGeometryChanges:0,publication:false};
writeFileSync(new URL(out,root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(rows.map(row=>({uid:row.uid,rimSamples:row.rimSamples,contactsWithinHalfMetre:row.contactsWithinHalfMetre,minDistance:row.minDistance,maxDistance:row.maxDistance}))));
