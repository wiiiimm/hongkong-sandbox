/** Read-only exact literal closure including the existing browser-evaluated URL. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {literalDependencies,snapshotModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),hashes={},edges=[],serverRoutes=[];
function visit(url){const u=new URL(url);u.search='';u.hash='';assert(u.protocol==='file:'&&u.pathname.startsWith(root.pathname));const path=u.pathname.slice(root.pathname.length);if(hashes[path])return;const b=readFileSync(u);hashes[path]=createHash('sha256').update(b).digest('hex');
 const d=literalDependencies(b.toString(),path);assert(!d.libraries.length&&!d.decoderDirectories.length);
 for(const q of d.imports){if(q.specifier.startsWith('node:'))continue;let target;if(q.specifier==='/city/model-spatial-index.js'){target=new URL('3d-viewer/city/model-spatial-index.js',root);serverRoutes.push({from:path,specifier:q.specifier,to:'3d-viewer/city/model-spatial-index.js',existingBrowserEvaluatedLiteralRoute:true});}else{assert(q.specifier.startsWith('.'),'Unknown source route');target=new URL(q.specifier,u);}edges.push({from:path,...q,to:target.pathname.slice(root.pathname.length)});visit(target);}
}
visit(new URL('./upton_dimension_joint_resolution_browser_v2_20261014.mjs',import.meta.url));assert.equal(serverRoutes.length,1);
const app=snapshotModuleClosure(new URL('3d-viewer/city/app.js',root),root);for(const [p,h]of Object.entries(app.inputHashes)){if(hashes[p])assert.equal(hashes[p],h);hashes[p]=h;}
const path=process.argv[2];assert(path?.startsWith('docs/astra-city/government-import/')&&!path.includes('..')&&!existsSync(new URL(path,root)));writeFileSync(new URL(path,root),JSON.stringify({inputHashes:hashes,literalEdges:edges,exactAppClosure:app,explicitExistingServerRoutes:serverRoutes,computedImportsRejected:true,readOnlyCodeHashingOnly:true},null,2)+'\n');
