/** Bind only the reviewed validator's four deterministic pathToFileURL imports. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {parse} from './dependency-closure-vendor/acorn-8.8.1/acorn.mjs';
import {literalDependencies,snapshotModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
export const VALIDATOR='source-scripts/city/building-batch/validate_candidates.mjs';
export const ROOT_STATEMENT="const root=realpathSync(resolve(option('--root',fileURLToPath(new URL('../../../',import.meta.url)))));";
export const IMPORT_STATEMENT="const imports=await Promise.all(['3d-viewer/vendor/three.module.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/geo.js','3d-viewer/city/world.js'].map(p=>import(pathToFileURL(resolve(root,p)))));";
export const PATHS=['3d-viewer/vendor/three.module.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/geo.js','3d-viewer/city/world.js'];
export function auditValidatorSource(source){
 const ast=parse(source,{ecmaVersion:'latest',sourceType:'module'}),top=ast.body.map(n=>source.slice(n.start,n.end));
 assert.equal(top.filter(s=>s===ROOT_STATEMENT).length,1,'Existing top-level root declaration differs');
 assert.equal(top.filter(s=>s===IMPORT_STATEMENT).length,1,'Existing top-level deterministic import statement differs');
 // The original statement is fully matched before removing it from parser input.
 // Original producer bytes are always hashed; production source is never edited.
 const remaining=literalDependencies(source.replace(IMPORT_STATEMENT,''),VALIDATOR);
 assert(remaining.imports.every(q=>q.specifier.startsWith('node:')),'Unbound additional validator module');
 assert.equal(remaining.libraries.length,0);assert.equal(remaining.decoderDirectories.length,0);
 return {auditedRootDeclaration:ROOT_STATEMENT,auditedLiteralDynamicImportCall:IMPORT_STATEMENT,literalDynamicRoots:[...PATHS],remainingLiteralDependencies:remaining,onlyExistingDeterministicComputedImportBound:true,everyOtherComputedImportRejected:true,productionSourceUnchanged:true};
}
export function snapshotValidatorClosure(root,{reader=readFileSync}={}){
 root=new URL(root);const url=new URL(VALIDATOR,root),raw=reader(url),audit=auditValidatorSource(raw.toString('utf8')),producer={path:VALIDATOR,sha256:createHash('sha256').update(raw).digest('hex')},inputHashes={[VALIDATOR]:producer.sha256},closures=[];
 for(const p of PATHS){const c=snapshotModuleClosure(new URL(p,root),root,{reader});closures.push(c);for(const[path,sha]of Object.entries(c.inputHashes)){if(inputHashes[path])assert.equal(inputHashes[path],sha);inputHashes[path]=sha;}}
 return {producer,...audit,inputHashes,closures,defaultRootCLIUsed:true,allFourRuntimeTargetsAndTransitiveBytesBound:true};
}
export function verifyValidatorClosure(snapshot,root,options){assert.deepEqual(snapshot,snapshotValidatorClosure(root,options));return true;}
