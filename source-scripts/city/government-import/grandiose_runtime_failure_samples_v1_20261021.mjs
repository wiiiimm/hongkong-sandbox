import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const prior='docs/astra-city/government-import/government-xl-grandiose-private-runtime-v1-20261021/',cap=read('source-scripts/city/government-import/local/government-xl-grandiose-private-runtime-v1-20261021/runtime-geometry.json.gz'),selection=read(prior+'selection.json.gz'),expected=read(prior+'metrics.json');const rows=[];
for(const r of cap.rows){const e=selection.rows.find(x=>x.uid===r.uid).candidate.entry;const position=r.position,index=r.index,g=r.drawnGroundGeometry,surface=nativeTerrainSurface({position:g,index:Array.from({length:g.length/3},(_,i)=>i)});let count=0,min=Infinity;const failures=[];
const check=(p,origin)=>{count++;const ground=surface.height(p[0],p[2]);assert.notEqual(ground,null);const gap=p[1]-ground;min=Math.min(min,gap);if(gap<-.5)failures.push({position:p,ground,gap,...origin});};
for(let i=0;i<position.length;i+=3)check(position.slice(i,i+3),{kind:'vertex',vertex:i/3});
for(let i=0;i<index.length;i+=3){const v=[0,1,2].map(k=>position.slice(index[i+k]*3,index[i+k]*3+3));check([0,1,2].map(k=>v.reduce((s,p)=>s+p[k],0)/3),{kind:'centroid',face:i/3});for(let edge=0;edge<3;edge++){const a=v[edge],b=v[(edge+1)%3];if(Math.max(a[1],b[1])>e.worldBounds[0][1]+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(a.map((x,k)=>x+(b[k]-x)*j/steps),{kind:'edge',face:i/3,edge,step:j,steps});}}
const metric=expected.rows.find(x=>x.uid===r.uid);assert.equal(count,metric.checks);assert.equal(min,metric.minSurfaceGap);rows.push({uid:r.uid,checks:count,minSurfaceGap:min,failures});}
writeFileSync(new URL(process.argv[2],root),JSON.stringify({rows,installationApproved:false}));
