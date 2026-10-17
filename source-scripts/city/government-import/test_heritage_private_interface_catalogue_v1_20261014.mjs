/** Actual production metadata validator only; no decode/geometry/browser. */
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {makePrivateInterfaceCatalogue} from './heritage_private_interface_catalogue_v1_20261014.mjs';
import {prepareModelCatalogue} from '../../../3d-viewer/city/official-model-assets.js';
const root=new URL('../../../',import.meta.url),saved=JSON.parse(readFileSync(new URL('docs/astra-city/government-import/government-xl-heritage165054-starmart57455-private-interface-review-v2-20261014/preview-input.json',root))),url='http://127.0.0.1:4176/city/data/private-source-review/fixture/catalogue.json';
// V2 failure before assets: the exact actual incomplete envelope must reject.
assert.throws(()=>prepareModelCatalogue({models:[saved.sources[0].entry]},url),/Invalid compact model catalogue/);
// V2's unexecuted original scenario also omitted Star objectId; retain rejection.
assert.throws(()=>prepareModelCatalogue(makePrivateInterfaceCatalogue(saved.sources,'original-Star'),url),/Invalid compact model entry landsd\/57455:0/);
const sources=saved.sources.map(s=>s.uid==='landsd/57455:0'?{...s,entry:{...s.entry,objectId:s.currentForm.objectId}}:s);
for(const scenario of ['current-BASIC','original-Star']){
 const c=makePrivateInterfaceCatalogue(sources,scenario),rows=prepareModelCatalogue(c,url);assert.equal(rows.length,scenario==='current-BASIC'?1:2);assert.equal(c.counts.packedModels,rows.length);
 for(const [i,row]of rows.entries()){assert.equal(c.models[i],sources[i].entry);assert.equal(row.sha256,sources[i].asset.sha256);assert.deepEqual(row.rootTranslation,[-834500,0,816500]);assert.equal(row.privateSourceInterpretationOnly,true);assert.equal(row.sourceIdentityReviewed,false);assert.equal(row.placementReviewed,false);assert.equal(row.publicationApproved,false);}
}
const wrong=makePrivateInterfaceCatalogue(sources,'original-Star');wrong.counts.packedModels=1;assert.throws(()=>prepareModelCatalogue(wrong,url),/Invalid compact model catalogue/);
assert.throws(()=>makePrivateInterfaceCatalogue(sources,'other'),/Unknown private source scenario/);
console.log(JSON.stringify({passed:true,cases:6,actualUnchangedProductionCatalogueValidator:true,sourceDecodeGeometryRendererDBLease:false}));
