/** Thin adapter to the existing reviewed triangle engine; fail if required anchors change. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../../../',import.meta.url),upstream=new URL('source-scripts/city/assembly-support-review/review.mjs',root);let source=readFileSync(upstream,'utf8');
function replace(old,value){if(source.split(old).length!==2)throw Error('Support engine anchor changed: '+old.slice(0,80));source=source.replace(old,value);}
replace("from './triangles.mjs'","from '../assembly-support-review/triangles.mjs'");
replace("read('docs/astra-city/landmark-preflight/report.json')","read('source-scripts/city/residual-support-review/input.json')");
replace("const contexts=[...entries.values()]",`for(const e of prepareModelCatalogue(read('source-scripts/city/residential-support-review/support-catalogue.json'),'http://review.local/support/catalogue.json')){const folder=e.uid==='landsd/54170:0'?'source-scripts/city/residential-support-review/candidates/':'source-scripts/city/residential-support-review/omitted-support/candidates/';if(!entries.has(e.uid))entries.set(e.uid,{...e,path:resolve(root,folder,e.asset),state:'candidate'});}
const contexts=[...entries.values()]`);
replace("entries.set(e.uid,{...e,path:resolve(root,dirname(candidatePath),'assets',e.asset),state:'candidate'});","if(!entries.has(e.uid))entries.set(e.uid,{...e,path:resolve(root,dirname(candidatePath),'assets',e.asset),state:'candidate'});");

const generated=new URL('./review-adapter.generated.mjs',import.meta.url);writeFileSync(generated,source);writeFileSync(new URL('docs/astra-city/residual-support-review/engine-input.json',root),JSON.stringify({upstream:'source-scripts/city/assembly-support-review/review.mjs',upstreamSHA256:createHash('sha256').update(readFileSync(upstream)).digest('hex'),modifications:['Additional source-accounted catalogue/context','Supplemental exact-ID review input','Current installed native terrain patches'],method:'Existing triangle engine unchanged; adapter fails on changed injection anchors.'},null,2)+'\n');
await import(generated.href);
