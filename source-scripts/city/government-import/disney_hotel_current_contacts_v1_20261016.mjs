/** Replay exact production contact samples on saved original/runtime geometry. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),folder=process.argv[2];
const read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root)));
const input=read(folder+'input.json'),g=read(input.geometryPath).rows[0],expected=read(input.metricsPath).rows[0],selection=read(input.selectionPath).rows[0];
assert.equal(g.sourceSHA256,selection.sourceSHA256);const {position,index}=g,bottom=selection.candidate.entry.worldBounds[0][1],surface=nativeTerrainSurface({position:g.drawnGroundGeometry,index:Array.from({length:g.drawnGroundGeometry.length/3},(_,i)=>i)});
const incidents=new Map();for(let i=0;i<index.length;i++) {const v=index[i];if(!incidents.has(v))incidents.set(v,new Set());incidents.get(v).add(Math.floor(i/3));}
let checks=0,lowCount=0,minGap=Infinity,maxLowGap=-Infinity,minLowGap=Infinity;const failures=[];
function check(p,kind,sourceFaces){const height=surface.height(p[0],p[2]);assert.notEqual(height,null);checks++;const gap=p[1]-height,low=p[1]<=bottom+.35;minGap=Math.min(minGap,gap);if(low){lowCount++;maxLowGap=Math.max(maxLowGap,gap);minLowGap=Math.min(minLowGap,gap);}if(gap<-.5||(low&&gap>1))failures.push({position:p,kind,sourceFaces,gapM:gap,drawnHeight:height,reason:gap<-.5?'burial':'low-rim-gap'});}
for(let i=0;i<position.length;i+=3)check(position.slice(i,i+3),'vertex',[...(incidents.get(i/3)||[])]);
for(let i=0;i<index.length;i+=3){const v=[0,1,2].map(k=>position.slice(index[i+k]*3,index[i+k]*3+3));check([0,1,2].map(k=>v.reduce((s,p)=>s+p[k],0)/3),'centroid',[i/3]);for(let e=0;e<3;e++){const a=v[e],b=v[(e+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(a.map((n,k)=>n+(b[k]-n)*j/steps),'edge',[i/3]);}}
assert.equal(checks,expected.checks);assert.equal(lowCount,expected.lowRimChecks);assert.equal(minGap,expected.minSurfaceGap);assert.equal(maxLowGap,expected.maxLowGap);assert.equal(minLowGap,expected.minLowGap);
const ids=[...new Set(failures.flatMap(r=>r.sourceFaces))].sort((a,b)=>a-b),faces=ids.map(id=>({face:id,vertices:[0,1,2].map(k=>position.slice(index[id*3+k]*3,index[id*3+k]*3+3))}));
const summary={checks,lowCount,minGap,maxLowGap,minLowGap,burialSamples:failures.filter(f=>f.reason==='burial').length,lowRimGapSamples:failures.filter(f=>f.reason==='low-rim-gap').length,affectedSourceFaces:faces.length,fullAcceptance:false};
writeFileSync(new URL(folder+'contacts.json.gz',root),gzipSync(JSON.stringify({summary,failures,faces})));writeFileSync(new URL(folder+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
