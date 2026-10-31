/** Exact module byte closure for Block16 current diagnostic producers. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],verify=process.argv.includes('--verify'),sha=b=>createHash('sha256').update(b).digest('hex');
assert.equal(doc,'docs/astra-city/government-import/government-xl-parkview-block16-fresh-current-physical-capture-v1-20261011/');
const validator='source-scripts/city/building-batch/validate_candidates.mjs',source=readFileSync(new URL(validator,root)).toString(),literal="const imports=await Promise.all(['3d-viewer/vendor/three.module.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/geo.js','3d-viewer/city/world.js'].map(p=>import(pathToFileURL(resolve(root,p)))));";
assert(source.includes(literal));assert.equal([...source.matchAll(/\bimport\s*\(/g)].length,1);
const roots=['3d-viewer/vendor/three.module.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/geo.js','3d-viewer/city/world.js'];
const producers={'acceptance-module-closure.json':'source-scripts/city/government-import/acceptance-metrics.mjs','native-module-closure.json':'source-scripts/city/government-import/parkview_block16_check_all_current_native_20261011.mjs','neighbour-module-closure.json':'source-scripts/city/government-import/check-neighbours.mjs'};
for(const [name,path]of Object.entries(producers)){
 const target=new URL(doc+name,root);
 if(verify)assert(verifyModuleClosure(JSON.parse(readFileSync(target)),root));
 else{assert(!existsSync(target));writeFileSync(target,JSON.stringify(snapshotModuleClosure(new URL(path,root),root),null,2)+'\n');}
}
const target=new URL(doc+'validation-module-closure.json',root);
if(verify){const d=JSON.parse(readFileSync(target));assert.equal(d.producer.sha256,sha(readFileSync(new URL(validator,root))));assert.equal(d.auditedLiteralDynamicImportCall,literal);assert.deepEqual(d.literalDynamicRoots,roots);for(const c of d.closures)assert(verifyModuleClosure(c,root));assert.equal(d.captureHelper.sha256,sha(readFileSync(new URL(import.meta.url))));}
else{assert(!existsSync(target));writeFileSync(target,JSON.stringify({producer:{path:validator,sha256:sha(readFileSync(new URL(validator,root)))},captureHelper:{path:'source-scripts/city/government-import/parkview_block16_capture_module_closures_20261011.mjs',sha256:sha(readFileSync(new URL(import.meta.url)))},auditedLiteralDynamicImportCall:literal,literalDynamicRoots:roots,closures:roots.map(p=>snapshotModuleClosure(new URL(p,root),root)),allOnlyDynamicTargetsExplicitlyBound:true},null,2)+'\n');}
console.log(JSON.stringify({completeAcceptanceNativeNeighbourAndValidationModuleClosuresVerified:true,verifyOnly:verify}));
