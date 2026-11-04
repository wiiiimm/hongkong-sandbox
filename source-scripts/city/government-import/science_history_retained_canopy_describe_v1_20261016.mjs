import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {describeBuilding} from '../../../3d-viewer/city/building-geometry.js';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],b=JSON.parse(readFileSync(new URL(dir+'/form.json',root)));assert.equal(b.uid,'landsd/4760:0');const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);const d=describeBuilding(b);assert(d.foundationApplied&&d.openSided);assert(verifyModuleClosure(closure,root));writeFileSync(new URL(dir+'/description.json',root),JSON.stringify({parts:d.parts,inputHashes:closure.inputHashes}));
