/** Locate existing strict floating low-rim failures in immutable runtime geometry. No acceptance. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const [path,out]=process.argv.slice(2),root=new URL('../../../',import.meta.url);
assert(path&&out&&!existsSync(new URL(out,root)),'Fresh diagnostic output required');
const sha=b=>createHash('sha256').update(b).digest('hex'),raw=readFileSync(new URL(path,root));
const input=JSON.parse(gunzipSync(raw));
for(const [p,h] of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h,`Changed input ${p}`);
const rows=input.rows.map(r=>{
 const p=r.position,idx=r.index,g=r.drawnGroundGeometry;
 const surface=nativeTerrainSurface({position:g,index:Array.from({length:g.length/3},(_,i)=>i)});
 const bottom=Math.min(...p.filter((_,i)=>i%3===1)),failed=[],counts={vertex:0,centre:0,lowEdge:0};let minimum=Infinity;
 const check=(point,kind,face,vertex=null)=>{const ground=surface.height(point[0],point[2]);assert(ground!==null,'No drawn terrain');const gap=point[1]-ground;minimum=Math.min(minimum,gap);if(point[1]<=bottom+.35&&gap>1){counts[kind]++;failed.push({point,ground,gap,kind,face,vertex});}};
 for(let i=0;i<p.length;i+=3)check(p.slice(i,i+3),'vertex',null,i/3);
 for(let i=0;i<idx.length;i+=3){const v=[0,1,2].map(k=>p.slice(idx[i+k]*3,idx[i+k]*3+3));check([0,1,2].map(k=>v.reduce((s,q)=>s+q[k],0)/3),'centre',i/3);
  for(let e=0;e<3;e++){const a=v[e],b=v[(e+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const n=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<n;j++)check(a.map((x,k)=>x+(b[k]-x)*j/n),'lowEdge',i/3);}
 }
 return {uid:r.uid,sourceSHA256:r.sourceSHA256,minimumGap:minimum,counts,failed};
});
writeFileSync(new URL(out,root),JSON.stringify({geometry:{path,sha256:sha(raw)},inputHashes:input.inputHashes,runnerSHA256:sha(readFileSync(new URL(import.meta.url))),rows,diagnosticOnly:true,publication:false,modelGeometryChanges:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,minimumGap:r.minimumGap,counts:r.counts,failed:r.failed.length}))));
