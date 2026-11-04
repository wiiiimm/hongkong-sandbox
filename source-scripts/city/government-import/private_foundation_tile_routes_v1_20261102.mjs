import assert from 'node:assert/strict';
export async function bindPrivateFoundationTileRoutes(page,config,mode='staged'){
 // Private exact foundation overlays compose all changes in a tile once.
 if(mode==='staged')for(const overlay of config.privateFoundationTileOverlays||[])await page.route('**/'+overlay.tile,async route=>{
  assert(config.diagnosticOnly===true);const response=await route.fetch(),raw=await response.body();assert.equal((await import('node:crypto')).createHash('sha256').update(raw).digest('hex'),overlay.tileSHA256);
  const data=JSON.parse(raw),seen=new Set();for(const update of overlay.updates){assert(!seen.has(update.uid));seen.add(update.uid);const matches=data.buildings.filter(b=>b.uid===update.uid);assert.equal(matches.length,1);const b=matches[0];assert.deepEqual(b,update.before);assert(!b.modelGeometry&&b.foundationBase===undefined);assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.heightSource,'estimated');assert.equal(b.baseHeightHKPD,null);assert.equal(b.topHeightHKPD,null);assert(['Open-sided Structure','Temporary Structure'].includes(b.structureType));assert(Number.isFinite(update.foundationBase)&&update.foundationBase<b.base-.02);b.foundationBase=update.foundationBase;}
  await route.fulfill({response,json:data});
 });

}
