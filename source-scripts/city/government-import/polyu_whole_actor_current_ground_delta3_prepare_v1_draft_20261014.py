"""ROOT-only exact saved-source schema + current delta3/ground literal preparation."""
from pathlib import Path
import json,gzip,hashlib,sys,os,subprocess,ast
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014-proposal';PRIOR=BASE/'government-xl-polyu-four-compatible-parent-current-production-v3-20261014-proposal';CAP=BASE/'government-xl-polyu-four-compatible-parent-current-production-v3-20261014'
CALLER=HERE/'polyu_whole_actor_current_ground_delta3_caller_v1_draft_20261014.py';RUNTIME=HERE/'polyu_whole_actor_current_ground_delta3_runtime_v1_draft_20261014.mjs'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 with p.open('x')as f:json.dump(v,f,sort_keys=True,separators=(',',':'));f.write('\n')
def distinct(rows):
 d={}
 for q in rows:
  if q['path']in d:assert d[q['path']]==q
  d[q['path']]=q
 return [d[p]for p in sorted(d)]
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
 sys.path.insert(0,str(HERE));import polyu_whole_actor_current_ground_delta3_caller_v1_draft_20261014 as c
 previous=read(PRIOR/'draft-pins.json');c.prior.load();rows,roi,source_ref=c.actor_inputs()
 inputs=previous['inputRefs']+[ref(PRIOR/'draft-pins.json'),ref(CAP/'result.json'),ref(CAP/'ROOT-VERIFIED.json'),ref(CAP/'private-native-terrain-candidate.json.gz'),ref(CAP/'guard-first-viability.json'),ref(CAP/'actual-production-replay.json.gz'),ref(CAP/'input.json.gz'),ref(CAP/'complete-fresh-current-native59527-and24-BASIC.json.gz'),ref(CAP/'native59527-unchanged-provider-original-world.json.gz'),source_ref,
  ref(c.FEAS/'complete-nine-parent-restoration-feasibility.json.gz'),ref(BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012/inventory.json.gz'),ref(BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/complete-current-actual-source-and-ground-305582-0.json.gz')]
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');wanted=set(c.DELTAS)
 for tile in manifest['tiles']:inputs.append(ref(ROOT/'3d-viewer'/tile['url']))
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']in wanted:inputs.append(ref(p.parent/e['asset']))
 code=distinct(previous['codeRefs']+code_closure()+[ref(RUNTIME),ref(P/'METHOD.md'),ref(HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'),ref(HERE/'actual_float32_model_matrix_bounds_20261011.mjs'),ref(HERE/'current_geometry_capture_preflight_20261011.mjs'),ref(HERE/'exact_incremental_json_gzip_v1_20261012.mjs'),ref(HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs')])
 for q in distinct(code+inputs):assert ref(ROOT/q['path'])==q
 save(P/'draft-pins.json',dict(caller=ref(CALLER),runtime=ref(RUNTIME),codeRefs=code,inputRefs=distinct(inputs),completeWholeActorROI=roi))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),completeWholeActorROI=roi,codeRefs=len(code),inputRefs=len(distinct(inputs)),noFiniteSourceDecodeOrDBLease=True)))
def prepare():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME);declared=distinct(pins['codeRefs']+pins['inputRefs'])
 def fence():
  for q in declared:assert ref(ROOT/q['path'])==q
 fence();commands=[];evidence=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));evidence.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
 run('actual-whole-ground-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-whole-ground-schema',[sys.executable,str(CALLER),'--schema-only'])
 closure=P/'literal-runtime-closure.json';js="import fs from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url),c=snapshotModuleClosure(new URL("+json.dumps(str(RUNTIME.relative_to(ROOT)))+",root),root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);fs.writeFileSync("+json.dumps(str(closure))+",JSON.stringify(c)+String.fromCharCode(10),{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length}));"
 run('actual-whole-ground-literal-closure',['node','--input-type=module','-e',js]);evidence.append(ref(closure))
 for path,h in read(closure)['inputHashes'].items():assert ref(ROOT/path)==dict(path=path,sha256=h);evidence.append(dict(path=path,sha256=h))
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),commands=commands,beforeEndAllDeclaredPinsVerified=True,literalClosureRef=ref(closure),evidenceRefs=distinct(evidence+[ref(Path(__file__)),ref(P/'draft-pins.json')]),noGuardFiniteSourceDecodeDBLease=True));print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
