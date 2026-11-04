import assert from 'node:assert/strict';
export async function fallbackChecks(page,active,catalogue){
 for(const model of catalogue.models)for(const uid of model.suppressesBuildingUids||[]){
  await page.waitForFunction(({uid,active})=>{const r=window.__port,e=[...r.stream.cache.entries.values()].find(e=>e.data.buildings.some(b=>b.uid===uid));if(!e)return false;const i=e.data.buildings.findIndex(b=>b.uid===uid),hasFaces=e.buildings.group.children.some(m=>{const f=m.geometry?.attributes.feature;return f&&Array.from(f.array).includes(i);});return active?e.detailSuppressions?.has(uid)&&!hasFaces:!e.detailSuppressions?.has(uid)&&hasFaces;},{uid,active},{timeout:120000});
 }
 const supports=await page.evaluate(()=>{const r=window.__port;return [...r.officialModels.models.values()].flatMap(m=>(m.retainedBasicSupportDependencies||[]).map(d=>{const b=r.stream.getLoadedBuilding(d.supportUid);return {uid:d.supportUid,csuid:b?.buildingCSUID,basic:!!b&&!b.modelGeometry,active:!!r.stream.detailedModels.get(d.supportUid)?.active};}));});
 const expected=catalogue.models.flatMap(m=>m.retainedBasicSupportDependencies||[]);for(const d of expected){const actual=supports.find(x=>x.uid===d.supportUid);assert(actual&&actual.basic&&!actual.active&&actual.csuid===d.supportCSUID);}
 return {suppressionMatchesActivation:true,retainedBasicSupports:expected.map(d=>d.supportUid)};
}
