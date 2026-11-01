/** Observe complete original fallback and all retained foundation neighbours. */
import assert from 'node:assert/strict';
import {fallbackChecks} from './elegant_live_fallback_checks_v1_20261028.mjs';
export async function originalGroupFallbackChecks(page,active,catalogue,config){
 const suppression=await fallbackChecks(page,active,catalogue);
 assert.deepEqual(config.privateSourceBoundTileOverlays,[]);
 const rows=await page.evaluate(({uids,updates})=>{
  const r=window.__port;
  return [...uids,...updates.map(u=>u.uid)].map(uid=>{
   const e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)throw new Error('Missing current fallback tile '+uid);
   const b=e.data.buildings.find(b=>b.uid===uid),at=e.data.buildings.findIndex(b=>b.uid===uid),i=e.index.buildings.findIndex(b=>b.uid===uid),volumes=i<0?[]:e.index.volumes[i];let faces=0;
   for(const mesh of e.buildings.group.children){const f=mesh.geometry?.attributes.feature;if(f)for(const v of f.array)if(v===at)faces++;}
   return {uid,fields:Object.fromEntries(['uid','kind','structureType','buildingCSUID','base','height','minimum','baseHeightHKPD','topHeightHKPD','baseSource','heightSource'].map(k=>[k,b[k]])),faces,foundationBase:b.foundationBase,nativeFallbackGround:b.nativeFallbackGround,kinds:volumes.map(v=>v.kind),posts:volumes.filter(v=>v.kind==='post').map(v=>({bottom:v.bottom,top:v.top})),foundations:volumes.filter(v=>v.kind==='foundation').map(v=>({bottom:v.bottom,top:v.top,windows:v.windows}))};
  });
 },{uids:catalogue.models.map(m=>m.uid),updates:config.privateFoundationTileOverlays.flatMap(o=>o.updates)});
 for(const model of catalogue.models){const row=rows.find(r=>r.uid===model.uid);assert(row);assert.equal(row.faces>0,!active);assert.equal(row.kinds.includes('model-surface'),active);assert.equal(row.foundationBase,undefined);assert.equal(row.nativeFallbackGround,undefined);}
 for(const update of config.privateFoundationTileOverlays.flatMap(o=>o.updates)){
  const row=rows.find(r=>r.uid===update.uid);assert(row&&row.faces>0);assert.equal(row.foundationBase,update.foundationBase);
  for(const k of Object.keys(row.fields))assert.deepEqual(row.fields[k],update.before[k],k);
  if(update.before.structureType==='Open-sided Structure'){assert(row.posts.length>0);assert(row.posts.every(p=>p.bottom===update.foundationBase));}
  else{assert.deepEqual(row.foundations,[{bottom:update.foundationBase,top:update.before.base,windows:false}]);}
 }
 return {active,suppression,rows,actualRenderedAndCollisionFallbackObserved:true,sourceBoundContinuationsProposed:false};
}
