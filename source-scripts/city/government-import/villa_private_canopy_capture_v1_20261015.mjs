/** Private candidate capture through unchanged production generator, not current live geometry. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {createBuildingGeometry,describeBuilding} from '../../../3d-viewer/city/building-geometry.js';
const hash=b=>createHash('sha256').update(b).digest('hex');
const inputPath=process.argv[2],input=JSON.parse(readFileSync(inputPath));
const mp='3d-viewer/city/data/manifest.json',tp='3d-viewer/city/data/tiles/-7_-9.json';
assert.equal(hash(readFileSync(mp)),input.manifestSHA256);assert.equal(hash(readFileSync(tp)),input.tileSHA256);
const actual=JSON.parse(readFileSync(tp)).buildings.find(x=>x.uid===input.uid);assert.deepEqual(actual,input.currentForm);assert(!actual.modelGeometry);
const rows=[];
for(const [mode,forms] of [['current',[actual]],['privateCandidate',input.privateCandidateRings.map(rings=>({...actual,rings}))]]){
 for(let part=0;part<forms.length;part++){
  const form=forms[part],description=describeBuilding(form),geometry=createBuildingGeometry(form),position=Array.from(geometry.attributes.position.array),index=geometry.index?Array.from(geometry.index.array):Array.from({length:position.length/3},(_,i)=>i);
  assert(position.every(Number.isFinite));rows.push({mode,part,uid:actual.uid,form,description,position,index});geometry.dispose();
 }
}
const paths=[inputPath,mp,tp,'source-scripts/city/government-import/villa_private_canopy_capture_v1_20261015.mjs','3d-viewer/city/building-geometry.js','3d-viewer/city/tai-o-estimates.js','3d-viewer/vendor/three.module.js','3d-viewer/vendor/BufferGeometryUtils.js'];
writeFileSync(process.argv[3],JSON.stringify({rows,inputHashes:Object.fromEntries(paths.map(p=>[p,hash(readFileSync(p))])),qualification:'Private candidate and current baseline through unchanged production geometry builder. All Float32 faces retained; no live mutation or approval.'})+'\n');
