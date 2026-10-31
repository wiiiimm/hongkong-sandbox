// Replay the canonical runtime low-rim samples against both unchanged source TIN and candidate.
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url);
const read=p=>JSON.parse(gunzipSync(readFileSync(new URL(p,root))));
const base='docs/astra-city/government-import/government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019/';
const row=read(base+'selection.json.gz').rows.find(r=>r.uid==='landsd/281463:0');
const g=read('source-scripts/city/government-import/local/government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019/runtime-geometry.json.gz').rows.find(r=>r.uid===row.uid);
assert.equal(g.sourceSHA256,row.sourceSHA256);
const original=read('source-scripts/city/government-import/local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz').completeAdjoiningTerrain.flat(2);
const surface=p=>nativeTerrainSurface({position:p,index:Array.from({length:p.length/3},(_,i)=>i)});
const source=surface(original),candidate=surface(g.drawnGroundGeometry),bottom=row.candidate.entry.worldBounds[0][1],samples=[];
let checks=0;const missing=[];
function check(p,origin){checks++;const a=source.height(p[0],p[2]),b=candidate.height(p[0],p[2]);if(b===null)missing.push({point:p,origin,originalHeight:a});if(p[1]>bottom+.35)return;assert(a!==null&&b!==null);samples.push({point:p,origin,originalGap:p[1]-a,candidateGap:p[1]-b,terrainChange:b-a});}
const {position:p,index}=g;
for(let i=0;i<p.length;i+=3)check(p.slice(i,i+3),{vertex:i/3});
for(let i=0;i<index.length;i+=3){const v=[0,1,2].map(k=>p.slice(index[i+k]*3,index[i+k]*3+3));check([0,1,2].map(k=>v.reduce((s,x)=>s+x[k],0)/3),{face:i/3,centroid:true});for(let edge=0;edge<3;edge++){const a=v[edge],b=v[(edge+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(a.map((x,k)=>x+(b[k]-x)*j/steps),{face:i/3,edge,j,steps});}}
const metrics=JSON.parse(readFileSync(new URL(base+'metrics.json',root))).rows.find(r=>r.uid===row.uid);
assert.equal(checks,metrics.checks);assert.equal(missing.length,metrics.missingTerrain);assert.equal(samples.length,metrics.lowRimChecks);
const range=key=>[Math.min(...samples.map(r=>r[key])),Math.max(...samples.map(r=>r[key]))];
assert(Math.abs(range('candidateGap')[0]-metrics.minLowGap)<1e-9);assert(Math.abs(range('candidateGap')[1]-metrics.maxLowGap)<1e-9);
const fails=r=>r<-.5||r>1;
const summary={uid:row.uid,sourceSHA256:g.sourceSHA256,checks,missingTerrain:missing.length,lowRimChecks:samples.length,originalGapRange:range('originalGap'),candidateGapRange:range('candidateGap'),terrainChangeRange:range('terrainChange'),newlyFailingSamples:samples.filter(r=>fails(r.candidateGap)&&!fails(r.originalGap)).length,installationApproved:false};
writeFileSync(process.argv[2],JSON.stringify({summary,samples,missing},null,2)+'\n');console.log(JSON.stringify(summary));
