/** Observe real rendered fallback vertices and real tile collision volumes. */
import assert from 'node:assert/strict';
import {fallbackChecks} from './elegant_live_fallback_checks_v1_20261028.mjs';
export async function sourceBoundFallbackChecks(page,active,catalogue,config){
 const suppression=await fallbackChecks(page,active,catalogue);
 const changes=config.privateSourceBoundTileOverlays.flatMap(o=>o.changes);
 const rows=await page.evaluate(async({active,changes})=>{
  const r=window.__port,{createBuildingGeometry}=await import('/city/building-geometry.js'),{BuildingIndex,inPolygon}=await import('/city/geo.js');
  return changes.map(change=>{
   const uid=change.uid,e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)throw new Error('Expected fallback tile absent '+uid);
   const b=e.data.buildings.find(b=>b.uid===uid),feature=e.data.buildings.findIndex(b=>b.uid===uid),at=e.index.buildings.findIndex(b=>b.uid===uid),volumes=at<0?[]:e.index.volumes[at];
   const ys=[];for(const mesh of e.buildings.group.children){const f=mesh.geometry?.attributes.feature,p=mesh.geometry?.attributes.position;if(f&&p)for(let i=0;i<f.count;i++)if(f.getX(i)===feature)ys.push(p.getY(i));}
   const result={uid,base:b.base,height:b.height,minimum:b.minimum,baseHeightHKPD:b.baseHeightHKPD,topHeightHKPD:b.topHeightHKPD,hint:b.nativeFallbackGround,foundationBase:b.foundationBase,hasBasicFaces:ys.length>0,renderedBasicMinY:ys.length?Math.min(...ys):null,renderedBasicMaxY:ys.length?Math.max(...ys):null,collisionKinds:volumes.map(v=>v.kind),continuations:volumes.filter(v=>v.kind==='basic-ground-continuation').map(v=>({bottom:v.bottom,top:v.top,windows:v.windows})),posts:volumes.filter(v=>v.kind==='post').map(v=>({bottom:v.bottom,top:v.top}))};
   if(!active&&change.role==='source-bound-basic-continuation'){
    const g=createBuildingGeometry(b),p=g.attributes.position;let probe=null,area=0;
    for(let i=0;i<p.count;i+=3){const a=[p.getX(i),p.getY(i),p.getZ(i)],c=[p.getX(i+1),p.getY(i+1),p.getZ(i+1)],d=[p.getX(i+2),p.getY(i+2),p.getZ(i+2)];if(![a,c,d].every(v=>v[1]===Math.fround(change.hint.originalBottom)))continue;const signed=(c[2]-a[2])*(d[0]-a[0])-(c[0]-a[0])*(d[2]-a[2]),x=(a[0]+c[0]+d[0])/3,z=(a[2]+c[2]+d[2])/3;if(signed>area&&inPolygon(x,z,b.rings)){area=signed;probe={x,z};}}
    g.dispose();if(!probe)throw new Error('No interior continuation probe '+uid);
    const bottom=(change.hint.base+change.hint.originalBottom)/2,top=bottom+.01;
    result.collisionProbe={...probe,bottom,top,target:!!new BuildingIndex([b]).collision(probe.x,probe.z,bottom,top,0),actualTile:!!e.index.collision(probe.x,probe.z,bottom,top,0)};
   }
   return result;
  });
 },{active,changes});
 for(const row of rows){
  const c=changes.find(c=>c.uid===row.uid);
  for(const key of ['base','height','minimum','baseHeightHKPD','topHeightHKPD'])assert.deepEqual(row[key],c.before[key],key);
  if(c.role==='source-bound-basic-continuation'){
   assert.deepEqual(row.hint,c.hint);
   if(active){assert(!row.hasBasicFaces);assert.equal(row.continuations.length,0);assert(row.collisionKinds.includes('model-surface'));}
   else{assert(row.hasBasicFaces);assert.equal(row.renderedBasicMinY,Math.fround(c.hint.base));assert.equal(row.renderedBasicMaxY,Math.fround(c.before.base+c.before.height));assert.deepEqual(row.continuations,[{bottom:c.hint.base,top:c.hint.originalBottom,windows:false}]);assert(row.collisionProbe.target&&row.collisionProbe.actualTile);}
  }else{
   assert.equal(row.foundationBase,c.foundationBase);assert.equal(row.hasBasicFaces,!active);
   if(!active){assert(row.posts.length>0);assert(row.posts.every(p=>p.bottom===c.foundationBase));assert.equal(row.renderedBasicMaxY,Math.fround(c.before.base+c.before.height));}
  }
 }
 return {active,suppression,rows,actualRenderedAndCollisionFallbackObserved:true};
}
