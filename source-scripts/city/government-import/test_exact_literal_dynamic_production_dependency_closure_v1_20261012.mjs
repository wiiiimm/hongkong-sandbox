import test from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,mkdirSync,writeFileSync,rmSync}from'node:fs';import {tmpdir}from'node:os';import {pathToFileURL}from'node:url';import {snapshotModuleClosure,verifyModuleClosure}from'./exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
function fixture(files,fn){const dir=mkdtempSync(tmpdir()+'/literal-closure-'),root=pathToFileURL(dir+'/');try{for(const [p,s]of Object.entries(files)){mkdirSync(new URL('.',new URL(p,root)),{recursive:true});writeFileSync(new URL(p,root),s);}fn(root,(p,s)=>writeFileSync(new URL(p,root),s));}finally{rmSync(dir,{recursive:true,force:true});}}
const snapshot=r=>snapshotModuleClosure(new URL('entry.mjs',r),r);
test('static, dynamic and transitive imports complete',()=>fixture({'entry.mjs':"import './a.mjs';await import('./b.mjs')",'a.mjs':"import './c.mjs'",'b.mjs':'','c.mjs':''},r=>assert.equal(snapshot(r).modules.length,4)));
test('reexports complete',()=>fixture({'entry.mjs':"export * from './a.mjs';export {x} from './b.mjs'",'a.mjs':'','b.mjs':'export const x=1'},r=>assert.equal(snapshot(r).modules.length,3)));
test('computed identifier rejected',()=>fixture({'entry.mjs':'const x="./a.mjs";import(x)'},r=>assert.throws(()=>snapshot(r),/Computed/)));
test('computed concatenation rejected',()=>fixture({'entry.mjs':"import('./a'+'.mjs')"},r=>assert.throws(()=>snapshot(r),/Computed/)));
test('template import nested in interpolation rejected',()=>fixture({'entry.mjs':'const x=`${import(`./a.mjs`)}`'},r=>assert.throws(()=>snapshot(r),/Computed/)));
test('comments strings regex cannot invent imports',()=>fixture({'entry.mjs':'// import(x)\nconst s="import(x)";const r=/import\\(x\\)/;'},r=>assert.equal(snapshot(r).modules.length,1)));
test('missing literal dependency rejected',()=>fixture({'entry.mjs':"import('./absent.mjs')"},r=>assert.throws(()=>snapshot(r))));
test('source root escape rejected',()=>fixture({'entry.mjs':"import('../outside.mjs')"},r=>assert.throws(()=>snapshot(r),/escapes/)));
test('external dependency rejected',()=>fixture({'entry.mjs':"import('https://example.com/a.mjs')"},r=>assert.throws(()=>snapshot(r),/nonrelative/)));
test('changed dependency bytes fail verification',()=>fixture({'entry.mjs':"import './a.mjs'",'a.mjs':''},(r,w)=>{const s=snapshot(r);w('a.mjs','export const changed=true');assert.throws(()=>verifyModuleClosure(s,r));}));
test('added graph dependency fail verification',()=>fixture({'entry.mjs':'','a.mjs':''},(r,w)=>{const s=snapshot(r);w('entry.mjs',"import './a.mjs'");assert.throws(()=>verifyModuleClosure(s,r));}));
const draco="this._loadLibrary('draco_decoder.js','text');this._loadLibrary('draco_wasm_wrapper.js','text');this._loadLibrary('draco_decoder.wasm','arraybuffer');";
const resources={'entry.mjs':"import './3d-viewer/vendor/DRACOLoader.js'",'3d-viewer/vendor/DRACOLoader.js':draco,'3d-viewer/vendor/draco_decoder.js':'/*opaque*/','3d-viewer/vendor/draco_wasm_wrapper.js':'/*opaque*/','3d-viewer/vendor/draco_decoder.wasm':Buffer.from([0,97,115,109])};
test('all three actual Draco resource families bound',()=>fixture(resources,r=>{const s=snapshot(r);assert.equal(s.resources.length,3);assert(verifyModuleClosure(s,r));}));
test('missing WASM rejected',()=>fixture(Object.fromEntries(Object.entries(resources).filter(([p])=>!p.endsWith('.wasm'))),r=>assert.throws(()=>snapshot(r))));
test('changed WASM rejected',()=>fixture(resources,(r,w)=>{const s=snapshot(r);w('3d-viewer/vendor/draco_decoder.wasm',Buffer.from([1]));assert.throws(()=>verifyModuleClosure(s,r));}));
test('computed Draco resource rejected',()=>fixture({...resources,'3d-viewer/vendor/DRACOLoader.js':draco.replace("'draco_decoder.js'",'resourceName')},r=>assert.throws(()=>snapshot(r),/Computed/)));
test('extra Draco resource call rejected',()=>fixture({...resources,'3d-viewer/vendor/DRACOLoader.js':draco+"this._loadLibrary('other.js','text');"},r=>assert.throws(()=>snapshot(r),/schema/)));
test('current full production closure binds literal codecs and resources',()=>{const root=new URL('../../../',import.meta.url),s=snapshotModuleClosure(new URL('3d-viewer/city/app.js',root),root);for(const p of ['3d-viewer/city/model-codecs.js','3d-viewer/vendor/DRACOLoader.js','3d-viewer/vendor/meshopt_decoder.module.js'])assert(s.modules.includes(p));assert.equal(s.resources.length,3);assert(verifyModuleClosure(s,root));});

test('bracket resource call cannot hide extra dependency',()=>fixture({...resources,'3d-viewer/vendor/DRACOLoader.js':draco+"this['_loadLibrary']('other.js','text');"},r=>assert.throws(()=>snapshot(r),/schema/)));
test('computed resource method name rejected',()=>fixture({...resources,'3d-viewer/vendor/DRACOLoader.js':draco+"this[methodName]('other.js','text');"},r=>assert.throws(()=>snapshot(r),/Computed resource method/)));
