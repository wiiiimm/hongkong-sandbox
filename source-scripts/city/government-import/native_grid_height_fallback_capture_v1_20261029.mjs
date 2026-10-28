/** Capture the production native patch grid height fallback, not a drawn mesh. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {ORIGIN,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[source,out]=process.argv.slice(2),hash=b=>createHash('sha256').update(b).digest('hex');
assert(source.startsWith('source-scripts/city/government-import/local/')&&!source.includes('..'));
assert(out.startsWith('docs/astra-city/government-import/')&&!out.includes('..'));
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const raw=readFileSync(new URL(source,root)),data=JSON.parse(raw),g=data.meta.georef;
assert(data.nativeMesh?.source?.numericalCoverageGap?.policy==='parent-grid-fallback'&&!data.patches?.length&&!data.hydro);
const position=[],index=[];
for(let r=0;r<data.h;r++)for(let c=0;c<data.w;c++)position.push(g.bE+c*g.aE-ORIGIN[0],terrainVertexHeight(data,r*data.w+c),ORIGIN[1]-(g.bN+r*g.aN));
for(let r=0;r<data.h-1;r++)for(let c=0;c<data.w-1;c++){const a=r*data.w+c;index.push(a,a+data.w,a+1,a+1,a+data.w,a+data.w+1);}
assert(verifyModuleClosure(closure,root));
writeFileSync(new URL(out,root),gzipSync(JSON.stringify({kind:'production-native-parent-grid-height-fallback',source,sourceSHA256:hash(raw),position,index,inputHashes:{...closure.inputHashes,[source]:hash(raw)},qualification:'Height-sampler fallback grid only. No native geometry, terrain file, source model or publication changes.'})));
console.log(JSON.stringify({gridTriangles:index.length/3,sourceSHA256:hash(raw)}));
