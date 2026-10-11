import assert from 'node:assert/strict';
import {test} from 'node:test';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('file:///fixture/'),entry=new URL('entry.mjs',root);
const reader=files=>u=>{const p=u.pathname.slice(root.pathname.length);assert(Object.hasOwn(files,p),'Missing actual fixture module '+p);return Buffer.from(files[p]);};
test('actual complete audited production source graph',()=>{
 const actualRoot=new URL('../../../',import.meta.url),actualEntry=new URL('xl-one-peking-current-literal-production-geometry-v1-20261010.mjs',import.meta.url),snapshot=snapshotModuleClosure(actualEntry,actualRoot);
 assert(snapshot.modules.length>=29);assert(snapshot.modules.includes('3d-viewer/vendor/GLTFLoader.js'));assert(snapshot.modules.includes('3d-viewer/city/official-model-assets.js'));assert(verifyModuleClosure(snapshot,actualRoot));
});
test('nested relative imports and export-from',()=>{
 const files={'entry.mjs':"import {x} from './sub/a.mjs';",'sub/a.mjs':"export {x} from '../b.mjs';",'b.mjs':'export const x=1;'};const s=snapshotModuleClosure(entry,root,{reader:reader(files)});assert.equal(s.modules.length,3);assert(verifyModuleClosure(s,root,{reader:reader(files)}));
});
test('side-effect import included',()=>{const files={'entry.mjs':"import './a.mjs';",'a.mjs':''};assert.equal(snapshotModuleClosure(entry,root,{reader:reader(files)}).modules.length,2);});
test('query and fragment preserve actual file bytes',()=>{const files={'entry.mjs':"import './a.mjs?v=1'; import './a.mjs?v=2#x';",'a.mjs':''};assert.equal(snapshotModuleClosure(entry,root,{reader:reader(files)}).modules.length,2);});
test('cyclic modules bounded once per file',()=>{const files={'entry.mjs':"import './a.mjs';",'a.mjs':"import './entry.mjs';"};assert.equal(snapshotModuleClosure(entry,root,{reader:reader(files)}).modules.length,2);});
test('changed nested file rejected after snapshot',()=>{const files={'entry.mjs':"import './a.mjs';",'a.mjs':'export const x=1;'};const s=snapshotModuleClosure(entry,root,{reader:reader(files)});files['a.mjs']='export const x=2;';assert.throws(()=>verifyModuleClosure(s,root,{reader:reader(files)}));});
test('missing actual static dependency rejects',()=>{assert.throws(()=>snapshotModuleClosure(entry,root,{reader:reader({'entry.mjs':"import './missing.mjs';"})}));});
test('literal dynamic import rejects rather than incomplete coverage',()=>{assert.throws(()=>snapshotModuleClosure(entry,root,{reader:reader({'entry.mjs':"const m=import('./a.mjs');",'a.mjs':''})}));});
test('expression dynamic import rejects',()=>{assert.throws(()=>snapshotModuleClosure(entry,root,{reader:reader({'entry.mjs':'const m=import(variable);'})}));});
test('source-root escape rejects',()=>{assert.throws(()=>snapshotModuleClosure(entry,root,{reader:reader({'entry.mjs':"import '../outside.mjs';"})}));});
test('Node builtin imports require no project file',()=>{const files={'entry.mjs':"import {readFileSync} from 'node:fs';"};assert.equal(snapshotModuleClosure(entry,root,{reader:reader(files)}).modules.length,1);});
