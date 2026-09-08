/** Native vertex/terrain and M+ tower-to-podium triangle support. No edits. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {makeTerrainSampler,inPolygon} from '../../../3d-viewer/city/geo.js';
const root=new URL('../../../',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root))),hashes={},tracked=p=>{const b=readFileSync(new URL(p,root));hashes[p]=createHash('sha256').update(b).digest('hex');return JSON.parse(b);};
const folder='source-scripts/city/cultural-model-review/candidates/',cat=tracked(folder+'catalogue.json'),manifest=tracked('3d-viewer/city/data/manifest.json'),data=tracked('3d-viewer/city/data/terrain.json');
data.patches=manifest.terrainPatches.map(p=>tracked('3d-viewer/'+p.url));const sampler=makeTerrainSampler(data),buildings=new Map();
for(const t of manifest.tiles){const tile=read('3d-viewer/'+t.url);for(const b of tile.buildings)if(cat.models.some(m=>m.uid===b.uid)){tracked('3d-viewer/'+t.url);buildings.set(b.uid,b);}}
const lighting={night:{value:1},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},loaded=new Map(),rows=[];
const quantiles=xs=>{xs.sort((a,b)=>a-b);return[0,.25,.5,.75,1].map(q=>xs[Math.floor((xs.length-1)*q)]);};
try{
 for(const m of prepareModelCatalogue(cat,'http://staged.local/catalogue.json')){
  const asset=readFileSync(new URL(folder+m.asset,root));const model=await loadOfficialModel(m,buildings.get(m.uid),lighting,{fetcher:async()=>new Response(asset)});loaded.set(m.uid,model);
  const p=model.record.modelGeometry.position,seen=new Set(),unique=[];for(let i=0;i<p.length;i+=3){const key=[p[i],p[i+1],p[i+2]].join(',');if(!seen.has(key)){seen.add(key);unique.push([p[i],p[i+1],p[i+2]]);}}
  const base=m.worldBounds[0][1],deltas=unique.map(p=>p[1]-sampler.height(p[0],p[2])),bottom=unique.filter(p=>p[1]<=base+.5),bottomDelta=bottom.map(p=>p[1]-sampler.height(p[0],p[2]));
  rows.push({uid:m.uid,sourceYBounds:[base,m.worldBounds[1][1]],surveyedBaseTop:[m.recordedBaseHeight,m.recordedTopHeight],uniqueVertices:unique.length,verticesBuried05m:deltas.filter(d=>d<-.5).length,verticesBuried2m:deltas.filter(d=>d<-2).length,nearBottomVertices:bottom.length,nearBottomClearanceQuantiles:quantiles(bottomDelta),terrainResolutions:[...new Set(bottom.map(p=>sampler.resolutionAt(p[0],p[2])))]});
 }
 const tower=cat.models.find(m=>m.uid==='landsd/310908:0'),podium=loaded.get('landsd/279530:0'),b=buildings.get(tower.uid),[a,c]=tower.worldBounds,rays=[],ray=new THREE.Raycaster();
 for(let x=a[0]+.5;x<c[0];x+=1)for(let z=a[2]+.5;z<c[2];z+=1){if(!inPolygon(x,z,b.rings))continue;ray.set(new THREE.Vector3(x,a[1]+10,z),new THREE.Vector3(0,-1,0));const levels=ray.intersectObjects(podium.meshes).map(h=>h.point.y),differences=levels.map(y=>Math.abs(y-a[1])),nearest=levels.length?levels[differences.indexOf(Math.min(...differences))]:null;rays.push({x,z,supportY:nearest,difference:nearest===null?null:nearest-a[1]});}
 const hits=rays.filter(r=>r.supportY!==null),within=hits.filter(r=>Math.abs(r.difference)<=.5);
 const support={target:tower.uid,support:'landsd/279530:0',method:'1 m grid inside actual source tower footprint; downward intersections with native indexed podium triangles; nearest surface to native tower base, not a bounding-box support proxy.',towerBase:a[1],samples:rays.length,actualTriangleHits:hits.length,within05m:within.length,differenceQuantiles:quantiles(hits.map(r=>r.difference)),rays};
 assert(rays.length>100);assert.equal(hits.length,rays.length);assert(within.length/rays.length>.99,'M+ support requires further review');
 const report={verticalScale:1,units:'metres HKPD',published:false,hashes,rows,support,limits:['All native vertices compared with the current final rendered terrain sampler; statistics include legitimate substructure and are not automatic acceptance.','Support proves sampled source surfaces at the tower base; architectural membership is checked separately against exact government identities and official M+ references.']};
 writeFileSync(new URL('docs/astra-city/cultural-model-review/context.json',root),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({rows,support:{...support,rays:undefined}}));
}finally{for(const m of loaded.values())disposeOfficialModel(m);}
