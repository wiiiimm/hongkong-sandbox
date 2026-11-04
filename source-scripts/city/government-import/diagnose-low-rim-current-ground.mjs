/** Read-only exact acceptance samples, comparing a completed candidate to current ground. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {parseArgs} from 'node:util';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const root=new URL('../../../',import.meta.url);
const {values:a}=parseArgs({options:{doc:{type:'string'},geometry:{type:'string'},out:{type:'string'}}});
assert(a.doc&&a.geometry&&a.out);
const inputs={},hash=b=>createHash('sha256').update(b).digest('hex');
function load(path){const raw=readFileSync(new URL(path,root));inputs[path]=hash(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const result=load(a.doc+'/result.json');
for(const ref of result.evidenceRefs)assert.equal(hash(readFileSync(new URL(ref.path,root))),ref.sha256,ref.path);
const metrics=load(a.doc+'/metrics.json');
for(const [path,pinned] of Object.entries(metrics.inputHashes))assert.equal(hash(readFileSync(new URL(path,root))),pinned,path);
const selected=load(a.doc+'/selection.json.gz');
const manifest=load('3d-viewer/city/data/manifest.json');
assert.equal(inputs['3d-viewer/city/data/manifest.json'],selected.manifestSHA256);
const data=load('3d-viewer/city/data/terrain.json');data.patches=manifest.terrainPatches.map(r=>load('3d-viewer/'+r.url));
const current=makeTerrainSampler(data),geometry=load(a.geometry),rows=[];
for(const r of selected.rows){
 const g=geometry.rows.find(g=>g.uid===r.uid);assert(g&&g.sourceSHA256===r.sourceSHA256);
 const surface=nativeTerrainSurface({position:g.drawnGroundGeometry,index:Array.from({length:g.drawnGroundGeometry.length/3},(_,i)=>i)});
 const bottom=r.candidate.entry.worldBounds[0][1],points=[];let checks=0;
 function check(p,kind,face=null){checks++;if(p[1]>bottom+.35)return;const drawn=surface.height(p[0],p[2]),old=current.height(p[0],p[2]);assert(drawn!==null);points.push({point:p,kind,face,candidateGround:drawn,currentGround:old,candidateGap:p[1]-drawn,currentGap:p[1]-old});}
 for(let i=0;i<g.position.length;i+=3)check(g.position.slice(i,i+3),'vertex');
 for(let i=0;i<g.index.length;i+=3){const v=[0,1,2].map(k=>g.position.slice(g.index[i+k]*3,g.index[i+k]*3+3));check([0,1,2].map(k=>v.reduce((s,p)=>s+p[k],0)/3),'centre',i/3);
  for(let e=0;e<3;e++){const p=v[e],q=v[(e+1)%3];if(Math.max(p[1],q[1])>bottom+.35)continue;const n=Math.ceil(Math.hypot(p[0]-q[0],p[2]-q[2]));for(let j=1;j<n;j++)check(p.map((x,k)=>x+(q[k]-x)*j/n),'edge',i/3);}
 }
 const m=metrics.rows.find(m=>m.uid===r.uid);assert.equal(checks,m.checks);assert.equal(points.length,m.lowRimChecks);assert.equal(Math.max(...points.map(p=>p.candidateGap)),m.maxLowGap);
 rows.push({uid:r.uid,sourceSHA256:r.sourceSHA256,checks,lowRimChecks:points.length,failed:points.filter(p=>p.candidateGap>1||p.candidateGap<-.5),points});
}
inputs['source-scripts/city/government-import/diagnose-low-rim-current-ground.mjs']=hash(readFileSync(new URL('./diagnose-low-rim-current-ground.mjs',import.meta.url)));
const out=new URL(a.out,root);mkdirSync(new URL('.',out),{recursive:true});writeFileSync(out,JSON.stringify({policy:'unchanged-acceptance-low-rim-current-ground-diagnostic-v1',inputHashes:inputs,rows,publication:false,modelGeometryChanges:0,scriptExternalAICalls:0},null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,checks:r.checks,lowRimChecks:r.lowRimChecks,failed:r.failed.length}))));
