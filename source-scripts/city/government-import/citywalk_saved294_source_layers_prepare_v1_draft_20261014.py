"""ROOT-only current tuple/pin/import/schema/test/literal closure preparation."""
from pathlib import Path
import ast,json,sys,os,subprocess
import citywalk_saved294_source_layers_caller_v1_draft_20261014 as caller
ROOT,HERE=caller.ROOT,caller.HERE;P=caller.P;CALLER=Path(caller.__file__);RUNTIME=caller.RUNTIME
read,save,ref,check=caller.read,caller.save,caller.ref,caller.check;distinct=caller.distinct_refs
HELPER=HERE/'citywalk_saved294_source_layers_helper_v1_draft_20261014.mjs';TEST=HERE/'test_citywalk_saved294_source_layers_helper_v1_draft_20261014.mjs'
def code_closure():
 todo=[CALLER,Path(__file__)];seen=set();roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return [ref(p)for p in sorted(seen)]
def build():
 attrs=read(caller.CAP/'actual-attributes.json.gz');cap=read(caller.CAP/'current-interface-input.json.gz');inventory=read(caller.GLOBAL/'inventory.json.gz');native=read(caller.GLOBAL/'input.json.gz')
 historical=read(caller.BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014/input.json.gz')['historicalSceneManifestReference'];assert historical['sha256']==caller.delta.OLD
 relevant=[dict(path=p,sha256=h)for closure in [attrs['completeRecursiveProductionModuleClosure'],inventory['completeRecursiveProductionModuleClosure']]for p,h in closure['inputHashes'].items()]
 # Producer arithmetic/decoder code remains exact; unrelated old actor assets
 # and catalogue byte identity are not made whole-current-scene conditions.
 for hashes in [attrs['inputHashes'],inventory['inputHashes']]:
  relevant +=[dict(path=p,sha256=h)for p,h in hashes.items()if p.startswith('source-scripts/')and Path(p).suffix in ['.py','.mjs','.js']]
 relevant +=[ref(ROOT/cap['sourceCatalogue']['path'])]+[ref(ROOT/r['path'])for r in cap['rows']+cap['nativeContextRows']]
 relevant +=[r['source']for r in native['rows']if r['uid']in caller.TOWERS]
 live=read(ROOT/'3d-viewer/city/data/manifest.json');assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==caller.delta.CURRENT
 scope=read(caller.PRIOR_SCOPE)['currentState']['uids'];tile_refs=[]
 for tile in live['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  if any(f['uid']in scope for f in read(path)['buildings']):tile_refs.append(ref(path))
 names=['result.json','current-interface-input.json.gz','actual-attributes.json.gz']
 inputs=distinct(relevant+[ref(caller.CAP/n)for n in names]+[ref(caller.GLOBAL/n)for n in ['result.json','input.json.gz','inventory.json.gz']]+[ref(caller.OLD/'tower-support.json'),ref(caller.COMP),ref(caller.PROFILE),read(caller.PROFILE)['providerOriginalNPZ'],ref(caller.PRIOR_SCOPE),historical,ref(ROOT/'3d-viewer/city/data/manifest.json'),ref(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')]+[ref(ROOT/'3d-viewer'/url)for url in live['officialModelCatalogues']]+tile_refs)
 code=distinct(code_closure()+[ref(q)for q in [HELPER,TEST,RUNTIME,P/'METHOD.md',caller.FREEZER,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs']])
 for q in distinct(code+inputs):check(q)
 save(P/'draft-pins.json',dict(caller=ref(CALLER),runtime=ref(RUNTIME),codeRefs=code,inputRefs=inputs,relevantCapturedSourceAndCodeRefs=distinct(relevant),actualC00Archive=historical,nativeBoundsJob=read(caller.GLOBAL/'result.json')['jobId']))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),codeRefs=len(code),inputRefs=len(inputs),noNumericalCallDBLease=True)))
def prepare():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME);declared=distinct(pins['codeRefs']+pins['inputRefs']);commands=[];evidence=[]
 def fence():
  for q in declared:check(q)
 fence();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));evidence.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
 run('actual-eight-source-layer-fixtures',['node','--test',str(TEST)])
 run('actual-source-layer-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-source-layer-schema',[sys.executable,str(CALLER),'--schema-only'])
 closure=P/'literal-runtime-closure.json';js="import fs from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url),c=snapshotModuleClosure(new URL("+json.dumps(str(RUNTIME.relative_to(ROOT)))+",root),root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);fs.writeFileSync("+json.dumps(str(closure))+",JSON.stringify(c)+String.fromCharCode(10),{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length}));"
 run('actual-source-layer-literal-closure',['node','--input-type=module','-e',js]);evidence.append(ref(closure))
 for p,h in read(closure)['inputHashes'].items():check(dict(path=p,sha256=h));evidence.append(dict(path=p,sha256=h))
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),literalClosureRef=ref(closure),commands=commands,beforeEndAllDeclaredPinsVerified=True,fixtures=8,executedFixtureCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=distinct(evidence+[ref(Path(__file__)),ref(P/'draft-pins.json')]),noActualSavedPointPredicateDBLease=True))
 print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
