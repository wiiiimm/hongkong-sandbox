/** Exact-byte closure; parser-backed literal imports only, opaque Draco decoder resources. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {parse} from './dependency-closure-vendor/acorn-8.8.1/acorn.mjs';
const sha=b=>createHash('sha256').update(b).digest('hex');
const DRACO='3d-viewer/vendor/DRACOLoader.js',CODECS='3d-viewer/city/model-codecs.js';
const LIBRARIES=[['draco_decoder.js','text'],['draco_decoder.wasm','arraybuffer'],['draco_wasm_wrapper.js','text']];
function walk(node,fn){if(!node||typeof node!=='object')return;if(typeof node.type==='string')fn(node);for(const [key,value]of Object.entries(node)){if(key==='start'||key==='end')continue;if(Array.isArray(value))for(const item of value)walk(item,fn);else if(value&&typeof value==='object')walk(value,fn);}}
export function literalDependencies(source,path){
 const ast=parse(source,{ecmaVersion:'latest',sourceType:'module'}),imports=[],libraries=[],decoderDirectories=[];
 walk(ast,node=>{
  if((path===DRACO||path===CODECS)&&node.type==='CallExpression'&&node.callee.type==='MemberExpression'&&node.callee.computed)assert(node.callee.property.type==='Literal'&&typeof node.callee.property.value==='string','Computed resource method in '+path);
  const method=node.type==='CallExpression'&&node.callee.type==='MemberExpression'?(node.callee.computed?node.callee.property.value:node.callee.property.name):null;
  if(['ImportDeclaration','ExportNamedDeclaration','ExportAllDeclaration'].includes(node.type)&&node.source)imports.push({kind:node.type,specifier:node.source.value});
  if(node.type==='ImportExpression'){
   assert(node.source.type==='Literal'&&typeof node.source.value==='string','Computed dynamic import in '+path);
   assert(!node.options,'Unsupported dynamic import options in '+path);imports.push({kind:'literal-dynamic',specifier:node.source.value});
  }
  if(path===DRACO&&node.type==='CallExpression'&&node.callee.type==='MemberExpression'&&method==='_loadLibrary'){
   assert(node.arguments.length===2&&node.arguments.every(n=>n.type==='Literal'&&typeof n.value==='string'),'Computed Draco resource in '+path);libraries.push(node.arguments.map(n=>n.value));
  }
  if(path===CODECS&&node.type==='CallExpression'&&node.callee.type==='MemberExpression'&&method==='setDecoderPath'){
   const a=node.arguments[0];assert(node.arguments.length===1&&a?.type==='MemberExpression'&&a.property.name==='href','Unbound decoder directory');const u=a.object;
   assert(u?.type==='NewExpression'&&u.callee.name==='URL'&&u.arguments.length===2&&u.arguments[0].type==='Literal'&&typeof u.arguments[0].value==='string','Unbound decoder directory');const base=u.arguments[1];
   assert(base.type==='MemberExpression'&&base.property.name==='url'&&base.object.type==='MetaProperty'&&base.object.meta.name==='import'&&base.object.property.name==='meta','Unbound decoder directory base');decoderDirectories.push(u.arguments[0].value);
  }
 });
 if(path===DRACO)assert.deepEqual(libraries.sort((a,b)=>a[0].localeCompare(b[0])),LIBRARIES,'Draco resource schema changed');
 if(path===CODECS)assert.deepEqual(decoderDirectories,['../vendor/'],'Decoder directory changed');
 return {imports,libraries,decoderDirectories};
}
export function snapshotModuleClosure(entryURL,rootURL,{reader=readFileSync}={}){
 const root=new URL(rootURL),inputHashes={},modules=[],resources=[],importEdges=[],resourceEdges=[];assert(root.protocol==='file:'&&root.pathname.endsWith('/'));
 function located(url){const u=new URL(url);assert(u.protocol==='file:'&&u.pathname.startsWith(root.pathname),'Dependency escapes source root');const path=decodeURIComponent(u.pathname.slice(root.pathname.length));assert(!path.split('/').includes('..'),'Encoded path escape');const file=new URL(u);file.search='';file.hash='';return {u,file,path};}
 function visit(url){const {u,file,path}=located(url);if(inputHashes[path])return;const raw=reader(file);inputHashes[path]=sha(raw);modules.push(path);const found=literalDependencies(raw.toString('utf8'),path);
  for(const {kind,specifier}of found.imports){assert(typeof specifier==='string');if(specifier.startsWith('node:')){importEdges.push({from:path,kind,specifier,builtin:true});continue;}assert(specifier.startsWith('.'),'Unbound nonrelative import '+specifier+' in '+path);const target=located(new URL(specifier,u));importEdges.push({from:path,kind,specifier,to:target.path});visit(target.u);}
  for(const [name,responseType]of found.libraries){const target=located(new URL(name,u));const raw=reader(target.file);assert(!inputHashes[target.path],'Resource/module role overlap');inputHashes[target.path]=sha(raw);resources.push(target.path);resourceEdges.push({from:path,to:target.path,responseType,decoderDirectory:'3d-viewer/vendor/',opaqueRuntimeResource:true});}
 }
 visit(entryURL);assert(!modules.includes(CODECS)||modules.includes(DRACO),'Codec route missing Draco module');
 return {schema:'exact-literal-static-dynamic-resource-closure-v1',entryPath:located(entryURL).path,inputHashes,modules,resources,importEdges,resourceEdges,unsupportedDynamicImports:0,completeAuditedLiteralImportClosure:true,computedImportsRejected:true,opaqueResourcesAreNotParsedModules:true};
}
export function verifyModuleClosure(snapshot,rootURL,{reader=readFileSync}={}){
 assert(snapshot.schema==='exact-literal-static-dynamic-resource-closure-v1');assert(snapshot.completeAuditedLiteralImportClosure&&snapshot.unsupportedDynamicImports===0&&snapshot.computedImportsRejected);
 assert.deepEqual(snapshot,snapshotModuleClosure(new URL(snapshot.entryPath,rootURL),rootURL,{reader}),'Dependency graph or bytes changed');return true;
}
