/** Pointwise original-surface feasibility only; full facets/identity/gates still required. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
const [folder]=process.argv.slice(2),root=new URL('../../../',import.meta.url),sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));return {data:JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw),hash:sha(raw)};}
const path=folder+'/inputs.json',inputs=read(path);assert(inputs.data.diagnosticOnly&&!existsSync(new URL(folder+'/result.json',root)));
for(const ref of [inputs.data.parent,inputs.data.source,inputs.data.manifest,inputs.data.preview])assert.equal(sha(readFileSync(new URL(ref.path,root))),ref.sha256);
const rows=[];
for(const item of inputs.data.rows){
 const raw=read(item.samples.path);assert.equal(raw.hash,item.samples.sha256);const sample=raw.data;
 const geometry=read(sample.geometry.path);assert.equal(geometry.hash,sample.geometry.sha256);
 const model=geometry.data.rows.find(row=>row.uid===sample.uid);assert.equal(model.sourceSHA256,sample.sourceSHA256);
 const drawn=model.drawnGroundGeometry,surface=nativeTerrainSurface({position:drawn,index:Array.from({length:drawn.length/3},(_,i)=>i)});
 let unresolved=0,missing=0,unresolvedLow=0,dtmOnly=0,parentOnly=0,contactPossible=false;
 sample.points.forEach((point,i)=>{
  const low=point[1]<=sample.bottom+.35,valid=height=>height!==null&&Number.isFinite(height)&&point[1]-height>=-.5&&(!low||point[1]-height<=1);
  const heights=[surface.height(point[0],point[2]),sample.originalParentHeights[i],sample.originalDTMHeights[i]],passes=heights.map(valid);
  if(heights[0]===null)missing++;
  if(!passes.some(Boolean)){unresolved++;if(low)unresolvedLow++;}
  if(passes[2]&&!passes[0]&&!passes[1])dtmOnly++;
  if(passes[1]&&!passes[0]&&!passes[2])parentOnly++;
  if(low&&heights.some(height=>valid(height)&&point[1]-height<=.1))contactPossible=true;
 });
 const row={uid:sample.uid,sourceSHA256:sample.sourceSHA256,geometry:sample.geometry,samples:item.samples,checks:sample.points.length,edgeChecks:sample.edgeChecks,unresolvedPoints:unresolved,unresolvedLowPoints:unresolvedLow,missingCurrentTerrain:missing,dtmOnlyRecoverablePoints:dtmOnly,parentOnlyRecoverablePoints:parentOnly,contactPossible,pointwisePositive:unresolved===0&&contactPossible,currentInputHashesMatch:sample.currentInputHashesMatch};rows.push(row);console.log(JSON.stringify({uid:row.uid,positive:row.pointwisePositive,unresolved,dtmOnly,parentOnly}));
}
writeFileSync(new URL(folder+'/result.json',root),JSON.stringify({rows,inputs:{path,sha256:inputs.hash},runnerSHA256:sha(readFileSync(new URL(import.meta.url))),diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,qualification:'Each sample may select a different original surface. Positive pointwise feasibility never proves a coherent terrain, full identity/foundation/neighbours, runtime or browser acceptance. Historical input freshness is explicit.'},null,2)+'\n');
console.log(JSON.stringify({models:rows.length,positiveUids:rows.filter(row=>row.pointwisePositive).map(row=>row.uid)}));
