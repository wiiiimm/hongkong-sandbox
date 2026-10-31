/** Describe unchanged production BASIC parts. No geometry or live-form writes. */
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {describeBuilding} from '../../../3d-viewer/city/building-geometry.js';
const root=new URL('../../../',import.meta.url);
const input=JSON.parse(readFileSync(new URL(process.argv[2],root)));
assert(input.building.uid===input.expectedUid&&!input.building.modelGeometry);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const description=describeBuilding(input.building);
assert(verifyModuleClosure(closure,root));
writeFileSync(new URL(process.argv[3],root),JSON.stringify({uid:input.expectedUid,description,inputHashes:closure.inputHashes,geometryChanges:0,publication:false}));
