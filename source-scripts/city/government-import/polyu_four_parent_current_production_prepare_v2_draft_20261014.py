"""ROOT-only completed-nominee pins, seven fixtures, import/schema and literal closure."""
from pathlib import Path
import ast,json,gzip,hashlib,sys,subprocess,os
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-polyu-four-compatible-parent-current-production-v2-20261014-proposal'
CALLER=HERE/'polyu_four_parent_current_production_caller_v2_draft_20261014.py';RUNTIME=HERE/'polyu_four_parent_current_production_runtime_v2_draft_20261014.mjs'
HELPER=HERE/'polyu_four_parent_current_capture_binding_v2_draft_20261014.py';TEST=HERE/'test_polyu_four_parent_current_capture_binding_v2_draft_20261014.py'
NOM=BASE/'government-xl-polyu-four-compatible-parent-region-nomination-v1-20261014';CAP=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014'
UPTON=BASE/'government-xl-upton-joint-original-functional-installed-v2-20261014';AQUA=BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014'
MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 with p.open('x')as f:json.dump(v,f,sort_keys=True,separators=(',',':'),allow_nan=False);f.write('\n')
def distinct(qs):
 d={}
 for q in qs:
  if q['path']in d:assert d[q['path']]==q
  d[q['path']]=q
 return [d[p]for p in sorted(d)]
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
 todo=[CALLER,HELPER,TEST,Path(__file__),HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'resolve-pass-indexed-parent-clipping.py'];seen=set()
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
 return sorted(seen)
def build():
 from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
 q=read(NOM/'result.json');assert q['jobId']=='f2df44cd1ac7864fd9e0a31b55b635679d7ad8f1356eafc2bb27f28423da8400'and ref(NOM/'result.json')['sha256']=='6e63791bab6ee7c1f2a802a47aaf95ed1e2eaf006852f90f83c4c26662e5c025'
 nom=read(NOM/'private-compatible-current-parent-append-nomination.json.gz');attrs=read(CAP/'complete-fresh-current-native59527-and24-BASIC.json.gz');input=read(CAP/'input.json.gz');manifest=read(MANIFEST)
 # Literal relevant old source/code bytes must be unchanged. Only the old
 # manifest reference is resolved to its explicitly authenticated archive.
 relevant=[]
 for path,h in attrs['inputHashes'].items():
  if path=='3d-viewer/city/data/manifest.json':continue
  if path.startswith('3d-viewer/')or path.endswith(('.js','.mjs')):relevant.append(dict(path=path,sha256=h))
 relevant=distinct(relevant)
 for pin in relevant:assert ref(ROOT/pin['path'])==pin,pin
 inputs=[ref(MANIFEST),ref(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'),ref(NOM/'result.json'),ref(NOM/'ROOT-VERIFIED.json'),ref(NOM/'private-compatible-current-parent-append-nomination.json.gz'),nom['previousApprovedCandidate'],
  ref(CAP/'input.json.gz'),ref(CAP/'complete-fresh-current-native59527-and24-BASIC.json.gz'),ref(CAP/'native59527-unchanged-provider-original-world.json.gz'),input['historicalSceneManifestReference']]+relevant
 for folder in [UPTON,AQUA]:inputs +=[ref(folder/n)for n in ['result.json','ROOT-VERIFIED.json','installed-acceptance.json']]
 for url in manifest['officialModelCatalogues']:inputs.append(ref(ROOT/'3d-viewer'/url))
 for entry in manifest['terrainPatches']:inputs.append(ref(ROOT/'3d-viewer'/entry['url']))
 inputs +=[ref(P/'actual-scene-delta-diagnosis.json')]+[ref(BASE/'government-xl-polyu-four-compatible-parent-current-production-v1-20261014-proposal'/n)for n in ['draft-pins.json','draft-files.json','METHOD.md','binding-validation.json','actual-six-binding-fixtures.log','actual-current-capture-import.log','actual-current-capture-schema.log']]+[ref(HERE/n)for n in ['polyu_four_parent_current_capture_binding_v1_draft_20261014.py', 'test_polyu_four_parent_current_capture_binding_v1_draft_20261014.py', 'polyu_four_parent_current_production_caller_v1_draft_20261014.py', 'polyu_four_parent_current_production_runtime_v1_draft_20261014.mjs', 'polyu_four_parent_current_production_prepare_v1_draft_20261014.py']]
 inputs +=[ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(ROOT/'3d-viewer/city/data/government-native-79882-0.json')]
 for pin in distinct(inputs):assert ref(ROOT/pin['path'])==pin
 code=[ref(p)for p in code_paths()]+[ref(RUNTIME),ref(P/'METHOD.md'),ref(P/'runtime-historical-append-to-current-four-parent.patch'),ref(HERE/'polyu_compact_runtime_mesh_projection_v1_draft_20261014.mjs'),ref(HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'),ref(HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs'),ref(HERE/'exact_incremental_json_gzip_v1_20261012.mjs')]
 save(P/'draft-pins.json',dict(caller=ref(CALLER),runtime=ref(RUNTIME),codeRefs=distinct(code),inputRefs=distinct(inputs),completedNominationJob=q['jobId'],
  previousApprovedCandidate=nom['previousApprovedCandidate'],completeNewMeshBinding=mesh_binding(nom['newNativeMesh']),relevantActorSourceAndFormRefs=relevant,
  uptonInstalledManifestSHA256=read(UPTON/'installed-acceptance.json')['manifest']['sha256'],currentManifestSHA256=ref(MANIFEST)['sha256']))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),codeRefs=len(distinct(code)),inputRefs=len(distinct(inputs)))))
def prepare():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME);declared=distinct(pins['codeRefs']+pins['inputRefs'])
 def fence():
  for q in declared:assert ref(ROOT/q['path'])==q
 fence();commands=[];refs=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));refs.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
  return log
 log=run('actual-seven-binding-fixtures',[sys.executable,str(TEST),'-v']);text=log.read_text();assert 'Ran 7 tests'in text and '\nOK\n'in text
 validation=P/'binding-validation.json';save(validation,dict(passedTests=7,failedTests=0,exitCode=0,executedCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(TEST),ref(log)]));refs.append(ref(validation))
 run('actual-current-capture-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-current-capture-schema',[sys.executable,str(CALLER),'--schema-only'])
 closure=P/'literal-runtime-closure.json'
 js="import fs from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url),c=snapshotModuleClosure(new URL("+json.dumps(str(RUNTIME.relative_to(ROOT)))+",root),root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);fs.writeFileSync("+json.dumps(str(closure))+",JSON.stringify(c)+'\\n',{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length}));"
 run('actual-current-capture-literal-closure',['node','--input-type=module','-e',js]);c=read(closure);refs.append(ref(closure))
 for path,h in c['inputHashes'].items():assert ref(ROOT/path)==dict(path=path,sha256=h);refs.append(dict(path=path,sha256=h))
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),bindingValidationRef=ref(validation),commands=commands,literalClosureRef=ref(closure),
  evidenceRefs=distinct(refs+[ref(Path(__file__)),ref(P/'draft-pins.json')]),transitivePythonCodeRefs=pins['codeRefs'],beforeEndAllDeclaredRefsVerified=True,noDrawGuardFiniteDBLeaseWorker=True))
 print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
