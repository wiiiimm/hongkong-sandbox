/** Exact literal/static/dynamic/resource closure only; does not import the renderer exporter. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),path=process.argv[2],verify=process.argv.includes('--verify');
assert.equal(path,'source-scripts/city/government-import/local/government-xl-citywalk134332-surviving-native-interface-context-v1-20261013/complete-exporter-module-closure.json');
const target=new URL(path,root);
if(verify)assert(verifyModuleClosure(JSON.parse(readFileSync(target)),root));
else{assert(!existsSync(target));writeFileSync(target,JSON.stringify(snapshotModuleClosure(new URL('citywalk134332_actual_surviving_native_attributes_draft_v1_20261013.mjs',import.meta.url),root),null,2)+'\n');}
console.log(JSON.stringify({completeExporterLiteralDynamicResourceClosureVerified:true,verifyOnly:verify,noRendererImport:true}));
