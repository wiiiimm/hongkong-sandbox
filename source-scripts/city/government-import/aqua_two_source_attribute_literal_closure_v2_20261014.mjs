/** Read-only exact literal closure; no renderer execution. */
import {snapshotModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {existsSync,writeFileSync} from 'node:fs';import assert from 'node:assert/strict';
const root=new URL('../../../',import.meta.url),entry='source-scripts/city/government-import/aqua_marine193086138449_current_actual_attributes_v2_20261014.mjs';
const closure=snapshotModuleClosure(new URL(entry,root),root),dest=process.argv[2];assert(dest?.startsWith('docs/astra-city/government-import/')&&!dest.includes('..')&&!existsSync(new URL(dest,root)));writeFileSync(new URL(dest,root),JSON.stringify({inputHashes:closure.inputHashes,closure,readOnlyCodeHashingOnly:true,noRendererExecuted:true},null,2)+'\n');
