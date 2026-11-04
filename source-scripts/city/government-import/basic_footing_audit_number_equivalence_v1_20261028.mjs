/** Exact production geometry equality for an audit-only JSON number spelling. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),inputPath=process.argv[2],outputPath=process.argv[3],sha=b=>createHash('sha256').update(b).digest('hex'),input=JSON.parse(readFileSync(new URL(inputPath,root)));
for(const [path,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(path,root))),h);
const current=JSON.parse(readFileSync(new URL(input.tile,root))).buildings.find(b=>b.uid===input.uid),prepared=JSON.parse(readFileSync(new URL(input.proposalInput,root))).building;
assert.deepEqual(current,prepared);const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const rows=[];
for(const foundation of [false,true]){
 const a=createBuildingGeometry({...current,...(foundation?{foundationBase:input.foundationBase}:{})}),b=createBuildingGeometry({...prepared,...(foundation?{foundationBase:input.foundationBase}:{})});
 assert.deepEqual(Object.keys(a.attributes).sort(),Object.keys(b.attributes).sort());const attributes={};
 for(const name of Object.keys(a.attributes)){
  const x=a.attributes[name],y=b.attributes[name];assert.equal(x.itemSize,y.itemSize);assert.equal(x.normalized,y.normalized);assert.deepEqual(x.array,y.array);
  attributes[name]=sha(Buffer.from(x.array.buffer,x.array.byteOffset,x.array.byteLength));
 }
 assert.deepEqual(a.index?.array??null,b.index?.array??null);assert.deepEqual(a.groups,b.groups);rows.push({foundation,attributes,indexEqual:true,groupsEqual:true});a.dispose();b.dispose();
}
assert(verifyModuleClosure(closure,root));for(const [path,h]of Object.entries(input.inputHashes))assert.equal(sha(readFileSync(new URL(path,root))),h);
writeFileSync(new URL(outputPath,root),JSON.stringify({uid:input.uid,exactJavaScriptSourceFormValuesEqual:true,exactAllProductionGeometryAttributesBeforeAndAfterEqual:true,rows,inputHashes:{...input.inputHashes,...closure.inputHashes},completeRecursiveProductionModuleClosure:closure,sourceGeometryChanges:0,installationApproved:false}));
