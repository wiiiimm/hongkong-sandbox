/** Use the actual production catalogue/dependency parser before browser work. */
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {prepareModelCatalogue} from '../../../3d-viewer/city/official-model-assets.js';
import {activationClosure} from '../../../3d-viewer/city/model-activation-groups.js';
import {modelSupportDependencies} from '../../../3d-viewer/city/model-support.js';
const root=new URL('../../../',import.meta.url),catalogue=JSON.parse(await readFile(new URL(process.argv[2],root)));
const models=prepareModelCatalogue(catalogue,'http://127.0.0.1:4177/private-original/catalogue.json');
const byUid=new Map(models.map(m=>[m.uid,m]));
assert.equal(byUid.size,models.length);
for(const model of models){
 const {ordered}=activationClosure(model.uid,byUid,modelSupportDependencies,()=>true,64);
 assert(ordered.includes(model.uid));
}
console.log(JSON.stringify({productionCatalogueParserPassed:true,models:models.length,sourceGeometryChanges:0,publication:false}));
