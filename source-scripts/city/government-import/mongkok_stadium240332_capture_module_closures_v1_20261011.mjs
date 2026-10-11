/** Source-only producer closures; no runtime/browser acceptance or current capture approval. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],verify=process.argv.includes('--verify');
assert.equal(doc,'docs/astra-city/government-import/government-xl-mongkok-stadium240332-complete-current-ground-capture-v1-20261011/');
for(const [name,path]of Object.entries({'acceptance-module-closure.json':'source-scripts/city/government-import/acceptance-metrics.mjs','actual-attributes-module-closure.json':'source-scripts/city/government-import/mongkok_stadium240332_current_actual_render_attributes_v1_20261011.mjs'})){
 const target=new URL(doc+name,root);if(verify)assert(verifyModuleClosure(JSON.parse(readFileSync(target)),root));else{assert(!existsSync(target));writeFileSync(target,JSON.stringify(snapshotModuleClosure(new URL(path,root),root),null,2)+'\n');}
}
console.log(JSON.stringify({completeProducerModuleClosuresVerified:true,verifyOnly:verify}));
