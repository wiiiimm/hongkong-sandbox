/** Measures unchanged source geometry against its independently acquired original TIN.
 * A source compatibility diagnostic, never the viewer's physical acceptance.
 */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const root=new URL('../../../',import.meta.url),[modelsPath,terrainPath,outPath]=process.argv.slice(2),inputs={};
assert(modelsPath&&terrainPath&&outPath&&!existsSync(new URL(outPath,root)));
const hash=b=>createHash('sha256').update(b).digest('hex');
const load=path=>{const raw=readFileSync(new URL(path,root));inputs[path]=hash(raw);return JSON.parse(gunzipSync(raw));};
const models=load(modelsPath).rows,terrains=load(terrainPath).rows;
const self='source-scripts/city/government-import/original-terrain-clearance-diagnostic.mjs';inputs[self]=hash(readFileSync(new URL(self,root)));const impl='3d-viewer/city/native-terrain.js';inputs[impl]=hash(readFileSync(new URL(impl,root)));
const rows=[];
for(const model of models){const terrain=terrains.find(t=>t.uid===model.uid);assert(terrain);const position=terrain.terrainTriangles.flat(2),index=Array.from({length:position.length/3},(_,i)=>i);const surface=nativeTerrainSurface({position,index}),bottom=model.worldBounds[0][1];
 let checks=0,lowRimChecks=0,minSurfaceGap=Infinity,minLowGap=Infinity,maxLowGap=-Infinity,missingTerrain=0,penetratingSamples=0;
 const failed=[];
 const check=(x,y,z,kind)=>{checks++;const t=surface.height(x,z);if(t===null){missingTerrain++;return;}const gap=y-t;minSurfaceGap=Math.min(minSurfaceGap,gap);if(y<=bottom+.35){lowRimChecks++;minLowGap=Math.min(minLowGap,gap);maxLowGap=Math.max(maxLowGap,gap);}if(gap<-.5)penetratingSamples++;if(gap<-.5||y<=bottom+.35&&gap>1)failed.push({point:[x,y,z],gap,kind});};
 for(const t of model.triangles){for(const p of t)check(...p,'vertex');check(...[0,1,2].map(a=>t.reduce((s,p)=>s+p[a],0)/3),'centre');for(let i=0;i<3;i++){const a=t[i],b=t[(i+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++)check(...a.map((v,k)=>v+(b[k]-v)*j/steps),'low-edge');}}
 const row={uid:model.uid,sourceSHA256:model.sourceSHA256,worldTrianglesSHA256:model.worldTrianglesSHA256,checks,lowRimChecks,minSurfaceGap,minLowGap,maxLowGap,missingTerrain,penetratingSamples,failedSamples:failed,originalTINContactPassed:!missingTerrain&&minSurfaceGap>=-.5&&minLowGap>=-.5&&maxLowGap<=1,identityAccepted:false,runtimeAccepted:false,installationApproved:false};rows.push(row);console.log(JSON.stringify({...row,failedSamples:failed.length}));
}
mkdirSync(new URL('.',new URL(outPath,root)),{recursive:true});writeFileSync(new URL(outPath,root),JSON.stringify({inputHashes:inputs,rows,publication:false,sourceGeometryChanges:0,qualification:'Diagnostic compatibility with original government TIN only. Original triangles are unmodified. Does not construct a drawn terrain patch or verify current neighbours, loader, identity, browser or publication.'},null,2)+'\n');
