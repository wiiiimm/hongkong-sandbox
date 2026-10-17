/** Source catalogue support closure audit; does not load models or change data. */
import {readFile,writeFile}from 'node:fs/promises';
import {createHash}from 'node:crypto';
import {modelSupportDependencies,supportedModelPlan}from '../../../3d-viewer/city/model-support.js';
import {modelBudget}from '../../../3d-viewer/city/official-model-assets.js';
import {MODEL_PROFILES}from '../../../3d-viewer/city/official-models.js';
const root=new URL('../../../',import.meta.url),read=async p=>JSON.parse(await readFile(new URL(p,root),'utf8'));
const manifestPath='3d-viewer/city/data/manifest.json',manifest=await read(manifestPath),models=new Map(),hashes={};
for(const path of [manifestPath,...manifest.officialModelCatalogues.map(p=>'3d-viewer/'+p)]){
 const bytes=await readFile(new URL(path,root));hashes[path]=createHash('sha256').update(bytes).digest('hex');
 if(path!==manifestPath)for(const m of JSON.parse(bytes).models){if(models.has(m.uid))throw new Error('Duplicate source UID '+m.uid);models.set(m.uid,m);}
}
const rows=[];for(const m of models.values()){
 const dependencies=modelSupportDependencies(m);if(!dependencies.length)continue;
 const plan=supportedModelPlan([m.uid],models,MODEL_PROFILES.mobile,modelBudget,()=>true);
 rows.push({uid:m.uid,dependencies,closure:plan.wanted,held:plan.blocked.get(m.uid)||null,budget:plan.used});
}
const report={issue:'HKS-214',models:models.size,withDependencies:rows.length,held:rows.filter(r=>r.held).length,rows,inputHashes:hashes,scope:'Catalogue closure and unchanged mobile budgets; actual source tile readiness is checked by the runtime and is not asserted by this static audit.'};
await writeFile(new URL('docs/astra-city/model-support-review/catalogue-audit.json',root),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({models:report.models,withDependencies:report.withDependencies,held:report.held}));
