/** DRAFT exact literal production import snapshots; no browser/runtime approval. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],verify=process.argv.includes('--verify');
assert.equal(doc,'docs/astra-city/government-import/government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011/');
for(const name of ['app','world','geo','native-terrain']){
 const target=new URL(doc+'runtime-'+name+'-closure.json',root);
 if(verify)assert(verifyModuleClosure(JSON.parse(readFileSync(target)),root));
 else{assert(!existsSync(target));writeFileSync(target,JSON.stringify(snapshotModuleClosure(new URL('3d-viewer/city/'+name+'.js',root),root),null,2)+'\n');}
}
console.log(JSON.stringify({literalRuntimeImportClosureVerified:true,verifyOnly:verify,runtimeAcceptance:false}));
