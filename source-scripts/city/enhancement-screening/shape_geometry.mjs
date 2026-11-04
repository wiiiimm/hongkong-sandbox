/** Export triangles through the same geometry builders/loaders as City. No renderer or AI. */
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {gzipSync, gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {loadOfficialModel, disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {MODEL_PROFILES} from '../../../3d-viewer/city/official-models.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {Vector3} from '../../../3d-viewer/vendor/three.module.js';

const sha=b=>createHash('sha256').update(b).digest('hex');
const input=JSON.parse(readFileSync(process.argv[2])),out=resolve(process.argv[3]);
mkdirSync(out,{recursive:true});
const lighting={night:{value:0},activity:{value:new Float32Array([0,0,0,0])},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const triangles=g=>{
  const p=g.attributes.position,idx=g.index,point=new Vector3(),a=[];
  for(let i=0;i<(idx?.count??p.count);i++){point.fromBufferAttribute(p,idx?idx.getX(i):i);a.push(...point.toArray());}
  return a;
};
async function native(spec,b){
  const raw=readFileSync(spec.path),entry={...spec.entry,assetURL:'https://screening.invalid/asset.glb.gz'};
  const model=await loadOfficialModel(entry,b,lighting,{fetcher:async()=>new Response(raw)});
  const {position,index}=model.record.modelGeometry,a=[];
  for(const i of index)a.push(position[i*3],position[i*3+1],position[i*3+2]);
  const budget=model.budget;disposeOfficialModel(model);return {position:a,budget,sha:sha(raw)};
}
const repo=new URL('../../../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,repo)));
const manifest=read('3d-viewer/city/data/manifest.json'),terrainData=read('3d-viewer/city/data/terrain.json');
terrainData.patches=(manifest.terrainPatches||[]).map(p=>read('3d-viewer/'+p.url));
const sampler=makeTerrainSampler(terrainData);
function terrainDiagnostic(position){
 const low=position.reduce((v,x,i)=>i%3===1?Math.min(v,x):v,Infinity),gaps=[];let outside=0;
 for(let i=0;i<position.length;i+=3){if(position[i+1]>low+.35)continue;const [x,y,z]=position.slice(i,i+3);if(!sampler.contains(x,z)){outside++;continue;}gaps.push(y-sampler.height(x,z));}
 return {status:outside?'diagnostic-partial-coverage':gaps.length?'diagnostic-complete':'outside-terrain-coverage',lowRimGapRange:gaps.length?gaps.reduce(([a,b],g)=>[Math.min(a,g),Math.max(b,g)],[Infinity,-Infinity]):null,outsideTerrainSamples:outside,sourceLowRimVertices:gaps.length+outside,placementApproved:false,method:'All triangle low-rim vertices against current City terrain sampler; support and burial are not certified'};
}
const index=[];
for(const row of input.rows){
  try{
    const current=row.currentNative?await native(row.currentNative,row.building):null;
    const g=current?null:createBuildingGeometry(row.building);
    const a=current?.position??triangles(g);g?.dispose();
    const b=await native(row.candidate,row.building);
    const data={uid:row.uid,current:a,candidate:b.position,currentKind:row.currentNative?'native':row.building.modelGeometry?'embedded':'footprint',candidateSHA:b.sha,budget:b.budget,terrain:terrainDiagnostic(b.position)};
    const raw=Buffer.from(JSON.stringify(data)),key=sha(raw),file=key+'.json.gz';
    writeFileSync(resolve(out,file),gzipSync(raw,{mtime:0}));
    index.push({uid:row.uid,file,sha256:sha(readFileSync(resolve(out,file))),geometrySHA256:key,budget:b.budget,terrain:data.terrain});
  }catch(e){index.push({uid:row.uid,error:String(e.message)});}
}
writeFileSync(resolve(out,'index.json'),JSON.stringify({rows:index,profiles:MODEL_PROFILES},null,2)+'\n');
console.log(JSON.stringify({geometryPairs:index.filter(r=>!r.error).length,errors:index.filter(r=>r.error).length}));
