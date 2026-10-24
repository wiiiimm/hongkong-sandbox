import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync}from'node:fs';
import {auditValidatorSource,snapshotValidatorClosure,verifyValidatorClosure,IMPORT_STATEMENT,ROOT_STATEMENT,PATHS,VALIDATOR}from'./exact_existing_validator_runtime_closure_v1_20261014.mjs';
const root=new URL('../../../',import.meta.url),source=readFileSync(new URL(VALIDATOR,root)).toString();
test('actual unchanged statement binds exactly four default-root paths',()=>{const a=auditValidatorSource(source);assert.deepEqual(a.literalDynamicRoots,PATHS);assert(a.everyOtherComputedImportRejected&&a.productionSourceUnchanged);});
test('changed target or root declaration rejected',()=>{assert.throws(()=>auditValidatorSource(source.replace(PATHS[0],'3d-viewer/vendor/other.js')));assert.throws(()=>auditValidatorSource(source.replace(ROOT_STATEMENT,"const root='/tmp';")));});
test('additional computed import rejected despite approved statement',()=>assert.throws(()=>auditValidatorSource(source+'\nconst future="./unknown.js";await import(future);'),/Computed/));
test('additional unbound literal module rejected',()=>assert.throws(()=>auditValidatorSource(source+"\nimport './extra.js';"),/Unbound/));
test('known statement hidden in new scope rejected',()=>assert.throws(()=>auditValidatorSource(source.replace(IMPORT_STATEMENT,'async function hidden(){'+IMPORT_STATEMENT+'}')),/top-level/));
test('exact producer and all transitive hashes verify; changed producer fails',()=>{const s=snapshotValidatorClosure(root);assert.equal(s.closures.length,4);assert(verifyValidatorClosure(s,root));const reader=url=>new URL(url).pathname===new URL(VALIDATOR,root).pathname?Buffer.from(source+'\n// changed bytes\n'):readFileSync(url);assert.throws(()=>verifyValidatorClosure(s,root,{reader}));});
