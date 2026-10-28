/** Bind/verify actual viewer inputs around a private browser observation. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const [mode,path]=process.argv.slice(2),root=new URL('../../../',import.meta.url);
assert(['capture','verify'].includes(mode)&&path.startsWith('docs/astra-city/government-import/')&&!path.includes('..'));
const closure=mode==='capture'?snapshotModuleClosure(new URL('3d-viewer/city/app.js',root),root):JSON.parse(readFileSync(new URL(path,root)));
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
assert(verifyModuleClosure(closure,root),'Actual viewer runtime changed during observation');
if(mode==='capture')writeFileSync(new URL(path,root),JSON.stringify(closure));
console.log(JSON.stringify({mode,verified:true,inputs:Object.keys(closure.inputHashes).length,opaqueResources:closure.resources.length}));
