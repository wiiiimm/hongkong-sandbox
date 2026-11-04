/** Offline serialization equivalence; no production geometry imports/leases/DB. */
import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';import {join} from 'node:path';
import {gunzipSync} from 'node:zlib';
import {exactJsonUtf8Fragments,writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const text=(value,budget=16384)=>Buffer.concat([...exactJsonUtf8Fragments(value,{maxFragmentBytes:budget})]).toString('utf8');
function equivalent(value,budget=16384){assert.equal(text(value,budget),JSON.stringify(value));}
test('complete renderer packet-shaped arrays/metadata preserve exact field order',()=>{
  const attribute={array:[-0,1.125,Math.fround(.1)],arrayType:'Float32Array',itemSize:3,count:1,normalized:false,byteSHA256:'a'.repeat(64),byteBase64:Buffer.from([0,127,128,255]).toString('base64')};
  equivalent({rows:[{uid:'landsd/338946:0',role:'owned-original',actualObjectGraph:[{name:'root',parentName:null}],actualRenderMeshes:[{allActualAttributes:{position:attribute},completeGeometryGroups:[],drawRange:{start:0,count:'Infinity'},actualMaterials:[{metadata:{version:4.6},color:0xffffff}],completeOriginalIndex:[0,1,2],matrixWorldFloat64:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]}]}],nativeContextRows:[],basicContextRows:[],inputHashes:{'a/b.mjs':'b'.repeat(64)},currentAcceptance:false});
});
test('actual saved Upton current forms/entry/proof structures are byte-equivalent',()=>{
  const p=new URL('../../../docs/astra-city/government-import/government-xl-upton-whole-parent-current-domain-capture-v1-20261012/input.json.gz',import.meta.url);
  const input=JSON.parse(gunzipSync(readFileSync(p)));
  assert.equal(input.ownedRows.length,3);assert.equal(input.nativeRows.length,1);assert.equal(input.basicRows.length,1911);
  equivalent({rows:input.ownedRows,nativeContextRows:input.nativeRows,basicContextRows:input.basicRows.slice(0,3),wholeDomain:input.domain,currentAcceptance:false});
});
test('million-value numeric array is equivalent with bounded fragments',()=>{
  const a=Array.from({length:1000000},(_,i)=>(i%13===0?-0:i%7===0?i+.125:-i));
  const chunks=[...exactJsonUtf8Fragments({position:a})];assert(chunks.length>100);
  assert(chunks.every(c=>c.length<=65536));assert.equal(Buffer.concat(chunks).toString(),JSON.stringify({position:a}));
});
test('large single attribute string never needs whole-string stringify',()=>{
  const s=('"\\\n\t\ud800\udc00😺漢字').repeat(100000);
  const chunks=[...exactJsonUtf8Fragments({byteBase64:s},{maxFragmentBytes:31})];
  assert(chunks.every(c=>c.length<=31));assert.equal(Buffer.concat(chunks).toString(),JSON.stringify({byteBase64:s}));
});
test('all control characters, quotation and backslash exactly escape',()=>equivalent({['k"\\\n']:Array.from({length:32},(_,i)=>String.fromCharCode(i)).join('')},16));
test('surrogate boundaries and lone surrogates remain well-formed JSON',()=>equivalent(['a'.repeat(1023)+'😺', '\ud800', '\udc00', '\ud800a', 'é漢\u2028\u2029'],16));
test('undefined functions symbols omit only object fields',()=>equivalent({keep:null,u:undefined,f:()=>1,s:Symbol('x'),array:[undefined,()=>1,Symbol(),null]}));
test('sparse arrays retain null slots and ignore extra properties',()=>{const a=[];a.length=5;a[2]=3;a.extra=4;equivalent(a);});
test('nonfinite numbers and negative zero match JSON semantics',()=>equivalent([NaN,Infinity,-Infinity,-0,Number.MIN_VALUE,Number.MAX_VALUE]));
test('integer object keys/enumerable strings retain native ordering',()=>{const a={z:1,2:'two',1:'one',a:3};a[Symbol()]=5;Object.defineProperty(a,'hidden',{value:4});equivalent(a);});
test('toJSON key/date and boxed primitives match existing material metadata',()=>equivalent({date:new Date('2026-10-12T00:00:00Z'),x:{toJSON(key){return {key};}},n:new Number(2),s:new String('x'),b:new Boolean(false)}));
test('shared repeated objects allowed but cycles and BigInt rejected',()=>{const a={x:1};equivalent([a,a]);a.self=a;assert.throws(()=>text(a),/circular/);assert.throws(()=>text(1n),/BigInt/);});
test('undefined root yields no JSON fragments',()=>assert.equal(text(undefined),''));
test('unsupported nonplain containers fail closed instead of dropping data',()=>{
  for(const x of [new Map([['x',1]]),new Set([1]),new Float32Array([1]),new(class X{constructor(){this.a=1;}})])assert.throws(()=>text(x),/nonplain/);
});
test('gzip file decompresses to exactly native JSON and cannot overwrite',async()=>{
  const d=mkdtempSync(join(tmpdir(),'upton-json-test-'));try{
    const p=join(d,'out.json.gz'),value={a:Array.from({length:20000},(_,i)=>i),s:'😺\\"\n'};
    const r=await writeExactJsonGzip(p,value);assert(r.fragments>1);
    assert.equal(gunzipSync(readFileSync(p)).toString(),JSON.stringify(value));
    assert(!existsSync(p+'.serialization-partial'));await assert.rejects(writeExactJsonGzip(p,value),/overwrite/);
  }finally{rmSync(d,{recursive:true,force:true});}
});
test('failed serialization preserves partial artifact, never final output',async()=>{
  const d=mkdtempSync(join(tmpdir(),'upton-json-fail-'));try{
    const p=join(d,'out.json.gz');await assert.rejects(writeExactJsonGzip(p,{a:1,b:2n}),/BigInt/);
    assert(!existsSync(p));assert(existsSync(p+'.serialization-partial'));
  }finally{rmSync(d,{recursive:true,force:true});}
});
