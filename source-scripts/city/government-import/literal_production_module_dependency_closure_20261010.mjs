/** Byte pins for the audited relative literal-import production loader graph. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const sha=b=>createHash('sha256').update(b).digest('hex');
export function snapshotModuleClosure(entryURL,rootURL,{reader=readFileSync}={}){
 const root=new URL(rootURL),hashes={},modules=[];
 assert(root.protocol==='file:'&&root.pathname.endsWith('/'));
 function visit(url){
  const u=new URL(url);assert(u.protocol==='file:'&&u.pathname.startsWith(root.pathname),'Module escapes source root');
  const path=decodeURIComponent(u.pathname.slice(root.pathname.length));if(hashes[path])return;
  // Query/fragment are module identities, not different filesystem bytes.
  const file=new URL(u);file.search='';file.hash='';const raw=reader(file),source=raw.toString('utf8');hashes[path]=sha(raw);modules.push(path);
  assert(!/\bimport\s*\(/.test(source),'Unbound dynamic import in '+path);
  for(const m of source.matchAll(/\b(?:from|import)\s*['"]([^'"]+)['"]/g))if(m[1].startsWith('.'))visit(new URL(m[1],u));
 }
 visit(entryURL);return {inputHashes:hashes,modules,unsupportedDynamicImports:0,completeAuditedLiteralImportClosure:true};
}
export function verifyModuleClosure(snapshot,rootURL,{reader=readFileSync}={}){
 const root=new URL(rootURL);assert(snapshot.completeAuditedLiteralImportClosure&&snapshot.unsupportedDynamicImports===0);
 assert(snapshot.modules.length===Object.keys(snapshot.inputHashes).length&&new Set(snapshot.modules).size===snapshot.modules.length);
 for(const [path,pin] of Object.entries(snapshot.inputHashes)){
  const u=new URL(path,root);assert(u.protocol==='file:'&&u.pathname.startsWith(root.pathname),'Module escapes source root');
  assert.equal(sha(reader(u)),pin,'Production module bytes changed: '+path);
 }
 return true;
}
