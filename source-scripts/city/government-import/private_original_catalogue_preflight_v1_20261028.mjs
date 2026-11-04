/** Use the real catalogue validator before spending time in a private browser. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {prepareModelCatalogue} from '../../../3d-viewer/city/official-model-assets.js';
const root=new URL('../../../',import.meta.url),path=process.argv[2],url=process.argv[3];
assert(path.startsWith('source-scripts/city/government-import/local/'));
const raw=JSON.parse(readFileSync(new URL(path,root)));
assert(raw.diagnosticOnly===true&&raw.publicationApproved===false);
const models=prepareModelCatalogue(raw,url);
for(const model of models){
 assert.equal(model.publicationApproved,false);assert.equal(model.placementReviewed,false);
 const source=raw.models.find(m=>m.uid===model.uid),asset=new URL(source.asset,new URL(path,root));
 const bytes=readFileSync(asset);assert.equal(bytes.length,source.bytes);
 assert.equal(createHash('sha256').update(bytes).digest('hex'),source.sha256);
}
console.log(JSON.stringify({productionCatalogueValidatorPassed:true,exactOriginalAssets:models.length,sourceGeometryChanges:0,installationApproved:false}));
