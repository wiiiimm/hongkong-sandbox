/** No production imports or actor loads: dependency AST and exact byte schema only. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {snapshotModuleClosure,verifyModuleClosure} from '../../../../../source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../../../',import.meta.url),out=new URL('./closure-schema-validation.json',import.meta.url);
function assertClosureSchema(c){
 assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert.equal(c.unsupportedDynamicImports,0);assert.equal(c.completeAuditedLiteralImportClosure,true);assert.equal(c.computedImportsRejected,true);assert.equal(c.opaqueResourcesAreNotParsedModules,true);
 assert.equal(new Set(c.modules).size,c.modules.length);assert.equal(new Set(c.resources).size,c.resources.length);assert(c.resources.every(p=>!c.modules.includes(p)));assert.deepEqual(Object.keys(c.inputHashes).sort(),[...c.modules,...c.resources].sort());
 const expected=c.modules.includes('3d-viewer/vendor/DRACOLoader.js')?['3d-viewer/vendor/draco_decoder.js','3d-viewer/vendor/draco_decoder.wasm','3d-viewer/vendor/draco_wasm_wrapper.js']:[];assert.deepEqual([...c.resources].sort(),expected.sort());
 const resourceTypes={'3d-viewer/vendor/draco_decoder.js':'text','3d-viewer/vendor/draco_decoder.wasm':'arraybuffer','3d-viewer/vendor/draco_wasm_wrapper.js':'text'};assert.equal(c.resourceEdges.length,c.resources.length);assert.equal(new Set(c.resourceEdges.map(e=>e.to)).size,c.resourceEdges.length);for(const e of c.resourceEdges)assert.deepEqual(e,{from:'3d-viewer/vendor/DRACOLoader.js',to:e.to,responseType:resourceTypes[e.to],decoderDirectory:'3d-viewer/vendor/',opaqueRuntimeResource:true});
}

assert(!existsSync(out));
const loader=snapshotModuleClosure(new URL('3d-viewer/city/official-model-assets.js',root),root),terrain=snapshotModuleClosure(new URL('3d-viewer/city/world.js',root),root);
const helpers=['source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs','source-scripts/city/government-import/current_geometry_capture_preflight_20261011.mjs'].map(p=>snapshotModuleClosure(new URL(p,root),root));
for(const c of [loader,terrain,...helpers]){assertClosureSchema(c);assert(verifyModuleClosure(c,root));}
const acorn='source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs';assert(helpers[0].modules.includes(acorn));
const result={schemaValidationPassed:true,noProductionModuleImported:true,noActorLoaded:true,noDatabaseAccess:true,noReservation:true,completeRecursiveLoaderModuleClosure:loader,completeRecursiveTerrainModuleClosure:terrain,completeRecursiveCaptureHelperModuleClosures:helpers,actualAcornBytePin:{path:acorn,sha256:createHash('sha256').update(readFileSync(new URL(acorn,root))).digest('hex')},qualification:'Dependency syntax/schema and exact bytes only; no runtime, finite, architectural or acceptance credit.'};
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({schemaValidationPassed:true,loaderModules:loader.modules.length,loaderResources:loader.resources.length,terrainModules:terrain.modules.length,terrainResources:terrain.resources.length,helperModules:helpers.map(c=>c.modules.length),noProductionModuleImported:true}));
