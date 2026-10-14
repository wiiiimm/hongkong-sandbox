/** Read-only literal closure for the unchanged runtime tools and current app. */
import {snapshotModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {existsSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('../../../',import.meta.url),entries=['source-scripts/city/government-import/acceptance-metrics.mjs','source-scripts/city/building-batch/validate_candidates.mjs','source-scripts/city/government-import/check-neighbours.mjs','source-scripts/city/government-import/check-native-neighbours.mjs','3d-viewer/city/app.js'],inputHashes={},closures=[];
for(const path of entries){const c=snapshotModuleClosure(new URL(path,root),root);closures.push(c);for(const[p,h]of Object.entries(c.inputHashes)){if(inputHashes[p])assert.equal(inputHashes[p],h);inputHashes[p]=h;}}
const dest=process.argv[2];assert(dest?.startsWith('docs/astra-city/government-import/')&&!dest.includes('..')&&!existsSync(new URL(dest,root)));writeFileSync(new URL(dest,root),JSON.stringify({inputHashes,entries,closures,computedImportsRejected:true,readOnlyCodeHashingOnly:true},null,2)+'\n');
