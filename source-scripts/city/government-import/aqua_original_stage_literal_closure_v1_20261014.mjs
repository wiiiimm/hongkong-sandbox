/** Exact read-only closure for solid browser and current served app. */
import {snapshotModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeFileSync,existsSync} from 'node:fs';import assert from 'node:assert/strict';
const root=new URL('../../../',import.meta.url),entries=['source-scripts/city/government-import/aqua_marine193086_solid_original_browser_v1_20261014.mjs','3d-viewer/city/app.js'],inputHashes={},closures=[];
for(const path of entries){const c=snapshotModuleClosure(new URL(path,root),root);closures.push(c);for(const[p,h]of Object.entries(c.inputHashes)){if(inputHashes[p])assert.equal(inputHashes[p],h);inputHashes[p]=h;}}
const dest=process.argv[2];assert(dest?.startsWith('docs/astra-city/government-import/')&&!dest.includes('..')&&!existsSync(new URL(dest,root)));writeFileSync(new URL(dest,root),JSON.stringify({inputHashes,entries,closures,readOnlyCodeHashingOnly:true},null,2)+'\n');
