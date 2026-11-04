/** Exact-byte PRIVATE continuation experiment. Never enabled in live mode. */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {sourceBoundBasicBottom} from '../../../3d-viewer/city/source-bound-basic-ground.js';
const sha=b=>createHash('sha256').update(b).digest('hex');
export async function bindPrivateSourceBoundRoutes(page,config,root,mode,report){
 if(!config.privateSourceBoundTileOverlays&&!config.privateBasicGeometryModule)return;
 assert.equal(mode,'staged');assert.equal(config.diagnosticOnly,true);assert.equal(config.publication,false);
 assert(config.privateBasicGeometryModule&&config.privateSourceBoundTileOverlays?.length);
 const module=config.privateBasicGeometryModule;
 assert.equal(module.url,'city/building-geometry.js');assert.equal(module.originalAlias,'city/building-geometry-original-private.js');
 assert(module.source.startsWith('source-scripts/city/government-import/local/')&&!module.source.includes('..'));
 const baseline=await readFile(new URL('3d-viewer/city/building-geometry.js',root)),wrapper=await readFile(new URL('3d-viewer/city/source-bound-basic-geometry-private.js',root));
 assert.equal(sha(baseline),module.originalSHA256);assert.equal(sha(wrapper),module.wrapperSHA256);
 const expected=wrapper.toString().replace("from './building-geometry.js';","from './building-geometry-original-private.js';")+"\nexport {prepareModelGeometry,isOpenSidedBuilding} from './building-geometry-original-private.js';\n";
 const bytes=await readFile(new URL(module.source,root));assert.equal(bytes.toString(),expected);assert.equal(sha(bytes),module.sha256);
 await page.route('**/'+module.originalAlias+'*',r=>r.fulfill({contentType:'application/javascript',body:baseline}));
 await page.route('**/'+module.url+'*',r=>r.fulfill({contentType:'application/javascript',body:bytes}));
 const seen=new Set(),catalogue=JSON.parse(await readFile(new URL(config.stage+'catalogue.json',root)));
 for(const overlay of config.privateSourceBoundTileOverlays){
  assert(overlay.url.startsWith('city/data/tiles/')&&!overlay.url.includes('..'));
  assert(overlay.source.startsWith('source-scripts/city/government-import/local/')&&!overlay.source.includes('..'));
  const originalBytes=await readFile(new URL('3d-viewer/'+overlay.url,root));assert.equal(sha(originalBytes),overlay.beforeSHA256);
  const original=JSON.parse(originalBytes),expected=structuredClone(original);
  for(const change of overlay.changes){
   assert(!seen.has(change.uid));seen.add(change.uid);assert.equal(change.proposalApproved,false);
   const b=expected.buildings.find(b=>b.uid===change.uid);assert.deepEqual(b,change.before);assert(!b.modelGeometry&&b.foundationBase==null&&!b.nativeFallbackGround);
   if(change.role==='source-bound-basic-continuation'){
    assert.deepEqual(change.after,{...b,nativeFallbackGround:change.hint});
    const owner=catalogue.models.find(m=>m.uid===b.uid);assert(owner&&owner.sha256===change.hint.sourceSHA256);
    assert(config.terrain.some(t=>t.sha256===change.hint.terrainSHA256));
    assert.equal(sourceBoundBasicBottom(change.after),change.hint.base);Object.assign(b,change.after);
   }else{
    assert.equal(change.role,'existing-estimated-open-canopy');assert.equal(b.structureType,'Open-sided Structure');
    assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.heightSource,'estimated');assert(b.baseHeightHKPD==null&&b.topHeightHKPD==null);
    assert(Number.isFinite(change.foundationBase)&&change.foundationBase<b.base-.02);
    assert.deepEqual(change.after,{...b,foundationBase:change.foundationBase});Object.assign(b,change.after);
   }
  }
  const bytes=await readFile(new URL(overlay.source,root));assert.equal(sha(bytes),overlay.afterSHA256);assert.deepEqual(JSON.parse(bytes),expected);
  await page.route('**/'+overlay.url,async route=>{const response=await route.fetch(),current=await response.body();assert.equal(sha(current),overlay.beforeSHA256);assert.deepEqual(JSON.parse(current),original);await route.fulfill({response,body:bytes});});
 }
 assert.equal(seen.size,4);report.privateSourceBoundExperiment={uids:[...seen],moduleSHA256:module.sha256,originalSHA256:module.originalSHA256,diagnosticOnly:true,publication:false};
}
